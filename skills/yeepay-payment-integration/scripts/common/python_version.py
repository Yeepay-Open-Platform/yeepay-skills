"""Python 运行时版本校验。

本模块语法保持 3.7+ 兼容，供 check_python_env 与各 CLI 入口共用。
scripts 其余代码须 Python >= 3.10（PEP 604 联合类型等）。
"""

import sys

MIN_PYTHON = (3, 10)


def format_current_python() -> str:
    return "{}.{}.{}".format(*sys.version_info[:3])


def format_min_python() -> str:
    return "{}.{}.0".format(*MIN_PYTHON)


def python_version_ok() -> bool:
    return sys.version_info >= MIN_PYTHON


def upgrade_hint() -> str:
    return (
        "scripts 需要 Python >= {}，当前 {}。\n"
        "请先升级 Python（推荐 3.10+ LTS），或在 scripts/ 目录执行:\n"
        "  python tools/check_python_env.py\n"
        "安装参考: https://www.python.org/downloads/"
    ).format(format_min_python(), format_current_python())


def ensure_python_version() -> None:
    if not python_version_ok():
        print(upgrade_hint(), file=sys.stderr)
        raise SystemExit(1)
