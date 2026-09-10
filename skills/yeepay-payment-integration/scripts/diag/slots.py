# -*- coding: utf-8 -*-
"""槽位闭集白名单与本地预校验。

白名单是双向的：对上限制 Skill 只能问这些字段，对下丢弃请求里的未知 key。
必须是白名单而不是黑名单——黑名单永远列不全，而模型在长对话里会很自然地
把刚读过的代码片段塞进请求。

字段定义见 references/排障/diagnostic-protocol.md 第四节。
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta

from .errors import EXIT_LOCAL_INVALID, DiagError

# 服务端接受的槽位（闭集）
SLOT_WHITELIST = (
    "merchantNo",
    "startTime",
    "endTime",
    "requestId",
    "orderId",
    "notifyOrderId",
    # 服务端文档把 notificationId 列为 notifyOrderId 的同义槽位，两个都收
    "notificationId",
    "errorCode",
    "subErrorCode",
    "apiUri",
    # 契约标为「兼容旧字段，不推荐新接入使用」，但部分剧本会
    # 主动索要它。留在白名单里，仅当服务端点名索要时填；优先仍用 startTime/endTime。
    "time_range",
    # 2026-08-31 契约变更：environment 从「禁止字段」改为合法槽位。同一 appKey 可能
    # 同时存在于沙箱与生产，会话环境按「请求 > 会话已存 > token 默认」取。顶层优先，
    # slots.environment 为兼容写法。
    "environment",
)

# 绝不允许出现在请求体里的字段：appKey —— 生产禁止覆盖（APP_OVERRIDE_DENIED）。
# environment 已于 2026-08-31 移出本表（见 SLOT_WHITELIST 注释）。
FORBIDDEN_KEYS = ("appKey",)

# 创建会话时允许出现在顶层的字段
TOP_LEVEL_ALLOWED = ("source", "initialMessage", "merchantNo", "startTime", "endTime",
                     "requestId", "environment", "slots")

ENV_ALIASES = {
    "SANDBOX": "SANDBOX", "QA": "SANDBOX", "TEST": "SANDBOX",
    "PRODUCT": "PRODUCT", "PROD": "PRODUCT", "PRODUCTION": "PRODUCT",
}


def normalize_environment(value):
    """归一化请求体里的 environment，非法值本地拦下。

    服务端对认不出的值会回落到默认环境——那意味着用户以为在查生产、实际查的是
    沙箱，然后拿到「平台侧没有记录」。这种假阴性会被当成事实说出去，所以宁可报错。
    """
    if value is None or value == "":
        return None
    normalized = ENV_ALIASES.get(str(value).strip().upper())
    if not normalized:
        raise DiagError(
            EXIT_LOCAL_INVALID,
            f"environment 取值非法：{value}；只接受 SANDBOX/QA/TEST 或 PRODUCT/PROD/PRODUCTION",
        )
    return normalized

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_SPAN = timedelta(days=1)

_PATTERNS = {
    "merchantNo": re.compile(r"^[A-Za-z0-9_-]{1,32}$"),
    "requestId": re.compile(r"^[A-Za-z0-9-]{8,64}$"),
    "orderId": re.compile(r"^[A-Za-z0-9_-]{1,64}$"),
    "notifyOrderId": re.compile(r"^[A-Za-z0-9_-]{1,64}$"),
    "notificationId": re.compile(r"^[A-Za-z0-9_-]{1,64}$"),
    "errorCode": re.compile(r"^[A-Za-z0-9._-]{1,32}$"),
    "subErrorCode": re.compile(r"^[A-Za-z0-9._-]{1,32}$"),
    "apiUri": re.compile(r"^/[A-Za-z0-9/._-]{1,128}$"),
    "time_range": re.compile(r"^[0-9 :\-~,]{1,64}$"),
}


def filter_slots(raw: dict | None, warn) -> dict:
    """丢弃白名单外的 key、剔除禁止字段、逐字段格式校验。

    warn(msg) 用于向 stderr 汇报被丢弃的字段（可见比静默更重要）。
    """
    if not raw:
        return {}
    out: dict = {}
    for key, value in raw.items():
        if key in FORBIDDEN_KEYS:
            warn(f"已剔除禁止字段 slots.{key}（可见范围由服务端按 token 判定，不接受客户端覆盖）")
            continue
        if key not in SLOT_WHITELIST:
            warn(f"已丢弃白名单外字段 slots.{key}")
            continue
        if value is None or value == "":
            continue
        if key == "environment":
            out[key] = normalize_environment(value)
            continue
        text = value if isinstance(value, str) else str(value)
        pattern = _PATTERNS.get(key)
        if pattern and not pattern.match(text):
            warn(f"已丢弃格式不合法的 slots.{key}")
            continue
        out[key] = text
    return out


def validate_time_window(start: str | None, end: str | None) -> None:
    """校验时间格式、先后顺序与跨度。

    服务端在非法时会静默回落到当天 00:00:00~23:59:59——那会让用户以为查的是
    自己给的时间段，所以这里提前拦下并让用户确认，而不是放过去。
    """
    if not start and not end:
        return
    if bool(start) != bool(end):
        raise DiagError(EXIT_LOCAL_INVALID, "startTime 与 endTime 必须同时提供")
    try:
        start_dt = datetime.strptime(start, TIME_FORMAT)
        end_dt = datetime.strptime(end, TIME_FORMAT)
    except ValueError:
        raise DiagError(EXIT_LOCAL_INVALID, "时间格式须为 yyyy-MM-dd HH:mm:ss（如 2026-08-26 00:00:00）")
    if end_dt < start_dt:
        raise DiagError(EXIT_LOCAL_INVALID, "endTime 早于 startTime")
    if end_dt - start_dt > MAX_SPAN:
        raise DiagError(
            EXIT_LOCAL_INVALID,
            "时间跨度超过 1 天：服务端会回落到当天 00:00:00~23:59:59，请缩小到 1 天内并与用户确认",
        )


def strip_top_level(payload: dict, warn) -> dict:
    """创建会话请求体：剔除禁止字段与顶层未知字段。"""
    out = {}
    for key, value in payload.items():
        if key in FORBIDDEN_KEYS:
            warn(f"已剔除禁止字段 {key}（可见范围由服务端按 token 判定）")
            continue
        if key not in TOP_LEVEL_ALLOWED:
            warn(f"已丢弃白名单外字段 {key}")
            continue
        if value is None or value == "":
            continue
        out[key] = normalize_environment(value) if key == "environment" else value
    return out
