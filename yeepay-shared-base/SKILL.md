---
name: yeepay-shared-base
description: 易宝支付共享基础规则。用于易宝支付接入准备、签名验签、密钥配置、回调验签、幂等重试与通用错误码排查。当用户提到接入易宝支付、签名错误、验签失败、密钥/证书配置、平台错误码时使用，所有业务域执行前必须先读取本技能。
version: 0.1.0
---

# 易宝支付共享基础规则

本技能是所有业务域的前置依赖，不直接承载某一个业务接口。

## 使用规则

1. 进入任一业务域前，先读取本技能和对应 references 文档。
2. 写操作前需二次确认（如支付、退款、分账、提现）。
3. 交易结果以后端查单或回调确认为准，不以前端页面结果为准。
4. 禁止输出密钥、私钥、完整敏感标识。

## 文档索引

- `references/integration-prerequisites.md`
- `references/no-sdk-integration-rsa.md`
- `references/signing-and-verify.md`
- `references/callback-contract.md`
- `references/idempotency-and-retry.md`
- `references/error-code-top.md`