#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RSA 结果通知密文编解码（四段 $ 格式）。

与 references/平台文档/平台规范/安全认证/回调解密协议.md、
YopRsaCallbackExample.java 步骤一致；仅用于联调验证。
"""

import base64
import os
import secrets

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

SEPARATOR = "$"
AES_ALG = "AES"
DIGEST_ALG = "SHA256"


def _b64decode(data: str) -> bytes:
    pad = "=" * (-len(data) % 4)
    return base64.b64decode(data + pad)


def _b64encode(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def load_private_key(pem: str):
    pem = pem.strip()
    if "BEGIN" not in pem:
        pem = (
            "-----BEGIN PRIVATE KEY-----\n"
            + "\n".join(pem[i : i + 64] for i in range(0, len(pem), 64))
            + "\n-----END PRIVATE KEY-----\n"
        )
    return serialization.load_pem_private_key(pem.encode("utf-8"), password=None)


def load_public_key(pem: str):
    pem = pem.strip()
    if "BEGIN" not in pem:
        pem = (
            "-----BEGIN PUBLIC KEY-----\n"
            + "\n".join(pem[i : i + 64] for i in range(0, len(pem), 64))
            + "\n-----END PUBLIC KEY-----\n"
        )
    return serialization.load_pem_public_key(pem.encode("utf-8"))


def load_key(path_or_pem: str, kind: str):
    text = open(path_or_pem, encoding="utf-8").read() if os.path.isfile(path_or_pem) else path_or_pem
    return load_private_key(text) if kind == "private" else load_public_key(text)


def _rsa_encrypt(data: bytes, public_key) -> bytes:
    return public_key.encrypt(data, padding.PKCS1v15())


def _rsa_decrypt(data: bytes, private_key) -> bytes:
    return private_key.decrypt(data, padding.PKCS1v15())


def _aes_encrypt(data: bytes, key: bytes) -> bytes:
    # 与 Java AES/ECB/PKCS5Padding 对齐：随机 key 16 字节，明文 PKCS7 填充
    pad_len = 16 - (len(data) % 16)
    padded = data + bytes([pad_len] * pad_len)
    cipher = Cipher(algorithms.AES(key), modes.ECB())
    enc = cipher.encryptor()
    return enc.update(padded) + enc.finalize()


def _aes_decrypt(data: bytes, key: bytes) -> bytes:
    cipher = Cipher(algorithms.AES(key), modes.ECB())
    dec = cipher.decryptor()
    padded = dec.update(data) + dec.finalize()
    pad_len = padded[-1]
    if pad_len < 1 or pad_len > 16:
        raise ValueError("AES 解密失败：填充非法")
    return padded[:-pad_len]


def _sign(source: bytes, private_key) -> bytes:
    return private_key.sign(source, padding.PKCS1v15(), hashes.SHA256())


def _verify(source: bytes, signature: bytes, public_key) -> bool:
    try:
        public_key.verify(signature, source, padding.PKCS1v15(), hashes.SHA256())
        return True
    except Exception:
        return False


def encrypt_notify(plaintext: str, yop_private_key, merchant_public_key,
                   aes_key: bytes = None) -> str:
    """构造四段密文：encRandomKey$encData$AES$SHA256

    aes_key 可显式传入以复现固定测试向量（见 rsa/tests/vectors/）。
    """
    sign = _sign(plaintext.encode("utf-8"), yop_private_key)
    inner = plaintext + SEPARATOR + _b64encode(sign)
    aes_key = aes_key or secrets.token_bytes(16)
    enc_data = _aes_encrypt(inner.encode("utf-8"), aes_key)
    enc_key = _rsa_encrypt(aes_key, merchant_public_key)
    return SEPARATOR.join([_b64encode(enc_key), _b64encode(enc_data), AES_ALG, DIGEST_ALG])


def decrypt_notify(ciphertext: str, merchant_private_key, yop_public_key) -> str:
    """解密并验签，失败抛 ValueError 并注明环节。"""
    parts = ciphertext.split(SEPARATOR)
    if len(parts) != 4:
        raise ValueError(f"格式拆分失败：期望 4 段，实际 {len(parts)} 段")

    enc_key_b64, enc_data_b64, sym_alg, digest_alg = parts
    if sym_alg != AES_ALG:
        raise ValueError(f"对称算法不支持：{sym_alg}")
    if digest_alg != DIGEST_ALG:
        raise ValueError(f"摘要算法不支持：{digest_alg}")

    try:
        aes_key = _rsa_decrypt(_b64decode(enc_key_b64), merchant_private_key)
    except Exception as e:
        raise ValueError(f"RSA 解随机密钥失败：{e}") from e

    try:
        inner = _aes_decrypt(_b64decode(enc_data_b64), aes_key).decode("utf-8")
    except Exception as e:
        raise ValueError(f"AES 解数据失败：{e}") from e

    if SEPARATOR not in inner:
        raise ValueError("拆签失败：明文内无 $ 分隔符")
    source_data, sign_b64 = inner.rsplit(SEPARATOR, 1)
    try:
        signature = _b64decode(sign_b64)
    except Exception as e:
        raise ValueError(f"签名 Base64 解码失败：{e}") from e

    if not _verify(source_data.encode("utf-8"), signature, yop_public_key):
        raise ValueError("验签失败：公钥不匹配或数据被篡改")

    return source_data
