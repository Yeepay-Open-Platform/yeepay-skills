#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""易宝 YOP API 应答验签（RSA / SM2）。

与 Java SDK YopSigner.checkSignature、YopRsaEncryptExample.verifyResponseSignature 对齐：
  1. 对响应 body 移除空格、制表符、换行后作为待验签原文
  2. 从 x-yop-sign 解析签名值与摘要算法（格式 {sig}$SHA256 或 {sig}$SM3）
  3. 签名值优先按 URL-safe Base64 解码；若含 + / = 则按标准 Base64 解码

文档：references/平台文档/平台规范/安全认证/请求签名协议.md §应答验签

被 rsa/client、sm/client、tools/verify_* 引用。
"""

from __future__ import annotations

import base64
import os
import re
import subprocess
import tempfile
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

HEADER_SIGN = "x-yop-sign"
HEADER_SERIAL = "x-yop-sign-serial-no"


class ResponseVerifyError(Exception):
    """应答验签失败。"""


def normalize_response_content(content: str) -> bytes:
    """移除 body 中的空格、制表符、换行（与 Java replaceAll(\"[ \\t\\n]\", \"\") 一致）。"""
    return re.sub(r"[ \t\n]", "", content).encode("utf-8")


def parse_yop_signature(signature: str) -> tuple[str, str, str | None]:
    parts = signature.split("$")
    if len(parts) not in (2, 4):
        raise ResponseVerifyError(f"x-yop-sign 格式非法：{signature!r}")
    serial = parts[3] if len(parts) == 4 else None
    return parts[0], parts[1], serial


def decode_signature_bytes(sig_value: str) -> bytes:
    """与 SDK 一致：含 + / = 时用标准 Base64，否则 URL-safe Base64。"""
    if any(ch in sig_value for ch in "+/="):
        pad = "=" * ((4 - len(sig_value) % 4) % 4)
        return base64.b64decode(sig_value + pad)
    s = sig_value.replace("-", "+").replace("_", "/")
    pad = "=" * ((4 - len(s) % 4) % 4)
    return base64.b64decode(s + pad)


def _get_header(headers, name: str) -> str | None:
    target = name.lower()
    for key, value in headers.items():
        if key.lower() == target:
            return value
    return None


def sign_rsa_response(content: str, private_key) -> str:
    """构造 x-yop-sign（RSA，供测试向量）。"""
    data = normalize_response_content(content)
    sig = private_key.sign(data, padding.PKCS1v15(), hashes.SHA256())
    b64 = base64.urlsafe_b64encode(sig).decode("ascii").rstrip("=")
    return f"{b64}$SHA256"


def verify_rsa_response(content: str, signature_header: str, public_key) -> None:
    sig_value, digest, _ = parse_yop_signature(signature_header)
    if digest != "SHA256":
        raise ResponseVerifyError(f"不支持的应答摘要算法：{digest}")
    data = normalize_response_content(content)
    sig_bytes = decode_signature_bytes(sig_value)
    try:
        public_key.verify(sig_bytes, data, padding.PKCS1v15(), hashes.SHA256())
    except InvalidSignature as e:
        raise ResponseVerifyError("RSA 应答验签失败") from e


def sign_sm2_response(content: str, private_hex: str, random_hex: str | None = None) -> str:
    from sm.crypto import sign_sm3

    return sign_sm3(normalize_response_content(content), private_hex, random_hex=random_hex)


def verify_sm2_response(content: str, signature_header: str, public_hex: str) -> None:
    from sm.crypto import verify_sm3

    sig_value, digest, _ = parse_yop_signature(signature_header)
    if digest != "SM3":
        raise ResponseVerifyError(f"不支持的应答摘要算法：{digest}")
    data = normalize_response_content(content)
    if not verify_sm3(data, signature_header, public_hex):
        raise ResponseVerifyError("SM2 应答验签失败")


def _read_text(path_or_pem: str) -> str:
    if os.path.isfile(path_or_pem):
        return Path(path_or_pem).read_text(encoding="utf-8").strip()
    return path_or_pem.strip()


def _sm2_hex_from_cert_pem(cert_pem: str) -> str:
    from sm.crypto import load_sm2_public

    with tempfile.NamedTemporaryFile(suffix=".cer.pem", delete=False, mode="w", encoding="utf-8") as tmp:
        tmp.write(cert_pem if cert_pem.endswith("\n") else cert_pem + "\n")
        cert_path = tmp.name
    try:
        proc = subprocess.run(
            ["openssl", "x509", "-in", cert_path, "-pubkey", "-noout"],
            check=True,
            capture_output=True,
            text=True,
        )
    finally:
        os.unlink(cert_path)
    return load_sm2_public(proc.stdout)


def resolve_sm2_public_hex(
    yop_pubkey: str | None,
    cert_dir: str | Path | None,
    serial_no: str | None,
) -> str:
    """按 x-yop-sign-serial-no 从 cert_dir 选公钥，否则用 yop_pubkey（PEM 公钥或证书）。"""
    if cert_dir and serial_no:
        base = Path(cert_dir)
        candidates = [
            base / f"yop_sm2_{serial_no}_public.pem",
            base / f"yop_sm2_{serial_no}.cer.pem",
        ]
        for path in candidates:
            if path.is_file():
                text = path.read_text(encoding="utf-8")
                if "CERTIFICATE" in text:
                    return _sm2_hex_from_cert_pem(text)
                from sm.crypto import load_sm2_public
                return load_sm2_public(text)

    if not yop_pubkey:
        raise ResponseVerifyError(
            "SM2 验签需要 --yop-pubkey / YOP_PLATFORM_PUBLIC_KEY，或 --cert-dir 下存在对应序列号证书"
        )
    text = _read_text(yop_pubkey)
    if "CERTIFICATE" in text:
        return _sm2_hex_from_cert_pem(text)
    from sm.crypto import load_sm2_public
    return load_sm2_public(text)


def verify_http_response(
    response,
    *,
    algorithm: str = "rsa",
    yop_pubkey: str | None = None,
    cert_dir: str | Path | None = None,
    strict_missing: bool = False,
) -> bool:
    """对 requests.Response 验签。无 x-yop-sign 时默认跳过，返回 False；验签通过返回 True。"""
    signature = _get_header(response.headers, HEADER_SIGN)
    if not signature or not signature.strip():
        if strict_missing:
            raise ResponseVerifyError("响应缺少 x-yop-sign 头")
        return False

    content = response.text
    algo = algorithm.lower()
    if algo in ("rsa", "rsa2048"):
        if not yop_pubkey:
            raise ResponseVerifyError("RSA 验签需要平台公钥（--yop-pubkey / YOP_PLATFORM_PUBLIC_KEY）")
        from rsa.notify_crypto import load_key

        verify_rsa_response(content, signature, load_key(yop_pubkey, "public"))
        return True

    if algo in ("sm", "sm2"):
        serial = _get_header(response.headers, HEADER_SERIAL)
        pub_hex = resolve_sm2_public_hex(yop_pubkey, cert_dir, serial)
        verify_sm2_response(content, signature, pub_hex)
        return True

    raise ValueError(f"不支持的 algorithm: {algorithm}")
