"""Idempotent leaf wrapping for Chinese text in WeChat HTML fragments."""

from __future__ import annotations

import re
from html.parser import HTMLParser

CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")


class _LeafWrapper(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.out: list[str] = []
        self.leaf_depth = 0
        self.exempt_depth = 0

    def handle_starttag(self, tag, attrs):
        raw = self.get_starttag_text() or ""
        self.out.append(raw)
        lowered = tag.lower()
        if lowered == "span" and any(name.lower() == "leaf" for name, _ in attrs):
            self.leaf_depth += 1
        if lowered in {"svg", "style", "script"}:
            self.exempt_depth += 1

    def handle_startendtag(self, tag, attrs):
        self.out.append(self.get_starttag_text() or "")

    def handle_endtag(self, tag):
        lowered = tag.lower()
        self.out.append(f"</{tag}>")
        if lowered == "span" and self.leaf_depth:
            self.leaf_depth -= 1
        if lowered in {"svg", "style", "script"} and self.exempt_depth:
            self.exempt_depth -= 1

    def handle_data(self, data):
        if self.leaf_depth or self.exempt_depth or not CJK_RE.search(data):
            self.out.append(data)
        else:
            self.out.append(f'<span leaf="">{data}</span>')

    def handle_entityref(self, name):
        self.out.append(f"&{name};")

    def handle_charref(self, name):
        self.out.append(f"&#{name};")

    def handle_comment(self, data):
        self.out.append(f"<!--{data}-->")

    def handle_decl(self, decl):
        self.out.append(f"<!{decl}>")


def wrap_cjk_leaf(html: str) -> str:
    parser = _LeafWrapper()
    parser.feed(html)
    parser.close()
    return "".join(parser.out)
