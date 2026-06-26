# tools —— 跨算法工具与发版辅助

在 `scripts/` 目录下执行（与 `rsa/`、`sm/` 并列）。

| 脚本 | 用途 |
|------|------|
| `check_python_env.py` | **环境校验**（Python ≥3.10 + 依赖；运行任何脚本前必做） |
| `verify_vectors.py` | RSA + SM2 测试向量校验 / `--regen` 重算 |
| `verify_response.py` | 离线应答验签（`--algo rsa\|sm2`） |
| `resolve_java_sdk_version.py` | 查询 `yop-java-sdk` Maven Central 最新稳定版 |

共享库见 `../common/response_verify.py`（被 `rsa/client`、`sm/client` 引用）。

```bash
python tools/check_python_env.py
python tools/verify_vectors.py
python tools/verify_response.py --algo rsa --body-file resp.json --signature '...$SHA256' --yop-pubkey ./keys/yop_public.pem
python tools/resolve_java_sdk_version.py
python tools/resolve_java_sdk_version.py --json
```
