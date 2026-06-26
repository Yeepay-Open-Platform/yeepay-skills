# 鉴权认证机制(RSA)

本文适合的阅读人群

-   YOP 平台开发者
-   YOP SDK 编写者

## [](https://open.yeepay.com/docs-v3/platform/203.md#%E4%B8%80%E3%80%81%E9%89%B4%E6%9D%83%E8%AE%A4%E8%AF%81%E4%B8%B2authorization)一、鉴权认证串Authorization

```
Authorization: securityReq authString/signedHeaders/signature
```

鉴权认证串`Authorization`示例：

```
Authorization: YOP-RSA2048-SHA256 yop-auth-v3/app_100123456789/2021-12-08T11:59:16Z/1800/content-type;x-yop-appkey;x-yop-content-sha256;x-yop-request-id/pOVoj1mI5bqYQQKTlE8iIYm0DKHpL5Q2vscY03lwP3KXpHRPJlKQfEOgpW-jfsyWf46c-uPehOZfOke7vla3rY6FtAVeoX0g8319WEdvQVgXwzW7xPtp5er4No8gpCrizsbmp2Fw7NSjASGsCaLEEri8iHsvN_TgFsGEIUf9JtQYWkoqdOh6vK1-xZvisp2ePAg2GKHy1Y0tbkXbzO9Bp_dBkgEHI7B2N80mzn-tEZ0xi6uMKSSvI8VPK14Rys8pJ4c4I4RZjoDEnxxsG2Z977RGtCuf_3RvrwohxECO5iF8BMjJF89nqi50QaZtS2mx32649_cORFLbD8VFpQhyxA$SHA256
```

### [](https://open.yeepay.com/docs-v3/platform/203.md#1%E3%80%81%E5%AE%89%E5%85%A8%E9%9C%80%E6%B1%82securityreq)1、安全需求securityReq

YOP支持的安全需求`securityReq`：

-   YOP-RSA2048-SHA256

### [](https://open.yeepay.com/docs-v3/platform/203.md#2%E3%80%81%E8%AE%A4%E8%AF%81%E5%AD%97%E7%AC%A6%E4%B8%B2authstring)2、认证字符串authString

认证字符串authString，由协议版本`protocolVersion`、应用标识`appKey`、日期值`timestamp`和签名有效时长`expiredSeconds`组成。 确保 YOP 平台在收到请求时能使用相同的签名协议并匹配您计算出的签名且在有效期内。否则，您的请求将被拒绝。

```
authString: protocolVersion/appKey/timestamp/expiredSeconds
```

示例：

```
authString: yop-auth-v3/app_100123456789/2021-12-08T11:59:16Z/1800
```

#### [](https://open.yeepay.com/docs-v3/platform/203.md#a%E3%80%81%E5%8D%8F%E8%AE%AE%E7%89%88%E6%9C%ACprotocolversion%EF%BC%8C%E4%BB%A5'%2F'%E7%BB%93%E5%B0%BE)a、协议版本protocolVersion，以'/'结尾

目前固定为`yop-auth-v3`，以'/'结尾：

```
yop-auth-v3/
```

#### [](https://open.yeepay.com/docs-v3/platform/203.md#b%E3%80%81%E5%BA%94%E7%94%A8%E6%A0%87%E8%AF%86appkey%EF%BC%8C%E4%BB%A5'%2F'%E7%BB%93%E5%B0%BE)b、应用标识appKey，以'/'结尾

您的`appKey`，以'/'结尾如：

```
app_100123456789/
```

#### [](https://open.yeepay.com/docs-v3/platform/203.md#c%E3%80%81%E6%97%A5%E6%9C%9F%E5%80%BCtimestamp%EF%BC%8C%E4%BB%A5'%2F'%E7%BB%93%E5%B0%BE)c、日期值timestamp，以'/'结尾

日期值`timestamp`遵循 ISO8601 基本格式，即`yyyy-MM-ddTHH:mm:ssZ`，以'/'结尾。该日期值`timestamp`必须与您在所有步骤中使用的值保持一致，比如`x-yop-date`标头。

```
2021-12-08T11:59:16Z/
```

#### [](https://open.yeepay.com/docs-v3/platform/203.md#d%E3%80%81%E7%AD%BE%E5%90%8D%E6%9C%89%E6%95%88%E6%97%B6%E9%95%BFexpiredseconds)d、签名有效时长expiredSeconds

单位为秒，无需以'/'结尾如：

```
1800
```

