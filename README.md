# yeepay-skills

[![版本](https://img.shields.io/badge/version-1.0.0-blue)](./skills/yeepay-payment-integration/SKILL.md) [![许可证](https://img.shields.io/badge/license-Apache--2.0-green)](./LICENSE.md) · [变更历史](./CHANGELOG.md)

> 易宝开放平台（YeePay）面向 Coding Agent 的 **Skills 集合仓库**（monorepo）。  
> 对外发布：[Yeepay-Open-Platform/yeepay-skills](https://github.com/Yeepay-Open-Platform/yeepay-skills)

---

## 这是什么

本仓库收纳多个可独立安装的 Agent Skill。每个技能位于 `skills/<技能 ID>/`，内含 `SKILL.md`（Agent 执行入口）、`references/`（文档）与 `scripts/`（可选联调工具）。

安装后，在对话中提及对应技能覆盖的业务关键词时，Agent 会自动加载相应 `SKILL.md` 并按其中纪律协助完成选型、接入与排障。

## 包含的技能

| 技能 ID | 版本 | 说明 | 文档 |
| --- | --- | --- | --- |
| `yeepay-payment-integration` | [1.0.0](./skills/yeepay-payment-integration/SKILL.md) | 易宝支付接入、联调与排障（收单 / 退款 / 分账 / 出款 / 对账） | [README](./skills/yeepay-payment-integration/README.md) · [SKILL.md](./skills/yeepay-payment-integration/SKILL.md) |

## 快速安装

在任意目录执行（推荐）：

```bash
npx skills add Yeepay-Open-Platform/yeepay-skills
```

按提示选择安装范围（个人 / 当前项目）。各技能的详细说明、手动克隆与软连接方式见上表对应 **README**。

## 目录结构

```text
yeepay-skills/                        仓库根目录
├── README.md                         本文件（monorepo 总览）
├── CHANGELOG.md                      变更历史（各技能版本以各自 SKILL.md 为准）
├── LICENSE.md
└── skills/
    └── yeepay-payment-integration/   技能包（Agent 加载此目录，详见其 README）
        ├── README.md
        ├── SKILL.md
        ├── scripts/
        └── references/
```

后续新增技能时，在 `skills/` 下增加同级目录即可，无需改动已有技能包。

---

## 许可证

本仓库采用 [Apache License 2.0](./LICENSE.md)。使用、修改与再分发须遵守许可证条款；易宝及相关商标归权利人所有，本许可证不授予商标使用许可。

## 相关链接

| 链接 | 说明 |
| --- | --- |
| [易宝开放平台](https://open.yeepay.com) | 商户入驻、应用与密钥管理 |
| [GitHub 仓库](https://github.com/Yeepay-Open-Platform/yeepay-skills) | 源码与发版 |
| [CHANGELOG.md](./CHANGELOG.md) | 版本变更记录 |
| [GitHub Issues](https://github.com/Yeepay-Open-Platform/yeepay-skills/issues) | 问题反馈与建议 |
