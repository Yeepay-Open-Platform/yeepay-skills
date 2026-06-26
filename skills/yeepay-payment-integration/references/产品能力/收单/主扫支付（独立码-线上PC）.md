# 主扫支付（微信/支付宝独立码，线上 PC 场景）

**用户扫商户**展示的二维码完成支付；每个渠道一个独立码（微信码 / 支付宝码分开），典型用于线上 PC 收银台。

> 接口字段以在线文档为准：按下表 catalog id 在 `../api-index.yaml` 取其 `doc_md`，执行
> `curl -sS "<doc_md>"` 后再实现（单文件含字段/示例/错误码/示例代码）。

## 场景 → 接口

| 用途 | catalog id | 方法 | 路径 |
|------|-----------|------|------|
| 下单 | `aggpay-pre-pay` | POST | `/rest/v1.0/aggpay/pre-pay` |
| 查单 | `trade-order-query` | GET | `/rest/v1.0/trade/order/query` |
| 公众号配置（微信，条件必读） | `aggpay-wechat-config-add` | POST | `/rest/v2.0/aggpay/wechat-config/add` |

支付结果回调：`aggpay-pre-pay` 的 `notify_spi: trade.pay-result`。

prePayTn 返回类型与前端唤起方式见 `prePayTn唤起方式速查.md`（USER_SCAN → URL 二维码）。

## 开通产品（产品码）

| 产品名称 | 产品码 |
|----------|--------|
| 用户扫码_微信_线上 | `USER_SCAN_WECHAT_ONLINE` |
| 用户扫码_支付宝_线上 | `USER_SCAN_ALIPAY_ONLINE` |
| 用户扫码_微信_线下 | `USER_SCAN_WECHAT_OFFLINE` |
| 用户扫码_支付宝_线下 | `USER_SCAN_ALIPAY_OFFLINE` |

## 前提条件

1. 收单商户需开通上表四个产品：用户扫码_微信_线上、用户扫码_支付宝_线上、用户扫码_微信_线下、用户扫码_支付宝_线下。
2. 商户完成微信、支付宝**子商户号认证**。
3. 商户完成微信公众号 `appId`、`appSecret`、**支付授权目录**配置：调 `aggpay-wechat-config-add`，`appIdList` 中传公众号 `appId`/`appSecret`、`appIdType=OFFICIAL_ACCOUNT`，`tradeAuthDirList` 传支付授权目录。

## 流程

1. 调 `aggpay-pre-pay`：`payWay=USER_SCAN`，`channel` 指定 `WECHAT` 或 `ALIPAY`（独立码每渠道一码）。
2. 接口**同步返回** `prePayTn` 参数，该参数包含**二维码链接**；商家包装该链接生成二维码展示在 PC 页面，供用户扫码支付。
3. 用户用对应 App 扫码支付。
4. PC 页面轮询查单刷新状态；以「支付结果通知 + 查单」确认终态。

## 易错点

- 独立码每渠道一码，用户必须用对应 App 扫（微信码用微信扫）；一码多渠道用 `主扫支付（聚合码）.md`。
- PC 端需轮询查单刷新支付状态，不要只等回调。
- 二维码有有效期，过期需重新下单。
- 终态以后端为准。

## 排障

- 业务错误码：见 doc_md「错误码」章节（与接口文档同文件）。
- 平台错误码/验签：`../../troubleshooting.md`、`../../平台文档/开始对接/平台错误码说明.md`。
- 建议联调时 `curl` 该接口 doc_md 核对独立码的 `payWay`/`channel`/返回字段。

## 代码示例

- 加验签（不使用 SDK 时）：`../../平台文档/平台规范/安全认证/请求签名协议.md`
- 回调解密验签：`../../平台文档/平台规范/安全认证/回调解密协议.md`
