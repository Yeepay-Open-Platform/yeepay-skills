#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查询 yop-java-sdk 在 Maven Central 的最新稳定版。

优先 central.sonatype.com Solr API（须 sort=v desc）；
失败时回退 repo1.maven.org maven-metadata.xml。

在 scripts/ 目录下执行：
    python tools/resolve_java_sdk_version.py
    python tools/resolve_java_sdk_version.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from common.python_version import ensure_python_version  # noqa: E402

GROUP_ID = "com.yeepay.yop.sdk"
ARTIFACT_ID = "yop-java-sdk"
CENTRAL_SOLR_URL = (
    "https://central.sonatype.com/solrsearch/select"
    f"?q=g:{GROUP_ID}+AND+a:{ARTIFACT_ID}&rows=1&wt=json&sort=v+desc"
)
METADATA_URL = (
    "https://repo1.maven.org/maven2/com/yeepay/yop/sdk/yop-java-sdk/maven-metadata.xml"
)
USER_AGENT = "yeepay-payment-integration/resolve_java_sdk_version"


def _fetch_text(url: str, timeout: float = 15.0) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8")


def resolve_from_central_solr() -> str | None:
    data = json.loads(_fetch_text(CENTRAL_SOLR_URL))
    docs = data.get("response", {}).get("docs", [])
    if not docs:
        return None
    doc = docs[0]
    version = doc.get("v") or doc.get("latestVersion")
    return str(version).strip() if version else None


def resolve_from_metadata() -> str | None:
    root = ET.fromstring(_fetch_text(METADATA_URL))
    for tag in ("release", "latest"):
        node = root.find(f"./versioning/{tag}")
        if node is not None and node.text:
            return node.text.strip()
    return None


def resolve_latest_java_sdk_version() -> str:
    errors: list[str] = []
    for name, resolver in (
        ("central.sonatype.com", resolve_from_central_solr),
        ("maven-metadata.xml", resolve_from_metadata),
    ):
        try:
            version = resolver()
            if version:
                return version
            errors.append(f"{name}: 未返回版本")
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ET.ParseError) as exc:
            errors.append(f"{name}: {exc}")
    raise RuntimeError("无法解析 yop-java-sdk 最新版本 — " + "; ".join(errors))


def main() -> int:
    ensure_python_version()
    parser = argparse.ArgumentParser(
        description="查询 yop-java-sdk 在 Maven Central 的最新稳定版",
    )
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()

    version = resolve_latest_java_sdk_version()
    if args.json:
        payload = {
            "groupId": GROUP_ID,
            "artifactId": ARTIFACT_ID,
            "version": version,
            "source": "central.sonatype.com",
        }
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print(version)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc
