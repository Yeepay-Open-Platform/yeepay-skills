# 变更历史

版本规则与发版流程见 `README.md`「版本管理与更新机制」。最新条目置顶，首条版本号须与 `SKILL.md` frontmatter 一致（`validate_docs.py` 校验）。

## 0.6.22 - 2026-06-23

出站签名与 HTTP 报文编码规范化（不含文件上传/下载，后续支持）：

- 新增 `common/url_encoding.py`：签名一次编码（空格 `%20`）与 HTTP 报文二次编码（`http_form_body` / `http_query_string`）
- 新增 `common/yop_content_type.py`、`common/yop_http.py`：Content-Type 规范传递；GET/POST Form 统一 `application/x-www-form-urlencoded;charset=UTF-8`，**不参与签名**
- `rsa/client.py`、`sm/client.py` 对齐上述规则；测试向量与 `请求签名协议.md` 同步更新

## 0.6.21 - 2026-06-22

出站请求补充 SDK 标准头：

- 新增 `common/yop_headers.py`：`x-yop-sdk-version` 固定 `4.0.0`，`x-yop-sdk-langs`，`x-yop-session-id` 进程启动时生成、运行期间不变，`User-Agent` 第二段为 Python 运行时版本
- `rsa/client.py`、`sm/client.py` 签名后自动附带标准头，避免网关返回旧版响应格式
- `请求签名协议.md` 补充 SDK 标准头说明

## 0.6.18 - 2026-06-22

小程序支付补充支付宝小程序接入：

- `产品能力/收单/小程序支付.md`：开通产品表新增支付宝线上/线下产品码；接入步骤补充支付宝 authCode 换取 userId 与唤起收银台参考链接；前端示例新增支付宝授权码获取与 `my.tradePay` 唤起示例。

## 0.6.17 - 2026-06-16

脚本目录归类：

- `common/response_verify.py`：跨 RSA/SM2 应答验签库
- `tools/verify_vectors.py`、`tools/verify_response.py`：跨算法 CLI
- 根目录仅保留 `validate_docs.py` 发版入口

## 0.6.16 - 2026-06-16

环境变量命名调整（不保留旧名）：

- `YOP_YOP_PUBLIC_KEY` → `YOP_PLATFORM_PUBLIC_KEY`
- `YOP_YOP_PRIVATE_KEY` → `YOP_PLATFORM_PRIVATE_KEY`

## 0.6.15 - 2026-06-16

API 应答验签：

- 新增应答验签模块（RSA SHA256 / SM2 SM3，与 Java SDK 对齐）及 CLI `tools/verify_response.py`。
- `rsa/client.py`、`sm/client.py` 支持 `call(..., verify=True)`；`query_order.py` 支持 `--verify`。
- `请求签名协议.md` 补充应答验签章节；新增应答验签测试向量。

## 0.6.14 - 2026-06-16

平台商密证书文档合并与归位：

- 将密钥管理下两篇平台商密证书文档合并为 `平台规范/安全认证/平台商密证书.md`。
- 更新 manifest、密钥管理交叉引用及 `报文加密机制(SM).md` 内链。

## 0.6.13 - 2026-06-16

平台商密证书文档与查询脚本：

- 新增平台商密证书文档（整理自在线文档 3862 / 2479；0.6.14 起合并为 `平台规范/安全认证/平台商密证书.md`）。
- 新增 `scripts/sm/list_platform_certs.py`：SM2 鉴权调用 `GET /rest/v2.0/yop/platform/certs`，表格展示序列号与有效期，支持 `--save-dir` 落盘 PEM 并导出公钥。
- 更新 manifest、密钥管理交叉引用及 SKILL 工具表。

## 0.6.12 - 2026-06-16

SM2 密钥输出格式与 RSA 对齐：

- `sm/gen_keypair.py` 改为输出 `sm2_private_pkcs8.pem` / `sm2_public.pem`（PKCS8/SPKI PEM），不再生成 hex 文件。
- `sm/crypto.py` 新增 PEM 导出；`load_sm2_*` 仅接受 PKCS8/SPKI PEM（文件或 PEM 文本）。
- SM2 测试向量密钥文件由 `.hex` 转为 `.pem`（密钥材料不变）。

## 0.6.11 - 2026-06-16

RSA 脚本目录重组：

