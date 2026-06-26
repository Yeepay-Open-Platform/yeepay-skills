#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SM2/SM3/SM4 国密联调工具（基于 gmssl SM2P256V1）。

签名/验签使用 gmssl CryptSM2.sign_with_sm3 / verify_with_sm3（SM3withSM2，默认 userId）。
SM2 加解密 mode=C1C3C2；SM4 使用 CBC/PKCS7（与 Java PKCS5Padding 对齐）。
"""

import base64
import os
import re
import secrets
import subprocess
import tempfile
from pathlib import Path

from gmssl import func, sm2, sm3, sm4

PROTOCOL_VERSION = "yop-auth-v3"
SECURITY_REQ = "YOP-SM2-SM3"
DIGEST_SUFFIX = "$SM3"
SM2_MODE_C1C3C2 = 1
DEFAULT_USER_ID = b"1234567812345678"
EC_PUBLIC_KEY_OID = "1.2.840.10045.2.1"
SM2_CURVE_OID = "1.2.156.10197.1.301"


def _encode_der_length(length: int) -> bytes:
    if length < 0x80:
        return bytes([length])
    nbytes = (length.bit_length() + 7) // 8
    return bytes([0x80 | nbytes]) + length.to_bytes(nbytes, "big")


def _encode_der_oid(oid: str) -> bytes:
    parts = [int(x) for x in oid.split(".")]
    body = bytearray([40 * parts[0] + parts[1]])
    for value in parts[2:]:
        if value == 0:
            body.append(0)
            continue
        stack: list[int] = []
        while value:
            stack.append(value & 0x7F)
            value >>= 7
        for i, b in enumerate(reversed(stack)):
            body.append(b | (0x80 if i < len(stack) - 1 else 0))
    content = bytes(body)
    return b"\x06" + _encode_der_length(len(content)) + content


def _encode_der_integer(value: int) -> bytes:
    if value == 0:
        content = b"\x00"
    else:
        content = value.to_bytes((value.bit_length() + 7) // 8, "big")
        if content[0] & 0x80:
            content = b"\x00" + content
    return b"\x02" + _encode_der_length(len(content)) + content


def _encode_der_octet_string(data: bytes) -> bytes:
    return b"\x04" + _encode_der_length(len(data)) + data


def _encode_der_bit_string(data: bytes) -> bytes:
    content = b"\x00" + data
    return b"\x03" + _encode_der_length(len(content)) + content


def _encode_der_sequence(items: list[bytes]) -> bytes:
    body = b"".join(items)
    return b"\x30" + _encode_der_length(len(body)) + body


def _encode_der_context(tag: int, content: bytes) -> bytes:
    return bytes([0xA0 | tag]) + _encode_der_length(len(content)) + content


def _encode_sm2_algorithm_identifier() -> bytes:
    return _encode_der_sequence([
        _encode_der_oid(EC_PUBLIC_KEY_OID),
        _encode_der_oid(SM2_CURVE_OID),
    ])


def _export_sm2_private_pkcs8_der(priv_hex: str, pub_hex: str | None = None) -> bytes:
    priv_bytes = bytes.fromhex(priv_hex)
    pub_hex = pub_hex or _derive_public_hex(priv_hex)
    pub_point = bytes.fromhex("04" + pub_hex)
    ec_private = _encode_der_sequence([
        _encode_der_integer(1),
        _encode_der_octet_string(priv_bytes),
        _encode_der_context(1, _encode_der_bit_string(pub_point)),
    ])
    return _encode_der_sequence([
        _encode_der_integer(0),
        _encode_sm2_algorithm_identifier(),
        _encode_der_octet_string(ec_private),
    ])


def _export_sm2_public_spki_der(pub_hex: str) -> bytes:
    pub_point = bytes.fromhex("04" + pub_hex)
    return _encode_der_sequence([
        _encode_sm2_algorithm_identifier(),
        _encode_der_bit_string(pub_point),
    ])


def _to_pem(label: str, der: bytes) -> bytes:
    body = base64.encodebytes(der).decode("ascii")
    return f"-----BEGIN {label}-----\n{body}-----END {label}-----\n".encode("ascii")


def export_sm2_private_pem(priv_hex: str, pub_hex: str | None = None) -> bytes:
    return _to_pem("PRIVATE KEY", _export_sm2_private_pkcs8_der(priv_hex, pub_hex))


def export_sm2_public_pem(pub_hex: str) -> bytes:
    return _to_pem("PUBLIC KEY", _export_sm2_public_spki_der(pub_hex))



def urlsafe_b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def urlsafe_b64decode(data: str) -> bytes:
    s = data.replace("-", "+").replace("_", "/")
    pad = "=" * ((4 - len(s) % 4) % 4)
    return base64.b64decode(s + pad)


def sm3_hex(data: bytes) -> str:
    return sm3.sm3_hash(func.bytes_to_list(data))


def generate_sm2_keypair():
    """生成 SM2P256V1 密钥对（内部为 hex，导出见 export_sm2_*_pem）。"""
    table = sm2.default_ecc_table
    order = int(table["n"], 16)
    generator = table["g"]
    hex_len = len(table["n"])
    helper = sm2.CryptSM2(
        private_key="1" * hex_len,
        public_key="0" * (hex_len * 2),
    )
    probe = b"yeepay-sm2-keygen-check"

    for _ in range(32):
        scalar = secrets.randbelow(order - 1) + 1
        priv_hex = format(scalar, f"0{hex_len}x")
        pub_hex = helper._kg(scalar, generator)
        crypt = sm2.CryptSM2(private_key=priv_hex, public_key=pub_hex)
        sig = crypt.sign_with_sm3(probe, func.random_hex(hex_len))
        if crypt.verify_with_sm3(sig, probe):
            return priv_hex, pub_hex

    raise RuntimeError("SM2 密钥生成失败")


def _read_text(path_or_text: str) -> str:
    if os.path.isfile(path_or_text):
        return Path(path_or_text).read_text(encoding="utf-8").strip()
    return path_or_text.strip()


def _pem_body(text: str) -> str:
    return "".join(
        line.strip()
        for line in text.splitlines()
        if line and "BEGIN" not in line and "END" not in line
    )


def _pkcs8_to_private_hex(pkcs8_b64: str) -> str:
    der = base64.b64decode(pkcs8_b64.strip())
    with tempfile.NamedTemporaryFile(suffix=".pk8", delete=False) as tmp:
        tmp.write(der)
        tmp_path = tmp.name
    try:
        out = subprocess.check_output(
            ["openssl", "ec", "-inform", "DER", "-in", tmp_path, "-text", "-noout"],
            text=True,
        )
    finally:
        os.unlink(tmp_path)
    block = re.search(r"priv:\n((?:\s+[0-9a-f:]+\n)+)", out)
    if not block:
        raise ValueError("无法从 PKCS8 解析 SM2 私钥")
    return "".join(re.findall(r"[0-9a-f]{2}", block.group(1)))


def load_sm2_private(path_or_pem: str) -> str:
    text = _read_text(path_or_pem)
    if "BEGIN" not in text:
        raise ValueError("SM2 私钥须为 PKCS8 PEM 文件或 PEM 文本（BEGIN PRIVATE KEY）")
    return _pkcs8_to_private_hex(_pem_body(text))


def load_sm2_public(path_or_pem: str) -> str:
    text = _read_text(path_or_pem)
    if "BEGIN" not in text:
        raise ValueError("SM2 公钥须为 SPKI PEM 文件或 PEM 文本（BEGIN PUBLIC KEY）")
    der = base64.b64decode(_pem_body(text))
    with tempfile.NamedTemporaryFile(suffix=".pub.der", delete=False) as tmp:
        tmp.write(der)
        tmp_path = tmp.name
    try:
        out = subprocess.check_output(
            ["openssl", "ec", "-pubin", "-inform", "DER", "-in", tmp_path, "-text", "-noout"],
            text=True,
        )
    finally:
        os.unlink(tmp_path)
    block = re.search(r"pub:\n((?:\s+[0-9a-f:]+\n)+)", out)
    if not block:
        raise ValueError("无法从 PEM 解析 SM2 公钥")
    return "".join(re.findall(r"[0-9a-f]{2}", block.group(1)))[2:]


def crypt_sm2(private_hex: str | None, public_hex: str | None) -> sm2.CryptSM2:
    return sm2.CryptSM2(
        private_key=private_hex or ("1" * 64),
        public_key=public_hex or ("0" * 128),
        mode=SM2_MODE_C1C3C2,
    )


def _derive_public_hex(private_hex: str) -> str:
    table = sm2.default_ecc_table
    scalar = int(private_hex, 16)
    helper = sm2.CryptSM2(private_key="1" * 64, public_key="0" * 128)
    return helper._kg(scalar, table["g"])


def sign_sm3(message: bytes, private_hex: str, random_hex: str | None = None) -> str:
    pub_hex = _derive_public_hex(private_hex)
    crypt = crypt_sm2(private_hex, pub_hex)
    k = random_hex or func.random_hex(64)
    sig_hex = crypt.sign_with_sm3(message, k)
    return urlsafe_b64encode(bytes.fromhex(sig_hex)) + DIGEST_SUFFIX


def verify_sm3(message: bytes, signature: str, public_hex: str) -> bool:
    sig_part = signature.split("$", 1)[0]
    sig_hex = urlsafe_b64decode(sig_part).hex()
    return crypt_sm2(None, public_hex).verify_with_sm3(sig_hex, message)


def sm2_encrypt(data: bytes, public_hex: str) -> bytes:
    return crypt_sm2(None, public_hex).encrypt(data)


def sm2_decrypt(ciphertext: bytes, private_hex: str) -> bytes:
    return crypt_sm2(private_hex, None).decrypt(ciphertext)


def sm4_cbc_encrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    crypt = sm4.CryptSM4()
    crypt.set_key(list(key), sm4.SM4_ENCRYPT)
    return crypt.crypt_cbc(iv, data)


def sm4_cbc_decrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    crypt = sm4.CryptSM4()
    crypt.set_key(list(key), sm4.SM4_DECRYPT)
    return crypt.crypt_cbc(iv, data)
