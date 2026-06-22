# sm —— 国密（SM2/SM3/SM4）联调脚本

与 `rsa/` 对称，运行前请在 `scripts/` 目录安装依赖：

```bash
pip install -r ../requirements.txt
```

## 工具一览

| 脚本 | 用途 | 依据文档 |
|------|------|----------|
| `client.py` | YOP SM2/SM3 鉴权客户端（`call(verify=True)` 可验签应答） | `安全认证/鉴权认证机制(SM).md` |
| `gen_keypair.py` | 生成 SM2 密钥对（PKCS8/SPKI PEM） | `密钥介绍.md` |
| `mock_notify.py` | 模拟 SM2 结果通知 | `安全认证/结果通知(SM2).md` |
| `decrypt_notify.py` | SM2 回调解密验签 | `安全认证/结果通知(SM2).md` |
| `list_platform_certs.py` | 查询平台 SM2 证书列表（V2） | `平台规范/安全认证/平台商密证书.md` |
| `notify_crypto.py` | 回调编解码（内部模块） | `回调解密协议.md`（SM2 章节） |
| `crypto.py` | SM2/SM3/SM4 国密原语（内部模块） | `鉴权认证机制(SM).md` |

## SM2 密钥生成

`gen_keypair.py` 使用 **gmssl**（`CryptSM2.default_ecc_table`，SM2P256V1）生成密钥对，输出与 RSA 一致的 PEM 文件：

| 输出文件 | 格式 | 用途 |
|----------|------|------|
| `sm2_private_pkcs8.pem` | PKCS#8 PEM（`BEGIN PRIVATE KEY`） | 本地联调签名/解密 |
| `sm2_public.pem` | SubjectPublicKeyInfo PEM（`BEGIN PUBLIC KEY`） | 上传平台或互打验签 |

**注意：** 生产商密接入须使用 **CFCA 证书**（控制台上传证书，非 PEM 公钥文件），见 `../../references/平台文档/接入准备/密钥管理/CFCA证书制备.md`。

## 示例

在 `scripts/` 目录下执行：

```bash
# 生成 SM2 密钥对
python sm/gen_keypair.py --out ./keys

# SM2 回调互打验证
python sm/mock_notify.py --mode real --dry-run \
  --url http://127.0.0.1:8080/notify \
  --yop-key ./keys/sm2_yop_private_pkcs8.pem \
  --merchant-pubkey ./keys/sm2_merchant_public.pem \
  --data '{"status":"SUCCESS","orderId":"ORDER_xxx"}'
python sm/decrypt_notify.py \
  --headers-file /tmp/sm_headers.json \
  --body '...' \
  --merchant-key ./keys/sm2_merchant_private_pkcs8.pem \
  --yop-pubkey ./keys/sm2_yop_public.pem

# 查询平台商密证书（须已配置 CFCA 商密私钥）
python sm/list_platform_certs.py \
  --appkey 你的appKey \
  --key ./keys/sm2_private_pkcs8.pem \
  --save-dir ./certs/yop
```

## 测试向量（tests/vectors/）

SM2 签名/回调向量与 RSA 向量分开存放。校验入口仍在根目录：

```bash
python tools/verify_vectors.py
```

协议实现变更时：`python tools/verify_vectors.py --regen` → 同步协议文档示例 → 提升 Skill 版本。
