# 报文加密机制(RSA)

本文适合的阅读人群

- 无 SDK 对接 API 的开发者
- YOP SDK 编写者

## 适用范围

此机制适用于安全需求为`YOP-RSA2048-SHA256`，有请求参数或响应结果有在传输过程中有加密需求的用户。可参考[示例demo](https://github.com/yop-platform/yop-java-sdk/blob/develop/yop-java-sdk-test/src/test/java/com/yeepay/yop/sdk/example/YopRsaEncryptExample.java)（支持get&form、post&form、post&json、get下载文件）

## 请求报文加密过程

加密信息通过请求头`x-yop-encrypt`传递。格式如下

{YOP加密协议版本(必填)}/{平台证书序列号(必填)}/{密钥类型(必填)}`_`{分组模式(必填)}`_`{填充算法(必填)}/{加密密钥值(必填)}/{IV}{;}{附加信息}/{客户端支持的大参数加密模式(必填)}/{encryptHeaders}/{encryptParams}

### 请求头各组成部分说明：

**{YOP加密协议版本}**：目前YOP的加密协议版本号为`yop-encrypt-v1`

**{平台证书序列号}**：用于加密AES密钥的平台商密证书的序列号。若加密类型为RSA时，该字段为**空字符串**。

**{密钥类型}`_`{分组模式}`_`{填充算法}**：目前可选`AES_ECB_PKCS5Padding`

**{加密密钥值}**：平台RSA公钥加密后进行urlSafeBase64编码的值

**{IV}{;}{附加信息}**：加密数据时的随机向量（进行urlSafeBase64编码）及附加信息，目前`AES_ECB_PKCS5Padding`中无附加信息，不填即可

**{客户端支持的大参数加密模式}**:目前支持stream（流式加密模式），故就填stream即可

**{encryptHeaders}**：加密请求参数之外还支持对请求头进行加密(YOP指定的请求头不能进行加密)，加密方式与加密form格式参数相同，若加密了请求头，此处为请求头名称，多个值之间用半角分号分隔，最后需要进行urlSafeBase64编码。

**{encryptParams}**：加密了的参数名称。若加密了form参数中的所有参数或加密了json格式的参数，则参数名称为$，否则多个值之间用半角分号分隔,最后最后对整体进行urlSafeBase64编码。

### 使用随机AES密钥加密请求参数

目前YOP支持加密算法为`AES/ECB/PKCS5Padding`。示例如下

使用的AES密钥为

```
// 为了便于展示，对密钥进行urlSafeBase64编码
AlRQyjbizp7NoIqp9C3Uig
```

```
// form格式传参，对参数idNo进行加密传输
// 请求参数明文值
String idNo = "123456789";

// 请求参数采用 AES/ECB/PKCS5Padding 算法模式加密后的值(进行了urlSafeBase64编码）
String encryptedIdNo = "vcd4Lql6101cAC8xmjQ2Jg";

// 调用API时传入加密后的参数值（params存放form格式的请求参数，与requestParameterMap的作用相同）
// params.put("idNo",encryptedIdNo);

// 将需要加密的请求头放入set集合，用于生成加密头
// encryptHeaders.add(xxx);

// 将需要加密的参数名称放入set集合，用于生成加密头
// encryptParams.add("idNo");

// 文件流加密 参考javax.crypto.CipherInputStream
```

```
// json格式传参，对整个json数据进行加密
String jsonRequest = "{\"appId\":\"app_1595815987915711\",\"alias\":\"alias_0329\"}";

// 加密后的json数据（进行了urlSafeBase64编码）
String encryptedJsonRequest = "uK2aKRPX-zD_SJObtQs8-G9XvxCOCS7UyZQk-XVEjCPVjNINsSYrGHQ7eu3GUzijIqKjJkV8UFKKk2vYEM_cPA";

// 将请求数据替换为加密后的数据
// jsonPayload.setContent(encryptedJsonRequest);

// 将需要加密的请求头放入set集合，用于生成加密头
// encryptHeaders.add(xxx);

// 将需要加密的参数名称放入set集合，用于生成加密头。目前json推荐整体加密
// encryptParams.add("$");
```

### 使用平台RSA公钥加密AES密钥

若要获取平台RSA公钥，请进入【[控制台](https://open.yeepay.com/developer-center)】->【我的应用】->【密钥配置】->【易宝公钥】，点击“查看公钥”获取。

加密过程具体可参考源码中的 [YopRsaEncryptor](https://github.com/yop-platform/yop-java-sdk/blob/develop/yop-java-sdk-crypto-inter/src/main/java/com/yeepay/yop/sdk/inter/security/encrypt/YopRsaEncryptor.java)。

### 构造请求头

上述示例中构造出的请求头分别为

```
// 对form格式中的参数idNo进行加密传输
yop-encrypt-v1//AES_ECB_PKCS5Padding/tJ3F5sQBVY4zJe-hSqKHsoSYDLBhRSDdWnNGHofF_jhpbPB4ZC4WK8Ot1GV2yJv2dNaDDBYjv8V47F8XyxK1RewthitpDwRJWQKNMMD4_Eaj_3TQsORBOMaXhuLY0Buc-_gY-yoSRbF4NOPqWe_mccEPh8Jn53ijZ6iCOUc-GWU_aaxIuPRmv4f2roXEfTNeVsNG6L4Uf9kCZHbyGvWyE_Ed_Ku4cu2p5j5Vms7jzqFakd53bYjKLzY2wbOlkCkk0YSnpXonbLtFNGU1VT9om4nNG-xUmzVdYMTmrLwsQdve0YuCGuAS5_8AQX0wZWccZLnbu7ghDG1f7Xx5LHNibw//stream//aWRObw
```

```
// 对json格式参数进行加密传输
yop-encrypt-v1//AES_ECB_PKCS5Padding/mz9f81mfJEG9QrfgYfLulvCaKYQiw9BiBwSs4GsO5nes-b_4fp8n_QnEZTpLtlkax7w-xtVW8kNLSd8egeGulsO5egwFKYVoXWtmVwQJf8tOr7g0RLOGkJcqM5oN66UB15Cjrsuwhx0R0kX5B0twmeA9AyXW4PRhl7eXWr4ST7K_P2-btHej-qe0-5lwe2B_f-x_BWMQVeOKJfD5H-humU7Ac2JPzJ_ZO3twEc_Q7ebe2-ZmCmzn2RM8ni6kvA5PwmXYSXoOUNTT_YlvNwL7u4dgf0TT7aPy06R9998fHxXFaXbwGGaz7PUh1HWwfz5zr-PA6UXwVNyTA2HxjTB8Zg//stream//JA
```

## 响应报文解密过程

若请求进行了加密，且API对响应结果定义为需要加密，则YOP会对返回给商户的响应结果进行加密，商户收到后需要对响应结果进行解密。目前，加密响应结果的对称密钥与加密请求时的一样。故响应头`x-yop-encrypt`中的对称密钥值部分为空，直接用加密请求报文的密钥进行解密即可。