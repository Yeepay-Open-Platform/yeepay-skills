# diag — 远端排障通道

与易宝排障服务 `yop-agent` 通信的**唯一**通道。协议与边界见
`references/排障/diagnostic-protocol.md`；离线态边界见 `references/排障/offline-l1.md`。

**跑任何 diag 脚本前先跑 `diag_env.py`**（与 `tools/check_python_env.py` 同一纪律）。

## 脚本

| 脚本 | 用途 |
| --- | --- |
| `diag_env.py` | 本地自检：Python、依赖、本地 token 状态、yop-agent 连通性。**不外发任何用户数据** |
| `diag_auth.py` | 兑换 / 吊销诊断 token（`--revoke`）、列出本地 token（`--list`） |
| `diag_session.py` | 创建 / 继续 / 查询排障会话 |
| `diag_knowledge.py` | 查平台公开知识库（**匿名，不需要凭证**）：`search` / `list` / `get` / `verify-map` |
| `diag_ticket.py` | 创建 support-ticket 工单与上传附件（默认预览，`--confirm` 才真建/真传） |
| `tests/test_redact.py` | 自测：脱敏、业务单号保真、槽位白名单、时间窗、错误码映射 |

内部模块：`transport.py`（HTTP + Bearer + 解包 + 结构校验）、`signer.py`（appKey 签名，RSA/SM2）、
`credentials.py`（`~/.yeepay/diag/credentials.json`，0600）、`redact.py`（脱敏兜底）、
`slots.py`（槽位白名单与时间窗校验）、`errors.py`（退出码映射）。

每次与服务端交互都会在 stderr 打印 `sessionId=...`，便于与 yop-agent 日志（`sessionId=...`）联查。

**所有端点挂在 `/yop-agent` 下**（2026-08-31 起）。前缀只在 `transport.build_url()` 拼一次，脚本里的路径字面量仍写 `/v1/...`；服务端 `needInfos.submitPath` 可能不带前缀，`build_url` 对带与不带都成立。需要时用 `YOP_AGENT_CONTEXT_PATH` 覆盖。

服务端已下线工单草稿链路（`/ticket-draft` 废弃），`diag_ticket.py` 直接调 `POST /v1/support-ticket/tickets` 建正式工单——所以默认是 `--dry-run` 预览，**只有加 `--confirm` 才真建**。

## 典型链路

```bash
# 0) 自检
python diag/diag_env.py --env SANDBOX

# 1) 兑换 token（私钥只传路径；RSA 与 SM2 都支持，算法按密钥类型自动选）
python diag/diag_auth.py --app-key app_100xxx --private-key ./keys/rsa_private_pkcs8.pem --env SANDBOX

# 2) 创建会话（请求走文件，不走命令行参数）
cat > /tmp/req.json <<'JSON'
{"source":"SKILL","initialMessage":"商户反馈支付成功后没有收到回调",
 "merchantNo":"10080792238","startTime":"2026-08-26 00:00:00","endTime":"2026-08-26 23:59:59",
 "slots":{"orderId":"389565332051589553"}}
JSON
python diag/diag_session.py create --json /tmp/req.json

# 3) 按响应 needInfos 补槽（一次性问全用户，再一次提交）
cat > /tmp/more.json <<'JSON'
{"message":"补充 requestId","slots":{"requestId":"1804d5f4e55b48559abf82153ddae702"}}
JSON
python diag/diag_session.py continue --session sess_xxx --json /tmp/more.json

# 4) 查询会话当前状态、槽位、结论与证据
python diag/diag_session.py get --session sess_xxx

# 用户换了个问题（不是补槽）→ 起新会话，不要在旧 session 上 continue
python diag/diag_session.py create --json /tmp/another.json

# 4b) 本地知识不够 / 用户没有凭证：查平台公开知识库（匿名，关键词在本地匹配，不外发）
python diag/diag_knowledge.py search "回调 通知 未收到" --limit 5
python diag/diag_knowledge.py get kn-docs-78a9fc48deabe08d
python diag/diag_knowledge.py verify-map     # 核对 knowledge-map.yaml 的 knowledgeId 是否真实存在

# 5) 需要人工介入时：先预览工单内容给用户看
python diag/diag_ticket.py --session sess_xxx --merchant-no 100xxx \
  --title "支付成功但未收到回调" --scene 回调未收到 --priority HIGH
# 用户明确同意后才真建
python diag/diag_ticket.py --session sess_xxx --merchant-no 100xxx \
  --title "支付成功但未收到回调" --scene 回调未收到 --confirm

# 6) 工单附件：同样默认预览，--confirm 才真传
python diag/diag_ticket.py --session sess_xxx --ticket-id tk_xxx --attach /tmp/notify.log
python diag/diag_ticket.py --session sess_xxx --ticket-id tk_xxx --attach /tmp/notify.log --confirm

# 远端不可用时：用本地已收集信息拼工单内容供用户自行提交（标注「未经平台生成」）
python diag/diag_ticket.py --session sess_xxx --merchant-no 100xxx --offline \
  --phenomenon "支付成功但未收到回调" --slots-json /tmp/slots.json
```

