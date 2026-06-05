# 易宝支付接入技能

本项目用于在智能编程工具中，辅助开发者完成易宝支付接入与联调排障。

## 定位与边界

- 本技能是接入知识与流程规则集合，不是支付网关或生产交易通道。
- 生产交易调用以易宝标准开放接口为准。
- 代码编写能力来自智能编程工具平台，本技能负责提供规范、路径和约束。

## 当前版本覆盖范围

- 收单：APP支付、小程序支付、浏览器页面支付、微信内 H5+公众号支付、主扫支付、被扫支付
- 退款：退款申请、退款查询
- 分账：订单分账、余额分账
- 出款：结算、提现
- 对账：交易、分账、资金、结算对账

## 版本与更新说明

- 当前版本号见根目录文件 `VERSION`（当前为 `0.2.0`）。
- 建议采用语义化版本：
  - `MAJOR`：目录结构或使用方式发生不兼容变化
  - `MINOR`：新增业务能力、接口文档或规则
  - `PATCH`：文案修正、链接修复、排障提示优化等兼容性修改

## 使用方式

1. 先读 `yeepay-shared-base/SKILL.md` 及其 `references`。
   - 无 SDK 对接场景可优先阅读 `yeepay-shared-base/references/no-sdk-integration-rsa.md`。
2. 按业务域进入对应目录，从 `references/api-index.md` 开始。
3. 需要排障时使用 `yeepay-ops/references` 文档。
4. 上线前执行 `yeepay-ops/references/go-live-checklist.md`。

## 目录概览

```text
yeepay-shared-base/            # 共享规则：签名、回调、幂等、错误码
yeepay-acquiring/              # 收单
yeepay-refund/                 # 退款
yeepay-profit-sharing/         # 分账
yeepay-payout/                 # 出款
yeepay-reconciliation/         # 对账
yeepay-ops/                    # 运维保障
```

## 关键规则

- 涉及状态变更的操作（如支付、退款、分账、提现）应先确认环境与关键参数。
- 支付结果以后端查单或回调确认为准，不以前端页面展示为准。
- 禁止输出密钥、私钥及完整敏感标识。

## 当前限制

- 当前版本不覆盖全部开放接口。
- 生成代码仍需开发者结合项目结构完成适配与验证。

## 许可证

专有许可证（保留所有权利）。详见 `LICENSE.md`。

