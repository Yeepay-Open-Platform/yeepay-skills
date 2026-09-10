# -*- coding: utf-8 -*-
"""脱敏兜底（代码层，第二道）。

提示词层的约束在长对话里会漂移，正则不会——所以这一层是必须的，
不是「以防万一」。规则见 references/排障/diagnostic-protocol.md 第五节。
"""

from __future__ import annotations

import re

MAX_FREE_TEXT = 2000

# 自由文本用全量规则；结构化 slot 值只过密钥类规则。
# 原因：数字类规则对 slot 是必错的——YOP 订单号本身就是 18 位纯数字，
# 会被身份证/卡号规则整条吃掉，把查询条件毁掉。slot 侧的控制手段是
# 白名单 + 逐字段格式校验（slots.py），不是数字正则。
_SECRET_RULES: list[tuple[str, re.Pattern[str]]] = [
    # PEM 私钥/证书整块（含头尾），优先于 base64 长串
    ("pem", re.compile(r"-----BEGIN[^-]{0,64}-----[\s\S]*?-----END[^-]{0,64}-----")),
    ("pem", re.compile(r"-----BEGIN[^-]{0,64}-----")),
    # 疑似 base64 长串（>512 字符）
    ("base64", re.compile(r"[A-Za-z0-9+/=_-]{513,}")),
]

# 数字类规则带内容校验，不只看长度：YOP 订单号常见就是 16~19 位纯数字，
# 只按长度判定会把订单号当卡号吃掉，等于毁掉排障线索。
_ID_DATE = re.compile(r"^\d{6}(\d{4})(\d{2})(\d{2})")


def _luhn_ok(digits: str) -> bool:
    total, alt = 0, False
    for ch in reversed(digits):
        n = ord(ch) - 48
        if alt:
            n *= 2
            if n > 9:
                n -= 9
        total += n
        alt = not alt
    return total % 10 == 0


def _looks_like_card(value: str) -> bool:
    return _luhn_ok(value)


def _looks_like_idcard(value: str) -> bool:
    """中国居民身份证：第 7~14 位是 YYYYMMDD，日期不合法的直接放过。"""
    m = _ID_DATE.match(value)
    if not m:
        return False
    year, month, day = (int(g) for g in m.groups())
    return 1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31


