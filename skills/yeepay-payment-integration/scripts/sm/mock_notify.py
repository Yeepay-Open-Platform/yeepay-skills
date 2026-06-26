#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""本地模拟 SM2 结果通知，验证商户回调解密逻辑。

用法：
    python sm/mock_notify.py --mode real --dry-run \\
        --url http://127.0.0.1:8080/notify \\
        --yop-key ./keys/sm2_yop_private_pkcs8.pem \\
        --merchant-pubkey ./keys/sm2_merchant_public.pem \\
        --data '{"status":"SUCCESS","orderId":"ORDER_xxx"}'
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

try:
    import requests
except ImportError:
    requests = None

from common.python_version import ensure_python_version
from sm.crypto import load_sm2_private, load_sm2_public
from sm.notify_crypto import encrypt_notify


def main():
    ensure_python_version()
    p = argparse.ArgumentParser(description="本地模拟 SM2 结果通知")
    p.add_argument("--mode", choices=["simple", "real"], default="real",
                   help="real=SM2/SM4 密文（可互打验证）；simple 仅 JSON 明文")
    p.add_argument("--url", required=True, help="商户回调 notifyUrl")
    p.add_argument("--yop-key", default=os.getenv("YOP_PLATFORM_PRIVATE_KEY"),
                   help="易宝侧 SM2 私钥 PEM（模拟平台签名）")
    p.add_argument("--merchant-pubkey", default=os.getenv("YOP_MERCHANT_PUBLIC_KEY"),
                   help="商户 SM2 公钥 PEM（加密 SM4 密钥）")
    p.add_argument("--appkey", default=os.getenv("YOP_APPKEY", "app_test_sm"))
    p.add_argument("--request-id", default="mock-sm-notify-001")
    p.add_argument("--data", help="回调 JSON")
    p.add_argument("--data-file", help="回调 JSON 文件")
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
        headers = {"Content-Type": "application/json"}
        body = payload
        print("== 模式: simple（明文 JSON，不可验证 SM 解密）==")
    else:
        if not args.yop_key or not args.merchant_pubkey:
            raise SystemExit("real 模式需要 --yop-key 与 --merchant-pubkey")
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        headers, body = encrypt_notify(
            payload,
            load_sm2_private(args.yop_key),
            load_sm2_public(args.merchant_pubkey),
            app_key=args.appkey,
            request_id=args.request_id,
            timestamp=timestamp,
        )
        print("== 模式: real（SM2/SM4，可用 sm/decrypt_notify.py 验证）==")

    print("== headers ==")
    for k, v in headers.items():
        print(f"{k}: {v}")
    print("== body ==")
    print(body)

    if args.dry_run:
        return
    if requests is None:
        raise SystemExit("缺少依赖 requests：pip install requests")
    resp = requests.post(args.url, data=body.encode("utf-8"), headers=headers, timeout=15)
    print(f"== 商户回调返回 HTTP {resp.status_code} ==")
    print(resp.text[:1000])


if __name__ == "__main__":
    main()
