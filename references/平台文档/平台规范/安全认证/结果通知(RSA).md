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
| customerIdentification | string | 应用标识(appKey) | app\_100xxxxxxxx |

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

### [](https://open.yeepay.com/docs-v3/platform/207.md#%E6%96%B9%E6%A1%88%E4%B8%80%EF%BC%9A%E4%BD%BF%E7%94%A8-sdk%EF%BC%88%E6%8E%A8%E8%8D%90%EF%BC%89)方案一：使用 SDK（推荐）

#### [](https://open.yeepay.com/docs-v3/platform/207.md#java-sdk-%E7%A4%BA%E4%BE%8B)Java SDK 示例

```
// 引入工具类
import com.yeepay.yop.sdk.utils.DigitalEnvelopeUtils;
import com.yeepay.yop.sdk.inter.utils.RSAKeyUtils;


String response = "lVBazeHF7PSSpI7p5BAd6Z4kVZbr_LCP5lT72GA_UQMRHLSx6oa1pK8oFTPMb9Ns3_FyX2smaRW0J13RKithQRvKvKpD3pbmvvkuOfIU9ak2MAwHoTeG_VqCb8NSw-NPDAJKn_GPH4WF5RDx0EMzDzoQ8krOzB3naBZpCqhWmnZqZ-GvyC_NaAuFdBQYSs5LIKkGHwPm7Hsprgpb4uRdnSL0_G7BagRFSe-HS3gbSwJhGxrmI59jsCaiGlW7TfN3FSpL-7C76sW6WjtCotguKZOf9ZgXbLMH0VRUgul5PwALiNEuUmFHebu5RtQONkRvlKlb7haMS6ryL46kradL3Q$_ZhicudE6S4GsolpCyDNVFDqG1IGf2SnwwFW7JeNQChdfSh_qaR88xlk9Adq2YHdV7LStPAJcZE8-z7iFjMOW8QUIXwhA4S_8Q5KW07xT2P1CcTwMBOjYUVM2w6Wls3dNKR3TN5Z06ruoR2ZQdshL579CRIb1ZhjpJPYwei75IMb2L3qPTflEPAGoocijf3W3-A2pbxLTzsG-lt5iJRgFXPkdtJd21XioEhapPyckXyu4Czaj8ByuxWgmTAcwwW-pED0QN0l3INAo1XbwvgIuZqvHE8uM2K2uCUL_dK_196BbhyL-jmdeQ5ZKMEvTP3KIt55GAEkp7sdbbnPtBPnyC5MJpLA8_Qy38wIxV2A8z31rSlx7po0xptjTlub9O4K4OgNjyfSD3XbNiR8Ns5zgK-ii0eHEIZsc-wO20byFmTy031NeONuH2gwtVRgv_vyeoaj5g96o4UOjW3nvmnI5X5_yABm_R2cgwGLTpLL9ouibuWw1-Z-8mY22wt3whrp2ZapYc7ZZ60UXEP4ly_uOg$AES$SHA256";
String privateKeyStr = "MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCtIAOnUbibis2X4rHeM8Kdij11d1Mr+WmOBc5qsBLXtDMGs0D2r/wcqZe9WttShbSoYWOqmD6uGhUrWIsYrag7mYdlI+KT6thhcGmLxM+5IFdYXhIFIYySRBstWti8H5knGs7KuWMkWWzjH/Su21AWYx9R4mSoG1JlAuPeAePrx248NmOhD45FNaRuYTf++Ecmjmbbyo+Ch285N2M3SSXHbbYhsrNpDSWDVfQfFZ4RTTWceLwwuvGJCY8hT+JiK30CN5qa02wYl56l2HeK+zHBBGS6DBUm+qzOoE+eAizLHvKTySExhH8VZa5F2t9T1RPeRlYbCD62VMceuqqRuAD/AgMBAAECggEBAJb+/TDKDgFbpsV6azgqXOuazs/NKzWHa5D7b3WN7GFGQdruLRL7myBEqpv0yqXHCDJz/sGj18dx6FTN/UOg8sJIvdZw3gW1JtSVfvjwx1vn4UaphX4ELN7FmA6O1cn+pU1+DC60Usw5Uscl7/syPT/JZF++3ZvheJOxWZ0gePICopz1grychDlLPk5sVA6rttCJxkTFAEnFFB6qxSsa7hJl3rb6iziVtpUGot1M0kMr1vm+EXx4hh+UJ+xcE1mGy26xw4tsWA8Kla2nUlzQiNqNSnzEcravnB2XqLr53z3axJOYp4hz5QyH1LiNgAiRQNdyM3fhjlQwkTLCjnAJPAECgYEA+UpZ3DTrpdG4uR2HksuEaI7czGr/oXbkxH2sWKPkUovxjPNwQjNpxg9+xNlP33kvMjXFETSGZDEJKk5awTkyKP3lvHQN63jlLv9EV+eZR0XQCYRPGoC5js49M/Lh8qjG5yRjPp5igSLrm7ZBEwpjXZI7hhKi2A0lXhH/Kz/Gaz8CgYEAscjfSgmTzIzJKmdW0lUY6QkgZIYrCX8EdFO3Bb+SJNPZYjL7vcM7L2SpUt6DkeEcI/sVgM2CwXmQNvXWWn9ibdM/DCIK41qkZ9/rOXPcI9R/03GT681Va3oVCyzaGWxbsDigoYoo/WhnppHiRydvvDSq/f4OBYCGIPtyJkXVukECgYBun1nE6A7x5GDOdJYmw/0b0NmWNJz/b50QvJvwMbouDz+/Rn+4QMxdQZ8Fh1F0X3hcFZQ/kElayI/CoEaRm+nwWsrJl85dgaZh9pDDWVihUg+BSZ84qYquHkL2fH9biR3KkFEiBnK7z10yGexCoMd7TFrxoe91ZFACsIXFEWXhTQKBgFogw1H9WPgxxynACbvHeEFrZwiPG/JMei2e4wH/BE+3NlUaE5U4DCESnuRr+bdSr7lt6JDLnqYGwp2aM3jda0DR/vxfpbVsljwywET3/3oKmGLRCXRZPByoX1KzAj4xOKo1ivlZ2T3eV+2Rt2zrCTIYYTcyPFl9toGx90R/0sIBAoGBAOHc1x61ofaUPKQvY40A54VOuKTLDKcsHmlZ+mKWasFKSykQJ76Np42ctlZ+ucUjT66jPD4/kr7kwqPfOco9FOSOhqG3l+0qJnE8lo8+UEbuVA4ZWdflI1mdUzPFs1r0f3N1YasMRM5cBJUEGm8SjoUshKLLKOwTakGvnmoJpLpu";
String appKey = "app_100276759800045";
PrivateKey isvPrivateKey = RSAKeyUtils.string2PrivateKey(privateKeyStr);

// 根据自身情况从下列三种方式中选择其一
// 解密方法1：走程序配置的默认appKey，默认私钥
String plaintText = DigitalEnvelopeUtils.decrypt(response, "RSA2048");

// 解密方法2：走指定appKey配置的私钥
String plaintTextWithAppKey = DigitalEnvelopeUtils.decrypt(
    response, appKey, "RSA2048"
);

// 解密方法3：走指定私钥
String plaintTextWithPrivateKey = DigitalEnvelopeUtils.decrypt(
    response, isvPrivateKey
);
```

