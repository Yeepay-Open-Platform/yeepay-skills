# h5唤起微信公众号支付

> 在微信客户端浏览器访问的H5网页，进入支付环节。

## 唤起微信公众号支付

> 服务端在易宝平台下单后，会返回 `paySign` 参数，这个参数为一个 JSON 串，包含支付所需的所有签名信息(paySign)，通过 JSON.parse() 解析。

```javascript
function onBridgeReady() {
    WeixinJSBridge.invoke('getBrandWCPayRequest', {
        "appId": "wxxxxxxx",     //公众号ID，由商户传入
        "timeStamp": "",     //时间戳，自1970年以来的秒数
        "nonceStr": "",      //随机串
        "package": "",
        "signType": "RSA",     //微信签名方式
        "paySign": "" //签名信息
    },
    function(res) {
        if (res.err_msg == "get_brand_wcpay_request:ok") {
            // 使用以上方式判断前端返回,微信团队郑重提示：
            //res.err_msg将在用户支付成功后返回ok，但并不保证它绝对可靠，商户需进一步调用后端查单确认支付结果。
        }
    });
}
if (typeof WeixinJSBridge == "undefined") {
    if (document.addEventListener) {
        document.addEventListener('WeixinJSBridgeReady', onBridgeReady, false);
    } else if (document.attachEvent) {
        document.attachEvent('WeixinJSBridgeReady', onBridgeReady);
        document.attachEvent('onWeixinJSBridgeReady', onBridgeReady);
    }
} else {
    onBridgeReady();
}
```
