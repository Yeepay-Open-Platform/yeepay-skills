"""YOP 出站请求标准头（不参与 Authorization 签名）。

网关据 x-yop-sdk-version 选择响应报文格式；>= 4.3.0 返回新格式（含 x-yop-sign、x-yop-sign-serial-no 等）。
"""

from __future__ import annotations

import platform
import uuid

# 固定协议版本；>= 4.3.0 时网关按新响应格式返回
YOP_SDK_VERSION = "4.0.0"
YOP_SDK_LANGS = "python"
# 进程启动时生成一次，与 Java SDK YopConstants.YOP_SESSION_ID 一致
YOP_SESSION_ID = str(uuid.uuid4())


def build_standard_headers() -> dict[str, str]:
    """构造每次请求应附带的 SDK 元信息头（勿加入 canonical signed headers）。"""
    return {
        "x-yop-sdk-version": YOP_SDK_VERSION,
        "x-yop-sdk-langs": YOP_SDK_LANGS,
        "x-yop-session-id": YOP_SESSION_ID,
        "User-Agent": _user_agent(),
    }


def _user_agent() -> str:
    # {lang}/{python版本}/{os}/{os_release}/；SDK 版本仅走 x-yop-sdk-version 头
    py_ver = platform.python_version()
    return f"python/{py_ver}/{platform.system()}/{platform.release()}/"
