# 远端排障交互协议（yop-agent）

本文是 Skill 与易宝排障服务 `yop-agent` 交互的**契约参考**，字段与状态以服务端接口文档为准。

> `scripts/diag/` 提供 `diag_env.py` / `diag_auth.py` / `diag_session.py` / `diag_ticket.py`。无凭证或远端不可用时走 `references/排障/offline-l1.md` 的离线 L1。

## 一、边界（三条硬约束）

1. **唯一通道**：与排障服务的一切通信只经 `scripts/diag/` CLI。不用 `curl` 调排障端点，不直连知识库、不直连日志、不直连底层诊断工具（`diagnose_notify_trace` / `diagnose_invoke_log` 等由服务端按 playbook 调度）。
2. **不做决策**：识别场景、选 playbook、是否升 L2、调哪些只读工具、生成结论，**全在服务端**。Skill 只负责采集、传输安全与呈现；CLI 只负责传输与安全，不解释响应。
3. **不落盘**：证据与结论只在本轮对话呈现，不写入工作区、不进 git、不在下一轮从本地缓存复用。`sessionId` 可记录，用于与服务端日志联查。
4. **能本地解决就不上远端**：持有诊断凭证不等于每个问题都走 L2。`knowledge-map.yaml` 里 `evidenceRequired: false` 的条目在本地就是终答，不调远端；`true` 的条目先给本地自查建议，需要该商户实时事实时才升 L2。用户直接索要某一笔的平台事实时，有凭证则经⑤后 `create`，不要先堆自查清单；用户已贴控制台截图时只复述可见字段，截图不是 L2。判定与话术见 `SKILL.md`「先本地，后远端」与「帮我查一下这笔」。
5. **一个问题一个会话**：`sessionId` 按会话累积槽位、命中剧本、计轮次，把新问题塞进旧会话会带着上一个问题的商户号与时间窗去查。判定见下方第六节之二。

## 二、端点

环境地址：默认 `https://sandbox.yeepay.com`（SANDBOX / PRODUCT 同一入口，查哪个环境由请求 `environment` 决定）。可用 `--base-url` 或环境变量 `YOP_AGENT_BASE_URL` 覆盖。

**所有端点挂在 `/yop-agent` 下**（2026-08-31 起；不带前缀的老路径返回 Tomcat 404 HTML，不是业务错误码）。前缀由 `transport.build_url()` 统一拼接，代码里的路径字面量仍写 `/v1/...`；需要时可用环境变量 `YOP_AGENT_CONTEXT_PATH` 覆盖。

| 用途 | 方法与路径 | 鉴权 |
| --- | --- | --- |
| 签发诊断 token | `POST /yop-agent/v1/auth/token` | 签名 |
| 吊销诊断 token | `POST /yop-agent/v1/auth/revoke` | 签名 |
| 创建排障会话 | `POST /yop-agent/v1/diagnosis/sessions` | Bearer |
| 继续会话 / 补充槽位 | `POST /yop-agent/v1/diagnosis/sessions/{sessionId}/messages` | Bearer |
| 查询会话 | `GET /yop-agent/v1/diagnosis/sessions/{sessionId}` | Bearer |
| 公开知识列表 | `GET /yop-agent/v1/knowledge/summaries` | **无** |
| 公开知识详情 | `GET /yop-agent/v1/knowledge/{knowledgeId}` | **无** |
| 创建工单 | `POST /yop-agent/v1/support-ticket/tickets` | Bearer |
| 上传工单附件 | `POST /yop-agent/v1/support-ticket/tickets/{ticketId}/attachments` | Bearer（multipart） |

> `needInfos.submitPath` 可能返回不带 `/yop-agent` 前缀的 `/v1/diagnosis/sessions/{id}/messages`。`build_url()` 对带前缀与不带前缀都成立（已带前缀就不重复加），照 `submitPath` 走即可。

**没有独立的错误码方案端点**：L2 命中错误码时由服务端自动补查方案并并入结论。
**工单草稿链路已下线**：`POST /v1/diagnosis/sessions/{sessionId}/ticket-draft` 废弃，统一用 `POST /v1/support-ticket/tickets` **直接建正式工单**（见第八节）。

## 三、鉴权

签名：用商户应用私钥对 **`appKey` 原文**签名。算法**按本地密钥类型决定**，用户无需声明：

