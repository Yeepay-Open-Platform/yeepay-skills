#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""签名/回调解密/应答验签测试向量的生成与校验。

在 scripts/ 目录下执行：
    python tools/verify_vectors.py
    python tools/verify_vectors.py --regen

测试密钥仅供本向量使用，禁止用于任何真实环境。
"""

import argparse
import json
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from common.python_version import ensure_python_version
from common.yop_gateway import resolve_gateway
from common.yop_multipart import files_from_vector
from common.response_verify import (
    sign_rsa_response,
    sign_sm2_response,
    verify_rsa_response,
    verify_sm2_response,
)
from rsa import client as rsa_client
from rsa import notify_crypto as rsa_notify_crypto
from sm import client as sm_client
from sm import notify_crypto as sm_notify_crypto
from sm.crypto import (
    export_sm2_private_pem,
    export_sm2_public_pem,
    generate_sm2_keypair,
    load_sm2_private,
    load_sm2_public,
)

SCRIPTS_DIR = _SCRIPTS_DIR
RSA_VECTOR_DIR = SCRIPTS_DIR / "rsa" / "tests" / "vectors"
SM_VECTOR_DIR = SCRIPTS_DIR / "sm" / "tests" / "vectors"

MERCHANT_PRIVATE = RSA_VECTOR_DIR / "test_merchant_private.pem"
MERCHANT_PUBLIC = RSA_VECTOR_DIR / "test_merchant_public.pem"
YOP_PRIVATE = RSA_VECTOR_DIR / "test_yop_private.pem"
YOP_PUBLIC = RSA_VECTOR_DIR / "test_yop_public.pem"
SIGN_VECTORS = RSA_VECTOR_DIR / "sign_vectors.json"
NOTIFY_VECTOR = RSA_VECTOR_DIR / "notify_vector.json"
RESPONSE_VECTOR = RSA_VECTOR_DIR / "response_vector.json"

MERCHANT_SM2_PRIVATE = SM_VECTOR_DIR / "test_merchant_sm2_private.pem"
MERCHANT_SM2_PUBLIC = SM_VECTOR_DIR / "test_merchant_sm2_public.pem"
YOP_SM2_PRIVATE = SM_VECTOR_DIR / "test_yop_sm2_private.pem"
YOP_SM2_PUBLIC = SM_VECTOR_DIR / "test_yop_sm2_public.pem"
SIGN_SM_VECTORS = SM_VECTOR_DIR / "sign_sm_vectors.json"
NOTIFY_SM_VECTOR = SM_VECTOR_DIR / "notify_sm_vector.json"
RESPONSE_SM_VECTOR = SM_VECTOR_DIR / "response_sm_vector.json"

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
    {
        "name": "POST multipart 上传（content-sha256 仅非文件参数）",
        "method": "POST",
        "path": "/yos/v1.0/test/upload-demo",
        "params": {"merchantNo": "10086032562", "bizType": "TEST"},
        "files": [
            {"field": "_file", "filename": "hello.txt", "content_b64": "SGVsbG8="},
        ],
        "json_body": None,
    },
]

NOTIFY_PLAINTEXT = (
    '{"orderId":"TEST_ORDER_20260101_001","uniqueOrderNo":"1001202601010000000001",'
    '"status":"SUCCESS","orderAmount":"0.01"}'
)
NOTIFY_AES_KEY_HEX = "000102030405060708090a0b0c0d0e0f"

SM_SIGN_RANDOM_HEX = "a" * 64
SM_SIGN_CASE = {
    "name": "POST Form 退款（SM2/SM3）",
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
}

NOTIFY_SM_PLAINTEXT = NOTIFY_PLAINTEXT
NOTIFY_SM4_KEY_HEX = "00112233445566778899aabbccddeeff"
NOTIFY_SM4_IV_HEX = "0102030405060708090a0b0c0d0e0f10"
NOTIFY_SM_APP_KEY = APP_KEY
NOTIFY_SM_REQUEST_ID = "00000000-0000-4000-8000-000000000002"
NOTIFY_SM_TIMESTAMP = "2026-01-01T00:00:00Z"
NOTIFY_SM_URI = "/notify/sm-vector"

RESPONSE_BODY = (
    '{\n'
    '  "state": "SUCCESS",\n'
    '  "result": {"orderId": "TEST_ORDER_20260101_001"}\n'
    '}'
)
RESPONSE_SM_SIGN_RANDOM = "b" * 64


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


def _files_from_case(case: dict):
    specs = case.get("files")
    return files_from_vector(specs) if specs else None


def _compute_sign_case(case: dict, merchant_pem: str) -> dict:
    req = rsa_client.build_request(
        APP_KEY, merchant_pem, case["method"], case["path"],
        params=case["params"], json_body=case["json_body"],
        files=_files_from_case(case),
        base_url=resolve_gateway(yos=bool(case.get("files"))),
        expire_seconds=EXPIRE_SECONDS, timestamp=TIMESTAMP, request_id=REQUEST_ID,
    )
    return {
        "content_sha256": req["headers"]["x-yop-content-sha256"],
        "canonical_request": req["canonical_request"],
        "authorization": req["headers"]["Authorization"],
        "body": req["body"],
        "url": req["url"],
        "content_type": req.get("content_type"),
    }


def _ensure_sm2_keypair(private_path: Path, public_path: Path) -> None:
    if private_path.exists() and public_path.exists():
        return
    priv, pub = generate_sm2_keypair()
    private_path.write_bytes(export_sm2_private_pem(priv, pub))
    public_path.write_bytes(export_sm2_public_pem(pub))


def _compute_sm_sign_case(case: dict, merchant_priv_pem: str) -> dict:
    req = sm_client.build_request(
        APP_KEY, merchant_priv_pem, case["method"], case["path"],
        params=case["params"], json_body=case["json_body"],
        files=_files_from_case(case),
        expire_seconds=EXPIRE_SECONDS, timestamp=TIMESTAMP, request_id=REQUEST_ID,
        sign_random_hex=SM_SIGN_RANDOM_HEX,
    )
    return {
        "content_sm3": req["headers"]["x-yop-content-sm3"],
        "canonical_request": req["canonical_request"],
        "authorization": req["headers"]["Authorization"],
        "body": req["body"],
        "url": req["url"],
        "content_type": req.get("content_type"),
    }


def regen() -> None:
    RSA_VECTOR_DIR.mkdir(parents=True, exist_ok=True)
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
        if case.get("files"):
            entry["files"] = case["files"]
        entry["expected"] = _compute_sign_case(case, merchant_pem)
        sign_vectors["cases"].append(entry)
    SIGN_VECTORS.write_text(
        json.dumps(sign_vectors, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    yop_priv = rsa_notify_crypto.load_key(str(YOP_PRIVATE), "private")
    merchant_pub = rsa_notify_crypto.load_key(str(MERCHANT_PUBLIC), "public")
    ciphertext = rsa_notify_crypto.encrypt_notify(
        NOTIFY_PLAINTEXT, yop_priv, merchant_pub,
        aes_key=bytes.fromhex(NOTIFY_AES_KEY_HEX))
    notify_vector = {
        "plaintext": NOTIFY_PLAINTEXT,
        "aes_key_hex": NOTIFY_AES_KEY_HEX,
        "ciphertext": ciphertext,
    }
    NOTIFY_VECTOR.write_text(
        json.dumps(notify_vector, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    response_vector = {
        "body": RESPONSE_BODY,
        "signature": sign_rsa_response(RESPONSE_BODY, yop_priv),
    }
    RESPONSE_VECTOR.write_text(
        json.dumps(response_vector, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    SM_VECTOR_DIR.mkdir(parents=True, exist_ok=True)
    _ensure_sm2_keypair(MERCHANT_SM2_PRIVATE, MERCHANT_SM2_PUBLIC)
    _ensure_sm2_keypair(YOP_SM2_PRIVATE, YOP_SM2_PUBLIC)
    merchant_sm2_priv = load_sm2_private(str(MERCHANT_SM2_PRIVATE))
    yop_sm2_priv = load_sm2_private(str(YOP_SM2_PRIVATE))
    merchant_sm2_pub = load_sm2_public(str(MERCHANT_SM2_PUBLIC))
    yop_sm2_pub = load_sm2_public(str(YOP_SM2_PUBLIC))

    sign_sm_vectors = {
        "app_key": APP_KEY,
        "timestamp": TIMESTAMP,
        "request_id": REQUEST_ID,
        "expire_seconds": EXPIRE_SECONDS,
        "sign_random_hex": SM_SIGN_RANDOM_HEX,
        "cases": [],
    }
    entry = {k: SM_SIGN_CASE[k] for k in ("name", "method", "path", "params", "json_body")}
    entry["expected"] = _compute_sm_sign_case(SM_SIGN_CASE, str(MERCHANT_SM2_PRIVATE))
    sign_sm_vectors["cases"].append(entry)
    SIGN_SM_VECTORS.write_text(
        json.dumps(sign_sm_vectors, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    headers, body = sm_notify_crypto.encrypt_notify(
        NOTIFY_SM_PLAINTEXT,
        yop_sm2_priv,
        merchant_sm2_pub,
        app_key=NOTIFY_SM_APP_KEY,
        request_id=NOTIFY_SM_REQUEST_ID,
        timestamp=NOTIFY_SM_TIMESTAMP,
        uri=NOTIFY_SM_URI,
        sm4_key=bytes.fromhex(NOTIFY_SM4_KEY_HEX),
        iv=bytes.fromhex(NOTIFY_SM4_IV_HEX),
        sign_random_hex=SM_SIGN_RANDOM_HEX,
    )
    notify_sm_vector = {
        "plaintext": NOTIFY_SM_PLAINTEXT,
        "sm4_key_hex": NOTIFY_SM4_KEY_HEX,
        "sm4_iv_hex": NOTIFY_SM4_IV_HEX,
        "headers": headers,
        "body": body,
        "uri": NOTIFY_SM_URI,
    }
    NOTIFY_SM_VECTOR.write_text(
        json.dumps(notify_sm_vector, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    response_sm_vector = {
        "body": RESPONSE_BODY,
        "signature": sign_sm2_response(
            RESPONSE_BODY, yop_sm2_priv, random_hex=RESPONSE_SM_SIGN_RANDOM,
        ),
        "sign_random_hex": RESPONSE_SM_SIGN_RANDOM,
    }
    RESPONSE_SM_VECTOR.write_text(
        json.dumps(response_sm_vector, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"[regen] 已写入 {SIGN_VECTORS.name} / {NOTIFY_VECTOR.name} / {RESPONSE_VECTOR.name}")
    print(f"[regen] 已写入 {SIGN_SM_VECTORS.name} / {NOTIFY_SM_VECTOR.name} / {RESPONSE_SM_VECTOR.name}")
    print("[regen] 请同步更新 请求签名协议.md / 回调解密协议.md 的「完整示例」并提升 Skill 版本")


def verify() -> list[str]:
    errors: list[str] = []
    regen_hint = "先运行 python tools/verify_vectors.py --regen"
    for f in (MERCHANT_PRIVATE, YOP_PUBLIC, SIGN_VECTORS, NOTIFY_VECTOR, RESPONSE_VECTOR):
        if not f.exists():
            return [f"缺少向量文件：{f}（{regen_hint}）"]

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
    merchant_priv = rsa_notify_crypto.load_key(str(MERCHANT_PRIVATE), "private")
    yop_pub = rsa_notify_crypto.load_key(str(YOP_PUBLIC), "public")
    try:
        plain = rsa_notify_crypto.decrypt_notify(
            notify_vector["ciphertext"], merchant_priv, yop_pub)
        if plain != notify_vector["plaintext"]:
            errors.append("回调向量不匹配：解密明文与期望不一致")
    except ValueError as e:
        errors.append(f"回调向量解密失败：{e}")

    yop_priv = rsa_notify_crypto.load_key(str(YOP_PRIVATE), "private")
    merchant_pub = rsa_notify_crypto.load_key(str(MERCHANT_PUBLIC), "public")
    rebuilt = rsa_notify_crypto.encrypt_notify(
        notify_vector["plaintext"], yop_priv, merchant_pub,
        aes_key=bytes.fromhex(notify_vector["aes_key_hex"]))
    enc_data_expect = notify_vector["ciphertext"].split("$")[1]
    enc_data_actual = rebuilt.split("$")[1]
    if enc_data_actual != enc_data_expect:
        errors.append("回调向量不匹配：encData 段不可复现（AES/签名实现变更？）")

    response_vector = json.loads(RESPONSE_VECTOR.read_text(encoding="utf-8"))
    try:
        verify_rsa_response(
            response_vector["body"],
            response_vector["signature"],
            yop_pub,
        )
    except Exception as e:
        errors.append(f"RSA 应答验签向量失败：{e}")
    rebuilt_sig = sign_rsa_response(response_vector["body"], yop_priv)
    if rebuilt_sig != response_vector["signature"]:
        errors.append("RSA 应答签名向量不可复现")

    sm_files = (
        MERCHANT_SM2_PRIVATE, YOP_SM2_PUBLIC, SIGN_SM_VECTORS, NOTIFY_SM_VECTOR,
        RESPONSE_SM_VECTOR,
    )
    for f in sm_files:
        if not f.exists():
            errors.append(f"缺少 SM2 向量文件：{f}（{regen_hint}）")
            return errors

    sign_sm_vectors = json.loads(SIGN_SM_VECTORS.read_text(encoding="utf-8"))
    merchant_sm2_priv = load_sm2_private(str(MERCHANT_SM2_PRIVATE))
    for case in sign_sm_vectors["cases"]:
        actual = _compute_sm_sign_case(case, str(MERCHANT_SM2_PRIVATE))
        for field, expect in case["expected"].items():
            if actual.get(field) != expect:
                errors.append(
                    f"SM2 签名向量不匹配 [{case['name']}] 字段 {field}：\n"
                    f"  期望: {expect}\n  实际: {actual.get(field)}")

    notify_sm_vector = json.loads(NOTIFY_SM_VECTOR.read_text(encoding="utf-8"))
    header_map = dict(notify_sm_vector["headers"])
    header_map["_canonical_uri"] = notify_sm_vector.get("uri", "/notify")
    try:
        plain = sm_notify_crypto.decrypt_notify(
            header_map,
            notify_sm_vector["body"],
            merchant_sm2_priv,
            load_sm2_public(str(YOP_SM2_PUBLIC)),
        )
        if plain != notify_sm_vector["plaintext"]:
            errors.append("SM2 回调向量不匹配：解密明文与期望不一致")
    except ValueError as e:
        errors.append(f"SM2 回调向量解密失败：{e}")

    response_sm_vector = json.loads(RESPONSE_SM_VECTOR.read_text(encoding="utf-8"))
    yop_sm2_pub = load_sm2_public(str(YOP_SM2_PUBLIC))
    yop_sm2_priv = load_sm2_private(str(YOP_SM2_PRIVATE))
    try:
        verify_sm2_response(
            response_sm_vector["body"],
            response_sm_vector["signature"],
            yop_sm2_pub,
        )
    except Exception as e:
        errors.append(f"SM2 应答验签向量失败：{e}")
    rand = response_sm_vector.get("sign_random_hex", RESPONSE_SM_SIGN_RANDOM)
    rebuilt_sm_sig = sign_sm2_response(
        response_sm_vector["body"], yop_sm2_priv, random_hex=rand,
    )
    if rebuilt_sm_sig != response_sm_vector["signature"]:
        errors.append("SM2 应答签名向量不可复现")

    return errors


def main() -> int:
    ensure_python_version()
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
