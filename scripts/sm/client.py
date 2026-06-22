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
from urllib.parse import quote

try:
    import requests
except ImportError:
    requests = None

from .crypto import SECURITY_REQ, PROTOCOL_VERSION, sign_sm3, sm3_hex

DEFAULT_OPENAPI = "https://openapi.yeepay.com"
DEFAULT_YOS = "https://yos.yeepay.com"


def _quote(value: str) -> str:
    return quote(str(value), safe="")


def _canonical_form(params: dict) -> str:
    items = sorted((k, "" if v is None else v) for k, v in params.items())
    return "&".join(f"{_quote(k)}={_quote(v)}" for k, v in items)


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
                  timestamp=None, request_id=None, sign_random_hex=None):
    """构造已签名的 SM 请求（url, headers, body）。"""
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

    content_sm3 = _content_sm3(method, content_type, params, json_body)

    signed = {
        "x-yop-appkey": app_key,
        "x-yop-content-sm3": content_sm3,
        "x-yop-request-id": request_id,
    }
    if content_type:
        signed["content-type"] = content_type

    auth_string = f"{PROTOCOL_VERSION}/{app_key}/{timestamp}/{expire_seconds}"
    signed_headers = ";".join(sorted(signed.keys()))
    canonical_qs = _canonical_form(params) if method == "GET" else ""
    canonical_headers = "\n".join(
        f"{_quote(k)}:{_quote(v)}" for k, v in sorted(signed.items())
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
        "x-yop-appkey": app_key,
        "x-yop-request-id": request_id,
        "x-yop-content-sm3": content_sm3,
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
        "canonical_request": canonical_request, "content_sm3": content_sm3,
    }


def call(app_key, private_key_hex, method, path, params=None, json_body=None,
         base_url=DEFAULT_OPENAPI, timeout=30):
    if requests is None:
        raise RuntimeError("缺少依赖 requests：pip install requests")
    req = build_request(app_key, private_key_hex, method, path, params, json_body, base_url)
    if req["method"] == "GET":
        return requests.get(req["url"], headers=req["headers"], timeout=timeout)
    return requests.post(req["url"], headers=req["headers"], data=req["body"], timeout=timeout)