| 本地密钥 | 算法 | 传参 |
| --- | --- | --- |
| RSA | `SHA256withRSA`（兼容 `SHA1withRSA`） | Base64 值，或 `签名值$SHA256` / `签名值$SHA1` |
| SM2 | `SM3withSM2` | Base64 值 + `$SM3`（客户端默认 urlsafe 编码） |
| CFCA 证书 | 取出证书内私钥后按其类型走上面两行 | 同上 |

服务端按 appKey 在库中的密钥数据识别类型并验签。

```json
POST /v1/auth/token
{ "appKey": "app_10080792238", "environment": "SANDBOX", "signature": "base64-signature" }
```

返回 `data.accessToken`（前缀 `yp-sk-`）、`expiresIn`（604800 秒 = 7 天）、绑定的 `appKey` 与 `environment`。后续请求用 `Authorization: Bearer <accessToken>`。

- **`environment` 已改为会话级参数（2026-08-31 契约变更）**。签发时传的那个只是**默认环境**，不再限制后续会话。同一 `appKey` 可能沙箱、生产都存在，实际查哪个按优先级取：

  | 动作 | 优先级 |
  | --- | --- |
  | 创建会话 | 请求 `environment` / `slots.environment` > token 默认环境 |
  | 继续会话 | 请求 `environment` / `slots.environment` > **会话已存环境** > token 默认环境 |

  取值 `SANDBOX`（含 `QA` / `TEST`）或 `PRODUCT`（含 `PROD` / `PRODUCTION`），顶层优先，`slots.environment` 为兼容写法。

  **客户端不按 `--env` 自动补这个字段**，只透传请求文件里显式写的值。原因是继续会话：`--env` 有默认值 `SANDBOX`，每轮自动补就会把上一轮指定的生产悄悄改回沙箱，而服务端本来设计成「不传就沿用会话环境」。不传时 CLI 给 `environment=default` 提示，显式值与凭证签发环境不一致时给 `environment_override=<env>` 提示——查的是哪个环境决定了「平台侧没有记录」这句话的真假，不能悄悄发生。
- 同一 `appKey + environment` 已有未过期 token 时**不能重复签发**（`CREDENTIAL_EXISTS`），须先 `/v1/auth/revoke` 或等过期。**不要自动吊销重签**——已有 token 可能正被另一台机器使用。
- **凭证决定可见范围，因此「用哪个」必须先确认再动手**。本地条目的选择规则：显式 `--app-key` 优先；未指定且本环境只有一条时用它，但 CLI 会打 `credential_pick=implicit` 要求核对；有多条时**直接退出 `2`** 并列出候选，由用户决定，客户端不替他挑。指定的 appKey 本地没有、但有别的应用的条目时，报错会列出已有条目并明确「不要改用它们」。每次使用都会在 stderr 打印 `使用凭证 <appKey>@<环境>`——用错应用查到的是另一个应用的数据，而结论看起来同样可信，只能靠这行当场发现。
- **不再需要时应吊销，但必须用户同意**。凭证有效期 7 天且不随对话结束失效；排障收尾、已转工单、换了应用时要主动询问是否 `--revoke`。吊销需私钥签名，须提前告知用户要再提供一次私钥路径；用户不便时如实说明凭证将于到期时间自然过期，不得声称已清理。
- **私钥只收路径**：只向用户索要私钥文件路径（PEM 私钥文件，或 `yop_sdk_config*.json`——CLI 会读其中的 `isv_private_key.value`），由 CLI 读文件本地签名。用户粘贴私钥内容时提示「已在本地丢弃，请改为提供文件路径」。
- `signature` 不是 secret，但也不展示、不存储；日志与终端**不得打印完整 `accessToken`**。
- **CFCA 证书口令**从环境变量或交互输入读取，不落盘、不回显、不进 shell 历史。密钥类型无法识别时明确报错（退出码 `11`），不静默失败。
- **密钥类型判定**优先取 `yop_sdk_config` 里的 `cert_type`：配置中的 `value` 常是无 PEM 头的裸 Base64，光看内容分不清 RSA 与 SM2。
- **SM2 已可兑换**（客户端默认传参形式即可）。同一算法下不同应用结果可能不同，失败原因通常在该应用的证书/密钥状态，不是算法不支持。因此 SM2 兑换失败时不要说「服务端不支持国密」，应按普通签名失败处理（退出码 `11`）：核对私钥与该 appKey 在平台报备的证书是否匹配。

