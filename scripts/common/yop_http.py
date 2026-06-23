# -*- coding: utf-8 -*-
"""YOP 出站 HTTP 发送辅助。"""

from __future__ import annotations

try:
    import requests
except ImportError:
    requests = None


def encode_body(body: str | bytes | None) -> bytes | None:
    if body is None:
        return None
    if isinstance(body, bytes):
        return body
    return body.encode("utf-8")


def send_request(req: dict, *, timeout: int = 30):
    """发送 build_request 构造的请求，保留 Content-Type 等自定义头。"""
    if requests is None:
        raise RuntimeError("缺少依赖 requests：pip install requests")
    headers = req["headers"]
    body = encode_body(req.get("body"))
    if req["method"].upper() == "GET":
        return requests.get(req["url"], headers=headers, timeout=timeout)
    return requests.post(req["url"], headers=headers, data=body, timeout=timeout)
