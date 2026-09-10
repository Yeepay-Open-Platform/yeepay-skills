# -*- coding: utf-8 -*-
"""与 yop-agent 通信的传输层与安全层。

职责边界：**只传输与校验，不做决策**——不解释响应、不归纳结论、不替 Skill
判断该不该升级或转人工，只把服务端 data 原样打到 stdout，把结构异常与
被丢弃的字段写到 stderr。

契约：HTTP 状态恒 200，业务成败看 code（成功 00000）；所有端点挂在 /yop-agent 下。
"""

from __future__ import annotations

import json
import os
import sys
import time

from .errors import (
    EXIT_BAD_RESPONSE,
    EXIT_LOCAL_INVALID,
    EXIT_RATE_LIMITED,
    EXIT_UNREACHABLE,
    SUCCESS_CODE,
    DiagError,
    exit_for_code,
)

# yop-agent 对外入口固定；查沙箱还是生产由请求里的 environment 决定，不换主机。
# --base-url / YOP_AGENT_BASE_URL 可覆盖默认入口。
DEFAULT_BASE_URL = "https://sandbox.yeepay.com"
ENV_VAR = "YOP_AGENT_BASE_URL"

# 服务端 2026-08-31 起统一挂在 /yop-agent 下（不带前缀的老路径直接 404）。
# 前缀只在这一处拼：路径字面量仍写 /v1/...，需要时可用 YOP_AGENT_CONTEXT_PATH 覆盖。
CONTEXT_PATH = os.environ.get("YOP_AGENT_CONTEXT_PATH", "/yop-agent").rstrip("/")

# 单个附件上限，与服务端一致；本地先拦一道，别把 10MB 传上去再被拒。
MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024

# (connect, read)。create 会话要跑场景识别 + L2 实时查询 + 模型成文，读超时放宽到 90s。
TIMEOUT = (5, 30)
TIMEOUT_CREATE_SESSION = (5, 90)
TIMEOUT_UPLOAD = (5, 60)

# 只对连不上/5xx 重试，不对业务失败重试。
RETRY_ON_UNREACHABLE = 1
# 创建会话**不重试**：它没有幂等键，超时重发可能让服务端建出第二个会话，
# 后续补槽会打到错误的 sessionId 上。宁可返回 20 让用户重来。
RETRY_CREATE_SESSION = 0

# 服务端返回展示值，不再返回 NEED_INFO / L1 等内部码。英文内部码视为未知 status，拒收。
STATUS_NEED_INFO = "待补充信息"
STATUS_KNOWLEDGE = "知识建议"
STATUS_DIAGNOSING = "诊断中"
STATUS_LOCATED = "已定位"
STATUS_UNRESOLVED = "暂未定位"
STATUS_HANDOFF = "转人工"
STATUS_CLOSED = "已关闭"

SESSION_STATUSES = (
    STATUS_NEED_INFO,
    STATUS_KNOWLEDGE,
    STATUS_DIAGNOSING,
    STATUS_LOCATED,
    STATUS_UNRESOLVED,
    STATUS_HANDOFF,
    STATUS_CLOSED,
)

LAYER_NONE = "未进入排障"
LAYER_L1 = "L1 知识建议"
LAYER_L2 = "L2 实时证据排障"


def warn(message: str) -> None:
    print(f"[diag] {message}", file=sys.stderr)


def resolve_base_url(environment: str, override: str | None = None) -> str:
    """解析 yop-agent 基址。environment 只用于凭证与请求体，不再选主机。"""
    base = override or os.environ.get(ENV_VAR) or DEFAULT_BASE_URL
    if not base:
        raise DiagError(
            EXIT_LOCAL_INVALID,
            f"yop-agent 地址未配置：用 --base-url 指定或设置 {ENV_VAR}",
        )
    return base.rstrip("/")


def build_url(base_url: str, path: str) -> str:
    """拼完整 URL，并保证 context-path 只出现一次。

    服务端 needInfos.submitPath 返回的是**带前缀**的完整路径，而代码里的字面量
    不带——两者都要能用，所以在这里判重，而不是让调用方各记各的。
    """
    base = base_url.rstrip("/")
    if not path.startswith("/"):
        path = "/" + path
    if CONTEXT_PATH and not base.endswith(CONTEXT_PATH) and not path.startswith(CONTEXT_PATH + "/"):
        path = CONTEXT_PATH + path
    return f"{base}{path}"


