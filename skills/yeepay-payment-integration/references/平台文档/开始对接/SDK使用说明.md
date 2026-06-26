# Java SDK 使用说明（yop-java-sdk）

> 其他语言见 `工具与支持/开发工具/平台SDK.md` 仓库 README。不使用 SDK 见 `平台规范/安全认证/` 下的请求签名协议/回调解密协议。

## 一、环境要求

- JDK 1.8+
- Maven 3.x 或 Gradle

## 二、引入依赖

生成 `pom.xml` / `build.gradle` 前须**实时解析**最新稳定版，禁止凭记忆或旧文档硬编码。

| 方式 | 用法 |
|------|------|
| 浏览器（推荐） | [Maven Central · yop-java-sdk](https://central.sonatype.com/artifact/com.yeepay.yop.sdk/yop-java-sdk) 页面 Versions 列表 |
| 命令行（推荐） | `cd scripts && python tools/resolve_java_sdk_version.py` |
| curl | 见下方「版本解析协议」 |

> **勿用** `search.maven.org` 查版本（索引滞后）。**勿用** `central.sonatype.com/solrsearch` 且不带 `sort=v desc`（会误返回 `4.2.2-jdk6on` 等旧版）。

### 版本解析协议

```text
1. 命令行（优先）：cd scripts && python tools/resolve_java_sdk_version.py
2. curl（central.sonatype.com Solr，须 sort=v desc）：
   curl -sS 'https://central.sonatype.com/solrsearch/select?q=g:com.yeepay.yop.sdk+AND+a:yop-java-sdk&rows=1&wt=json&sort=v%20desc'
   取 response.docs[0].v
3. 回退：repo1.maven.org maven-metadata.xml 的 <release> 节点
4. 软算法包（yop-java-sdk-crypto-gm / yop-java-sdk-crypto-inter）版本与主包一致
```

```xml
<dependency>
  <groupId>com.yeepay.yop.sdk</groupId>
  <artifactId>yop-java-sdk</artifactId>
  <version><!-- 按版本解析协议实时获取 --></version>
</dependency>
```

```groovy
implementation 'com.yeepay.yop.sdk:yop-java-sdk:<按版本解析协议实时获取>'
```

功能门槛：多域名路由需 SDK `4.4.1` 及以上。

### 软算法包（4.3.0+，未对接加密机时必需）

主包不含签名/加密实现，须按密钥类型**额外**引入（版本与主 SDK 一致）：

```xml
<!-- 国密 -->
<dependency>
  <groupId>com.yeepay.yop.sdk</groupId>
  <artifactId>yop-java-sdk-crypto-gm</artifactId>
  <version><!-- 与 yop-java-sdk 同版本 --></version>
</dependency>
<!-- RSA -->
<dependency>
  <groupId>com.yeepay.yop.sdk</groupId>
  <artifactId>yop-java-sdk-crypto-inter</artifactId>
  <version><!-- 与 yop-java-sdk 同版本 --></version>
</dependency>
```

同时锁定 BouncyCastle：`bcprov-jdk15on`、`bcpkix-jdk15on` **1.67**。依赖冲突处理见 `Java-SDK报错说明.md` §二。

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

**多 AppKey**：`isv_private_key` 可为数组，每项可带 `app_key`；请求级 `request.getRequestConfig().setAppKey("...")` 切换身份。

**测试/QA 网关、沙箱模式、域名与代理**：见 `沙箱环境联调测试.md`、`Java-SDK报错说明.md` §3.2–3.3。

**指定单笔域名**：`request.getRequestConfig().setServerRoot("...")`。

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

通用机制（notifyUrl、重试、应答、幂等）见 `平台规范/结果通知机制说明.md`。

| 密钥类型 | 协议文档 | SDK 工具 |
| --- | --- | --- |
| RSA | `平台规范/安全认证/结果通知(RSA).md` | `DigitalEnvelopeUtils` 或 `YopCallbackEngine` |
| SM2 | `平台规范/安全认证/结果通知(SM2).md` | `YopCallbackEngine`（须注册 Handler 并应答签名） |

不使用 SDK：见 `平台规范/安全认证/回调解密协议.md`；本地验证 `scripts/rsa/decrypt_notify.py`。网关方案见 `工具与支持/开发工具/结果通知工具.md`。

## 七、异常与超时

| 类型 | 处理建议 |
|------|----------|
| 网络超时 | 先查单确认状态，再决定是否重试；写操作必须幂等 |
| 验签失败 | 见 `Java-SDK报错说明.md` §6.1–6.2 |
| 业务错误码 | 先看接口 doc_md 错误码，再看 `平台错误码说明.md` |
| SDK 配置错误 | 见 `Java-SDK报错说明.md` §三 |

超时在 `yop_sdk_config_default.json` 的 `http_client` 段配置（默认连接 10s、读取 30s）；单笔 `request.getRequestConfig().setReadTimeout(ms)` **优先于**全局配置。

排障时提取 `yop-request-id`：`response.getMetadata().getYopRequestId()`，或异常消息 / `YopServiceException.getRequestId()`。

完整报错案例库见 `Java-SDK报错说明.md`。
