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

## 认证解密

### 推荐路径

| 方式 | 文档 |
| --- | --- |
| 结果通知网关 | `工具与支持/开发工具/结果通知工具.md` |
| Java SDK | `开始对接/SDK使用说明.md` §六（`YopCallbackEngine` + 注册 `YopCallbackHandler`） |

### 自实现要点

1. **验签**：校验 `x-yop-content-sm3` 与 body 摘要一致；`Authorization` 验签规则见 `鉴权认证机制(SM).md`。平台证书按 `x-yop-sign-serial-no` 查询（接口 `/rest/v2.0/yop/platform/certs`）。
2. **解密**：解析请求头 `x-yop-encrypt`（`yop-encrypt-v1` + SM4/CBC/PKCS5Padding）；商户 SM2 私钥解对称密钥，再解 JSON body。报文加密细节见 `报文加密机制(SM).md`（manifest 已索引）；非 SDK 见同目录 `回调解密协议.md`。
3. **Base64**：平台采用 URL 安全 Base64（`+`/`/` → `-`/`_`），解码前须还原。

## 应答报文

成功应答标准见 `结果通知机制说明.md` §四：HTTP 200 + `{"result":"SUCCESS"}` + 响应头 `x-yop-sign`（SDK 的 `YopCallbackEngine.handle` 可自动签名应答）。

处理失败返回 4xx/5xx 将触发平台重试。

## 通用机制与排障

notifyUrl、重试、幂等、查单兜底见 `结果通知机制说明.md`。验签/解密失败见 `../../../troubleshooting.md` §二。
