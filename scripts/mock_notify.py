#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""本地模拟"发结果通知"，用于联调商户回调接收与验签逻辑。

模拟易宝结果通知机制：用商户/平台私钥对通知报文签名，POST 到商户 notifyUrl。
便于在没有真实交易的情况下验证回调接收、验签、幂等处理。

签名形态（默认 RSA-SHA256，与结果通知机制一致的简化实现）：
    - 对回调 JSON 报文做 SHA256withRSA 签名，URL 安全 Base64，结尾拼 $SHA256
    - 通过请求头与表单字段携带签名，便于商户侧按需取用
具体字段/验签算法以 references/平台文档/平台规范/安全认证/结果通知(RSA).md 为准。

用法：
    python mock_notify.py \
        --url http://127.0.0.1:8080/yeepay/notify \
        --key ./keys/rsa_private_pkcs8.pem \
        --data '{"status":"SUCCESS","orderId":"ORDER_xxx","orderAmount":"0.01"}'
    # 或从文件读报文：--data-file ./notify.json
"""

import argparse
import base64
import json
import os

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

try:
    import requests
except ImportError:
    requests = None


def _load_private_key(pem: str):
    pem = pem.strip()
    if "BEGIN" not in pem:
        pem = ("-----BEGIN PRIVATE KEY-----\n"
               + "\n".join(pem[i:i + 64] for i in range(0, len(pem), 64))
               + "\n-----END PRIVATE KEY-----\n")
    return serialization.load_pem_private_key(pem.encode("utf-8"), password=None)


def sign(private_key, payload: str) -> str:
    sig = private_key.sign(payload.encode("utf-8"), padding.PKCS1v15(), hashes.SHA256())
    return base64.urlsafe_b64encode(sig).decode("ascii").rstrip("=") + "$SHA256"


def main():
    p = argparse.ArgumentParser(description="本地模拟发结果通知")
    p.add_argument("--url", required=True, help="商户回调接收地址 notifyUrl")
    p.add_argument("--key", default=os.getenv("YOP_PRIVATE_KEY"), help="签名私钥文件或 PEM")
    p.add_argument("--data", help="回调报文 JSON 字符串")
    p.add_argument("--data-file", help="回调报文 JSON 文件")
    p.add_argument("--dry-run", action="store_true", help="只打印签名后的报文，不发送")
    args = p.parse_args()

    if args.data_file:
        with open(args.data_file, "r", encoding="utf-8") as f:
            payload = f.read()
    elif args.data:
        payload = args.data
    else:
        raise SystemExit("请用 --data 或 --data-file 提供回调报文")
    # 规整为紧凑 JSON，保证签名与发送一致
    payload = json.dumps(json.loads(payload), ensure_ascii=False, separators=(",", ":"))

    if not args.key:
        raise SystemExit("缺少签名私钥：--key 或环境变量 YOP_PRIVATE_KEY")
    key_pem = open(args.key, encoding="utf-8").read() if os.path.isfile(args.key) else args.key
    signature = sign(_load_private_key(key_pem), payload)

    headers = {"Content-Type": "application/json", "x-yop-sign": signature}
    print("== 模拟回调报文 ==")
    print(payload)
    print("== 签名(x-yop-sign) ==")
    print(signature)

    if args.dry_run:
        return
    if requests is None:
        raise SystemExit("缺少依赖 requests：pip install requests")
    resp = requests.post(args.url, data=payload.encode("utf-8"), headers=headers, timeout=15)
    print(f"== 商户回调返回 HTTP {resp.status_code} ==")
    print(resp.text[:1000])


if __name__ == "__main__":
    main()
