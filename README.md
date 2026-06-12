# 易宝支付接入技能

> 当前版本以 `SKILL.md` frontmatter 的 `version` 为唯一来源；变更历史见 `CHANGELOG.md`。

面向 Agent 的易宝支付（Yeepay）接入与联调排障技能。覆盖**收单 / 退款 / 分账 / 出款 / 对账**全业务域，
内置签名验签、回调验签、幂等重试、查单纪律，并提供产品决策、场景流程、工具脚本与代码示例。

## 设计原则

- **单一入口**：唯一 `SKILL.md` 负责路由与纪律，不再有多个子技能 `SKILL.md`。
- **API 走在线**：接口字段/错误码不内置静态文档，统一由 `references/产品能力/api-index.yaml`
  维护 `doc_md` 在线文档链接，Agent 按「文档加载协议」用 `curl` 实时拉取，保证字段永远最新。
- **产品能力维度组织**：业务文档按「产品能力 / 业务域 / 场景」展开，每个场景一个 md，
  只写流程、易错点与引用（API 走 catalog、代码走示例代码、规则走平台文档）。
- **平台文档本地权威**：签名、加密、回调机制、接入准备、错误码等稳定规则本地保留，不走 curl。

## 目录结构

```text
yeepay-pay-skill-v0.4/
├── README.md                         本文件
├── LICENSE.md
├── SKILL.md                          唯一入口：路由 + 纪律 + 文档加载协议
├── scripts/                          Python 工具
│   ├── gen_keypair.py                生成密钥对（RSA/SM2）
│   ├── query_order.py                查单
│   ├── refund.py                     退款
│   └── mock_notify.py                本地模拟发结果通知
└── references/
    ├── 平台文档/                      本地权威（接入准备/安全认证/平台规范/工具与支持/错误码）
    │   └── 平台规范/安全认证/          含 请求签名协议.md、回调解密协议.md（不使用 SDK 时实现参考）
    ├── 产品能力/
    │   ├── 产品决策.md                方案与支付方式选型决策
    │   ├── api-index.yaml            所有 API 的 curl 清单
    │   ├── 收单/                      8 个支付场景（含前端示例代码）
    │   ├── 退款/退款.md
    │   ├── 分账/                      订单分账 / 余额分账
    │   ├── 出款/                      结算 / 提现
    │   └── 对账/                      交易 / 分账 / 资金 / 结算对账
    └── troubleshooting.md            各业务域排障汇总
```

## 接口数据源（实测确认）

接口规格由开放平台「在线 markdown 文档」提供，产品无关，可直接 `curl`：

| 用途 | URL 模板 |
|------|----------|
| 接口在线文档（基本信息/请求参数/请求示例/响应参数/响应示例/错误码/示例代码，单文件全含） | `https://open.yeepay.com/docs-v3/api/<slug>.md` |
| 结果通知（SPI）文档 | `https://open.yeepay.com/docs-v3/notify/<spi>.md` |

> slug 规则：`<method小写>_<path去掉开头/，/ 换 _>`（保留 `.` 与 `-`）。
> 例：`POST /rest/v2.0/aggpay/wechat-config/add` → `post_rest_v2.0_aggpay_wechat-config_add`。
> 例外：个别接口（如 yos 账单下载类）前缀为 `options_`，以 `api-index.yaml` 中实测的 `doc_md` 为准。
>
> 人类页 `https://open.yeepay.com/docs/products/<product>/api/<uri>` 是 SPA，curl 取不到字段，仅作链接。

## 使用约定

- 任何 API 字段实现前必须走 `curl`，不得凭记忆编造字段。
- `scripts/` 仅用于联调与本地验证，不用于生产出款/交易。
- 上线前对照 `references/troubleshooting.md` 的上线检查清单逐项确认。

## 版本管理与更新机制

### 版本号（语义化）

唯一版本来源为 `SKILL.md` frontmatter 的 `version`；`api-index.yaml`、`platform-doc-manifest.yaml` 的 `version` 字段发版时同步（由 `validate_docs.py` 强制一致）。

| 位 | 何时递增 | 示例 |
|----|----------|------|
| MAJOR | 面客纪律/路由/目录结构等不兼容调整 | 重写交互纪律 |
| MINOR | 新增场景/接口/脚本/协议文档 | 新增一个支付场景 md |
| PATCH | 文档勘误、措辞修订、错误码补充 | 修正易错点描述 |

### 变更触发器与责任分区

| 变更来源 | 改哪里 | 不要改哪里 |
|----------|--------|------------|
| 平台接口新增/变更 | `references/产品能力/api-index.yaml`（doc_md / api_id / path） | 不在场景 md 内置字段表 |
| 平台规范变更（签名/回调/密钥） | `references/平台文档/`，协议变更同步 `scripts/` 与测试向量 | — |
| 产品流程/易错点变更 | `references/产品能力/<域>/<场景>.md` | — |
| 协议实现变更 | `scripts/` + `scripts/verify_vectors.py --regen` 重算向量 + 同步协议文档「完整示例」 | — |

### 发版流程

1. 完成变更，按上表归位。
2. 跑守门：`cd scripts && python validate_docs.py --with-notify-test`（含死链/过期模式/版本一致/测试向量校验）。
3. 提升 `SKILL.md` 的 `version`，同步两个 yaml 的 `version`。
4. 在 `CHANGELOG.md` 顶部追加条目（版本、日期、变更要点、责任人）。
