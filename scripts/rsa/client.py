#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""易宝 YOP 开放平台轻量客户端（RSA 鉴权）。

仅用于联调与本地验证，不用于生产交易/出款。
签名实现依据：references/平台文档/平台规范/安全认证/鉴权认证机制(RSA).md

依赖：
    pip install cryptography requests
"""

import base64
import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from common.url_encoding import (
    canonical_form as _canonical_form,
    http_form_body,
    http_query_string,
    url_encode_for_sign,
)
from common.yop_content_type import pick_headers_to_sign, resolve_content_type
from common.yop_http import save_response_body, send_request
from common.yop_multipart import build_requests_multipart, normalize_files
from common.yop_payload import digest_payload_text, is_urlencoded_form

PROTOCOL_VERSION = "yop-auth-v3"
SECURITY_REQ = "YOP-RSA2048-SHA256"
from common.yop_gateway import DEFAULT_OPENAPI, DEFAULT_SANDBOX, DEFAULT_YOS, resolve_gateway


def _load_private_key(pem: str):
    """加载 PKCS8/PKCS1 PEM 私钥；支持传入纯 Base64（自动补 PEM 头尾）。"""
    pem = pem.strip()
    if "BEGIN" not in pem:
        pem = (
            "-----BEGIN PRIVATE KEY-----\n"
            + "\n".join(pem[i : i + 64] for i in range(0, len(pem), 64))
            + "\n-----END PRIVATE KEY-----\n"
        )
    return serialization.load_pem_private_key(pem.encode("utf-8"), password=None)


def _content_sha256(method: str, params: dict, json_body: str | None, files) -> str:
    payload = digest_payload_text(method, params, json_body, files)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _sign(private_key, canonical_request: str) -> str:
    sig = private_key.sign(
        canonical_request.encode("utf-8"),
        padding.PKCS1v15(),
        hashes.SHA256(),
    )
    return base64.urlsafe_b64encode(sig).decode("ascii").rstrip("=") + "$SHA256"


def build_request(app_key, private_key_pem, method, path, params=None,
                  json_body=None, files=None, base_url=DEFAULT_OPENAPI,
                  expire_seconds=1800, timestamp=None, request_id=None,
                  content_type=None):
    """构造已签名的请求（url, headers, body / multipart）。

    files：multipart 上传，见 ``common.yop_multipart.FilePart``。
    timestamp/request_id 可显式传入以复现固定测试向量。
    """
    method = method.upper()
    params = params or {}
    file_parts = normalize_files(files)
    if file_parts and method != "POST":
        raise ValueError("multipart 文件上传仅支持 POST")
    if file_parts and json_body is not None:
        raise ValueError("files 与 json_body 不能同时使用")

    timestamp = timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    request_id = request_id or str(uuid.uuid4())

    content_type = resolve_content_type(
        method, json_body=json_body, content_type=content_type,
        multipart=bool(file_parts),
    )
    content_sha256 = _content_sha256(method, params, json_body, file_parts)

    sign_headers: dict[str, str] = {
        "x-yop-appkey": app_key,
        "x-yop-content-sha256": content_sha256,
        "x-yop-request-id": request_id,
    }
    signed = pick_headers_to_sign(sign_headers)
    auth_string = f"{PROTOCOL_VERSION}/{app_key}/{timestamp}/{expire_seconds}"
    signed_headers = ";".join(sorted(signed.keys()))
    canonical_qs = _canonical_form(params) if method == "GET" else ""
    canonical_headers = "\n".join(
        f"{url_encode_for_sign(k)}:{url_encode_for_sign(v)}"
        for k, v in sorted(signed.items())
    )
    canonical_request = "\n".join([
        auth_string, method, path, canonical_qs, canonical_headers,
    ])
    signature = _sign(_load_private_key(private_key_pem), canonical_request)
    authorization = f"{SECURITY_REQ} {auth_string}/{signed_headers}/{signature}"

    headers = {"Authorization": authorization, **sign_headers}
    if content_type:
        headers["Content-Type"] = content_type

    from common.yop_headers import build_standard_headers

    headers.update(build_standard_headers())

    url = base_url.rstrip("/") + path
    canonical_body = None
    multipart = None
    body = None

    if method == "GET" and params:
        url = f"{url}?{http_query_string(params)}"
        canonical_body = _canonical_form(params)
    elif json_body is not None:
        body = json_body
    elif file_parts:
        canonical_body = _canonical_form(params)
        multipart = build_requests_multipart(params, file_parts)
    elif is_urlencoded_form(method, json_body, file_parts):
        canonical_body = _canonical_form(params)
        body = http_form_body(params)

    return {
        "url": url, "method": method, "headers": headers, "body": body,
        "multipart": multipart,
        "request_id": request_id, "timestamp": timestamp,
        "canonical_request": canonical_request,
        "canonical_body": canonical_body,
        "content_type": content_type,
    }


def _verify_response(resp, verify, yop_pubkey, strict_verify):
    if not verify:
        return resp
    import os

    from common.response_verify import ResponseVerifyError, verify_http_response

    pubkey = yop_pubkey or os.getenv("YOP_PLATFORM_PUBLIC_KEY")
    try:
        if verify_http_response(
            resp, algorithm="rsa", yop_pubkey=pubkey, strict_missing=strict_verify,
        ):
            resp.yop_sign_verified = True  # type: ignore[attr-defined]
    except ResponseVerifyError as e:
        raise RuntimeError(f"应答验签失败：{e}") from e
    return resp


def call(app_key, private_key_pem, method, path, params=None, json_body=None,
         files=None, base_url=None, sandbox=False, timeout=30, verify=False,
         yop_pubkey=None, strict_verify=False, content_type=None):
    """发送已签名请求并返回 requests.Response。"""
    if base_url is None:
        base_url = resolve_gateway(sandbox=sandbox)
    req = build_request(
        app_key, private_key_pem, method, path, params, json_body, files,
        base_url, content_type=content_type,
    )
    resp = send_request(req, timeout=timeout)
    return _verify_response(resp, verify, yop_pubkey, strict_verify)


def upload(app_key, private_key_pem, path, params=None, files=None,
           base_url=None, sandbox=False, timeout=120, verify=False, yop_pubkey=None,
           strict_verify=False):
    """multipart 文件上传（POST）。生产默认 yos 网关；沙箱走 sandbox 域名。"""
    if base_url is None:
        base_url = resolve_gateway(sandbox=sandbox, yos=True)
    return call(
        app_key, private_key_pem, "POST", path, params=params, files=files,
        base_url=base_url, sandbox=sandbox, timeout=timeout, verify=verify,
        yop_pubkey=yop_pubkey, strict_verify=strict_verify,
    )


def download(app_key, private_key_pem, path, params=None, base_url=None,
             sandbox=False, timeout=120, save_path=None, verify=False,
             yop_pubkey=None, strict_verify=False):
    """文件下载（GET）。生产默认 yos 网关；沙箱走 sandbox 域名。"""
    if base_url is None:
        base_url = resolve_gateway(sandbox=sandbox, yos=True)
    req = build_request(
        app_key, private_key_pem, "GET", path, params=params, base_url=base_url,
    )
    resp = send_request(req, timeout=timeout, stream=True)
    _verify_response(resp, verify, yop_pubkey, strict_verify)
    if save_path:
        return save_response_body(resp, save_path)
    return resp
