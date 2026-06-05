# 一、App跳易宝微信小程序支付流程：

## 1、前置准备：

1）易宝运营配置跳转易宝小程序appid;

2）收款商户完成微信实名认证；

3）APP已完成微信官方跳转小程序相关配置；

微信官方配置指引：[https://developers.weixin.qq.com/doc/oplatform/MobileApp/LaunchingaMiniProgram/LaunchingaMiniProgram.html](https://developers.weixin.qq.com/doc/oplatform/Mobile_App/Launching_a_Mini_Program/Launching_a_Mini_Program.html)

## 2、appid配置流程

1）易宝运营配置跳转易宝小程序appid;

2)易宝小程序appid同步给商户，绑定到收款商户下

3）商户调用公众号配置接口绑定appid

公众号配置接口：

API接口地址：/rest/v2.0/aggpay/wechat-config/add

按照接口传参数，绑定易宝提供的appid

原接口文档地址：

[https://open.yeepay.com/docs/products/fwssfk/api/postrestv2.0aggpaywechat-configadd](https://open.yeepay.com/docs/products/fwssfk/api/post__rest__v2.0__aggpay__wechat-config__add)

**接口关键字段参数：**


|                       |             |          |                                          |
| --------------------- | ----------- | -------- | ---------------------------------------- |
| **字段参数**              | **参数名称**    | **是否必填** | **备注**                                   |
| **merchantNo**        | 商户编号        | 是        | 收款商编                                     |
| **parentMerchantNo**  | 发起方商户编号     | 否        | 收款商户的父级商编                                |
| **tradeAuthDirList** | 支付授权目录列表    | 否        | 当需要绑定公众号支付授权目录时，需上传                      |
| **appIdList**         | 支付appId目录列表 | 否        | 当需要绑定小程序或者公众号appid时,需上传                  |
| **reportMerchantNo**  | 报备商户号       | 否        | 若指定报备商户号，则仅针对此报备商户号进行配置，不传则按商编下所有报备号进行绑定 |


**代码示例：**

```JSON
{
  "tradeAuthDirList": ["[\"https://weixin.keruyun.com/shop/\",\"https://h5.keruyun.com/shop/\",\"https://h5.keruyun.com/\"]"],
  "appIdList": ["[{\"appId\":\"wxf99a255ba9d9055f\",\"appIdType\":\"MINI_PROGRAM\"}]"],
  "parentMerchantNo": ["10090***194"],
  "merchantNo": ["10093***990"]
}
```

---

## 3、调用下单接口

聚合托管下单接口：/rest/v1.0/aggpay/tutelage/pre-pay

原接口文档地址：[https://open.yeepay.com/docs/apis/INDUSTRYSOLUTION/GENERAL/bzshsfk/juhezhifu/optionsrestv1.0aggpaytutelagepre-pay](https://open.yeepay.com/docs/apis/INDUSTRY_SOLUTION/GENERAL/bzshsfk/juhezhifu/options__rest__v1.0__aggpay__tutelage__pre-pay)

**接口关键字段参数：**


|                      |           |          |                                                                                               |
| -------------------- | --------- | -------- | --------------------------------------------------------------------------------------------- |
| **字段参数**             | **参数名称**  | **是否必填** | **备注**                                                                                        |
| **payWay**           | **支付方式**  | 是        | 传：SDK_PAY                                                                                     |
| **parentMerchantNo** | 发起方商户编号   | 否        | 收款商户的父级商编                                                                                     |
| **channel**          | 渠道类型      | 是        | 传：WECHAT                                                                                      |
| **scene场景**         | **场景**    | 是        | 可选值：ONLINE/OFFLINE/BAOXIAN/GONGYI/DC_SEPARATION/DIGITAL/REGISTRATION/PRIVATE_EDUCATION/DIRECT |
| **userIp**           | 用户IP      | 是        | 用户真实IP地址                                                                                      |
| **merchantNo**       | 商户编号      | 是        | 收单主体商编                                                                                        |
| **orderId**          | 商户收款请求号   | 是        | 商户系统内部生成的订单号，需要保持在同一个商户下唯一                                                                    |
| **orderAmount**      | 订单金额      | 是        | 业务上是必须参数，单位： 元， 两位小数， 最低 0.01                                                                 |
| **goodsName**        | 商品名称      | 是        | 商品名称，简单描述订单信息或商品简介，用于展示在收银台页面或者支付明细中                                                          |
| **fundProcessType**  | 分账订单标记    | 否        | - 需要分账:DELAY_SETTLE - 不需要分账:REAL_TIME - 实时分账;需同时传入divideDetail:REAL_TIME_DIVIDE               |
| **expiredTime**      | 订单截止时间    | 否        | 订单截止时间string(date-time)(32)订单截止时间格式"yyyy-MM-dd HH:mm:ss"不传默认一天                             |
| **memo**             | 对账备注      | 否        | string(256)对账备注商户自定义参数，会展示在交易对账单中，支持85个字符（中文或者英文字母）                                        |
| **notifyUrl**        | 支付结果通知地址 | 否        | 接收支付结果的通知地址注：回调地址可正常接收通知                                                                    |
| **csUrl**            | 清算回调地址    |          | 清算成功服务器回调地址，不传则不通知。详见清算结果通知注：回调地址可正常接收通知                                                     |
| 其他字段                 |           |          | 其他字段非必填，按照商户需求传                                                                               |


**请求下单代码示例：**

```JSON
{
  "orderId": ["S202*****768540859"],
  "channel": ["WECHAT"],
  "payWay": ["SDK_PAY"],
  "expiredTime": ["2026-04-21 20:02:43"],
  "scene": ["OFFLINE"],
  "fundProcessType": ["REAL_TIME"],
  "orderAmount": ["19.9"],
  "csUrl": ["https://bac*****/yeePayCsNotify/YeePayWeChatApp/1/13796/S20260421195943768540859"],
  "userIp": ["118.73.7.182"],
  "notifyUrl": ["https://backend.******fy/yeePayWechatApp/1/13796/S20260421195943768540859"],
  "parentMerchantNo": ["100***1605"],
  "goodsName": ["0421WX【晨烨蜜源·手工蜜皂】"],
  "merchantNo": ["100****743"]
}
```

**拉起支付：**

使用返参中的miniProgramOrgId和prePayTn进行拉起

```JSON
{
  "miniProgramOrgId": "gh_******bd73",
  "miniProgramPath": "pages/fromAppPay/index",
  "code": "00000",
  "orderId": "S2026******768540859",
  "appId": "wxeb***332a64879",
  "prePayTn": "pages/fromAppP************db1749523&customerNo=100***76743&goodsName=0421WX%E3%80%90%E6%99%A8%E7%83%A8%E8%9C%9C%E6%BA%90%C2%B7%E6%89%8B%E5%B7%A5%E8%9C%9C%E7%9A%82%E3%80%91&customerRequestNo=S20260421195943768540859&orderAmount=19.9&launchSource=SDK_PAY",
  "uniqueOrderNo": "30132*****1380507262",
  "message": "成功"
}
```

用户选择微信支付，商户需要根据微信文档进行APP拉起小程序，商家APP跳转到商家的小程序内。

- APP拉起小程序功能的微信官方文档链接：++[https://developers.weixin.qq.com/doc/oplatform/MobileApp/LaunchingaMiniProgram/LaunchingaMiniProgram.html](https://developers.weixin.qq.com/doc/oplatform/Mobile_App/Launching_a_Mini_Program/Launching_a_Mini_Program.html)++

用户支付成功后，易宝异步通知商家支付成功信息。

## 拉起支付示例：

# 二、App跳易宝支付宝小程序支付流程：

## 1、前置准备：

1）易宝运营配置跳转易宝支付宝小程序;

2）收款商户完成支付宝实名认证；

## 2、调用下单接口

聚合托管下单接口：/rest/v1.0/aggpay/tutelage/pre-pay

原接口文档地址：[https://open.yeepay.com/docs/apis/INDUSTRYSOLUTION/GENERAL/bzshsfk/juhezhifu/optionsrestv1.0aggpaytutelagepre-pay](https://open.yeepay.com/docs/apis/INDUSTRY_SOLUTION/GENERAL/bzshsfk/juhezhifu/options__rest__v1.0__aggpay__tutelage__pre-pay)

**接口关键字段参数：**


|                      |                |          |                                                                                               |
| -------------------- | -------------- | -------- | --------------------------------------------------------------------------------------------- |
| **字段参数**             | **参数名称**       | **是否必填** | **备注**                                                                                        |
| **payWay**           | **支付方式**       | 是        | 传：SDK_PAY                                                                                     |
| **parentMerchantNo** | 发起方商户编号        | 否        | 收款商户的父级商编                                                                                     |
| **channel**          | 渠道类型           | 是        | 传：WECHAT                                                                                      |
| **scene场景**         | **场景**         | 是        | 可选值：ONLINE/OFFLINE/BAOXIAN/GONGYI/DC_SEPARATION/DIGITAL/REGISTRATION/PRIVATE_EDUCATION/DIRECT |
| **userIp**           | 用户IP           | 是        | 用户真实IP地址                                                                                      |
| **merchantNo**       | 商户编号           | 是        | 收单主体商编                                                                                        |
| **orderId**          | 商户收款请求号        | 是        | 商户系统内部生成的订单号，需要保持在同一个商户下唯一                                                                    |
| **orderAmount**      | 订单金额           | 是        | 业务上是必须参数，单位： 元， 两位小数， 最低 0.01                                                                 |
| **goodsName**        | 商品名称           | 是        | 商品名称，简单描述订单信息或商品简介，用于展示在收银台页面或者支付明细中                                                          |
| **returnSchema**     | 返回商户APP的Schema | 是        | 支付宝且为SDK_PAY时必传，否则无法返回商户APP                                                                   |
| **fundProcessType**  | 分账订单标记         | 否        | - 需要分账:DELAY_SETTLE - 不需要分账:REAL_TIME - 实时分账;需同时传入divideDetail:REAL_TIME_DIVIDE               |
| **expiredTime**      | 订单截止时间         | 否        | 订单截止时间string(date-time)(32)订单截止时间格式"yyyy-MM-dd HH:mm:ss"不传默认一天                             |
| **memo**             | 对账备注           | 否        | string(256)对账备注商户自定义参数，会展示在交易对账单中，支持85个字符（中文或者英文字母）                                        |
| **notifyUrl**        | 支付结果通知地址      | 否        | 接收支付结果的通知地址注：回调地址可正常接收通知                                                                    |
| **csUrl**            | 清算回调地址         |          | 清算成功服务器回调地址，不传则不通知。详见清算结果通知注：回调地址可正常接收通知                                                     |
| 其他字段                 |                |          | 其他字段非必填，按照商户需求传                                                                               |


**请求下单代码示例：**

```JSON
{
"orderId":["251124*****16932981554"],
"channel":["ALIPAY"],
"payWay":["SDK_PAY"],
"locale":["zh_CN"],
"returnSchema":["yptest://"]
"expiredTime":["2025-11-2419:19:51"],
"scene":["OFFLINE"],
"fundProcessType":["DELAY_SETTLE"],
"orderAmount":["0.2"],
"userIp":["10.0.49.136"],
"notifyUrl":["https://livepay-de******3702/19023**773"],
"parentMerchantNo":["100***505"],
"goodsName":["测试便宜的商品商品购买支付:0.20元"],
"ts":["1763982891875"]，
"merchantNo":["100***3702"]
}
```

**拉起支付：**

使用返参中的miniProgramOrgId和prePayTn进行拉起

```JSON
{
"miniProgramPath":"pages/fromAppPay/index"，
"code":"00000"，
"orderId":"25112419****6932981554"，
"appId":"202100****43335"，
"prePay Tn":"aLipays://pLatforma******s2FfromAppPay2Findex33Fstate3D5b8e5669-36cf-45c7-804f-27de662bfe03%26customerNo%3D10091053702%26orderAmount%3D0.2&thirdPartSchema=","unique0rderNo":"301320251124000000000673874613"，
  "message": "成功"
}
```

用户选择支付宝支付，商户进行APP拉起小程序，商家APP跳转到易宝小程序内拉起支付，支付完成后返回APP。

[支付宝小程序跳转回APP](https://yeepay.feishu.cn/wiki/HSanwg7Z0inRF5knFvUczmD6nae?from=from_copylink)

用户支付成功后，易宝异步通知商家支付成功信息。

## 拉起支付示例：

# 三、异步通知

下单时候传传了notifyUrl支付结果通知地址，支付完成后易宝会将通知参数推送给回调地址；

**异步通知参数通知示例：**

```SQL
{
    "sumDiscountPromotionAmount": "0",
    "orderId": "2046586302xxxx-10982-0-xt0001",
    "bankOrderId": "5752490844260421",
    "settleAmount": "1.00",
    "channel": "WECHAT",
    "yopMerchantNo": "100xxxx66",
    "payWay": "USER_SCAN",
    "uniqueOrderNo": "301320260421000000317386901672",
    "merchantName": "欣意无限",
    "orderAmount": "1.00",
    "payAmount": "1.00",
    "yopMerchantName": "郑州欣意无限信息技术有限公司",
    "realPayAmount": "1.00",
    "basicsProductFirst": "USER_SCAN",
    "tradeType": "REALTIME",
    "channelOrderId": "4500000128202604214762773531",
    "basicsProductThird": "OFFLINE",
    "paySuccessDate": "2026-04-21 21:46:31",
    "basicsProductSecond": "WECHAT",
    "outClearChannel": "UP",
    "payerInfo": "{\"appID\":\"wx8b836f558bec6fd4\",\"bankCardNo\":\"\",\"bankId\":\"CFT\",\"cardType\":\"DEBIT\",\"channelTrxId\":\"4500000128202604214762773531\",\"mobilePhoneNo\":\"\",\"userID\":\"oMDsp6EeeFVVd5fNKJeJIQUPwpss\",\"yeepayOpenID\":\"obwCas1vtv-czNuClYSLqegJ18Fw\"}",
    "appID": "wx8b836f558bec6fd4",
    "channelSettleAmount": "1.00",
    "parentMerchantNo": "100xxxx66",
    "channelTrxId": "4500000128202604214762773531",
    "businessType": "DIRECT_OPERATION",
    "merchantNo": "10088890966",
    "status": "SUCCESS",
    "channelMerchantInfo": "{\"channelMerchantNo\":\"560180424\"}"
}
```

# 四、订单查询

**API请求地址：**/rest/v1.0/trade/order/query

**必传参数：**

merchantNo= 收款商编

orderId = 交易下单传入的商户收款请求号(合单收款场景请传入子单的商户收款请求号)

**请求报文示例**

```JSON
{
  "orderId": ["KZBNAxxxxxxx0585216"],
  "parentMerchantNo": ["1009xxxx704"],
  "merchantNo": ["100xxxx2704"]
}
```

**返回报文示例**

```JSON
{
  "orderId": "KZBNAxxxxxxx0585216",
  "yopMerchantNo": "1009xxxxx37",
  "ypSettleAmount": 0,
  "fundProcessType": "REAL_TIME",
  "parentMerchantNo": "100xxxx2704",
  "status": "PROCESSING",
  "merchantNo": "100xxxx2704",
  "code": "OPR00000",
  "uniqueOrderNo": "301320260421000000222384439554",
  "orderAmount": 8.8,
  "yopMerchantName": "成都柏岁创新科技有限公司",
  "tradeType": "REALTIME",
  "bizSystemNo": "AGG_PAY",
  "message": "成功",
  "businessType": "DIRECT_OPERATION"
}
```

