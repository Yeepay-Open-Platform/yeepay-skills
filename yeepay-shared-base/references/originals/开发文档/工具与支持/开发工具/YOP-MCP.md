# YOP-MCP

# YOP MCP 开发者快速入门指南

## 概览

Syntax error in textmermaid version 11.14.0

## 准备工作

### 易宝入网

获取正式商编和密钥，或者测试商编和密钥。

### 安装AI IDE

- **Cursor**: [https://www.cursor.com/cn](https://www.cursor.com/cn)
- **Trea**: [https://www.trae.com.cn](https://www.trae.com.cn/)
- **Cline**: [https://cline.bot/](https://cline.bot/)
- **RooCode**: [https://roocode.com](https://roocode.com/)

### 安装 python 开发环境

#### Mac 系统

使用 Homebrew 安装：

```
# 安装 Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 uv
brew install uv
```

#### Win 系统

在 Windows 系统上安装 uv，可以按照以下步骤操作：

1. 安装 Python（推荐 3.12 及以上版本） 可从 [Python 官网](https://www.python.org/downloads/windows/) 下载并安装，安装时请勾选“Add Python to PATH”。
2. 安装 uv 打开命令提示符（cmd）或 PowerShell，执行以下命令：
  ```
    pip install uv
  ```
    如果提示权限不足，可尝试加上 `--user` 参数：
3. 验证安装 安装完成后，输入以下命令检查 uv 是否安装成功：
  ```
    uv --version
  ```
    若能正确显示版本号，则说明安装成功。

如遇到网络问题，可配置国内 PyPI 镜像源

### 安装 YOP MCP

后续有新版本发布需再次运行该命令：

```
# 安装 YOP MCP
uvx yop-mcp
```

### 配置 YOP MCP

在 AI IDE 中配置mcp server

```
{
  "mcpServers": {
    "yop-mcp": {
      "command": "uvx",
      "args": [
        "yop-mcp"
      ]
    }
  }
}
```

### 配置 User Rule

在 AI IDE 中配置用户规则

```
1. yop-mcp工具使用规范
- 以MCP工具返回信息为准，如果获取不到请反馈给用户，再由用户手工提供，禁止从其他渠道获取不可靠信息
- 当MCP工具返回数据中包含链接时，请继续使用工具yeepay_yop_link_detail获取更多信息补充到上下文

2. 任务拆分规范
结合本地项目代码与文档，梳理出对接计划和详细的任务清单，每个任务描述至少包含以下信息：
- 任务名称：简洁动词开头，清晰描述该步骤做什么
- 详细描述：具体说明需要做什么，包含关键操作点
- 输入依赖：此任务开始前**必须**有哪些输入？来自哪里？
- 预期输出：此任务完成后**必须**产生的具体、可验证的结果
- 成功标准：如何**量化**或**明确判断**此任务是否成功完成？
- 失败处理/超时：如果此任务执行失败或超时，**必须**采取什么行动？

3. 生成代码规范
- 测试驱动，基于单元测试的运行结果调试与修正代码缺陷
- 使用基础SDK方式对接
- 构造YopClient使用单例模式
- 非文件下载接口返回的YopResponse中字段result类型为Map<String,Object>
- 请求/响应参数需生成模型类，添加字段注释，借助lombok注解精简代码
- 构造请求参数时添加参数校验，过滤空值
- 响应参数模型类中根据业务错误码生成isSuccess判定方法
- 代码逻辑中添加必要日志
- 优先使用本地项目已有工具类
- 禁止在聊天窗口输出代码，直接修改目标文件
- 代码变更向前兼容，不影响现有功能
- 使用SDK工具com.yeepay.yop.sdk.utils.DigitalEnvelopeUtils或者com.yeepay.yop.sdk.service.common.YopCallbackEngine处理结果通知，返回的就是业务数据，不需要自行再做其他处理

4. 测试密钥可以采用如下配置，默认以标准商户身份调用，可以根据需要指定其他appKey身份
{
  "app_key": "sandbox_rsa_10080662592",//默认标准商
  "isv_private_key": [
    {
      "app_key": "sandbox_rsa_10080662592",//测试标准商
      "store_type": "string",
      "cert_type": "RSA2048",
      "value": "MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQC2nVeqloNIEqII9SDUtU2i33le3rSf8xRkHAQ3z8s2JjhH0Cx4FHp7jRGgavc6zb94dsZ7LPsUXVRZD20oJx2pgKrJV2W0KhRWlvGMrDGy0Q2C1IYVPMCWq29Gk4vpAhfcopz4PeUMZju6jKtQgoPH6KbRpqRpvnSNbUsS5Y2IYPiDaTcsw3nI16eF/xYbjCQrtWocCQTMxc7V9cf5/bMlIZiLK0jcy2ecZDbRSLyjeQYy7tvxdXcdhzi9g4Z0O4cPb8EW+T91ZoHArQp5jyOF1xMD79dk5ETGMapGP9rLR9bfJM3gEkDSoIkTBOdTK/l04yQKiwAzyY/89Nf2q3m7AgMBAAECggEACnocfX0FKy1mfn0R1SJRwfZwUDEWy9Z2ZQf2df1F+2VV9UjMRFdob444ZKu+Y3FKeu7VlFuQTCrOnA12hcc4vHDVW5fYDe4cHJusYBXBBDFaRRdMWguSQRK036e3bzbfh5kMyHFEouF6q8lGSugyB1YhvAWDiU2UAkky9XKWHCzbRdbJWTklF2xpoNIoZoRDlbHhjTTXSyhCdfPfDxMB0RgyZmKDeBqff/VGA1A01m4cWPpYbsA1VKPYSg5cfBIN7rdiw009Wmv8FUNxByHJ97Yb7QgLF1RkpdhOp92mpZAy0w4/cxfkzXcM6nCNTljbkmdTJTXeOlYl1+90GvrwAQKBgQDYNNbqc0ssA0D3NWBXH65uhtrFwnSu5YzeuXkJbkgPsgxKdNs50lFbsMPHGuQckuQfkujLbnutF3uCKVx1ZSrIDGSY/aRtlrNlwe8hPcBDTP9lvG+Z+UXIjlnCzfB9wPPBthx+Dt9EchaPECmVmp1Mor8/LMmZXGbewq+Q/BeMOwKBgQDYObvAMjglbT9320GFvxbCCcrlxhSS6FeaLGWGyamYRtO0lW76taLssqenxk9fVzB9kFEiaVUEhOBZCVnSQUaIfceD94+ZynSSpokxgD8BWG3C2ktlxPta1xj1nrBq+7NgGsw58EpqCawhIHEfr2w6wrEiGzxD98S4+9D8MRxwgQKBgQC8cSmUxRKS9O8NyE8FAM8G9LD/xuHugpLKmXu+VYmnbHc7+igNeJuCwEmTY4PIx9rfDiurC8vt7Nawdx5oD9o+7FZN5l0HS19nZKXpIipOPnEoGhpnaJWDHVds7BQddyy9/N1OneXJgWraHKsyAsXxQrRP+thnu9rJc4SUaLSZewKBgQDLe9GHtvsFpcEj32/TGRimtKaABCAafJLsYTmOVjvHNWhIOpT9VXAlBqAmkMbjd18H24evNacvoIis4dLovktNaekX9SLr3Q5FcHoN3p3sezaYN+zasjzFqUUw6Q0nMQYGvFFTeSHelomphylOYz0cM1qVOUJGyGYWm8x5eRJFgQKBgQC47hglhAtZZCJV56oD4RFhnFtP8pRzfTJOoObo3uLvjERTZPVJte5FX9Aw1OyKS14SeYr7EQ7uSCOnwUeZQTAxl+RP8aEq8mAsc4U/voDXgmz9BQ0u+3q30023iccNaG6DJrdV4ZTBg4huphwg5WtdV/Pj7RMkkF/XOaf/cnD9IQ=="
    },
    {
      "app_key": "sandbox_rsa_10080662589",//测试服务商
      "store_type": "string",
      "cert_type": "RSA2048",
      "value": "MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQC2nVeqloNIEqII9SDUtU2i33le3rSf8xRkHAQ3z8s2JjhH0Cx4FHp7jRGgavc6zb94dsZ7LPsUXVRZD20oJx2pgKrJV2W0KhRWlvGMrDGy0Q2C1IYVPMCWq29Gk4vpAhfcopz4PeUMZju6jKtQgoPH6KbRpqRpvnSNbUsS5Y2IYPiDaTcsw3nI16eF/xYbjCQrtWocCQTMxc7V9cf5/bMlIZiLK0jcy2ecZDbRSLyjeQYy7tvxdXcdhzi9g4Z0O4cPb8EW+T91ZoHArQp5jyOF1xMD79dk5ETGMapGP9rLR9bfJM3gEkDSoIkTBOdTK/l04yQKiwAzyY/89Nf2q3m7AgMBAAECggEACnocfX0FKy1mfn0R1SJRwfZwUDEWy9Z2ZQf2df1F+2VV9UjMRFdob444ZKu+Y3FKeu7VlFuQTCrOnA12hcc4vHDVW5fYDe4cHJusYBXBBDFaRRdMWguSQRK036e3bzbfh5kMyHFEouF6q8lGSugyB1YhvAWDiU2UAkky9XKWHCzbRdbJWTklF2xpoNIoZoRDlbHhjTTXSyhCdfPfDxMB0RgyZmKDeBqff/VGA1A01m4cWPpYbsA1VKPYSg5cfBIN7rdiw009Wmv8FUNxByHJ97Yb7QgLF1RkpdhOp92mpZAy0w4/cxfkzXcM6nCNTljbkmdTJTXeOlYl1+90GvrwAQKBgQDYNNbqc0ssA0D3NWBXH65uhtrFwnSu5YzeuXkJbkgPsgxKdNs50lFbsMPHGuQckuQfkujLbnutF3uCKVx1ZSrIDGSY/aRtlrNlwe8hPcBDTP9lvG+Z+UXIjlnCzfB9wPPBthx+Dt9EchaPECmVmp1Mor8/LMmZXGbewq+Q/BeMOwKBgQDYObvAMjglbT9320GFvxbCCcrlxhSS6FeaLGWGyamYRtO0lW76taLssqenxk9fVzB9kFEiaVUEhOBZCVnSQUaIfceD94+ZynSSpokxgD8BWG3C2ktlxPta1xj1nrBq+7NgGsw58EpqCawhIHEfr2w6wrEiGzxD98S4+9D8MRxwgQKBgQC8cSmUxRKS9O8NyE8FAM8G9LD/xuHugpLKmXu+VYmnbHc7+igNeJuCwEmTY4PIx9rfDiurC8vt7Nawdx5oD9o+7FZN5l0HS19nZKXpIipOPnEoGhpnaJWDHVds7BQddyy9/N1OneXJgWraHKsyAsXxQrRP+thnu9rJc4SUaLSZewKBgQDLe9GHtvsFpcEj32/TGRimtKaABCAafJLsYTmOVjvHNWhIOpT9VXAlBqAmkMbjd18H24evNacvoIis4dLovktNaekX9SLr3Q5FcHoN3p3sezaYN+zasjzFqUUw6Q0nMQYGvFFTeSHelomphylOYz0cM1qVOUJGyGYWm8x5eRJFgQKBgQC47hglhAtZZCJV56oD4RFhnFtP8pRzfTJOoObo3uLvjERTZPVJte5FX9Aw1OyKS14SeYr7EQ7uSCOnwUeZQTAxl+RP8aEq8mAsc4U/voDXgmz9BQ0u+3q30023iccNaG6DJrdV4ZTBg4huphwg5WtdV/Pj7RMkkF/XOaf/cnD9IQ=="
    },
    {
      "app_key": "sandbox_sm_10080086386",//测试平台商
      "store_type": "string",
      "cert_type": "RSA2048",
      "value": "MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQC2nVeqloNIEqII9SDUtU2i33le3rSf8xRkHAQ3z8s2JjhH0Cx4FHp7jRGgavc6zb94dsZ7LPsUXVRZD20oJx2pgKrJV2W0KhRWlvGMrDGy0Q2C1IYVPMCWq29Gk4vpAhfcopz4PeUMZju6jKtQgoPH6KbRpqRpvnSNbUsS5Y2IYPiDaTcsw3nI16eF/xYbjCQrtWocCQTMxc7V9cf5/bMlIZiLK0jcy2ecZDbRSLyjeQYy7tvxdXcdhzi9g4Z0O4cPb8EW+T91ZoHArQp5jyOF1xMD79dk5ETGMapGP9rLR9bfJM3gEkDSoIkTBOdTK/l04yQKiwAzyY/89Nf2q3m7AgMBAAECggEACnocfX0FKy1mfn0R1SJRwfZwUDEWy9Z2ZQf2df1F+2VV9UjMRFdob444ZKu+Y3FKeu7VlFuQTCrOnA12hcc4vHDVW5fYDe4cHJusYBXBBDFaRRdMWguSQRK036e3bzbfh5kMyHFEouF6q8lGSugyB1YhvAWDiU2UAkky9XKWHCzbRdbJWTklF2xpoNIoZoRDlbHhjTTXSyhCdfPfDxMB0RgyZmKDeBqff/VGA1A01m4cWPpYbsA1VKPYSg5cfBIN7rdiw009Wmv8FUNxByHJ97Yb7QgLF1RkpdhOp92mpZAy0w4/cxfkzXcM6nCNTljbkmdTJTXeOlYl1+90GvrwAQKBgQDYNNbqc0ssA0D3NWBXH65uhtrFwnSu5YzeuXkJbkgPsgxKdNs50lFbsMPHGuQckuQfkujLbnutF3uCKVx1ZSrIDGSY/aRtlrNlwe8hPcBDTP9lvG+Z+UXIjlnCzfB9wPPBthx+Dt9EchaPECmVmp1Mor8/LMmZXGbewq+Q/BeMOwKBgQDYObvAMjglbT9320GFvxbCCcrlxhSS6FeaLGWGyamYRtO0lW76taLssqenxk9fVzB9kFEiaVUEhOBZCVnSQUaIfceD94+ZynSSpokxgD8BWG3C2ktlxPta1xj1nrBq+7NgGsw58EpqCawhIHEfr2w6wrEiGzxD98S4+9D8MRxwgQKBgQC8cSmUxRKS9O8NyE8FAM8G9LD/xuHugpLKmXu+VYmnbHc7+igNeJuCwEmTY4PIx9rfDiurC8vt7Nawdx5oD9o+7FZN5l0HS19nZKXpIipOPnEoGhpnaJWDHVds7BQddyy9/N1OneXJgWraHKsyAsXxQrRP+thnu9rJc4SUaLSZewKBgQDLe9GHtvsFpcEj32/TGRimtKaABCAafJLsYTmOVjvHNWhIOpT9VXAlBqAmkMbjd18H24evNacvoIis4dLovktNaekX9SLr3Q5FcHoN3p3sezaYN+zasjzFqUUw6Q0nMQYGvFFTeSHelomphylOYz0cM1qVOUJGyGYWm8x5eRJFgQKBgQC47hglhAtZZCJV56oD4RFhnFtP8pRzfTJOoObo3uLvjERTZPVJte5FX9Aw1OyKS14SeYr7EQ7uSCOnwUeZQTAxl+RP8aEq8mAsc4U/voDXgmz9BQ0u+3q30023iccNaG6DJrdV4ZTBg4huphwg5WtdV/Pj7RMkkF/XOaf/cnD9IQ=="
    }
  ]
}

5. 结果通知处理工具可根据情况自行选择
- YopCallbackEngine工具支持解密RSA、SM2等密钥类型的结果通知，需要注册一个自定义的YopCallbackHandler来处理解密后的业务数据YopCallback，并且在处理SM2类型时，需要对响应体签名后返回，示例代码如下：
package com.yeepay.yop.sdk.service.common;

import com.google.common.collect.Maps;
import com.yeepay.yop.sdk.BaseTest;
import com.yeepay.yop.sdk.http.Headers;
import com.yeepay.yop.sdk.http.YopContentType;
import com.yeepay.yop.sdk.service.common.callback.YopCallback;
import com.yeepay.yop.sdk.service.common.callback.YopCallbackRequest;
import com.yeepay.yop.sdk.service.common.callback.YopCallbackResponse;
import com.yeepay.yop.sdk.service.common.callback.enums.YopCallbackHandleStatus;
import com.yeepay.yop.sdk.service.common.callback.handler.YopCallbackHandler;
import com.yeepay.yop.sdk.service.common.callback.handler.YopCallbackHandlerFactory;
import org.apache.commons.lang3.StringUtils;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Map;


public class YopCallbackEngineTest {

    private static final Logger LOGGER = LoggerFactory.getLogger(YopCallbackEngineTest.class);

    private static String callbackPath = "/rest/v1.0/test/app-alias/create";
    private static String sm2CallbackPath = "/yop-callback/cs_1720925143663";

    @Before
    public void init() {
        MockYopCallbackHandler mockHandler = new MockYopCallbackHandler();
        MockSm2YopCallbackHandler mockSm2Handler = new MockSm2YopCallbackHandler();
        YopCallbackHandlerFactory.register(mockHandler.getType(), mockHandler);
        YopCallbackHandlerFactory.register(mockSm2Handler.getType(), mockSm2Handler);
    }

    @Test
    public void testRsa() {
        YopCallbackRequest request =
                new YopCallbackRequest(callbackPath,"POST")
                // yeepay测试环境qa，生产环境prod(不设置，默认为prod)，此处涉及易宝公钥选择，配置错误会影响验签结果
                        .setProvider("yeepay").setEnv("qa")
                        .setContentType(YopContentType.FORM_URL_ENCODE)
                        .addParam("customerIdentification", "app_Fe51qCyZWcEnDMtK")
                        .addParam("response", "ZIcrArlonH0mxIWCRejL2VQS2qeK5EFz2gALzdMbusIU8eqwnWNgJRWiTwJElSQEhnT42KkU3jXWZr2dd0A8-bZSjT-hvNCUI0aoJZkadRtJrWoe_ygGhOLegj7cTbk8y7GOzfFQteIFbB9ALae1CqWVHgfgyozbTLgsse4MfuYjio9r3DOkCJJSkW6mEHB0G4rTXSWFni0h_Uhtu5jsuCTU4vWDPKrBIZI17rr1AIqmyOd8C8oLCAplC1JT4KnLq5QCir4cnvZJrGYB5-bI00gPOdGX2_v4Az3VqMkh8PqqPSDriJ-PqDo9T2dnjR5njYkTSSzUpIXg6cfhLaTNIQ$0sn1fsX0zRYXv-bb0tV531Brbhb-fPORrXYqe8JzHbnL8NkAwIPRkSaTXfq3etJnmslkkBlPpZeTc7639TWQlBrl3eVW-aQKIjFX4bhfyythIh5ByjBAHw1RaYwoHw10kkpbBBk01K-6pzE9QzT6TvjZLsSsXZ6O3WJdvrB8dtpJA-PI-sOzm7DXkBqfKOSufkN1C1mRvexBlcN3ScSH2TKo5ZwKw3Fo_93GsYFD0hzYmHpC6yCyHXeY1PPlHYqd_KsqXVo_xBtXMCadoKnldYnMljXdhAQJLRdlkwTgeD8FX18SQSJ18O6Ag0w3IM9QXkcgZVgIo1-_ZUncc5AtNXyQCvfT4tNyaIRFsXlFqj5tCc5bekMz8OzYeRTPfmfCLKXmjvg4ICMw0aIRboX1tyZpCHdHU269u0-wX90pMDNRqBZsLag6glNDSzEG8RQaB4vGrjvxYy0ixeUnogwni2qqnnGX5Gfhkst7FPYubAsi5HweDT_aJIrmE6kMiBrpMAOcIGZ6slYK854FOH3ODO9-raz7n2P__NUTpziTF4t4Jru_erJevVoGyHH81qq_msIMvK7IRx2z1QoExRL08A$AES$SHA256");
        YopCallbackResponse response = YopCallbackEngine.handle(request);
        Assert.assertEquals(response.getStatus(), YopCallbackHandleStatus.SUCCESS);
        Assert.assertTrue(null == response.getHeaders() || StringUtils.isBlank(response.getHeaders().get(Headers.YOP_SIGN)));
    }

    @Test
    public void testSm2() {
        // 回调地址格式为，https://xxx/{path}，eventType为path部分加上"/"前缀
        // 举例说明：加入回调地址为"https://callback.test/payNotify"，则eventType为"/payNotify"
        String eventType = sm2CallbackPath;
        Map<String, String> headers = Maps.newHashMap();
        headers.put("Authorization", "YOP-SM2-SM3 yop-auth-v3/sandbox_sm_10080041523/2024-07-14T02:45:44Z/1800/content-length;content-type;x-yop-content-sm3;x-yop-encrypt;x-yop-request-id/GbzQbci-j9Qe2pC8lOwWejXo_1Cy8N5FD80xYKNhfX6d3LievqWPIanRLI8YL5UAb5AFJhcRpaax1BsxDQcHvA$SM3");
        headers.put("x-yop-content-sm3", "71a21d1557847e2865c9c5716490f16f4543686888cbdad6261afc015b4f91f7");
        headers.put("x-yop-encrypt", "yop-encrypt-v1//SM4_CBC_PKCS5Padding/BCbsJljzCjgpg7x1zK4z-EexCpADSpw0mSQL0ZXKOxyRDh_XSr_KUj7tX7GzJ-ouns1oT8MTrX76FYCp3pPQ-LElGwmvl-L3OpcaCP5ou9ABIH0zDrD8bCgm9eSLqiVLv_Jli6zh9VcWFsI-AZboUQo/4x2G0lyi51StUZjfPradeQ;eW9w/stream//JA");
        headers.put("x-yop-request-id", "cs_1720925143663");
        headers.put("x-yop-sign-serial-no", "4059376239");
        headers.put("x-yop-appkey", "sandbox_sm_10080041523");
        headers.put("Content-Type", "application/json");
        YopCallbackRequest request =
                new YopCallbackRequest(eventType, "POST")
                // yeepay测试环境qa，生产环境prod(不设置，默认为prod)，此处涉及易宝公钥选择，配置错误会影响验签结果
                        .setProvider("yeepay").setEnv("qa")
                        .setContentType(YopContentType.JSON)
                        .setHeaders(headers)
                        .setContent("\"cdsnFDl8bVJSOuROSxNVDbLyxlDC0QGYvzZwTWxb0dMuTzDVwTCkATAmiiiUSfgOYoJlsz91qH6d1j0_TBdnSjN7EecCFZdo6MvatWIX5burxxLDAMAwo3QAmyiT5dVh72giQ-EIJAt8R_X5rO4PcA\"");
        YopCallbackResponse response = YopCallbackEngine.handle(request);
        Assert.assertEquals(response.getStatus(), YopCallbackHandleStatus.SUCCESS);
        Assert.assertTrue(StringUtils.isNotBlank(response.getHeaders().get(Headers.YOP_SIGN)));
    }

    // 可以基于自身业务逻辑自行实现handler，处理解密后的明文数据YopCallback
    private static class MockYopCallbackHandler implements YopCallbackHandler {

        @Override
        public String getType() {
            return callbackPath;
        }

        @Override
        public void handle(YopCallback callback) {
            // 业务数据处理示例：处理解密后的 bizData
            String bizData = callback.getBizData();
            LOGGER.info("YopCallback handled success, callback:{}, type:{}", callback, getType());
        }
    }

    private static class MockSm2YopCallbackHandler implements YopCallbackHandler {

        @Override
        public String getType() {
            return sm2CallbackPath;
        }

        @Override
        public void handle(YopCallback callback) {
            // 业务数据处理示例：处理解密后的 bizData
            String bizData = callback.getBizData();
            LOGGER.info("YopCallback handled success, callback:{}, type:{}", callback, getType());
        }
    }
}

- DigitalEnvelopeUtils工具仅支持RSA密钥类型，但用法比较简单，示例代码如下

// 引入工具类
import com.yeepay.yop.sdk.utils.DigitalEnvelopeUtils;
import com.yeepay.yop.sdk.inter.utils.RSAKeyUtils;


String response = "加密后的业务数据";
String privateKeyStr = "您的RSA私钥";
String appKey = "您的appKey";
PrivateKey isvPrivateKey = RSAKeyUtils.string2PrivateKey(privateKeyStr);

// 根据自身情况从下列三种方式中选择其一

// 解密方法1：走指定appKey配置的私钥
//String bizData = DigitalEnvelopeUtils.decrypt(response, appKey, "RSA2048");

// 解密方法2：走程序配置的默认appKey，默认私钥
String bizData = DigitalEnvelopeUtils.decrypt(response, "RSA2048");

// 解密方法3：走指定私钥
//String bizData = DigitalEnvelopeUtils.decrypt(response, isvPrivateKey);

// 业务数据处理示例：处理解密后的 bizData
```

### 使用 YOP MCP

#### 基础用法

1. 了解平台产品与接口能力
2. 获取某个产品的详细说明
3. 引入SDK&配置
4. 单接口代码生成
5. 结果通知代码生成
6. 单元测试

#### 高级用法

1. 任务规划与执行

#### 最佳实践

1. 建议单次对话不超过5个接口功能，当前会话预估无法完成所有任务时，要及时拆分会话，并让AI帮忙并生成新会话的初始提示词
2. AI完成编码后，除了必要的单元测试验证外，可以进一步借助yop-mcp实时知识对参数、错误码等信息校对
3. AI偶尔会偷懒犯错，必要时需要人工介入，及时纠正他的思路和方向

#### 常见问题

1. 生成的代码不可用，与官网描述有出入，请检查yop-mcp配置，确保网络正常且工具已经启用

会话过程中，会有Called yeepayyopapidetail指令，并成功返回，这种视为mcp工具可用 