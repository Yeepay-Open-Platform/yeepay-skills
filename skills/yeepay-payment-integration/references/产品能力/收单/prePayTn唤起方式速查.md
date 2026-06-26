# 聚合统一下单 prePayTn 唤起方式速查

聚合统一下单（`aggpay-pre-pay` 等）同步返回的 **`prePayTn`** 为预支付标识信息。不同 `payWay + channel + scene` 组合下，返回类型与前端唤起方式不同（URL、JSON、订单号等）。

> 本文档为**跨收单场景**的本地权威速查表；各场景接入流程见同目录下对应场景 md。
> 在线备份：`api-index.yaml` 条目 `prepay-tn-usage` 的 `doc_md`。

## 字段说明

- `prePayTn` 为聚合统一下单返回的预支付标识信息。
- 调起支付前须按下表确认当前组合的**返回类型**与**唤起方式**。
- 示例值为脱敏示意，实际以接口响应为准。

## payWay + channel + scene → 唤起方式

| 支付方式 payWay | 渠道类型 channel | 场景 scene | 返回类型 | 唤起支付方式 | 参考链接 | 示例值 |
| --- | --- | --- | --- | --- | --- | --- |
| USER_SCAN | 不限 | 不限 | URL | 将 URL 做成二维码显示到前端页面 | 无 | 微信主扫：`https://qr.yeepay.com/oc/xxxxxxxx`；支付宝主扫：`https://qr.alipay.com/xxxxxxxx`；银联主扫：`https://qr.95516.com/00010000/0121623543770315423452773511xxxx` |
| MINI_PROGRAM | WECHAT | 除 STORE_ASST 外 | JSON | 参考微信小程序调起支付 API；解析 `prePayTn` 后传入 | https://pay.weixin.qq.com/doc/v2/merchant/4011939566 | `{"appId":"wxda0e24563e78d429","timeStamp":"1715745233","nonceStr":"3fcd256729dc42e7a961979xxxxc08da","package":"prepay_id=wx1511535xxxx0452fe308039699999f0001","signType":"RSA","paySign":"..."}` |
| MINI_PROGRAM | WECHAT | STORE_ASST | JSON | 参考微信小店 B2B 支付 API；解析 `prePayTn` 后传入（**注意字段顺序不能换**） | https://developers.weixin.qq.com/miniprogram/dev/platform-capabilities/industry/B2b_store_assistant.html | `{"signData":"{...}","paySig":"...","signature":"..."}` |
| MINI_PROGRAM | ALIPAY | 不限 | 订单号 | 参考支付宝小程序调起支付 API；将 `prePayTn` 作为 `tradeNO` 传入 | https://opendocs.alipay.com/mini/api/openapi-pay | `2024051522001475xxxx11717640` |
| WECHAT_OFFIACCOUNT | WECHAT | 不限 | JSON | 参考微信内 H5 调起支付（JSAPI）；解析 `prePayTn` 后传入 | https://pay.weixin.qq.com/doc/v2/merchant/4011935213 | `{"appId":"wxba8e2a384ba4f6f1","timeStamp":"1715745360","nonceStr":"...","package":"prepay_id=...","signType":"RSA","paySign":"..."}` |
| ALIPAY_LIFE | ALIPAY | 不限 | 订单号 | 参考 JSAPI 唤起收银台支付 | https://opendocs.alipay.com/open/common/105591 | `20240515220014102xxxx2268922` |
| JS_PAY | UNIONPAY | 不限 | URL | 直接重定向到返回的 URL 完成支付 | 无 | `https://qr.95516.com/UP04/qrcGtwWeb-web/front/confirmOrder?sessionId=...` |
| SDK_PAY | UNIONPAY | 不限 | 订单号 | 对接银联 SDK 支付或统一收银台 | 银联 SDK：https://open.unionpay.com/tjweb/acproduct/list?apiSvcId=450&index=5#5nav0；统一收银台：https://open.unionpay.com/tjweb/acproduct/list?apiSvcId=3021&index=4 | `{"tn":"79584822160697xxxx600"}` |
| H5_PAY | UNIONPAY | 不限 | JSON | 在移动端浏览器发起 **POST** 请求：`url` 为请求地址，`postParamMap` 为 POST 参数 | 无 | `{"postParamMap":"{...}","url":"https://gateway.xxxxx.com/gateway/api/frontTransReq.do"}` |
| SDK_PAY | WECHAT | ONLINE/DIGITAL | JSON | 商户 APP 通过 openSDK `sendReq` 拉起微信支付 | https://pay.weixin.qq.com/doc/v3/merchant/4013070351 | 注意 1：iOS 传 `package`，Android 传 `packagevalue`；注意 2：`paysign` 需转成 `sign` 传给微信 |

## 场景文档交叉引用

| 典型场景 | 主要涉及组合 | 场景 md |
| --- | --- | --- |
| 主扫（独立码 / 聚合码） | USER_SCAN → URL 二维码 | `主扫支付（独立码-线上PC）.md`、`主扫支付（聚合码）.md` |
| 小程序支付 | MINI_PROGRAM + WECHAT/ALIPAY | `小程序支付.md` |
| 微信内 H5 + 公众号 | WECHAT_OFFIACCOUNT | `微信内H5+公众号支付.md` |
| 浏览器 H5 | ALIPAY_LIFE、USER_SCAN URL 重定向等 | `浏览器H5支付.md` |
| APP 支付 | SDK_PAY + WECHAT 等 | `APP支付（使用易宝小程序）.md`、`APP支付（使用客户小程序）.md` |

## 易错点

- **返回类型误判**：同一接口在不同 `payWay` 下 `prePayTn` 可能是 URL、JSON 或纯订单号，须按表处理，不可统一当 JSON 解析。
- **微信小店 STORE_ASST**：`prePayTn` 内 JSON 字段顺序不可调换。
- **微信 APP SDK**：iOS / Android 的 `package` 字段名不同；`paysign` 需映射为微信侧的 `sign`。
- **银联 H5_PAY**：须用 POST 提交 `postParamMap`，不能简单 `location.href` 跳转。
