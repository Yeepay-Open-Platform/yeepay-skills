#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""推进排障会话（创建 / 继续 / 查询）。

请求走 --json <file>，不走命令行参数——避免用户原话与槽位进 shell 历史。
CLI 只做传输与校验：把服务端 data 原样打到 stdout，结构异常与被丢弃的字段写 stderr。
是否降级呈现、要不要转人工，由 Skill 按 SKILL.md 纪律决定。

用法：
    python diag/diag_session.py create   --json req.json [--env SANDBOX]
    python diag/diag_session.py continue --session sess_xxx --json req.json
    python diag/diag_session.py get      --session sess_xxx

req.json（create）：
    {"source":"SKILL","initialMessage":"商户反馈支付成功后没有收到回调",
     "merchantNo":"10080792238","startTime":"2026-08-26 00:00:00",
     "endTime":"2026-08-26 23:59:59","slots":{"orderId":"389565332051589553"}}

req.json（continue）：
    {"message":"补充排障信息","slots":{"requestId":"1804d5f4e55b48559abf82153ddae702"}}
"""

import argparse
import json
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from diag._bootstrap import normalize_env, run  # noqa: E402
from diag import credentials, transport  # noqa: E402
from diag.errors import EXIT_LOCAL_INVALID, DiagError  # noqa: E402
from diag.redact import redact_payload  # noqa: E402
from diag.slots import (  # noqa: E402
    filter_slots,
    normalize_environment,
    strip_top_level,
    validate_time_window,
)


def _load_payload(path_arg: str) -> dict:
    path = Path(path_arg).expanduser()
    if not path.is_file():
        raise DiagError(EXIT_LOCAL_INVALID, f"请求文件不存在：{path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DiagError(EXIT_LOCAL_INVALID, f"请求文件不是合法 JSON：{exc}")
    if not isinstance(payload, dict):
        raise DiagError(EXIT_LOCAL_INVALID, "请求文件顶层须为对象")
    return payload


def _prepare(payload: dict, mode: str) -> dict:
    if mode == "create":
        if not payload.get("initialMessage"):
            raise DiagError(EXIT_LOCAL_INVALID, "create 缺少 initialMessage（用户排障问题原文）")
        body = strip_top_level(payload, transport.warn)
        body["source"] = "SKILL"
        body["slots"] = filter_slots(payload.get("slots"), transport.warn)
        validate_time_window(body.get("startTime"), body.get("endTime"))
        slots = body.get("slots") or {}
        if slots.get("startTime") or slots.get("endTime"):
            validate_time_window(slots.get("startTime"), slots.get("endTime"))
    else:
        body = {"message": payload.get("message") or "补充排障信息"}
        # 只在请求里显式给了才传：不传时服务端沿用会话已存环境。若每轮都按 --env
        # 默认值补一个 SANDBOX，上一轮指定的生产会被下一轮悄悄改回沙箱。
        environment = normalize_environment(payload.get("environment"))
        if environment:
            body["environment"] = environment
        slots = filter_slots(payload.get("slots"), transport.warn)
        validate_time_window(slots.get("startTime"), slots.get("endTime"))
        body["slots"] = slots
        if not slots and not payload.get("message"):
            raise DiagError(EXIT_LOCAL_INVALID, "continue 既无 message 也无有效 slots")

    body, redacted = redact_payload(body)
    if not body.get("slots"):
        body.pop("slots", None)
    if redacted:
        transport.warn(f"redactedCount={redacted}：已本地脱敏，须告知用户清洗处数")
    return body


def _warn_env_mismatch(body: dict, entry: dict) -> None:
    """请求里的环境与凭证签发环境不一致时提醒。

    契约允许这么做（同一 appKey 可能沙箱、生产都有），但查的是哪个环境决定了
    「平台侧没有记录」这句话的真假，所以不能悄悄发生。
    """
    requested = body.get("environment") or (body.get("slots") or {}).get("environment")
    bound = entry.get("environment")
    if requested and bound and requested != bound:
        transport.warn(
            f"environment_override={requested}：凭证签发环境是 {bound}，本次按 {requested} 查询。"
            "请向用户确认排查的确实是该环境"
        )
    if not requested:
        transport.warn(
            f"environment=default：请求未指定环境，服务端将按会话已存环境或凭证默认（{bound}）处理"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="推进 yop-agent 排障会话")
    parser.add_argument("action", choices=("create", "continue", "get"))
    parser.add_argument("--json", dest="json_file", help="请求体文件（create / continue 必填）")
    parser.add_argument("--session", help="sessionId（continue / get 必填）")
    parser.add_argument("--submit-path", help="覆盖提交路径，用于遵循 needInfos.submitPath")
    parser.add_argument("--app-key", help="本地有多个 token 时指定")
    parser.add_argument("--env", default="SANDBOX", help="SANDBOX / PRODUCT")
    parser.add_argument("--base-url", help="覆盖 yop-agent 地址")
    args = parser.parse_args()

    environment = normalize_env(args.env)
    base_url = transport.resolve_base_url(environment, args.base_url)
    entry = credentials.require(args.app_key, environment)
    token = entry["accessToken"]

    if args.action == "get":
        if not args.session:
            raise DiagError(EXIT_LOCAL_INVALID, "get 缺少 --session")
        data = transport.request("GET", base_url, f"/v1/diagnosis/sessions/{args.session}",
                                 token=token, session_id=args.session)
    else:
        if not args.json_file:
            raise DiagError(EXIT_LOCAL_INVALID, f"{args.action} 缺少 --json <file>")
        body = _prepare(_load_payload(args.json_file), args.action)
        _warn_env_mismatch(body, entry)
        if args.action == "create":
            path = args.submit_path or "/v1/diagnosis/sessions"
            # 场景识别 + L2 实时查询 + 模型成文，给 90s；且不重试（create 无幂等键）
            timeout, retry = transport.TIMEOUT_CREATE_SESSION, transport.RETRY_CREATE_SESSION
        else:
            if not args.session:
                raise DiagError(EXIT_LOCAL_INVALID, "continue 缺少 --session")
            path = args.submit_path or f"/v1/diagnosis/sessions/{args.session}/messages"
            timeout, retry = None, None
        data = transport.request("POST", base_url, path, token=token, payload=body,
                                 session_id=args.session, timeout=timeout, retry=retry)

    transport.check_session_data(data, expect_session=args.session)
    transport.emit(data)
    return 0


if __name__ == "__main__":
    sys.exit(run(main))
