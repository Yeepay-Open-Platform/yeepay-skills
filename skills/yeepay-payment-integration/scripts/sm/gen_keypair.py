#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 SM2 密钥对，用于易宝国密接入联调。

用法：
    python sm/gen_keypair.py --out ./keys

依赖：gmssl（pip install gmssl），曲线 SM2P256V1（GB/T 32918）

生成文件：
    sm2_private_pkcs8.pem / sm2_public.pem   # PKCS8 / SPKI PEM（与 RSA 密钥文件格式一致）
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
from sm.crypto import export_sm2_private_pem, export_sm2_public_pem, generate_sm2_keypair


def _write(out_dir: str, name: str, data: bytes):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name)
    with open(path, "wb") as f:
        f.write(data)
    os.chmod(path, 0o600)


def main():
    ensure_python_version()
    p = argparse.ArgumentParser(description="生成 SM2 密钥对")
    p.add_argument("--out", default="./keys", help="输出目录")
    args = p.parse_args()

    try:
        import gmssl  # noqa: F401
    except ImportError:
        raise SystemExit("缺少依赖 gmssl：pip install gmssl")

    priv_hex, pub_hex = generate_sm2_keypair()
    _write(args.out, "sm2_private_pkcs8.pem", export_sm2_private_pem(priv_hex, pub_hex))
    _write(args.out, "sm2_public.pem", export_sm2_public_pem(pub_hex))
    print("[SM2] 已生成 sm2_private_pkcs8.pem / sm2_public.pem")
    print("[SM2] 曲线 SM2P256V1（PKCS8/SPKI PEM）；与 rsa/gen_keypair.py 输出格式一致。")
    print("[SM2] 生产环境商密接入须使用 CFCA 证书，见 references/平台文档/接入准备/密钥管理/CFCA证书介绍.md。")


if __name__ == "__main__":
    main()
