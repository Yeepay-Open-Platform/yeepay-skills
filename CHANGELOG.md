# 变更历史

版本规则与发版流程见 `README.md`「版本管理与更新机制」。最新条目置顶，首条版本号须与 `SKILL.md` frontmatter 一致（`validate_docs.py` 校验）。

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