### [](https://open.yeepay.com/docs-v3/platform/203.md#3%E3%80%81%E7%AD%BE%E5%90%8D%E5%A4%B4signedheaders)3、签名头signedHeaders

签名头`signedHeaders`由规范标头`canonicalHeaders`中的标头名称列表组成。签名头`signedHeaders`的作用是，告知 YOP 平台请求中的哪些标头是签名过程的一部分。 以下是签名头`signedHeaders`的伪代码格式。Lowercase 表示将所有字符转换为小写字母的函数。Sort 表示按照标头名称的 ASCII 顺序对所有标头进行升序排序。多个标头名称以';'分隔，结尾处不加';'。

```
Sort(Lowercase(HeaderName0);Lowercase(HeaderName1); ... Lowercase(HeaderNameN))
```

示例：

```
signedHeaders: content-type;x-yop-appkey;x-yop-content-sha256;x-yop-request-id
```

### [](https://open.yeepay.com/docs-v3/platform/203.md#4%E3%80%81%E7%AD%BE%E5%90%8Dsignature)4、签名signature

签名`signature`，由商户私钥`isvPrivateKey`、规范请求`canonicalRequest`和签名算法`SIGNER`生成。其中，签名算法`SIGNER`通常为 `SHA256withRSA`算法。 签名过程是，商户用摘要算法对规范请求`canonicalRequest`生成摘要，然后用自己的私钥对这个摘要进行加密，得到的就是签名`signature`。伪代码如下：

```
SIGNER(isvPrivateKey, canonicalRequest)
```

#### [](https://open.yeepay.com/docs-v3/platform/203.md#a%E3%80%81%E8%A7%84%E8%8C%83%E8%AF%B7%E6%B1%82canonicalrequest)a、规范请求canonicalRequest

规范请求`canonicalRequest`，由认证字符串`authString`、Http请求方法`httpRequestMethod`、规范URI`canonicalURI`、规范查询字符串`canonicalQueryString`和规范标头`canonicalHeaders`组成。用于生成摘要。

```
authString + "\n" +
httpRequestMethod + "\n" +
canonicalURI + "\n" +
canonicalQueryString + "\n" +
canonicalHeaders
```

示例：

```
yop-auth-v3/app_100123456789/2021-12-08T11:59:16Z/1800
POST
/rest/v1.0/trade/order

content-type:application%2Fx-www-form-urlencoded%3B%20charset%3Dutf-8
x-yop-appkey:app_100123456789
x-yop-content-sha256:d9c89c72b774c89e2d15c19fc3326e7c9508d605a7974ab0a636d9121c97e7ff
x-yop-request-id:d48782ac-93c1-466e-b417-f7a71e4965f0
```

##### [](https://open.yeepay.com/docs-v3/platform/203.md#%E2%91%A0-%E8%AE%A4%E8%AF%81%E5%AD%97%E7%AC%A6%E4%B8%B2authstring%EF%BC%8C%E4%BB%A5'%5Cn'%E6%8D%A2%E8%A1%8C%E7%AC%A6%E7%BB%93%E5%B0%BE)① 认证字符串authString，以'\\n'换行符结尾

