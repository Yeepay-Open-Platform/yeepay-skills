# rsa —— RSA 联调脚本

与 `sm/` 国密脚本对称，运行前请在 `scripts/` 目录安装依赖：

```bash
pip install -r ../requirements.txt
```

## 工具一览

| 脚本 | 用途 | 依据文档 |
|------|------|----------|
| `client.py` | YOP RSA 鉴权客户端（`call` / `upload` / `download`；`verify=True` 可验签应答） | `安全认证/鉴权认证机制(RSA).md`、`安全认证/请求签名协议.md` |
| `gen_keypair.py` | 生成 RSA2048 密钥对 | `密钥介绍.md` |
| `query_order.py` | 查单 | doc_md + api-index.yaml |
| `refund.py` | 退款申请/查询 | doc_md + api-index.yaml |
| `mock_notify.py` | 模拟 RSA 结果通知 | `安全认证/结果通知(RSA).md`、`安全认证/回调解密协议.md` |
| `decrypt_notify.py` | RSA 回调密文解密验签 | `安全认证/回调解密协议.md` |
| `notify_crypto.py` | 四段密文编解码（内部模块） | `回调解密协议.md` |

## mock_notify 两种模式

| 模式 | 说明 |
|------|------|
| `simple`（默认） | 简化 `x-yop-sign`，**仅打通 HTTP 链路**，不可验证四段解密 |
| `real` | 构造 `encKey$encData$AES$SHA256` 真实密文，可与 `decrypt_notify.py` 互打验证 |

## 示例

在 `scripts/` 目录下执行：

```bash
# 生成 RSA 密钥对
python rsa/gen_keypair.py --out ./keys

# 查单
python rsa/query_order.py --appkey app_100xxx --key ./keys/rsa_private_pkcs8.pem \
  --merchant 100xxx --order-id ORDER_xxx \
  --verify --yop-pubkey ./keys/yop_public.pem

# multipart 上传（files 可为路径或 {字段名: 路径}）
python -c "
from rsa import client
resp = client.upload('app_xxx', open('keys/rsa_private_pkcs8.pem').read(),
    '/yos/v1.0/xxx/upload', params={'merchantNo': '100xxx'},
    files={'_file': './invoice.pdf'})
print(resp.status_code, resp.text[:500])
"

# 文件下载（生产默认 yos；沙箱统一 sandbox 域名）
python -c "
from rsa import client
client.download('app_xxx', open('keys/rsa_private_pkcs8.pem').read(),
    '/yos/v1.0/xxx/download', params={'fileId': 'xxx'},
    sandbox=True, save_path='./out.pdf')
"

# 真实密文互打验证
python rsa/mock_notify.py --mode real --dry-run \
  --url http://127.0.0.1:8080/notify \
  --yop-key ./keys/rsa_private_pkcs8.pem \
  --merchant-pubkey ./keys/rsa_public.pem \
  --data '{"status":"SUCCESS","orderId":"ORDER_xxx"}'
python rsa/decrypt_notify.py --cipher '...' \
  --merchant-key ./keys/rsa_private_pkcs8.pem \
  --yop-pubkey ./keys/rsa_public.pem
```

## 测试向量（tests/vectors/）

RSA 签名/回调向量与国密向量分开存放。校验入口在根目录：

```bash
python tools/verify_vectors.py
```

协议实现变更时：`python tools/verify_vectors.py --regen` → 同步协议文档示例 → 提升 Skill 版本。