## 四、槽位白名单（闭集，双向）

**对上**：排障阶段只允许向用户收集这些字段。**对下**：CLI 丢弃请求 JSON 里的未知 key 并在 stderr 提示。必须是白名单而不是黑名单——黑名单永远列不全，而模型在长对话里会很自然地把刚读过的代码片段塞进请求。

| 字段 | 说明 |
| --- | --- |
| `merchantNo` | 商户号。回调类排障的核心必需信息 |
| `startTime` / `endTime` | `yyyy-MM-dd HH:mm:ss`；未传、格式错、先后颠倒或跨度 >1 天时服务端回落到当天 00:00:00~23:59:59 |
| `requestId` | 网关调用 requestId。**不是**通知查询主条件，只在通知链路无数据时辅助查 invoke 日志 |
| `orderId` | 业务订单号，提升通知链路查询精度，非必填 |
| `notifyOrderId` / `notificationId` | 通知订单号，两个字段同义，都在白名单里 |
| `environment` | 本次排障实际环境；顶层优先，`slots.environment` 兼容 |
| `errorCode` / `subErrorCode` | 错误码与子错误码 |
| `apiUri` | 接口 URI |
| `time_range` | 契约标为兼容旧字段；部分剧本会主动索要它，仅在服务端点名时填，优先仍用 `startTime`/`endTime` |
| `initialMessage` / `message` | 唯一自由文本字段，≤2000 字符且过脱敏 |

**禁止出现在请求体里**：`slots.appKey`（生产禁止覆盖，`APP_OVERRIDE_DENIED`）。CLI 强制剔除，即使调用方传入。

`environment` 曾在此列，**2026-08-31 起改为合法字段**（见第三节）。取值非法时 CLI 本地报错退出 `2`，不放给服务端——服务端对认不出的值会回落到默认环境，那意味着用户以为查生产、实际查了沙箱，再拿到一句「平台侧没有记录」当事实。
`time_range` 为兼容旧字段，新接入不使用。

槽位值（`merchantNo` / `requestId` / `orderId` / `notifyOrderId` / 时间窗等）**只能**来自用户本轮明确提供或确认。服务端 `needInfos` 点名的意思是**问用户**，不是让 Skill 去工作区、`.venv` 日志、demo 输出、配置文件或历史会话里翻一个值填进 continue。翻到候选也必须先展示并得到用户确认。

## 四之二、超时与重试

| 接口 | 读超时 | 重试 |
| --- | --- | --- |
| `POST /v1/diagnosis/sessions`（创建会话） | **90s** | **不重试** |
| 其余接口 | 30s | 连不上 / 5xx 重试 1 次 |

创建会话要跑场景识别 + L2 实时查询 + 模型成文，读超时放宽到 90s。它不重试是因为**没有幂等键**：超时重发可能让服务端建出第二个会话，后续补槽会打到错误的 `sessionId` 上。超时后想取回上一次结论用 `GET /v1/diagnosis/sessions/{sessionId}`，不要重新创建。

## 五、脱敏：两道

- **第一道（提示词层）**：只把闭集槽位与用户原话摘要交给 CLI。工作区代码文件内容、`.env`、密钥文件、完整请求/响应报文一律不进自由文本字段。
- **第二道（代码层，兜底）**：CLI 分两档清洗，并输出 `redactedCount`（退出码仍为 `0`）：

| 位置 | 规则 |
| --- | --- |
| 自由文本（`initialMessage` / `message`） | 密钥类（PEM 块、`-----BEGIN`、>512 字符疑似 Base64 长串）**加** 个人信息类（卡号、身份证、手机号）→ `<redacted:type>`；另有 2000 字符上限 |
| 结构化 slot 值 | **只过密钥类规则** |

数字类规则带内容校验、不只看长度：卡号过 Luhn、身份证校验第 7~14 位的出生日期。原因是 YOP 订单号本身常是 16~19 位纯数字，只按长度判定会把订单号当卡号吃掉，**把查询条件毁掉**。slot 侧的控制手段是白名单 + 逐字段格式校验，不是数字正则。

