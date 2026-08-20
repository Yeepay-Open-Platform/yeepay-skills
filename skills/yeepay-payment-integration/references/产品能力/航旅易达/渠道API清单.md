# 航旅易达 渠道与 API 清单

本清单收录航旅易达当前支持的全部渠道、渠道编码、**产品介绍（适用场景）**、渠道配置说明、接口调用指引与逐接口 openapi.json 链接。渠道选型与易错点见 `航旅易达.md`。

> 使用方式：
>
> 1. 先在 `航旅易达.md`「渠道决策」锁定渠道，再到本清单定位该渠道小节。
> 2. **先 curl「产品介绍」**（含适用场景：航程类型、国内/国际、旅客类型、是否支持退改/政策池等），确认场景匹配后再继续；产品介绍不匹配时不得直接按本渠道接口实现。
> 3. 若该渠道节有**渠道配置说明**：先 curl 读取配置说明，并指导商户完成配置/确认配置已完成（配置通常需商户后台、运营、客户经理或航司侧动作，Agent 不能代完成）。
> 4. 再 curl **接口调用指引**（含接口调用顺序矩阵），接口调用顺序须严格遵循。
> 5. **接口规格**以对应 openapi.json（可直接 curl，含字段/错误码/示例代码）为准；输出字段级内容前必须拉取目标接口的 openapi.json，不得从其他渠道推导接口契约。
> 6. **参数解读**：各参数的支持方式以该 API 内该参数的**描述（description）**为准；`是否必填` = **条件必填** 时，须额外读取该参数的 `x-yop-api-param-condition` 字段获取必填条件，不得按「可选」处理或自行编造条件。
> 7. curl 失败（403/404/超时）时不得臆造内容，提示检查网络后停止字段级实现。

## 航司 NDC

### 南航 NDC2C（`AIR_CZ_NDC2C`）

- 产品介绍（适用场景，必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-nhndc/12839.md](https://open.yeepay.com/docs-v3/solution/hlyd-nhndc/12839.md)
- 接口调用指引：[https://open.yeepay.com/docs-v3/solution/hlyd-nhndc/14411.md](https://open.yeepay.com/docs-v3/solution/hlyd-nhndc/14411.md)

> **API 分组说明**：本节 API 分【南航NDC】与【南航NDC国内来回程】两组，**来回程 = 往返**。接口调用指引中凡属**往返直飞**场景的接口调用，一律使用【南航NDC国内来回程】分组下的 API；单程等其他场景用【南航NDC】分组。两组存在同名接口（如出票创建订单、验仓验价），openapi.json 链接不同，**不可混用**。

【南航NDC】

- 改签航班批量查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/7d8db0888ae70f287e5329d840975bcb/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/7d8db0888ae70f287e5329d840975bcb/openapi.json)
- 改签申请接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/2c6013eae59ce171ddbcdb7a0a0becef/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/2c6013eae59ce171ddbcdb7a0a0becef/openapi.json)
- 批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/c7c3dd47a945b8fe55d8c3f6d8b0484d/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/c7c3dd47a945b8fe55d8c3f6d8b0484d/openapi.json)
- 验仓验价：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/b8c4464e7ee7dc326d7807a8549e449f/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/b8c4464e7ee7dc326d7807a8549e449f/openapi.json)
- 改签支付接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/8c840250b11f70ae9830d7f73fad61ab/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/8c840250b11f70ae9830d7f73fad61ab/openapi.json)
- 出票创建订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/237949cceaabe986ac5c1cd65cef13ff/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/237949cceaabe986ac5c1cd65cef13ff/openapi.json)
- 出票订单支付：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/1d2ff8c099cb5e3435323c49c8c5ba87/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/1d2ff8c099cb5e3435323c49c8c5ba87/openapi.json)
- 查询出票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/186f8f4eba86cca7bdf06db31f155a15/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/186f8f4eba86cca7bdf06db31f155a15/openapi.json)
- 查询退票费详情：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/5ef893a3104ab0cc85519a2ad3fec050/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/5ef893a3104ab0cc85519a2ad3fec050/openapi.json)
- 退票申请：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/b5d4adb2328af2ef23f9db2582ab3578/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/b5d4adb2328af2ef23f9db2582ab3578/openapi.json)
- 查询退票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/4e0db76ef57112b337ab492a727a6069/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/4e0db76ef57112b337ab492a727a6069/openapi.json)
- 改签订单查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/0f40c9bdd25fd8950dc1c7e66862e6d9/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/0f40c9bdd25fd8950dc1c7e66862e6d9/openapi.json)

【南航NDC国内来回程】

- 改签订单查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/e1f9b39289e1893622852cf8de6e14db/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/e1f9b39289e1893622852cf8de6e14db/openapi.json)
- 来回程去程批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/d169e16da608a6a8d61bc64a2d333e8a/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/d169e16da608a6a8d61bc64a2d333e8a/openapi.json)
- 改签支付接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/a0340694826ab06bae7fe3167683c669/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/a0340694826ab06bae7fe3167683c669/openapi.json)
- 来回程返程批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/efb534de6f86b9996e556b05ddf72357/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/efb534de6f86b9996e556b05ddf72357/openapi.json)
- 验仓验价：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/4915f20d2c36611cb101e95e5c34b4e7/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/4915f20d2c36611cb101e95e5c34b4e7/openapi.json)
- 改签航班批量查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/f78a3fbff320d57c670af3fcdafebc7e/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/f78a3fbff320d57c670af3fcdafebc7e/openapi.json)
- 验舱验价（外部）：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/5f745f6c801324b8334d1ec452b5740f/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/5f745f6c801324b8334d1ec452b5740f/openapi.json)
- 出票创建订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/6e2c22ab08479b1da4206a0c5d7da31e/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/6e2c22ab08479b1da4206a0c5d7da31e/openapi.json)
- 批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/6b41fd33b36a1ce27fc0a3b8f9d8df4c/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/6b41fd33b36a1ce27fc0a3b8f9d8df4c/openapi.json)
- 出票订单支付：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/238f646b998ed51f3d0c612d5a373414/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/238f646b998ed51f3d0c612d5a373414/openapi.json)
- 查询退票费详情：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/93819e80e5e3693840fa1f2c327b51b5/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/93819e80e5e3693840fa1f2c327b51b5/openapi.json)
- 查询出票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/e9bbcc76e4c32d0a1276efc5e6c1d6c8/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/e9bbcc76e4c32d0a1276efc5e6c1d6c8/openapi.json)
- 退票申请：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/97cbc42bf29a147e4a2c287664032734/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/97cbc42bf29a147e4a2c287664032734/openapi.json)
- 查询退票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/1f30c0ce8636ff2c424549971dcab5d8/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/1f30c0ce8636ff2c424549971dcab5d8/openapi.json)
- 改签申请接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/73a2ef803debeee21de0e42f9c91aa6c/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc/73a2ef803debeee21de0e42f9c91aa6c/openapi.json)



### 厦航 NDC2C（`AIR_MF_NDC`）

- 产品介绍（适用场景，必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-xhndc/12865.md](https://open.yeepay.com/docs-v3/solution/hlyd-xhndc/12865.md)
- 接口调用指引：[https://open.yeepay.com/docs-v3/solution/hlyd-xhndc/14413.md](https://open.yeepay.com/docs-v3/solution/hlyd-xhndc/14413.md)

- 改签航班批量查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc/8c23abf230b77ce18d89e5c51ee4f509/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc/8c23abf230b77ce18d89e5c51ee4f509/openapi.json)
- 改签申请接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc/f1b9528d5fb5c272d2f05a5b82611b3c/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc/f1b9528d5fb5c272d2f05a5b82611b3c/openapi.json)
- 批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc/83b7e1c6a22424f5b4c47bb30798b770/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc/83b7e1c6a22424f5b4c47bb30798b770/openapi.json)
- 验仓验价：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc/77684c8fdb7c184134e96d5535715990/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc/77684c8fdb7c184134e96d5535715990/openapi.json)
- 改签支付接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc/064d5929fb1f298f64353d6f3e25ffac/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc/064d5929fb1f298f64353d6f3e25ffac/openapi.json)
- 出票创建订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc/5e056558ced8fa424facc20b1ba2369c/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc/5e056558ced8fa424facc20b1ba2369c/openapi.json)
- 出票订单支付：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc/06d77b5b9334a3747200e0e617cb73d5/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc/06d77b5b9334a3747200e0e617cb73d5/openapi.json)
- 查询出票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc/cb4b635a95a5e567747155f54a000542/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc/cb4b635a95a5e567747155f54a000542/openapi.json)
- 查询退票费详情-new：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc/1ada62a8c0df8c2909a8669d78a338cb/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc/1ada62a8c0df8c2909a8669d78a338cb/openapi.json)
- 取消出票未支付订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc/a370afda41a7ae62dcb8d1b721b92bed/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc/a370afda41a7ae62dcb8d1b721b92bed/openapi.json)
- 退票申请：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc/003a8eb4813be2f8c5ad692ff1866162/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc/003a8eb4813be2f8c5ad692ff1866162/openapi.json)
- 查询退票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc/ce74b141bbb6d057b757fffd582cad93/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc/ce74b141bbb6d057b757fffd582cad93/openapi.json)
- 改签订单查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc/71964ed9f684f669180eed60be305c42/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc/71964ed9f684f669180eed60be305c42/openapi.json)
- 取消改签未支付订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc/d92d7ec47187a662aacda2d4b4c7628e/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc/d92d7ec47187a662aacda2d4b4c7628e/openapi.json)



