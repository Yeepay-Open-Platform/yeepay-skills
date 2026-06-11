#!/usr/bin/env python3
"""平台文档质量守门：检查 references/平台文档/ 下的 markdown 文件。"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
PLATFORM_DOC_ROOT = SKILL_ROOT / "references" / "平台文档"
SCRIPTS_DIR = Path(__file__).resolve().parent


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


def run_notify_roundtrip() -> list[str]:
    issues: list[str] = []
    gen = SCRIPTS_DIR / "gen_keypair.py"
    mock = SCRIPTS_DIR / "mock_notify.py"
    decrypt = SCRIPTS_DIR / "decrypt_notify.py"
    if not all(p.exists() for p in (gen, mock, decrypt)):
        return issues

    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        key_dir = Path(tmp) / "keys"
        subprocess.run(
            [sys.executable, str(gen), "--alg", "rsa", "--out", str(key_dir)],
            check=True,
            capture_output=True,
        )
        priv = key_dir / "rsa_private_pkcs8.pem"
        pub = key_dir / "rsa_public.pem"
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
                str(priv),
                "--merchant-pubkey",
                str(pub),
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
                str(priv),
                "--yop-pubkey",
                str(pub),
            ],
            capture_output=True,
            text=True,
        )
        if proc2.returncode != 0 or "验签通过" not in proc2.stdout:
            issues.append(f"decrypt_notify 互打失败: {proc2.stderr or proc2.stdout}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="校验平台文档质量")
    parser.add_argument("--with-notify-test", action="store_true", help="执行 mock/decrypt 互打")
    args = parser.parse_args()

    all_issues: list[str] = []
    for md in sorted(PLATFORM_DOC_ROOT.rglob("*.md")):
        all_issues.extend(check_file(md))

    if args.with_notify_test:
        all_issues.extend(run_notify_roundtrip())

    if all_issues:
        print("平台文档校验未通过：")
        for item in all_issues:
            print(f"  - {item}")
        return 1

    count = len(list(PLATFORM_DOC_ROOT.rglob("*.md")))
    print(f"平台文档校验通过（{count} 个文件）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
