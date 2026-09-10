#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""创建 support-ticket 工单（经 yop-agent 代理）。

契约：POST /yop-agent/v1/support-ticket/tickets。**服务端已下线草稿链路**
（`/ticket-draft` 废弃），本接口直接创建正式工单；附件走
POST /yop-agent/v1/support-ticket/tickets/{ticketId}/attachments。

因此本脚本的纪律是：**不静默建单、不静默上传**。
    默认         只打印将要提交/上传的内容，不落地；把它展示给用户确认
    --confirm    用户明确同意后才真正建单或上传

服务端按「一天内同 playbookId 不重复」去重，命中去重会返回已有 ticketNo
且 duplicated=true，不会重复建单。

用法：
    python diag/diag_ticket.py --session sess_xxx --merchant-no 100xxx \
        --title "生产环境支付成功但未收到回调" [--scene 回调未收到] [--priority HIGH]
    # 用户确认后追加 --confirm

    # 建单成功后上传附件（单个 ≤10MB，每单最多 10 个，以服务端校验为准）
    python diag/diag_ticket.py --session sess_xxx --ticket-id tk_xxx --attach /tmp/notify.log
    # 用户确认后追加 --confirm
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from diag._bootstrap import normalize_env, run  # noqa: E402
from diag import credentials, transport  # noqa: E402
from diag.errors import EXIT_LOCAL_INVALID, DiagError, exit_for_code  # noqa: E402
from diag.redact import redact_text, scan_attachment  # noqa: E402
from diag.slots import filter_slots  # noqa: E402

PRIORITIES = ("LOW", "NORMAL", "HIGH", "URGENT")


def _upload_attachment(args) -> int:
    """上传工单附件。

    附件是绕过两道文本脱敏的通道——文本字段会被清洗，二进制文件原样出境。
    所以这里比建单还严：先本地体检，命中私钥特征直接拒传（不是清洗，私钥没有
    脱敏后还能用的版本），其余可疑项列成提醒交给用户，且同样要 --confirm。
    """
    path = Path(args.attach).expanduser()
    if not path.is_file():
        raise DiagError(EXIT_LOCAL_INVALID, f"附件不存在或不是文件：{path}")
    if not args.ticket_id:
        raise DiagError(EXIT_LOCAL_INVALID, "--attach 需要 --ticket-id（建单响应里的 ticketId）")

    size = path.stat().st_size
    if size == 0:
        raise DiagError(EXIT_LOCAL_INVALID, "附件为空文件")
    if size > transport.MAX_ATTACHMENT_BYTES:
        raise DiagError(
            EXIT_LOCAL_INVALID,
            f"附件 {size} 字节超过 {transport.MAX_ATTACHMENT_BYTES} 字节上限，请裁剪后再传",
        )

    refuse, notes = scan_attachment(path)
    for note in notes:
        transport.warn(f"attachment_check：{note}")
    if refuse:
        raise DiagError(
            EXIT_LOCAL_INVALID,
            "拒绝上传（" + "；".join(refuse) + "）。私钥与凭证一旦进工单系统就不在本机，"
            "请改传脱敏后的日志片段。",
        )

    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    transport.log_session(args.session, "附件")

    if not args.confirm:
        print(json.dumps({
            "dryRun": True,
            "note": "以上为将上传的附件。请把文件名与体检提醒完整展示给用户；"
                    "用户明确同意后加 --confirm 才会真正上传。",
            "willPostTo": f"/yop-agent/v1/support-ticket/tickets/{args.ticket_id}/attachments",
            "attachment": {"fileName": path.name, "bytes": size, "sha256": digest},
            "checks": notes or ["未命中敏感特征"],
        }, ensure_ascii=False, indent=2))
        return 0

    environment = normalize_env(args.env)
    base_url = transport.resolve_base_url(environment, args.base_url)
    entry = credentials.require(args.app_key, environment)
    data = transport.upload(
        base_url, f"/v1/support-ticket/tickets/{args.ticket_id}/attachments",
        token=entry["accessToken"], fields={"sessionId": args.session},
        file_path=path, session_id=args.session,
    )
    transport.emit(data)
    if isinstance(data, dict) and data.get("scanStatus") not in (None, "CLEAN"):
        transport.warn(f"attachment_scan={data.get('scanStatus')}：服务端敏感信息扫描未通过，附件可能未生效")
    return 0


def _check_ticket_result(data) -> None:
    """建单响应里的业务失败：新口径在顶层 code=YOP-AGTA0429（unwrap 已处理）；
    旧口径顶层仍是 00000、失败藏在 data.errorCode。这里兜住旧口径，避免把
    「超限、没建成」当成「已建单」报给用户。
    """
    if not isinstance(data, dict):
        return
    error_code = data.get("errorCode")
    if error_code:
        raise DiagError(
            exit_for_code(error_code, data.get("message") or ""),
            f"建单未成功：{error_code} {data.get('message') or ''}".strip(),
        )
    if not data.get("created") and not data.get("ticketNo"):
        transport.warn("ticket_check=not_created：响应既无 created 也无 ticketNo，不要告诉用户工单已建")
    if data.get("duplicated"):
        transport.warn("duplicated=true：命中服务端去重，返回的是已存在的工单，未新建")


