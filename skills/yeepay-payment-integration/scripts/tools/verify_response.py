#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""独立应答验签 CLI（不发起 HTTP 请求）。

在 scripts/ 目录下执行：
    python tools/verify_response.py --algo rsa \\
        --body-file ./response.json \\
        --signature 'xxx...$SHA256' \\
        --yop-pubkey ./keys/yop_public.pem
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from common.python_version import ensure_python_version
from common.response_verify import (
    HEADER_SERIAL,
    HEADER_SIGN,
    ResponseVerifyError,
    verify_http_response,
)


class _HeaderResponse:
    def __init__(self, headers: dict[str, str], text: str):
        self.headers = headers
        self.text = text


def _load_headers(path: str) -> dict[str, str]:
    text = Path(path).read_text(encoding="utf-8")
    if path.endswith(".json"):
        data = json.loads(text)
        return {str(k): str(v) for k, v in data.items()}
    headers: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        name, value = line.split(":", 1)
        headers[name.strip()] = value.strip()
    return headers


def main() -> int:
    ensure_python_version()
    p = argparse.ArgumentParser(description="易宝 API 应答验签")
    p.add_argument("--algo", choices=["rsa", "sm2"], default="rsa", help="验签算法")
    p.add_argument("--body", help="响应 body 原文")
    p.add_argument("--body-file", help="从文件读取响应 body")
    p.add_argument("--signature", help="x-yop-sign 值（不含头名）")
    p.add_argument("--serial-no", help="x-yop-sign-serial-no（SM2，可选）")
    p.add_argument("--headers-file", help="响应头（JSON 或 name: value 每行）")
    p.add_argument("--yop-pubkey", default=os.getenv("YOP_PLATFORM_PUBLIC_KEY"), help="平台公钥 PEM")
    p.add_argument("--cert-dir", help="SM2 平台证书目录（按序列号选公钥）")
    p.add_argument("--strict-missing", action="store_true", help="缺少 x-yop-sign 时报错")
    args = p.parse_args()

    if args.body_file:
        body = Path(args.body_file).read_text(encoding="utf-8")
    elif args.body is not None:
        body = args.body
    else:
        raise SystemExit("缺少 --body 或 --body-file")

    headers: dict[str, str] = {}
    if args.headers_file:
        headers.update(_load_headers(args.headers_file))
    if args.signature:
        headers[HEADER_SIGN] = args.signature
    if args.serial_no:
        headers[HEADER_SERIAL] = args.serial_no

    if HEADER_SIGN not in headers:
        raise SystemExit("缺少 x-yop-sign（--signature 或 --headers-file）")

    resp = _HeaderResponse(headers, body)
    try:
        ok = verify_http_response(
            resp,
            algorithm=args.algo,
            yop_pubkey=args.yop_pubkey,
            cert_dir=args.cert_dir,
            strict_missing=args.strict_missing,
        )
    except ResponseVerifyError as e:
        print(f"验签失败：{e}", file=sys.stderr)
        return 1

    if ok:
        print("应答验签通过")
        return 0
    print("未验签（无 x-yop-sign）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
