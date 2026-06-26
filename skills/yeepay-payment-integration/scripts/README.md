# scripts —— 易宝接入工具（Python）

本目录为联调/本地验证工具，**非生产组件**；生产交易、出款请走商户自有系统并做完整风控与审计。

## 环境要求

- **Python ≥ 3.10**（脚本使用 PEP 604 类型语法；`requests` 2.33+ 亦要求 3.10+）
- 第三方依赖见 `requirements.txt`

**运行任何联调脚本前，先执行环境校验：**

```bash
cd scripts
python tools/check_python_env.py   # 检查 Python 版本与 cryptography/requests/gmssl
pip install -r requirements.txt    # 校验失败时安装依赖
```

各 CLI 入口也会在启动时二次校验 Python 版本；`check_python_env.py` 可在低版本 Python 上运行并给出升级引导。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 目录结构

```text
scripts/
├── validate_docs.py      # Skill 发版守门（文档 + 向量 + 版本）
├── requirements.txt
├── common/               # 跨算法共享库
│   ├── response_verify.py   # API 应答验签（RSA/SM2）
│   ├── url_encoding.py      # 签名一次编码 / HTTP 二次编码
│   ├── yop_headers.py       # YOP 标准头
│   ├── yop_content_type.py  # Content-Type 规范
│   ├── yop_http.py          # HTTP 报文组装
│   ├── yop_gateway.py       # 生产 yos / 沙箱 sandbox 网关
│   ├── yop_multipart.py     # multipart 签名
│   ├── yop_payload.py         # 请求体编解码
│   └── python_version.py      # Python 版本校验（≥3.10）
├── tools/                # 跨算法 CLI（见 tools/README.md）
│   ├── check_python_env.py  # 环境校验（运行任何脚本前必做）
│   ├── verify_vectors.py    # 测试向量校验 / --regen
│   ├── verify_response.py # 离线应答验签
│   └── resolve_java_sdk_version.py  # yop-java-sdk 最新版（Maven Central）
├── rsa/                  # RSA 联调（见 rsa/README.md）
└── sm/                   # 国密 SM2 联调（见 sm/README.md）
```

## 发版守门

```bash
python validate_docs.py                      # 文档质量 + 死链 + 版本一致 + 测试向量
python validate_docs.py --with-notify-test   # 额外含 RSA + SM2 mock/decrypt 互打
```

## 常用环境变量

| 变量 | 含义 |
|------|------|
| `YOP_APPKEY` | 应用 appKey |
| `YOP_PRIVATE_KEY` | 商户私钥（查单/退款/simple mock） |
| `YOP_PLATFORM_PRIVATE_KEY` | 易宝平台私钥（real mock 模拟平台签名） |
| `YOP_MERCHANT_PUBLIC_KEY` | 商户公钥（real mock 加密） |
| `YOP_PLATFORM_PUBLIC_KEY` | 易宝平台公钥（应答/回调验签） |
| `YOP_MERCHANT_NO` | 商户编号 |

## 快速入口

| 算法 | 密钥生成 | 出站签名/查单 | 回调互打 |
|------|----------|---------------|----------|
| RSA | `python rsa/gen_keypair.py` | `rsa/query_order.py`、`rsa/refund.py`（`--verify` 验签应答） | `rsa/mock_notify.py` + `rsa/decrypt_notify.py` |
| SM2 | `python sm/gen_keypair.py` | `sm/client.py`、`sm/list_platform_certs.py`（`call(verify=True)`） | `sm/mock_notify.py` + `sm/decrypt_notify.py` |

跨算法工具：`python tools/verify_vectors.py`、`python tools/verify_response.py --algo rsa|sm2 ...`

> 协议文档位于 `../references/平台文档/平台规范/安全认证/`。

## 测试向量

- RSA：`rsa/tests/vectors/`
- SM2：`sm/tests/vectors/`

固定测试密钥与签名/回调解密的输入输出期望值，供商户自研实现逐字节比对。
协议实现变更时：`python tools/verify_vectors.py --regen` 重算 → 同步协议文档示例 → 提升 Skill 版本。
**测试密钥仅供向量使用，禁止用于任何真实环境。**

## 重要约定

- 接口字段以在线 `doc_md` 为准（见 `../references/产品能力/api-index.yaml`）。
- 私钥不入库、不进日志；`keys/` 建议加入 `.gitignore`。
