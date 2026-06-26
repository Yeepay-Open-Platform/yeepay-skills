#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SM2 结果通知加解密（x-yop-encrypt + Authorization）。

与 references/平台文档/平台规范/安全认证/回调解密协议.md（SM2 章节）对齐，用于联调验证。
"""

import secrets

from .crypto import (
    PROTOCOL_VERSION,
    SECURITY_REQ,
    sign_sm3,
    sm2_decrypt,
    sm2_encrypt,
    sm3_hex,
    sm4_cbc_decrypt,
    sm4_cbc_encrypt,
    urlsafe_b64decode,
    urlsafe_b64encode,
    verify_sm3,
)

ENCRYPT_PROTOCOL = "yop-encrypt-v1"
ENCRYPT_ALG = "SM4_CBC_PKCS5Padding"


def _normalize(value: str) -> str:
    """回调 canonical header 使用的 RFC3986 编码（与 Java SDK 示例一致）。"""
    unreserved = set(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~"
    )
    out = []
    for ch in value:
        if ch in unreserved:
            out.append(ch)
        else:
            out.append("".join(f"%{b:02X}" for b in ch.encode("utf-8")))
    return "".join(out)


def _build_callback_canonical(auth_string: str, signed_headers: str, headers: dict) -> str:
    lines = []
    for name in signed_headers.split(";"):
        key = name.strip().lower()
        value = headers.get(key, "")
        if not value:
            continue
        lines.append(f"{_normalize(key)}:{_normalize(value.strip())}")
    lines.sort()
    return "\n".join([
        auth_string,
        "POST",
        headers.get("_canonical_uri", "/"),
        "",
        "\n".join(lines),
    ])


def build_encrypt_header(
    encrypted_key_b64: str,
    iv_b64: str,
    platform_serial: str = "",
    encrypt_params_b64: str = "JA",
) -> str:
    return (
        f"{ENCRYPT_PROTOCOL}/{platform_serial}/{ENCRYPT_ALG}/"
        f"{encrypted_key_b64}/{iv_b64};/stream//{encrypt_params_b64}"
    )


def encrypt_notify(
    plaintext: str,
    yop_private_hex: str,
    merchant_public_hex: str,
    *,
    app_key: str,
    request_id: str,
    timestamp: str,
    expire_seconds: int = 1800,
    uri: str = "/notify",
    platform_serial: str = "",
    sm4_key: bytes | None = None,
    iv: bytes | None = None,
    sign_random_hex: str | None = None,
) -> tuple[dict, str]:
    """构造 SM2 回调（headers + 加密 body）。"""
    sm4_key = sm4_key or secrets.token_bytes(16)
    iv = iv or secrets.token_bytes(16)

    cipher = sm4_cbc_encrypt(plaintext.encode("utf-8"), sm4_key, iv)
    body = urlsafe_b64encode(cipher)
    enc_key = urlsafe_b64encode(sm2_encrypt(sm4_key, merchant_public_hex))
    iv_b64 = urlsafe_b64encode(iv)
    encrypt_header = build_encrypt_header(enc_key, iv_b64, platform_serial)

    content_length = str(len(body.encode("utf-8")))
    content_sm3 = sm3_hex(body.encode("utf-8"))

    auth_string = f"{PROTOCOL_VERSION}/{app_key}/{timestamp}/{expire_seconds}"
    signed_header_names = sorted([
        "content-length",
        "content-type",
        "x-yop-content-sm3",
        "x-yop-encrypt",
        "x-yop-request-id",
    ])
    signed_headers = ";".join(signed_header_names)

    header_map = {
        "content-length": content_length,
        "content-type": "application/json",
        "x-yop-appkey": app_key,
        "x-yop-content-sm3": content_sm3,
        "x-yop-encrypt": encrypt_header,
        "x-yop-request-id": request_id,
        "_canonical_uri": uri,
    }
    if platform_serial:
        header_map["x-yop-sign-serial-no"] = platform_serial

    canonical = _build_callback_canonical(auth_string, signed_headers, header_map)
    signature = sign_sm3(canonical.encode("utf-8"), yop_private_hex, random_hex=sign_random_hex)
    authorization = f"{SECURITY_REQ} {auth_string}/{signed_headers}/{signature}"

    headers = {
        "Authorization": authorization,
        "Content-Type": "application/json",
        "Content-Length": content_length,
        "x-yop-appkey": app_key,
        "x-yop-content-sm3": content_sm3,
        "x-yop-encrypt": encrypt_header,
        "x-yop-request-id": request_id,
    }
    if platform_serial:
        headers["x-yop-sign-serial-no"] = platform_serial
    return headers, body


def decrypt_notify(
    headers: dict,
    body: str,
    merchant_private_hex: str,
    yop_public_hex: str,
) -> str:
    """解密 SM2 回调并验签，失败抛 ValueError。"""
    lower = {k.lower(): v for k, v in headers.items()}
    authorization = lower.get("authorization", "")
    if not authorization.startswith(SECURITY_REQ):
        raise ValueError(f"Authorization 非 {SECURITY_REQ}")

    parts = authorization[len(SECURITY_REQ):].strip().split("/")
    if len(parts) < 6:
        raise ValueError("Authorization 格式错误")
    auth_string = "/".join(parts[0:4])
    signed_headers = parts[4]
    signature = parts[5]

    header_map = dict(lower)
    header_map["_canonical_uri"] = header_map.get("_canonical_uri", "/notify")
    canonical = _build_callback_canonical(auth_string, signed_headers, header_map)
    if not verify_sm3(canonical.encode("utf-8"), signature, yop_public_hex):
        raise ValueError("验签失败：公钥不匹配或数据被篡改")

    content_sm3 = lower.get("x-yop-content-sm3", "")
    if content_sm3 and sm3_hex(body.encode("utf-8")) != content_sm3.lower():
        raise ValueError("x-yop-content-sm3 与 body 摘要不一致")

    encrypt_header = lower.get("x-yop-encrypt", "")
    segments = encrypt_header.split("/")
    if len(segments) < 5:
        raise ValueError("x-yop-encrypt 格式错误")
    enc_key_b64 = segments[3]
    iv_part = segments[4].split(";")[0]
    sm4_key = sm2_decrypt(urlsafe_b64decode(enc_key_b64), merchant_private_hex)
    if len(sm4_key) != 16:
        raise ValueError(f"SM2 解 SM4 密钥长度异常：{len(sm4_key)}")
    iv = urlsafe_b64decode(iv_part)
    plain = sm4_cbc_decrypt(urlsafe_b64decode(body), sm4_key, iv)
    return plain.decode("utf-8")
