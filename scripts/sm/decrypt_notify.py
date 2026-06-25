#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SM2 回调解密验签工具。

用法：
    python sm/decrypt_notify.py \\
        --header Authorization:'YOP-SM2-SM3 ...' \\
        --header x-yop-encrypt:'yop-encrypt-v1/...' \\
        --body 'urlSafeBase64Cipher' \\
        --merchant-key ./keys/sm2_private_pkcs8.pem \\
        --yop-pubkey ./keys/sm2_yop_public.pem
"""

import argparse
import json
import os
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from common.python_version import ensure_python_version
from sm.crypto import load_sm2_private, load_sm2_public
from sm.notify_crypto import decrypt_notify


def _parse_headers(items: list[str]) -> dict:
    headers = {}
    for item in items:
        if ":" not in item:
            raise SystemExit(f"无效 header：{item}，格式 name:value")
        name, value = item.split(":", 1)
        headers[name.strip()] = value.strip()
    return headers


def main():
    ensure_python_version()
    p = argparse.ArgumentParser(description="SM2 回调解密验签")
    p.add_argument("--header", action="append", default=[], help="请求头，可重复")
    p.add_argument("--headers-file", help="JSON 文件存放 headers")
    p.add_argument("--body", required=True, help="加密 body（urlSafeBase64）")
    p.add_argument("--body-file", help="从文件读取 body")
    p.add_argument("--merchant-key", default=os.getenv("YOP_PRIVATE_KEY"),
                   help="商户 SM2 私钥 PEM 或 PKCS8 base64")
    p.add_argument("--yop-pubkey", default=os.getenv("YOP_PLATFORM_PUBLIC_KEY"),
                   help="易宝 SM2 公钥 PEM 或 SPKI base64")
    args = p.parse_args()

    if args.headers_file:
        headers = json.loads(open(args.headers_file, encoding="utf-8").read())
    else:
        headers = _parse_headers(args.header)
    if not headers:
        raise SystemExit("请通过 --header 或 --headers-file 提供请求头")

    body = open(args.body_file, encoding="utf-8").read().strip() if args.body_file else args.body.strip()
    if not args.merchant_key or not args.yop_pubkey:
        raise SystemExit("缺少 --merchant-key / --yop-pubkey")

    try:
        plain = decrypt_notify(
            headers,
            body,
            load_sm2_private(args.merchant_key),
            load_sm2_public(args.yop_pubkey),
        )
    except ValueError as e:
        print(f"失败：{e}", file=sys.stderr)
        sys.exit(1)

    print("验签通过，明文：")
    print(plain)


if __name__ == "__main__":
    main()
