#!/usr/bin/env python3
"""Skill 发版守门。

检查项：
  1. 平台文档质量（H1/CSS 残留/表格断裂/截图密度）
  2. 全库过期模式黑名单（旧数据源、已删除目录的引用）
  3. md 内相对引用死链
  4. 版本一致性（SKILL.md / CHANGELOG.md / 两个 yaml）
  5. 签名/回调解密测试向量（脚本实现 + 协议文档「完整示例」一致）
  6. 排障资产（knowledge-map 结构与锚点、troubleshooting 标记与映射一致、diag 脚本清单与自测）
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = SKILL_ROOT.parent.parent
REFERENCES_ROOT = SKILL_ROOT / "references"
PLATFORM_DOC_ROOT = REFERENCES_ROOT / "平台文档"
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
DIAG_REF_DIR = REFERENCES_ROOT / "排障"
DIAG_SCRIPTS_DIR = SCRIPTS_DIR / "diag"
RSA_VECTOR_DIR = SCRIPTS_DIR / "rsa" / "tests" / "vectors"
SM_VECTOR_DIR = SCRIPTS_DIR / "sm" / "tests" / "vectors"

# 全库禁止出现的过期模式（CHANGELOG.md 作为历史记录豁免）
from common.python_version import ensure_python_version

STALE_PATTERNS = {
    "definition.json": "旧数据源，应改用 doc_md（docs-v3/api/<slug>.md）",
    "errcode.json": "旧数据源，错误码在 doc_md「错误码」章节",
    "apis/docs/apis": "旧数据源 URL，应改用 doc_md",
    "search.maven.org/solrsearch": "已弃用索引，查 yop-java-sdk 版本请用 central.sonatype.com（见 SDK使用说明.md 版本解析协议）",
    "示例代码/后端代码": "目录已迁移至 平台文档/平台规范/安全认证/",
    "references/示例代码": "目录已删除，前端示例在产品场景 md，后端协议在 安全认证/",
}


def _strip_fenced_code(text: str) -> str:
    """移除 fenced 代码块，避免样例中的 # 注释被误判为一级标题。"""
    return re.sub(r"```[\s\S]*?```", "", text)


def check_file(path: Path) -> list[str]:
    issues: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    rel = path.relative_to(PLATFORM_DOC_ROOT)

    if len(text.strip()) == 0:
        issues.append(f"{rel}: 空文件")
        return issues

    prose = _strip_fenced_code(text)
    h1 = re.findall(r"^# [^\n]+", prose, re.M)
    if len(h1) != 1:
        issues.append(f"{rel}: 一级标题数量={len(h1)}（期望 1）")

    if "--un-" in text or "<style" in text or '<div class="' in text:
        issues.append(f"{rel}: 含 HTML/CSS 残留")

    if "Syntax error in textmermaid" in text:
        issues.append(f"{rel}: mermaid 损坏占位未修复")

    if re.search(r'^\d+\.png["\']?\s*$', text, re.M):
        issues.append(f"{rel}: 含孤立图片占位文本")

    # 表格行断裂：以 | 开头但上一行非表格且非表头分隔
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("|") and i > 0:
            prev = lines[i - 1].strip()
            if prev and not prev.startswith("|") and not prev.startswith(">"):
                if not re.match(r"^#{1,6}\s", prev):
                    issues.append(f"{rel}:{i+1}: 疑似表格行断裂（前行非表格）")
                    break

    img_count = len(re.findall(r"!\[[^\]]*\]\([^)]+\)", text))
    if img_count > 3:
        issues.append(f"{rel}: 截图引用 {img_count} 处（建议 ≤3，以文字步骤为主）")

    return issues


def _md_display_path(md: Path) -> str:
    try:
        return str(md.relative_to(SKILL_ROOT))
    except ValueError:
        return str(md.relative_to(REPO_ROOT))