### 山航 NDC2C（`AIR_SC_NDC`）

- 产品介绍（适用场景，必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-shndc/12891.md](https://open.yeepay.com/docs-v3/solution/hlyd-shndc/12891.md)
- 接口调用指引：[https://open.yeepay.com/docs-v3/solution/hlyd-shndc/14414.md](https://open.yeepay.com/docs-v3/solution/hlyd-shndc/14414.md)

- 改签航班批量查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-shndc/bd8d8aaed497d204a9c3a92e55e4aeab/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shndc/bd8d8aaed497d204a9c3a92e55e4aeab/openapi.json)
- 改签申请接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-shndc/f61b215f9d7ee27ff88b8de694fee22e/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shndc/f61b215f9d7ee27ff88b8de694fee22e/openapi.json)
- 批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-shndc/0eeee4beb285c6046d12de9cb4033d5d/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shndc/0eeee4beb285c6046d12de9cb4033d5d/openapi.json)
- 验仓验价：[https://open.yeepay.com/apis/docs/solutions/hlyd-shndc/09ea221d3db11df1f369094ffb4bda7c/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shndc/09ea221d3db11df1f369094ffb4bda7c/openapi.json)
- 改签支付接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-shndc/570ad3934c8f0b03f70f9481e7bd8b13/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shndc/570ad3934c8f0b03f70f9481e7bd8b13/openapi.json)
- 出票创建订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-shndc/469410db93f46bc8d2eb3a0b9717d326/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shndc/469410db93f46bc8d2eb3a0b9717d326/openapi.json)
- 出票订单支付：[https://open.yeepay.com/apis/docs/solutions/hlyd-shndc/786e3e9f1f618f5e6dcdef631286543a/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shndc/786e3e9f1f618f5e6dcdef631286543a/openapi.json)
- 查询出票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-shndc/ef0e27f5a8bf73583a680da7f20ef5e9/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shndc/ef0e27f5a8bf73583a680da7f20ef5e9/openapi.json)
- 查询退票费详情-new：[https://open.yeepay.com/apis/docs/solutions/hlyd-shndc/0d3350e2519bca2aa09823ebbfd3d5ed/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shndc/0d3350e2519bca2aa09823ebbfd3d5ed/openapi.json)
- 退票申请：[https://open.yeepay.com/apis/docs/solutions/hlyd-shndc/6445ba9df3c5462884f5c510426474ff/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shndc/6445ba9df3c5462884f5c510426474ff/openapi.json)
- 查询退票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-shndc/867c51ec0949a1a888b8ddd7ccd77ca8/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shndc/867c51ec0949a1a888b8ddd7ccd77ca8/openapi.json)
- 改签订单查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-shndc/b53b8bcccc2850c4f7bc651343e63dc0/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shndc/b53b8bcccc2850c4f7bc651343e63dc0/openapi.json)



### 深航 NDC2C（`AIR_ZH_NDC2C`）

- 产品介绍（适用场景，必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-shndc2c/14362.md](https://open.yeepay.com/docs-v3/solution/hlyd-shndc2c/14362.md)
- 接口调用指引：[https://open.yeepay.com/docs-v3/solution/hlyd-shndc2c/14415.md](https://open.yeepay.com/docs-v3/solution/hlyd-shndc2c/14415.md)

- 改签航班批量查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-shndc2c/36fb4d8a9e7e1c0953cd80bbac2e50f0/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shndc2c/36fb4d8a9e7e1c0953cd80bbac2e50f0/openapi.json)
- 批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-shndc2c/a95c40505b26d14572fa13eb4f2e7fe0/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shndc2c/a95c40505b26d14572fa13eb4f2e7fe0/openapi.json)
- 改签申请接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-shndc2c/735dd629ab696e3a1bfcc0fe0d687bb1/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shndc2c/735dd629ab696e3a1bfcc0fe0d687bb1/openapi.json)
- 出票创建订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-shndc2c/3b661d671740495716434a3ba797c6f2/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shndc2c/3b661d671740495716434a3ba797c6f2/openapi.json)
- 改签支付接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-shndc2c/5b3a93d103a66345e5d404c61c5b5081/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shndc2c/5b3a93d103a66345e5d404c61c5b5081/openapi.json)
- 改签订单查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-shndc2c/306b0c0a95972617146049ce1a9a1613/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shndc2c/306b0c0a95972617146049ce1a9a1613/openapi.json)
- 出票订单支付：[https://open.yeepay.com/apis/docs/solutions/hlyd-shndc2c/7fa2c598be3498baead8d1d2c4485ab9/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shndc2c/7fa2c598be3498baead8d1d2c4485ab9/openapi.json)
- 退票申请：[https://open.yeepay.com/apis/docs/solutions/hlyd-shndc2c/97103cdf7b277304a7ceebd83c64fba1/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shndc2c/97103cdf7b277304a7ceebd83c64fba1/openapi.json)
- 查询出票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-shndc2c/8497c3b1d034ce7aaf059804b5c88db6/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shndc2c/8497c3b1d034ce7aaf059804b5c88db6/openapi.json)
- 查询退票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-shndc2c/761a0c714184cab2456d17bdfbb8d550/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shndc2c/761a0c714184cab2456d17bdfbb8d550/openapi.json)
- 取消改签未支付订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-shndc2c/6f7bc4baeb295716fa1dbbf64887fcff/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shndc2c/6f7bc4baeb295716fa1dbbf64887fcff/openapi.json)
- 取消出票未支付订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-shndc2c/00c54f9462673d4c09d2a88121860841/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shndc2c/00c54f9462673d4c09d2a88121860841/openapi.json)



### 昆航 NDC2C（`AIR_KY_NDC2C`）

- 产品介绍（适用场景，必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-khndc2c/14530.md](https://open.yeepay.com/docs-v3/solution/hlyd-khndc2c/14530.md)
- 接口调用指引：[https://open.yeepay.com/docs-v3/solution/hlyd-khndc2c/14537.md](https://open.yeepay.com/docs-v3/solution/hlyd-khndc2c/14537.md)

- 改签航班批量查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-khndc2c/e480d2975b5030af54b08e3551fe1693/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-khndc2c/e480d2975b5030af54b08e3551fe1693/openapi.json)
- 批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-khndc2c/2c5baeed3fd870447056fc00bf792427/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-khndc2c/2c5baeed3fd870447056fc00bf792427/openapi.json)
- 改签申请接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-khndc2c/25e95f3f099c48ac55080b306cfd0590/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-khndc2c/25e95f3f099c48ac55080b306cfd0590/openapi.json)
- 改签支付接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-khndc2c/0ef1989779e89d8c5a6c5f0df6929b39/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-khndc2c/0ef1989779e89d8c5a6c5f0df6929b39/openapi.json)
- 改签订单查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-khndc2c/5694b3b8e68d534f207261f9217afb73/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-khndc2c/5694b3b8e68d534f207261f9217afb73/openapi.json)
- 出票创建订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-khndc2c/395af6444dfab37005c07b8264090296/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-khndc2c/395af6444dfab37005c07b8264090296/openapi.json)
- 取消改签未支付订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-khndc2c/649a34787d84055f5480b9ff3e67af65/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-khndc2c/649a34787d84055f5480b9ff3e67af65/openapi.json)
- 出票订单支付：[https://open.yeepay.com/apis/docs/solutions/hlyd-khndc2c/d05aebfecc37280437b02591573d6e03/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-khndc2c/d05aebfecc37280437b02591573d6e03/openapi.json)
- 查询出票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-khndc2c/289811f8a30ebd69fe7215c3f8598abf/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-khndc2c/289811f8a30ebd69fe7215c3f8598abf/openapi.json)
- 取消出票未支付订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-khndc2c/f7f3bfce09a3008d185e1775549ec2d2/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-khndc2c/f7f3bfce09a3008d185e1775549ec2d2/openapi.json)
- 查询退票费详情：[https://open.yeepay.com/apis/docs/solutions/hlyd-khndc2c/fcf70ea0bbeb4edca72cc304e75f4c98/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-khndc2c/fcf70ea0bbeb4edca72cc304e75f4c98/openapi.json)
- 退票申请：[https://open.yeepay.com/apis/docs/solutions/hlyd-khndc2c/72893fc04ba9245ee8d8175dbb7d9b5a/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-khndc2c/72893fc04ba9245ee8d8175dbb7d9b5a/openapi.json)
- 查询退票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-khndc2c/92e7f4b2ddd224859b3f38aa9378f949/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-khndc2c/92e7f4b2ddd224859b3f38aa9378f949/openapi.json)



### 国航 NDC2C（`AIR_CA_NDC2C`）

- 产品介绍（适用场景，必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-ghndc2c/14791.md](https://open.yeepay.com/docs-v3/solution/hlyd-ghndc2c/14791.md)
- 接口调用指引：[https://open.yeepay.com/docs-v3/solution/hlyd-ghndc2c/14798.md](https://open.yeepay.com/docs-v3/solution/hlyd-ghndc2c/14798.md)

- 批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/ce2f2c502e5d4a00b8909503dad1d127/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/ce2f2c502e5d4a00b8909503dad1d127/openapi.json)
- 来回程去程批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/7ce96e616cfd1a5caa4127a0ce4bd7fd/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/7ce96e616cfd1a5caa4127a0ce4bd7fd/openapi.json)
- 来回程返程批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/4042d0c6a49921c64c6406c8921c9139/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/4042d0c6a49921c64c6406c8921c9139/openapi.json)
- 验仓验价：[https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/29ddf7414ac131a83205fe7195aff159/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/29ddf7414ac131a83205fe7195aff159/openapi.json)
- 出票创建订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/6c2de35b691097827da9fdaadc060d69/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/6c2de35b691097827da9fdaadc060d69/openapi.json)
- 出票订单支付：[https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/67738a8ef0ab585533cf0dba3b58eee9/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/67738a8ef0ab585533cf0dba3b58eee9/openapi.json)
- 查询出票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/209dc878267a1292ff2a1b0bdfbbc52e/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/209dc878267a1292ff2a1b0bdfbbc52e/openapi.json)
- 取消出票未支付订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/8e3e59214cfae2e1afa470119559e683/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/8e3e59214cfae2e1afa470119559e683/openapi.json)
- 查询订单退票原因：[https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/ca2d05e1c5b3d2b271fb96cf2e7f4cda/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/ca2d05e1c5b3d2b271fb96cf2e7f4cda/openapi.json)
- 改签航班批量查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/58eaa69d86c0bb41c0f334b95b6c8cf2/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/58eaa69d86c0bb41c0f334b95b6c8cf2/openapi.json)
- 查询去程改签航班：[https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/f277335b0fda4885798095b94a3d0bc8/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/f277335b0fda4885798095b94a3d0bc8/openapi.json)
- 查询返程改签航班：[https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/14d2bc475177e1dde633b4ca1972d53c/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/14d2bc475177e1dde633b4ca1972d53c/openapi.json)
- 改签验舱验价：[https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/fc0fef626c330003179e5377ee02750f/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/fc0fef626c330003179e5377ee02750f/openapi.json)
- 查询退票费详情：[https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/da16089c5560ff14541029aceefc54de/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/da16089c5560ff14541029aceefc54de/openapi.json)
- 改签申请接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/fb50ef2594daff9dd6322cbb5489bcbc/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/fb50ef2594daff9dd6322cbb5489bcbc/openapi.json)
- 退票申请：[https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/2c00306da25dd21c664a2404d553029b/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/2c00306da25dd21c664a2404d553029b/openapi.json)
- 改签支付接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/722fd8c97825bdea860322e28ac6dcbd/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/722fd8c97825bdea860322e28ac6dcbd/openapi.json)
- 查询退票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/e240e7dde1c1a18499e136f075403f75/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/e240e7dde1c1a18499e136f075403f75/openapi.json)
- 改签订单查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/69650a619af368c12a6ee24947ad7572/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/69650a619af368c12a6ee24947ad7572/openapi.json)
- 取消改签未支付订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/544a66d5696a6e07b69dc8df98d6f825/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-ghndc2c/544a66d5696a6e07b69dc8df98d6f825/openapi.json)



