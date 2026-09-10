# -*- coding: utf-8 -*-
"""退出码与服务端错误码映射。

退出码是 CLI 与 Skill 之间的唯一契约：Skill 只认退出码，不解析文案。
映射依据：references/排障/diagnostic-protocol.md 第七节。
"""

from __future__ import annotations

# 退出码
EXIT_OK = 0
EXIT_LOCAL_INVALID = 2      # 本地参数/输入校验失败（时间窗、缺参等），未发起请求
EXIT_NO_CREDENTIAL = 10     # 本地无 token；AUTH_MISSING
EXIT_KEY_OR_SIGN = 11       # 私钥/证书/密钥类型/签名被拒；AUTH_INVALID
EXIT_TOKEN_INVALID = 12     # 本地 token 过期；AUTH_EXPIRED / AUTH_REVOKED
EXIT_SCOPE_DENIED = 13      # APP_OVERRIDE_DENIED / ENVIRONMENT_OVERRIDE_DENIED / TENANT_MISMATCH
EXIT_RATE_LIMITED = 14      # 限流
EXIT_CREDENTIAL_EXISTS = 15 # CREDENTIAL_EXISTS：别处已有有效 token
EXIT_UNREACHABLE = 20       # 超时 / 5xx / 连不上
EXIT_BAD_RESPONSE = 21      # 响应结构非法 / code 未知

SUCCESS_CODE = "00000"

# 服务端 code → 退出码。
#
# 契约（2026-08-27 更新）：`YOP-AGT` + 级别（A=调用方错误 / B=本系统错误）+ 4 位业务码。
# 注意：CREDENTIAL_EXISTS / CREDENTIAL_NOT_FOUND / ENVIRONMENT_OVERRIDE_DENIED 三个 key
# 尚未注册到枚举，实际兜底为 YOP-AGTB0500——所以 B0500 必须再按 message 细分，
# 否则「已有有效 token」会被当成「远端不可用」，用户就永远不知道该去吊销。
CODE_TO_EXIT: dict[str, int] = {
    "YOP-AGTA0400": EXIT_LOCAL_INVALID,      # PARAM_INVALID
    "YOP-AGTA0404": EXIT_LOCAL_INVALID,      # NOT_FOUND：session 不存在
    "YOP-AGTA0413": EXIT_LOCAL_INVALID,      # ATTACHMENT_TOO_LARGE：单文件 10MB / 单请求 12MB
    "YOP-AGTA0429": EXIT_RATE_LIMITED,       # 提单频率超限：3/分钟、20/天（顶层 code）
    "YOP-AGTA1401": EXIT_NO_CREDENTIAL,      # AUTH_MISSING
    "YOP-AGTA1402": EXIT_KEY_OR_SIGN,        # AUTH_INVALID（再按 message 细分）
    "YOP-AGTA1403": EXIT_TOKEN_INVALID,      # AUTH_REVOKED
    "YOP-AGTA1404": EXIT_TOKEN_INVALID,      # AUTH_EXPIRED
    "YOP-AGTA1405": EXIT_SCOPE_DENIED,       # SCOPE_DENIED
    "YOP-AGTA1406": EXIT_SCOPE_DENIED,       # TENANT_MISMATCH
    "YOP-AGTA1407": EXIT_SCOPE_DENIED,       # APP_OVERRIDE_DENIED
    "YOP-AGTB0500": EXIT_UNREACHABLE,        # INNER_ERROR（再按 message 细分）
    "WEBB0500": EXIT_UNREACHABLE,            # 框架级兜底（如路径不存在）
    # 文档曾承诺、当前未注册的裸 key：服务端若补注册，客户端不需要改
    "AUTH_MISSING": EXIT_NO_CREDENTIAL,
    "AUTH_INVALID": EXIT_KEY_OR_SIGN,
    "AUTH_EXPIRED": EXIT_TOKEN_INVALID,
    "AUTH_REVOKED": EXIT_TOKEN_INVALID,
    "SCOPE_DENIED": EXIT_SCOPE_DENIED,
    "TENANT_MISMATCH": EXIT_SCOPE_DENIED,
    "APP_OVERRIDE_DENIED": EXIT_SCOPE_DENIED,
    "ENVIRONMENT_OVERRIDE_DENIED": EXIT_SCOPE_DENIED,
    "CREDENTIAL_EXISTS": EXIT_CREDENTIAL_EXISTS,
    "CREDENTIAL_NOT_FOUND": EXIT_TOKEN_INVALID,
    # 兼容旧码：曾出现在 data.errorCode（顶层仍 00000）。现已上提到顶层 YOP-AGTA0429，
    # 仍收下以免旧环境把「超限没建成」报成「已建单」。
    "YOP-AGT10429": EXIT_RATE_LIMITED,
    # 其余限流候选：客户端都收下
    "RATE_LIMITED": EXIT_RATE_LIMITED,
    "LIMIT_EXCEEDED": EXIT_RATE_LIMITED,
    "TOO_MANY_REQUESTS": EXIT_RATE_LIMITED,
}

