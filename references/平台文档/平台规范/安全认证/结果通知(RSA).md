# 国际密钥(RSA)结果通知

## [](https://open.yeepay.com/docs-v3/platform/207.md#%E6%A6%82%E8%BF%B0)概述

易宝开放平台使用数字签名+数字信封技术对异步通知报文进行加密和签名，确保通知数据的安全性和完整性。本文详细介绍基于 RSA 国际密钥的结果通知实现方案。

### [](https://open.yeepay.com/docs-v3/platform/207.md#%E6%8A%80%E6%9C%AF%E7%89%B9%E7%82%B9)技术特点

-   采用数字信封加密技术
-   支持 RSA 非对称加密
-   使用 AES 对称加密
-   实现数字签名机制

## [](https://open.yeepay.com/docs-v3/platform/207.md#%E6%8A%A5%E6%96%87%E8%A7%84%E8%8C%83)报文规范

### [](https://open.yeepay.com/docs-v3/platform/207.md#%E8%AF%B7%E6%B1%82%E6%A0%BC%E5%BC%8F)请求格式

-   Content-Type: application/x-www-form-urlencoded
-   请求方式: POST
-   字符编码: UTF-8

### [](https://open.yeepay.com/docs-v3/platform/207.md#%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0)请求参数

| 参数名 | 类型 | 说明 | 示例 |
| --- | --- | --- | --- |
| response | string | 加密签名后的业务数据 | ZIcrArl... |
| customerIdentification | string | 应用标识(appKey) | app_100xxxxxxxx |

### [](https://open.yeepay.com/docs-v3/platform/207.md#%E6%8A%A5%E6%96%87%E7%BB%93%E6%9E%84)报文结构

response 参数使用 `$` 符号分隔为四个部分：

1.  RSA加密的随机密钥
2.  AES加密的业务数据和签名
3.  对称加密算法标识
4.  摘要算法标识

### [](https://open.yeepay.com/docs-v3/platform/207.md#%E6%8A%A5%E6%96%87%E6%8E%A5%E6%94%B6)报文接收

此处基于java web服务，使用servlet进行接收

```
// 解析HttpServletRequest, 获取原始通知报文
public void parse(HttpServletRequest req) throws IOException {
    final String contentTypeStr = req.getContentType();
    if (!StringUtils.startsWith(contentTypeStr, "application/x-www-form-urlencoded")) {
        throw new IllegalArgumentException("RSA回调请求仅支持form格式");
    }
    String response = req.getParameter("response");
    String appKey = req.getParameter("customerIdentification");
    // 根据请求参数进行验签认证、解密等后续操作
}
```

## [](https://open.yeepay.com/docs-v3/platform/207.md#%E8%AE%A4%E8%AF%81%E8%A7%A3%E5%AF%86)认证解密

### 方案一：使用 SDK（推荐）

| 语言 | 文档 |
| --- | --- |
| Java | `开始对接/SDK使用说明.md` §六（`DigitalEnvelopeUtils` / `YopCallbackEngine`） |
| 其他 | `工具与支持/开发工具/平台SDK.md` 定位仓库 README |

### 方案二：使用事件网关

见 `工具与支持/开发工具/结果通知工具.md`。

### [](https://open.yeepay.com/docs-v3/platform/207.md#%E6%96%B9%E6%A1%88%E4%B8%89%EF%BC%9A%E8%87%AA%E8%A1%8C%E5%AE%9E%E7%8E%B0)方案三：自行实现

#### [](https://open.yeepay.com/docs-v3/platform/207.md#%E8%A7%A3%E5%AF%86%E6%AD%A5%E9%AA%A4)解密步骤

