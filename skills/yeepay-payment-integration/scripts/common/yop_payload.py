# -*- coding: utf-8 -*-
"""content-sha256 / content-sm3 载荷与请求形态判定。"""

from __future__ import annotations

from common.url_encoding import canonical_form


def has_multipart(files) -> bool:
    return bool(files)


def is_urlencoded_form(method: str, json_body, files) -> bool:
    return method.upper() == "POST" and json_body is None and not has_multipart(files)


def digest_payload_text(
    method: str,
    params: dict | None,
    json_body: str | None,
    files,
) -> str:
    """计算摘要用的请求参数字符串（UTF-8 文本）。

    - GET：空串
    - POST JSON：JSON 原文
    - POST Form / multipart：仅**非文件**参数的 canonical 串（一次编码）
    """
    method = method.upper()
    if method == "GET":
        return ""
    if json_body is not None:
        return json_body
    return canonical_form(params or {})
