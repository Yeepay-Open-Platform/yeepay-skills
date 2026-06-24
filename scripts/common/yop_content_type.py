# -*- coding: utf-8 -*-
"""YOP 出站请求 Content-Type 常量与解析。"""

from __future__ import annotations

# GET / POST Form 统一 UTF-8；该 Content-Type 仅作 HTTP 头，不参与签名
CONTENT_TYPE_FORM = "application/x-www-form-urlencoded;charset=UTF-8"
# POST JSON 默认值；仅作 HTTP 头，不参与签名
CONTENT_TYPE_JSON = "application/json"

# 参与 Authorization 签名的请求头（小写）；与 Java YopPKISigner.DEFAULT_HEADERS_TO_SIGN 对齐
HEADERS_TO_SIGN = frozenset({
    "content-length",
    "content-type",
    "content-md5",
    "x-yop-request-id",
    "x-yop-date",
    "x-yop-appkey",
    "x-yop-content-sha256",
    "x-yop-content-sm3",
    "x-yop-hash-crc64ecma",
    "x-yop-encrypt",
})


def resolve_content_type(
    method: str,
    *,
    json_body: str | None = None,
    content_type: str | None = None,
    multipart: bool = False,
) -> str | None:
    """解析出站 Content-Type。

    - multipart：不设 Content-Type（由 HTTP 客户端生成 boundary）
    - GET / POST Form → ``CONTENT_TYPE_FORM``（charset=UTF-8）
    - POST JSON → ``CONTENT_TYPE_JSON``
    - 均不参与签名
    """
    if multipart:
        return None
    if content_type:
        return content_type.strip()
    if json_body is not None:
        return CONTENT_TYPE_JSON
    return CONTENT_TYPE_FORM


def pick_headers_to_sign(headers: dict[str, str]) -> dict[str, str]:
    """从请求头中筛出参与签名的头（小写 key，值 trim）。"""
    signed: dict[str, str] = {}
    for key, value in headers.items():
        if value is None:
            continue
        name = key.lower().strip()
        if name in HEADERS_TO_SIGN and name != "authorization":
            signed[name] = str(value).strip()
    return signed
