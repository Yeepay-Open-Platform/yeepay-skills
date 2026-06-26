# 易宝支付接入集成技能

[版本](./skills/yeepay-payment-integration/SKILL.md) [许可证](./LICENSE.md)

> 面向 Coding Agent 的易宝支付（YeePay）接入、联调与排障技能。  
> 仓库：[Yeepay-Open-Platform/yeepay-skills](https://github.com/Yeepay-Open-Platform/yeepay-skills) · 变更历史见 [CHANGELOG.md](./CHANGELOG.md)

---

## 这是什么

面向易宝支付**接入、联调与排障**场景的 Agent Skill。安装后，在对话中提及「接入易宝支付」「YOP」「小程序支付」「APP 支付」「退款」「分账」「提现」「对账」「验签失败」「回调收不到」等问题时，Agent 会自动加载 [SKILL.md](./skills/yeepay-payment-integration/SKILL.md)，按其中的面客纪律、产品决策与文档加载协议协助完成选型、接入与排障。

## 能力与覆盖范围

Agent 可协助完成：

1. 根据业务场景判断应使用的易宝支付产品能力
2. 输出对应场景的接入流程、前置条件、接口位置和注意事项
3. 根据 SDK 或非 SDK 方式生成参数说明或示例代码
4. 围绕签名、验签、回调、查单、错误码、证书和网络配置进行排障
5. 使用本地工具完成签名、回调、应答验签和测试向量校验


| 业务域  | 覆盖内容                                                         |
| ---- | ------------------------------------------------------------ |
| 收单   | 小程序支付、APP 支付、浏览器 H5、微信内 H5+公众号、被扫付款码、主扫独立码/聚合码、prePayTn 唤起方式 |
| 退款   | 申请退款、退款查询、退款回调与排障                                            |
| 分账   | 订单分账、余额分账、入账方相关流程                                            |
| 出款   | 结算、提现                                                        |
| 对账   | 交易、分账、资金、结算对账                                                |
| 运维排障 | 签名验签、回调验签、YOP 错误码、沙箱联调、上线检查                                  |


## 快速开始

### 前置条件


| 项                                     | 要求                                     |
| ------------------------------------- | -------------------------------------- |
| AI 工具 | 支持 Agent Skills 的编码 Agent 环境 |
| Node.js                               | 用于执行 `npx skills add`（推荐安装）            |
| Python                                | 仅在使用 `scripts/` 联调工具时需要 **≥ 3.10**（可选） |


### 安装

#### 方式 A：命令行安装（推荐）

在任意目录执行：

```bash
npx skills add Yeepay-Open-Platform/yeepay-skills
```

按提示选择安装范围（个人 / 当前项目）即可。

#### 方式 B：手动克隆 + 软连接

适合需要本地开发、修改 skill 或固定 Git 版本的场景。

**克隆仓库：**

```bash
git clone https://github.com/Yeepay-Open-Platform/yeepay-skills.git
cd yeepay-skills
```

锁定某一发版版本（推荐生产接入前固定版本）：

```bash
git fetch --tags
git checkout v1.0.0   # 替换为目标 tag
```

**个人技能（所有项目可用）：**

```bash
mkdir -p ~/.agents/skills
ln -sfn "$(pwd)/skills/yeepay-payment-integration" ~/.agents/skills/yeepay-payment-integration
```

**项目技能（随仓库共享给团队）：**

在目标项目根目录执行（将 `SKILL_SRC` 换成本机技能包绝对路径）：

```bash
SKILL_SRC=/path/to/yeepay-skills/skills/yeepay-payment-integration
mkdir -p .agents/skills
ln -sfn "$SKILL_SRC" .agents/skills/yeepay-payment-integration
```

> 软连接须指向 `skills/yeepay-payment-integration/`（技能包根目录），不要链到仓库根目录。`git pull` 后即可更新；请勿将整仓复制进业务项目以免版本漂移。

### 验证安装

```bash
test -f ~/.agents/skills/yeepay-payment-integration/SKILL.md && echo "个人技能 OK"
# 或（项目级）
test -f .agents/skills/yeepay-payment-integration/SKILL.md && echo "项目技能 OK"
```

重启 AI 工具或打开新 Agent 会话后，在对话中提及易宝 / YOP 相关关键词，Agent 应自动匹配本技能（技能 ID：`yeepay-payment-integration`）。

### 示例提问

- 「我要接入易宝微信小程序支付，Java SDK，沙箱环境，帮我梳理接入步骤。」
- 「YOP 支付回调验签失败，帮我按排查清单定位。」
- 「易宝 APP 支付下单，不用 SDK，需要自研签名，给出参数说明。」

### 联调脚本（可选）

仅当需要本地签名、回调验签、测试向量校验时：

```bash
cd skills/yeepay-payment-integration/scripts
python tools/check_python_env.py
pip install -r requirements.txt
```

详见 [scripts/README.md](./skills/yeepay-payment-integration/scripts/README.md)。

### 更新与卸载


| 操作             | 命令                                                         |
| -------------- | ---------------------------------------------------------- |
| 更新技能（`npx` 安装） | 重新执行 `npx skills add Yeepay-Open-Platform/yeepay-skills` |
| 更新技能（软连接）      | 在克隆目录 `git pull`，无需重装                                      |
| 卸载个人技能         | `rm ~/.agents/skills/yeepay-payment-integration`           |
| 卸载项目技能         | `rm .agents/skills/yeepay-payment-integration`             |


软连接卸载仅删除链接，不删除源仓库。

---

## 目录结构

```text
yeepay-skills/                        仓库根目录
├── README.md                         本文件（仓库级说明）
├── CHANGELOG.md
├── LICENSE.md
└── skills/
    └── yeepay-payment-integration/   技能包（Agent 加载此目录）
        ├── README.md               技能包说明（安装见仓库根 README）
        ├── SKILL.md                唯一入口：面客纪律、技术执行顺序、路由、输出模板
        ├── scripts/                Python 联调工具（仅本地，详见 scripts/README.md）
        │   ├── README.md
        │   ├── requirements.txt
        │   ├── .python-version     Python 版本锁定（≥3.10）
        │   ├── validate_docs.py    发版守门：死链、版本一致、测试向量等
        │   ├── common/             跨算法共用库
        │   ├── tools/              环境校验、向量校验、Java SDK 版本查询等
        │   ├── rsa/                RSA 联调
        │   └── sm/                 国密 SM2 联调
        └── references/
            ├── troubleshooting.md
            ├── 产品能力/           产品决策、api-index、收单/退款/分账/出款/对账场景
            └── 平台文档/           接入准备、开始对接、平台规范、工具与支持
```

---

## 许可证

本仓库采用 [Apache License 2.0](./LICENSE.md)。使用、修改与再分发须遵守许可证条款；易宝及相关商标归权利人所有，本许可证不授予商标使用许可。

## 相关链接


| 链接                                                                               | 说明              |
| -------------------------------------------------------------------------------- | --------------- |
| [易宝开放平台](https://open.yeepay.com)                                                | 商户入驻、应用与密钥管理    |
| [SKILL.md](./skills/yeepay-payment-integration/SKILL.md)                         | Agent 执行入口与完整纪律 |
| [GitHub 仓库](https://github.com/Yeepay-Open-Platform/yeepay-skills)             | 源码与发版           |
| [CHANGELOG.md](./CHANGELOG.md)                                                   | 版本变更记录          |
| [GitHub Issues](https://github.com/Yeepay-Open-Platform/yeepay-skills/issues) | 问题反馈与建议         |

