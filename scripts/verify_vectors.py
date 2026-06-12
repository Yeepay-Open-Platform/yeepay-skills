#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""签名/回调解密测试向量的生成与校验。

用途：
  1. 校验（默认）：用 tests/vectors/ 中的固定输入重新计算签名、解密固定密文，
     与向量文件中的期望输出逐项比对——保证协议文档中的示例与脚本实现不漂移。
  2. 重新生成（--regen）：协议实现变更时重算向量并回写 JSON；
     重算后必须同步更新协议文档中的「完整示例」并提升 Skill 版本。

测试密钥仅供本向量使用，禁止用于任何真实环境。
"""

import argparse
import base64
import json
import sys
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

import notify_crypto
import yop_client

VECTOR_DIR = Path(__file__).resolve().parent / "tests" / "vectors"

MERCHANT_PRIVATE = VECTOR_DIR / "test_merchant_private.pem"
MERCHANT_PUBLIC = VECTOR_DIR / "test_merchant_public.pem"
YOP_PRIVATE = VECTOR_DIR / "test_yop_private.pem"
YOP_PUBLIC = VECTOR_DIR / "test_yop_public.pem"
SIGN_VECTORS = VECTOR_DIR / "sign_vectors.json"
NOTIFY_VECTOR = VECTOR_DIR / "notify_vector.json"

# ---- 固定输入（修改即破坏向量，须 --regen 并同步文档） ----

APP_KEY = "app_10086032562"
TIMESTAMP = "2026-01-01T00:00:00Z"
REQUEST_ID = "00000000-0000-4000-8000-000000000001"
EXPIRE_SECONDS = 1800

SIGN_CASES = [
    {
        "name": "GET 查单（query 含空格，验证 %20 编码与 key 升序）",
        "method": "GET",
        "path": "/rest/v1.0/trade/order/query",
        "params": {"merchantNo": "10086032562", "orderId": "TEST ORDER_20260101_001"},
        "json_body": None,
    },
    {
        "name": "POST Form 退款（body 含中文，canonicalQueryString 为空串）",
        "method": "POST",
        "path": "/rest/v1.0/trade/refund",
        "params": {
            "merchantNo": "10086032562",
            "orderId": "TEST_ORDER_20260101_001",
            "refundRequestId": "REFUND_20260101_001",
            "refundAmount": "0.01",
            "description": "测试退款",
        },
        "json_body": None,
    },
    {
        "name": "POST JSON（content-sha256 取 JSON 原文，canonicalQueryString 为空串）",
        "method": "POST",
        "path": "/rest/v1.0/test/json-demo",
        "params": None,
        "json_body": '{"merchantNo":"10086032562","orderId":"TEST_ORDER_20260101_001",'
                     '"orderAmount":"0.01","goodsName":"测试商品"}',
    },
]

NOTIFY_PLAINTEXT = (
    '{"orderId":"TEST_ORDER_20260101_001","uniqueOrderNo":"1001202601010000000001",'
    '"status":"SUCCESS","orderAmount":"0.01"}'
)
NOTIFY_AES_KEY_HEX = "000102030405060708090a0b0c0d0e0f"


def _gen_keypair(private_path: Path, public_path: Path) -> None:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_path.write_bytes(key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ))
    public_path.write_bytes(key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ))


def _compute_sign_case(case: dict, merchant_pem: str) -> dict:
    req = yop_client.build_request(
        APP_KEY, merchant_pem, case["method"], case["path"],
        params=case["params"], json_body=case["json_body"],
        expire_seconds=EXPIRE_SECONDS, timestamp=TIMESTAMP, request_id=REQUEST_ID,
    )
    return {
        "content_sha256": req["headers"]["x-yop-content-sha256"],
        "canonical_request": req["canonical_request"],
        "authorization": req["headers"]["Authorization"],
        "body": req["body"],
        "url": req["url"],
    }


def regen() -> None:
    VECTOR_DIR.mkdir(parents=True, exist_ok=True)
    if not MERCHANT_PRIVATE.exists():
        _gen_keypair(MERCHANT_PRIVATE, MERCHANT_PUBLIC)
    if not YOP_PRIVATE.exists():
        _gen_keypair(YOP_PRIVATE, YOP_PUBLIC)

    merchant_pem = MERCHANT_PRIVATE.read_text()
    sign_vectors = {
        "app_key": APP_KEY,
        "timestamp": TIMESTAMP,
        "request_id": REQUEST_ID,
        "expire_seconds": EXPIRE_SECONDS,
        "cases": [],
    }
    for case in SIGN_CASES:
        entry = {k: case[k] for k in ("name", "method", "path", "params", "json_body")}
        entry["expected"] = _compute_sign_case(case, merchant_pem)
        sign_vectors["cases"].append(entry)
    SIGN_VECTORS.write_text(
        json.dumps(sign_vectors, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    yop_priv = notify_crypto.load_key(str(YOP_PRIVATE), "private")
    merchant_pub = notify_crypto.load_key(str(MERCHANT_PUBLIC), "public")
    ciphertext = notify_crypto.encrypt_notify(
        NOTIFY_PLAINTEXT, yop_priv, merchant_pub,
        aes_key=bytes.fromhex(NOTIFY_AES_KEY_HEX))
    notify_vector = {
        "plaintext": NOTIFY_PLAINTEXT,
        "aes_key_hex": NOTIFY_AES_KEY_HEX,
        "ciphertext": ciphertext,
    }
    NOTIFY_VECTOR.write_text(
        json.dumps(notify_vector, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[regen] 已写入 {SIGN_VECTORS.name} / {NOTIFY_VECTOR.name}")
    print("[regen] 请同步更新 请求签名协议.md / 回调解密协议.md 的「完整示例」并提升 Skill 版本")


def verify() -> list[str]:
    errors: list[str] = []
    for f in (MERCHANT_PRIVATE, YOP_PUBLIC, SIGN_VECTORS, NOTIFY_VECTOR):
        if not f.exists():
            return [f"缺少向量文件：{f}（先运行 verify_vectors.py --regen）"]

    merchant_pem = MERCHANT_PRIVATE.read_text()
    sign_vectors = json.loads(SIGN_VECTORS.read_text(encoding="utf-8"))
    for case in sign_vectors["cases"]:
        actual = _compute_sign_case(case, merchant_pem)
        for field, expect in case["expected"].items():
            if actual.get(field) != expect:
                errors.append(
                    f"签名向量不匹配 [{case['name']}] 字段 {field}：\n"
                    f"  期望: {expect}\n  实际: {actual.get(field)}")

    notify_vector = json.loads(NOTIFY_VECTOR.read_text(encoding="utf-8"))
    merchant_priv = notify_crypto.load_key(str(MERCHANT_PRIVATE), "private")
    yop_pub = notify_crypto.load_key(str(YOP_PUBLIC), "public")
    try:
        plain = notify_crypto.decrypt_notify(
            notify_vector["ciphertext"], merchant_priv, yop_pub)
        if plain != notify_vector["plaintext"]:
            errors.append("回调向量不匹配：解密明文与期望不一致")
    except ValueError as e:
        errors.append(f"回调向量解密失败：{e}")

    # AES 随机密钥固定时密文应可整体复现
    yop_priv = notify_crypto.load_key(str(YOP_PRIVATE), "private")
    merchant_pub = notify_crypto.load_key(str(MERCHANT_PUBLIC), "public")
    rebuilt = notify_crypto.encrypt_notify(
        notify_vector["plaintext"], yop_priv, merchant_pub,
        aes_key=bytes.fromhex(notify_vector["aes_key_hex"]))
    enc_data_expect = notify_vector["ciphertext"].split("$")[1]
    enc_data_actual = rebuilt.split("$")[1]
    if enc_data_actual != enc_data_expect:
        errors.append("回调向量不匹配：encData 段不可复现（AES/签名实现变更？）")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--regen", action="store_true", help="重新生成向量文件")
    args = parser.parse_args()

    if args.regen:
        regen()
        return 0

    errors = verify()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"\n[FAIL] 测试向量校验失败 {len(errors)} 项", file=sys.stderr)
        return 1
    print("[OK] 签名/回调解密测试向量校验通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
