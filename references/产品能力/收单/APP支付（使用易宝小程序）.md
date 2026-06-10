# APP 支付（使用易宝小程序）

APP 内发起支付，**跳转易宝托管的小程序收银台**完成支付（托管下单）。

> 接口字段以在线文档为准：按下表 catalog id 在 `../api-index.yaml` 取其 `api_id`，执行
> `curl -sS "https://open.yeepay.com/apis/docs/apis/<api_id>/definition.json"` 后再实现。

## 场景 → 接口

| 用途 | catalog id | 方法 | 路径 |
|------|-----------|------|------|
| 托管下单 | `aggpay-tutelage-pre-pay` | POST | `/rest/v1.0/aggpay/tutelage/pre-pay` |
| 查单 | `trade-order-query` | GET | `/rest/v1.0/trade/order/query` |
| 公众号配置（微信，绑定易宝小程序 appid） | `aggpay-wechat-config-add` | POST | `/rest/v2.0/aggpay/wechat-config/add` |

支付结果回调：`aggpay-tutelage-pre-pay` 的 `notify_spi: trade.pay-result`。

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
- 支付宝场景 `returnSchema` 必填，否则无法返回商户 APP。
- 拉起需同时使用 `miniProgramOrgId` 和 `prePayTn`。
- 终态以「通知 + 查单」为准。

## 排障

- 业务错误码：`curl .../apis/<api_id>/errcode.json`。
- 平台错误码/验签：`../../troubleshooting.md`、`../../平台文档/开始对接/平台错误码说明.md`。

## 代码示例

- 加验签/加解密/回调接收：`../../示例代码/`（按需补充）。
