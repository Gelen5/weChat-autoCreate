#!/usr/bin/env python3
"""Source lint: validate every ```html block inside references/*.md.

The component library and style presets are the source of truth the model
copies from. If a snippet here violates a compliance rule, every generated
article inherits the violation. This script runs the same analyzer used for
rendered articles over the source snippets.

Teaching blocks that deliberately show wrong markup are marked with an
HTML comment containing the ❌ character and are skipped.

Usage:
    python scripts/source_lint.py                 # scan references/
    python scripts/source_lint.py path/to/file.md # scan one file
Exit codes: 0 = clean, 1 = blocking findings.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wechat_compliance_check import analyze  # noqa: E402

HTML_BLOCK_RE = re.compile(r"```html[^\n]*\n(.*?)```", re.S)
COUNTER_EXAMPLE_RE = re.compile(r"<!--[^>]*❌")  # deliberate wrong-markup demo
BLOCKING_SEVERITIES = ("error", "warn_blocking")


def lint_markdown(path: Path) -> list[tuple[int, list[str]]]:
    """Return [(block_index, blocking_codes)] for one markdown file."""
    text = path.read_text(encoding="utf-8")
    failures: list[tuple[int, list[str]]] = []
    for idx, block in enumerate(HTML_BLOCK_RE.findall(text), start=1):
        if COUNTER_EXAMPLE_RE.search(block):
            continue
        blocking = [
            f.code for f in analyze(block)
            if f.severity in BLOCKING_SEVERITIES
        ]
        if blocking:
            failures.append((idx, blocking))
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("targets", nargs="*", type=Path,
                        help="markdown files or directories (default: references/)")
    parser.add_argument("--root", type=Path, default=None,
                        help="repo root (default: parent of scripts/)")
    args = parser.parse_args()

    repo_root = args.root or Path(__file__).resolve().parent.parent
    targets = args.targets or [repo_root / "references"]

    files: list[Path] = []
    for target in targets:
        if target.is_dir():
            files.extend(sorted(target.rglob("*.md")))
        else:
            files.append(target)

    total_blocks = 0
    failed_files = 0
    for md in files:
        text = md.read_text(encoding="utf-8")
        total_blocks += len(HTML_BLOCK_RE.findall(text))
        failures = lint_markdown(md)
        if not failures:
            continue
        failed_files += 1
        rel = md.relative_to(repo_root) if md.is_relative_to(repo_root) else md
        print(f"{rel}:")
        for idx, codes in failures:
            print(f"  block {idx}: {', '.join(codes)}")

    if failed_files:
        print(f"\nFAIL: {failed_files} file(s) with blocking snippets "
              f"(scanned {total_blocks} html blocks)")
        print("Fix the snippets, or mark deliberate wrong-markup demos "
              "with an <!-- ... ❌ ... --> comment.")
        return 1
    print(f"OK: {total_blocks} html block(s) clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