[见上文](https://open.yeepay.com/docs-v3/platform/203.md#test2)，以'\\n'换行符结尾，示例：

```
yop-auth-v3/app_100123456789/2021-12-08T11:59:16Z/1800 + "\n"
```

##### [](https://open.yeepay.com/docs-v3/platform/203.md#%E2%91%A1-http%E8%AF%B7%E6%B1%82%E6%96%B9%E6%B3%95httprequestmethod%EF%BC%8C%E4%BB%A5'%5Cn'%E6%8D%A2%E8%A1%8C%E7%AC%A6%E7%BB%93%E5%B0%BE)② Http请求方法httpRequestMethod，以'\\n'换行符结尾

Http请求方法`httpRequestMethod`，分为`POST`和`GET`两种方式。以'\\n'换行符结尾，示例：

```
POST + "\n"
```

##### [](https://open.yeepay.com/docs-v3/platform/203.md#%E2%91%A2-%E8%A7%84%E8%8C%83uri-canonicaluri%EF%BC%8C%E4%BB%A5'%5Cn'%E6%8D%A2%E8%A1%8C%E7%AC%A6%E7%BB%93%E5%B0%BE)③ 规范URI canonicalURI，以'\\n'换行符结尾

规范URI`canonicalURI`，是 API 的请求路径。以'\\n'换行符结尾，示例：

```
/rest/v2.0/opr/queryorder + "\n"
```

##### [](https://open.yeepay.com/docs-v3/platform/203.md#%E2%91%A3-%E8%A7%84%E8%8C%83%E6%9F%A5%E8%AF%A2%E5%AD%97%E7%AC%A6%E4%B8%B2canonicalquerystring%EF%BC%8C%E4%BB%A5'%5Cn'%E6%8D%A2%E8%A1%8C%E7%AC%A6%E7%BB%93%E5%B0%BE)④ 规范查询字符串canonicalQueryString，以'\\n'换行符结尾

针对`GET`请求，或者`POST`请求且内容类型为`json`，规范查询字符串`canonicalQueryString`遵循 RFC 3986，构建步骤如下：

1.  对每个参数名称key 和参数值value 进行 URL 编码；
2.  用'='拼接 URL 编码后的参数名称key 和参数值value，如果参数没有参数值value，value为空字符串。例如：urlencode(key1)=urlencode(value1)，urlencode(key2)=urlencode(value2)；
3.  按照参数名称key 的 ASCII 顺序，对拼接后的参数对进行升序排序Sort。例如，以大写字母 F（ASCII 代码 70，10进制）开头的参数名称key 排在以小写字母 b（ASCII 代码 98，10进制）开头的参数名称key 之前；
4.  用'&'拼接排序后的多个参数对，最后一个参数对后面无需拼接'&'。

**注意：**

-   如果请求没有URL查询字符串(比如`json`类型请求，通常只会在请求体放参数，不会放在url上)，则规范查询字符串`canonicalQueryString`为空字符串。
-   针对`POST`请求，且内容类型为`form`，即`application/x-www-form-urlencoded`或者`multipart/form-data`的请求，规范查询字符串`canonicalQueryString`一律为空字符串。
-   不同编程语言对空格URL编码结果不一样，须统一转为`%20`

规范查询字符串`canonicalQueryString`伪代码如下，以'\\n'换行符结尾：

```
Sort(urlencode(key1)=urlencode(value1)&urlencode(key2)=urlencode(value2)&...&urlencode(keyN)=urlencode(valueN)) + "\n"
```

##### [](https://open.yeepay.com/docs-v3/platform/203.md#%E2%91%A4-%E8%A7%84%E8%8C%83%E6%A0%87%E5%A4%B4canonicalheaders)⑤ 规范标头canonicalHeaders

规范标头`canonicalHeaders`，由 HTTP 请求头中标头名称和标头值拼接组成。标头必须包含 `x-yop-appkey`、`x-yop-request-id`、`x-yop-content-sha256`。 以下是规范标头 `canonicalHeaders`的伪代码格式。urlencode 表示 URL 编码。Lowercase 表示将所有字符转换为小写字母的函数。Trimall 表示删除前后的多余空格并将连续空格转换为单个空格。Sort 表示按照标头名称的 ASCII 顺序对所有标头进行升序排序。标头名称和标头值以':'拼接，每个标头后面拼接'\\n'，最后一个标头后面无需拼接'\\n'。

```
Sort(urlencode(Lowercase(Trimall(HeaderName0))) + ":" + urlencode(Trimall(HeaderValue0)) + "\n" +
urlencode(Lowercase(Trimall(HeaderName1))) + ":" + urlencode(Trimall(HeaderValue1)) + "\n" +
...
urlencode(Lowercase(Trimall(HeaderNameN))) + ":" + urlencode(Trimall(HeaderValueN)))
```

其中，`x-yop-content-sha256`由请求参数组成，构建步骤如下：

1.  构建请求参数字符串A 针对`GET`请求，请求参数字符串A 为空字符串。 针对`POST`请求，且内容类型为`json`，请求参数字符串A 为`json`字符串。 对于`POST`请求，且内容类型为`form`，规则如下： a. 拼接非文件类型的参数键值对，对每个参数名称key 和参数值value 进行 URL 编码； b. 用'='拼接 URL 编码后的参数名称key 和参数值value。如果参数没有参数值value，value为空字符串。例如：urlencode(key1)=urlencode(value1)，urlencode(key2)=urlencode(value2)； c. 按照参数名称key 的 ASCII 顺序，对拼接后的参数对进行升序排序Sort。例如，以大写字母 F（ASCII 代码 70，10进制）开头的参数名称key 排在以小写字母 b（ASCII 代码 98，10进制）开头的参数名称key 之前； d. 用'&'拼接排序后的多个参数对，最后一个参数对后面无需拼接'&'。
2.  用 sha256算法对请求参数字符串A 计算摘要，并转为 hex值。伪代码为`hex(sha256(A))`

注意：

-   不同编程语言对空格URL编码结果不一样，须统一转为`%20`

示例： 原始标头：

```
Host:openapi.yeepay.com\n
Content-Type:application/x-www-form-urlencoded; charset=utf-8\n
My-header1:    a   b   c  \n
X-Yop-Appkey:app_10012481831\n
X-Yop-Date:20170124T021133Z\n
x-yop-session-id:01e447af-9749-4075-8e6c-17df519f2720\n
My-Header2:    "a   b   c"  \n
```

规范标头 `canonicalHeaders`：

```
content-type:application%2Fx-www-form-urlencoded%3B%20charset%3Dutf-8\n
host:openapi.yeepay.com\n
my-header1:a b c\n
my-header2:"a b c"\n
x-yop-appkey:app_10012481831\n
x-yop-date:20170124T021133Z\n
x-yop-request-id:01e447af-9749-4075-8e6c-17df519f2720\n
```

#### [](https://open.yeepay.com/docs-v3/platform/203.md#b%E3%80%81%E8%AE%A1%E7%AE%97%E7%AD%BE%E5%90%8D)b、计算签名

计算签名的具体步骤如下，以 `YOP-RSA-SHA256`为例：

1.  将规范请求`canonicalRequest`转换为字节数组byte\[\]；
2.  使用 java.security 包下的 Signature 类构造签名工具，签名方法使用“SHA256withRSA”；
3.  使用initSign方法导入商户私钥`isvPrivateKey`和字节数组byte\[\]；
4.  使用sign方法生成签名；
5.  使用 Base64.encodeBase64URLSafeString 对签名进行编码；
6.  在后面拼接“$SHA256”字符串。

#### [](https://open.yeepay.com/docs-v3/platform/203.md#c%E3%80%81%E8%AE%A1%E7%AE%97%E7%AD%BE%E5%90%8D%E7%A4%BA%E4%BE%8B)c、计算签名示例

规范请求`canonicalRequest`：

```
yop-auth-v3/app_100123456789/2021-12-08T11:59:16Z/1800
POST
/rest/v1.0/trade/order

content-type:application%2Fx-www-form-urlencoded
x-yop-appkey:app_100123456789
x-yop-content-sha256:d9c89c72b774c89e2d15c19fc3326e7c9508d605a7974ab0a636d9121c97e7ff
x-yop-request-id:d48782ac-93c1-466e-b417-f7a71e4965f0
```

商户私钥`isvPrivateKey`：

```
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC+YgO139eaN/Cjd3mTE4ePwqSI1F8ubXojffiwXy+mEiYGR4YscIcPQiYUGb2YpZQHa/Zoz+OyuloBCQBS1C8cva91KJojzUA4ll88vj8JF64G3P6WZh8acoUdNo8WRWfj9TVMMPBtzVcLK2bujrfx/t5Sggi66IK1FthcEtrkN8atA3rLj4OhNbZOzQRadecZDkeVelXU5LvNvBhBwO1cJ2Agr7ezkUaQENau/TSIAKdGJt607daB/MDgQdNrCNc/lUnp9+a8BUNYNCyJQZJKeAyVqFO73c/v3dlRaAUUfoH+hIbmS0g3aSpmxexvka6BFEld16wRG41VSGFhXbkRAgMBAAECggEASC9/uqkp5ZaKTmDRnvuLre2eVyc3A7KM2gI8lhsxROWit0TNUfJEs3tgVsS/x64YZ4v+/RS+ABl6YOQZ1E4RovMlIOYJM8PyMsKJT83OttLcsEuA2GPWLT/4yu/R5x7f2mYyFDaGIwv1kg2d1JwWkNITV/Nn/f6E+Ma1uIuJpXf9CVxIokfWFMstGNAGw/871V1qKAIDRsWTN4gTT4aRK/FPvQNzHv4nSEtlYdAYE8r53MaAZfigfFSOGowPFegyktQJXfmAUOhZbRhRZGQqcwU/1M5/TKu1cJECM/N/1ttjMlPNamQmONawq8dqfpK7a45YyWgyaadN2flA4/nWdQKBgQDWwrQsxnoVcoL88fFZYwol/5RYG+eA9zMffCi39KsKBU6ePbLlORYd2D/f2nDno6Uz2tFnUoRLvKy3ZINuIdN/jgD4ob69tk7XIKQSzh9Tv2485P8PasublywgdG9LnYk8qbF1VDsOkgecSSh7xG8Rz/U9p9kI5/wt3OOc0brjKwKBgQDi8PDtFziZNVSC58BcaWpAfZyDwB8X56BtNz1890zVOvF8ali6GUwgZkcH8KsQXhu+1YkmnC/YS6H0s+ZE4CIP6FGw5Z8988UB2i+oB0BMK8l8WDFOgPyW2n9l6502Qx1tqD3alekcksFsIlUgP9sVc5vtAKUPtNgguhRcP6mmswKBgQDCkkSLDIcvR0BFyy3OvlxDcPsFmMJ1pYE71VFO2Ozdd1FzLJMX+lB/WZ0FQvNn6muSP33ZDnmt5JLW1Mn+zcbAmfdnS6N0XeewIHKGVxkq1xUZNp+faDJwFNZ10QfEikX8IAIXOukGmmcqwV1cROwcRzz5T0jjOMrRAn91ZM7dYQKBgC91JVzfU0WuwlqRrkdlAAQ2gGmI3re4B3NvbttYN+gLaH6VGrLoIWRRHx+I86z7kR/KNeEuHk9EGb07dbcHi/f5pEOy8ScaeCNYBklEIu0K5xqqsrzw+mFtleCxcfHr/RZ2bWDtoo8IHYzIbTbOQ7lrsLrSPLJZJi1J3IIiCg9DAoGAOxT0qqTUADmSvwnzyQAYJ5sFI36eMcKqwkBuqb7ZQiLFNv1WZROrkeGin2ishntFKsIUtrpeikPjNP2AX6X0UuSQsUNNWx1zYpSlNUyGtGueYhmmP+7plPN5BhuJ3Ba6IYC/uI/l1tJP3S4e/xa/rCcNrf36RzK+PLLPq/uPAaY=
```

签名`signature`：

```
pOVoj1mI5bqYQQKTlE8iIYm0DKHpL5Q2vscY03lwP3KXpHRPJlKQfEOgpW-jfsyWf46c-uPehOZfOke7vla3rY6FtAVeoX0g8319WEdvQVgXwzW7xPtp5er4No8gpCrizsbmp2Fw7NSjASGsCaLEEri8iHsvN_TgFsGEIUf9JtQYWkoqdOh6vK1-xZvisp2ePAg2GKHy1Y0tbkXbzO9Bp_dBkgEHI7B2N80mzn-tEZ0xi6uMKSSvI8VPK14Rys8pJ4c4I4RZjoDEnxxsG2Z977RGtCuf_3RvrwohxECO5iF8BMjJF89nqi50QaZtS2mx32649_cORFLbD8VFpQhyxA$SHA256
```

附本示例的请求报文：

```
POST /yop-center/rest/v1.0/trade/order HTTP/1.1
Host: openapi.yeepay.com
Authorization: YOP-RSA2048-SHA256 yop-auth-v3/app_100123456789/2021-12-08T11:59:16Z/1800/content-type;x-yop-appkey;x-yop-content-sha256;x-yop-request-id/pOVoj1mI5bqYQQKTlE8iIYm0DKHpL5Q2vscY03lwP3KXpHRPJlKQfEOgpW-jfsyWf46c-uPehOZfOke7vla3rY6FtAVeoX0g8319WEdvQVgXwzW7xPtp5er4No8gpCrizsbmp2Fw7NSjASGsCaLEEri8iHsvN_TgFsGEIUf9JtQYWkoqdOh6vK1-xZvisp2ePAg2GKHy1Y0tbkXbzO9Bp_dBkgEHI7B2N80mzn-tEZ0xi6uMKSSvI8VPK14Rys8pJ4c4I4RZjoDEnxxsG2Z977RGtCuf_3RvrwohxECO5iF8BMjJF89nqi50QaZtS2mx32649_cORFLbD8VFpQhyxA$SHA256
x-yop-request-id: d48782ac-93c1-466e-b417-f7a71e4965f0
User-Agent: java/4.1.8/Mac_OS_X/10.16/Java_HotSpot(TM)_64-Bit_Server_VM/25.291-b10/1.8.0_291/zh/
x-yop-appkey: app_100123456789
x-yop-content-sha256: d9c89c72b774c89e2d15c19fc3326e7c9508d605a7974ab0a636d9121c97e7ff
Content-Type: application/x-www-form-urlencoded
Content-Length: 108
Connection: Keep-Alive
Accept-Encoding: gzip,deflate

orderId=1234321&orderAmount=100.05&notifyUrl=https%253A%252F%252Fxxx.com%252Fnotify&parentMerchantNo=1234321
```
