# 配置国际密钥（RSA）

## [](https://open.yeepay.com/docs-v3/platform/193.md#%E4%B8%80%E3%80%81%E9%85%8D%E7%BD%AE%E5%89%8D%E5%87%86%E5%A4%87%E5%B7%A5%E4%BD%9C)一、配置前准备工作

### [](https://open.yeepay.com/docs-v3/platform/193.md#1.%E5%87%86%E5%A4%87%E5%A5%BD%E7%99%BB%E5%BD%95%E5%B9%B3%E5%8F%B0%E7%9A%84%E8%B4%A6%E5%8F%B7%E4%BF%A1%E6%81%AF)1.准备好登录平台的账号信息

### [](https://open.yeepay.com/docs-v3/platform/193.md#2.%E5%B7%B2%E5%88%B6%E5%A4%87%E5%A5%BD%E7%9A%84%E5%95%86%E6%88%B7%E5%85%AC%E9%92%A5-%E6%88%96-cfca-%E8%AF%81%E4%B9%A6)2.已制备好的商户公钥 或 CFCA 证书

若你已开通或计划开通的产品接口中，有要求使用CFCA 证书的，例如：代付代发、企业付款接口，请先完成CFCA 证书的制备；

-   制备商户密钥，具体参见[制备商户密钥](https://open.yeepay.com/docs/v2/platform/sign_rsa/generate-rsa-key-pairs "如何配置RSA密钥")
-   制备CFCA证书，具体参见[制备CFCA国际证书（RSA）](https://open.yeepay.com/docs/open/developer/prepare/cfca-make "如何制备CFCA证书")

## [](https://open.yeepay.com/docs-v3/platform/193.md#%E4%BA%8C%E3%80%81%E5%9B%BD%E9%99%85%E5%AF%86%E9%92%A5%EF%BC%88rsa%EF%BC%89%E9%85%8D%E7%BD%AE)二、国际密钥（RSA）配置

### [](https://open.yeepay.com/docs-v3/platform/193.md#%E7%AC%AC%E4%B8%80%E6%AD%A5%EF%BC%9A%E7%99%BB%E5%BD%95%E5%B9%B3%E5%8F%B0%E8%BF%9B%E5%85%A5%EF%BC%8C%E5%AF%86%E9%92%A5%E9%85%8D%E7%BD%AE%E9%A1%B5%E9%9D%A2)第一步：登录平台进入，密钥配置页面

1.  进入 【[控制台](https://open.yeepay.com/home?redirect=/developer-center)】>【我的应用】>【密钥配置】，公钥类型选择：【国际（RSA2048）】

![1.png](https://open.yeepay.com/attachments/access?fileId=170FlRHzNNA) 2. 若密钥格式选择【文本】，请录入RSA格式的【商户公钥】内容

![2.png](https://open.yeepay.com/attachments/access?fileId=170GjgyRfYu)

3.  若密钥格式选择【证书】，请在【公钥证书】中选择【RSA格式的CFCA证书】

-   若列表中没有可用RSA格式的证书：请先完成 CFCA证书的制备[查看制备方法](https://open.yeepay.com/docs/open/developer/prepare/cfca-make)
-   若想使用非CFCA证书：请手工 【上传证书文件】，证书格式支持 .p7b、.cer。![密钥配置RSA3.png](https://open.yeepay.com/attachments/access?fileId=170HAdvc1tg)

### [](https://open.yeepay.com/docs-v3/platform/193.md#%E7%AC%AC%E4%BA%8C%E6%AD%A5%EF%BC%9A%E9%AA%8C%E8%AF%81%E7%BB%91%E5%AE%9A%E6%89%8B%E6%9C%BA%E5%8F%B7)第二步：验证绑定手机号

![密钥配置RSA4.png](https://open.yeepay.com/attachments/access?fileId=170HJZs6Cqe)

### [](https://open.yeepay.com/docs-v3/platform/193.md#%E7%AC%AC%E4%B8%89%E6%AD%A5%EF%BC%9A%E5%AF%86%E9%92%A5%E8%AE%BE%E7%BD%AE%E6%88%90%E5%8A%9F)第三步：密钥设置成功

![密钥配置RSA5.png](https://open.yeepay.com/attachments/access?fileId=170HKhN06Do)

## [](https://open.yeepay.com/docs-v3/platform/193.md#%E4%B8%89%E3%80%81%E4%BF%AE%E6%94%B9%E5%95%86%E6%88%B7%E5%85%AC%E9%92%A5)三、修改商户公钥

在私钥泄漏等情况下，开发者可能需要变更密钥，此时可以在密钥配置页面进行变更。

1.  在 【[控制台](https://open.yeepay.com/home?redirect=/developer-center)】>【 我的应用】>【密钥配置】 页面，点击【设置公钥】按钮![密钥配置RSA6.png](https://open.yeepay.com/attachments/access?fileId=170HLzAHTge)
2.  填写新【商户公钥】![密钥配置RSA7.png](https://open.yeepay.com/attachments/access?fileId=170HLzAHTge)
3.  验证绑定手机号![密钥配置RSA8.png](https://open.yeepay.com/attachments/access?fileId=170INQWsZZg)
4.  修改成功![密钥配置RSA9.jpeg](https://open.yeepay.com/attachments/access?fileId=170JDLczpdg)

## [](https://open.yeepay.com/docs-v3/platform/193.md#%E5%9B%9B%E3%80%81%E5%AF%86%E9%92%A5%E5%8F%98%E6%9B%B4%E5%90%8A%E9%94%80)四、密钥变更吊销

变更密钥后，密钥配置页面弹出提示，点击“立即吊销”，进行二次确认，确认后，即可吊销旧密钥。如图所示： ![密钥配置RSA10.png](https://open.yeepay.com/attachments/access?fileId=170JFFFkwsa)

## [](https://open.yeepay.com/docs-v3/platform/193.md#%E4%BA%94%E3%80%81%E5%AF%86%E9%92%A5%E5%8F%98%E6%9B%B4%E6%92%A4%E9%94%80)五、密钥变更撤销

变更密钥后，密钥配置页面弹出提示，点击“撤销变更”，进行二次确认，确认后，即可撤销新配置的密钥。如图所示： ![密钥配置RSA11.png](https://open.yeepay.com/attachments/access?fileId=170JGllXiW8)

## [](https://open.yeepay.com/docs-v3/platform/193.md#%E5%85%AD%E3%80%81%E6%91%98%E8%A6%81%E4%BF%A1%E6%81%AF%EF%BC%88%E6%95%B0%E5%AD%97%E7%AD%BE%E5%90%8D%EF%BC%89)六、摘要信息（数字签名）

平台支持查看商户公钥的摘要信息 ![密钥配置RSA12.png](https://open.yeepay.com/attachments/access?fileId=170JIz8pRLs) ![密钥配置RSA13.png](https://open.yeepay.com/attachments/access?fileId=170JJQoDo6C)

# [](https://open.yeepay.com/docs-v3/platform/193.md#%E4%B8%83%E3%80%81%E6%9F%A5%E7%9C%8B%E6%98%93%E5%AE%9D%E5%85%AC%E9%92%A5)七、查看易宝公钥

国际密钥（RSA）类型，可以【查看】并【复制】易宝公钥 ![密钥配置RSA14.png](https://open.yeepay.com/attachments/access?fileId=170JN4NDSeO)