清洗触发时 Skill 必须把清洗处数告知用户。提示词层的约束在长对话里会漂移，正则不会。

## 六、响应与状态

统一响应体 `{ code, message, data }`，成功 `code = "00000"`；**HTTP 状态一律 200**，业务成败只看 `code`。

`data` 主要字段：`sessionId`、`status`、`layer`、`knowledgeId`、`playbookId`、`slots`、`needInfos`、`nextQuestion`、`conclusion`（**一段文本**）、`evidence`、`excludedItems`、`unknownItems`、`relatedDocs`、`confidence`（0~1 数值）。

> **2026-09-08**：`status` / `layer` / `playbookId` 只返回**中文展示值**。客户端只认展示值；英文内部码（`NEED_INFO` / `L1` / `callback-missing`）视为未知 status，退出 `21`，不得自行映射后继续用。`playbookId` 示例：`回调未收到` / `验签失败` / `交易掉单` / `配置异常`。建单 `--scene` 传该展示值。

| `status` | Skill 处理 |
| --- | --- |
| `待补充信息` | 把 `needInfos` **问给用户**，一次性问全；用户给出或确认后再 continue。禁止用本机日志/工作区里翻到的值静默补槽 |
| `知识建议` | L1 建议：必须标注「未查询实时数据，不能作为生产根因」 |
| `已定位` | L2 已定位：按 D2 呈现；`evidence` 为空则降级按 `暂未定位` 呈现 |
| `暂未定位` | L2 已查证据但未定位：呈现结论并提示可提交工单 |
| `转人工` | 含查无调用单、无有效证据、轮次耗尽：不再追问、不再 `continue`，预览工单内容，用户确认后建正式工单 |
| `诊断中` | 结果未就绪，不是失败。立即 `get` 轮询（约 3 秒间隔，最多 10 次），不要向用户补槽或提单。超时仍为 `诊断中` → 降级 D1，可预览工单 |
| `已关闭` | 会话终态（≠ 转人工）。禁止 `continue`，不要自动建单。有 `conclusion` 则原样贴出；用户还要查 → `create` |

`layer` 展示值：`未进入排障` / `L1 知识建议` / `L2 实时证据排障`。

`needInfos` 元素：`{ slot, field, question, submitPath, submitMethod }`。**优先用结构化 `needInfos`，不要只解析 `nextQuestion` 文本**。

> 服务端有时把要问的信息**只放在 `nextQuestion` 文本里，`needInfos` 留空**（例如 `请补充以下信息：merchantNo：请提供商户号。`）。若严格只看 `needInfos`，Skill 会什么都不问、链路卡死。因此 CLI 在这种情况会给 `client_check=needinfos_empty_with_question` 提示：此时**可以**按该文本追问，但必须向用户标明这是文本解析、不是结构化补槽。结构化 `needInfos` 可用时回到结构化路径。

> **`conclusion` 自带固定标签**：原文通常已含「层级 / 现象 / 已排除 / 最可能原因 / 建议操作 / 未知项 / 文档 / 证据 / 置信度」。呈现时按原文标签拆段、标签加粗独占一行、正文原样另起一段；不要在 D2 外再套一层同名 `##`（会叠两层）。不要改写正文。

服务端有最大轮次上限，超过后返回 `转人工`——此时不要继续追问。

`evidence` 元素的字段**以服务端接口文档为准**：证据表按返回对象的实际键渲染，不硬编码列名、不为缺失字段补值、不丢弃未知字段——服务端加字段时客户端无需改动。

`conclusion` 同样以服务端为准：它是一整段文本、不带证据序号，无 `evidenceRefs`，因此「逐条追溯」退化为整体约束——`已定位` 必须有非空 `evidence`，否则按 `暂未定位` 呈现。正因为本地无从判断哪句话有证据支撑，**任何润色都可能把服务端没说的因果关系写实**，这条红线比结构化结论时更严。

## 六之二、会话边界与响应结构校验

### 何时起新会话

