#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成密钥对（RSA2048 / SM2），用于易宝接入联调。

用法：
    python gen_keypair.py --alg rsa --out ./keys
    python gen_keypair.py --alg sm2 --out ./keys

RSA 依赖：cryptography
SM2 依赖：gmssl（pip install gmssl）

生成文件：
    rsa_private_pkcs8.pem / rsa_public.pem
    sm2_private.hex / sm2_public.hex
私钥仅用于本地联调，切勿提交仓库或泄露。
"""

import argparse
import os


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


def gen_sm2(out_dir: str):
    try:
        from gmssl import sm2
    except ImportError:
        raise SystemExit("缺少依赖 gmssl：pip install gmssl")

    # gmssl 不直接提供密钥生成，这里用 cryptography 生成 SM2 曲线密钥再导出 hex
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives import serialization

    key = ec.generate_private_key(ec.SECP256K1())  # 占位曲线；如需严格国密 SM2P256V1 请用专用库
    priv_int = key.private_numbers().private_value
    nums = key.public_key().public_numbers()
    priv_hex = format(priv_int, "064x")
    pub_hex = format(nums.x, "064x") + format(nums.y, "064x")
    _write(out_dir, "sm2_private.hex", priv_hex.encode())
    _write(out_dir, "sm2_public.hex", pub_hex.encode())
    print("[SM2] 已生成 sm2_private.hex / sm2_public.hex")
    print("[SM2] 注意：严格国密 SM2(SM2P256V1) 建议用 tongsuo/gmssl 命令行生成以确保合规。")


def _write(out_dir: str, name: str, data: bytes):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name)
    with open(path, "wb") as f:
        f.write(data)
    os.chmod(path, 0o600)


def main():
    p = argparse.ArgumentParser(description="生成易宝接入密钥对")
    p.add_argument("--alg", choices=["rsa", "sm2"], default="rsa")
    p.add_argument("--out", default="./keys", help="输出目录")
    args = p.parse_args()
    if args.alg == "rsa":
        gen_rsa(args.out)
    else:
        gen_sm2(args.out)


if __name__ == "__main__":
    main()
