---
name: yeepay-ops
description: 易宝运维保障域。用于回调验签、回调排障、上线检查。当用户提到验签失败、回调收不到、签名失败、上线前检查、上线检查清单时使用。
version: 0.1.0
---

# 运维保障域

## 前置依赖（必须先读）

先读取 `../yeepay-shared-base/SKILL.md` 及其 references。

## 默认路由

当用户提到“准备上线、可上线吗、上线检查”时，优先读取 `references/go-live-checklist.md`。