# 按 message 关键词细分的 code，及其规则（命中顺序即优先级）。
# 未命中时回落到 CODE_TO_EXIT 里该 code 的默认值。
MESSAGE_RULES: dict[str, tuple[tuple[str, int], ...]] = {
    "YOP-AGTA1402": (
        ("token 不存在", EXIT_TOKEN_INVALID),
        ("token 前缀", EXIT_TOKEN_INVALID),
        ("已过期", EXIT_TOKEN_INVALID),
        ("已吊销", EXIT_TOKEN_INVALID),
        ("为空", EXIT_LOCAL_INVALID),
        ("仅支持", EXIT_LOCAL_INVALID),
        ("签名校验失败", EXIT_KEY_OR_SIGN),
    ),
    "YOP-AGTB0500": (
        ("CREDENTIAL_EXISTS", EXIT_CREDENTIAL_EXISTS),
        ("已有有效", EXIT_CREDENTIAL_EXISTS),
        ("已存在", EXIT_CREDENTIAL_EXISTS),
        ("CREDENTIAL_NOT_FOUND", EXIT_TOKEN_INVALID),
        ("未找到", EXIT_TOKEN_INVALID),
        ("ENVIRONMENT_OVERRIDE_DENIED", EXIT_SCOPE_DENIED),
        ("环境", EXIT_SCOPE_DENIED),
    ),
}

# Skill 侧行为提示，随 stderr 一起给出，便于 Skill 按纪律处理
EXIT_HINT: dict[int, str] = {
    EXIT_LOCAL_INVALID: "参数问题（本地校验未过 / 服务端判定参数无效或 session 不存在）：修正后重试，必要时起新会话",
    EXIT_NO_CREDENTIAL: "无可用诊断 token：走离线 L1，并一次性告知可用 appKey + 私钥兑换",
    EXIT_KEY_OR_SIGN: "密钥或签名问题：停止，核对私钥路径与密钥类型，不重试、不改用其他密钥",
    EXIT_TOKEN_INVALID: "token 无效/过期/已吊销：走离线 L1，提示重新执行 diag_auth.py",
    EXIT_SCOPE_DENIED: "范围或环境校验失败：停止，不重试、不换参数再试",
    EXIT_RATE_LIMITED: "已限流（提单 3/分钟·20/天，附件 10/分钟·100/天）：如实告知配额，稍后再试，不反复重试",
    EXIT_CREDENTIAL_EXISTS: "别处已有有效 token：复用本地条目，或由用户确认后先 --revoke，不自动吊销",
    EXIT_UNREACHABLE: "远端不可用：走离线 L1 并预览工单内容，不得用本地推测冒充平台事实",
    EXIT_BAD_RESPONSE: "响应结构非法：丢弃响应，不呈现任何结论，转工单",
}


class DiagError(Exception):
    """带退出码的 CLI 错误。"""

    def __init__(self, exit_code: int, message: str):
        super().__init__(message)
        self.exit_code = exit_code
        self.message = message


def exit_for_code(code: str | None, message: str = "") -> int:
    """先按 code 映射；对会兜底聚合的 code 再按 message 关键词细分。"""
    if not code:
        return EXIT_BAD_RESPONSE
    for keyword, exit_code in MESSAGE_RULES.get(code, ()):
        if keyword in (message or ""):
            return exit_code
    return CODE_TO_EXIT.get(code, EXIT_BAD_RESPONSE)
