# -*- coding: utf-8 -*-
"""对 appKey 原文签名，用于兑换 / 吊销诊断 token。

算法按**本地密钥类型**自动选择，用户不需要声明：

    RSA  -> SHA256withRSA（兼容 SHA1withRSA），签名值后缀 $SHA256 / $SHA1
    SM2  -> SM3withSM2，签名值后缀 $SM3

服务端按 appKey 在库中的密钥数据识别类型并验签。签名值编码沿用 yop-center
风格（URL-safe Base64 + 摘要后缀），与 scripts/rsa、scripts/sm 一致；
可用 --sig-encoding / --no-digest-suffix 切换。

私钥只经文件路径读取，绝不接受粘贴的 PEM 内容——见 diagnostic-protocol.md 第三节。
"""

from __future__ import annotations

import base64
from pathlib import Path

from .errors import EXIT_KEY_OR_SIGN, EXIT_LOCAL_INVALID, DiagError

RSA = "RSA"
SM2 = "SM2"

_PEM_MARK = "-----BEGIN"


def _b64(raw: bytes, encoding: str) -> str:
    if encoding == "standard":
        return base64.b64encode(raw).decode("ascii")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _strip_jsonc(text: str) -> str:
    """去掉 // 与 /* */ 注释。

    真实的 yop_sdk_config 常带注释（各环境 server_root 注释着放），标准 json
    解析不了。必须按字符串字面量扫描——粗暴替换 "//" 会把 https:// 打断。
    """
    out: list[str] = []
    i, n = 0, len(text)
    in_string = False
    escaped = False
    while i < n:
        ch = text[i]
        if in_string:
            out.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            i += 1
            continue
        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue
        if ch == "/" and i + 1 < n:
            nxt = text[i + 1]
            if nxt == "/":
                while i < n and text[i] != "\n":
                    i += 1
                continue
            if nxt == "*":
                i += 2
                while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                    i += 1
                i += 2
                continue
        out.append(ch)
        i += 1
    return "".join(out)


def _extract_from_sdk_config(text: str, app_key: str | None) -> tuple[str, str | None] | None:
    """从 yop_sdk_config*.json 里取商户私钥。

    商户手上通常只有这个文件，没有单独的 PEM——让他们再导一次容易出错，
    不如直接读。格式见 references/平台文档/开始对接/SDK使用说明.md 第三节。
    """
    import json

    try:
        config = json.loads(_strip_jsonc(text))
    except (json.JSONDecodeError, ValueError):
        return None
    if not isinstance(config, dict):
        return None

    entries = config.get("isv_private_key")
    if isinstance(entries, dict):
        entries = [entries]
    if not isinstance(entries, list):
        return None

    candidates = [e for e in entries if isinstance(e, dict) and e.get("value")]
    if not candidates:
        return None
    if app_key:
        matched = [e for e in candidates if e.get("app_key") in (None, app_key)]
        if matched:
            candidates = matched
    if len(candidates) > 1:
        raise DiagError(
            EXIT_LOCAL_INVALID,
            "配置文件中有多个 isv_private_key，且无法按 appKey 唯一确定；请改为直接提供该应用的私钥文件路径",
        )
    entry = candidates[0]
    store_type = str(entry.get("store_type") or "").upper()
    if store_type and store_type not in ("STRING", "FILE_P8", "PEM"):
        raise DiagError(
            EXIT_KEY_OR_SIGN,
            f"配置中的私钥 store_type={store_type}（如 PKCS12/CFCA 证书）暂不支持直接读取，"
            "请导出 PEM 私钥后用 --private-key 指定",
        )
    # cert_type 是配置里最可靠的类型来源：value 常是无 PEM 头的裸 base64，
    # 光看内容分不清 RSA 与 SM2（长度也不能当判据）。
    cert_type = str(entry.get("cert_type") or "").upper() or None
    return str(entry["value"]), cert_type


def read_app_key_from_config(path_arg: str) -> str | None:
    """从 yop_sdk_config 里读 app_key，省掉用户重复输入。"""
    import json

    path = Path(path_arg).expanduser()
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None
    if path.suffix.lower() != ".json" and not text.lstrip().startswith("{"):
        return None
    try:
        config = json.loads(_strip_jsonc(text))
    except (json.JSONDecodeError, ValueError):
        return None
    value = config.get("app_key") if isinstance(config, dict) else None
    return str(value) if value else None


