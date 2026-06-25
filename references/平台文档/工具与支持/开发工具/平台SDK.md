# 平台 SDK

## 概述

易宝开放平台 SDK 封装请求签名、报文加密、响应解析与证书管理，降低对接成本。本 skill 中 **yop-java-sdk 为参考实现**（最规范，本地可校对源码）。

## 对接路径选择

写对接代码前，先确认客户**是否使用官方 SDK**：

| 路径 | 适用 | 知识来源 |
|------|------|----------|
| **使用 SDK** | 愿意引入官方 SDK | Java → `开始对接/SDK使用说明.md`；其他语言 → 下表仓库 README + doc_md 参数表 |
| **不使用 SDK** | 无官方 SDK、或主动不引依赖/自研网关/合规限制 | `平台规范/安全认证/` 请求签名协议/回调解密协议 + doc_md 参数表 + `scripts/` 本地验证 |

客户未声明时，列入「待确认」询问，**不默认**选路径。

## SDK 清单

| 名称 | 语言 | 仓库 / 包 | 环境要求 |
|------|------|-----------|----------|
| yop-java-sdk | Java | [Maven Central](https://central.sonatype.com/artifact/com.yeepay.yop.sdk/yop-java-sdk) · [GitHub](https://github.com/yop-platform/yop-java-sdk) | JDK 1.8+；多域名路由需 `4.4.1+` |
| yop-php-sdk | PHP | [Packagist](https://packagist.org/packages/yeepay/yop-php-sdk) · [GitHub](https://github.com/yop-platform/yop-php-sdk) | PHP 5.5+ |
| yop-dotnet-sdk | .NET | [GitHub](https://github.com/yop-platform/yop-dotnet-sdk) | .NET Framework 2.0+ |
| yop-nodejs-sdk | Node.js | `npm i @yeepay/yop-nodejs-sdk` · [GitHub](https://github.com/yop-platform/yop-nodejs-sdk) | Node.js 18+ |
| yop-python-sdk | Python | [GitHub](https://github.com/yop-platform/yop-python-sdk) | Python 2.7+ |
| yop-go-sdk | Go | [GitHub](https://github.com/yop-platform/yop-go-sdk) | Go 1.18+ |

版本请使用各包仓库的**最新稳定版**。Java 查版本优先 [Maven Central（central.sonatype.com）](https://central.sonatype.com/artifact/com.yeepay.yop.sdk/yop-java-sdk)，或执行 `scripts/tools/resolve_java_sdk_version.py`；**勿用** `search.maven.org`（索引滞后）。解析细则见 `开始对接/SDK使用说明.md`「版本解析协议」。

## 最佳实践

1. 使用最新稳定版 SDK，做好异常处理，合理设置超时。
2. 妥善保管私钥，及时更新证书，验证回调签名。
3. 生产交易走商户自有系统；`scripts/` 仅用于联调验证。
