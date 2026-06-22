# Java SDK 报错信息说明

> 依赖与配置权威说明见 `SDK使用说明.md`；HTTP 204/503 概念见 `工具与支持/常见问题.md`；沙箱网关见 `沙箱环境联调测试.md`。

商户使用 YOP Java SDK 时，先按**对接阶段**定位，再按**异常类型/日志关键词**查表。

## 一、对接阶段与报错类型

| 阶段 | 典型动作 | 常见报错类型 |
| --- | --- | --- |
| 初始化 | ServiceLoader、`XxxClient` 构建 | 依赖、配置、类加载/SPI |
| 构造请求 | `XxxRequest`、`addParameter` | 参数 |
| 请求处理 | 签名/加密、选域名、HTTP 调用 | 依赖、配置、参数、网络 |
| 响应处理 | 验签、解密、反序列化 | 配置、业务、平台限制 |

---

## 二、依赖与打包问题

> Maven 坐标、软算法包（`crypto-gm` / `crypto-inter`）、BC 1.67 锁定见 `SDK使用说明.md` §二。

### 2.1 缺包典型日志

`YopCertParser not found`、`YopSigner not found`、`YopEncryptor not found`、`No YopHttpClientProvider found!` → 检查软算法包是否按密钥类型引入。

### 2.2 BouncyCastle 版本

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| `找不到符号 SM2Engine` | BC < 1.59 | 统一升至 **1.67** |
| `找不到符号 SM2Engine.Mode` | BC < 1.62 | 同上 |
| `NoClassDefFoundError: SM2P256V1Curve` | 冲突或版本过低 | `dependency:analyze` 排查，锁定 `bcprov-jdk15on`、`bcpkix-jdk15on` 均为 1.67 |

### 2.3 shade 包与依赖冲突

**sentinel / jackson / apache 冲突**时，推荐：

1. 业务包 `yop-java-sdk-biz`：保留，`exclusion *:*` 排除传递依赖。
2. 基础包 `yop-java-sdk`：使用 `<classifier>shade</classifier>`，同样 `exclusion *:*`。
3. 单独引入 BC 1.67 两个包。

**禁止**：已引 shade 包后又引入被 shade 的原始依赖（如重复 jackson），会导致配置文件读取错乱。

业务 SDK 源码集成：须同时引入 `yop-java-sdk` + `crypto-inter` + `crypto-gm`（按密钥类型），业务 SDK 只含业务 DTO/Client，**不能**替代基础 SDK。

### 2.4 JDK 6/7 额外依赖

SSL 握手失败（JDK 7）时，除升级 JDK 外可引入：

```xml
<dependency>
  <groupId>org.bouncycastle</groupId>
  <artifactId>bctls-jdk15on</artifactId>
  <version>1.67</version>
</dependency>
```

JDK 8u161 之前若报密钥长度限制，需安装 JCE unlimited policy；更高版本 JDK 默认已放开。

### 2.5 JDK 9+ 反射与 Jackson

JDK 17 等若报 `module java.base does not "opens java.io"` 或 Jackson `JsonMappingException`，启动参数添加：

```text
--add-opens java.base/java.lang.reflect=ALL-UNNAMED
```

### 2.6 SPI 被 APM 探针干扰（Pinpoint 等）

SDK 4.4.14+ 已集成 `YopSdkInitUtils`。主类添加：

```java
static {
    com.yeepay.yop.sdk.utils.YopSdkInitUtils.loadSpiClasses();
}
```

---

## 三、配置问题

> 配置文件结构、多 AppKey、超时、代理、域名见 `SDK使用说明.md` §三。

### 3.1 配置文件踩坑

- 指定 `-Dyop.sdk.config.env=qa` 时，须在 `classpath:config/qa/` 下存在对应配置；**勿只设 env 却不放文件**。
- 生产/内测：**不要**误设 `yop.sdk.config.env`；若必须设，生产用 `prod`。

