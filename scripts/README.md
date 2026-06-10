# scripts —— 易宝接入工具（Python）

本目录为联调/本地验证工具，**非生产组件**；生产交易、出款请走商户自有系统并做完整风控与审计。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 工具一览

| 脚本 | 用途 | 说明 |
|------|------|------|
| `yop_client.py` | YOP RSA 鉴权客户端 | 被其他脚本复用，实现签名与请求构造 |
| `gen_keypair.py` | 生成密钥对 | RSA2048 / SM2，私钥仅本地联调 |
| `query_order.py` | 查单 | `GET /rest/v1.0/trade/order/query` |
| `refund.py` | 退款（申请/查询） | `apply` / `query` 两个子命令 |
| `mock_notify.py` | 本地模拟发结果通知 | 验证商户回调接收与验签/幂等 |

## 常用环境变量

| 变量 | 含义 |
|------|------|
| `YOP_APPKEY` | 应用 appKey（如 `app_100xxx`） |
| `YOP_PRIVATE_KEY` | 商户私钥（文件路径或 PEM 文本） |
| `YOP_MERCHANT_NO` | 商户编号 |
| `YOP_PARENT_MERCHANT_NO` | 发起方商户编号（默认同 merchant） |

## 示例

```bash
# 1. 生成密钥对
python gen_keypair.py --alg rsa --out ./keys

# 2. 查单
python query_order.py --appkey app_100xxx --key ./keys/rsa_private_pkcs8.pem \
  --merchant 100xxx --order-id ORDER_xxx

# 3. 退款（会二次确认）
python refund.py apply --appkey app_100xxx --key ./keys/rsa_private_pkcs8.pem \
  --merchant 100xxx --order-id ORDER_xxx --refund-id REFUND_xxx --amount 0.01

# 4. 本地模拟回调（先 --dry-run 看签名，再真正发送）
python mock_notify.py --url http://127.0.0.1:8080/notify --key ./keys/rsa_private_pkcs8.pem \
  --data '{"status":"SUCCESS","orderId":"ORDER_xxx"}' --dry-run
```

## 重要约定

- 接口字段以在线 `doc_md` 文档为准（见 `../references/产品能力/api-index.yaml`）；脚本字段如与文档不符以文档为准。
- 私钥不入库、不进日志、不外传；`keys/` 建议加入 `.gitignore`。
- 签名实现依据 `../references/平台文档/平台规范/安全认证/鉴权认证机制(RSA).md`。
- `mock_notify.py` 的签名为简化实现，仅用于打通商户验签链路；真实回调字段/算法以结果通知文档为准。
