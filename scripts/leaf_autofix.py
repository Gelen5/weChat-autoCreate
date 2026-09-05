#!/usr/bin/env python3
"""Auto-wrap unwrapped CJK text nodes in ```html blocks with <span leaf="">.

Idempotent: nodes already inside a <span leaf...> ancestor are left alone.
Teaching blocks containing an <!-- ... ❌ ... --> comment are skipped.
SVG subtrees are untouched (<text> is exempt from leaf wrapping).

Usage:
    python scripts/leaf_autofix.py file1.md [file2.md ...]   # rewrite in place
    python scripts/leaf_autofix.py --check file1.md          # report only
Exit codes: 0 = nothing to do, 1 = fixes applied (or --check found gaps).
"""
from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from source_lint import HTML_BLOCK_RE, COUNTER_EXAMPLE_RE  # noqa: E402

CJK_RE = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf]")
VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


class LeafWrapper(HTMLParser):
    """Rebuild HTML, wrapping bare CJK text nodes in <span leaf="">.

    Tags are re-emitted verbatim via get_starttag_text() so attribute order,
    quoting and whitespace survive round-tripping.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self.leaf_depth = 0
        self.svg_depth = 0
        self.raw_depth = 0  # inside <style>/<script>
        self.changed = False

    # -- tag handlers ---------------------------------------------------
    def handle_starttag(self, tag: str, attrs) -> None:  # noqa: ANN001
        original = self.get_starttag_text() or ""
        self.out.append(original)
        lowered = tag.lower()
        if re.fullmatch(r"span", lowered) and re.search(
                r"leaf", original, re.I):
            self.leaf_depth += 1
        if lowered == "svg":
            self.svg_depth += 1
        if lowered in ("style", "script"):
            self.raw_depth += 1

    def handle_startendtag(self, tag: str, attrs) -> None:  # noqa: ANN001
        self.out.append(self.get_starttag_text() or "")

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.lower()
        self.out.append(f"</{tag}>")
        if re.fullmatch(r"span", lowered) and self.leaf_depth:
            self.leaf_depth -= 1
        if lowered == "svg" and self.svg_depth:
            self.svg_depth -= 1
        if lowered in ("style", "script") and self.raw_depth:
            self.raw_depth -= 1

    def handle_data(self, data: str) -> None:
        if (self.leaf_depth or self.svg_depth or self.raw_depth
                or not CJK_RE.search(data)):
            self.out.append(data)
            return
        self.out.append(f'<span leaf="">{data}</span>')
        self.changed = True

    def unknown_decl(self, data: str) -> None:
        self.out.append(f"<![{data}]>")

    def result(self) -> str:
        return "".join(self.out)


def fix_block(block: str) -> str:
    if COUNTER_EXAMPLE_RE.search(block):
        return block
    for _ in range(10):  # nested spans may need a couple of passes
        wrapper = LeafWrapper()
        wrapper.feed(block)
        wrapper.close()
        if not wrapper.changed:
            return wrapper.result()
        block = wrapper.result()
    return block


def process_file(path: Path, check_only: bool) -> bool:
    """Return True if the file needed fixes."""
    text = path.read_text(encoding="utf-8")
    changed = False

    def repl(match: re.Match[str]) -> str:  # noqa: ANN202
        nonlocal changed
        fixed = fix_block(match.group(1))
        if fixed != match.group(1):
            changed = True
        return f"```html\n{fixed}```"

    new_text = HTML_BLOCK_RE.sub(repl, text)
    if changed and not check_only:
        path.write_text(new_text, encoding="utf-8")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--check", action="store_true",
                        help="report only, do not rewrite")
    args = parser.parse_args()

    touched = 0
    for path in args.files:
        if process_file(path, args.check):
            touched += 1
            verb = "needs wrapping" if args.check else "wrapped"
            print(f"{path}: {verb}")
        else:
            print(f"{path}: clean")
    return 1 if touched else 0


if __name__ == "__main__":
    sys.exit(main())
