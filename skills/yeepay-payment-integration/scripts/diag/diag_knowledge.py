#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查询 yop-agent 公开知识库（匿名，不需要诊断凭证）。

用途：本地 references/ 没有对应条目，或用户根本没有诊断凭证时，仍能拿到
平台侧维护的文档知识来辅助排查。

两条纪律：

1. **这里拿到的一律是 L1**。知识条目来自平台文档，不是该商户的实时数据，
   呈现时必须标注「未查询实时数据，不能作为生产根因」——与离线 L1 同级。
2. **检索在本地做**。服务端只提供「列全部摘要」和「按 id 取详情」两个接口，
   没有搜索端点；本脚本拉回摘要后在本机按关键词过滤，所以**用户的问题描述
   不会外发**。这点在没有凭证、未签任何数据出境约定时尤其重要。

用法：
    python diag/diag_knowledge.py search "回调 未收到" [--limit 10]
    python diag/diag_knowledge.py list [--limit 20]
    python diag/diag_knowledge.py get kn-docs-xxxxxxxx
    python diag/diag_knowledge.py verify-map      # 核对本地 knowledge-map.yaml 的 knowledgeId
"""

import argparse
import json
import re
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from diag._bootstrap import normalize_env, run  # noqa: E402
from diag import transport  # noqa: E402
from diag.errors import EXIT_BAD_RESPONSE, EXIT_LOCAL_INVALID, DiagError  # noqa: E402

LAYER_NOTE = "来源：yop-agent 公开知识库（平台文档派生）。属 L1，未查询该商户实时数据，不能作为生产根因。"


def _fetch_summaries(base_url: str) -> list:
    data = transport.request("GET", base_url, "/v1/knowledge/summaries")
    if not isinstance(data, list):
        raise DiagError(EXIT_BAD_RESPONSE, "知识摘要响应不是数组")
    return [x for x in data if isinstance(x, dict) and x.get("id")]


def _score(summary: str, terms: list[str]) -> int:
    text = summary.lower()
    return sum(1 for term in terms if term in text)


def _verify_map(base_url: str) -> int:
    """核对 knowledge-map.yaml 里的 knowledgeId 是否真在服务端公开目录里。

    协议禁止伪造 knowledgeId；公开目录里没有的条目必须留空。
    """
    km = Path(__file__).resolve().parents[2] / "references" / "排障" / "knowledge-map.yaml"
    if not km.is_file():
        raise DiagError(EXIT_LOCAL_INVALID, f"找不到 knowledge-map.yaml：{km}")
    local = re.findall(r'^\s*knowledgeId:\s*"?([^"\s#]+)"?', km.read_text(encoding="utf-8"), re.M)
    remote = {e["id"] for e in _fetch_summaries(base_url)}

    missing = [k for k in local if k not in remote]
    transport.emit({
        "note": "核对本地 knowledge-map.yaml 与服务端公开知识目录",
        "localIds": local,
        "remoteTotal": len(remote),
        "missing": missing,
    })
    if missing:
        transport.warn(
            f"knowledge_map=stale：{len(missing)} 个 knowledgeId 在服务端公开目录中不存在，"
            "须改成真实条目或留空，不得保留自造标识"
        )
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="查询 yop-agent 公开知识库（匿名）")
    parser.add_argument("action", choices=("search", "list", "get", "verify-map"))
    parser.add_argument("query", nargs="?", help="search 的关键词（空格分隔，本地匹配）／get 的 knowledgeId")
    parser.add_argument("--limit", type=int, default=10, help="search / list 返回条数上限")
    parser.add_argument("--env", default="SANDBOX", help="SANDBOX / PRODUCT")
    parser.add_argument("--base-url", help="覆盖 yop-agent 地址")
    args = parser.parse_args()

    base_url = transport.resolve_base_url(normalize_env(args.env), args.base_url)

    if args.action == "verify-map":
        return _verify_map(base_url)

    if args.action == "get":
        if not args.query:
            raise DiagError(EXIT_LOCAL_INVALID, "get 缺少 knowledgeId")
        data = transport.request("GET", base_url, f"/v1/knowledge/{args.query}")
        transport.emit({"note": LAYER_NOTE, "data": data})
        return 0

    entries = _fetch_summaries(base_url)

    if args.action == "list":
        transport.emit({"note": LAYER_NOTE, "total": len(entries),
                        "data": entries[: max(args.limit, 0)]})
        return 0

    if not args.query:
        raise DiagError(EXIT_LOCAL_INVALID, "search 缺少关键词")
    terms = [t.lower() for t in args.query.split() if t]
    scored = [(_score(str(e.get("summary") or ""), terms), e) for e in entries]
    hits = sorted([p for p in scored if p[0] > 0], key=lambda p: -p[0])[: max(args.limit, 0)]
    transport.warn(f"knowledge_search=local：在本地对 {len(entries)} 条摘要匹配，关键词未外发")
    transport.emit({
        "note": LAYER_NOTE,
        "query": args.query,
        "scanned": len(entries),
        "matched": len(hits),
        "data": [dict(e, matchedTerms=score) for score, e in hits],
    })
    if not hits:
        transport.warn("knowledge_search=empty：公开知识库无匹配条目，不要拿不相关条目凑答案")
    return 0


if __name__ == "__main__":
    sys.exit(run(main))