_PII_RULES: list[tuple[str, re.Pattern[str], object]] = [
    ("idcard", re.compile(r"(?<!\d)\d{17}[\dXx](?!\d)"), _looks_like_idcard),
    ("card", re.compile(r"(?<!\d)\d{16,19}(?!\d)"), _looks_like_card),
    ("mobile", re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"), None),
]


def redact_text(text: str, secret_only: bool = False) -> tuple[str, int]:
    """返回 (清洗后文本, 清洗处数)。

    secret_only=True 时只过密钥类规则，用于结构化 slot 值。
    """
    count = 0
    for kind, pattern in _SECRET_RULES:
        text, n = pattern.subn(f"<redacted:{kind}>", text)
        count += n
    if secret_only:
        return text, count

    for kind, pattern, predicate in _PII_RULES:
        def _sub(match, kind=kind, predicate=predicate):
            value = match.group(0)
            if predicate is not None and not predicate(value):
                return value  # 不像该类敏感信息（多为业务单号），放过
            return f"<redacted:{kind}>"

        before = text
        text = pattern.sub(_sub, text)
        if text != before:
            count += sum(1 for _ in re.finditer(rf"<redacted:{kind}>", text))
    return text, count


def count_pii(text: str) -> int:
    """只数个人信息类命中，不含密钥类。

    redact_text 返回的是两类之和，用它判断「有没有个人信息」会把 PEM 块也算进去。
    """
    total = 0
    for _, pattern, predicate in _PII_RULES:
        for match in pattern.finditer(text):
            if predicate is None or predicate(match.group(0)):
                total += 1
    return total


# 附件是绕过前面两道脱敏的通道：文本字段会被清洗，二进制文件不会。
# 所以附件走「拒绝」而不是「清洗」——私钥没有脱敏后还能用的版本。
#
# 但只拒绝**明确的私钥材料**。公钥证书、含密文报文的日志都要放行：商户排查
# 回调解密/验签失败时，要传的恰恰就是这类文件，一律拦掉等于把功能废了。
_PRIVATE_KEY_NAMES = re.compile(
    r"(^|[._-])(id_rsa|id_dsa|id_ecdsa|id_ed25519)($|[._-])"
    r"|\.(pem|key|p12|pfx|jks|keystore)$"
    r"|(^|[/\\])\.env($|\.)"
    r"|credentials\.json$"
    r"|yop_sdk_config.*\.json$",
    re.IGNORECASE,
)
_PUBLIC_CERT_NAMES = re.compile(r"\.(crt|cer|der)$", re.IGNORECASE)
# BEGIN 块里凡不是证书/公钥的，都按私钥对待（PRIVATE KEY、RSA PRIVATE KEY、EC PARAMETERS…）
_PEM_BLOCK = re.compile(r"-----BEGIN ([A-Z0-9 ]{0,64})-----")
_PEM_PUBLIC = re.compile(r"^(CERTIFICATE|PUBLIC KEY|CERTIFICATE REQUEST|X509 CRL)$")
_LONG_BASE64 = re.compile(r"[A-Za-z0-9+/=_-]{513,}")

SCAN_BYTES = 256 * 1024  # 只嗅探文件头部；私钥与配置的特征都在开头


def scan_attachment(path) -> tuple[list[str], list[str]]:
    """附件上传前的本地体检，返回 (拒绝理由, 提醒)。

    拒绝理由非空时**不得上传**——附件一旦进工单系统就不在本机了，
    事后再发现是私钥或 .env 已经晚了。提醒则交给用户判断。
    """
    refuse: list[str] = []
    notes: list[str] = []
    if _PRIVATE_KEY_NAMES.search(path.name):
        refuse.append(f"文件名 {path.name} 像私钥/密钥库/凭证文件")
    if _PUBLIC_CERT_NAMES.search(path.name):
        notes.append(f"{path.name} 像证书文件；公钥证书可传，但请确认不是私钥改的扩展名")

    head = path.open("rb").read(SCAN_BYTES)
    text = head.decode("utf-8", errors="ignore")
    for match in _PEM_BLOCK.finditer(text):
        label = match.group(1).strip()
        if _PEM_PUBLIC.match(label):
            notes.append(f"文件内含 PEM 块（{label}），公开材料可传")
        else:
            refuse.append(f"文件内含 PEM 私钥块（BEGIN {label}）")
            break
    if _LONG_BASE64.search(text):
        # 不拒绝：回调密文报文就长这样，而那正是要给人工看的东西
        notes.append("文件内含超长 Base64 串（可能是密文报文，也可能是密钥），请确认后再传")

    pii_hits = count_pii(text)
    if pii_hits:
        notes.append(f"文件内含 {pii_hits} 处个人信息类特征（卡号/身份证/手机号），须与用户确认后再传")
    return refuse, notes


def redact_value(value):
    """对单个 slot 值脱敏：只过密钥类规则，非字符串原样返回。"""
    if isinstance(value, str):
        return redact_text(value, secret_only=True)
    return value, 0


def redact_payload(payload: dict) -> tuple[dict, int]:
    """对请求体中的自由文本与所有 slot 值脱敏。

    自由文本（initialMessage / message）额外做长度截断。
    """
    total = 0
    out = dict(payload)
    for key in ("initialMessage", "message"):
        if isinstance(out.get(key), str):
            cleaned, n = redact_text(out[key])
            total += n
            if len(cleaned) > MAX_FREE_TEXT:
                cleaned = cleaned[:MAX_FREE_TEXT]
            out[key] = cleaned
    for key, value in list(out.items()):
        if key in ("initialMessage", "message", "slots"):
            continue
        cleaned, n = redact_value(value)
        total += n
        out[key] = cleaned
    if isinstance(out.get("slots"), dict):
        slots = {}
        for key, value in out["slots"].items():
            cleaned, n = redact_value(value)
            total += n
            slots[key] = cleaned
        out["slots"] = slots
    return out, total
