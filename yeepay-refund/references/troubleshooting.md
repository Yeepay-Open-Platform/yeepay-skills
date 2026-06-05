# 退款排障

## 接口返回错误码时（优先）

当接口调用返回错误码（如 `00012`、`00001` 等业务码），按以下顺序排查：

1. **先查所调用接口文档的“错误码”章节**  
   - 申请退款：`apis/refund-create.md` → `originals/退款/申请退款.md`
   - 查询退款：`apis/refund-query.md` → `originals/退款/查询退款.md`
   - 阅读原文末尾的“错误码”表格，按“子错误码”匹配并执行“解决方案”
2. **接口文档未覆盖该码** → 查 `平台错误码说明.md`
3. **仍无法判断** → 走下方“通用排障建议”

参考：`../../yeepay-shared-base/references/error-code-top.md`（错误码两层结构与处理顺序）

## 常用入口

- 平台错误码：`../../yeepay-shared-base/references/originals/开发文档/开始对接/平台错误码说明.md`
- 接入诊断：`../../yeepay-shared-base/references/originals/开发文档/工具与支持/开发工具/接入诊断.md`

## 通用排障建议

建议先查退款状态，再决定是否重试发起退款。
