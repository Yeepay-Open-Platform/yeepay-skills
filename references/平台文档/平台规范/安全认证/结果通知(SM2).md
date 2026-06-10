# SM2数字信封加密+签名的结果通知

对于仅向YOP平台报备了SM2证书的商户，YOP平台使用商户报备的商户证书做数字信封加密然后使用YOP平台证书对通知内容进行签名的流程对通知内容进行处理。若您是使用Java进行开发的商户，我们在Java版sdk中提供了相应的解密的工具类。

## [](https://open.yeepay.com/docs-v3/platform/14023.md#%E9%80%9A%E7%9F%A5%E6%8A%A5%E6%96%87%E7%A4%BA%E4%BE%8B)通知报文示例

商户端接收到的通知报文如下：(content-type为application/json)

请求头：其中 `x-yop-content-sm3`是对请求体中的内容计算摘要，为16进制编码

```
content-length : 109
x-yop-content-sm3:e48ba8b36a206edb80d869883cfa2d2f13be90d162505e684ec0c3b978f7789f
authorization:YOP-SM2-SM3 yop-auth-v3/app_100276759800069/2022-07-11T10:42:33Z/43200/content-length;content-type;x-yop-content-sm3;x-yop-encrypt;x-yop-request-id/9IFlijcEIMHao7cvY_vT9sab5foPofxcWJ4RsmdqHqxRzVqOwW2lZWyxJ0VZG_hQQhjoSDJOm5TNjYO3ID8teQ$SM3
x-yop-encrypt:yop-encrypt-v1/289799549289/SM4_CBC_PKCS5Padding/BDr0cE1oKuJWGDlXWHLJOUTsuclHjy69a93ykX9n2dvhI14Yfk0Bq6NqtvGUG6mPwbOikT6hcUFXflnxuq_1b6HW7KashWlnkfsZpv5MVi3U7USYgQ4q5Yuxyv4c-zoiJ1fCGdj_gGBZvhr1w2RJlbw/pEdbp94uPmyw-2xcSIKW2A;eW9w/stream//JA
x-yop-sign-serial-no:4379555845
x-yop-request-id:test1657530870560
x-yop-appkey:app_100276759800069
content-type:application/json
```

请求体：(此处为加密(`SM4/CBC/PKCS5Padding`)、编码(urlSafeBase64)后的通知报文)

```
LBP09kWnN13p69ENTjmLJNPn1scK__ai1Fa29eFyFJ6DsOyP0MR7aqZrZnXpGeDwRyrOVWfWIjvBpTXaNvcLIfNzX1W9s-D4apZveNYYsYc
```

## [](https://open.yeepay.com/docs-v3/platform/14023.md#%E6%8A%A5%E6%96%87%E6%8E%A5%E6%94%B6%E7%A4%BA%E4%BE%8B)报文接收示例

此处基于java web服务，使用servlet进行接收

```
// 解析HttpServletRequest, 获取原始通知报文
public String parse(HttpServletRequest req) throws IOException {
    final String contentTypeStr = req.getContentType();
    if (!StringUtils.startsWith(contentTypeStr, "application/json")) {
    	throw new IllegalArgumentException("SM2回调请求仅支持json格式");
    }
    String reqMethod = req.getMethod();
    String reqURI = req.getRequestURI();
    Map&lt;String, String&gt; reqHeaders = getHeaders(req);
    String jsonReqBody = org.apache.commons.io.IOUtils.toString(req.getInputStream(), "UTF-8");
    // 根据请求头、请求体，进行验签认证、解密等后续操作
}

// 获取请求头
private Map&lt;String, String&gt; getHeaders(HttpServletRequest request) {
    Map&lt;String, String&gt; result = Maps.newHashMap();
    final Enumeration&lt;String&gt; headerNames = request.getHeaderNames();
    while (headerNames.hasMoreElements()) {
        final String headerName = headerNames.nextElement();
        final String headerValue = request.getHeader(headerName);
        result.put(headerName, headerValue);
    }
    return result;
}
```