### 南航 NDC2B（`AIR_CZ_NDC2B`）

- 产品介绍（适用场景，必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-nhndc2b/14228.md](https://open.yeepay.com/docs-v3/solution/hlyd-nhndc2b/14228.md)
- 渠道配置说明（对接前必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-nhndc2b/14360.md](https://open.yeepay.com/docs-v3/solution/hlyd-nhndc2b/14360.md)
- 接口调用指引：[https://open.yeepay.com/docs-v3/solution/hlyd-nhndc2b/14416.md](https://open.yeepay.com/docs-v3/solution/hlyd-nhndc2b/14416.md)

- 改签航班批量查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/c1bc667b9299979b8de601f81461032a/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/c1bc667b9299979b8de601f81461032a/openapi.json)
- 查询去程改签航班：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/90949b6cfd26574a426edea70f6f3485/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/90949b6cfd26574a426edea70f6f3485/openapi.json)
- 批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/0676f43ba89ef089f43c6f36ca40fa4a/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/0676f43ba89ef089f43c6f36ca40fa4a/openapi.json)
- 来回程去程批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/7551e734ecfa518db7c1e6175abe5bfb/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/7551e734ecfa518db7c1e6175abe5bfb/openapi.json)
- 查询返程改签航班：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/fb465909b8627e4912b4a32d1030164c/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/fb465909b8627e4912b4a32d1030164c/openapi.json)
- 改签申请接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/2ac82abfbbba61cc903d25f55ed38aa8/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/2ac82abfbbba61cc903d25f55ed38aa8/openapi.json)
- 来回程返程批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/a4315d65e05d0a6ce8724fae0d6380bf/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/a4315d65e05d0a6ce8724fae0d6380bf/openapi.json)
- 验仓验价：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/29b2cd4a11745fefecc14912d2f95dd8/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/29b2cd4a11745fefecc14912d2f95dd8/openapi.json)
- 改签支付接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/24988d9aa627ea723a4769c83e481a76/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/24988d9aa627ea723a4769c83e481a76/openapi.json)
- 改签订单查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/b899ce5418c4ff13144e96c1af4d6306/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/b899ce5418c4ff13144e96c1af4d6306/openapi.json)
- 验舱验价（外部）：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/695146e2eb92eb4df74536a74b022fcf/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/695146e2eb92eb4df74536a74b022fcf/openapi.json)
- 外部pnr验舱验价：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/40a65e5a692bf1f5f1a81ec33021bda4/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/40a65e5a692bf1f5f1a81ec33021bda4/openapi.json)
- 出票创建订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/8425bc94a44e3d1bb3c8c026b2702c00/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/8425bc94a44e3d1bb3c8c026b2702c00/openapi.json)
- 出票订单支付：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/a0e2a88fbfdb8e16682cda2046d6a40d/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/a0e2a88fbfdb8e16682cda2046d6a40d/openapi.json)
- 退票费用详情查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/dce30dee7d6980c287d5c2992de9b752/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/dce30dee7d6980c287d5c2992de9b752/openapi.json)
- 查询出票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/194309a52da9de185b531cfc697cfca8/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/194309a52da9de185b531cfc697cfca8/openapi.json)
- 退票申请：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/61c0bc869c02703fe2244a64cf2860d9/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/61c0bc869c02703fe2244a64cf2860d9/openapi.json)
- 查询退票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/b8a0cabd92e8b9ab1727347dfd138421/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhndc2b/b8a0cabd92e8b9ab1727347dfd138421/openapi.json)



### 厦航 NDC2B（`AIR_MF_NDC2B`）

- 产品介绍（适用场景，必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-xhndc2b/13819.md](https://open.yeepay.com/docs-v3/solution/hlyd-xhndc2b/13819.md)
- 接口调用指引：[https://open.yeepay.com/docs-v3/solution/hlyd-xhndc2b/14417.md](https://open.yeepay.com/docs-v3/solution/hlyd-xhndc2b/14417.md)

- 批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc2b/aba2b11d01c3742d77a4391276731579/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc2b/aba2b11d01c3742d77a4391276731579/openapi.json)
- 获取pnr航班信息：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc2b/7d7b04e989115e193107af57ad662dd2/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc2b/7d7b04e989115e193107af57ad662dd2/openapi.json)
- 出票创建订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc2b/2d8fe42de2f833581faa077f788329fa/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc2b/2d8fe42de2f833581faa077f788329fa/openapi.json)
- 出票订单支付：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc2b/08b94fd98ee63a60c5d191649dcfe29a/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc2b/08b94fd98ee63a60c5d191649dcfe29a/openapi.json)
- 查询出票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc2b/042aec9e604155f2f06c0a16c5f9ba06/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc2b/042aec9e604155f2f06c0a16c5f9ba06/openapi.json)
- 查询退票费详情：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc2b/51e2038e383ecfc953bf1ab5a0747c63/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc2b/51e2038e383ecfc953bf1ab5a0747c63/openapi.json)
- 取消出票未支付订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc2b/9181a74736d3b86345dadbc90e29390e/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc2b/9181a74736d3b86345dadbc90e29390e/openapi.json)
- 退票申请：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc2b/bbc4cd33ff8bc2cfdff66557dbd84a85/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc2b/bbc4cd33ff8bc2cfdff66557dbd84a85/openapi.json)
- 查询退票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc2b/c55c6eea07345c455a100597687a61d2/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc2b/c55c6eea07345c455a100597687a61d2/openapi.json)
- 改签航班批量查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc2b/29f81692d9af87c8826aafca8ff5dad3/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc2b/29f81692d9af87c8826aafca8ff5dad3/openapi.json)
- 改签申请接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc2b/e286a04b20bc52074820789fd5eb78f6/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc2b/e286a04b20bc52074820789fd5eb78f6/openapi.json)
- 改签支付接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc2b/b1fb3726a5a825732f9a25e210426c4a/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc2b/b1fb3726a5a825732f9a25e210426c4a/openapi.json)
- 改签订单查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc2b/cdcc686a434d09ed24e4b736d593858f/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc2b/cdcc686a434d09ed24e4b736d593858f/openapi.json)
- 取消改签未支付订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc2b/ebd58b8a3f1d72f4206201da62fb1204/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhndc2b/ebd58b8a3f1d72f4206201da62fb1204/openapi.json)