def read_key_file(path_arg: str, app_key: str | None = None) -> tuple[Path, str, str | None]:
    """只接受文件路径：PEM 私钥文件，或 yop_sdk_config*.json。

    返回 (路径, 私钥文本, 类型提示)。类型提示来自配置的 cert_type，PEM 文件为 None。
    传入疑似 PEM 内容时明确拒绝，而不是当路径去 open。
    """
    if _PEM_MARK in path_arg or "\n" in path_arg:
        raise DiagError(
            EXIT_LOCAL_INVALID,
            "检测到私钥内容而不是文件路径：请改为提供私钥文件路径（内容已在本地丢弃，未外发）",
        )
    path = Path(path_arg).expanduser()
    if not path.is_file():
        raise DiagError(EXIT_KEY_OR_SIGN, f"私钥文件不存在：{path}")
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise DiagError(
            EXIT_KEY_OR_SIGN,
            f"{path} 不是文本格式的私钥；CFCA/PKCS#12 证书请先导出 PEM 私钥后再使用",
        )
    if path.suffix.lower() == ".json" or text.lstrip().startswith("{"):
        extracted = _extract_from_sdk_config(text, app_key)
        if extracted is None:
            raise DiagError(
                EXIT_KEY_OR_SIGN,
                f"{path} 看起来是 JSON 但没找到 isv_private_key.value；请确认是 yop_sdk_config 文件",
            )
        value, cert_type = extracted
        return path, value, cert_type
    return path, text, None


def detect_key_type(pem_text: str, hint: str | None = None) -> str:
    """判断密钥类型：优先用外部提示（配置的 cert_type），否则按内容推断。"""
    from cryptography.hazmat.primitives import serialization

    if hint:
        upper = hint.upper()
        if "SM" in upper:
            return SM2
        if "RSA" in upper:
            return RSA

    text = pem_text.strip()
    if _PEM_MARK not in text:
        # 裸 Base64 且无类型提示：试着按 PKCS8 DER 解析算法 OID，认不出再当 RSA
        try:
            import base64 as _b64

            key = serialization.load_der_private_key(_b64.b64decode(text), password=None)
            return SM2 if "EllipticCurve" in type(key).__name__ else RSA
        except Exception:
            return RSA
    try:
        key = serialization.load_pem_private_key(text.encode("utf-8"), password=None)
    except Exception:
        # cryptography 不认的多为 SM2（SM2P256V1 曲线），交给 gmssl 解析
        return SM2
    name = type(key).__name__
    if "RSA" in name:
        return RSA
    if "EllipticCurve" in name:
        curve = getattr(getattr(key, "curve", None), "name", "")
        if "sm2" in curve.lower() or curve == "":
            return SM2
        raise DiagError(EXIT_KEY_OR_SIGN, f"不支持的椭圆曲线密钥：{curve}")
    raise DiagError(EXIT_KEY_OR_SIGN, f"无法识别的密钥类型：{name}")


def sign_app_key(app_key: str, pem_text: str, *, encoding: str = "urlsafe",
                 digest_suffix: bool = True, hint: str | None = None) -> tuple[str, str]:
    """返回 (signature, key_type)。签名原文就是 appKey 字符串本身。"""
    key_type = detect_key_type(pem_text, hint)
    message = app_key.encode("utf-8")

    if key_type == RSA:
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding

        text = pem_text.strip()
        if _PEM_MARK not in text:
            text = (
                "-----BEGIN PRIVATE KEY-----\n"
                + "\n".join(text[i : i + 64] for i in range(0, len(text), 64))
                + "\n-----END PRIVATE KEY-----\n"
            )
        try:
            key = serialization.load_pem_private_key(text.encode("utf-8"), password=None)
        except Exception as exc:  # 口令保护的私钥也走这里
            raise DiagError(EXIT_KEY_OR_SIGN, f"私钥解析失败：{exc}")
        raw = key.sign(message, padding.PKCS1v15(), hashes.SHA256())
        signature = _b64(raw, encoding)
        return (signature + "$SHA256" if digest_suffix else signature), key_type

    # SM2：复用 scripts/sm 的实现（gmssl，SM2P256V1 + SM3），产出纯 R||S
    try:
        from sm.crypto import load_sm2_private, sign_sm3
    except ImportError as exc:
        raise DiagError(EXIT_KEY_OR_SIGN, f"SM2 依赖缺失（pip install gmssl）：{exc}")
    sm2_text = pem_text.strip()
    if _PEM_MARK not in sm2_text:
        # load_sm2_private 只吃 PKCS8 PEM；配置里的是裸 base64，补上头尾
        sm2_text = (
            "-----BEGIN PRIVATE KEY-----\n"
            + "\n".join(sm2_text[i : i + 64] for i in range(0, len(sm2_text), 64))
            + "\n-----END PRIVATE KEY-----\n"
        )
    try:
        private_hex = load_sm2_private(sm2_text)
        signed = sign_sm3(message, private_hex)  # 形如 <urlsafe-b64>$SM3
    except DiagError:
        raise
    except Exception as exc:
        raise DiagError(EXIT_KEY_OR_SIGN, f"SM2 签名失败：{exc}")
    value, _, _ = signed.partition("$")
    if encoding == "standard":
        pad = "=" * (-len(value) % 4)
        value = base64.b64encode(base64.urlsafe_b64decode(value + pad)).decode("ascii")
    return (value + "$SM3" if digest_suffix else value), key_type