> **SM2 可用**（客户端默认传参形式即可）。同一算法下不同应用结果可能不同，
> 失败原因通常在该应用的证书/密钥状态。SM2 兑换失败时按普通签名失败
> 处理（退出码 `11`：核对私钥与平台报备证书是否匹配），**不要**说成「服务端不支持国密」。

## 职责边界（别越线）

- CLI 是**传输层与安全层，不是决策层**：不解释响应、不归纳结论、不替 Skill 判断该不该转人工。
  服务端 `data` 原样打到 stdout，结构异常与被丢弃字段写 stderr。
- 是否降级呈现（如 `已定位` 无证据按 `暂未定位` 处理）由 **Skill 按 SKILL.md 纪律**执行，
  CLI 只在 stderr 给出 `client_check=...` 提示。`status` / `layer` / `playbookId` 只认中文展示值。
- 不缓存任何查询结果，证据不落盘。
- **公开知识库是 L1**：`diag_knowledge.py` 拿到的是平台文档派生的知识，不是该商户的实时数据；
  查到条目不等于查过平台，呈现仍用 D1 模板。检索在本机做，用户问题描述不外发。
- **一个 sessionId 只服务一个问题**：补槽用 `continue`，换问题用 `create`。服务端按会话
  累积槽位与轮次，串会话会带着上一个问题的商户号和时间窗去查。判定清单见 SKILL.md
  「会话边界：一个问题一个会话」。

## 响应自洽校验

结论内容不改写，但要确认**结构自洽**——数据自相矛盾时按较弱的一方呈现。

硬失败（退出 `21`，不呈现任何结论）只有两类：

| 情况 | 理由 |
| --- | --- |
| `data` 非对象 / 缺 `status` / `status` 不在枚举内 | 没法判断怎么呈现 |
| 响应 `sessionId` ≠ 请求的 `--session` | **可能是别人的会话与证据**，属安全问题，拒收而非降级 |

其余写 stderr（`client_check=<key>`，不改动 `data`）：`located_without_evidence`、
`knowledge_with_evidence`、`layer_status_mismatch`、`empty_conclusion`、`bad_confidence`、
`bad_<field>_type`、`missing_session_id`、`need_info_without_needinfos`、
`needinfos_empty_with_question`、`status_diagnosing`、`status_closed`。逐条处理方式见 SKILL.md 的降级表。

校验只判自洽、不判对错：不核对 `conclusion` 内容、不判断证据是否支持结论——那是服务端职责，
本地判不了，也与「远端结论不可改写」红线冲突。

## 附件：唯一能绕过脱敏的通道

自由文本与槽位都过两道脱敏，**二进制附件不过**——它是原样出境的。所以上传前本地体检
（`redact.scan_attachment`），分两档：

| 结果 | 处理 |
| --- | --- |
| 私钥特征：`.pem`/`.key`/`.p12`/`.pfx`/`.jks`/`.env`/`credentials.json`/`yop_sdk_config*.json`，或 PEM 私钥块 | **拒传**，退出 `2` |
| 公钥证书、超长 Base64 串、个人信息特征 | 只提醒 `attachment_check：…`，交用户决定 |

第二档刻意不拒：排查回调解密/验签失败时要传的正是含密文报文的日志，一律拦掉等于把功能废了。
本地另拦空文件与 >10MB（服务端口径：单文件 10MB、单次请求 12MB，超限 `YOP-AGTA0413`）。
预览输出含文件名、字节数与 SHA-256，供用户核对传的是哪个文件。上传频率 10/分钟、100/天，
超限走 **HTTP 429** → 退出 `14`。**附件不支持删除**，传错了没有回退手段。

## 安全