def _all_md_files() -> list[Path]:
    files = [
        SKILL_ROOT / "SKILL.md",
        REPO_ROOT / "README.md",
        REPO_ROOT / "CHANGELOG.md",
    ]
    skill_readme = SKILL_ROOT / "README.md"
    if skill_readme.exists():
        files.append(skill_readme)
    files += sorted(REFERENCES_ROOT.rglob("*.md"))
    return [f for f in files if f.exists()]


def check_stale_patterns() -> list[str]:
    issues: list[str] = []
    for md in _all_md_files():
        if md.name == "CHANGELOG.md":
            continue
        text = md.read_text(encoding="utf-8", errors="replace")
        rel = _md_display_path(md)
        for pattern, hint in STALE_PATTERNS.items():
            if pattern in text:
                issues.append(f"{rel}: 含过期模式「{pattern}」（{hint}）")
    return issues


def check_dead_links() -> list[str]:
    """检查 md 中以反引号/链接形式引用的 .md 相对路径是否存在。"""
    issues: list[str] = []
    ref_pattern = re.compile(r"`([^`\s]+\.md)`|\]\(([^)\s]+\.md)\)")
    for md in _all_md_files():
        text = _strip_fenced_code(md.read_text(encoding="utf-8", errors="replace"))
        rel = _md_display_path(md)
        for match in ref_pattern.finditer(text):
            target = match.group(1) or match.group(2)
            if target.startswith("http"):
                continue
            if "<" in target or ">" in target:  # 模板占位路径，如 <域>/<场景>.md
                continue
            if "/" in target:
                bases = (md.parent, REFERENCES_ROOT, PLATFORM_DOC_ROOT, SKILL_ROOT, REPO_ROOT)
                if not any((base / target).exists() for base in bases):
                    issues.append(f"{rel}: 引用不存在的文件 `{target}`")
            else:
                # 裸文件名：同名文件需在 skill 内任意位置存在
                if not (list(SKILL_ROOT.glob(target)) or list(SKILL_ROOT.rglob(target))):
                    issues.append(f"{rel}: 引用不存在的文件 `{target}`")
    return issues


def check_version_consistency() -> list[str]:
    issues: list[str] = []
    versions: dict[str, str | None] = {}

    skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    m = re.search(r"^version:\s*([\d.]+)\s*$", skill_text, re.M)
    versions["SKILL.md"] = m.group(1) if m else None

    for name, path in {
        "api-index.yaml": REFERENCES_ROOT / "产品能力" / "api-index.yaml",
        "platform-doc-manifest.yaml": PLATFORM_DOC_ROOT / "platform-doc-manifest.yaml",
    }.items():
        m = re.search(r'^version:\s*"([\d.]+)"\s*$', path.read_text(encoding="utf-8"), re.M)
        versions[name] = m.group(1) if m else None

    changelog = REPO_ROOT / "CHANGELOG.md"
    m = re.search(r"^## ([\d.]+) - ", changelog.read_text(encoding="utf-8"), re.M)
    versions["CHANGELOG.md 首条"] = m.group(1) if m else None

    expected = versions["SKILL.md"]
    if not expected:
        return ["SKILL.md: 未找到 frontmatter version"]
    for name, ver in versions.items():
        if ver != expected:
            issues.append(f"版本不一致：{name}={ver}，期望与 SKILL.md 一致（{expected}）")
    return issues


def _heading_anchor(heading: str) -> str:
    """markdown 标题 → GitHub 风格锚点（保留中英文，去标点，空格转连字符）。"""
    text = heading.lstrip("#").strip().lower()
    text = re.sub(r"[^\w\u4e00-\u9fff\- ]", "", text)
    return text.replace(" ", "-")