def log_session(session_id: str | None, phase: str = "") -> None:
    """会话标识随每次交互打印，便于与 yop-agent 日志（sessionId=...）联查。"""
    if session_id:
        suffix = f" {phase}" if phase else ""
        print(f"[diag] sessionId={session_id}{suffix}", file=sys.stderr)


def request(method: str, base_url: str, path: str, *, token: str | None = None,
            payload: dict | None = None, session_id: str | None = None,
            timeout: tuple[int, int] | None = None, retry: int | None = None) -> dict:
    """发请求并解包 {code, message, data}；失败一律抛 DiagError。

    timeout / retry 由调用方按动作指定——CLI 知道自己在调哪个接口，
    比在传输层按路径猜更直白。
    """
    import requests

    timeout = timeout or TIMEOUT
    retry = RETRY_ON_UNREACHABLE if retry is None else retry
    log_session(session_id, "→ 请求")
    url = build_url(base_url, path)
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    last_error = ""
    for attempt in range(retry + 1):
        try:
            resp = requests.request(
                method, url, headers=headers,
                data=json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None,
                timeout=timeout,
            )
        except requests.RequestException as exc:
            last_error = f"请求失败：{type(exc).__name__}（读超时 {timeout[1]}s）"
            if attempt < retry:
                time.sleep(1)
                continue
            raise DiagError(EXIT_UNREACHABLE, last_error)

        if resp.status_code >= 500:
            last_error = f"服务端 {resp.status_code}"
            if attempt < retry:
                time.sleep(1)
                continue
            raise DiagError(EXIT_UNREACHABLE, last_error)
        return unwrap(resp, session_id)

    raise DiagError(EXIT_UNREACHABLE, last_error or "请求失败")


def unwrap(resp, session_id: str | None = None):
    """解包 {code, message, data}：HTTP 恒 200，业务成败只看 code。

    唯一例外是附件上传的限流，它走 HTTP 429 而不是 200——不单独认它就会被当成
    「响应结构非法」转工单，而正确处置是告知配额、稍后再试。
    """
    if resp.status_code == 429:
        raise DiagError(EXIT_RATE_LIMITED, "附件上传频率超限（10/分钟、100/天），请稍后再试")
    if resp.status_code != 200:
        raise DiagError(EXIT_BAD_RESPONSE, f"非预期 HTTP 状态 {resp.status_code}")
    try:
        body = resp.json()
    except ValueError:
        raise DiagError(EXIT_BAD_RESPONSE, "响应不是合法 JSON")
    if not isinstance(body, dict) or "code" not in body:
        raise DiagError(EXIT_BAD_RESPONSE, "响应缺少 code 字段")

    code = body.get("code")
    if code != SUCCESS_CODE:
        message = body.get("message") or ""
        log_session(session_id, "← 失败")
        raise DiagError(exit_for_code(code, message), f"服务端返回 {code}：{message}")

    data = body.get("data")
    if data is None:
        raise DiagError(EXIT_BAD_RESPONSE, "响应 code 成功但 data 为空")
    if isinstance(data, dict):
        log_session(data.get("sessionId"), "← 响应")
    return data


def upload(base_url: str, path: str, *, token: str, fields: dict, file_path,
           session_id: str | None = None):
    """multipart 上传（工单附件）。

    **不重试**：附件上传没有幂等键，重发可能在工单上挂出两份同样的附件。
    """
    import requests

    log_session(session_id, "→ 上传附件")
    url = build_url(base_url, path)
    headers = {"Authorization": f"Bearer {token}"}
    with open(file_path, "rb") as handle:
        try:
            resp = requests.post(
                url, headers=headers, data=fields,
                files={"file": (file_path.name, handle, "application/octet-stream")},
                timeout=TIMEOUT_UPLOAD,
            )
        except requests.RequestException as exc:
            raise DiagError(EXIT_UNREACHABLE, f"附件上传失败：{type(exc).__name__}")
    if resp.status_code >= 500:
        raise DiagError(EXIT_UNREACHABLE, f"服务端 {resp.status_code}")
    return unwrap(resp, session_id)