1.  分割 response 参数
    
    ```
    第一部分：RSA加密的随机密钥
    第二部分：AES加密的业务数据和签名
    第三部分：AES
    第四部分：SHA256
    ```
    
    ```
    ZIcrArlonH0mxIWCRejL2VQS2qeK5EFz2gALzdMbusIU8eqwnWNgJRWiTwJElSQEhnT42KkU3jXWZr2dd0A8-bZSjT-hvNCUI0aoJZkadRtJrWoe_ygGhOLegj7cTbk8y7GOzfFQteIFbB9ALae1CqWVHgfgyozbTLgsse4MfuYjio9r3DOkCJJSkW6mEHB0G4rTXSWFni0h_Uhtu5jsuCTU4vWDPKrBIZI17rr1AIqmyOd8C8oLCAplC1JT4KnLq5QCir4cnvZJrGYB5-bI00gPOdGX2_v4Az3VqMkh8PqqPSDriJ-PqDo9T2dnjR5njYkTSSzUpIXg6cfhLaTNIQ
    
    0sn1fsX0zRYXv-bb0tV531Brbhb-fPORrXYqe8JzHbnL8NkAwIPRkSaTXfq3etJnmslkkBlPpZeTc7639TWQlBrl3eVW-aQKIjFX4bhfyythIh5ByjBAHw1RaYwoHw10kkpbBBk01K-6pzE9QzT6TvjZLsSsXZ6O3WJdvrB8dtpJA-PI-sOzm7DXkBqfKOSufkN1C1mRvexBlcN3ScSH2TKo5ZwKw3Fo_93GsYFD0hzYmHpC6yCyHXeY1PPlHYqd_KsqXVo_xBtXMCadoKnldYnMljXdhAQJLRdlkwTgeD8FX18SQSJ18O6Ag0w3IM9QXkcgZVgIo1-_ZUncc5AtNXyQCvfT4tNyaIRFsXlFqj5tCc5bekMz8OzYeRTPfmfCLKXmjvg4ICMw0aIRboX1tyZpCHdHU269u0-wX90pMDNRqBZsLag6glNDSzEG8RQaB4vGrjvxYy0ixeUnogwni2qqnnGX5Gfhkst7FPYubAsi5HweDT_aJIrmE6kMiBrpMAOcIGZ6slYK854FOH3ODO9-raz7n2P__NUTpziTF4t4Jru_erJevVoGyHH81qq_msIMvK7IRx2z1QoExRL08A
    
    AES
    
    SHA256
    ```
    
2.  解密随机密钥
    
    -   BASE64解码第一部分
    -   使用商户私钥RSA解密
    -   获得AES随机密钥
    
    ```
    // 为了便于展示，我们对密钥进行了urlSafeBase64编码，编码后的密钥如下
    kLNl5Q7MOV0FRw_dl1VDPg
    ```
    
    本示例中使用的商户私钥是：
    
    ```
    MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCFqza8OmK0drABjmphX3erNEoLJ6kCqaE/AWvqEReAq5K8+3btAVEJYBiMbEJUvZpV4YCITDhyJeRzdfLl2EGnsvI4lrhvrvGAjW9lB34b7GdJSMFFj+ExrTuCQ7zDeUgATlmhLyHxWZ6IAVwf1a3G5bk2GhUipFc0dL8HviVk25CSAgCWKL8LZ0V4ec+FF3/Z6orJUChQOuvpNlclH65pHbdQ4Mr3rQUI0z7WSaW1U1EZeXSctRPf/3JQYLi+RW/yogXG8t+6zn9jE/tGuWJV0bm/ZUDU2XydjZgU0E/NzMutmNVSSKpBy74vt5SCNXkK0BgjRTXP8HGvEgA7IYfLAgMBAAECggEAQNlOxcUBrBHE1Ax22eTKFvpYTc8g9NS9EOcsprNCFr+mgh7xlIxF92lyn3XKPHh8DtxHUljALcjqa4W2oQHo4GY1k3Sz6CMUsUxs1bPr37oyZeBxO8FQ/JvRuiIIy0DkyJk6bLOEISZcfhlCy4MMOumqkG/Y/ySB1kYpg6UhWStlGdQZbHEL7NUBW1QVQqaDAtSV8cgNNXbinQ08pIMlfqnH57DM8J7lx+687li41ZkQgCc/r/zkV5Tf5ABlhDxmZZbHmU7jsvlqh6zxm12r7A0gOwnb/wVd0ZrpIE2TfsDGOQckfEmaD4uhsabDAVO7I6IDM86hH3Sm285hkQ/2eQKBgQC6eNRpJQv6TfXMqEoNMf503WGskWF0RFSU0mU/5dSX8GELhLkyAtAhZFnrOKcseZJng/Z6grfS2wIG3Y17kXIlbi8Wprk0F9AsUOSEFPFRW/I7y7aUDvGf8Jz/TsiYEatSE0SJCWZbpaO8+WoczNybWNyyHapq2g6+xHSlyEp9nQKBgQC3gjOIF1dt67lrWSogVDX1eEpp6yLxKXC0usGV/0sB2FK5S9KqEh2Ul+rWwlxXxLpVYHhHFr1k7PyFrnwsTUxNHj2joCD1yOhMoxgMoRm0/z43cV/0TeTcLTQkxdCtwZ6pQwHIAHenLRpxpnD8Y8EplA3VS9Lno7eSC9VjqgFShwKBgF83vfcm1LPuxTnJIW8VfUK9nNeasPHGxo3r1YnIWUNwmo1gK5UO/KpgbM4A8tRyC8FSEDVEtIs2DBXnYgycG3ZjiiX94opoMoO+lsGfVA5gbhP8lPGLo/Qw0GpKF4IXW60ga5myNBNORIsFrRqhvXCR8rf9D/1Z9beR56KT4P29AoGAV986+dHjhbk4wpShvXVVmUOOroVv5/cmBwTeqgrjSfDiO+R47gNassrEIy5StZx4dWWKctAKxQdOLF1PDI+/F7aBYZbN8aPQyNHYNEP4YVlP25Col/2st1nV/D3VHT730KlLcw/2O9E3NnCy7ch+uIAy145FYbJdtst/1QeVNoUCgYEAtv3w9xNugsYl4/yNkC/DIXat9u/56sVjnYzxvwHZT8jtg4uo3qqlRqqm4OcUmzcsYodrsbn8upizq9ZS2NVdPrGIPFOZBgNUKWL1Ok/dJgfBcdpo72/UX4+KQ2/9c1ZrjjMs4sglsrzvZTXqkryXkPKxKk1EcjDaKiOExFnk6Y8=
    ```
    
