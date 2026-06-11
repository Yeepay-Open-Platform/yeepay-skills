# app唤起微信小程序并支付

```javascript
 wx.miniapp.launchMiniProgram({
    userName: '', // 微信小程序原始ID
    path: '',
    miniprogramType: 2, //0 release ，1 test, 2 preview
    success: (res) => {
        wx.showModal({
            content: res.data,
        })
        console.log('get wx phonenumber success:', res)
    }
})
```

## 微信支付

> 空白参数由服务端在易宝平台下单后，会返回 `prepayTn` 参数，这个参数为一个 JSON 串，通过 JSON.parse() 解析。

```javascript
wx.miniapp.requestPayment({
    timeStamp: '',
    mchId: '',
    prepayId: '',
    package: '',
    nonceStr: '',
    sign: '',
    success: (res) => {
      console.warn('wx.miniapp.requestPayment success:', res)
    },
    fail: (res) => {
      console.error('wx.miniapp.requestPayment res:', res)
    },
    complete: (res) => {
      console.error('wx.miniapp.requestPayment res:', res)
    }
  })
```
