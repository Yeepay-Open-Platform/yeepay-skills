# 变更历史

最新条目置顶，首条版本号须与 `SKILL.md` frontmatter 一致（`validate_docs.py` 校验）。

## 1.1.0 - 2026-07-16

**yeepay-payment-integration** 新增入网业务域。

- 新增 `references/产品能力/入网/入网.md`：易宝客户模型、商户入网审核流程、接口调用流程、商户管理（信息变更/产品变更/沉默商户解冻）及入网易错点。
- 新增 `references/产品能力/入网/实名认证.md`：微信/支付宝实名认证（支付前置准备）接口清单、线下/API 两种微信认证方式与排障。
- `api-index.yaml` 新增 `merchant-netin` 分组（文件上传、服务商/平台商入网、进度与状态查询、信息变更、实名认证等 21 个接口，doc_md 已逐个实测）。
- `SKILL.md` 业务域路由与触发关键词覆盖入网/进件/实名认证；`产品决策.md` 新增入网关键词匹配与覆盖范围说明。

## 1.0.0 - 2026-06-26

**yeepay-payment-integration** 首次公开发布。

面向 Coding Agent 的易宝支付（YeePay）接入技能，协助商户完成产品选型、接入指导、代码生成与联调排障。