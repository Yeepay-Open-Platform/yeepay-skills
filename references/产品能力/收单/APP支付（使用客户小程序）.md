# APP 支付（使用客户小程序）

APP 内发起支付，**跳转商家自有小程序**完成支付（统一下单）。

> 接口字段以在线文档为准：按下表 catalog id 在 `../api-index.yaml` 取其 `doc_md` 链接，执行
> `curl -sS "<doc_md>"` 后再实现（单文件含字段/示例/错误码/示例代码）。

## 场景 → 接口

| 用途 | catalog id | 方法 | 路径 |
|------|-----------|------|------|
| 下单 | `aggpay-pre-pay` | POST | `/rest/v1.0/aggpay/pre-pay` |
| 查单 | `trade-order-query` | GET | `/rest/v1.0/trade/order/query` |
| 公众号配置（异步，条件必读） | `aggpay-wechat-config-add` | POST | `/rest/v2.0/aggpay/wechat-config/add` |

支付结果回调：`aggpay-pre-pay` 的 `notify_spi: trade.pay-result`。

## 流程

1. APP 跳转商家自有小程序，前端在小程序内换取 `openId`/`userId`。
2. 后端调 `aggpay-pre-pay`，`payWay=MINI_PROGRAM`，传入商家 `appId`、`userId`。
3. 前端用 `prePayTn` 唤起小程序支付。
4. 以「支付结果通知 + 查单」确认终态。

## 何时选本方案

- 商户**已有自有小程序**，希望支付承载在自有小程序内（会员/营销/复购）。
- 若无自有小程序，改用 `APP支付（使用易宝小程序）.md`。

## 必读规则

1. `../../平台文档/平台规范/安全认证/鉴权认证机制(RSA).md`（请求签名）。
2. `../../平台文档/平台规范/安全认证/结果通知(RSA).md`（回调验签）。

## 易错点

- 使用统一下单 `aggpay-pre-pay`，不要错用托管下单接口。
- `openId` 必须基于商家自有 `appId` 获取。
- 终态以后端为准。

## 排障

- 业务错误码：见接口 `doc_md` 的「错误码」章节。
- 平台错误码/验签：`../troubleshooting.md`、`../../平台文档/开始对接/平台错误码说明.md`。

## 代码示例

- 加验签/加解密/回调接收：`../../示例代码/`（按需补充）。
