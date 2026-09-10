#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""兑换 / 吊销诊断 token。

用商户应用私钥对 appKey 原文签名换取 token（POST /v1/auth/token）。
算法按本地密钥类型自动选择（RSA→SHA256withRSA，SM2→SM3withSM2），
服务端按 appKey 在库中的密钥数据识别类型并验签。

**私钥只经文件路径读取，不出本机**；请求体只含 appKey、environment、signature。

用法：
    python diag/diag_auth.py --app-key app_100xxx --private-key ./keys/rsa_private_pkcs8.pem --env SANDBOX
    python diag/diag_auth.py --app-key app_100xxx --private-key ./keys/sm2_private_pkcs8.pem --env SANDBOX
    python diag/diag_auth.py --app-key app_100xxx --private-key <path> --env SANDBOX --revoke
    python diag/diag_auth.py --list

环境变量：YOP_APPKEY、YOP_PRIVATE_KEY（文件路径）、YOP_AGENT_BASE_URL
"""

import argparse
import json
import os
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from diag._bootstrap import normalize_env, run  # noqa: E402
from diag import credentials, transport  # noqa: E402
from diag.errors import EXIT_CREDENTIAL_EXISTS, EXIT_LOCAL_INVALID, EXIT_TOKEN_INVALID, DiagError  # noqa: E402
from diag.signer import read_app_key_from_config, read_key_file, sign_app_key  # noqa: E402


def _build_signature(app_key: str, key_arg: str, encoding: str, digest_suffix: bool) -> tuple[str, str]:
    path, pem, hint = read_key_file(key_arg, app_key)
    # 敏感动作必须可见
    print(f"[diag] 已读取 {path}，仅用于本地签名，未外发", file=sys.stderr)
    signature, key_type = sign_app_key(app_key, pem, encoding=encoding,
                                       digest_suffix=digest_suffix, hint=hint)
    print(f"[diag] 密钥类型 {key_type}，签名原文为 appKey 本身", file=sys.stderr)
    return signature, key_type


def main() -> int:
    parser = argparse.ArgumentParser(description="兑换 / 吊销 yop-agent 诊断 token")
    parser.add_argument("--app-key", default=os.environ.get("YOP_APPKEY"))
    parser.add_argument("--private-key", default=os.environ.get("YOP_PRIVATE_KEY"),
                        help="私钥文件路径，或 yop_sdk_config*.json 路径（只收路径，不收内容）")
    parser.add_argument("--env", default="SANDBOX", help="SANDBOX / PRODUCT")
    parser.add_argument("--base-url", help="覆盖 yop-agent 地址")
    parser.add_argument("--sig-encoding", choices=("urlsafe", "standard"), default="urlsafe",
                        help="签名值 Base64 编码；默认 urlsafe（yop-center 风格）")
    parser.add_argument("--no-digest-suffix", action="store_true",
                        help="不追加 $SHA256 / $SM3 后缀，直接传 Base64 值")
    parser.add_argument("--revoke", action="store_true", help="吊销该 appKey+环境的 token 并删除本地条目")
    parser.add_argument("--list", action="store_true", help="列出本地已存 token（掩码）")
    args = parser.parse_args()

    if args.list:
        entries = credentials.list_entries()
        if not entries:
            print("本地没有诊断 token")
            return 0
        for entry in entries:
            state = "已过期" if credentials.is_expired(entry) else "有效"
            print(f"{entry['appKey']} @ {entry['environment']}  "
                  f"{credentials.mask(entry['accessToken'])}  {state}  到期 {entry.get('expiresAt')}")
        return 0

    if not args.private_key:
        raise DiagError(EXIT_LOCAL_INVALID, "缺少 --private-key（私钥文件路径，或环境变量 YOP_PRIVATE_KEY）")
    if not args.app_key:
        # 传的是 yop_sdk_config 时，appKey 就在里面，不必让用户再抄一遍
        args.app_key = read_app_key_from_config(args.private_key)
        if args.app_key:
            print(f"[diag] 从配置文件读到 appKey={args.app_key}", file=sys.stderr)
    if not args.app_key:
        raise DiagError(EXIT_LOCAL_INVALID, "缺少 --app-key（或环境变量 YOP_APPKEY）")

    environment = normalize_env(args.env)
    base_url = transport.resolve_base_url(environment, args.base_url)
    signature, key_type = _build_signature(args.app_key, args.private_key,
                                          args.sig_encoding, not args.no_digest_suffix)
    payload = {"appKey": args.app_key, "environment": environment, "signature": signature}

    if args.revoke:
        try:
            transport.request("POST", base_url, "/v1/auth/revoke", payload=payload)
        except DiagError as exc:
            # 服务端已无该 token：本地条目同样清掉，这不是错误
            if exc.exit_code == EXIT_TOKEN_INVALID and "CREDENTIAL_NOT_FOUND" in exc.message:
                credentials.remove(args.app_key, environment)
                print(json.dumps({"revoked": True, "note": "服务端无该 token，已清理本地条目"},
                                 ensure_ascii=False))
                return 0
            raise
        credentials.remove(args.app_key, environment)
        print(json.dumps({"revoked": True, "appKey": args.app_key, "environment": environment},
                         ensure_ascii=False))
        return 0

    try:
        data = transport.request("POST", base_url, "/v1/auth/token", payload=payload)
    except DiagError as exc:
        if key_type == "SM2" and "签名校验失败" in exc.message:
            # SM2 服务端是支持的。同算法不同应用结果不同 → 失败原因在该应用的证书状态，
            # 不是算法。所以这里只补一句排查方向，不再替服务端认领问题。
            raise DiagError(
                exc.exit_code,
                f"{exc.message}；服务端支持 SM2（已有国密应用兑换成功），因此这多半是该 appKey "
                "自身的问题：核对私钥是否与平台报备的 SM2 证书配对、证书是否在有效期内。"
                "不要据此认为服务端不支持国密",
            )
        if exc.exit_code == EXIT_CREDENTIAL_EXISTS:
            local = credentials.find(args.app_key, environment)
            hint = ("本地已有该 token，可直接使用" if local and not credentials.is_expired(local)
                    else "本地没有可用条目：该 token 可能在另一台机器上。"
                         "确认不会影响他人后再执行 --revoke 重新兑换（不会自动吊销）")
            raise DiagError(EXIT_CREDENTIAL_EXISTS, f"{exc.message}；{hint}")
        raise

    entry = credentials.save(args.app_key, environment, data)
    print(json.dumps({
        "bound": {"appKey": entry["appKey"], "environment": entry["environment"]},
        "accessToken": credentials.mask(entry["accessToken"]),
        "expiresAt": entry["expiresAt"],
        "storedAt": str(credentials.STORE_PATH),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(run(main))
