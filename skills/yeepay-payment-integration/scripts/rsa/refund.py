#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""退款（申请退款 / 查询退款），用于联调。

接口：
    申请退款 POST /rest/v1.0/trade/refund        （catalog id: trade-refund）
    查询退款 GET  /rest/v1.0/trade/refund/query   （catalog id: trade-refund-query）
字段以在线 doc_md 文档为准。

用法：
    # 申请退款
    python rsa/refund.py apply --appkey app_100xxx --key ./keys/rsa_private_pkcs8.pem \\
        --merchant 100xxx --order-id ORDER_xxx --refund-id REFUND_xxx --amount 0.01
    # 查询退款
    python rsa/refund.py query --appkey app_100xxx --key ./keys/rsa_private_pkcs8.pem \\
        --merchant 100xxx --order-id ORDER_xxx --refund-id REFUND_xxx

注意：退款单号(refund-id)需业务唯一；重试请用同一单号避免重复退款。
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


def _common(p):
    p.add_argument("--appkey", default=os.getenv("YOP_APPKEY"))
    p.add_argument("--key", default=os.getenv("YOP_PRIVATE_KEY"))
    p.add_argument("--merchant", default=os.getenv("YOP_MERCHANT_NO"))
    p.add_argument("--parent-merchant", default=os.getenv("YOP_PARENT_MERCHANT_NO"))
    p.add_argument("--order-id", required=True, help="原交易商户收款请求号 orderId")
    p.add_argument("--refund-id", required=True, help="退款请求号 refundRequestId（业务唯一）")
    p.add_argument("--base-url", default=yop_client.DEFAULT_OPENAPI)


def main():
    ensure_python_version()
    parser = argparse.ArgumentParser(description="易宝退款")
    sub = parser.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("apply", help="申请退款")
    _common(pa)
    pa.add_argument("--amount", required=True, help="退款金额（元，两位小数）")
    pa.add_argument("--notify-url", default=os.getenv("YOP_NOTIFY_URL"))
    pa.add_argument("--description", default="refund")

    pq = sub.add_parser("query", help="查询退款")
    _common(pq)

    args = parser.parse_args()
    if not (args.appkey and args.key and args.merchant):
        raise SystemExit("缺少 appkey/key/merchant，请用参数或环境变量提供")
    private_key = _read_key(args.key)
    parent = args.parent_merchant or args.merchant

    if args.cmd == "apply":
        if not _confirm(f"将对订单 {args.order_id} 退款 {args.amount} 元，退款单号 {args.refund_id}"):
            raise SystemExit("已取消")
        params = {
            "parentMerchantNo": parent,
            "merchantNo": args.merchant,
            "orderId": args.order_id,
            "refundRequestId": args.refund_id,
            "refundAmount": args.amount,
            "description": args.description,
        }
        if args.notify_url:
            params["notifyUrl"] = args.notify_url
        resp = yop_client.call(args.appkey, private_key, "POST",
                               "/rest/v1.0/trade/refund", params=params, base_url=args.base_url)
    else:
        params = {
            "parentMerchantNo": parent,
            "merchantNo": args.merchant,
            "orderId": args.order_id,
            "refundRequestId": args.refund_id,
        }
        resp = yop_client.call(args.appkey, private_key, "GET",
                               "/rest/v1.0/trade/refund/query", params=params, base_url=args.base_url)
    _print_resp(resp)


def _confirm(msg: str) -> bool:
    return input(f"[确认] {msg} ？(yes/no) ").strip().lower() in ("y", "yes")


def _read_key(key: str) -> str:
    if os.path.isfile(key):
        with open(key, "r", encoding="utf-8") as f:
            return f.read()
    return key


def _print_resp(resp):
    print(f"HTTP {resp.status_code}  request-id={resp.headers.get('x-yop-request-id')}")
    try:
        print(json.dumps(resp.json(), ensure_ascii=False, indent=2))
    except ValueError:
        print(resp.text)


if __name__ == "__main__":
    main()
