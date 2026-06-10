# APP 支付（使用客户小程序）

APP 内发起支付，**跳转商家自有小程序**完成支付（统一下单）。

> 接口字段以在线文档为准：按下表 catalog id 在 `../api-index.yaml` 取其 `api_id`，执行
> `curl -sS "https://open.yeepay.com/apis/docs/apis/<api_id>/definition.json"` 后再实现。

## 场景 → 接口

| 用途 | catalog id | 方法 | 路径 |
|------|-----------|------|------|
| 下单 | `aggpay-pre-pay` | POST | `/rest/v1.0/aggpay/pre-pay` |
| 查单 | `trade-order-query` | GET | `/rest/v1.0/trade/order/query` |
| 公众号/小程序配置（微信，绑定商家小程序 appid） | `aggpay-wechat-config-add` | POST | `/rest/v2.0/aggpay/wechat-config/add` |

支付结果回调：`aggpay-pre-pay` 的 `notify_spi: trade.pay-result`。

## 何时选本方案

- 商户**已有自有小程序**，支付承载在自有小程序内（会员/营销/复购）。无自有小程序见 `APP支付（使用易宝小程序）.md`。

## 业务流程图

```dot
digraph 聚合支付_APP唤醒小程序支付流程 {
    rankdir=TB; // 从上到下布局

    平台APP -> 平台小程序 [label="1. 从APP唤醒小程序"];
    平台小程序 -> 平台小程序 [label="2. 获取订单信息"];
    平台小程序 -> 平台小程序 [label="3. 获取用户ID(openid/buyer_id)"];
    平台小程序 -> 平台后端 [label="4. 发起支付"];
    平台后端 -> 易宝 [label="5. 聚合支付统一下单"];
    易宝 -> "微信/支付宝" [label="6. 支付下单"];
    "微信/支付宝" -> 易宝 [label="7. 返回支付参数"];
    易宝 -> 平台后端 [label="8. 返回支付参数"];
    平台后端 -> 平台小程序 [label="9. 返回支付参数"];
    平台小程序 -> "微信/支付宝" [label="10. 调用微信/支付宝支付接口"];
    "微信/支付宝" -> "微信/支付宝" [label="11. 处理支付业务"];
    "微信/支付宝" -> 易宝 [label="12. 支付成功通知"];
    易宝 -> 平台后端 [label="13. 支付成功通知"];
}
```

## 对接步骤（指引文字版）

1. 用户在商户 APP 商城购买 → 商家 APP 生成订单。
2. 商家后台调易宝下单 → 易宝返回拉起微信/支付宝小程序信息。
3. 商家 APP 跳转到商家小程序。
4. 商家小程序用 `prePayTn` 调起微信/支付宝支付。
5. 用户确认支付 → 渠道通知易宝 → 易宝通知商户扣款成功。

> 以最终异步通知和查单结果为准。

## 一、App 跳商家微信小程序

前置：微信开放平台有通过的 APP 移动应用；微信公众平台有小程序并与移动应用关联；完成「APP 拉起小程序」配置；可引用易宝 demo（`pay-applet`）拉起支付页。

获取 openId：小程序 `wx.login` 取 code → 服务端 `code2Session` 换 `openId`；收款商户完成微信报备与实名认证。

appid 配置：调 `aggpay-wechat-config-add` 绑定需跳转的小程序 appid 与 appSecret。

下单（`aggpay-pre-pay`）关键参数：`payWay=MINI_PROGRAM`、`channel=WECHAT`、`appId`=跳转小程序 appid、`userId`=openId、`userIp` 必填、`scene` 一般 OFFLINE、`notifyUrl`/`csUrl`。

拉起：小程序用返参 `prePayTn` 发起微信支付（小程序内拉起密码框）。微信侧限制：支付完成后需用户点按钮才能回到商户 APP，可自行开发引导页。

## 二、App 跳商户支付宝小程序

前置：已上架 APP；准备好跳转用支付宝小程序；收款商户完成支付宝实名认证；APP 用 `alipays://platformapi/startapp?appId=...&page=...` 打开小程序；获取用户支付宝 `userId`。

下单关键参数：`payWay=MINI_PROGRAM`、`channel=ALIPAY`、`userId`=支付宝 userId、`appId`=小程序 appid、`userIp` 必填、`scene` 一般 OFFLINE。

拉起：用 `prePayTn` 按支付宝小程序 JSAPI 唤起收银台。

## 通知与查单

- 易宝异步通知到 `notifyUrl`。
- 查单 `trade-order-query` 必传 `merchantNo` + `orderId`。

## 易错点

- 使用统一下单 `aggpay-pre-pay`、`payWay=MINI_PROGRAM`，不要错用托管下单。
- 微信 `openId` 必须基于商家自有 `appId` 获取；支付宝需 `userId`。
- 微信支付后返回 APP 需用户点按钮（不能自动跳回），按需做引导页。
- 终态以后端为准。

## 排障

- 业务错误码：`curl .../apis/<api_id>/errcode.json`。
- 平台错误码/验签：`../../troubleshooting.md`、`../../平台文档/开始对接/平台错误码说明.md`。

## 代码示例

- 加验签/加解密/回调接收：`../../示例代码/`（按需补充）。
