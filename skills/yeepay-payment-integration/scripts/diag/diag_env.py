#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag 本地自检：跑任何其他 diag 脚本前先跑它。

检查 Python 版本、依赖、本地 token 状态与 yop-agent 连通性。
**不发送任何用户数据**：连通性探测只发一个空请求，不含原话、槽位或业务标识。

用法：
    python diag/diag_env.py [--env SANDBOX|PRODUCT] [--base-url http://...]
"""

import argparse
import importlib.util
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from diag._bootstrap import normalize_env, run  # noqa: E402
from diag import credentials, transport  # noqa: E402
from diag.errors import DiagError  # noqa: E402

REQUIRED = (("cryptography", "cryptography>=42.0.0"), ("requests", "requests>=2.31.0"), ("gmssl", "gmssl>=3.2.1"))


def main() -> int:
    parser = argparse.ArgumentParser(description="diag 本地自检（不外发用户数据）")
    parser.add_argument("--env", default="SANDBOX", help="SANDBOX / PRODUCT")
    parser.add_argument("--base-url", help="覆盖 yop-agent 地址")
    args = parser.parse_args()

    problems: list[str] = []
    print(f"Python: {sys.version.split()[0]}  OK")

    for module, spec in REQUIRED:
        if importlib.util.find_spec(module) is None:
            problems.append(f"缺少依赖 {module}（pip install -r scripts/requirements.txt）")
            print(f"依赖 {module}: 缺失")
        else:
            print(f"依赖 {module}: OK")

    entries = []
    try:
        entries = credentials.list_entries()
    except DiagError as exc:
        problems.append(exc.message)
        print(f"本地 token: {exc.message}")
    if entries:
        live = 0
        for entry in entries:
            expired = credentials.is_expired(entry)
            live += not expired
            print(
                f"本地 token: {entry['appKey']} @ {entry['environment']} "
                f"{credentials.mask(entry['accessToken'])} {'已过期' if expired else '有效'}"
                f"（{entry.get('expiresAt')}）"
            )
        if live > 1:
            # 多个有效凭证意味着「用哪个」有歧义，而用错应用查到的是别人的数据
            print(f"提示: 有 {live} 个有效凭证，排障前须与用户确认属于哪个应用，并用 --app-key 指定")
        if live:
            print("提示: 诊断凭证有效期 7 天，用户不再需要时应询问其是否吊销"
                  "（diag_auth.py --revoke），不要放着自然过期")
    elif not problems:
        print("本地 token: 无（需要远端诊断时先执行 diag/diag_auth.py 兑换）")

    environment = normalize_env(args.env)
    try:
        base_url = transport.resolve_base_url(environment, args.base_url)
    except DiagError as exc:
        print(f"yop-agent 地址: {exc.message}")
        problems.append(exc.message)
        base_url = None

    if base_url:
        print(f"yop-agent 地址: {base_url}")
        import requests

        try:
            resp = requests.post(
                transport.build_url(base_url, "/v1/auth/token"), json={}, timeout=(5, 10)
            )
            print(f"连通性: OK（HTTP {resp.status_code}，空请求，未发送任何用户数据）")
        except requests.RequestException as exc:
            msg = f"连不上 yop-agent：{type(exc).__name__}（请确认网络可达）"
            print(f"连通性: {msg}")
            problems.append(msg)

    if problems:
        print("\n自检未通过：")
        for item in problems:
            print(f"  - {item}")
        print("未通过时不要继续执行其他 diag 脚本；无法连通时按离线 L1 处理。")
        return 1
    print("\n自检通过。")
    return 0


if __name__ == "__main__":
    sys.exit(run(main))
