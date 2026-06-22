# 报文加密机制(SM)

本文适合的阅读人群

-   无 SDK 对接 API 的开发者
-   YOP SDK 编写者

## [](https://open.yeepay.com/docs-v3/platform/14024.md#%E9%80%82%E7%94%A8%E8%8C%83%E5%9B%B4)适用范围

此机制适用于安全需求为`YOP-SM2-SM3`，有请求参数或响应结果有在传输过程中有加密需求的用户。

## [](https://open.yeepay.com/docs-v3/platform/14024.md#%E8%AF%B7%E6%B1%82%E6%8A%A5%E6%96%87%E5%8A%A0%E5%AF%86%E8%BF%87%E7%A8%8B)请求报文加密过程

加密信息通过请求头`x-yop-encrypt`传递。格式如下

{YOP加密协议版本(必填)}/{平台证书序列号(必填)}/{密钥类型(必填)}`_`{分组模式(必填)}`_`{填充算法(必填)}/{加密密钥值(必填)}/{IV}{;}{附加信息}/{客户端支持的大参数加密模式(必填)}/{encryptHeaders}/{encryptParams}

### [](https://open.yeepay.com/docs-v3/platform/14024.md#%E8%AF%B7%E6%B1%82%E5%A4%B4%E5%90%84%E7%BB%84%E6%88%90%E9%83%A8%E5%88%86%E8%AF%B4%E6%98%8E%EF%BC%9A)请求头各组成部分说明：

**{YOP加密协议版本}**：目前YOP的加密协议版本号为`yop-encrypt-v1`

**{平台证书序列号}**：用于加密SM4密钥的平台商密证书的序列号，获取方式见 `平台商密证书.md`

**{密钥类型}`_`{分组模式}`_`{填充算法}**：目前可选`SM4_CBC_PKCS5Padding`

**{加密密钥值}**：平台SM2公钥加密后进行urlSafeBase64编码的值

**{IV}{;}{附加信息}**：加密数据时的随机向量（进行urlSafeBase64编码）及附加信息，目前`SM4_CBC_PKCS5Padding`中无附加信息，不填即可

**{客户端支持的大参数加密模式}**:目前支持stream（流式加密模式），故就填stream即可

**{encryptHeaders}**：加密请求参数之外还支持对请求头进行加密(YOP指定的请求头不能进行加密)，加密方式与加密form格式参数相同，若加密了请求头，此处为请求头名称，多个值之间用半角分号分隔，最后需要进行urlSafeBase64编码。

**{encryptParams}**：加密了的参数名称。若加密了form参数中的所有参数或加密了json格式的参数，则参数名称为$，否则多个值之间用半角分号分隔,最后最后对整体进行urlSafeBase64编码。

### [](https://open.yeepay.com/docs-v3/platform/14024.md#%E4%BD%BF%E7%94%A8%E9%9A%8F%E6%9C%BAsm4%E5%AF%86%E9%92%A5%E5%8A%A0%E5%AF%86%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0)使用随机SM4密钥加密请求参数

目前YOP支持加密算法为`SM4/CBC/PKCS5Padding`。示例如下

使用的SM4密钥为

```
// 为了便于展示，对密钥进行urlSafeBase64编码
nZKUHddTj2hHBBSHsi8GYQ
```

若content-type为form，则加密参数传参为：

```
// form格式传参，对参数idNo进行加密传输
// 请求参数明文值
String idNo = "123456789";
// 请求参数采用 SM4/CBC/PKCS5Padding 算法模式加密后的值(进行了urlSafeBase64编码）
String encryptedIdNo = "PNzhXByfDeyfQ2w8LD07Ug";

// 调用API时传入加密后的参数值（params存放form格式的请求参数，与requestParameterMap的作用相同）
// params.put("idNo",encryptedIdNo);

// 将需要加密的请求头放入set集合，用于生成加密头
// encryptHeaders.add(xxx);

// 将需要加密的参数名称放入set集合，用于生成加密头
// encryptParams.add("idNo");

// 文件流加密 参考javax.crypto.CipherInputStream
```