| 情形 | 动作 |
| --- | --- |
| 现象换了（回调没收到 → 验签失败；A 接口 → B 接口；入网通知 vs 交易通知） | `create`，起新会话 |
| **换了单号**（另一笔业务单号 / 通知订单号，不是纠正写错） | `create`，起新会话 |
| 上一个问题已收尾（商户说解决了 / 已建单转人工） | `create`，起新会话 |
| 换商户号、换应用 | `create`；**换应用还要换 token** |
| 换环境（沙箱 ↔ 生产） | **建议** `create` 起新会话。契约允许同一会话切环境（每轮显式传 `environment`）；漏传会沿用上一轮环境 |
| 上一会话返回 `转人工`（含轮次耗尽）或 `已关闭` 后仍要继续排查 | `create`，旧会话已终结 |
| 按 `needInfos` / `nextQuestion` 补槽位 | `continue --session <id>` |
| 同一现象补细节、纠正给错的值、对同一结论追问 | `continue --session <id>` |

契约明确：`sessionId` 不跨用户、跨 appKey 复用。同一会话切环境契约允许，但仍建议起新会话以免槽位与证据混在两个环境里。拿不准是不是新问题时问商户一句，比默认沿用旧会话安全；起新会话后要把新的 `sessionId` 告知商户，否则上文里的旧会话号会造成混淆。

### 客户端结构校验（`transport.check_session_data`）

服务端结论不改写，但**要确认它自洽**——数据自相矛盾时按较弱的一方呈现，不能照单全收。

硬失败（退出 `21`，不呈现任何结论）：

| 检查 | 理由 |
| --- | --- |
| `data` 不是对象 / 缺 `status` / `status` 不在枚举内 | 没法判断该怎么呈现 |
| 响应 `sessionId` 与请求的 `--session` 不一致 | **可能是别人的会话与证据**，属安全问题，直接拒收 |

其余写 stderr（`client_check=<key>`），由 Skill 按 `SKILL.md` 的降级表处理：

| key | 检查 |
| --- | --- |
| `located_without_evidence` | `已定位` 但 `evidence` 为空 → 按 `暂未定位` 呈现 |
| `knowledge_with_evidence` | `知识建议` 层出现证据 |
| `layer_status_mismatch` | `已定位`/`暂未定位` 应为 `L2 实时证据排障`、`知识建议` 应为 `L1 知识建议` |
| `empty_conclusion` | `知识建议`/`已定位`/`暂未定位` 但 `conclusion` 为空 |
| `bad_confidence` | `confidence` 非数值或不在 0~1 |
| `bad_<field>_type` | `evidence` / `needInfos` / `excludedItems` / `unknownItems` / `relatedDocs` 不是数组 |
| `missing_session_id` | 响应无 `sessionId`，后续无处补槽 |
| `need_info_without_needinfos` | `待补充信息` 但没说要问什么 |
| `needinfos_empty_with_question` | 只有 `nextQuestion` 文本 |
| `status_diagnosing` | `诊断中`：立即 `get` 轮询，不补槽不提单 |
| `status_closed` | `已关闭`：禁止 continue，不自动建单 |

**校验只判自洽，不判对错**：不核对 `conclusion` 的内容、不比对证据是否支持结论——那是服务端的职责，客户端无从判断，也不允许判断（结论不可改写红线）。

## 六之三、公开知识库（匿名）

`GET /yop-agent/v1/knowledge/summaries`（列全部摘要）与 `GET /yop-agent/v1/knowledge/{knowledgeId}`（条目详情）**不鉴权、不需要凭证、不需要 sessionId**。详情字段：`id`、`version`、`summary`、`symptom`、`likelyCause`、`checkSteps`、`solution`。

三条边界：

1. **拿到的一律是 L1。** 内容由平台文档派生，不是该商户的实时数据。查到公开条目**不等于**查过平台，呈现照旧用 D1 模板加徽标。
2. **没有搜索端点。** 只能「列全部 + 按 id 取详情」，所以 `diag_knowledge.py search` 是把摘要拉回本机再按关键词过滤——**用户的问题描述不外发**。无凭证态可以放心用。
3. **`knowledgeId` 与会话响应同一命名空间**（`kn-docs-<hash>`）。本地 `knowledge-map.yaml` 的 `knowledgeId` 可用下列命令核对：

```bash
python scripts/diag/diag_knowledge.py verify-map
```

`knowledgeId` 查不到对应条目时**留空**，不得自造。本地 `knowledge-map.yaml` 只填公开目录里真实存在的标识。

## 六之四、工单附件

