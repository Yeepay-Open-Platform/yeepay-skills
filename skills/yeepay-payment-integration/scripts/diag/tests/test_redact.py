#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag 自测：脱敏、槽位白名单、错误码映射、响应结构自洽校验、URL 前缀、附件体检。

发版守门（validate_docs.py）会调用本脚本。断言失败即退出码 1。
用法：python diag/tests/test_redact.py
"""

import os
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from diag.errors import (  # noqa: E402
    EXIT_BAD_RESPONSE,
    EXIT_CREDENTIAL_EXISTS,
    EXIT_KEY_OR_SIGN,
    EXIT_LOCAL_INVALID,
    EXIT_NO_CREDENTIAL,
    EXIT_RATE_LIMITED,
    EXIT_SCOPE_DENIED,
    EXIT_TOKEN_INVALID,
    EXIT_UNREACHABLE,
    exit_for_code,
)
from diag.redact import redact_payload, redact_text, scan_attachment  # noqa: E402
from diag.slots import DiagError, filter_slots, validate_time_window  # noqa: E402
from diag import transport  # noqa: E402

FAILED: list[str] = []


def check(label: str, actual, expected) -> None:
    if actual != expected:
        FAILED.append(f"{label}: 期望 {expected!r}，实际 {actual!r}")


def test_secrets_are_redacted() -> None:
    text, count = redact_text("私钥 -----BEGIN PRIVATE KEY-----abc-----END PRIVATE KEY----- 结束")
    check("PEM 被脱敏", "<redacted:pem>" in text, True)
    check("PEM 计数", count, 1)
    check("手机被脱敏", redact_text("联系 13800138000")[0], "联系 <redacted:mobile>")
    check("Luhn 合法卡号被脱敏", redact_text("卡 4111111111111111")[0], "卡 <redacted:card>")
    check("身份证被脱敏", redact_text("证件 11010119900307123X")[0], "证件 <redacted:idcard>")
    long_b64 = "A" * 600
    check("超长 base64 被脱敏", "<redacted:base64>" in redact_text(long_b64)[0], True)


def test_business_ids_survive() -> None:
    """数字类规则必须带内容校验：订单号是排障线索，误脱敏等于毁掉查询条件。"""
    check("18 位订单号保留", redact_text("订单 389565332051589553")[0], "订单 389565332051589553")
    check("Luhn 非法的 16 位业务号保留", redact_text("单号 6222021234567890")[0], "单号 6222021234567890")
    check(
        "requestId 保留",
        redact_text("requestId 1804d5f4e55b48559abf82153ddae702")[0],
        "requestId 1804d5f4e55b48559abf82153ddae702",
    )


def test_slot_values_only_filter_secrets() -> None:
    body, count = redact_payload({"slots": {"orderId": "389565332051589553"}})
    check("slot 中的订单号保留", body["slots"]["orderId"], "389565332051589553")
    check("slot 无脱敏计数", count, 0)
    body, count = redact_payload({"slots": {"orderId": "-----BEGIN PRIVATE KEY-----x-----END PRIVATE KEY-----"}})
    check("slot 中的 PEM 仍被拦", body["slots"]["orderId"], "<redacted:pem>")
    check("slot PEM 计数", count, 1)


def test_free_text_truncated() -> None:
    body, _ = redact_payload({"initialMessage": "字" * 3000})
    check("自由文本截断到 2000", len(body["initialMessage"]), 2000)


def test_slot_whitelist() -> None:
    dropped: list[str] = []
    out = filter_slots(
        {
            "merchantNo": "10080792238",
            "appKey": "app_x",
            "environment": "PRODUCT",
            "stackTrace": "...",
            "errorCode": "非法!",
            "orderId": "389565332051589553",
        },
        dropped.append,
    )
    # environment 自 2026-08-31 起是合法槽位（会话级，决定查沙箱还是生产），会被归一化保留
    check("白名单结果", out, {"merchantNo": "10080792238", "environment": "PRODUCT",
                              "orderId": "389565332051589553"})
    check("被丢弃项数", len(dropped), 3)


def test_environment_field() -> None:
    """查错环境不会报错，只会拿到一句「平台侧没有记录」——所以非法值要本地拦下。"""
    from diag.slots import normalize_environment

    for raw, want in (("qa", "SANDBOX"), ("PROD", "PRODUCT"), ("Production", "PRODUCT")):
        check(f"归一化 {raw}", normalize_environment(raw), want)
    check("空值不传", normalize_environment(None), None)
    try:
        normalize_environment("生产")
        check("非法环境须报错", "未抛错", "应抛 DiagError")
    except DiagError as exc:
        check("非法环境退出码", exc.exit_code, 2)

    # 继续会话不带 environment 时不得自动补：补了会把上一轮指定的生产改回沙箱
    from diag.diag_session import _prepare

    check("continue 不注入环境", "environment" in _prepare({"message": "补充",
          "slots": {"merchantNo": "100"}}, "continue"), False)
    check("continue 显式传则透传",
          _prepare({"message": "补充", "environment": "prod"}, "continue").get("environment"),
          "PRODUCT")
    created = _prepare({"initialMessage": "回调没收到", "environment": "PRODUCT"}, "create")
    check("create 显式传则透传", created.get("environment"), "PRODUCT")
    check("create 强制 source=SKILL", created.get("source"), "SKILL")
    override = _prepare({"initialMessage": "回调没收到", "source": "CONSOLE",
                         "environment": "SANDBOX"}, "create")
    check("create 覆盖调用方 source", override.get("source"), "SKILL")


def test_ticket_inline_error() -> None:
    """旧口径：提单限流藏在 data.errorCode。新口径顶层 YOP-AGTA0429 由 unwrap 处理。"""
    from diag.diag_ticket import _check_ticket_result
    from diag.errors import EXIT_RATE_LIMITED

    try:
        _check_ticket_result({"created": False, "errorCode": "YOP-AGT10429",
                              "message": "提单频率超限"})
        check("限流须抛错", "未抛错", "应抛 DiagError")
    except DiagError as exc:
        check("限流退出码", exc.exit_code, EXIT_RATE_LIMITED)
    _check_ticket_result({"created": True, "ticketNo": "TK-1"})  # 正常不抛


def test_time_window() -> None:
    validate_time_window("2026-08-26 00:00:00", "2026-08-26 23:59:59")
    for start, end, why in [
        ("2026-08-20 00:00:00", "2026-08-26 00:00:00", "跨度超 1 天"),
        ("2026-08-26 10:00:00", "2026-08-26 09:00:00", "结束早于开始"),
        ("bad", "bad", "格式非法"),
        ("2026-08-26 00:00:00", None, "只给一端"),
    ]:
        try:
            validate_time_window(start, end)
            FAILED.append(f"时间校验未拦下：{why}")
        except DiagError:
            pass

    from diag.diag_session import _prepare
    try:
        _prepare({
            "initialMessage": "回调没收到",
            "slots": {"startTime": "2026-08-20 00:00:00", "endTime": "2026-08-26 00:00:00"},
        }, "create")
        FAILED.append("create slots 时间跨度超 1 天未拦下")
    except DiagError as exc:
        check("create slots 超窗退出码", exc.exit_code, 2)


def test_real_code_mapping() -> None:
    """契约错误码与兼容兜底。"""
    check("A0400 参数无效", exit_for_code("YOP-AGTA0400", "参数校验失败"), EXIT_LOCAL_INVALID)
    check("A0404 session 不存在", exit_for_code("YOP-AGTA0404", "session not found"), EXIT_LOCAL_INVALID)
    check("A0413 附件过大", exit_for_code("YOP-AGTA0413", "附件大小超过限制"), EXIT_LOCAL_INVALID)
    check("A0429 提单限流", exit_for_code("YOP-AGTA0429", "提单频率超限，限制为 3/分钟、20/天"), EXIT_RATE_LIMITED)
    check("AGT10429 旧限流码", exit_for_code("YOP-AGT10429", "提单频率超限"), EXIT_RATE_LIMITED)
    check("A1401 缺 Bearer", exit_for_code("YOP-AGTA1401", "缺少 Authorization Bearer"), EXIT_NO_CREDENTIAL)
    check("A1402 签名失败", exit_for_code("YOP-AGTA1402", "应用签名校验失败"), EXIT_KEY_OR_SIGN)
    check("A1402 token 不存在", exit_for_code("YOP-AGTA1402", "token 不存在"), EXIT_TOKEN_INVALID)
    check("A1402 参数为空", exit_for_code("YOP-AGTA1402", "appKey、environment 或 signature 为空"), EXIT_LOCAL_INVALID)
    check("A1402 env 非法", exit_for_code("YOP-AGTA1402", "environment 仅支持 SANDBOX/PRODUCT"), EXIT_LOCAL_INVALID)
    check("A1403 已吊销", exit_for_code("YOP-AGTA1403", "token 已吊销"), EXIT_TOKEN_INVALID)
    check("A1404 已过期", exit_for_code("YOP-AGTA1404", "token 已过期"), EXIT_TOKEN_INVALID)
    check("A1405 scope 不足", exit_for_code("YOP-AGTA1405", "scope 不足"), EXIT_SCOPE_DENIED)
    check("A1406 租户不符", exit_for_code("YOP-AGTA1406", "租户不一致"), EXIT_SCOPE_DENIED)
    check("A1407 覆盖 appKey", exit_for_code("YOP-AGTA1407", "试图覆盖 appKey"), EXIT_SCOPE_DENIED)
    # 三个未注册的 key 会兜底成 B0500，必须按 message 救回来
    check("B0500 + 重复签发", exit_for_code("YOP-AGTB0500", "CREDENTIAL_EXISTS"), EXIT_CREDENTIAL_EXISTS)
    check("B0500 + 环境覆盖", exit_for_code("YOP-AGTB0500", "ENVIRONMENT_OVERRIDE_DENIED"), EXIT_SCOPE_DENIED)
    check("B0500 其他内部错误", exit_for_code("YOP-AGTB0500", "系统内部错误"), EXIT_UNREACHABLE)
    check("WEBB0500 归 20", exit_for_code("WEBB0500", "internal-server-error(NT)"), EXIT_UNREACHABLE)


def test_code_mapping() -> None:
    check("AUTH_EXPIRED", exit_for_code("AUTH_EXPIRED"), EXIT_TOKEN_INVALID)
    check("TENANT_MISMATCH", exit_for_code("TENANT_MISMATCH"), EXIT_SCOPE_DENIED)
    check("CREDENTIAL_EXISTS", exit_for_code("CREDENTIAL_EXISTS"), EXIT_CREDENTIAL_EXISTS)
    check("RATE_LIMITED", exit_for_code("RATE_LIMITED"), EXIT_RATE_LIMITED)
    check("未知 code 归 21", exit_for_code("SOMETHING_NEW"), EXIT_BAD_RESPONSE)


def _capture_checks(data, expect_session=None) -> list[str]:
    """跑一次结构校验，收集 client_check=<key>；硬失败让它抛出去。"""
    keys: list[str] = []
    original = transport.warn
    transport.warn = lambda msg: keys.append(msg.split("client_check=", 1)[1].split("：")[0]
                                             if "client_check=" in msg else msg)
    try:
        transport.check_session_data(data, expect_session=expect_session)
    finally:
        transport.warn = original
    return keys


def _base(**over) -> dict:
    data = {"sessionId": "sess_a", "status": "已定位", "layer": "L2 实时证据排障",
            "conclusion": "结论正文", "evidence": [{"id": "ev_1"}], "confidence": 0.9}
    data.update(over)
    return data


def test_session_mismatch_is_hard_failure() -> None:
    """串会话可能拿到别人的证据，必须拒收而不是降级呈现。"""
    try:
        transport.check_session_data(_base(sessionId="sess_other"), expect_session="sess_a")
    except DiagError as exc:
        check("串会话退出码", exc.exit_code, EXIT_BAD_RESPONSE)
    else:
        FAILED.append("串会话未被拒收")

    # create 时无 --session，不该因此报错
    check("create 无期望会话", _capture_checks(_base(), expect_session=None), [])
    check("会话号一致", _capture_checks(_base(), expect_session="sess_a"), [])


def test_status_hard_failures() -> None:
    for label, data in (("缺 status", {"sessionId": "s"}),
                        ("未知 status", {"sessionId": "s", "status": "DONE"}),
                        ("英文内部码", {"sessionId": "s", "status": "NEED_INFO"}),
                        ("data 非对象", ["x"])):
        try:
            transport.check_session_data(data)
        except DiagError as exc:
            check(f"{label} 退出码", exc.exit_code, EXIT_BAD_RESPONSE)
        else:
            FAILED.append(f"{label} 未被拒收")


def test_self_consistency_warnings() -> None:
    check("已定位无证据", _capture_checks(_base(evidence=[])), ["located_without_evidence"])
    check("知识建议带证据",
          _capture_checks(_base(status="知识建议", layer="L1 知识建议")), ["knowledge_with_evidence"])
    check("layer 与 status 不符",
          _capture_checks(_base(layer="L1 知识建议")), ["layer_status_mismatch"])
    check("终态无结论", _capture_checks(_base(conclusion="   ")), ["empty_conclusion"])
    check("置信度越界", _capture_checks(_base(confidence=1.7)), ["bad_confidence"])
    check("置信度非数值", _capture_checks(_base(confidence="高")), ["bad_confidence"])
    check("置信度 True 不算数值", _capture_checks(_base(confidence=True)), ["bad_confidence"])
    check("证据非数组", _capture_checks(_base(evidence={"id": "ev_1"})),
          ["bad_evidence_type", "located_without_evidence"])
    check("无 sessionId", _capture_checks(_base(sessionId=None)), ["missing_session_id"])
    check("待补充信息无 needInfos",
          _capture_checks({"sessionId": "s", "status": "待补充信息", "layer": "未进入排障"}),
          ["need_info_without_needinfos"])
    check("只有 nextQuestion",
          _capture_checks({"sessionId": "s", "status": "待补充信息", "layer": "未进入排障",
                           "nextQuestion": "请提供商户号"}),
          ["need_info_without_needinfos", "needinfos_empty_with_question"])
    check("诊断中须轮询",
          _capture_checks({"sessionId": "s", "status": "诊断中", "layer": "L2 实时证据排障"}),
          ["status_diagnosing"])
    check("已关闭不自动建单",
          _capture_checks({"sessionId": "s", "status": "已关闭", "layer": "未进入排障"}),
          ["status_closed"])
    check("结构完好不报", _capture_checks(_base(confidence=0)), [])


def test_context_path() -> None:
    """context-path 只能出现一次：submitPath 可能不带前缀，文档示例带，两种都要成立。"""
    base = "http://h:1"
    check("字面量补前缀", transport.build_url(base, "/v1/auth/token"),
          "http://h:1/yop-agent/v1/auth/token")
    check("submitPath 已带前缀不重复加",
          transport.build_url(base, "/yop-agent/v1/diagnosis/sessions/s/messages"),
          "http://h:1/yop-agent/v1/diagnosis/sessions/s/messages")
    check("base 已含前缀不重复加", transport.build_url("http://h:1/yop-agent", "/v1/auth/token"),
          "http://h:1/yop-agent/v1/auth/token")
    check("base 结尾斜杠", transport.build_url("http://h:1/", "/v1/auth/token"),
          "http://h:1/yop-agent/v1/auth/token")


def _scan(name: str, body: bytes):
    import tempfile

    path = Path(tempfile.mkdtemp()) / name
    path.write_bytes(body)
    return scan_attachment(path)


def test_attachment_scan() -> None:
    """附件是唯一绕过脱敏的通道：只拒私钥材料，密文日志必须放行。"""
    refuse, _ = _scan("app.pem", b"whatever")
    check("私钥扩展名拒传", bool(refuse), True)
    refuse, _ = _scan("dump.txt", b"x-----BEGIN RSA PRIVATE KEY-----x")
    check("PEM 私钥块拒传", bool(refuse), True)
    refuse, notes = _scan("platform.crt", b"-----BEGIN CERTIFICATE-----\nMIIB\n")
    check("公钥证书放行", refuse, [])
    check("公钥证书给提醒", any("CERTIFICATE" in n for n in notes), True)
    # 回调排障要传的就是这种含密文报文的日志，拦掉等于把功能废了
    refuse, notes = _scan("notify.log", b"resp=" + b"A" * 600 + b" mobile=13800138000")
    check("密文日志放行", refuse, [])
    check("密文串给提醒", any("Base64" in n for n in notes), True)
    check("个人信息只数 PII 不含密钥", any("1 处个人信息" in n for n in notes), True)
    refuse, notes = _scan("plain.txt", b"signature verify failed")
    check("干净文件无拒绝无提醒", (refuse, notes), ([], []))


def _store(monkey_entries: dict):
    """把 credentials 的存储换成内存字典，避免自测读写真实 ~/.yeepay。"""
    from diag import credentials

    credentials._load_all = lambda: monkey_entries
    return credentials


def test_credential_pick() -> None:
    """凭证决定可见范围：不能替用户挑，也不能默认唯一那条就是对的。"""
    from diag.errors import EXIT_LOCAL_INVALID, EXIT_NO_CREDENTIAL

    one = {"a@SANDBOX": {"appKey": "a", "environment": "SANDBOX", "accessToken": "t"}}
    two = dict(one, **{"b@SANDBOX": {"appKey": "b", "environment": "SANDBOX", "accessToken": "t"}})

    creds = _store(one)
    check("唯一条目可隐式取用", creds.find(None, "SANDBOX")["appKey"], "a")

    creds = _store(two)
    try:
        creds.find(None, "SANDBOX")
        check("多条目须显式指定", "未抛错", "应抛 DiagError")
    except DiagError as exc:
        # 缺的是「用哪个」这个决定，不是缺凭证——所以是 2 不是 10
        check("多条目退出码", exc.exit_code, EXIT_LOCAL_INVALID)
        check("多条目列出候选", "a@SANDBOX" in exc.message and "b@SANDBOX" in exc.message, True)

    try:
        creds.find("c", "SANDBOX")
        check("指定的应用不存在须报错", "未抛错", "应抛 DiagError")
    except DiagError as exc:
        check("不存在时退出码", exc.exit_code, EXIT_NO_CREDENTIAL)
        check("不存在时劝阻改用他人凭证", "不要改用" in exc.message, True)


def test_default_base_url() -> None:
    """入口固定；环境不换主机；--base-url / 环境变量可覆盖。"""
    old = os.environ.pop("YOP_AGENT_BASE_URL", None)
    try:
        check("默认入口", transport.resolve_base_url("SANDBOX"), "https://sandbox.yeepay.com")
        check("生产同一入口", transport.resolve_base_url("PRODUCT"), "https://sandbox.yeepay.com")
        check("参数覆盖", transport.resolve_base_url("SANDBOX", "http://h:1/"), "http://h:1")
        os.environ["YOP_AGENT_BASE_URL"] = "http://from-env"
        check("环境变量覆盖", transport.resolve_base_url("PRODUCT"), "http://from-env")
        check("参数优先于环境变量",
              transport.resolve_base_url("PRODUCT", "http://from-arg"), "http://from-arg")
    finally:
        if old is None:
            os.environ.pop("YOP_AGENT_BASE_URL", None)
        else:
            os.environ["YOP_AGENT_BASE_URL"] = old


def main() -> int:
    for func in (
        test_secrets_are_redacted,
        test_business_ids_survive,
        test_slot_values_only_filter_secrets,
        test_free_text_truncated,
        test_slot_whitelist,
        test_time_window,
        test_real_code_mapping,
        test_code_mapping,
        test_session_mismatch_is_hard_failure,
        test_status_hard_failures,
        test_self_consistency_warnings,
        test_context_path,
        test_attachment_scan,
        test_credential_pick,
        test_environment_field,
        test_ticket_inline_error,
        test_default_base_url,
    ):
        func()
    if FAILED:
        print("diag 自测未通过：")
        for item in FAILED:
            print(f"  - {item}")
        return 1
    print("diag 自测通过（脱敏 / 业务单号保真 / 槽位白名单 / 时间窗 / 两套错误码映射 / "
          "响应自洽校验 / URL 前缀 / 附件体检 / 凭证选择 / 环境参数 / 提单限流）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
