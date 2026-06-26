#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""本地模拟发结果通知，验证商户回调接收与验签/解密逻辑。

两种模式：
  simple（默认）：简化签名，仅打通 HTTP 链路，**不可**验证四段密文解密实现。
  real：按真实四段密文格式（encKey$encData$AES$SHA256）构造，可与 decrypt_notify.py 互打验证。

用法：
    python rsa/mock_notify.py --url http://127.0.0.1:8080/notify --key ./merchant.pem --data '{"orderId":"x"}'

    python rsa/mock_notify.py --mode real \\
        --url http://127.0.0.1:8080/notify \\
        --yop-key ./yop_private.pem \\
        --merchant-pubkey ./merchant_public.pem \\
        --data '{"status":"SUCCESS","orderId":"ORDER_xxx"}'
"""

import argparse
import base64
import json
import os
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from common.python_version import ensure_python_version
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from rsa.notify_crypto import encrypt_notify, load_key

try:
    import requests
except ImportError:
    requests = None


def _load_private_key(pem: str):
    pem = pem.strip()
    if "BEGIN" not in pem:
        pem = (
            "-----BEGIN PRIVATE KEY-----\n"
            + "\n".join(pem[i : i + 64] for i in range(0, len(pem), 64))
            + "\n-----END PRIVATE KEY-----\n"
        )
    return serialization.load_pem_private_key(pem.encode("utf-8"), password=None)


def sign_simple(private_key, payload: str) -> str:
    sig = private_key.sign(payload.encode("utf-8"), padding.PKCS1v15(), hashes.SHA256())
    return base64.urlsafe_b64encode(sig).decode("ascii").rstrip("=") + "$SHA256"


def main():
    ensure_python_version()
    p = argparse.ArgumentParser(
        description="本地模拟发结果通知",
        epilog="simple 模式仅打通 HTTP；验证解密实现请用 --mode real + decrypt_notify.py",
    )
    p.add_argument("--mode", choices=["simple", "real"], default="simple",
                   help="simple=简化签名(默认); real=四段密文(可互打验证)")
    p.add_argument("--url", required=True, help="商户回调 notifyUrl")
    p.add_argument("--key", default=os.getenv("YOP_PRIVATE_KEY"),
                   help="[simple] 签名私钥")
    p.add_argument("--yop-key", default=os.getenv("YOP_PLATFORM_PRIVATE_KEY"),
                   help="[real] 易宝侧私钥（模拟平台签名）")
    p.add_argument("--merchant-pubkey", default=os.getenv("YOP_MERCHANT_PUBLIC_KEY"),
                   help="[real] 商户公钥（加密随机密钥）")
    p.add_argument("--data", help="回调报文 JSON")
    p.add_argument("--data-file", help="回调报文 JSON 文件")
    p.add_argument("--dry-run", action="store_true", help="只打印，不发送")
    args = p.parse_args()

    if args.data_file:
        payload = open(args.data_file, encoding="utf-8").read()
    elif args.data:
        payload = args.data
    else:
        raise SystemExit("请用 --data 或 --data-file 提供回调报文")
    payload = json.dumps(json.loads(payload), ensure_ascii=False, separators=(",", ":"))

    if args.mode == "simple":
        if not args.key:
            raise SystemExit("simple 模式需要 --key 或 YOP_PRIVATE_KEY")
        key_pem = open(args.key, encoding="utf-8").read() if os.path.isfile(args.key) else args.key
        body = payload
        headers = {"Content-Type": "application/json", "x-yop-sign": sign_simple(_load_private_key(key_pem), payload)}
        print("== 模式: simple（仅打通 HTTP，不可验证四段解密）==")
    else:
        if not args.yop_key or not args.merchant_pubkey:
            raise SystemExit("real 模式需要 --yop-key 与 --merchant-pubkey")
        body = encrypt_notify(
            payload,
            load_key(args.yop_key, "private"),
            load_key(args.merchant_pubkey, "public"),
        )
        headers = {"Content-Type": "text/plain"}
        print("== 模式: real（四段密文，可用 rsa/decrypt_notify.py 验证）==")

    print("== 发送 body ==")
    print(body)
    if args.mode == "simple":
        print("== x-yop-sign ==")
        print(headers.get("x-yop-sign"))

    if args.dry_run:
        return
    if requests is None:
        raise SystemExit("缺少依赖 requests：pip install requests")
    resp = requests.post(args.url, data=body.encode("utf-8"), headers=headers, timeout=15)
    print(f"== 商户回调返回 HTTP {resp.status_code} ==")
    print(resp.text[:1000])


if __name__ == "__main__":
    main()