`POST /yop-agent/v1/support-ticket/tickets/{ticketId}/attachments`，`multipart/form-data`：文本字段 `sessionId`（必填，服务端用它校验会话与工单归属，防跨会话上传）+ 文件字段 `file`。响应含 `id`、`fileName`、`contentType`、`size`、`checksum`、`scanStatus`。

限额与限流（服务端校验，客户端只本地预拦单文件大小）：

| 项 | 值 | 超限表现 |
| --- | --- | --- |
| 单文件 | 10MB | `code=YOP-AGTA0413` → 退出 `2` |
| 单次 multipart 请求 | 12MB | 同上 |
| 每单附件数 | 10 个（服务端校验） | 由服务端拒绝 |
| 上传频率 | 10/分钟、100/天 | **HTTP 429** → 退出 `14` |

服务端会做敏感信息扫描，命中即拒；上传失败**不回滚已建工单**；不支持经 yop-agent 删除或下载附件——**传错了没有回退手段**，这正是上传前必须让用户确认的原因。

**附件是唯一能绕过两道脱敏的通道**——自由文本与槽位都会被清洗，二进制文件原样出境。所以客户端在上传前本地体检（`redact.scan_attachment`），并分两档：

| 结果 | 处理 |
| --- | --- |
| 命中私钥特征（`.pem`/`.key`/`.p12`/`.jks`/`.env`/`credentials.json`/`yop_sdk_config*.json`，或 PEM 私钥块） | **拒传**，退出 `2`；私钥没有脱敏后还能用的版本 |
| 公钥证书、超长 Base64 串、个人信息特征 | 只提醒（`attachment_check：…`），交用户决定 |

第二档刻意不拒：商户排查回调解密/验签失败时要传的恰恰是含密文报文的日志，一律拦掉等于把功能废掉。上传与建单同纪律：默认只预览（打印文件名、字节数、SHA-256 与体检结果），**用户明确同意后才加 `--confirm`**。

## 七、错误码与退出码

服务端用粗粒度 code + message 区分具体原因。客户端两层处理：先按 code，认证类通用码再按 message 关键词细分；文档口径的 `AUTH_*` / `CREDENTIAL_*` 与现行粗粒度码都收下。

错误码：

| code | 含义 | message 示例 |
| --- | --- | --- |
| `YOP-AGTA1401` | 缺少 Authorization Bearer | `缺少 Authorization Bearer` |
| `YOP-AGTA1402` | 认证类通用码 | `应用签名校验失败` / `token 不存在` / `appKey、environment 或 signature 为空` / `environment 仅支持 SANDBOX/PRODUCT` |
| `WEBB0500` | 框架级异常（如路径不存在） | `internal-server-error(NT)` |

归一化后的退出码：

| 情况 | 退出码 | Skill 行为 |
| --- | --- | --- |
| 本地校验失败（时间窗、缺参等），未发起请求；`YOP-AGTA1402` + `为空` / `仅支持` | `2` | 修正输入后重试 |
| 本地无 token；`YOP-AGTA1401`；`AUTH_MISSING` | `10` | 离线 L1 + 一次性告知可兑换 |
| 私钥读取失败、密钥类型不识别；`YOP-AGTA1402` + `签名校验失败`（**及未收录的 message，兜底走这里**）；`AUTH_INVALID` | `11` | 停止，核对私钥路径与密钥类型，不重试、不改用其他密钥 |
| 本地 token 过期；`YOP-AGTA1402` + `token 不存在` / `已过期` / `已吊销` / `未找到`；`AUTH_EXPIRED` / `AUTH_REVOKED` | `12` | 离线 L1 + 提示重新兑换 |
| `YOP-AGTA1402` + `租户` / `不一致` / `覆盖`；`APP_OVERRIDE_DENIED` / `TENANT_MISMATCH` | `13` | 停止，不重试、不换参数再试 |
| `YOP-AGTA0413`（附件超限：单文件 10MB、单请求 12MB） | `2` | 压缩、拆分或改传片段后重试 |
| 提单限流：顶层 `code=YOP-AGTA0429`（旧口径 `data.errorCode=YOP-AGT10429` 仍收下）；附件限流：**HTTP 429** | `14` | 如实告知配额，稍后再试，不反复重试 |
| 限流：`RATE_LIMITED` / `LIMIT_EXCEEDED` / `TOO_MANY_REQUESTS`（客户端全部收下） | `14` | 告知配额与恢复时间，转离线 L1 |
| `YOP-AGTA1402` + `已存在` / `已有有效`；`CREDENTIAL_EXISTS` | `15` | 提示复用本地条目或由用户确认后先 `--revoke`，**不自动吊销** |
| 超时 / 连不上 / `WEBB0500` | `20` | 离线 L1 + 预览工单内容 |
| 响应结构非法、code 未收录 | `21` | 丢弃响应，不呈现任何结论，转工单 |

