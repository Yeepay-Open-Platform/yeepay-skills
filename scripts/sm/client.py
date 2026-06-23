#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""易宝 YOP 开放平台轻量客户端（SM2/SM3 鉴权）。

仅用于联调与本地验证，不用于生产交易/出款。
签名实现依据：references/平台文档/平台规范/安全认证/鉴权认证机制(SM).md

依赖：
    pip install gmssl requests
"""

import uuid
from datetime import datetime, timezone

from common.url_encoding import (
    canonical_form as _canonical_form,
    http_form_body,
    http_query_string,
    url_encode_for_sign,
)
from common.yop_content_type import pick_headers_to_sign, resolve_content_type
from common.yop_http import send_request
from .crypto import SECURITY_REQ, PROTOCOL_VERSION, sign_sm3, sm3_hex

DEFAULT_OPENAPI = "https://openapi.yeepay.com"
DEFAULT_YOS = "https://yos.yeepay.com"


def _content_sm3(method: str, content_type: str, params: dict, json_body: str) -> str:
    if method == "GET":
        payload = b""
    elif json_body is not None:
        payload = json_body.encode("utf-8")
    else:
        payload = _canonical_form(params or {}).encode("utf-8")
    return sm3_hex(payload)


def build_request(app_key, private_key_hex, method, path, params=None,
                  json_body=None, base_url=DEFAULT_OPENAPI, expire_seconds=1800,
                  timestamp=None, request_id=None, sign_random_hex=None,
                  content_type=None):
    """构造已签名的 SM 请求（url, headers, body）。"""
    method = method.upper()
    params = params or {}
    timestamp = timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    request_id = request_id or str(uuid.uuid4())

    is_form = method == "POST" and json_body is None
    content_type = resolve_content_type(
        method, json_body=json_body, content_type=content_type,
    )

    content_sm3 = _content_sm3(method, content_type, params, json_body)

    sign_headers: dict[str, str] = {
        "x-yop-appkey": app_key,
        "x-yop-content-sm3": content_sm3,
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

    from .crypto import load_sm2_private

    private_hex = load_sm2_private(private_key_hex)

    signature = sign_sm3(
        canonical_request.encode("utf-8"),
        private_hex,
        random_hex=sign_random_hex,
    )
    authorization = f"{SECURITY_REQ} {auth_string}/{signed_headers}/{signature}"

    headers = {
        "Authorization": authorization,
        **sign_headers,
        "Content-Type": content_type,
    }

    from common.yop_headers import build_standard_headers

    headers.update(build_standard_headers())

    url = base_url.rstrip("/") + path
    canonical_body = None
    if method == "GET" and params:
        url = f"{url}?{http_query_string(params)}"
        canonical_body = _canonical_form(params)
        body = None
    elif json_body is not None:
        body = json_body
    elif is_form:
        canonical_body = _canonical_form(params)
        body = http_form_body(params)
    else:
        body = None

    return {
        "url": url, "method": method, "headers": headers, "body": body,
        "request_id": request_id, "timestamp": timestamp,
        "canonical_request": canonical_request, "content_sm3": content_sm3,
        "canonical_body": canonical_body,
        "content_type": content_type,
    }


def call(app_key, private_key_hex, method, path, params=None, json_body=None,
         base_url=DEFAULT_OPENAPI, timeout=30, verify=False, yop_pubkey=None,
         cert_dir=None, strict_verify=False, content_type=None):
    """发送已签名请求。verify=True 时验签应答（须 yop_pubkey 或 cert_dir + x-yop-sign-serial-no）。"""
    req = build_request(
        app_key, private_key_hex, method, path, params, json_body, base_url,
        content_type=content_type,
    )
    resp = send_request(req, timeout=timeout)

    if verify:
        import os

        from common.response_verify import ResponseVerifyError, verify_http_response

        pubkey = yop_pubkey or os.getenv("YOP_PLATFORM_PUBLIC_KEY")
        try:
            if verify_http_response(
                resp,
                algorithm="sm2",
                yop_pubkey=pubkey,
                cert_dir=cert_dir,
                strict_missing=strict_verify,
            ):
                resp.yop_sign_verified = True  # type: ignore[attr-defined]
        except ResponseVerifyError as e:
            raise RuntimeError(f"应答验签失败：{e}") from e
    return resp
