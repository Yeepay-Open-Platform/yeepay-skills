# 示例代码

## 后端代码（协议参考，不使用 SDK 时优先）

| 文件 | 用途 |
|------|------|
| `后端代码/请求签名协议.md` | 出站 API Authorization 构造（RSA/SM2） |
| `后端代码/回调解密协议.md` | 入站结果通知四段密文解密验签 |

与 `scripts/yop_client.py`、`scripts/decrypt_notify.py`、`scripts/mock_notify.py --mode real` 互为印证。

## 前端代码

| 文件 | 用途 |
|------|------|
| `前端代码/微信小程序支付.md` | 小程序调起支付 |
| `前端代码/h5唤起微信小程序支付.md` | H5 唤起小程序支付 |
