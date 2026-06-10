---
name: yeepay-pay-skill
description: >-
  易宝支付（Yeepay）接入与联调排障技能。覆盖收单、退款、分账、出款、对账与运维上线；
  内置签名验签、回调验签、幂等重试与查单纪律。接口字段以开放平台在线文档为准（通过 curl 实时拉取），
  本技能提供路由、纪律、产品决策、场景流程、易错点、工具脚本与代码示例。用户提到易宝/yeepay/
  支付下单/小程序支付/APP支付/主扫/被扫/验签/回调/查单/退款/分账/结算/提现/对账/上线检查时使用。
disable-model-invocation: true
version: 0.4.1
---

# 易宝支付接入技能（统一入口）

本技能是**唯一入口**：按业务域路由、约束接入纪律、提供产品决策、场景流程、易错点、工具脚本与代码示例。
**接口字段/错误码不内置静态文档**，统一通过 `curl` 从开放平台在线文档实时获取（见「文档加载协议」）。

## 通用纪律（所有任务都遵守）

- 写操作（支付、退款、分账、提现等）前确认：环境（沙箱/生产）、商户号、AppKey、notifyUrl 来源。
- 交易终态 = **回调 + 查单** 双通道确认，不以前端页面为准。
- 写操作使用业务唯一单号；回调处理必须幂等；超时/未知先查状态再决定是否重试。
- 错误码两层：先看接口自身业务码，再看平台通用码（见 `references/平台文档/开始对接/平台错误码说明.md`）。
- 禁止输出私钥、完整密钥、完整卡号/证件号。

## 强制执行顺序

1. 读 `references/平台文档/` 中与任务相关的规则（签名/加密/回调/接入准备）。
2. 用户在「选什么方案」上犹豫时，先读 `references/产品能力/产品决策.md`。
3. 在 `references/产品能力/<业务域>/<场景>.md` 选择目标场景，确认流程与易错点。
4. 在 `references/产品能力/api-index.yaml` 按域+场景定位接口的 `doc_md` 链接。
5. **生成或核对接口字段/错误码前，必须执行文档加载协议（curl）。**
6. 需要本地验证/工具时，使用 `scripts/` 下的 Python 工具。
7. 按「标准输出模板」回复。

## 文档加载协议（API 类任务，核心）

接口规格统一从「开放平台在线 markdown 文档」实时 curl 获取（已实测可用，产品无关）：

```text
1. 在 references/产品能力/api-index.yaml 按域+场景定位目标接口，取其 doc_md 链接。
2. 拉取接口在线文档（基本信息/请求参数/请求示例/响应参数/响应示例/错误码/示例代码，单文件全含）：
   curl -sS "https://open.yeepay.com/docs-v3/api/<slug>.md"
   slug 规则：<method小写>_<path去掉开头/，/ 换 _>（保留 . 与 -）
   例：POST /rest/v2.0/aggpay/wechat-config/add -> post_rest_v2.0_aggpay_wechat-config_add
   例外：个别接口（如 yos 账单下载类）前缀为 options_；优先用 api-index.yaml 中已实测的 doc_md，
   自行推导遇 403/404 时再试 options_ 前缀。
3. 涉及回调时，拉结果通知文档：
   curl -sS "https://open.yeepay.com/docs-v3/notify/<notify_spi>.md"
4. 场景 md 只提供流程、易错点、引用；禁止仅凭它拼接口参数。
5. curl 失败时：提示用户检查网络；不得凭记忆编造字段；停止字段级实现。
6. 回复中注明 doc_md「基本信息」中的 API ID 与「最后更新时间」。
```

> doc_md 章节结构：`基本信息`（API ID/请求路径/请求方法/安全需求/最后更新时间）、
> `请求参数`、`请求示例`、`响应参数`、`响应示例`、`错误码`、`示例代码`。
> 错误码已含在 doc_md 内，无需单独拉取。
>
> 人类可读页 `https://open.yeepay.com/docs/products/<product>/api/<uri>` 为 SPA，
> **curl 取不到字段**，只可作给用户看的链接。

> `references/平台文档/`（签名验签、加密机制、回调机制、接入准备、错误码）为本地权威内容，**不走 curl**。

## 业务域路由

| 用户意图（关键词） | 场景目录 | catalog 分组 |
|--------------------|----------|--------------|
| 下单/小程序/APP/H5/主扫/被扫/查单 | `references/产品能力/收单/` | `acquiring` |
| 退款/退款查询 | `references/产品能力/退款/退款.md` | `refund` |
| 分账/分账查询/资金归还 | `references/产品能力/分账/` | `profit-sharing` |
| 结算/提现/提现卡 | `references/产品能力/出款/` | `payout` |
| 对账/账单下载/差异处理 | `references/产品能力/对账/` | `reconciliation` |
| 验签失败/回调收不到/上线检查 | `references/troubleshooting.md` + `references/平台文档/` | （本地，无 curl） |

## 收单场景索引

| 场景 | 场景文件 |
|------|----------|
| 浏览器 H5 支付 | `references/产品能力/收单/浏览器H5支付.md` |
| 小程序支付 | `references/产品能力/收单/小程序支付.md` |
| APP 支付（使用易宝小程序） | `references/产品能力/收单/APP支付（使用易宝小程序）.md` |
| APP 支付（使用客户小程序） | `references/产品能力/收单/APP支付（使用客户小程序）.md` |
| 微信内 H5+公众号支付 | `references/产品能力/收单/微信内H5+公众号支付.md` |
| 被扫支付 | `references/产品能力/收单/被扫支付.md` |
| 主扫支付（独立码-线上PC） | `references/产品能力/收单/主扫支付（独立码-线上PC）.md` |
| 主扫支付（聚合码） | `references/产品能力/收单/主扫支付（聚合码）.md` |

## 工具脚本（本地，Python）

| 用途 | 脚本 |
|------|------|
| 生成密钥对（RSA/SM2） | `scripts/gen_keypair.py` |
| 查单 | `scripts/query_order.py` |
| 退款 | `scripts/refund.py` |
| 本地模拟发结果通知 | `scripts/mock_notify.py` |

> 脚本仅用于联调与本地验证；生产请走商户自有系统。使用前阅读 `scripts/README.md`。

## 标准输出模板

### A. 接入方案
```markdown
## 场景
## 必读规则（平台文档）
## 接口（含 API ID 与最后更新时间）
## 实现步骤
## 风险与约束（幂等/回调/查单）
## 待确认（环境/支付方式/参数来源）
```

### B. 排障结论
```markdown
## 现象
## 已排除
## 最可能原因（按优先级）
## 建议操作（先查后重试）
## 需补充的信息
```

## 目录说明

```text
SKILL.md                       本文件，唯一入口
scripts/                       Python 工具：密钥/查单/退款/模拟回调
references/
  平台文档/                    本地权威：接入准备/安全认证/平台规范/工具与支持/错误码
  产品能力/
    产品决策.md                方案与支付方式选型决策
    api-index.yaml             所有 API 的 curl 清单（doc_md / path / method / api_id）
    收单/ 退款/ 分账/ 出款/ 对账/   各业务域场景文档（流程+易错点+引用，不含接口静态文档）
  示例代码/                    加验签/加解密/接收回调/前端示例（占位，按需补充）
  troubleshooting.md           各业务域排障汇总
```