### 东航 NDC2T（`AIR_MU_NDC2T`）

- 产品介绍（适用场景，必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-dhndc2t/12943.md](https://open.yeepay.com/docs-v3/solution/hlyd-dhndc2t/12943.md)
- 渠道配置说明（对接前必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-dhndc2t/12946.md](https://open.yeepay.com/docs-v3/solution/hlyd-dhndc2t/12946.md)
- 接口调用指引：[https://open.yeepay.com/docs-v3/solution/hlyd-dhndc2t/14418.md](https://open.yeepay.com/docs-v3/solution/hlyd-dhndc2t/14418.md)

- 外部查询改签航班政策：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhndc2t/d18b09180684862f5665e1932fdb54fb/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhndc2t/d18b09180684862f5665e1932fdb54fb/openapi.json)
- 改签航班批量查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhndc2t/24322cab50d699df38e74ee891f86f77/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhndc2t/24322cab50d699df38e74ee891f86f77/openapi.json)
- 验舱验价（外部）：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhndc2t/966b795bc7f3ccb35e3da08aebe98f18/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhndc2t/966b795bc7f3ccb35e3da08aebe98f18/openapi.json)
- 改签申请接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhndc2t/420c841038c492fed4d19999a813009d/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhndc2t/420c841038c492fed4d19999a813009d/openapi.json)
- 批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhndc2t/15e69232b3bfbcce60261950230e734b/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhndc2t/15e69232b3bfbcce60261950230e734b/openapi.json)
- 改签支付接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhndc2t/0baa10f95ef302bf877f1f11e8ffef58/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhndc2t/0baa10f95ef302bf877f1f11e8ffef58/openapi.json)
- 出票创建订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhndc2t/ab96c631d50e81c5f961bcbf25e49475/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhndc2t/ab96c631d50e81c5f961bcbf25e49475/openapi.json)
- 出票订单支付：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhndc2t/61cb6463141119abd41762825ad4f9cd/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhndc2t/61cb6463141119abd41762825ad4f9cd/openapi.json)
- 查询出票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhndc2t/066999ed9322bd434f20ad5ec4dd6b48/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhndc2t/066999ed9322bd434f20ad5ec4dd6b48/openapi.json)
- 查询退票费详情-new：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhndc2t/8e0251b8f27dd86e04c9049a1eeda4a3/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhndc2t/8e0251b8f27dd86e04c9049a1eeda4a3/openapi.json)
- 退票申请：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhndc2t/d3779a48ccf8e469f915ffdbc55f6e2e/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhndc2t/d3779a48ccf8e469f915ffdbc55f6e2e/openapi.json)
- 查询退票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhndc2t/006bfae3a90bab38e29382170867e962/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhndc2t/006bfae3a90bab38e29382170867e962/openapi.json)
- 改签订单查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhndc2t/657538ca3ad286a7b345fb515d41e14b/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhndc2t/657538ca3ad286a7b345fb515d41e14b/openapi.json)



### 深航 NDC2B（`AIR_ZH_B2B`）

- 产品介绍（适用场景，必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-shb2b/14035.md](https://open.yeepay.com/docs-v3/solution/hlyd-shb2b/14035.md)
- 接口调用指引：[https://open.yeepay.com/docs-v3/solution/hlyd-shb2b/14419.md](https://open.yeepay.com/docs-v3/solution/hlyd-shb2b/14419.md)

【深航B2B往返】

- 改签订单查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/b083c8db8880429bba105c048a7ea1b6/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/b083c8db8880429bba105c048a7ea1b6/openapi.json)
- 改签支付接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/4c4f120e57ea9448ccb7a07c48df40ff/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/4c4f120e57ea9448ccb7a07c48df40ff/openapi.json)
- 改签航班批量查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/a4546d484e137a6c92e317daae0e7131/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/a4546d484e137a6c92e317daae0e7131/openapi.json)
- 批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/e875a3ad4f52e44482240713d709930e/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/e875a3ad4f52e44482240713d709930e/openapi.json)
- 查询退票费详情：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/1d4db1fbfe9d6377c9226ff1e48b90ce/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/1d4db1fbfe9d6377c9226ff1e48b90ce/openapi.json)
- 退票申请：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/787e8665307884350308429f4fc60451/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/787e8665307884350308429f4fc60451/openapi.json)
- 查询退票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/d99fa3a9dd5df426e62b19597322920a/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/d99fa3a9dd5df426e62b19597322920a/openapi.json)
- 改签申请接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/70cf1f7eb14c9f52277f07e84a2775f3/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/70cf1f7eb14c9f52277f07e84a2775f3/openapi.json)
- 来回程去程批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/e8cb5f581442030021d62fd780fa674d/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/e8cb5f581442030021d62fd780fa674d/openapi.json)
- 来回程返程批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/5dc624e80d9ab94e3229ec29f675c19d/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/5dc624e80d9ab94e3229ec29f675c19d/openapi.json)
- 获取pnr航班信息：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/a1d41c14c1d0aa9b9cc1e228d962fe42/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/a1d41c14c1d0aa9b9cc1e228d962fe42/openapi.json)
- 验仓验价：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/62ef6dc6cdbfc1c60305b7d3d9a420a6/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/62ef6dc6cdbfc1c60305b7d3d9a420a6/openapi.json)
- 出票创建订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/0503bf609757acf2e75aa8cbc0d8323b/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/0503bf609757acf2e75aa8cbc0d8323b/openapi.json)
- 出票订单支付：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/319e33a217f7368ff7ceef7731ccf024/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/319e33a217f7368ff7ceef7731ccf024/openapi.json)
- 查询出票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/7dd21654ce1c39ec7632d219e8e71f11/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/7dd21654ce1c39ec7632d219e8e71f11/openapi.json)

【深航B2B单程】

- 改签航班批量查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/2e0a791950a53842e60d83295368cdff/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/2e0a791950a53842e60d83295368cdff/openapi.json)
- 批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/effbafd134873f47f49c740581fb1854/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/effbafd134873f47f49c740581fb1854/openapi.json)
- 改签申请接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/184264bf0c886f2ee3198ff54561c51d/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/184264bf0c886f2ee3198ff54561c51d/openapi.json)
- 获取pnr航班信息：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/746206d63610c80c08bdf440226b462a/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/746206d63610c80c08bdf440226b462a/openapi.json)
- 验仓验价：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/96fe1255e032940e2739e06072855b95/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/96fe1255e032940e2739e06072855b95/openapi.json)
- 改签支付接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/90c5841cb33b6ffdf75850044c595725/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/90c5841cb33b6ffdf75850044c595725/openapi.json)
- 查询退票费详情：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/ccd44234c58cba8173f8ae706a0fce24/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/ccd44234c58cba8173f8ae706a0fce24/openapi.json)
- 出票创建订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/0a7ff96e4fa7c92a13ccab013d580930/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/0a7ff96e4fa7c92a13ccab013d580930/openapi.json)
- 改签订单查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/d45959550312221e15fde04690b18acd/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/d45959550312221e15fde04690b18acd/openapi.json)
- 退票申请：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/54d0ad877584296abb129e2e4f60ee67/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/54d0ad877584296abb129e2e4f60ee67/openapi.json)
- 出票订单支付：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/eb6bdd281dfc2688a42174679b8e5bbd/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/eb6bdd281dfc2688a42174679b8e5bbd/openapi.json)
- 查询退票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/37b1fe960daba91fffadbdb5a3a9db15/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/37b1fe960daba91fffadbdb5a3a9db15/openapi.json)
- 查询出票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/b9e255d57bdc3d30828bfd835b86749c/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/b9e255d57bdc3d30828bfd835b86749c/openapi.json)
- 来回程去程批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/61d584107d2d965b4bc26d8c9958b518/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/61d584107d2d965b4bc26d8c9958b518/openapi.json)
- 来回程返程批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/1c7836dbabd12c458d20e3b35633733a/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-shb2b/1c7836dbabd12c458d20e3b35633733a/openapi.json)



## 航司 B2B



### 东航 B2T（`AIR_MU_B2T_NEW`）

