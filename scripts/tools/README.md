# tools —— 跨算法工具与发版辅助

在 `scripts/` 目录下执行（与 `rsa/`、`sm/` 并列）。

| 脚本 | 用途 |
|------|------|
| `verify_vectors.py` | RSA + SM2 测试向量校验 / `--regen` 重算 |
| `verify_response.py` | 离线应答验签（`--algo rsa\|sm2`） |

共享库见 `../common/response_verify.py`（被 `rsa/client`、`sm/client` 引用）。

```bash
python tools/verify_vectors.py
python tools/verify_response.py --algo rsa --body-file resp.json --signature '...$SHA256' --yop-pubkey ./keys/yop_public.pem
```
