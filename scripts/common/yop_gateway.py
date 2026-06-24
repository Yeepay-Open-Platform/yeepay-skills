# -*- coding: utf-8 -*-
"""YOP 网关根地址（生产 / 沙箱）。"""

PROD_OPENAPI = "https://openapi.yeepay.com/yop-center"
PROD_YOS = "https://yos.yeepay.com/yop-center"
SANDBOX = "https://sandbox.yeepay.com/yop-center"

# 历史别名（生产 openapi）
DEFAULT_OPENAPI = PROD_OPENAPI
DEFAULT_YOS = PROD_YOS
DEFAULT_SANDBOX = SANDBOX


def resolve_gateway(*, sandbox: bool = False, yos: bool = False) -> str:
    """解析出站网关根地址。

    - **沙箱**：无独立 yos 域，交易 / 上传 / 下载均走 ``SANDBOX``
    - **生产**：交易类走 openapi；**文件上传与下载**均走 yos
    """
    if sandbox:
        return SANDBOX
    if yos:
        return PROD_YOS
    return PROD_OPENAPI