若content-type为json，则加密参数传参为：

```
// json格式传参，对整个json数据进行加密
String jsonRequest = "{\"appId\":\"app_1595815987915711\",\"alias\":\"alias_0329\"}";

// 加密后的json数据（进行了urlSafeBase64编码）
String encryptedJsonRequest = "C3UTRPenhJfxJh2M5Dzy_aqWumu9gHa2NXblArC3trzhMS6KTgaXIkzd8gQ7KcI0pX81geA9lsKSM59oOIpljg";

// 将请求数据替换为加密后的数据（jsonPayload存放json格式的请求参数）
// jsonPayload.setContent(encryptedJsonRequest);

// 将需要加密的请求头放入set集合，用于生成加密头
// encryptHeaders.add(xxx);

// 将需要加密的参数名称放入set集合，用于生成加密头。目前json推荐整体加密
// encryptParams.add("$");
```

### [](https://open.yeepay.com/docs-v3/platform/14024.md#%E4%BD%BF%E7%94%A8%E5%B9%B3%E5%8F%B0sm2%E5%85%AC%E9%92%A5%E5%8A%A0%E5%AF%86sm4%E5%AF%86%E9%92%A5)使用平台SM2公钥加密SM4密钥

若要获取平台 SM2 公钥，详见 `平台商密证书.md`。

加密过程具体可参考源码中的 [YopSm2Encryptor](https://github.com/yop-platform/yop-java-sdk/blob/develop/yop-java-sdk-crypto-gm/src/main/java/com/yeepay/yop/sdk/gm/security/encrypt/YopSm2Encryptor.java)。 注：构建 SM2Engine 的 mode 设置为`SM2Engine.Mode.C1C3C2`

### [](https://open.yeepay.com/docs-v3/platform/14024.md#%E6%9E%84%E9%80%A0%E8%AF%B7%E6%B1%82%E5%A4%B4)构造请求头

上述示例中构造出的请求头分别为

```
// 对form格式中的参数idNo进行加密传输
yop-encrypt-v1/4028129061/SM4_CBC_PKCS5Padding/BEYlmrR6tuygyt6vLwtr8irXXlrDT_FqFmFcVlsbwyyuvYOt3WQcsbiNlCBO4y_o5NDuI0c64xiYkbZwjNs_8xDsTRvVZnDDCzQt_GlruF3nA-iVjNNAoogyEAX-UI1-jBU0NF4BqG2-3eyl7WdpSsk/IH_plF0-yR1Yd5pMaZvnlQ/stream//aWRObw
```

```
// 对json格式参数进行加密传输
yop-encrypt-v1/4028129061/SM4_CBC_PKCS5Padding/BKK-34fu3C_jIky3ETcEMFwEFE9vf1rxeBHor8NSJ3ti1i0CJFY05Tz0kBTvxnJnclr6hW8-MXvCObw_9Cg_dvHKxleMhiTUWq1uyyBTUqn4j4QBLFLlzH-Ks3ky9lslXMq_fYzlt1ffrylscsYehRQ/daCGuq8ep1UIIcAXYi6OqQ/stream//JA
```

## [](https://open.yeepay.com/docs-v3/platform/14024.md#%E5%93%8D%E5%BA%94%E6%8A%A5%E6%96%87%E8%A7%A3%E5%AF%86%E8%BF%87%E7%A8%8B)响应报文解密过程

若请求进行了加密，且API对响应结果定义为需要加密，则YOP会对返回给商户的响应结果进行加密，商户收到后需要对响应结果进行解密。目前，加密响应结果的对称密钥与加密请求时的一样。故响应头`x-yop-encrypt`中的对称密钥值部分为空，直接用加密请求报文的密钥进行解密即可。