### 3.2 联调测试环境（≤4.3.3 常见踩坑）

调用 QA/测试网关且验签失败时，build Client **之前**：

```java
System.setProperty("yop.sdk.config.env", "qa");
```

或覆盖 `server_root` / `preferred_server_roots` / `yos_server_root`（见 `沙箱环境联调测试.md`）。

### 3.3 沙箱模式

任选其一（系统初始化、build Client 之前）：

```java
System.setProperty("yop.sdk.mode", "sandbox");
System.setProperty("yop.sdk.config.env", "qa");
```

### 3.4 多 AppKey 切换

单笔请求指定身份：`request.getRequestConfig().setAppKey("your_appkey")`。

自实现密钥加载须三步：实现 Provider → 启动时注册 Registry → 请求级 `setAppKey`。

### 3.5 Provider 配套

自实现 `YopSdkConfigProvider` 时，**必须**配套自实现 `YopCredentialsProvider`，否则私钥/平台证书自动加载失败。

### 3.6 Nginx 反代

经 Nginx 转发时，SDK 配置的 root 填 Nginx 地址，由 Nginx 反代到 `openapi.yeepay.com` 等；健康检查：`curl -i http://nginx地址/sandbox/metrics/healthcheck` 应返回 200。

### 3.7 关闭故障上报

配置文件：

```json
"yop_report": { "enable": false }
```

---

## 四、业务 SDK 特有问题

### 4.1 升级后找不到类（V2 命名）

2024 年前后部分接口 Model 生成规则调整，类名/方法名带 `V2` 后缀。示例：

| 旧 | 新 |
| --- | --- |
| `MerClient#registerContributeMicro` | `registerContributeMicroV2` |
| `RegisterContributeMicroRequest` | `RegisterContributeMicroV2Request` |
| `FrontcashierClient#bindcardRequest_0` | `bindcardRequestV2` |

处理：重新从开发者中心下载业务 SDK，全局替换旧类名；或对照编译错误逐项改 import。

### 4.2 接口动态参数（2024-09-15 后业务 SDK）

文档未收录的新增字段，可直接：

```java
request.addParam("newField", value);           // form
xxxModel.addParam("newField", value);          // json 嵌套
Object ext = responseModel.get_extParam("newField");
Map<String, Object> all = responseModel.get_extParamMap();
```

### 4.3 手动改业务 SDK 参数

1. 按 `apiUri` 找到 `XxxRequestMarshaller`；
2. 改 `XxxRequest` 增字段与 getter/setter；
3. 在 `marshall` 中写入 `internalRequest`。

### 4.4 老版 API 代码生成

响应复杂 Object 缺 `dto_class_name` 会导致生成代码编译失败——重新拉取最新业务 SDK 或改用手工 DTO。

---

## 五、网络与 HTTP 异常

| 现象 | 排查 |
| --- | --- |
| `Connection refused` | `server_root`/`yos_server_root` 错误；本机网络；防火墙 |
| `UnknownHostException` | 域名拼写；DNS；内网须走代理 |
| `Read timed out` | 调大 read_timeout；查运维侧网关耗时 |
| `ConnectionPoolTimeoutException` | 连接池耗尽，检查并发与 Client 复用 |
| HTTP **204** / **503** | 概念与常见成因见 `工具与支持/常见问题.md`；204 另查 apiUri 与 server_root 拼接 |

连通性自检：

```bash
curl -i https://openapi-a.yeepay.com/yop-center/metrics/healthcheck
curl -i https://openapi-h.yeepay.com/yop-center/metrics/healthcheck
```

---

## 六、异常类型与日志关键词

### 6.1 `YopClientException`（客户端）