def main() -> int:
    parser = argparse.ArgumentParser(description="经 yop-agent 创建 support-ticket 工单")
    parser.add_argument("--session", required=True, help="sessionId（必填，同时作为 businessKey；--offline 时仅作标识）")
    parser.add_argument("--merchant-no", help="商户号（建单必填，只能用用户提供或服务端点名的值；--attach 时不需要）")
    parser.add_argument("--ticket-id", help="--attach 时必填：建单响应里的 ticketId")
    parser.add_argument("--attach", help="上传附件的本地文件路径；同样默认预览，须 --confirm 才真传")
    parser.add_argument("--title", help="一句话现象，不要拼整段诊断")
    parser.add_argument("--scene", help="可选，传会话返回的 playbookId 展示值（如 回调未收到）；不传时服务端回退到会话命中的场景")
    parser.add_argument("--priority", choices=PRIORITIES, default="NORMAL")
    parser.add_argument("--routing-dimension", help="如 INDUSTRY_LINE")
    parser.add_argument("--routing-value", help="如 RETAIL")
    parser.add_argument("--confirm", action="store_true",
                        help="用户已明确同意建单；不加则只预览（不建单）")
    parser.add_argument("--offline", action="store_true",
                        help="远端不可用（退出码 20）时用本地已收集信息拼工单内容，供用户自行提交")
    parser.add_argument("--phenomenon", help="--offline 时的现象描述")
    parser.add_argument("--slots-json", help="--offline 时已收集槽位的 JSON 文件")
    parser.add_argument("--env", default="SANDBOX", help="SANDBOX / PRODUCT")
    parser.add_argument("--base-url", help="覆盖 yop-agent 地址")
    parser.add_argument("--app-key", help="本地有多个 token 时指定")
    args = parser.parse_args()

    if args.attach:
        return _upload_attachment(args)
    if not args.merchant_no:
        raise DiagError(EXIT_LOCAL_INVALID, "建单缺少 --merchant-no")

    if args.title:
        title, redacted = redact_text(args.title)
        if redacted:
            transport.warn(f"redactedCount={redacted}：标题已本地脱敏，须告知用户清洗处数")
    else:
        title = None

    payload: dict = {"sessionId": args.session, "merchantNo": args.merchant_no,
                     "priority": args.priority}
    if title:
        payload["title"] = title
    if args.scene:
        payload["scene"] = args.scene
    if args.routing_dimension and args.routing_value:
        payload["routingContext"] = {
            "dimension": args.routing_dimension,
            "value": args.routing_value,
            "source": "yeepay-payment-integration",
            "version": "v1",
        }
    elif args.routing_dimension or args.routing_value:
        raise DiagError(EXIT_LOCAL_INVALID, "--routing-dimension 与 --routing-value 必须同时提供")

    # 可信身份字段由服务端覆盖，客户端不得伪造
    for forbidden in ("queue", "source", "sourceSystem", "tenantId", "actor", "businessKey"):
        payload.pop(forbidden, None)

    transport.log_session(args.session, "工单")

    if args.offline:
        # 远端不可用时也得让用户拿到能自己提交的内容，但必须标明不是平台生成的
        collected = {}
        if args.slots_json:
            slots_path = Path(args.slots_json).expanduser()
            if not slots_path.is_file():
                raise DiagError(EXIT_LOCAL_INVALID, f"槽位文件不存在：{slots_path}")
            try:
                collected = json.loads(slots_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise DiagError(EXIT_LOCAL_INVALID, f"槽位文件不是合法 JSON：{exc}")
            if not isinstance(collected, dict):
                raise DiagError(EXIT_LOCAL_INVALID, "槽位文件顶层须为对象")
            collected = filter_slots(collected, transport.warn)
        phenomenon, redacted_p = redact_text(args.phenomenon or title or "（未提供现象描述）")
        if redacted_p:
            transport.warn(f"redactedCount={redacted_p}：现象描述已本地脱敏，须告知用户清洗处数")
        print(json.dumps({
            "offline": True,
            "note": "远端排障服务不可用，以下内容由本地已收集信息拼成，**未经平台生成**，"
                    "不含任何平台实时事实；请用户自行在控制台提交工单。",
            "sessionId": args.session,
            "merchantNo": args.merchant_no,
            "phenomenon": phenomenon,
            "collectedSlots": collected,
            "priority": args.priority,
        }, ensure_ascii=False, indent=2))
        return 0

    if not args.confirm:
        print(json.dumps({
            "dryRun": True,
            "note": "以上为将提交的工单内容。请完整展示给用户；用户明确同意后加 --confirm 才会真正建单。",
            "willPostTo": "/yop-agent/v1/support-ticket/tickets",
            "payload": payload,
        }, ensure_ascii=False, indent=2))
        return 0

    environment = normalize_env(args.env)
    base_url = transport.resolve_base_url(environment, args.base_url)
    entry = credentials.require(args.app_key, environment)
    data = transport.request("POST", base_url, "/v1/support-ticket/tickets",
                             token=entry["accessToken"], payload=payload,
                             session_id=args.session)
    _check_ticket_result(data)
    transport.emit(data)
    return 0


if __name__ == "__main__":
    sys.exit(run(main))