#### [](https://open.yeepay.com/docs-v3/platform/207.md#php-sdk-%E7%A4%BA%E4%BE%8B)PHP SDK 示例

```
// 引入工具类
use Yeepay\Yop\Sdk\V1\Util\YopSignUtils;

/**
 * @test rsa回调解密
 */
function rsa_callback(){
    //返回的密文
    $source='xxx';
    /*商户私钥*/
    $private_Key='xxx';
    /*YOP公钥*/
 $yop_public_Key='MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA6p0XWjscY+gsyqKRhw9MeLsEmhFdBRhT2emOck/F1Omw38ZWhJxh9kDfs5HzFJMrVozgU+SJFDONxs8UB0wMILKRmqfLcfClG9MyCNuJkkfm0HFQv1hRGdOvZPXj3Bckuwa7FrEXBRYUhK7vJ40afumspthmse6bs6mZxNn/mALZ2X07uznOrrc2rk41Y2HftduxZw6T4EmtWuN2x4CZ8gwSyPAW5ZzZJLQ6tZDojBK4GZTAGhnn3bg5bBsBlw2+FLkCQBuDsJVsFPiGh/b6K/+zGTvWyUcu+LUj2MejYQELDO3i2vQXVDk7lVi2/TcUYefvIcssnzsfCfjaorxsuwIDAQAB';
    //还原出原文
    $response = YopSignUtils::decrypt($source, $private_Key, $yop_public_Key);

    print_r($response);
}
```

