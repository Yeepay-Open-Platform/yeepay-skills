---
name: yeepay-payout
description: 易宝出款业务域。覆盖结算与提现，含结算申请、结算记录、提现下单、提现查询、提现卡管理。当用户提到结算、提现接入、提现失败、出款排障时使用。
version: 0.1.0
---

# 出款业务域

## 前置依赖（必须先读）

先读取 `../yeepay-shared-base/SKILL.md` 及其 references。

## 路由规则

- 结算：`references/apis/settlement.md`
- 提现：`references/apis/withdraw.md`
- **接口返回错误码时**：先按 `references/troubleshooting.md` 的错误码排障流程处理，优先查“所调用接口文档的错误码章节”，其次查平台错误码说明。