- **私钥只收文件路径**，拒绝粘贴的 PEM 内容；请求体只含 `appKey` / `environment` / `signature`。
  `--private-key` 接受两种文件：PEM 私钥，或 `yop_sdk_config*.json`（自动读 `isv_private_key.value`，
  多条时按 `--app-key` 匹配）。
- 请求体绝不含 `slots.appKey`（会被强制剔除并在 stderr 提示）——可见范围由服务端按 token 判定。
  `environment` 自 2026-08-31 起是**合法字段**（会话级，决定查沙箱还是生产），但 CLI **不按
  `--env` 自动补**：继续会话时不传即沿用会话环境，自动补默认值会把上一轮指定的生产改回沙箱。
  未指定时给 `environment=default`，与凭证签发环境不一致时给 `environment_override=<env>`。
- `merchantNo` 只能取用户明确提供或服务端 `needInfos` 点名的值，**不得**从工作区代码或配置推断。
- token 存 `~/.yeepay/diag/credentials.json`（0600），日志与终端只出现掩码值。
- **凭证选择不静默**：每次使用都在 stderr 打印 `使用凭证 <appKey>@<环境>`；未指定 `--app-key`
  而用了本环境唯一条目时额外给 `credential_pick=implicit`；本环境有多条时**退出 `2`** 并列出
  候选，由用户决定用哪个——凭证决定可见范围，挑错了查到的是另一个应用的数据。
- **不再需要的凭证要吊销**（`diag_auth.py --revoke`，需私钥签名），但须用户同意：同一
  `appKey + environment` 的凭证可能正被另一台机器使用。`diag_env.py` 会提示本地滞留的有效凭证。
- 脱敏两道：自由文本过全量规则（密钥 + 卡号/身份证/手机号，数字类带 Luhn 与出生日期校验，
  避免误伤业务单号）；结构化 slot 值只过密钥类规则，由白名单 + 格式校验兜住。

## 退出码

| 码 | 含义 | Skill 行为 |
| --- | --- | --- |
| `0` | 成功 | 按 D2 呈现（`client_check` 提示需按纪律降级时先降级） |
| `2` | 本地校验失败未发请求（含 environment 取值非法、多凭证未指定）；服务端 `YOP-AGTA0400` / `YOP-AGTA0404`（session 不存在）／ `YOP-AGTA0413`（附件超限） | 修正输入后重试，必要时起新会话 |
| `10` | 无 token / `AUTH_MISSING` | 离线 L1，一次性告知可兑换 |
| `11` | 私钥/密钥类型/签名问题、`AUTH_INVALID` | 停止，不重试、不改用其他密钥 |
| `12` | token 过期/已吊销 | 离线 L1，提示重新兑换 |
| `13` | 范围或环境校验失败 | 停止，不重试、不换参数再试 |
| `14` | 限流：提单顶层 `code=YOP-AGTA0429`（旧口径 `data.errorCode=YOP-AGT10429` 仍收下）／附件 HTTP 429 | 如实告知配额（提单 3/分·20/天，附件 10/分·100/天），稍后再试 |
| `15` | `CREDENTIAL_EXISTS` | 复用本地条目，或用户确认后先 `--revoke`；不自动吊销 |
| `20` | 超时 / 5xx / 连不上 / `YOP-AGTB0500` | 离线 L1 + 引导工单 |
| `21` | 响应结构非法 / 未知 code | 丢弃响应，不呈现结论，转工单 |

## 超时与重试

| 接口 | 读超时 | 重试 |
| --- | --- | --- |
| 创建会话 `create` | **90s** | **不重试** |
| 其余（兑换/吊销/继续/查询/建单） | 30s | 连不上或 5xx 重试 1 次 |

创建会话要跑场景识别 + L2 实时查询 + 模型成文，读超时放宽到 90s。它**不重试**是因为没有幂等键——超时重发可能让服务端建出第二个会话，后续补槽会打到错误的 `sessionId` 上；宁可返回 `20` 让用户重来。

超时后想拿回上一次的结论，用 `diag_session.py get --session <id>`，不要重新 `create`。

## 环境地址

默认入口 **`https://sandbox.yeepay.com`**，SANDBOX / PRODUCT 共用；查哪个环境由 `--env` 与请求体 `environment` 决定，不换主机。

可用 `--base-url` 或环境变量 `YOP_AGENT_BASE_URL` 覆盖默认入口。未覆盖时不再因 PRODUCT 缺地址而报错。
