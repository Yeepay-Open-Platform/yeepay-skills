# 配置商密证书(SM)

## [](https://open.yeepay.com/docs-v3/platform/2509.md#%E4%B8%80%E3%80%81%E9%85%8D%E7%BD%AE%E5%89%8D%E5%87%86%E5%A4%87%E5%B7%A5%E4%BD%9C)一、配置前准备工作

### [](https://open.yeepay.com/docs-v3/platform/2509.md#1.%E5%87%86%E5%A4%87%E5%A5%BD%E7%99%BB%E5%BD%95%E5%B9%B3%E5%8F%B0%E7%9A%84%E8%B4%A6%E5%8F%B7%E4%BF%A1%E6%81%AF)1.准备好登录平台的账号信息

### [](https://open.yeepay.com/docs-v3/platform/2509.md#2.%E5%B7%B2%E5%88%B6%E5%A4%87%E7%9A%84%E5%95%86%E5%AF%86%E8%AF%81%E4%B9%A6)2.已制备的商密证书

## [](https://open.yeepay.com/docs-v3/platform/2509.md#%E4%BA%8C%E3%80%81%E5%95%86%E5%AF%86%E8%AF%81%E4%B9%A6%E9%85%8D%E7%BD%AE)二、商密证书配置

### [](https://open.yeepay.com/docs-v3/platform/2509.md#%E7%AC%AC%E4%B8%80%E6%AD%A5%EF%BC%9A%E7%99%BB%E5%BD%95%E5%B9%B3%E5%8F%B0%E8%BF%9B%E5%85%A5%EF%BC%8C%E5%AF%86%E9%92%A5%E9%85%8D%E7%BD%AE%E9%A1%B5%E9%9D%A2)第一步：登录平台进入，密钥配置页面

1.  进入 【[控制台](https://open.yeepay.com/developer-center)】>【我的应用】>【密钥配置】，密钥类型选择：商密（sm2）
2.  请在【公钥证书】中选择【SM2格式的CFCA证书】

-   若列表中没有可用SM2格式的证书：请先完成 CFCA证书的制备[查看制备方法](https://open.yeepay.com/docs-v3/platform/7642.md)
    
    ![1.png](https://open.yeepay.com/attachments/access?fileId=171YcWjyA5o)
    

3.  点击【保存】，提交信息

### [](https://open.yeepay.com/docs-v3/platform/2509.md#%E7%AC%AC%E4%BA%8C%E6%AD%A5%EF%BC%9A%E9%AA%8C%E8%AF%81%E7%BB%91%E5%AE%9A%E6%89%8B%E6%9C%BA%E5%8F%B7)第二步：验证绑定手机号

![2.png](https://open.yeepay.com/attachments/access?fileId=171Yenzg9AG)

## [](https://open.yeepay.com/docs-v3/platform/2509.md#%E7%AC%AC%E4%B8%89%E6%AD%A5%EF%BC%9A%E5%AF%86%E9%92%A5%E8%AE%BE%E7%BD%AE%E6%88%90%E5%8A%9F)第三步：密钥设置成功

![3.png](https://open.yeepay.com/attachments/access?fileId=171Z0vpGk0u)

## [](https://open.yeepay.com/docs-v3/platform/2509.md#%E4%B8%89%E3%80%81%E4%BF%AE%E6%94%B9%E5%95%86%E6%88%B7%E5%85%AC%E9%92%A5)三、修改商户公钥

在私钥泄漏等情况下，开发者可能需要变更密钥，此时可以在密钥配置页面，点击公钥后的“设置“按钮进行变更。

1.  在 【[控制台](https://open.yeepay.com/developer-center)】>【 我的应用】>【密钥配置】 页面，点击【设置公钥】按钮。

![4.png](https://open.yeepay.com/attachments/access?fileId=171Z36fIzy4)

2.  选择要更新的【公钥证书】。

![5.png](https://open.yeepay.com/attachments/access?fileId=171Z5KiWImO)

3.  验证绑定手机号。

![6.png](https://open.yeepay.com/attachments/access?fileId=171ZBnXXxWi)

4.  修改成功

![7.png](https://open.yeepay.com/attachments/access?fileId=171ZFsV3YH2)

## [](https://open.yeepay.com/docs-v3/platform/2509.md#%E5%9B%9B%E3%80%81%E5%AF%86%E9%92%A5%E5%8F%98%E6%9B%B4%E5%90%8A%E9%94%80)四、密钥变更吊销

变更密钥后，密钥配置页面弹出提示，点击“立即吊销”，进行二次确认，确认后，即可吊销旧密钥。如图所示：

![8.png](https://open.yeepay.com/attachments/access?fileId=171ZHOltJui)

## [](https://open.yeepay.com/docs-v3/platform/2509.md#%E4%BA%94%E3%80%81%E5%AF%86%E9%92%A5%E5%8F%98%E6%9B%B4%E6%92%A4%E9%94%80)五、密钥变更撤销

变更密钥后，密钥配置页面弹出提示，点击“撤销变更”，进行二次确认，确认后，即可撤销新配置的密钥。如图所示：

![9.png](https://open.yeepay.com/attachments/access?fileId=171ZIVtyCo4)

## [](https://open.yeepay.com/docs-v3/platform/2509.md#%E5%85%AD%E3%80%81%E6%91%98%E8%A6%81%E4%BF%A1%E6%81%AF)六、摘要信息

平台支持查看 商户公钥的摘要信息 ![10.png](https://open.yeepay.com/attachments/access?fileId=171ZJFURLwu) ![11.png](https://open.yeepay.com/attachments/access?fileId=171ZK0XITAW)