- 产品介绍（适用场景，必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-dhb2b/13216.md](https://open.yeepay.com/docs-v3/solution/hlyd-dhb2b/13216.md)
- 渠道配置说明（对接前必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-dhb2b/13244.md](https://open.yeepay.com/docs-v3/solution/hlyd-dhb2b/13244.md)
- 接口调用指引：[https://open.yeepay.com/docs-v3/solution/hlyd-dhb2b/14420.md](https://open.yeepay.com/docs-v3/solution/hlyd-dhb2b/14420.md)

- 更新token：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/c999d5b6b8bab8662faae7fafe463f04/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/c999d5b6b8bab8662faae7fafe463f04/openapi.json)
- 批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/c1adc7e5ae982a010af2eb442b583640/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/c1adc7e5ae982a010af2eb442b583640/openapi.json)
- 获取pnr航班信息：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/b0e864a6eccfc779c8119f5a4468797f/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/b0e864a6eccfc779c8119f5a4468797f/openapi.json)
- 验仓验价：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/7507dafaedac784a18c852536bbd3c88/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/7507dafaedac784a18c852536bbd3c88/openapi.json)
- 出票创建订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/3f258712c3ba708ba78a60afde94352a/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/3f258712c3ba708ba78a60afde94352a/openapi.json)
- 出票订单支付：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/0e762b65028402721e10bbc97ede52b7/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/0e762b65028402721e10bbc97ede52b7/openapi.json)
- 查询出票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/b980be726641e1ce5cfa8dde32ee3bcf/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/b980be726641e1ce5cfa8dde32ee3bcf/openapi.json)
- 查询退票费详情：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/62cb1b02c845efe41e4f41b8c1fc87fd/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/62cb1b02c845efe41e4f41b8c1fc87fd/openapi.json)
- 导入航司订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/60d22149eee1175d3675575416f123b1/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/60d22149eee1175d3675575416f123b1/openapi.json)
- 取消出票未支付订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/b04f44eace1a193f15006e8a8a45624e/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/b04f44eace1a193f15006e8a8a45624e/openapi.json)
- 退票申请：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/729404b28f3bd32761c667a668453f4c/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/729404b28f3bd32761c667a668453f4c/openapi.json)
- 独立支付：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/65a2e5f265ac3d8ee8e39ff5d2bb3f96/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/65a2e5f265ac3d8ee8e39ff5d2bb3f96/openapi.json)
- 查询退票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/f5c80b20fdee4e645ff315a56f12a716/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/f5c80b20fdee4e645ff315a56f12a716/openapi.json)
- 改签航班批量查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/d8ffe0099bb7e2c98f8e6e5c37baffa2/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/d8ffe0099bb7e2c98f8e6e5c37baffa2/openapi.json)
- 改签申请接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/d71d9e49824fddceb67a26b34e5bc770/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/d71d9e49824fddceb67a26b34e5bc770/openapi.json)
- 改签支付接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/45ddfa251d2530f6865be72a998b03dc/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/45ddfa251d2530f6865be72a998b03dc/openapi.json)
- 改签订单查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/43b136e4e130934ebda7768e3e728671/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-dhb2b/43b136e4e130934ebda7768e3e728671/openapi.json)



### 厦航 B2B（高舱导入）（`AIR_MF_B2B`）

- 产品介绍（适用场景，必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-xhb2b/13195.md](https://open.yeepay.com/docs-v3/solution/hlyd-xhb2b/13195.md)
- 接口调用指引：[https://open.yeepay.com/docs-v3/solution/hlyd-xhb2b/14421.md](https://open.yeepay.com/docs-v3/solution/hlyd-xhb2b/14421.md)

- 获取pnr航班信息：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhb2b/b0a3f2a0d6f86051e6ab6c49d6d99e75/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhb2b/b0a3f2a0d6f86051e6ab6c49d6d99e75/openapi.json)
- 出票创建订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhb2b/a3b1c195e3033e5086eb7482c0942e4a/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhb2b/a3b1c195e3033e5086eb7482c0942e4a/openapi.json)
- 出票订单支付：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhb2b/f8218cc7aea3923da3fab72d435544c0/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhb2b/f8218cc7aea3923da3fab72d435544c0/openapi.json)
- 查询出票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhb2b/57e249d780392f6757229ae62dc68318/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhb2b/57e249d780392f6757229ae62dc68318/openapi.json)
- 查询退票费详情-new：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhb2b/3d7a8f67f51564c349478f7d52abee3b/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhb2b/3d7a8f67f51564c349478f7d52abee3b/openapi.json)
- 查询退改规则：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhb2b/645f86b5cec4da0a56ffea7a891720c9/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhb2b/645f86b5cec4da0a56ffea7a891720c9/openapi.json)
- 退票申请：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhb2b/6b406fba78d7b12a242a3bff04399604/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhb2b/6b406fba78d7b12a242a3bff04399604/openapi.json)
- 查询行李信息：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhb2b/31914689514c64a97d950a8d9eea3eeb/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhb2b/31914689514c64a97d950a8d9eea3eeb/openapi.json)
- 查询退票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhb2b/1a8207690ac54d845f7a57dd468970fa/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhb2b/1a8207690ac54d845f7a57dd468970fa/openapi.json)
- 改签航班批量查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhb2b/5b312a4c28761c463feda5a54c011676/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhb2b/5b312a4c28761c463feda5a54c011676/openapi.json)
- 改签申请接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhb2b/26a95b3bf6c0fa4ba909250facfb5ae9/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhb2b/26a95b3bf6c0fa4ba909250facfb5ae9/openapi.json)
- 改签支付接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhb2b/18b0ad2e92c278e9f6f4d23bfe8d9c77/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhb2b/18b0ad2e92c278e9f6f4d23bfe8d9c77/openapi.json)
- 改签订单查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-xhb2b/4a4ae8ed6f8e3608223f48427320c936/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-xhb2b/4a4ae8ed6f8e3608223f48427320c936/openapi.json)



### 南航 B2B（国内）（`AIR_CZ_NEW`）

- 产品介绍（适用场景，必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-nhb2b/12995.md](https://open.yeepay.com/docs-v3/solution/hlyd-nhb2b/12995.md)
- 接口调用指引：[https://open.yeepay.com/docs-v3/solution/hlyd-nhb2b/14422.md](https://open.yeepay.com/docs-v3/solution/hlyd-nhb2b/14422.md)

- 获取pnr航班信息：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/60430f4a984aa0a534e027339a7580a7/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/60430f4a984aa0a534e027339a7580a7/openapi.json)
- 出票创建订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/38398fab1dd3cccf0f624d935a57898d/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/38398fab1dd3cccf0f624d935a57898d/openapi.json)
- 出票订单支付：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/ba2cf4148007ed8a8b041f8abd9bbf96/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/ba2cf4148007ed8a8b041f8abd9bbf96/openapi.json)
- 查询出票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/8e28c44c7e1bb849ce85affc38d326bb/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/8e28c44c7e1bb849ce85affc38d326bb/openapi.json)
- 查询退改规则：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/24e709bb46c4ae9841eecac2a9e8c503/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/24e709bb46c4ae9841eecac2a9e8c503/openapi.json)
- 改签航班批量查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/7426f79c9a7f5af0a6cc457b2a7fb195/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/7426f79c9a7f5af0a6cc457b2a7fb195/openapi.json)
- 查询去程改签航班：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/db10579cd6a91c599220192b86e380eb/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/db10579cd6a91c599220192b86e380eb/openapi.json)
- 验仓验价：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/d4ff76af57c1ebcc7eca3807b9a431a6/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/d4ff76af57c1ebcc7eca3807b9a431a6/openapi.json)
- 改签申请接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/1ef4c899cd6f0d5cae3a2ea3a91adc1c/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/1ef4c899cd6f0d5cae3a2ea3a91adc1c/openapi.json)
- PNR模式查询去程航班信息：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/8f1dd6e7a88b9cf615c146330c591ba9/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/8f1dd6e7a88b9cf615c146330c591ba9/openapi.json)
- 改签支付接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/7101e4daaff4511510bbd4e6a0862fb7/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/7101e4daaff4511510bbd4e6a0862fb7/openapi.json)
- 改签订单查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/69c8d2b4af56551603877db8d897360f/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/69c8d2b4af56551603877db8d897360f/openapi.json)
- 查询退票原因：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/98ecba69accf294459adb07e02fc03e4/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/98ecba69accf294459adb07e02fc03e4/openapi.json)
- 外部pnr验舱验价：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/548bada0dbbcaf6d92cc76c5b773e7b9/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/548bada0dbbcaf6d92cc76c5b773e7b9/openapi.json)
- 来回程去程批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/291925ddbc6e2d194d0c22d268e0f865/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/291925ddbc6e2d194d0c22d268e0f865/openapi.json)
- 批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/9d4f684ba088d28ad1c2ae7d0aee496a/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/9d4f684ba088d28ad1c2ae7d0aee496a/openapi.json)
- 查询退票费详情：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/0e0f9e664029e8912996d65c1cf09761/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/0e0f9e664029e8912996d65c1cf09761/openapi.json)
- 查询行李信息：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/7d2d180c45c41870f36e747816456190/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/7d2d180c45c41870f36e747816456190/openapi.json)
- 验舱验价（外部）：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/846437e17a8d1d5f37fe3bb0e1762499/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/846437e17a8d1d5f37fe3bb0e1762499/openapi.json)
- 退票申请：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/729db3e07a09db3a41dc1734e04ce44e/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/729db3e07a09db3a41dc1734e04ce44e/openapi.json)
- 查询退票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/64cd16e5e16f6202eb5bd42f2f2e8ecc/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/64cd16e5e16f6202eb5bd42f2f2e8ecc/openapi.json)
- 查询返程改签航班：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/0bb759879533c4232940d44d174f0cf1/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/0bb759879533c4232940d44d174f0cf1/openapi.json)
- 来回程返程批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/8860b0b3ad5538d2ccc6c2bdd0341a1a/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/8860b0b3ad5538d2ccc6c2bdd0341a1a/openapi.json)



### 南航 B2B（国际）（`AIR_CZ_B2B`）

