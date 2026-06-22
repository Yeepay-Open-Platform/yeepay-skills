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
from urllib.parse import quote

try:
    import requests
except ImportError:  # 延迟报错，便于仅做签名自检时不强依赖 requests
    requests = None

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

PROTOCOL_VERSION = "yop-auth-v3"
SECURITY_REQ = "YOP-RSA2048-SHA256"
DEFAULT_OPENAPI = "https://openapi.yeepay.com"
DEFAULT_YOS = "https://yos.yeepay.com"


def _quote(value: str) -> str:
    """RFC3986 URL 编码：空格转 %20，保留 A-Za-z0-9-_.~（Python quote 默认即满足）。"""
    return quote(str(value), safe="")


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


def _canonical_form(params: dict) -> str:
    """form 参数：urlencode 后按 key 升序，用 & 拼接。"""
    items = sorted((k, "" if v is None else v) for k, v in params.items())
    return "&".join(f"{_quote(k)}={_quote(v)}" for k, v in items)


def _content_sha256(method: str, content_type: str, params: dict, json_body: str) -> str:
    if method == "GET":
        payload = ""
    elif json_body is not None:
        payload = json_body
    else:  # POST form
        payload = _canonical_form(params or {})
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _sign(private_key, canonical_request: str) -> str:
    sig = private_key.sign(
        canonical_request.encode("utf-8"),
        padding.PKCS1v15(),
        hashes.SHA256(),
    )
    return base64.urlsafe_b64encode(sig).decode("ascii").rstrip("=") + "$SHA256"


def build_request(app_key, private_key_pem, method, path, params=None,
                  json_body=None, base_url=DEFAULT_OPENAPI, expire_seconds=1800,
                  timestamp=None, request_id=None):
    """构造已签名的请求（url, headers, body）。不直接发送，便于自检与复用。

    timestamp/request_id 可显式传入以复现固定测试向量（见 rsa/tests/vectors/）。
    """
    method = method.upper()
    params = params or {}
    timestamp = timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    request_id = request_id or str(uuid.uuid4())

    is_form = method == "POST" and json_body is None
    content_type = (
        "application/json" if json_body is not None
        else "application/x-www-form-urlencoded" if is_form
        else None
    )

    content_sha256 = _content_sha256(method, content_type, params, json_body)

    # 参与签名的标头
    signed = {
        "x-yop-appkey": app_key,
        "x-yop-content-sha256": content_sha256,
        "x-yop-request-id": request_id,
    }
    if content_type:
        signed["content-type"] = content_type

    auth_string = f"{PROTOCOL_VERSION}/{app_key}/{timestamp}/{expire_seconds}"
    signed_headers = ";".join(sorted(signed.keys()))

    # GET 的规范查询串；POST(form/json) 一律空串
    canonical_qs = _canonical_form(params) if method == "GET" else ""

    canonical_headers = "\n".join(
        f"{_quote(k)}:{_quote(v)}" for k, v in sorted(signed.items())
    )

    canonical_request = "\n".join([
        auth_string, method, path, canonical_qs, canonical_headers,
    ])

    signature = _sign(_load_private_key(private_key_pem), canonical_request)
    authorization = f"{SECURITY_REQ} {auth_string}/{signed_headers}/{signature}"

    headers = {
        "Authorization": authorization,
        "x-yop-appkey": app_key,
        "x-yop-request-id": request_id,
        "x-yop-content-sha256": content_sha256,
    }
    if content_type:
        headers["Content-Type"] = content_type

    url = base_url.rstrip("/") + path
    if method == "GET" and params:
        url = f"{url}?{_canonical_form(params)}"
        body = None
    elif json_body is not None:
        body = json_body
    elif is_form:
        body = _canonical_form(params)
    else:
        body = None

    return {
        "url": url, "method": method, "headers": headers, "body": body,
        "request_id": request_id, "timestamp": timestamp,
        "canonical_request": canonical_request,
    }


def call(app_key, private_key_pem, method, path, params=None, json_body=None,
         base_url=DEFAULT_OPENAPI, timeout=30, verify=False, yop_pubkey=None,
         strict_verify=False):
    """发送已签名请求并返回 requests.Response。

    verify=True 时对响应做平台应答验签，须提供 yop_pubkey（或环境变量 YOP_PLATFORM_PUBLIC_KEY）。
    """
    if requests is None:
        raise RuntimeError("缺少依赖 requests：pip install requests")
    req = build_request(app_key, private_key_pem, method, path, params, json_body, base_url)
    if method.upper() == "GET":
        resp = requests.get(req["url"], headers=req["headers"], timeout=timeout)
    else:
        resp = requests.post(req["url"], headers=req["headers"], data=req["body"], timeout=timeout)

    if verify:
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