def _parse_knowledge_map(text: str) -> tuple[str | None, list[dict[str, str]]]:
    """极简解析：本文件结构固定（version + entries 列表），不引入 PyYAML 依赖。"""
    version = None
    m = re.search(r"^version:\s*(\S+)\s*$", text, re.M)
    if m:
        version = m.group(1)
    entries: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for raw in text.splitlines():
        if raw.lstrip().startswith("#"):
            continue
        # 只剥行尾注释：# 前须有空白且不在引号内（localAnchor 的锚点自带 #，不能被切掉）
        line = re.sub(r'\s+#(?=(?:[^"]*"[^"]*")*[^"]*$).*$', "", raw).rstrip()
        if not line.strip():
            continue
        m = re.match(r"^\s*-\s+(\w+):\s*(.+)$", line)
        if m:
            if current:
                entries.append(current)
            current = {m.group(1): m.group(2).strip().strip('"')}
            continue
        m = re.match(r"^\s+(\w+):\s*(.+)$", line)
        if m and current:
            current[m.group(1)] = m.group(2).strip().strip('"')
    if current:
        entries.append(current)
    return version, entries


def check_diagnostic_assets() -> list[str]:
    """排障资产：knowledge-map 结构与锚点、troubleshooting 标记与映射一致、diag 脚本清单。"""
    issues: list[str] = []
    km = DIAG_REF_DIR / "knowledge-map.yaml"
    if not km.exists():
        return [f"缺少 {km.relative_to(SKILL_ROOT)}"]

    for name in ("diagnostic-protocol.md", "offline-l1.md"):
        if not (DIAG_REF_DIR / name).exists():
            issues.append(f"缺少 references/排障/{name}")

    version, entries = _parse_knowledge_map(km.read_text(encoding="utf-8"))
    if not version:
        issues.append("knowledge-map.yaml: 缺少 version")
    if not entries:
        issues.append("knowledge-map.yaml: 无 entries")

    # knowledgeId 是可选的：公开知识目录里查不到对应条目时留空，好过自造一个标识。
    required = ("localAnchor", "evidenceRequired", "slots")
    mapped: dict[str, str] = {}
    for i, entry in enumerate(entries, 1):
        missing = [k for k in required if k not in entry]
        if missing:
            issues.append(f"knowledge-map.yaml: 第 {i} 条缺少字段 {missing}")
            continue
        if entry["evidenceRequired"] not in ("true", "false"):
            issues.append(
                f"knowledge-map.yaml: {entry['localAnchor']} 的 evidenceRequired 须为 true/false"
            )
        kid = entry.get("knowledgeId")
        if kid:
            # 形状固定为 kn-<来源>-<hash>；挡住再写回 kb.* 这类自造标识
            if not re.match(r"^kn-[a-z0-9-]+$", kid):
                issues.append(
                    f"knowledge-map.yaml: knowledgeId `{kid}` 不是服务端形状（kn-…），"
                    "查不到对应条目时应留空而不是自造"
                )
            mapped[kid] = entry["evidenceRequired"]

        target, _, anchor = entry["localAnchor"].partition("#")
        path = SKILL_ROOT / target
        if not path.exists():
            issues.append(f"knowledge-map.yaml: localAnchor 指向不存在的文件 `{target}`")
            continue
        if anchor:
            headings = re.findall(r"^#{1,6} .+$", path.read_text(encoding="utf-8"), re.M)
            if anchor not in {_heading_anchor(h) for h in headings}:
                issues.append(f"knowledge-map.yaml: `{target}` 中找不到锚点 `#{anchor}`")

    # troubleshooting.md 中的标记必须登记在 map 里且 evidenceRequired 一致
    ts_text = (REFERENCES_ROOT / "troubleshooting.md").read_text(encoding="utf-8")
    for kid, ev in re.findall(
        r"`knowledgeId:\s*([\w.-]+)`\s*·\s*`evidenceRequired:\s*(true|false)`", ts_text
    ):
        if kid not in mapped:
            issues.append(f"troubleshooting.md: 标记 {kid} 未登记在 knowledge-map.yaml")
        elif mapped[kid] != ev:
            issues.append(
                f"troubleshooting.md: {kid} 的 evidenceRequired={ev}，与 knowledge-map.yaml（{mapped[kid]}）不一致"
            )

    # scripts/diag 存在时（P1 起）：README 与脚本清单一致，且自测通过
    if DIAG_SCRIPTS_DIR.exists():
        readme = DIAG_SCRIPTS_DIR / "README.md"
        if not readme.exists():
            issues.append("scripts/diag/: 缺少 README.md")
        else:
            listed = readme.read_text(encoding="utf-8")
            for script in sorted(DIAG_SCRIPTS_DIR.glob("*.py")):
                if script.name.startswith("_"):
                    continue
                if script.name not in listed:
                    issues.append(f"scripts/diag/README.md: 未收录 {script.name}")
        selftest = DIAG_SCRIPTS_DIR / "tests" / "test_redact.py"
        if not selftest.exists():
            issues.append("scripts/diag/tests/test_redact.py 缺失")
        else:
            proc = subprocess.run(
                [sys.executable, str(selftest)], capture_output=True, text=True,
            )
            if proc.returncode != 0:
                issues.append(f"diag 自测失败：{(proc.stdout or proc.stderr).strip()}")
    return issues