3.  解密业务数据
    
    -   BASE64解码第二部分
    -   使用随机密钥AES解密
    -   获得明文和签名
    
    ```
    {"date":"20181014000000","aaa":"","boolean":true,"SIZE":-14,"name":"易宝支付","dou":12.134}$egc-j7UPBntdMMaz5P08MhVkkpOl8RbbBKzfAgQeNoDTbOG8RYxIlVPu1rIaZnSwc7J6ZQB-gYSDatzQ4tZlHOXRqVcuZiKX0qU2CjdSUscWOLkL95g6wFAMTCNCK0OmHEj8oldCrlD1F0-_klVRFPiVn4kUAnJ8GggAn05nP1PDeV3ZFsVxGUTA4aGHVZwdRMCkcbxhnAyJRPcWPmjkMfXUrp5a76s8iHd9-SCdeA-I5AXcr0TVp9ELACPqG-K-u7wTAaQvf5c2yWIjkqHsTygXKaDEmY9MDJJFqANDbI6D5F5_m2vV_rrUYtAMbHQ6ivhgBOyrYWm0COfR-n1F1g
    ```
    
4.  验证签名
    
    -   分离明文和签名
    -   使用平台公钥验证签名
    -   确认数据完整性

上述明文用 `$`分隔为2部分，第1部分为异步通知明文；第2部分为签名。用 YOP 平台公钥和第4部分指定的摘要算法（比如 SHA256），做SHA256withRSA签名验证，如果通过即可认为报文为 YOP 平台签发。

**注意**：

-   通知明文中可能存在 `$`符号，但是签名部分中没有 `$`符号, 所以首先应该定位到最后一个 `$`符号的位置，其前为通知明文，其后为签名
-   平台BASE64编码采用的URL安全模式(将非法字符'+'和'/'转为'-'和'_', 见RFC3548)，部分语言解码时须先进行手动替换还原，伪代码示例：`$data.replaceAll("-", "+").replaceAll("_", "/")`

## 响应规范

成功/失败应答、重试与幂等见 `结果通知机制说明.md` §三–§四。RSA 成功应答：HTTP 200 + 纯文本 `SUCCESS`。

## 通用机制与排障

notifyUrl、重试策略、幂等、查单兜底、成功应答格式等见 `平台规范/结果通知机制说明.md`。

验签/解密失败、回调收不到：见 `../../../troubleshooting.md` §二；Java SDK 见 `开始对接/Java-SDK报错说明.md`。
