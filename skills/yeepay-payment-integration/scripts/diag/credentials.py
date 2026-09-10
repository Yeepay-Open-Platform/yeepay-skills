# -*- coding: utf-8 -*-
"""诊断 token 的本地存储。

位置固定 ~/.yeepay/diag/credentials.json，权限 0600，按 appKey + environment 多条目。
不写项目目录、不进 git、不存 signature、不回显完整 token。
"""

from __future__ import annotations

import json
import os
import stat
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .errors import EXIT_LOCAL_INVALID, EXIT_NO_CREDENTIAL, EXIT_TOKEN_INVALID, DiagError

STORE_DIR = Path.home() / ".yeepay" / "diag"
STORE_PATH = STORE_DIR / "credentials.json"
_MODE = 0o600


def mask(token: str) -> str:
    """token 只以掩码示人：日志与终端都不得出现完整值。"""
    if not token:
        return ""
    return f"{token[:9]}***{token[-4:]}" if len(token) > 16 else "***"


def _entry_key(app_key: str, environment: str) -> str:
    return f"{app_key}@{environment}"


def _check_mode(path: Path) -> None:
    mode = stat.S_IMODE(path.stat().st_mode)
    if mode & 0o077:
        raise DiagError(
            EXIT_NO_CREDENTIAL,
            f"{path} 权限为 {oct(mode)}，过宽；执行 chmod 600 {path} 后重试",
        )


def _load_all() -> dict:
    if not STORE_PATH.exists():
        return {}
    _check_mode(STORE_PATH)
    try:
        return json.loads(STORE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        raise DiagError(EXIT_NO_CREDENTIAL, f"{STORE_PATH} 解析失败，请删除后重新兑换")


def _save_all(data: dict) -> None:
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    os.chmod(STORE_DIR, 0o700)
    fd = os.open(STORE_PATH, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, _MODE)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    os.chmod(STORE_PATH, _MODE)


def save(app_key: str, environment: str, token_data: dict) -> dict:
    """存 token。expiresIn 换算成绝对过期时间，避免时钟漂移时反复重签。"""
    expires_in = int(token_data.get("expiresIn") or 0)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    entry = {
        "appKey": app_key,
        "environment": environment,
        "accessToken": token_data.get("accessToken", ""),
        "tokenType": token_data.get("tokenType", "Bearer"),
        "credentialId": token_data.get("credentialId"),
        "expiresAt": expires_at.isoformat(timespec="seconds"),
    }
    store = _load_all()
    store[_entry_key(app_key, environment)] = entry
    _save_all(store)
    return entry


def _describe(entries: list[dict]) -> str:
    return "、".join(f"{e.get('appKey')}@{e.get('environment')}" for e in entries) or "（无）"


def find(app_key: str | None, environment: str | None) -> dict | None:
    """取本地条目；不带 appKey 时，若只有一条则用它，多条则要求显式指定。"""
    store = _load_all()
    if not store:
        return None
    if app_key and environment:
        entry = store.get(_entry_key(app_key, environment))
        if entry is None:
            # 本地有别的应用的 token 时，别只说「没有 token」——那会让人以为要重新兑换，
            # 而真正的问题是「你要的这个应用没有」。
            others = [e for e in store.values() if e.get("environment") == environment]
            if others:
                raise DiagError(
                    EXIT_NO_CREDENTIAL,
                    f"本地没有 {app_key}@{environment} 的诊断 token；"
                    f"已有的是 {_describe(others)}。不要改用它们——那是别的应用的可见范围。",
                )
        return entry
    candidates = [
        entry
        for entry in store.values()
        if (not app_key or entry.get("appKey") == app_key)
        and (not environment or entry.get("environment") == environment)
    ]
    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        # 退出 2 而不是 10：不缺凭证，缺的是「用哪个」这个决定，且只有用户能做
        raise DiagError(
            EXIT_LOCAL_INVALID,
            f"本地有多个诊断 token（{_describe(candidates)}），"
            "请先与用户确认这次排障属于哪个应用，再用 --app-key / --env 指定",
        )
    return None


def require(app_key: str | None, environment: str | None) -> dict:
    entry = find(app_key, environment)
    if not entry:
        raise DiagError(EXIT_NO_CREDENTIAL, "本地没有诊断 token，请先执行 diag_auth.py 兑换")
    if is_expired(entry):
        raise DiagError(
            EXIT_TOKEN_INVALID,
            f"诊断 token 已于 {entry.get('expiresAt')} 过期，请重新执行 diag_auth.py（不会自动续期）",
        )
    # 用的是谁的凭证必须每次可见：可见范围由它决定，用错应用查出来的是别人的数据。
    # 不打印就只能等结论出来后靠人眼发现，那时错误结论已经说出口了。
    print(
        f"[diag] 使用凭证 {entry.get('appKey')}@{entry.get('environment')} "
        f"{mask(entry.get('accessToken', ''))}",
        file=sys.stderr,
    )
    if not app_key:
        print(
            "[diag] credential_pick=implicit：未指定 --app-key，用的是本地唯一匹配条目。"
            "若本次排障不属于该应用，结论无效，须换凭证并起新会话",
            file=sys.stderr,
        )
    return entry


def is_expired(entry: dict) -> bool:
    raw = entry.get("expiresAt")
    if not raw:
        return False
    try:
        return datetime.fromisoformat(raw) <= datetime.now(timezone.utc)
    except ValueError:
        return False


def remove(app_key: str, environment: str) -> bool:
    store = _load_all()
    removed = store.pop(_entry_key(app_key, environment), None) is not None
    if removed:
        _save_all(store)
    return removed


def list_entries() -> list[dict]:
    return list(_load_all().values())
