# -*- coding: utf-8 -*-
"""diag CLI 的公共启动逻辑：路径、版本校验、错误退出。"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from common.python_version import ensure_python_version  # noqa: E402

from diag.errors import EXIT_HINT, DiagError  # noqa: E402


def run(main_func) -> int:
    """统一入口：版本校验 + DiagError → 退出码 + 行为提示。"""
    ensure_python_version()
    try:
        return main_func()
    except DiagError as exc:
        print(f"[diag] {exc.message}", file=sys.stderr)
        hint = EXIT_HINT.get(exc.exit_code)
        if hint:
            print(f"[diag] exit={exc.exit_code} 处理：{hint}", file=sys.stderr)
        return exc.exit_code
    except KeyboardInterrupt:
        print("[diag] 已取消", file=sys.stderr)
        return 130


def normalize_env(value: str | None) -> str:
    """环境归一化，与服务端一致：QA/TEST→SANDBOX，PROD/PRODUCTION→PRODUCT。"""
    from diag.errors import EXIT_LOCAL_INVALID

    if not value:
        raise DiagError(EXIT_LOCAL_INVALID, "缺少环境参数：--env SANDBOX|PRODUCT")
    upper = value.strip().upper()
    if upper in ("SANDBOX", "QA", "TEST"):
        return "SANDBOX"
    if upper in ("PRODUCT", "PROD", "PRODUCTION"):
        return "PRODUCT"
    raise DiagError(EXIT_LOCAL_INVALID, f"未知环境 {value}：只接受 SANDBOX 或 PRODUCT")
