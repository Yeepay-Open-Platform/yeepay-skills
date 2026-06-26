# -*- coding: utf-8 -*-
"""YOP 出站 HTTP 发送辅助。"""

from __future__ import annotations

from pathlib import Path

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


def send_request(req: dict, *, timeout: int = 30, stream: bool = False):
    """发送 build_request 构造的请求。

    multipart 上传：``req["multipart"]`` 非空时不发送手写 Content-Type。
    stream=True 用于文件下载等大响应体。
    """
    if requests is None:
        raise RuntimeError("缺少依赖 requests：pip install requests")
    headers = dict(req["headers"])
    method = req["method"].upper()
    multipart = req.get("multipart")
    if multipart:
        headers.pop("Content-Type", None)
        if method == "GET":
            raise ValueError("multipart 仅支持 POST")
        return requests.post(
            req["url"], headers=headers, files=multipart, timeout=timeout, stream=stream,
        )
    body = encode_body(req.get("body"))
    if method == "GET":
        return requests.get(req["url"], headers=headers, timeout=timeout, stream=stream)
    return requests.post(req["url"], headers=headers, data=body, timeout=timeout, stream=stream)


def save_response_body(resp, save_path: str | Path) -> Path:
    """将响应体写入本地文件（适用于文件下载）。"""
    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(resp.content)
    return path
