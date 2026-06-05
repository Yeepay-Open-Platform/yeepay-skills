---
name: yeepay-profit-sharing
description: 易宝分账业务域。覆盖订单分账、余额分账、分账查询、完结分账与分账资金归还。当用户提到分账接入、申请分账、完结分账、分账查询、分账资金归还时使用。
version: 0.1.0
---

# 分账业务域

## 前置依赖（必须先读）

先读取 `../yeepay-shared-base/SKILL.md` 及其 references。

## 路由规则

- 订单分账：`references/apis/order-profit-sharing.md`
- 余额分账：`references/apis/balance-profit-sharing.md`
- **接口返回错误码时**：先按 `references/troubleshooting.md` 的错误码排障流程处理，优先查“所调用接口文档的错误码章节”，其次查平台错误码说明。