# status 与 layer 的自洽期望：查过实时数据的状态必须落在 L2，纯知识建议必须落在 L1。
_EXPECTED_LAYER = {
    STATUS_KNOWLEDGE: LAYER_L1,
    STATUS_LOCATED: LAYER_L2,
    STATUS_UNRESOLVED: LAYER_L2,
}
# 到了这些状态就该有话可说；没有 conclusion 等于没有可呈现的结论。
# 诊断中 / 已关闭 / 待补充信息 / 转人工 不强制 conclusion。
_CONCLUSION_EXPECTED = (STATUS_KNOWLEDGE, STATUS_LOCATED, STATUS_UNRESOLVED)


def check_session_data(data, expect_session: str | None = None) -> None:
    """结构校验：只把异常写 stderr，降级呈现由 Skill 按纪律执行（CLI 不做决策）。

    唯二硬失败（退出 21，不呈现任何结论）是「没法用」和「不是我的会话」：
    status 缺失或不认识，以及 sessionId 与请求的不一致。其余一律 warn，
    让 Skill 按 SKILL.md 纪律降级呈现。
    """
    if not isinstance(data, dict):
        raise DiagError(EXIT_BAD_RESPONSE, "会话响应 data 不是对象")
    status = data.get("status")
    if not status:
        raise DiagError(EXIT_BAD_RESPONSE, "会话响应缺少 status")
    if status not in SESSION_STATUSES:
        raise DiagError(EXIT_BAD_RESPONSE, f"未知 status：{status}")

    # 串会话是安全问题不是呈现问题：拿到的可能是别人的结论与证据，直接拒收。
    returned = data.get("sessionId")
    if expect_session and returned and returned != expect_session:
        raise DiagError(
            EXIT_BAD_RESPONSE,
            f"响应 sessionId={returned} 与请求的 {expect_session} 不一致，拒绝呈现",
        )
    if not returned:
        warn("client_check=missing_session_id：响应无 sessionId，后续补槽无处可发，须重新创建会话")

    layer = data.get("layer")
    expected_layer = _EXPECTED_LAYER.get(status)
    if layer and expected_layer and layer != expected_layer:
        warn(
            f"client_check=layer_status_mismatch：status={status} 但 layer={layer}"
            f"（期望 {expected_layer}），按较弱的一方呈现"
        )

    if status in _CONCLUSION_EXPECTED and not (data.get("conclusion") or "").strip():
        warn(f"client_check=empty_conclusion：status={status} 但 conclusion 为空，不要自行补写结论")

    confidence = data.get("confidence")
    if confidence is not None and (
        isinstance(confidence, bool)
        or not isinstance(confidence, (int, float))
        or not 0 <= confidence <= 1
    ):
        warn(f"client_check=bad_confidence：confidence={confidence!r} 不是 0~1 数值，不要呈现置信度")

    for key in ("evidence", "needInfos", "excludedItems", "unknownItems", "relatedDocs"):
        value = data.get(key)
        if value is not None and not isinstance(value, list):
            warn(f"client_check=bad_{key}_type：{key} 不是数组，按缺失处理")

    evidence = data.get("evidence") if isinstance(data.get("evidence"), list) else []
    if status == STATUS_LOCATED and not evidence:
        warn("client_check=located_without_evidence：已定位但无证据，须按暂未定位呈现，不得给生产根因")
    if status == STATUS_KNOWLEDGE and evidence:
        warn("client_check=knowledge_with_evidence：知识建议层出现证据，视为异常，按本地 L1 呈现并提示用户反馈")
    need_infos = data.get("needInfos") if isinstance(data.get("needInfos"), list) else []
    if status == STATUS_NEED_INFO and not need_infos:
        warn("client_check=need_info_without_needinfos：待补充信息但无 needInfos，不要自行猜要问什么")
    if status == STATUS_DIAGNOSING:
        warn("client_check=status_diagnosing：诊断尚未完成，立即 get 轮询，不要向用户补槽或提单")
    if status == STATUS_CLOSED:
        warn("client_check=status_closed：会话已结束，禁止 continue；不要自动建单（已关闭 ≠ 转人工）")
    # 服务端有时把要问的信息只放在 nextQuestion 文本里、needInfos 留空。
    # 若不提示，Skill 按「只问 needInfos」的纪律会什么都不问，链路直接卡死。
    if not need_infos and data.get("nextQuestion"):
        warn(
            "client_check=needinfos_empty_with_question：needInfos 为空但 nextQuestion 有内容，"
            "可按该文本追问，并向用户标明这是文本解析、非结构化补槽"
        )


def emit(data) -> None:
    """服务端 data 原样出 stdout。"""
    print(json.dumps(data, ensure_ascii=False, indent=2))
