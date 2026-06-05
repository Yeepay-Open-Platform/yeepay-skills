# 回调验签

## 规范来源

- `../../yeepay-shared-base/references/originals/开发文档/平台规范/安全认证/结果通知(RSA).md`
- `../../yeepay-shared-base/references/originals/开发文档/平台规范/安全认证/结果通知(SM2).md`
- `../../yeepay-shared-base/references/originals/开发文档/平台规范/结果通知机制说明.md`

## 诊断说明

当前发布版本不提供本地验签脚本，建议按上述规范来源文档逐项核对：

1. 回调头字段是否完整。
2. 回调报文是否与验签输入一致。
3. 公钥/证书与环境是否匹配。