##### [](https://open.yeepay.com/docs-v3/platform/207.md#%E7%9B%B8%E5%85%B3%E5%B7%A5%E5%85%B7%E7%B1%BB)相关工具类

其中`YopSignUtils`请查看[源码](https://github.com/yop-platform/yop-php-sdk/blob/main/src/Util/YopSignUtils.php)

#### [](https://open.yeepay.com/docs-v3/platform/207.md#%E4%BC%98%E5%8A%BF)优势

-   封装了复杂的加解密逻辑
-   自动处理密钥管理
-   持续更新和维护
-   经过充分测试验证

### [](https://open.yeepay.com/docs-v3/platform/207.md#%E6%96%B9%E6%A1%88%E4%BA%8C%EF%BC%9A%E4%BD%BF%E7%94%A8%E4%BA%8B%E4%BB%B6%E7%BD%91%E5%85%B3)方案二：使用事件网关

参考 [商户通知快速对接网关](https://open.yeepay.com/docs-v3/platform/2238.md) 实现。

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
-   平台BASE64编码采用的URL安全模式(将非法字符'+'和'/'转为'-'和'\_', 见RFC3548)，部分语言解码时须先进行手动替换还原，伪代码示例：`$data.replaceAll("-", "+").replaceAll("_", "/")`

## [](https://open.yeepay.com/docs-v3/platform/207.md#%E5%93%8D%E5%BA%94%E8%A7%84%E8%8C%83)响应规范

### [](https://open.yeepay.com/docs-v3/platform/207.md#%E6%88%90%E5%8A%9F%E5%93%8D%E5%BA%94)成功响应

-   HTTP状态码：200
-   响应内容：SUCCESS
-   格式要求：纯文本，无需加密签名

### [](https://open.yeepay.com/docs-v3/platform/207.md#%E5%A4%B1%E8%B4%A5%E5%93%8D%E5%BA%94)失败响应

-   HTTP状态码：4xx 或 500
-   响应内容：自定义错误信息
-   用途：用于通知重试判断

## [](https://open.yeepay.com/docs-v3/platform/207.md#%E6%9C%80%E4%BD%B3%E5%AE%9E%E8%B7%B5)最佳实践

### [](https://open.yeepay.com/docs-v3/platform/207.md#%E5%AE%9E%E7%8E%B0%E5%BB%BA%E8%AE%AE)实现建议

1.  优先使用官方SDK
2.  做好异常处理
3.  实现幂等性控制
4.  记录详细日志
5.  设置合理超时

### [](https://open.yeepay.com/docs-v3/platform/207.md#%E5%AE%89%E5%85%A8%E5%BB%BA%E8%AE%AE)安全建议

1.  妥善保管私钥
2.  验证每次签名
3.  检查通知来源
4.  加密敏感数据

### [](https://open.yeepay.com/docs-v3/platform/207.md#%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96)性能优化

1.  使用线程池
2.  异步处理通知
3.  合理设置超时
4.  做好限流保护

## [](https://open.yeepay.com/docs-v3/platform/207.md#%E6%95%85%E9%9A%9C%E6%8E%92%E9%99%A4)故障排除

### [](https://open.yeepay.com/docs-v3/platform/207.md#%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98)常见问题

1.  签名验证失败
    -   检查密钥是否正确
    -   确认签名算法
    -   验证数据完整性
2.  解密失败
    -   确认密钥格式
    -   检查加密算法
    -   验证数据编码
3.  响应超时
    -   优化处理逻辑
    -   增加超时时间
    -   实现异步处理