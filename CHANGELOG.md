# 变更历史

版本规则与发版流程见 `README.md`「版本管理与更新机制」。最新条目置顶，首条版本号须与 `SKILL.md` frontmatter 一致（`validate_docs.py` 校验）。

## 0.6.1 - 2026-06-12

外链与措辞修订：

- 控制台入口统一为 `https://open.yeepay.com/developer-center`（替换旧商户后台登录页与 home?redirect 变体，共 12 处：密钥配置 RSA/SM、CFCA证书制备、密钥工具）。
- Maven Central 链接更新为新版 `central.sonatype.com/artifact/...`（SDK使用说明、平台SDK）。
- 平台错误码说明标注【新版】错误码。

## 0.6.0 - 2026-06-12

评审会落地（后端协议归位 / 前端示例进产品文档 / 测试向量 / 版本机制）：

- 后端协议文档 `请求签名协议.md`、`回调解密协议.md` 由 `references/示例代码/后端代码/` 迁入 `references/平台文档/平台规范/安全认证/`，纳入 manifest 索引与文档质量守门。
- 前端示例代码全部内联到对应产品场景 md（小程序支付 / 微信内H5+公众号支付 / 浏览器H5支付 / APP支付），删除 `references/示例代码/` 目录，全局引用同步更新。
- 新增加验签/回调解密**固定测试向量**（`scripts/tests/vectors/`）：固定测试密钥 + GET/POST Form/POST JSON 三个签名用例 + 固定四段密文回调用例；协议文档补「完整示例」节，可逐字节比对。
- 新增 `scripts/verify_vectors.py`：校验测试向量与脚本实现一致，支持 `--regen` 重算。
- `validate_docs.py` 升级为发版守门：扫描范围扩大到全部 md，新增相对引用死链检查、过期模式黑名单（definition.json/errcode.json/示例代码 旧路径）、版本一致性检查、测试向量与文档一致性检查。
- 修复 13 个产品场景 md 仍指向旧数据源 `apis/docs/apis/<api_id>/definition.json`、`errcode.json` 的问题，统一为 doc_md 协议。
- 版本号统一以 `SKILL.md` 为单一来源（0.6.0），README 标题去版本号，新增本 CHANGELOG 与「版本管理与更新机制」说明。

## 0.5.1 及更早

- 0.5.x：面客交互纪律（四步）、写代码任务路由（SDK/L1/L2/L3）、标准输出模板。
- 0.4.x：业务文档展开为 `产品能力/<域>/<场景>.md`（收单 8 场景）；新增 `产品决策.md`、`scripts/` 工具、`api-index.yaml`；平台文档全量本地化。
- 0.3-draft：初版草稿（domains 单文件结构）。
