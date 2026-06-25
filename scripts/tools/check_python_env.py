#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验 scripts 运行环境：Python 版本与第三方依赖。

本脚本语法保持 3.7+ 兼容，可在低版本 Python 上运行并给出升级引导；
scripts 其余联调工具须 Python >= 3.10。

在 scripts/ 目录下执行：
    python tools/check_python_env.py
"""

import importlib.util
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from common.python_version import (  # noqa: E402
    format_current_python,
    format_min_python,
    python_version_ok,
    upgrade_hint,
)

REQUIRED_PACKAGES = (
    ("cryptography", "cryptography>=42.0.0"),
    ("requests", "requests>=2.31.0"),
    ("gmssl", "gmssl>=3.2.1"),
)


def check_python() -> list[str]:
    if python_version_ok():
        print("[OK] Python {} (requires >= {})".format(
            format_current_python(), format_min_python()))
        return []
    return upgrade_hint().splitlines()


def check_packages() -> list[str]:
    issues = []
    for module, pip_spec in REQUIRED_PACKAGES:
        if importlib.util.find_spec(module) is None:
            issues.append(
                "缺少依赖 {}，请执行: pip install -r requirements.txt".format(
                    pip_spec.split(">=")[0]))
        else:
            print("[OK] {}".format(module))
    return issues


def main() -> int:
    print("=== YOP scripts 环境校验 ===\n")
    issues = check_python()
    if issues:
        for line in issues:
            print("[FAIL] {}".format(line))
        return 1

    print()
    issues = check_packages()
    if issues:
        for line in issues:
            print("[FAIL] {}".format(line))
        print("\n安装：cd scripts && pip install -r requirements.txt")
        return 1

    print("\n环境就绪，可运行 scripts/ 下联调工具。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