def check_vectors() -> list[str]:
    """脚本实现与向量一致 + 协议文档「完整示例」与向量一致。"""
    issues: list[str] = []
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "tools" / "verify_vectors.py")],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        issues.append(f"测试向量校验失败：{(proc.stderr or proc.stdout).strip()}")
        return issues

    auth_dir = PLATFORM_DOC_ROOT / "平台规范" / "安全认证"
    sign_doc = (auth_dir / "请求签名协议.md").read_text(encoding="utf-8")
    sign_vectors = json.loads((RSA_VECTOR_DIR / "sign_vectors.json").read_text(encoding="utf-8"))
    for case in sign_vectors["cases"]:
        expected = case["expected"]
        if expected["content_sha256"] not in sign_doc:
            issues.append(f"请求签名协议.md: 缺少向量 [{case['name']}] 的 content_sha256")
    # 文档逐行展示前两个用例的 Authorization；第 3 个用例指向 JSON 文件
    for case in sign_vectors["cases"][:2]:
        if case["expected"]["authorization"] not in sign_doc:
            issues.append(f"请求签名协议.md: 缺少/不匹配向量 [{case['name']}] 的 Authorization")

    notify_doc = (auth_dir / "回调解密协议.md").read_text(encoding="utf-8")
    notify_vector = json.loads((RSA_VECTOR_DIR / "notify_vector.json").read_text(encoding="utf-8"))
    if notify_vector["ciphertext"] not in notify_doc:
        issues.append("回调解密协议.md: 完整示例密文与 notify_vector.json 不一致")
    if notify_vector["plaintext"] not in notify_doc:
        issues.append("回调解密协议.md: 完整示例明文与 notify_vector.json 不一致")
    return issues


