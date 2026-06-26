# APP 支付（使用易宝小程序）

APP 内发起支付，**跳转易宝托管的小程序收银台**完成支付（托管下单）。

> ⚠️ **生成参数或代码前，必须先完整阅读本文「易错点」章节。** 易宝托管小程序与客户自有小程序是**不同接口**（本场景用 `aggpay-tutelage-pre-pay` 托管下单，非 `aggpay-pre-pay` 统一下单）；选错方案会导致传参错误。

> 接口字段以在线文档为准：按下表 catalog id 在 `../api-index.yaml` 取其 `doc_md`，执行
> `curl -sS "<doc_md>"` 后再实现（单文件含字段/示例/错误码/示例代码）。

## 场景 → 接口

| 用途 | catalog id | 方法 | 路径 |
|------|-----------|------|------|
| 托管下单 | `aggpay-tutelage-pre-pay` | POST | `/rest/v1.0/aggpay/tutelage/pre-pay` |
| 查单 | `trade-order-query` | GET | `/rest/v1.0/trade/order/query` |
| 公众号配置（微信，绑定易宝小程序 appid） | `aggpay-wechat-config-add` | POST | `/rest/v2.0/aggpay/wechat-config/add` |

支付结果回调：`aggpay-tutelage-pre-pay` 的 `notify_spi: trade.pay-result`。

prePayTn 返回类型与前端唤起方式见 `prePayTn唤起方式速查.md`。

## 何时选本方案

- 商户**没有自有小程序**或希望最省事：用易宝托管收银台。已有自有小程序见 `APP支付（使用客户小程序）.md`。

## 一、App 跳易宝微信小程序

前置准备：易宝运营配置跳转易宝小程序 appid；收款商户完成微信实名认证；APP 完成微信官方「跳转小程序」配置。

appid 配置：易宝小程序 appid 同步并绑定到收款商户后，商户调 `aggpay-wechat-config-add` 绑定该 appid（`appIdType=MINI_PROGRAM`）。

下单（`aggpay-tutelage-pre-pay`）关键参数：

| 参数 | 取值 |
|------|------|
| `payWay` | `SDK_PAY` |
| `channel` | `WECHAT` |
| `scene` | ONLINE/OFFLINE/...（按业务，一般 OFFLINE） |
| `userIp` | 用户真实 IP（必填） |
| `merchantNo`/`orderId`/`orderAmount`/`goodsName` | 必填 |
| `notifyUrl`/`csUrl` | 支付/清算回调 |
| `fundProcessType` | 需分账时传（见 `../分账/订单分账.md`） |

拉起支付：用返参 `miniProgramOrgId` + `prePayTn`，按微信「APP 拉起小程序」官方方式跳转到易宝小程序内完成支付。

## 二、App 跳易宝支付宝小程序

前置准备：易宝运营配置跳转易宝支付宝小程序；收款商户完成支付宝实名认证。

下单关键参数：同上，但 `channel=ALIPAY`，且 **`returnSchema` 必填**（支付宝 SDK_PAY 时用于支付完成返回商户 APP）。

拉起支付：用返参 `miniProgramOrgId` + `prePayTn` 拉起支付宝，跳易宝小程序内支付，完成后按 schema 返回 APP。

## 通知与查单

- 易宝异步通知到下单 `notifyUrl`（示例字段：`status`、`orderId`、`uniqueOrderNo`、`orderAmount`、`payWay` 等）。
- 查单 `trade-order-query` 必传 `merchantNo` + `orderId`（合单场景传子单 orderId）。

## 易错点

- 托管下单与统一下单是**不同接口**，本场景用 `aggpay-tutelage-pre-pay`，`payWay=SDK_PAY`。
- **`preventTheftMark`（防盗标识）默认不传**：仅易宝运营已为该商编开通「防盗标识」定制能力、且需校验微信来源 appID 时才传（JSON 数组字符串，最多 5 个 appID）。在线 doc_md 示例代码为全参模板，**勿照抄**；未开通商户传此字段可能导致下单失败，排障时先去掉该参数重试。
- 支付宝场景 `returnSchema` 必填，否则无法返回商户 APP。
- 拉起需同时使用 `miniProgramOrgId` 和 `prePayTn`。
- 终态以「通知 + 查单」为准。

## 排障

- 业务错误码：见 doc_md「错误码」章节（与接口文档同文件）。
- 平台错误码/验签：`../../troubleshooting.md`、`../../平台文档/开始对接/平台错误码说明.md`。

## 前端示例代码

- APP 唤起微信小程序与拉起支付的前端代码见 `APP支付（使用客户小程序）.md` 的「前端示例代码」（本场景跳转目标为易宝小程序，跳转方式相同）。

## 后端代码（不使用 SDK 时）

- 加验签：`../../平台文档/平台规范/安全认证/请求签名协议.md`
- 回调解密验签：`../../平台文档/平台规范/安全认证/回调解密协议.md`
