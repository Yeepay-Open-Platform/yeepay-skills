# -*- coding: utf-8 -*-
"""multipart/form-data 文件上传辅助（与平台 202.md / Java SDK 对齐）。"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path

from common.url_encoding import url_encode_http


@dataclass(frozen=True)
class FilePart:
    """单个文件表单项。"""

    field: str
    filename: str
    content: bytes
    content_type: str = "application/octet-stream"


def normalize_files(files) -> list[FilePart]:
    """将多种入参形式规范为 ``FilePart`` 列表。

    支持：
    - ``FilePart`` / ``FilePart`` 列表
    - ``{field: path}`` / ``{field: (filename, bytes)}`` / ``{field: bytes}``
    - ``[(field, path), ...]`` / ``[(field, filename, bytes), ...]``
    """
    if not files:
        return []
    if isinstance(files, FilePart):
        return [files]
    if isinstance(files, dict):
        items = []
        for field, value in files.items():
            items.append(_coerce_file_part(field, value))
        return items
    parts: list[FilePart] = []
    for item in files:
        if isinstance(item, FilePart):
            parts.append(item)
        elif isinstance(item, tuple):
            if len(item) == 2:
                parts.append(_coerce_file_part(item[0], item[1]))
            elif len(item) == 3:
                field, filename, content = item
                parts.append(FilePart(field, filename, _as_bytes(content)))
            else:
                raise ValueError(f"files 元组长度非法：{item!r}")
        else:
            raise TypeError(f"不支持的 files 元素类型：{type(item)!r}")
    return parts


def files_from_vector(specs: list[dict]) -> list[FilePart]:
    """从测试向量 JSON（含 content_b64）还原 FilePart。"""
    return [
        FilePart(
            s["field"],
            s["filename"],
            base64.b64decode(s["content_b64"]),
            s.get("content_type", "application/octet-stream"),
        )
        for s in specs
    ]


def build_requests_multipart(text_params: dict, file_parts: list[FilePart]) -> list:
    """构造 ``requests.post(..., files=...)`` 参数。

    文本字段：值按 HTTP 协议 **编码一次**（等同 Java MultipartEntityBuilder.addTextBody + URLEncoder）。
    文件字段：二进制上传，不参与 content-sha256。
    """
    parts: list = []
    for k, v in sorted((k, "" if v is None else v) for k, v in (text_params or {}).items()):
        parts.append((k, (None, url_encode_http(str(v)))))
    for fp in sorted(file_parts, key=lambda x: x.field):
        parts.append((fp.field, (fp.filename, fp.content, fp.content_type)))
    return parts


def _coerce_file_part(field: str, value) -> FilePart:
    if isinstance(value, FilePart):
        return value
    if isinstance(value, (bytes, bytearray)):
        return FilePart(field, field, bytes(value))
    if isinstance(value, tuple) and len(value) == 2:
        filename, content = value
        return FilePart(field, filename, _as_bytes(content))
    path = Path(str(value))
    return FilePart(field, path.name, path.read_bytes())


def _as_bytes(value) -> bytes:
    if isinstance(value, bytearray):
        return bytes(value)
    if isinstance(value, bytes):
        return value
    raise TypeError(f"文件内容须为 bytes，实际为 {type(value)!r}")
