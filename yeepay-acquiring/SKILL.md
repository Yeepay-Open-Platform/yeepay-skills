---
name: yeepay-acquiring
description: 易宝收单业务域。覆盖APP支付、小程序支付、浏览器页面支付、微信内页面加公众号支付、主扫支付、被扫支付及查单。当用户提到接入易宝支付、收单接入、支付下单、支付结果查询、对接支付时使用。
version: 0.1.0
---

# 收单业务域

## 前置依赖（必须先读）

先读取 `../yeepay-shared-base/SKILL.md` 及其 references，再进入本域接口。

## 路由规则

- 接入支付方式：先读 `references/api-index.md` 选择场景接口。
- 写操作前需确认环境与参数来源。
- 支付结果以查单或回调确认为准。
- **接口返回错误码时**：先按 `references/troubleshooting.md` 的错误码排障流程处理，优先查“所调用接口文档的错误码章节”，其次查平台错误码说明。