- 产品介绍（适用场景，必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-nhb2b/12995.md](https://open.yeepay.com/docs-v3/solution/hlyd-nhb2b/12995.md)
- 接口调用指引：[https://open.yeepay.com/docs-v3/solution/hlyd-nhb2b/14422.md](https://open.yeepay.com/docs-v3/solution/hlyd-nhb2b/14422.md)

- PNR模式查询去程航班信息：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/40195594f1244e7ec627b1c6a5a35585/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/40195594f1244e7ec627b1c6a5a35585/openapi.json)
- 来回程返程批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/f416d0fbce436dde50730df3a12bba3b/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/f416d0fbce436dde50730df3a12bba3b/openapi.json)
- 出票创建订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/04c32d4d95425f73b3a1d6502aed4d48/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/04c32d4d95425f73b3a1d6502aed4d48/openapi.json)
- 出票订单支付：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/58fe2003170159fd68519b7f9840fdb2/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/58fe2003170159fd68519b7f9840fdb2/openapi.json)
- 查询出票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/0aaf61723a352ba7ea1be4502df85765/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/0aaf61723a352ba7ea1be4502df85765/openapi.json)
- 查询退改规则：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/33501018d710f3e2dd8438a4050ea9c2/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/33501018d710f3e2dd8438a4050ea9c2/openapi.json)
- 查询去程改签航班：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/2750dc2828e8f769ede73fd216f19b62/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/2750dc2828e8f769ede73fd216f19b62/openapi.json)
- 验仓验价：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/2ee2b71a912ddc28699435eca8bd6486/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/2ee2b71a912ddc28699435eca8bd6486/openapi.json)
- 改签订单查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/c32efcb7f667f6c5def39db8eda2e6ce/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/c32efcb7f667f6c5def39db8eda2e6ce/openapi.json)
- 外部pnr验舱验价：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/94bdf49dcb9b7357c377c7310c411343/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/94bdf49dcb9b7357c377c7310c411343/openapi.json)
- 来回程去程批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/0563cad67522fc198dee8690630e475a/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/0563cad67522fc198dee8690630e475a/openapi.json)
- 改签支付接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/3f8025f81c08669208bc39bdcbaf4eda/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/3f8025f81c08669208bc39bdcbaf4eda/openapi.json)
- 改签航班批量查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/3d22f11fce309b14796ac009553b3451/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/3d22f11fce309b14796ac009553b3451/openapi.json)
- 获取pnr航班信息：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/f00b6379b82a515a9478b6e58b783de9/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/f00b6379b82a515a9478b6e58b783de9/openapi.json)
- 批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/b8b0e04211dce1c104dfcdb685c9b9ad/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/b8b0e04211dce1c104dfcdb685c9b9ad/openapi.json)
- 查询退票费详情：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/e417baa9cdf34202f71b55a27da899e8/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/e417baa9cdf34202f71b55a27da899e8/openapi.json)
- 查询行李信息：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/c80728aa924ef2e490a13188e1178518/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/c80728aa924ef2e490a13188e1178518/openapi.json)
- 查询退票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/b4c174fbc208372a8facfe462868ebf1/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/b4c174fbc208372a8facfe462868ebf1/openapi.json)
- 验舱验价（外部）：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/ed80be7e22f987619ac49099673ad49f/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/ed80be7e22f987619ac49099673ad49f/openapi.json)
- 退票申请：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/4e79ea6638ba8bc06d414c9fc94760f7/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/4e79ea6638ba8bc06d414c9fc94760f7/openapi.json)
- 改签申请接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/494ad0d24e15c7da81c7ea265c7f4cb4/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/494ad0d24e15c7da81c7ea265c7f4cb4/openapi.json)
- 查询返程改签航班：[https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/7a1ccfe60223a5bda015a388f354cf62/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-nhb2b/7a1ccfe60223a5bda015a388f354cf62/openapi.json)



### 港航 B2B（`AIR_HX_B2B`）

- 产品介绍（适用场景，必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-ghb2b/14300.md](https://open.yeepay.com/docs-v3/solution/hlyd-ghb2b/14300.md)
- 接口调用指引：[https://open.yeepay.com/docs-v3/solution/hlyd-ghb2b/14423.md](https://open.yeepay.com/docs-v3/solution/hlyd-ghb2b/14423.md)

- 获取pnr航班信息：[https://open.yeepay.com/apis/docs/solutions/hlyd-ghb2b/5364de2e6064f4d8a13c960b970b9f24/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-ghb2b/5364de2e6064f4d8a13c960b970b9f24/openapi.json)
- 出票创建订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-ghb2b/89ea5cb67579289ce2b6a46c42e30424/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-ghb2b/89ea5cb67579289ce2b6a46c42e30424/openapi.json)
- 出票订单支付：[https://open.yeepay.com/apis/docs/solutions/hlyd-ghb2b/717fb24cc33821afb4bcd529696cdfce/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-ghb2b/717fb24cc33821afb4bcd529696cdfce/openapi.json)
- 查询出票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-ghb2b/380714d486fbd50c0c9dfc7e4d8be9f7/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-ghb2b/380714d486fbd50c0c9dfc7e4d8be9f7/openapi.json)



## CDP 渠道



### CDP 渠道（`AIR_**_CDP_PTS`）

- 产品介绍（适用场景，必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-cdpqd/12969.md](https://open.yeepay.com/docs-v3/solution/hlyd-cdpqd/12969.md)
- 渠道配置说明（对接前必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-cdpqd/12972.md](https://open.yeepay.com/docs-v3/solution/hlyd-cdpqd/12972.md)
- 接口调用指引：[https://open.yeepay.com/docs-v3/solution/hlyd-cdpqd/14424.md](https://open.yeepay.com/docs-v3/solution/hlyd-cdpqd/14424.md)

- 改签航班批量查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/293643def1ba1161bcdcfbfe434ab76d/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/293643def1ba1161bcdcfbfe434ab76d/openapi.json)
- 改签申请接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/3b63d1d64de8f499eadb49b53aa90964/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/3b63d1d64de8f499eadb49b53aa90964/openapi.json)
- 查询退票原因：[https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/50a889faa543a3d86525f9325e47e593/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/50a889faa543a3d86525f9325e47e593/openapi.json)
- 批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/2e36742b377be90ffbf553692153d9a1/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/2e36742b377be90ffbf553692153d9a1/openapi.json)
- 获取pnr航班信息：[https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/b8262a23052612c56595a230615f2250/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/b8262a23052612c56595a230615f2250/openapi.json)
- 验仓验价：[https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/950d4aea25553820c10d71160da80944/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/950d4aea25553820c10d71160da80944/openapi.json)
- 改签支付接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/0f542615d6c3ceb0f8bb299b1a9fe396/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/0f542615d6c3ceb0f8bb299b1a9fe396/openapi.json)
- 出票创建订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/34470a05eb3bfbee2352941dd1b94320/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/34470a05eb3bfbee2352941dd1b94320/openapi.json)
- 出票订单支付：[https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/aaf662be6cd123f4c54c4d90d24b1373/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/aaf662be6cd123f4c54c4d90d24b1373/openapi.json)
- 查询出票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/7ad2e4fc29a62f8e86213a998a5675b2/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/7ad2e4fc29a62f8e86213a998a5675b2/openapi.json)
- 查询退票费详情：[https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/97ef7f4a6f519343cfcc3c26a3639178/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/97ef7f4a6f519343cfcc3c26a3639178/openapi.json)
- 导入航司订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/b49732e7c77fbc9badd37b4f49960698/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/b49732e7c77fbc9badd37b4f49960698/openapi.json)
- 退票申请：[https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/ce93b7b0e618ad3ba298514c691dfad1/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/ce93b7b0e618ad3ba298514c691dfad1/openapi.json)
- 查询退票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/2e37d41c9bf5cbd339a02696196e9a7b/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/2e37d41c9bf5cbd339a02696196e9a7b/openapi.json)
- 改签订单查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/97f58cc60361f36cb40942c5c9a9e029/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-cdpqd/97f58cc60361f36cb40942c5c9a9e029/openapi.json)



## 分销渠道（OTA）



### 美团（`AIR_MT_PTS`）

