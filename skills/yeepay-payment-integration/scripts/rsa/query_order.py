#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查单（交易订单查询），用于联调确认交易终态。

接口：GET /rest/v1.0/trade/order/query（catalog id: trade-order-query）
字段以在线 doc_md 文档为准，本脚本仅演示鉴权与调用。

用法：
    python rsa/query_order.py \\
        --appkey app_100xxx \
        --key ./keys/rsa_private_pkcs8.pem \
        --merchant 100xxx \
        --order-id ORDER202401010515217305372872

环境变量可替代参数：YOP_APPKEY、YOP_PRIVATE_KEY(文件路径或 PEM)、YOP_MERCHANT_NO
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
from rsa import client as yop_client


def main():
    ensure_python_version()
    p = argparse.ArgumentParser(description="易宝查单")
    p.add_argument("--appkey", default=os.getenv("YOP_APPKEY"))
    p.add_argument("--key", default=os.getenv("YOP_PRIVATE_KEY"), help="私钥文件路径或 PEM 文本")
    p.add_argument("--merchant", default=os.getenv("YOP_MERCHANT_NO"), help="商户编号")
    p.add_argument("--parent-merchant", default=os.getenv("YOP_PARENT_MERCHANT_NO"))
    p.add_argument("--order-id", required=True, help="商户收款请求号 orderId")
    p.add_argument("--unique-order-no", help="易宝订单号 uniqueOrderNo（可选）")
    p.add_argument("--base-url", default=yop_client.DEFAULT_OPENAPI)
    p.add_argument("--verify", action="store_true", help="验签平台应答（须 --yop-pubkey）")
    p.add_argument("--yop-pubkey", default=os.getenv("YOP_PLATFORM_PUBLIC_KEY"), help="易宝 RSA 公钥 PEM")
    args = p.parse_args()

    if not (args.appkey and args.key and args.merchant):
        raise SystemExit("缺少 appkey/key/merchant，请用参数或环境变量提供")

    private_key = _read_key(args.key)
    params = {
        "parentMerchantNo": args.parent_merchant or args.merchant,
        "merchantNo": args.merchant,
        "orderId": args.order_id,
    }
    if args.unique_order_no:
        params["uniqueOrderNo"] = args.unique_order_no

    resp = yop_client.call(
        args.appkey, private_key, "GET",
        "/rest/v1.0/trade/order/query", params=params, base_url=args.base_url,
        verify=args.verify, yop_pubkey=args.yop_pubkey,
    )
    _print_resp(resp)


def _read_key(key: str) -> str:
    if os.path.isfile(key):
        with open(key, "r", encoding="utf-8") as f:
            return f.read()
    return key


def _print_resp(resp):
    verified = getattr(resp, "yop_sign_verified", False)
    flag = "  [应答验签通过]" if verified else ""
    print(f"HTTP {resp.status_code}  request-id={resp.headers.get('x-yop-request-id')}{flag}")
    try:
        print(json.dumps(resp.json(), ensure_ascii=False, indent=2))
    except ValueError:
        print(resp.text)


if __name__ == "__main__":
    main()