- 将 RSA 相关脚本迁入 `scripts/rsa/`，与 `scripts/sm/` 对称；RSA 测试向量迁至 `scripts/rsa/tests/vectors/`。
- 根目录仅保留 `validate_docs.py`、`verify_vectors.py` 等公共守门脚本。
- 更新 `scripts/README.md`、`scripts/rsa/README.md`、SKILL 工具表及协议文档路径引用。

## 0.6.10 - 2026-06-16

国密脚本目录重组：

- 将 SM2 相关脚本迁入 `scripts/sm/`，与 RSA 根目录脚本分离；SM2 测试向量迁至 `scripts/sm/tests/vectors/`。
- 根目录 `gen_keypair.py` 仅保留 RSA；SM2 使用 `sm/gen_keypair.py`。
- 更新 `scripts/README.md`、`scripts/sm/README.md`、SKILL 工具表及 `密钥介绍.md` 路径引用。

## 0.6.9 - 2026-06-22

SM2 全链路脚本与 RSA 互打测试修复：

- 新增 `sm2_crypto.py`、`yop_client_sm.py`、`notify_crypto_sm.py`、`mock_notify_sm.py`、`decrypt_notify_sm.py`。
- 新增 SM2 测试向量：`sign_sm_vectors.json`、`notify_sm_vector.json` 及对应 hex 密钥。
- `validate_docs.py`：`run_notify_roundtrip` 改为易宝/商户双钥互打；新增 SM2 互打测试。
- `回调解密协议.md`：同步 RSA 向量密文（encKey 段随 PKCS1 随机填充变化）。

## 0.6.8 - 2026-06-22

SM2 密钥生成修复：

- `scripts/gen_keypair.py`：改用 gmssl `CryptSM2.default_ecc_table`（SM2P256V1）生成标准 SM2 密钥对，移除错误的 SECP256K1 占位实现；生成后签名自检。
- `scripts/README.md`、`密钥介绍.md`：补充 SM2 输出格式、CFCA 与脚本能力边界说明。

## 0.6.7 - 2026-06-12

产品决策澄清模板微调：

- 模板 1：浏览器 H5 明确为唤起微信小程序/支付宝 APP。
- 模板 2：APP 支付推荐改为商家自有小程序方案。
- 模板 6：提现说明补充余额分账资金场景。

## 0.6.6 - 2026-06-12

产品决策文档精简：

- `产品决策.md`：移除 RSA/国密选型与环境上线节（归平台文档与 troubleshooting）；重排章节编号；表格与澄清模板格式整理。

## 0.6.5 - 2026-06-12

prePayTn 唤起方式速查落地：

- 新增 `产品能力/收单/prePayTn唤起方式速查.md`：聚合统一下单 `payWay + channel + scene` → 返回类型与前端唤起方式速查表。
- `SKILL.md` 收单场景索引新增跨场景速查条目；6 个收单场景 md 与 `troubleshooting.md` 交叉引用。
- `api-index.yaml`：`prepay-tn-usage` 标注本地权威路径。

## 0.6.4 - 2026-06-12

审核缺口修复与回调 SPI 兜底策略：

- `SKILL.md` 文档加载协议：回调实现 MUST 先 curl 接口 doc_md，从「结果通知」节取通知编码与 notify 文档 URL；api-index 的 `notify_spi` 仅为索引提示，与 doc_md 不一致或缺失时以 doc_md 为准。
- `api-index.yaml`：新增 `withdraw-card-bind`（提现卡添加）；修正提现回调 SPI 为 `account.business.withdraw-result`；删除未核对的 `platform-error-codes` 在线条目（平台码走本地 `平台错误码说明.md`）。
- `提现.md`：绑卡接口纳入 catalog 表与流程第一步；回调说明改为 doc_md 权威。
- `订单分账.md`：新增「分账接收方准备」节，交叉引用入账方申请流程（`mer-receiver-apply` / `余额分账.md`）。
- `退款.md`：回调说明改为 doc_md 权威。
- `快速接入.md`：移除「上线前检查清单尚未落地」过时措辞。

## 0.6.3 - 2026-06-12

技术执行顺序重排（修正步骤依赖关系，读取范围可判定）：

