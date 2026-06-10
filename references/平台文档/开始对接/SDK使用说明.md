# Java SDK 使用说明（yop-java-sdk）

> 其他语言见 `工具与支持/开发工具/平台SDK.md` 仓库 README。不使用 SDK 见 `示例代码/后端代码/` 协议文档。

## 一、环境要求

- JDK 1.8+
- Maven 3.x 或 Gradle

## 二、引入依赖

使用 [Maven Central](https://search.maven.org/search?q=g:com.yeepay.yop.sdk%20a:yop-java-sdk) **最新稳定版**。

```xml
<dependency>
  <groupId>com.yeepay.yop.sdk</groupId>
  <artifactId>yop-java-sdk</artifactId>
  <version><!-- 最新稳定版 --></version>
</dependency>
```

```groovy
implementation 'com.yeepay.yop.sdk:yop-java-sdk:<最新稳定版>'
```

功能门槛：多域名路由需 SDK `4.4.1` 及以上。

## 三、配置文件

默认路径：`classpath:/config/yop_sdk_config_default.json`。

```json
{
  "app_key": "YOUR_APP_KEY",
  "isv_private_key": { "value": "YOUR_PRIVATE_KEY_BASE64" },
  "yos_server_root": "https://yos.yeepay.com/yop-center",
  "preferred_server_roots": ["https://openapi.yeepay.com/yop-center"],
  "http_client": {
    "connect_timeout": 10000,
    "read_timeout": 30000
  }
}
```

自定义路径：JVM 参数 `-Dyop.sdk.config.file=file:///path/to/yop_sdk_config.json`（Tomcat/Jetty 等写入 `JAVA_OPTS`）。

沙箱网关与 `withEnv("sandbox")` 见 `沙箱环境联调测试.md`。

## 四、YopClient 单例

```java
// 线程安全，全局单例，每个环境一套
private static final YopClient client = YopClientBuilder.builder().build();
```

## 五、四种请求姿势

### 1. GET

```java
YopRequest request = new YopRequest("/rest/v1.0/trade/order/query", "GET");
request.addParameter("merchantNo", "100xxx");
request.addParameter("orderId", "ORDER_xxx");
YopResponse response = client.request(request);
```

### 2. POST Form（application/x-www-form-urlencoded）

```java
YopRequest request = new YopRequest("/rest/v1.0/aggpay/pre-pay", "POST");
request.addParameter("merchantNo", "100xxx");
request.addParameter("orderId", "ORDER_xxx");
request.addParameter("orderAmount", "0.01");
YopResponse response = client.request(request);
```

### 3. POST JSON

```java
YopRequest request = new YopRequest("/rest/v1.0/xxx/json-api", "POST");
Map<String, Object> body = new HashMap<>();
body.put("field", "value");
request.setContent(JsonUtils.toJsonString(body));
YopResponse response = client.request(request);
```

### 4. 文件上传 / 下载

```java
// 上传
request.addMultiPartFile("_file", inputStream);
YosUploadResponse uploadResp = client.upload(request);

// 下载
YosDownloadResponse downloadResp = client.download(request);
YosDownloadInputStream in = downloadResp.getResult();
```

> 逐接口参数以 doc_md「请求参数」表为准；「示例代码」节为全参数模板，**只取调用骨架**，见 SKILL.md 纪律。

## 六、回调验签

结果通知为四段密文（`encRandomKey$encData$AES$SHA256`），商户侧：

1. 商户私钥 RSA 解随机密钥 → AES 解数据 → 拆出明文与签名。
2. 易宝公钥 `SHA256withRSA` 验签。

规则详见 `平台规范/安全认证/结果通知(RSA).md`；不使用 SDK 时见 `示例代码/后端代码/回调解密协议.md`，可用 `scripts/decrypt_notify.py` 本地验证。

## 七、异常与超时

| 类型 | 处理建议 |
|------|----------|
| 网络超时 | 先查单确认状态，再决定是否重试；写操作必须幂等 |
| 验签失败 | 核对密钥、环境（沙箱/生产）、网关地址 |
| 业务错误码 | 先看接口 doc_md 错误码，再看 `平台错误码说明.md` |
| SDK 配置错误 | 检查 app_key、私钥格式、`-Dyop.sdk.config.file` 路径 |

超时在 `yop_sdk_config_default.json` 的 `http_client` 段配置；生产建议 connect 10s、read 30s，按业务调整。
