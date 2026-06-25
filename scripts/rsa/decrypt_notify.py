#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""回调密文解密验签工具（RSA 四段格式）。

用法：
    python rsa/decrypt_notify.py \\
        --cipher 'encKey$encData$AES$SHA256' \
        --merchant-key ./keys/rsa_private_pkcs8.pem \
        --yop-pubkey ./keys/yop_public.pem
"""

import argparse
import os
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from common.python_version import ensure_python_version
from rsa.notify_crypto import decrypt_notify, load_key


def main():
    ensure_python_version()
    p = argparse.ArgumentParser(description="RSA 回调密文解密验签")
    p.add_argument("--cipher", required=True, help="四段密文（可用引号包裹）")
    p.add_argument("--cipher-file", help="从文件读取密文")
    p.add_argument("--merchant-key", default=os.getenv("YOP_PRIVATE_KEY"),
                     help="商户私钥（解随机密钥）")
    p.add_argument("--yop-pubkey", default=os.getenv("YOP_PLATFORM_PUBLIC_KEY"),
                     help="易宝公钥（验签）")
    args = p.parse_args()

    cipher = open(args.cipher_file, encoding="utf-8").read().strip() if args.cipher_file else args.cipher.strip()
    if not args.merchant_key or not args.yop_pubkey:
        raise SystemExit("缺少 --merchant-key / --yop-pubkey（或对应环境变量）")

    try:
        plain = decrypt_notify(
            cipher,
            load_key(args.merchant_key, "private"),
            load_key(args.yop_pubkey, "public"),
        )
    except ValueError as e:
        print(f"失败：{e}", file=sys.stderr)
        sys.exit(1)

    print("验签通过，明文：")
    print(plain)


if __name__ == "__main__":
    main()