- `SKILL.md`「技术执行顺序」按依赖链重排：核对产品前提（方案/收款主体/场景流程）→ 锁定 SDK 路径（L1/L2/L3）→ 按路径与任务类型读平台文档 → 定位接口与 curl doc_md → 生成代码 → 本地验证 → 输出。原第 1 步"读相关规则"与第 2 步"选路径"存在循环依赖（读哪些文档取决于路径选择），现已调正。
- 第 1 步明确为"核对前提"而非决策：核对不通过退回面客纪律①②，与章节前提「商户已确认场景」保持一致。
- 读平台文档步骤挂载 `platform-doc-manifest.yaml` 作为导航索引，并新增「任务特征 → 必读文档」映射表（L1/L2/L2'、出款 CFCA、回调、排障），收敛原本散落在「通用技术纪律」与「写代码任务路由」中的隐式必读规则。
- 新增显式步骤"依据 doc_md 与所选路径生成代码/参数表"，代码生成不再隐含于拉文档与输出之间。

## 0.6.2 - 2026-06-12

资金出款类接口 CFCA 证书强约束（遗留问题落地，范围按接口分组界定）：

- `接入准备/密钥管理/CFCA证书介绍.md` 新增「资金出款类接口必须使用 CFCA 证书（强约束）」节：明确 **`account`（账户，`/rest/v1.0/account/...`，如提现下单）与 `balance`（代付代发，`/rest/v1.0/balance/...`，如 transfer_send）分组**必须用证书签名，仅配普通 RSA 文本密钥调用会被拒绝报错；`settle` 分组（结算）不在强制范围；关联证书制备、密钥配置（证书格式）与 IP 白名单。
- `密钥介绍.md` 两处"高风险接口"措辞改为按 account/balance 分组明确点名并指向 `CFCA证书介绍.md`。
- `提现.md` 顶部新增前置条件提示（account 分组须 CFCA 证书 + IP 白名单）；`结算.md` 注明 settle 分组不在强制范围、避免误判。
- `troubleshooting.md` §五 新增排障首条：account/balance 分组接口被拒/签名权限类报错先核对是否使用 CFCA 证书。
- `SKILL.md` 通用技术纪律新增一条对应纪律；manifest 为 `CFCA证书介绍.md` 补充 topics/related。

## 0.6.1 - 2026-06-12

外链与措辞修订：

- 控制台入口统一为 `https://open.yeepay.com/developer-center`（替换旧商户后台登录页与 home?redirect 变体，共 12 处：密钥配置 RSA/SM、CFCA证书制备、密钥工具）。
- Maven Central 链接更新为新版 `central.sonatype.com/artifact/...`（SDK使用说明、平台SDK）。
- 平台错误码说明标注【新版】错误码。

## 0.6.0 - 2026-06-12

评审会落地（后端协议归位 / 前端示例进产品文档 / 测试向量 / 版本机制）：

- 后端协议文档 `请求签名协议.md`、`回调解密协议.md` 由 `references/示例代码/后端代码/` 迁入 `references/平台文档/平台规范/安全认证/`，纳入 manifest 索引与文档质量守门。
- 前端示例代码全部内联到对应产品场景 md（小程序支付 / 微信内H5+公众号支付 / 浏览器H5支付 / APP支付），删除 `references/示例代码/` 目录，全局引用同步更新。
- 新增加验签/回调解密**固定测试向量**（`scripts/tests/vectors/`）：固定测试密钥 + GET/POST Form/POST JSON 三个签名用例 + 固定四段密文回调用例；协议文档补「完整示例」节，可逐字节比对。
- 新增 `scripts/verify_vectors.py`：校验测试向量与脚本实现一致，支持 `--regen` 重算。
- `validate_docs.py` 升级为发版守门：扫描范围扩大到全部 md，新增相对引用死链检查、过期模式黑名单（definition.json/errcode.json/示例代码 旧路径）、版本一致性检查、测试向量与文档一致性检查。
- 修复 13 个产品场景 md 仍指向旧数据源 `apis/docs/apis/<api_id>/definition.json`、`errcode.json` 的问题，统一为 doc_md 协议。
- 版本号统一以 `SKILL.md` 为单一来源（0.6.0），README 标题去版本号，新增本 CHANGELOG 与「版本管理与更新机制」说明。

## 0.5.1 及更早

- 0.5.x：面客交互纪律（四步）、写代码任务路由（SDK/L1/L2/L3）、标准输出模板。
- 0.4.x：业务文档展开为 `产品能力/<域>/<场景>.md`（收单 8 场景）；新增 `产品决策.md`、`scripts/` 工具、`api-index.yaml`；平台文档全量本地化。
- 0.3-draft：初版草稿（domains 单文件结构）。
