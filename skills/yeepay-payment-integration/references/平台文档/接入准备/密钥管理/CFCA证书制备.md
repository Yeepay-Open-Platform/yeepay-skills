# 制备CFCA证书

## 一、制备前的准备工作：

1. 准备好登录平台的【账号信息】
2. 下载好CFCA证书下载与制备证书所需的[【离线生成工具】](https://open.yeepay.com/docs-v3/platform/2981.md)

## 二、申请CFCA证书

获取CFCA证书需要在[控制台](https://open.yeepay.com/developer-center)进行操作，详细步骤如下：

1.进入【[控制台](https://open.yeepay.com/developer-center)】->【开发服务】->【CFCA证书】，点击【立即申请】。 申请证书1  
  


2.确认申请信息，选择“密钥算法”后，点击“立即申请”

- 若本地生成的是RSA2048类型的密钥，请选择：国际（RSA2048）
- 若本地生成的是SM2-256类型的密钥，请选择：商密（SM2）

申请证书2.png

4.验证绑定手机

申请证书3.png

5.申请成功，获得【证书序列号】与【证书授权码】。

申请证书4.png

## 三、在线激活CFCA证书

注意事项：

- 使用此功能前，需要到【[控制台](https://open.yeepay.com/developer-center)】申请CFCA证书。[查看申请方法](https://open.yeepay.com/docs-v3/platform/3832.md)
- CFCA证书类型包括：RSA-2048（国际）、SM2-256（商密）：
- 生成的私钥或证书需妥善保管，避免遗失，不要泄露。

操作步骤：

1.（证书申请成功后立即激活）；申请成功页面点击立即激活；

申请证书4.png

2.（在证书列表激活）：登录[控制台](https://open.yeepay.com/developer-center)，点击证书列表后点击立即激活。

申请证书5.png

3.安全验证，验证手机号码 申请证书3.png

4.输入P10文件激活。支持手动输入，也支持上传文件。

申请证书6.png

申请证书7.jpg

4.点击激活后，出现激活结果。激活成功后点击立即下载，可以得到后缀为.cer的公钥证书，下一步进行配置。

## 四、配置应用的 CFCA 公钥证书

**配置国际密钥（RSA）**：[配置国际密钥（RSA）](https://open.yeepay.com/docs/open/developer/prepare/key-config-rsa)。

**配置商密密钥（SM）**： [配置商密密钥（SM）](https://open.yeepay.com/docs/open/developer/prepare/key-config-sm)。

## 五、从私钥证书（.pfx格式）导出私钥

注意：

1. 请将导出的私钥证书文件（.pfx格式），转交给技术人员，由技术人员解析密钥后，将证书部署到服务器上。
2. 请务必妥善保管证书及私钥，因为私钥文件只能通过证书工具导出，若私钥丢失，则无法找回。

**Java SDK 支持“密钥文本”和“p12文件”2种方式，其他语言请根据实际情况选择。具体描述如下：**

### 1、密钥文本方式

1.安装密钥解析工具 OpenSSL

OpenSSL是用于安全通信的著名开源密码学工具包，包括主要的密码算法、常见密码和证书封装功能。官网下载地址： [https://www.openssl.org/source/。](https://www.openssl.org/source/%E3%80%82)

OpenSSL官网没有提供windows版本的安装包，可以选择其他开源平台提供的工具，比如 [Win32OpenSSL](http://slproweb.com/products/Win32OpenSSL.html)。

A.设置环境变量:例如工具安装在C:OpenSSL-Win64，则将“C:OpenSSL-Win64bin;”追加到现有Path值之前，原有内容务必保留。 B.验证安装:打开命令行程序cmd，输入：openssl version，如输出版本号表示openssl工具安装成功。

2.打开终端工具，进入pfx证书文件所在目录

3.从导出的pfx证书文件导出密钥对：

```
openssl pkcs12 -in original.pfx -nocerts -nodes -out client.key
```

4.从密钥对提取私钥 pkcs1

```
// client_pri.txt 的内容即为私钥文本
openssl rsa -in client.key -out client_pri.txt
```

5.获取pkcs8模式的私钥

```
openssl pkcs8 -topk8 -inform PEM -in client_pri.txt -outform PEM -nocrypt
```

### 2、p12 证书方式

1.安装 JRE 环境

2.打开终端工具，进入pfx证书文件所在目录

2.从导出的pfx证书文件导出p12文件：

```
keytool -importkeystore -destkeystore client_pri.p12 -deststoretype pkcs12 -srckeystore original.pfx
```