- 产品介绍（适用场景，必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-mt/12659.md](https://open.yeepay.com/docs-v3/solution/hlyd-mt/12659.md)
- 渠道配置说明（对接前必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-mt/12679.md](https://open.yeepay.com/docs-v3/solution/hlyd-mt/12679.md)
- 接口调用指引：[https://open.yeepay.com/docs-v3/solution/hlyd-mt/14425.md](https://open.yeepay.com/docs-v3/solution/hlyd-mt/14425.md)

- 改签航班批量查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-mt/217ffec3caf17a44bf340fc11d93e8ab/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-mt/217ffec3caf17a44bf340fc11d93e8ab/openapi.json)
- 改签申请接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-mt/b3d5c779237614a9cef5305b85a28273/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-mt/b3d5c779237614a9cef5305b85a28273/openapi.json)
- 批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-mt/51b7dae1031b20174cacc7e69d6e4bf0/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-mt/51b7dae1031b20174cacc7e69d6e4bf0/openapi.json)
- 查询出票航班详情：[https://open.yeepay.com/apis/docs/solutions/hlyd-mt/185afe2ab60395b0fb41349aa1469a7f/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-mt/185afe2ab60395b0fb41349aa1469a7f/openapi.json)
- 验仓验价：[https://open.yeepay.com/apis/docs/solutions/hlyd-mt/3f97b78c2ce73939fca9916a27115445/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-mt/3f97b78c2ce73939fca9916a27115445/openapi.json)
- 改签支付接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-mt/32cfba8a13694631a8418e4d246e55fa/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-mt/32cfba8a13694631a8418e4d246e55fa/openapi.json)
- 出票创建订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-mt/eef15e7066deb4f1a7a6c1e2d24eda9e/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-mt/eef15e7066deb4f1a7a6c1e2d24eda9e/openapi.json)
- 出票订单支付：[https://open.yeepay.com/apis/docs/solutions/hlyd-mt/354680832fcea7e2b7057a5ac2c489f8/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-mt/354680832fcea7e2b7057a5ac2c489f8/openapi.json)
- 查询出票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-mt/e7728fab6844dee91aa0cc03c0b97bdd/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-mt/e7728fab6844dee91aa0cc03c0b97bdd/openapi.json)
- 查询退票费详情-new：[https://open.yeepay.com/apis/docs/solutions/hlyd-mt/a7ba7390e92513e12fc5fe070e40ee7e/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-mt/a7ba7390e92513e12fc5fe070e40ee7e/openapi.json)
- 退票申请：[https://open.yeepay.com/apis/docs/solutions/hlyd-mt/d5542ec466d3f3446d5be39e42606a61/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-mt/d5542ec466d3f3446d5be39e42606a61/openapi.json)
- 查询退票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-mt/fffb8ef15de06d87e6ba6c830f3b6284/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-mt/fffb8ef15de06d87e6ba6c830f3b6284/openapi.json)
- 改签订单查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-mt/8c0f24a304f10044bcb756fd2ab2370f/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-mt/8c0f24a304f10044bcb756fd2ab2370f/openapi.json)



### 航班管家（`AIR_HBGJ_PTS`）

- 产品介绍（适用场景，必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-hbgj/12683.md](https://open.yeepay.com/docs-v3/solution/hlyd-hbgj/12683.md)
- 渠道配置说明（对接前必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-hbgj/12686.md](https://open.yeepay.com/docs-v3/solution/hlyd-hbgj/12686.md)
- 接口调用指引：[https://open.yeepay.com/docs-v3/solution/hlyd-hbgj/14426.md](https://open.yeepay.com/docs-v3/solution/hlyd-hbgj/14426.md)

- 改签费用查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-hbgj/c379a1046f90b893557efbd459480ae5/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-hbgj/c379a1046f90b893557efbd459480ae5/openapi.json)
- 改签申请接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-hbgj/5a5fa2512d295bc18b5d557fb34a0888/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-hbgj/5a5fa2512d295bc18b5d557fb34a0888/openapi.json)
- 退票费用查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-hbgj/22781293bd688d958f3be27e4c26d2c3/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-hbgj/22781293bd688d958f3be27e4c26d2c3/openapi.json)
- 批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-hbgj/9fa8671d6d5f2796100bbd67eca81450/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-hbgj/9fa8671d6d5f2796100bbd67eca81450/openapi.json)
- 查询出票航班详情：[https://open.yeepay.com/apis/docs/solutions/hlyd-hbgj/edf7f2f34f6b96fae76c68bc2268c128/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-hbgj/edf7f2f34f6b96fae76c68bc2268c128/openapi.json)
- 验仓验价：[https://open.yeepay.com/apis/docs/solutions/hlyd-hbgj/d8a3b2dde3181c8257e2e45efbd1e8ae/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-hbgj/d8a3b2dde3181c8257e2e45efbd1e8ae/openapi.json)
- 改签支付接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-hbgj/0ec5ba872f1179835987f9028c4cc4df/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-hbgj/0ec5ba872f1179835987f9028c4cc4df/openapi.json)
- 出票创建订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-hbgj/26d6e896db39edc7d7bdd357d6984c95/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-hbgj/26d6e896db39edc7d7bdd357d6984c95/openapi.json)
- 出票订单支付：[https://open.yeepay.com/apis/docs/solutions/hlyd-hbgj/d869c99656ec60fc9de27338a87b2506/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-hbgj/d869c99656ec60fc9de27338a87b2506/openapi.json)
- 查询出票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-hbgj/d7852cd2408d9d3205dc75b59a6ce22e/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-hbgj/d7852cd2408d9d3205dc75b59a6ce22e/openapi.json)
- 退票申请：[https://open.yeepay.com/apis/docs/solutions/hlyd-hbgj/b31f0c758bb498b5d56b5fea80f313a7/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-hbgj/b31f0c758bb498b5d56b5fea80f313a7/openapi.json)
- 查询退票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-hbgj/129ccfc1c1a82b0b23d4473a72373a0a/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-hbgj/129ccfc1c1a82b0b23d4473a72373a0a/openapi.json)
- 改签订单查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-hbgj/bdffc7973c9f8f88ab4effb397c59f92/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-hbgj/bdffc7973c9f8f88ab4effb397c59f92/openapi.json)



### 蜗牛 / 去哪儿（`AIR_QUNAR_PTS`）

- 产品介绍（适用场景，必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-qne/12707.md](https://open.yeepay.com/docs-v3/solution/hlyd-qne/12707.md)
- 渠道配置说明（对接前必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-qne/12710.md](https://open.yeepay.com/docs-v3/solution/hlyd-qne/12710.md)
- 接口调用指引：[https://open.yeepay.com/docs-v3/solution/hlyd-qne/14427.md](https://open.yeepay.com/docs-v3/solution/hlyd-qne/14427.md)

- 改签航班批量查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-qne/9ca90593821a015f234e9a8195ae5582/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-qne/9ca90593821a015f234e9a8195ae5582/openapi.json)
- 改签申请接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-qne/4530de238502b5aee3ad8eec65a4a70f/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-qne/4530de238502b5aee3ad8eec65a4a70f/openapi.json)
- 批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-qne/9e69fd6d1c5d1cef75ffbe159c1f322e/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-qne/9e69fd6d1c5d1cef75ffbe159c1f322e/openapi.json)
- 查询出票航班详情：[https://open.yeepay.com/apis/docs/solutions/hlyd-qne/47ba327b57be22b98eee0e5dc3e14711/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-qne/47ba327b57be22b98eee0e5dc3e14711/openapi.json)
- 验仓验价：[https://open.yeepay.com/apis/docs/solutions/hlyd-qne/0ad19a1cd666b3b65b6e46ad4ccc42f5/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-qne/0ad19a1cd666b3b65b6e46ad4ccc42f5/openapi.json)
- 改签支付接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-qne/646e058fac455de8d1e52c4c49baac06/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-qne/646e058fac455de8d1e52c4c49baac06/openapi.json)
- 出票创建订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-qne/6f350848b6612b5249daaa73cec0189b/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-qne/6f350848b6612b5249daaa73cec0189b/openapi.json)
- 出票订单支付：[https://open.yeepay.com/apis/docs/solutions/hlyd-qne/5736586058c1336221a695e83618b69d/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-qne/5736586058c1336221a695e83618b69d/openapi.json)
- 查询出票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-qne/12ae3f826bb1b9873c71c353f3df494c/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-qne/12ae3f826bb1b9873c71c353f3df494c/openapi.json)
- 查询退票费详情-new：[https://open.yeepay.com/apis/docs/solutions/hlyd-qne/b26be92d375bc16823077bd874693e9c/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-qne/b26be92d375bc16823077bd874693e9c/openapi.json)
- 查询航司订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-qne/e17343fd137bd00f14b47f1ea35ec3ca/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-qne/e17343fd137bd00f14b47f1ea35ec3ca/openapi.json)
- 退票申请：[https://open.yeepay.com/apis/docs/solutions/hlyd-qne/40dfe505df48f152d8a0c574872251aa/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-qne/40dfe505df48f152d8a0c574872251aa/openapi.json)
- 查询退票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-qne/1ea83680196dbebca4f47216650521ed/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-qne/1ea83680196dbebca4f47216650521ed/openapi.json)
- 改签订单查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-qne/8e636fbd9b5bd3c70e5bacdfbf9714e1/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-qne/8e636fbd9b5bd3c70e5bacdfbf9714e1/openapi.json)



### 京杭（`AIR_JH_PTS`）