| 分类 | 日志关键词 | 排查要点 |
| --- | --- | --- |
| 商户私钥 | `Can't init ISV private key`、`No cert config found`、`can not find private key for appKey` | `isv_private_key` 格式、appKey 匹配、store_type |
| 易宝公钥 | `Can't init YOP public key`、`response sign verify failure` | 环境公钥是否匹配（生产/沙箱/QA） |
| 签名/加密 | `sign fail`、`verifySign fail`、`rsa encrypt failed`、`error happened when decrypt` | 密钥对错、算法 RSA/SM 是否与配置一致 |
| 参数 | `parameter name: should not be empty`、`can't be null`、`Unexpected file parameter type` | addParameter / addMultiPartFile |
| HTTP | `Unable to execute HTTP request`、`Unknown HTTP method`、`content should not be empty` | 方法、body、编码 UTF-8 |
| 回调 | `unsupported content Type for YopCallback`、`no YopCallbackHandler found` | 注册 Handler；Content-Type |
| 配置加载 | `Can't load config, file:` | 路径、JSON 格式、重复 shade 包 |
| 类加载 | `YopCertParser not found`、`YopDigester not found` | 软算法包、SPI 初始化 |
| 其他 | `No credentials specified`、`unable to deserialize stringResult` | 凭证未绑定；响应体非预期 JSON |

### 6.2 `VerifySignFailedException`

| 日志 | 含义 |
| --- | --- |
| `response sign verify failure, content:..., requestId:...` | 同步响应验签失败：易宝公钥环境错误或响应被篡改 |
| `Unexpected signature` / `Illegal format` | 回调验签：密文格式或签名段错误 |

### 6.3 `YopServiceException`（服务端/网关）

关注 `subCode`；**40044** 查接口业务错误码，**40029** 等查 `平台错误码说明.md`。

### 6.4 获取 `yop-request-id`（联系技术支持必备）

| 场景 | 获取方式 |
| --- | --- |
| 正常响应 | `response.getMetadata().getYopRequestId()` |
| `YopClientException` | 异常消息中通常已打印 |
| `YopServiceException` | `exception.getRequestId()` |
| 其他异常 | 提供完整堆栈 |

---

## 七、日志配置

SDK 使用 SLF4J。**勿同时引入多个 SLF4J 绑定**（会报 `multiple SLF4J bindings`）。

联调建议将 `com.yeepay`、`org.apache` 设为 DEBUG（Logback / Log4j2 均可）。详见 SDK 仓库 README。

---

## 八、v2 / v3 鉴权协议差异（自研网关必读）

SDK 4.x 默认 v3，与 v2 主要差异：

1. 请求头增加 `x-yop-content-sha256`（GET 对空串；POST JSON 对 body；POST form 对**排序后**非文件参数拼接，无参数时对 `""` 计算，**不能**直接返回空串跳过）。
2. Authorization 待签名字段集合变化（含 `content-length`、`x-yop-appkey` 等）。
3. POST form 签名时 CanonicalQueryString 按空串处理（因摘要已单独计算）。

自研实现见 `平台规范/安全认证/请求签名协议.md`；完整规则见 `平台规范/安全认证/鉴权认证机制(RSA).md` / `鉴权认证机制(SM).md`。

---

## 九、快速对照表（高频案例）

| 商户现象 | 优先检查 |
| --- | --- |
| 仅测试环境验签失败 | `yop.sdk.config.env=qa` 或 server_root 指向测试网关 |
| 生产验签失败 | 是否误设 env；易宝公钥是否生产环境 |
| 升级 SDK 后编译失败 | 业务 SDK 是否同步下载；类名 V2 |
| 依赖冲突 / 类找不到 | shade 包姿势；排除传递依赖 |
| 回调解密失败 | `结果通知机制说明.md` + `结果通知(RSA).md` / `结果通知(SM2).md`；非 SDK 用 `scripts/rsa/decrypt_notify.py` 或 `scripts/sm/decrypt_notify.py` |
| 超时 | 单笔 timeout > 全局；查单后再重试写操作 |
