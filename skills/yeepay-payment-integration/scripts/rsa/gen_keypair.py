#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 RSA2048 密钥对，用于易宝接入联调。

用法：
    python rsa/gen_keypair.py --out ./keys

依赖：cryptography

生成文件：
    rsa_private_pkcs8.pem / rsa_public.pem
私钥仅用于本地联调，切勿提交仓库或泄露。
"""

import argparse
import os
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from common.python_version import ensure_python_version


def gen_rsa(out_dir: str):
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    priv = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pub = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    _write(out_dir, "rsa_private_pkcs8.pem", priv)
    _write(out_dir, "rsa_public.pem", pub)
    print("[RSA] 已生成 rsa_private_pkcs8.pem / rsa_public.pem")
    print("[RSA] 商户私钥用于请求签名；将 rsa_public.pem 配置到易宝开放平台。")


def _write(out_dir: str, name: str, data: bytes):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name)
    with open(path, "wb") as f:
        f.write(data)
    os.chmod(path, 0o600)


def main():
    ensure_python_version()
    p = argparse.ArgumentParser(description="生成 RSA 密钥对")
    p.add_argument("--out", default="./keys", help="输出目录")
    args = p.parse_args()
    gen_rsa(args.out)


if __name__ == "__main__":
    main()
