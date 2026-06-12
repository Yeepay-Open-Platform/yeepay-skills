# scripts —— 易宝接入工具（Python）

本目录为联调/本地验证工具，**非生产组件**；生产交易、出款请走商户自有系统并做完整风控与审计。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 工具一览

| 脚本 | 用途 | 依据文档 |
|------|------|----------|
| `yop_client.py` | YOP RSA 鉴权客户端（被其他脚本复用） | `安全认证/鉴权认证机制(RSA).md`、`安全认证/请求签名协议.md` |
| `gen_keypair.py` | 生成 RSA/SM2 密钥对 | `密钥工具.md` |
| `query_order.py` | 查单 | doc_md + api-index.yaml |
| `refund.py` | 退款申请/查询 | doc_md + api-index.yaml |
| `mock_notify.py` | 模拟发结果通知 | `安全认证/结果通知(RSA).md`、`安全认证/回调解密协议.md` |
| `decrypt_notify.py` | 回调密文解密验签 | `安全认证/回调解密协议.md` |
| `notify_crypto.py` | 四段密文编解码（内部模块） | `安全认证/回调解密协议.md` |
| `verify_vectors.py` | 签名/回调解密测试向量校验（`--regen` 重算） | `tests/vectors/` + 两份协议文档「完整示例」 |
| `validate_docs.py` | 发版守门（文档质量/死链/过期模式/版本一致/测试向量） | 全 `references/` + SKILL/README/CHANGELOG |

> 协议文档位于 `../references/平台文档/平台规范/安全认证/`。

## mock_notify 两种模式

| 模式 | 说明 |
|------|------|
| `simple`（默认） | 简化 `x-yop-sign`，**仅打通 HTTP 链路**，不可验证商户四段解密代码 |
| `real` | 构造 `encKey$encData$AES$SHA256` 真实密文，与 `decrypt_notify.py` 互打验证 |

## 常用环境变量

| 变量 | 含义 |
|------|------|
| `YOP_APPKEY` | 应用 appKey |
| `YOP_PRIVATE_KEY` | 商户私钥（查单/退款/simple mock） |
| `YOP_YOP_PRIVATE_KEY` | 模拟平台签名私钥（real mock） |
| `YOP_MERCHANT_PUBLIC_KEY` | 商户公钥（real mock 加密） |
| `YOP_YOP_PUBLIC_KEY` | 易宝公钥（decrypt_notify 验签） |
| `YOP_MERCHANT_NO` | 商户编号 |

## 示例

```bash
# 1. 生成密钥对
python gen_keypair.py --alg rsa --out ./keys

# 2. 查单
python query_order.py --appkey app_100xxx --key ./keys/rsa_private_pkcs8.pem \
  --merchant 100xxx --order-id ORDER_xxx

# 3. 真实密文互打验证
python mock_notify.py --mode real --dry-run \
  --url http://127.0.0.1:8080/notify \
  --yop-key ./keys/rsa_private_pkcs8.pem \
  --merchant-pubkey ./keys/rsa_public.pem \
  --data '{"status":"SUCCESS","orderId":"ORDER_xxx"}' > /tmp/cipher.txt
python decrypt_notify.py --cipher "$(tail -1 /tmp/cipher.txt)" \
  --merchant-key ./keys/rsa_private_pkcs8.pem \
  --yop-pubkey ./keys/rsa_public.pem
```

## 发版守门

```bash
python validate_docs.py                      # 文档质量 + 死链 + 过期模式 + 版本一致 + 测试向量
python validate_docs.py --with-notify-test   # 额外含 mock/decrypt 互打
```

## 测试向量（tests/vectors/）

固定测试密钥与签名/回调解密的输入输出期望值，供商户自研实现逐字节比对（详见两份协议文档「完整示例」）。
协议实现变更时：`python verify_vectors.py --regen` 重算 → 同步协议文档示例 → 提升 Skill 版本。
**测试密钥仅供向量使用，禁止用于任何真实环境。**

## 重要约定

- 接口字段以在线 `doc_md` 为准（见 `../references/产品能力/api-index.yaml`）。
- 私钥不入库、不进日志；`keys/` 建议加入 `.gitignore`。