`YOP-AGTA1402` 未收录的 message 兜到 `11`（停止、不重试）而不是 `21`：它确实是认证失败，按认证问题处理比当成结构异常转工单更贴近实情；服务端原始 message 会写到 stderr，Skill 可原样告知用户。

`CREDENTIAL_NOT_FOUND`（吊销时未找到）视为已吊销：删除本地条目并正常结束。

结构异常不改变退出码，CLI 只在 stderr 给 `client_check=...` 提示（如 `located_without_evidence`），**降级呈现由 Skill 执行**。

统一原则：**远端不可用 = 降级到弱结论，不是降级到猜**。任何情况下都不能用本地推测冒充平台事实。

## 八、工单

`POST /v1/support-ticket/tickets` —— **直接创建正式工单**，不是草稿。

请求：`sessionId`（必填，服务端固定用它作 `businessKey`）、`merchantNo`（必填）、`scene`（可选，传会话返回的 `playbookId` **展示值**如 `回调未收到`；不传回退到会话命中的场景，再没有用 `__DIRECT__`）、`title`（一句话现象，**不要拼整段诊断**）、`priority`（`LOW`/`NORMAL`/`HIGH`/`URGENT`）、`routingContext`（可选，建议带行业线）。

响应：`{created, duplicated, ticketId, ticketNo, status, playbookId, message}`。

纪律：

- **不静默建单**。`diag_ticket.py` 默认 `--dry-run` 只打印将提交的内容；**必须**把它完整展示给用户，用户明确同意（如「提交吧」「确认提单」）后才加 `--confirm` 真建。仅「还是没解决」不构成同意。
- 服务端按「一天内同 `playbookId` 不重复；一天内已有直接建单（`playbookId` 空，归一为 `__DIRECT__`）也不重复」去重；命中时返回已有 `ticketNo` 且 `duplicated=true`，Skill 应如实告知用户「命中去重，复用已有工单」而不是说「已新建」。
- 可信身份字段（`queue` / `source` / `sourceSystem` / `tenantId` / `actor` / `businessKey`）**一律由服务端覆盖**，客户端不得伪造，CLI 会剔除。
- `merchantNo` 仍只能用用户提供或服务端点名的值。
- **远端不可用时**（退出码 `20`）用 `diag_ticket.py --offline` 把本地现象与已收集槽位拼成工单内容供用户自行提交，输出必须显式标注「未经平台生成、不含平台实时事实」。

**提单限流：3/分钟、20/天。** 超限时 HTTP 仍是 200、顶层 `code=YOP-AGTA0429`（`message=提单频率超限，限制为 3/分钟、20/天`，`data=null`）。兼容旧响应把失败放在 `data.errorCode=YOP-AGT10429`（顶层仍 00000）；`unwrap` 认顶层新码，`_check_ticket_result` 兜住旧口径，都映射到退出码 `14`。

首次建单 `created=true`；同 session 再次提交若 `duplicated=true` 且返回同一 `ticketNo`，如实告知「复用已有工单」。

## 九、回调未收到场景的典型链路

1. 首轮只给 `initialMessage` → 服务端识别场景 `回调未收到`，通常先要 `merchantNo`；
2. 补 `merchantNo` + 时间 → 服务端查通知链路；有数据则以通知订单/记录/发送记录为证据出结论；
3. 通知链路无数据且无 `requestId` → 服务端要 `requestId`；用户给不出就直接转工单；
4. 给了 `requestId` → 服务端查 invoke 日志与详情，命中错误码时自动补查方案；
5. 全程无有效业务数据 → `转人工`。

`requestId` 与通知记录没有强关联，只用于「为什么没有产生通知」的辅助分析。