- 产品介绍（适用场景，必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-jh/13021.md](https://open.yeepay.com/docs-v3/solution/hlyd-jh/13021.md)
- 渠道配置说明（对接前必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-jh/13024.md](https://open.yeepay.com/docs-v3/solution/hlyd-jh/13024.md)
- 接口调用指引：[https://open.yeepay.com/docs-v3/solution/hlyd-jh/14428.md](https://open.yeepay.com/docs-v3/solution/hlyd-jh/14428.md)

- 改签航班批量查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-jh/14ee3cfc17b13a0f35bc3c22476ff77f/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-jh/14ee3cfc17b13a0f35bc3c22476ff77f/openapi.json)
- 改签申请接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-jh/9953a9514b2a810825f17416e1e32f7d/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-jh/9953a9514b2a810825f17416e1e32f7d/openapi.json)
- 批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-jh/3a900dc34f5f470bc5b734222f657d7f/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-jh/3a900dc34f5f470bc5b734222f657d7f/openapi.json)
- 查询出票航班详情：[https://open.yeepay.com/apis/docs/solutions/hlyd-jh/76c7c563b32ad9d8d09c72a2d17c90e1/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-jh/76c7c563b32ad9d8d09c72a2d17c90e1/openapi.json)
- 验仓验价：[https://open.yeepay.com/apis/docs/solutions/hlyd-jh/f2ce1333f818dec7cb51e00e74bedd15/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-jh/f2ce1333f818dec7cb51e00e74bedd15/openapi.json)
- 改签支付接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-jh/9e1a4ad1551fcb87bfeb7061da4e11a2/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-jh/9e1a4ad1551fcb87bfeb7061da4e11a2/openapi.json)
- 出票创建订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-jh/015c11191cbf983956d7c19e3434c0cf/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-jh/015c11191cbf983956d7c19e3434c0cf/openapi.json)
- 出票订单支付：[https://open.yeepay.com/apis/docs/solutions/hlyd-jh/527490f08486bf8af2b8d0bf6e73911b/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-jh/527490f08486bf8af2b8d0bf6e73911b/openapi.json)
- 查询出票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-jh/e0154ac829acb5cb5735e1d1e7f48c68/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-jh/e0154ac829acb5cb5735e1d1e7f48c68/openapi.json)
- 查询退票费详情-new：[https://open.yeepay.com/apis/docs/solutions/hlyd-jh/1c39c39d1a341ba03ae48a942c6a43ef/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-jh/1c39c39d1a341ba03ae48a942c6a43ef/openapi.json)
- 退票申请：[https://open.yeepay.com/apis/docs/solutions/hlyd-jh/91cf0815868e49fd91babbc6444805a4/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-jh/91cf0815868e49fd91babbc6444805a4/openapi.json)
- 查询退票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-jh/05b0ea6e9b8e791347dfe157d54d679f/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-jh/05b0ea6e9b8e791347dfe157d54d679f/openapi.json)
- 改签订单查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-jh/23745dd9b252ba856cdd795b606a47ea/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-jh/23745dd9b252ba856cdd795b606a47ea/openapi.json)



### 51BOOK（`AIR_51BOOK_PTS`）

- 产品介绍（适用场景，必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-51book/12755.md](https://open.yeepay.com/docs-v3/solution/hlyd-51book/12755.md)
- 渠道配置说明（对接前必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-51book/12770.md](https://open.yeepay.com/docs-v3/solution/hlyd-51book/12770.md)
- 接口调用指引：[https://open.yeepay.com/docs-v3/solution/hlyd-51book/14429.md](https://open.yeepay.com/docs-v3/solution/hlyd-51book/14429.md)

- 批量航班查询：[https://open.yeepay.com/apis/docs/solutions/hlyd-51book/6e361e90ca5f9bee5b36f3d413c51842/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-51book/6e361e90ca5f9bee5b36f3d413c51842/openapi.json)
- 查询出票航班详情：[https://open.yeepay.com/apis/docs/solutions/hlyd-51book/f73850aa36d8564629a0d62c51009acf/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-51book/f73850aa36d8564629a0d62c51009acf/openapi.json)
- 验仓验价：[https://open.yeepay.com/apis/docs/solutions/hlyd-51book/154d7da9e669c75ee317d46614381dd8/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-51book/154d7da9e669c75ee317d46614381dd8/openapi.json)
- 出票创建订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-51book/e6da32eef072f987685b6eddca072d4f/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-51book/e6da32eef072f987685b6eddca072d4f/openapi.json)
- 查询退票费详情-new：[https://open.yeepay.com/apis/docs/solutions/hlyd-51book/01cbec073018465086c9752e6508e0ec/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-51book/01cbec073018465086c9752e6508e0ec/openapi.json)
- 出票订单支付：[https://open.yeepay.com/apis/docs/solutions/hlyd-51book/abc2d30d4c86f34166c321f2c65dfaa3/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-51book/abc2d30d4c86f34166c321f2c65dfaa3/openapi.json)
- 查询出票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-51book/c80bfa00454a7564c07c0559808294fa/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-51book/c80bfa00454a7564c07c0559808294fa/openapi.json)
- 退票申请：[https://open.yeepay.com/apis/docs/solutions/hlyd-51book/5644fb01b5333e2548d12dfbc3d5a0c8/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-51book/5644fb01b5333e2548d12dfbc3d5a0c8/openapi.json)
- 查询退票订单：[https://open.yeepay.com/apis/docs/solutions/hlyd-51book/efcce1c8f8c7b18ffa9c63bf6a2713a7/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-51book/efcce1c8f8c7b18ffa9c63bf6a2713a7/openapi.json)



## 辅助接口（通用，`hlyd-tyjk`）

- 产品介绍（适用场景，必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-tyjk/13073.md](https://open.yeepay.com/docs-v3/solution/hlyd-tyjk/13073.md)



| 接口分类          | 接口说明                              | API                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| ------------- | --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 文件上传          | 用于航司非自愿退改上传附件                     | 文件上传：[https://open.yeepay.com/apis/docs/solutions/hlyd-tyjk/052a1a3c0142ad636571f88ea2506eac/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-tyjk/052a1a3c0142ad636571f88ea2506eac/openapi.json)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| 电子行程单 | 机票报销凭证/开票诉求通常引导至此；不要按通用增值税发票产品处理 | 行程单开具：[https://open.yeepay.com/apis/docs/solutions/hlyd-tyjk/f683900ca17bd492ad987ecf64e8ace6/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-tyjk/f683900ca17bd492ad987ecf64e8ace6/openapi.json) 查询行程单开具详情：[https://open.yeepay.com/apis/docs/solutions/hlyd-tyjk/81b1b300e54447e821ad2a2c690e296e/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-tyjk/81b1b300e54447e821ad2a2c690e296e/openapi.json) 重新发送电子行程单：[https://open.yeepay.com/apis/docs/solutions/hlyd-tyjk/95a372b63ab8641f092e77acc9bf468c/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-tyjk/95a372b63ab8641f092e77acc9bf468c/openapi.json) 红冲电子行程单：[https://open.yeepay.com/apis/docs/solutions/hlyd-tyjk/7e8dae845c0913d1bff36953378df627/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-tyjk/7e8dae845c0913d1bff36953378df627/openapi.json) 查询行程单红冲详情：[https://open.yeepay.com/apis/docs/solutions/hlyd-tyjk/9e52112668804599bae71e241e4b4548/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-tyjk/9e52112668804599bae71e241e4b4548/openapi.json) |
| 南航航班异步通知      | 用于接收南航航班异步通知                      | [https://open.yeepay.com/docs-v3/solution/hlyd-tyjk/13094.md](https://open.yeepay.com/docs-v3/solution/hlyd-tyjk/13094.md)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| 客票状态查询        | 支持 ZH、CZ、MF、CDP 航司、东航 B2T 新网站查询客票 | 查询客票状态：[https://open.yeepay.com/apis/docs/solutions/hlyd-tyjk/b2f1384b8feb04d2de9a85124dc64613/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-tyjk/b2f1384b8feb04d2de9a85124dc64613/openapi.json)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| 退改规则查询        | 支持南航、厦航 B2B                       | 查询退改规则：[https://open.yeepay.com/apis/docs/solutions/hlyd-tyjk/4c0303ffb193bd5e66078909a15268aa/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-tyjk/4c0303ffb193bd5e66078909a15268aa/openapi.json)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| 行李信息查询        | 支持南航、厦航 B2B                       | 查询行李信息：[https://open.yeepay.com/apis/docs/solutions/hlyd-tyjk/9c25dc28b94e5226f1983330dc421cec/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-tyjk/9c25dc28b94e5226f1983330dc421cec/openapi.json)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |




## 政策池支持情况（`hlyd-zcc`）

- 产品介绍（适用场景，必读）：[https://open.yeepay.com/docs-v3/solution/hlyd-zcc/13099.md](https://open.yeepay.com/docs-v3/solution/hlyd-zcc/13099.md)


政策池是易宝提供的**航司政策缓存**，用于避免商户频繁直连航司查政策而受到航司侧限制。下表为当前支持情况；**具体支持渠道与调用说明以各接口 openapi.json 描述为准**。


| 政策能力 | 支持航司                               | 支持方式                                                                | 接口                                                                                                                                                                                                                |
| ---- | ---------------------------------- | ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 政策查询 | 南航 NDC、厦航 NDC、山航 NDC、深航 NDC、昆航 NDC | 1. 获取FTP全量政策+接口变价通知（最推荐） 2. 通过该接口查询全量政策+变价通知（需要商户维护全量政策的OD（OD：城市对）） | 政策池查询接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-zcc/1686c5ec96f728148f941ab2b0f2cc35/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-zcc/1686c5ec96f728148f941ab2b0f2cc35/openapi.json)  |
| 变价通知 | 南航 NDC、厦航 NDC、山航 NDC               | 变价通知                                                                | 私有政策查询接口：[https://open.yeepay.com/apis/docs/solutions/hlyd-zcc/731d7f5490a6e7b524a9f2dba421edbf/openapi.json](https://open.yeepay.com/apis/docs/solutions/hlyd-zcc/731d7f5490a6e7b524a9f2dba421edbf/openapi.json) |