def run_notify_roundtrip() -> list[str]:
    issues: list[str] = []
    gen = SCRIPTS_DIR / "rsa" / "gen_keypair.py"
    mock = SCRIPTS_DIR / "rsa" / "mock_notify.py"
    decrypt = SCRIPTS_DIR / "rsa" / "decrypt_notify.py"
    if not all(p.exists() for p in (gen, mock, decrypt)):
        return issues

    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        yop_dir = Path(tmp) / "yop"
        merchant_dir = Path(tmp) / "merchant"
        for out_dir in (yop_dir, merchant_dir):
            subprocess.run(
                [sys.executable, str(gen), "--out", str(out_dir)],
                check=True,
                capture_output=True,
            )
        yop_priv = yop_dir / "rsa_private_pkcs8.pem"
        yop_pub = yop_dir / "rsa_public.pem"
        merchant_priv = merchant_dir / "rsa_private_pkcs8.pem"
        merchant_pub = merchant_dir / "rsa_public.pem"
        proc = subprocess.run(
            [
                sys.executable,
                str(mock),
                "--mode",
                "real",
                "--dry-run",
                "--url",
                "http://127.0.0.1:8080/notify",
                "--yop-key",
                str(yop_priv),
                "--merchant-pubkey",
                str(merchant_pub),
                "--data",
                '{"status":"SUCCESS","orderId":"VALIDATE"}',
            ],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            issues.append(f"mock_notify 失败: {proc.stderr.strip()}")
            return issues
        cipher = proc.stdout.strip().splitlines()[-1]
        proc2 = subprocess.run(
            [
                sys.executable,
                str(decrypt),
                "--cipher",
                cipher,
                "--merchant-key",
                str(merchant_priv),
                "--yop-pubkey",
                str(yop_pub),
            ],
            capture_output=True,
            text=True,
        )
        if proc2.returncode != 0 or "验签通过" not in proc2.stdout:
            issues.append(f"decrypt_notify 互打失败: {proc2.stderr or proc2.stdout}")
    return issues


def run_notify_sm_roundtrip() -> list[str]:
    issues: list[str] = []
    gen = SCRIPTS_DIR / "sm" / "gen_keypair.py"
    mock = SCRIPTS_DIR / "sm" / "mock_notify.py"
    decrypt = SCRIPTS_DIR / "sm" / "decrypt_notify.py"
    if not all(p.exists() for p in (gen, mock, decrypt)):
        return issues

    import json
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        yop_dir = Path(tmp) / "yop"
        merchant_dir = Path(tmp) / "merchant"
        for out_dir in (yop_dir, merchant_dir):
            subprocess.run(
                [sys.executable, str(gen), "--out", str(out_dir)],
                check=True,
                capture_output=True,
            )
        yop_priv = yop_dir / "sm2_private_pkcs8.pem"
        yop_pub = yop_dir / "sm2_public.pem"
        merchant_priv = merchant_dir / "sm2_private_pkcs8.pem"
        merchant_pub = merchant_dir / "sm2_public.pem"
        proc = subprocess.run(
            [
                sys.executable,
                str(mock),
                "--mode",
                "real",
                "--dry-run",
                "--url",
                "http://127.0.0.1:8080/notify",
                "--yop-key",
                str(yop_priv),
                "--merchant-pubkey",
                str(merchant_pub),
                "--data",
                '{"status":"SUCCESS","orderId":"VALIDATE_SM"}',
            ],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            issues.append(f"mock_notify (SM) 失败: {proc.stderr.strip()}")
            return issues
        lines = proc.stdout.strip().splitlines()
        body = lines[-1]
        headers = {}
        for line in lines:
            if ": " in line and not line.startswith("=="):
                name, value = line.split(": ", 1)
                headers[name] = value
        headers_path = Path(tmp) / "headers.json"
        headers_path.write_text(json.dumps(headers, ensure_ascii=False), encoding="utf-8")
        proc2 = subprocess.run(
            [
                sys.executable,
                str(decrypt),
                "--headers-file",
                str(headers_path),
                "--body",
                body,
                "--merchant-key",
                str(merchant_priv),
                "--yop-pubkey",
                str(yop_pub),
            ],
            capture_output=True,
            text=True,
        )
        if proc2.returncode != 0 or "验签通过" not in proc2.stdout:
            issues.append(f"decrypt_notify (SM) 互打失败: {proc2.stderr or proc2.stdout}")
    return issues


def main() -> int:
    ensure_python_version()
    parser = argparse.ArgumentParser(description="Skill 发版守门")
    parser.add_argument("--with-notify-test", action="store_true", help="执行 mock/decrypt 互打")
    args = parser.parse_args()

    all_issues: list[str] = []
    for md in sorted(PLATFORM_DOC_ROOT.rglob("*.md")):
        all_issues.extend(check_file(md))
    all_issues.extend(check_stale_patterns())
    all_issues.extend(check_dead_links())
    all_issues.extend(check_version_consistency())
    all_issues.extend(check_diagnostic_assets())
    all_issues.extend(check_vectors())

    if args.with_notify_test:
        all_issues.extend(run_notify_roundtrip())
        all_issues.extend(run_notify_sm_roundtrip())

    if all_issues:
        print("发版守门未通过：")
        for item in all_issues:
            print(f"  - {item}")
        return 1

    count = len(_all_md_files())
    print(f"发版守门通过（共检查 {count} 个 md 文件 + 版本一致性 + 排障资产 + 测试向量）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
