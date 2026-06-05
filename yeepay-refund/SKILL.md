---
name: yeepay-refund
description: 易宝退款业务域。覆盖申请退款与查询退款。当用户提到退款接入、申请退款、原路退回、部分退款、退款状态查询、退款失败排障时使用。
version: 0.1.0
---

# 退款业务域

## 前置依赖（必须先读）

先读取 `../yeepay-shared-base/SKILL.md` 及其 references。

## 路由规则

- 申请退款：读取 `references/apis/refund-create.md`
- 查询退款：读取 `references/apis/refund-query.md`
- **接口返回错误码时**：先按 `references/troubleshooting.md` 的错误码排障流程处理，优先查“所调用接口文档的错误码章节”，其次查平台错误码说明。