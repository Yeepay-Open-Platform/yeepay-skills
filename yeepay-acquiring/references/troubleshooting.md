# 收单排障

## 接口返回错误码时（优先）

当接口调用返回错误码（如 `00012`、`00001` 等业务码），按以下顺序排查：

1. **先查所调用接口文档的“错误码”章节**  
   - 定位接口：在 `references/api-index.md` 找到对应场景接口
   - 跳转原文：在 `references/originals/收单/...` 下找到该接口原文
   - 读取原文末尾的“错误码”表格，按“子错误码”匹配并执行“解决方案”
2. **接口文档未覆盖该码** → 查 `平台错误码说明.md`
3. **仍无法判断** → 走下方“通用排障建议”

参考：`../../yeepay-shared-base/references/error-code-top.md`（错误码两层结构与处理顺序）

## 常用入口

- 平台错误码：`../../yeepay-shared-base/references/originals/开发文档/开始对接/平台错误码说明.md`
- 接入诊断：`../../yeepay-shared-base/references/originals/开发文档/工具与支持/开发工具/接入诊断.md`
- 结果通知工具：`../../yeepay-shared-base/references/originals/开发文档/工具与支持/开发工具/结果通知工具.md`

## 通用排障建议

1. 先确认请求签名与鉴权是否正确。
2. 再确认回调配置与回调验签逻辑。
3. 对支付结果以查单接口为准。