## [](https://open.yeepay.com/docs-v3/platform/14023.md#%E8%AE%A4%E8%AF%81%E8%A7%A3%E5%AF%86%E7%A4%BA%E4%BE%8B)认证解密示例

### [](https://open.yeepay.com/docs-v3/platform/14023.md#%E4%BD%BF%E7%94%A8%E2%80%9C%E7%BB%93%E6%9E%9C%E9%80%9A%E7%9F%A5%E5%BF%AB%E9%80%9F%E5%AF%B9%E6%8E%A5%E7%BD%91%E5%85%B3%E2%80%9D%E7%AE%80%E5%8C%96%E5%AF%B9%E6%8E%A5%EF%BC%88%E6%8E%A8%E8%8D%90%EF%BC%89)使用“结果通知快速对接网关”简化对接（推荐）

目前我们提供了 Java 语言的“结果通知快速对接网关”工具，可以实现快速对接异步通知。具体参考 [商户通知快速对接网关](https://open.yeepay.com/docs-v3/platform/3842.md)

### [](https://open.yeepay.com/docs-v3/platform/14023.md#%E4%BD%BF%E7%94%A8sdk%E7%AE%80%E5%8C%96%E5%AF%B9%E6%8E%A5)使用sdk简化对接

若您使用了我们提供的Java-SDK，我们在SDK中提供解密结果通知的工具类，在对接之前，请先确保您正确配置了SDK，[参考Java-SDK配置](https://open.yeepay.com/docs/open/platform-doc/sdk_guide-sm/java-sdk-guide-sm#%E5%9B%9B-SDK%E9%85%8D%E7%BD%AE)

```
//引入工具类

import com.yeepay.yop.sdk.service.common.YopCallbackEngine;
import com.yeepay.yop.sdk.service.common.callback.YopCallbackRequest;
import com.yeepay.yop.sdk.http.YopContentType;
import com.yeepay.yop.sdk.service.common.callback.YopCallback;

/**
 * 基于上一步接收到的原始报文，解密后得到业务数据
 * 
 * @param reqMethod 请求方法，如POST
 * @param reqURI 请求路径, 如/rest/xxx，不包含query参数
 * @param reqHeaders 请求头
 * @param jsonReqBody json请求体
 */
public String decryptSm2Callback(String reqMethod, String reqURI, 
    Map&lt;String, String&gt; reqHeaders, String jsonReqBody) {
    YopCallbackRequest callbackReq = new YopCallbackRequest(reqURI, reqMethod)
            .setContentType(YopContentType.JSON)
            .setHeaders(reqHeaders).setContent(jsonReqBody);

    YopCallback callback = YopCallbackEngine.parse(callbackReq);
    return callback.getBizData();
}
```

### [](https://open.yeepay.com/docs-v3/platform/14023.md#%E8%87%AA%E5%AE%9E%E7%8E%B0%E5%8F%82%E8%80%83%E5%A6%82%E4%B8%8B)自实现参考如下

#### [](https://open.yeepay.com/docs-v3/platform/14023.md#%E8%AE%A4%E8%AF%81)认证

##### [](https://open.yeepay.com/docs-v3/platform/14023.md#%E5%86%85%E5%AE%B9%E6%91%98%E8%A6%81%E9%AA%8C%E8%AF%81)内容摘要验证

使用body中的内容计算sm3摘要，与header x-yop-content-sm3做比较，若不相同，说明通知内容可能已被篡改。验证签名。

**a.调用平台证书查询接口查询用于验签到平台证书。** 详情见 [获取平台证书列表](https://open.yeepay.com/docs-v3/platform/2479.md)

```
平台证书查询接口uri: /rest/v2.0/yop/platform/certs
content-type:
参数：
appId=app_100276759800069
certType=SM2
serialNo=4379555845 //通知报文中的请求头x-yop-sign-serial-no
```

**b.构造验签原文** 详情见 [鉴权认证机制](https://open.yeepay.com/docs-v3/platform/3838.md)

```
以上文为例，您收到的认证头为
authorization : YOP-SM2-SM3 yop-auth-v3/app_100276759800069/2022-07-11T10:42:33Z/43200/content-length;content-type;x-yop-content-sm3;x-yop-encrypt;x-yop-request-id/9IFlijcEIMHao7cvY_vT9sab5foPofxcWJ4RsmdqHqxRzVqOwW2lZWyxJ0VZG_hQQhjoSDJOm5TNjYO3ID8teQ$SM3
```

```
以上文通知报文为例，得到的签名原文如下：
yop-auth-v3/app_100276759800069/2022-07-11T09:14:31Z/43200
POST
/notify/uri

content-length:109
content-type:application%2Fjson
x-yop-content-sm3:821d8c55604eee3eb711f9977279889e65cb50658663b5ea4ed88a16ca76949e
x-yop-encrypt:yop-encrypt-v1%2F%2FSM4_CBC_PKCS5Padding%2FBMsnszaP8E1GJhax13HmB8gsUSHllhfhAWwtqGAOI7K8fL1SywxBQkxr3vErKZOswoioak1OETLHnpkjhU7qcB7FWzooGVeaA6htdpzphhuNlxg1upA2ZaSYxzok5rBC8nO6_GBFqPH7tyXVo3T47Xc%2FIqSmBreCIkaIbDu8L2a9wA%3BeW9w%2Fstream%2F%2FJA
x-yop-request-id:test1657530870560
```

**c.验证签名**

在步骤a中得到了平台公钥，步骤b得到签名，步骤c得到了原文，使用这些参数进行验签，若验签失败说明通知内容被篡改。

#### [](https://open.yeepay.com/docs-v3/platform/14023.md#%E8%A7%A3%E5%AF%86)解密

YOP平台采用了数字信封技术做通知内容加密，即随机对称密钥加密通知内容，商户公钥加密随机密钥。加密信息通过header x-yop-encrypt传递给商户。详情见 [报文加密机制](https://open.yeepay.com/docs-v3/platform/3926.md)

```
以上文通知报文为例：
x-yop-encrypt : yop-encrypt-v1/4379663169/SM4_CBC_PKCS5Padding/BDr0cE1oKuJWGDlXWHLJOUTsuclHjy69a93ykX9n2dvhI14Yfk0Bq6NqtvGUG6mPwbOikT6hcUFXflnxuq_1b6HW7KashWlnkfsZpv5MVi3U7USYgQ4q5Yuxyv4c-zoiJ1fCGdj_gGBZvhr1w2RJlbw/pEdbp94uPmyw-2xcSIKW2A;eW9w/stream//JA
加密协议版本：yop-encrypt-v1
服务端证书序列号：4379663169
加密密钥类型：SM4
分组模式：CBC
填充算法：PKCS5Padding
// 加密密钥是被商户的SM2公钥进行加密的密文，该密文进行的urlSafeBase64编码
加密密钥：BDr0cE1oKuJWGDlXWHLJOUTsuclHjy69a93ykX9n2dvhI14Yfk0Bq6NqtvGUG6mPwbOikT6hcUFXflnxuq_1b6HW7KashWlnkfsZpv5MVi3U7USYgQ4q5Yuxyv4c-zoiJ1fCGdj_gGBZvhr1w2RJlbw
// iv即对称加密同志内容时使用的随机向量（进行了urlSafeBase64编码）
iv：pEdbp94uPmyw-2xcSIKW2A
```

##### [](https://open.yeepay.com/docs-v3/platform/14023.md#1.%E4%BD%BF%E7%94%A8%E5%95%86%E6%88%B7%E7%A7%81%E9%92%A5%E8%A7%A3%E5%AF%86%E8%8E%B7%E5%BE%97%E5%AF%B9%E7%A7%B0%E5%8A%A0%E5%AF%86%E5%AF%86%E9%92%A5)1.使用商户私钥解密获得对称加密密钥

解密过程如下：decodeBase64表示进行Base64解码，sm2Decrypt表示使用sm2私钥进行解密。

```
String cipherKey = "BDr0cE1oKuJWGDlXWHLJOUTsuclHjy69a93ykX9n2dvhI14Yfk0Bq6NqtvGUG6mPwbOikT6hcUFXflnxuq_1b6HW7KashWlnkfsZpv5MVi3U7USYgQ4q5Yuxyv4c-zoiJ1fCGdj_gGBZvhr1w2RJlbw";
// 服务端序列号4379663169 对应的私钥
String priKey = "XXX";
byte[] key = sm2Decrypt(priKey,decodeBase64(cipherKey));
```

**注意**：

-   平台BASE64编码采用的URL安全模式(将非法字符'+'和'/'转为'-'和'_', 见RFC3548)，部分语言解码时须先进行手动替换还原，伪代码示例：`$data.replaceAll("-", "+").replaceAll("_", "/")`

##### [](https://open.yeepay.com/docs-v3/platform/14023.md#2.%E4%BD%BF%E7%94%A8%E5%AF%B9%E7%A7%B0%E5%8A%A0%E5%AF%86%E5%AF%86%E9%92%A5%E8%A7%A3%E5%AF%86%E8%8E%B7%E5%BE%97%E6%95%B0%E6%8D%AE%E6%98%8E%E6%96%87)2.使用对称加密密钥解密获得数据明文

解密过程如下：sm4CBCPkcs5paddingDecrypt表示sm4算法CBC分组模式，Pkcs5padding填充模式的解密过程。

```
// body中的内容
String cipherData = "LBP09kWnN13p69ENTjmLJNPn1scK__ai1Fa29eFyFJ6DsOyP0MR7aqZrZnXpGeDwRyrOVWfWIjvBpTXaNvcLIfNzX1W9s-D4apZveNYYsYc";
// key为上一步获得的值
byte[] data = sm4CBCPkcs5paddingDecrypt(key,decodeBase64(cipherData));
```

## [](https://open.yeepay.com/docs-v3/platform/14023.md#%E5%BA%94%E7%AD%94%E6%8A%A5%E6%96%87%E7%A4%BA%E4%BE%8B)应答报文示例

正常处理的应答标准：

\> 状态码：200 > 报文头：对报文体签名后，放`x-yop-sign`里 > 报文体：`{"result":"SUCCESS"}`（JSON格式）

报文示例：

```
HTTP/1.1 200 
Server: xxx
Date: xxx
Content-Type: application/json
Content-Length: 20
Connection: keep-alive
x-yop-sign: ygTa1ebQEL_nGM9hSP3r5eBDT8Jk9OpEP-1SZy1wm7QR6564VcU_nBXLalnEIBMs_H7kQsoYsNoWiP_QPGZ6zw
X-Frame-Options: SAMEORIGIN
X-XSS-Protection: 1; mode=block

{"result":"SUCCESS"}
```

SDK代码示例：SDK会自动处理响应签名

```
//import com.google.common.collect.Maps;
//import com.yeepay.yop.sdk.YopConstants;
//import com.yeepay.yop.sdk.http.YopContentType;
//import com.yeepay.yop.sdk.service.common.YopCallbackEngine;
//import com.yeepay.yop.sdk.service.common.callback.YopCallbackRequest;
//import com.yeepay.yop.sdk.service.common.callback.YopCallbackResponse;
//import com.yeepay.yop.sdk.constants.CharacterConstants;
//import org.apache.commons.collections4.MapUtils;
//import org.apache.commons.io.IOUtils;
//import org.apache.commons.lang3.StringUtils;

// 前提：自定义业务处理handler
@Component
public class MockCallbackHandler implements YopCallbackHandler {

    private static final Logger LOGGER = LoggerFactory.getLogger(MockCallbackHandler.class);

    @PostConstruct
    public void init() {
        YopCallbackHandlerFactory.register(getType(), this);
    }

    @Override
    public String getType() {
        // 注意：此处需与下面的 getCallbackType 保持一致
        return "/xxx";
    }

    @Override
    public void handle(YopCallback callback) {
        LOGGER.debug("mock notify handle:{}", callback);
        String bizData = callback.getBizData();
        // 业务处理示例：bizData 为解密后的业务报文 json
    }
}

// 主流程逻辑如下：
String respStr = "";
try {
    YopCallbackRequest callbackRequest = resolve(req);
    YopCallbackResponse callbackResponse = YopCallbackEngine.handle(callbackRequest);

    if (null != callbackResponse) {
        respStr = callbackResponse.getBody();
    }

    if (MapUtils.isNotEmpty(callbackResponse.getHeaders())) {
        callbackResponse.getHeaders().forEach(resp::addHeader);
    }
    resp.setContentType(callbackResponse.getContentType().getValue());
    resp.getOutputStream().write(respStr.getBytes(YopConstants.DEFAULT_ENCODING));
} catch (Exception e) {
    LOGGER.error("error when handle yop callback", e);
    resp.sendError(
            HttpServletResponse.SC_INTERNAL_SERVER_ERROR,
            e.getMessage());
}

private YopCallbackRequest resolve(HttpServletRequest req) throws IOException {
    final String contentTypeStr = req.getContentType();
    Object content = null;
    YopContentType contentType;
    if (StringUtils.startsWith(contentTypeStr, YOP_HTTP_CONTENT_TYPE_JSON)) {
        contentType = YopContentType.JSON;
        content = IOUtils.toString(req.getInputStream(), YopConstants.DEFAULT_ENCODING);
    } else {
        contentType = YopContentType.FORM_URL_ENCODE;
    }
    return new YopCallbackRequest(getCallbackType(req), req.getMethod())
            .setContentType(contentType)
            .setHeaders(getHeaders(req)).setParams(getParams(req)).setContent(content);
}

private String getCallbackType(HttpServletRequest req) {
    // 每个回调地址，对应一种通知类型
    return req.getRequestURI();
}

private Map&lt;String, String&gt; getHeaders(HttpServletRequest request) {
    Map&lt;String, String&gt; result = Maps.newHashMap();
    final Enumeration&lt;String&gt; headerNames = request.getHeaderNames();
    while (headerNames.hasMoreElements()) {
        final String headerName = headerNames.nextElement();
        final String headerValue = request.getHeader(headerName);
        result.put(headerName, headerValue);
    }
    return result;
}

private Map&lt;String, List&lt;String&gt;&gt; getParams(HttpServletRequest request) {
    Map&lt;String, List&lt;String&gt;&gt; result = Maps.newHashMap();
    Map&lt;String, String[]&gt; params = request.getParameterMap();
    for (Map.Entry&lt;String, String[]&gt; param : params.entrySet()) {
        result.put(param.getKey(), Arrays.asList(param.getValue()));
    }
    return result;
}
```

无SDK代码示例：须自行实现签名编码(可参考SDK代码)

```
// 构造应答报文
String respBody = "{\"result\":\"SUCCESS\"}";
HttpServletResponse resp;
resp.addHeader("x-yop-sign", encodeUrlSafeBase64(sign(respBody.getBytes("UTF-8"))));
// 注意：此处为测试环境国密证书，生产环境请联系技术支持获取
resp.addHeader("x-yop-sign-serial-no", "4059376239");
resp.setContentType("application/json");
resp.getOutputStream().write(respBody.getBytes("UTF-8"));
```

异常处理的应答方式：

\> 状态码：500或4xx > 报文体：任意 >
