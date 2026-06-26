# -*- coding: utf-8 -*-
"""YOP URL 编码：签名 canonical 串与 HTTP 报文组装使用不同规则。

签名（canonical request / content-sha256）：
  - header、query、form 参数名/值各 urlEncode 一次
  - 空格统一为 %20（RFC3986，等同 Java urlEncodeForSign）

HTTP 报文（实际 query / form body）：
  - form 参数值经 HTTP 协议编码两次（等同 Java URLEncoder + UrlEncodedFormEntity）
  - GET query 的 value 编码两次，key 编码一次
  - 使用 HTTP 协议编码即可（空格可为 +），不必统一为 %20
"""

from urllib.parse import quote, quote_plus


def url_encode_for_sign(value: str) -> str:
    """签名用：RFC3986，空格 %20（Python quote(safe='') 默认满足）。"""
    return quote(str(value), safe="")


def url_encode_http(value: str) -> str:
    """HTTP 报文用：等同 Java URLEncoder.encode（空格为 +）。"""
    return quote_plus(str(value), safe="")


def canonical_form(params: dict) -> str:
    """签名用 canonical query/form 串：key/value 各编码一次，key 升序 & 拼接。"""
    items = sorted((k, "" if v is None else v) for k, v in params.items())
    return "&".join(
        f"{url_encode_for_sign(k)}={url_encode_for_sign(v)}" for k, v in items
    )


def http_form_body(params: dict) -> str:
    """POST application/x-www-form-urlencoded 请求体：参数值 HTTP 编码两次。"""
    items = sorted((k, "" if v is None else v) for k, v in params.items())
    pairs = []
    for k, v in items:
        once_key = url_encode_http(k)
        once_value = url_encode_http(v)
        pairs.append(f"{url_encode_http(once_key)}={url_encode_http(once_value)}")
    return "&".join(pairs)


def http_query_string(params: dict) -> str:
    """GET query 串：key HTTP 编码一次，value HTTP 编码两次。"""
    items = sorted((k, "" if v is None else v) for k, v in params.items())
    pairs = []
    for k, v in items:
        encoded_name = url_encode_http(k)
        encoded_value = url_encode_http(url_encode_http(v))
        pairs.append(f"{encoded_name}={encoded_value}")
    return "&".join(pairs)
