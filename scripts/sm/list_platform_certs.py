#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查询易宝平台商密（SM2）证书列表。

接口：GET /rest/v2.0/yop/platform/certs（V2，返回 PEM cert 字段）
鉴权：YOP-SM2-SM3，须商户 CFCA 商密私钥。

文档：references/平台文档/平台规范/安全认证/平台商密证书.md

用法：
    python sm/list_platform_certs.py \\
        --appkey sandbox_sm_xxx \\
        --key ./keys/sm2_private_pkcs8.pem

    python sm/list_platform_certs.py --serial-no 4059376239 --save-dir ./certs/yop
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from common.python_version import ensure_python_version
from sm import client as sm_client

API_PATH = "/rest/v2.0/yop/platform/certs"
DATE_FMT = "%Y-%m-%d %H:%M:%S"


def _parse_response(resp) -> list[dict]:
    try:
        body = resp.json()
    except ValueError as e:
        raise SystemExit(f"响应非 JSON：{resp.text[:500]}") from e

    if isinstance(body, dict):
        if "result" in body and isinstance(body["result"], dict):
            payload = body["result"]
        else:
            payload = body
        data = payload.get("data")
        if data is None and "state" in body:
            raise SystemExit(f"接口返回异常：{json.dumps(body, ensure_ascii=False)}")
        if not isinstance(data, list):
            raise SystemExit(f"未找到 data 数组：{json.dumps(body, ensure_ascii=False)[:800]}")
        return data
    raise SystemExit(f"无法解析响应：{type(body)}")


def _parse_dt(text: str) -> datetime:
    return datetime.strptime(text.strip(), DATE_FMT)


def _status(now: datetime, effective: datetime, expire: datetime) -> str:
    if now > expire:
        return "已过期"
    if now < effective:
        return "待生效"
    return "有效"


def _save_cert(entry: dict, out_dir: Path, extract_pubkey: bool) -> None:
    serial = entry.get("serialNo", "unknown")
    cert_pem = entry.get("cert", "")
    if not cert_pem.strip():
        return
    out_dir.mkdir(parents=True, exist_ok=True)
    cert_path = out_dir / f"yop_sm2_{serial}.cer.pem"
    cert_path.write_text(cert_pem if cert_pem.endswith("\n") else cert_pem + "\n", encoding="utf-8")
    print(f"  已保存证书：{cert_path}")
    if extract_pubkey:
        pub_path = out_dir / f"yop_sm2_{serial}_public.pem"
        try:
            proc = subprocess.run(
                ["openssl", "x509", "-in", str(cert_path), "-pubkey", "-noout"],
                check=True,
                capture_output=True,
                text=True,
            )
            pub_path.write_text(proc.stdout, encoding="utf-8")
            print(f"  已导出公钥：{pub_path}")
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            print(f"  公钥导出跳过（需 openssl）：{e}", file=sys.stderr)


def _print_table(certs: list[dict], now: datetime) -> None:
    active = [c for c in certs if _status(now, _parse_dt(c["effectiveDate"]), _parse_dt(c["expireDate"])) == "有效"]
    latest_serial = None
    if active:
        latest = max(active, key=lambda c: _parse_dt(c["expireDate"]))
        latest_serial = latest["serialNo"]
        print(f"\n当前有效证书 {len(active)} 本；最晚到期序列号：{latest_serial}（{latest['expireDate']}）")
    print(f"\n{'序列号':<16} {'状态':<6} {'生效时间':<20} {'失效时间':<20} 剩余天数")
    print("-" * 80)
    for entry in sorted(certs, key=lambda c: _parse_dt(c["expireDate"]), reverse=True):
        eff = _parse_dt(entry["effectiveDate"])
        exp = _parse_dt(entry["expireDate"])
        st = _status(now, eff, exp)
        days = (exp - now).days if exp > now else 0
        mark = (
            " ← 当前有效且最晚到期"
            if latest_serial and entry.get("serialNo") == latest_serial and st == "有效"
            else ""
        )
        print(
            f"{entry.get('serialNo',''):<16} {st:<6} "
            f"{entry.get('effectiveDate',''):<20} {entry.get('expireDate',''):<20} "
            f"{days if st != '已过期' else '-'}{mark}"
        )


def main() -> int:
    ensure_python_version()
    p = argparse.ArgumentParser(description="查询易宝平台 SM2 证书列表（V2）")
    p.add_argument("--appkey", default=os.getenv("YOP_APPKEY"), help="商户 appKey")
    p.add_argument("--key", default=os.getenv("YOP_PRIVATE_KEY"), help="商户 SM2 私钥 PEM 路径")
    p.add_argument("--serial-no", help="仅查询指定证书序列号")
    p.add_argument("--cert-type", default="SM2", help="证书类型，默认 SM2")
    p.add_argument("--base-url", default=sm_client.DEFAULT_OPENAPI, help="网关地址")
    p.add_argument("--save-dir", help="将 cert PEM 保存到目录，并尝试 openssl 导出公钥")
    p.add_argument("--no-extract-pubkey", action="store_true", help="保存证书时不导出公钥")
    p.add_argument("--json", action="store_true", help="原样输出 JSON data 数组")
    args = p.parse_args()

    if not args.appkey or not args.key:
        raise SystemExit("缺少 --appkey / --key（或环境变量 YOP_APPKEY、YOP_PRIVATE_KEY）")

    params: dict[str, str] = {}
    if args.cert_type:
        params["certType"] = args.cert_type
    if args.serial_no:
        params["serialNo"] = args.serial_no

    resp = sm_client.call(
        args.appkey,
        args.key,
        "GET",
        API_PATH,
        params=params,
        base_url=args.base_url,
    )
    print(f"HTTP {resp.status_code}  request-id={resp.headers.get('x-yop-request-id')}")
    if resp.status_code != 200:
        print(resp.text[:2000], file=sys.stderr)
        return 1

    certs = _parse_response(resp)
    if args.json:
        print(json.dumps(certs, ensure_ascii=False, indent=2))
        return 0

    if not certs:
        print("证书列表为空")
        return 0

    now = datetime.now()
    _print_table(certs, now)
    print("\n提示：验签/回调解密请按报文头 x-yop-sign-serial-no 选择对应公钥；详见 平台规范/安全认证/平台商密证书.md")

    if args.save_dir:
        out = Path(args.save_dir)
        print(f"\n保存到 {out}：")
        for entry in certs:
            _save_cert(entry, out, extract_pubkey=not args.no_extract_pubkey)

    return 0


if __name__ == "__main__":
    sys.exit(main())
