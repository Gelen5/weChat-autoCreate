#!/usr/bin/env python3
"""Lightweight mobile WeChat layout quality checker.

The checker is intentionally heuristic. It catches common layout risks before
copy/paste delivery: manual line breaks, decoration overload, weak captions,
short-tail headings, and fragmented emphasis.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable


CHINESE_RE = re.compile(r"[\u4e00-\u9fff]")
TAG_RE = re.compile(r"<[^>]+>")


@dataclass
class Finding:
    code: str
    severity: str
    message: str
    evidence: str
    suggestion: str


class LayoutHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.heading_stack: list[tuple[str, list[str]]] = []
        self.emphasis_stack: list[tuple[str, list[str], dict[str, str]]] = []
        self.image_positions: list[int] = []
        self.text_chunks: list[str] = []
        self.headings: list[str] = []
        self.emphasis_texts: list[tuple[str, str]] = []
        self.img_count = 0
        self.br_count = 0
        self.hr_count = 0
        self.inline_styles: list[str] = []
        self.attrs_by_tag: list[tuple[str, dict[str, str]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key.lower(): value or "" for key, value in attrs}
        self.stack.append(tag)
        self.attrs_by_tag.append((tag, attr_map))

        style = attr_map.get("style", "")
        if style:
            self.inline_styles.append(style)

        if tag in {"h1", "h2", "h3"}:
            self.heading_stack.append((tag, []))

        if tag in {"strong", "b", "u", "em", "span", "mark"}:
            self.emphasis_stack.append((tag, [], attr_map))

        if tag == "img":
            self.img_count += 1
            self.image_positions.append(len(self.text_chunks))

        if tag == "br":
            self.br_count += 1

        if tag == "hr":
            self.hr_count += 1

    def handle_endtag(self, tag: str) -> None:
        if self.stack:
            self.stack.pop()

        if tag in {"h1", "h2", "h3"} and self.heading_stack:
            _, chunks = self.heading_stack.pop()
            text = normalize_text("".join(chunks))
            if text:
                self.headings.append(text)

        if tag in {"strong", "b", "u", "em", "span", "mark"} and self.emphasis_stack:
            emph_tag, chunks, attrs = self.emphasis_stack.pop()
            text = normalize_text("".join(chunks))
            if text:
                style = attrs.get("style", "")
                marker = emph_tag
                if "background" in style:
                    marker += "+background"
                if "underline" in style:
                    marker += "+underline"
                self.emphasis_texts.append((marker, text))

    def handle_data(self, data: str) -> None:
        if not data.strip():
            return
        self.text_chunks.append(data)
        if self.heading_stack:
            self.heading_stack[-1][1].append(data)
        if self.emphasis_stack:
            self.emphasis_stack[-1][1].append(data)


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def strip_tags(text: str) -> str:
    return normalize_text(TAG_RE.sub(" ", text))


def chinese_len(text: str) -> int:
    return len(CHINESE_RE.findall(text))


def likely_short_tail(text: str) -> bool:
    cjk = chinese_len(text)
    if cjk < 9:
        return False
    # A rough 375px estimate for 20-22px headings: 11-14 CJK chars per line.
    for line_width in (11, 12, 13, 14):
        tail = cjk % line_width
        if 1 <= tail <= 3:
            return True
    return False


def count_style_hits(styles: Iterable[str], patterns: Iterable[str]) -> int:
    total = 0
    for style in styles:
        lower = style.lower()
        total += sum(lower.count(pattern) for pattern in patterns)
    return total


def check_image_captions(parser: LayoutHTMLParser) -> int:
    if parser.img_count == 0:
        return 0
    text = " ".join(parser.text_chunks)
    caption_markers = ("图注", "图片来源", "来源：", "来源:", "caption", "photo", "image")
    marker_count = sum(text.lower().count(marker.lower()) for marker in caption_markers)
    return max(0, parser.img_count - marker_count)


def analyze_html(text: str) -> list[Finding]:
    parser = LayoutHTMLParser()
    parser.feed(text)
    findings: list[Finding] = []

    if parser.br_count > 3:
        findings.append(Finding(
            "manual_line_breaks",
            "warn",
            "Body content appears to use many manual line breaks.",
            f"{parser.br_count} <br> tags",
            "Remove body <br> breaks; split paragraphs or rewrite headings at semantic boundaries.",
        ))

    line_hits = count_style_hits(
        parser.inline_styles,
        ("border-bottom", "border-left", "border-top", "height:1px", "height: 1px"),
    ) + parser.hr_count
    if line_hits >= 8:
        findings.append(Finding(
            "decoration_overload",
            "warn",
            "The layout may rely on too many borders, dividers, or vertical rules.",
            f"{line_hits} line-like style hits",
            "Reduce dividers and borders; make heading hierarchy and spacing carry structure.",
        ))

    for heading in parser.headings:
        if likely_short_tail(heading):
            findings.append(Finding(
                "heading_short_tail_risk",
                "info",
                "A heading may create an awkward 2-3 character tail on mobile.",
                heading,
                "Rewrite the heading or split it at a complete semantic boundary.",
            ))

    short_emphasis = [
        text for marker, text in parser.emphasis_texts
        if chinese_len(text) in {1, 2, 3} and ("background" in marker or marker.startswith(("strong", "b", "u", "mark")))
    ]
    if len(short_emphasis) >= 3:
        findings.append(Finding(
            "fragmented_emphasis",
            "info",
            "Several emphasized fragments are very short.",
            " / ".join(short_emphasis[:6]),
            "Highlight complete phrases or full judgement sentences instead of isolated words.",
        ))

    missing_caption = check_image_captions(parser)
    if missing_caption:
        findings.append(Finding(
            "image_caption_gap",
            "warn",
            "Some images may lack captions or an explicit evidence role.",
            f"{parser.img_count} images, estimated {missing_caption} without caption markers",
            "Add captions that state what the image shows and where it came from.",
        ))

    broken_paths = []
    for tag, attrs in parser.attrs_by_tag:
        if tag != "img":
            continue
        src = attrs.get("src", "")
        if src.startswith(("file:", "C:\\", "D:\\", "./", "../")):
            broken_paths.append(src)
    if broken_paths:
        findings.append(Finding(
            "local_image_path",
            "error",
            "Image paths may break after pasting into WeChat.",
            " / ".join(broken_paths[:3]),
            "Use uploaded WeChat image URLs, base64 only where supported, or a publish-stable asset path.",
        ))

    return findings


def analyze_markdown(text: str) -> list[Finding]:
    findings: list[Finding] = []
    lines = text.splitlines()

    hard_breaks = [line for line in lines if line.endswith("  ") or "<br" in line.lower()]
    if len(hard_breaks) > 3:
        findings.append(Finding(
            "manual_line_breaks",
            "warn",
            "Markdown appears to contain many manual line breaks.",
            f"{len(hard_breaks)} hard-break lines",
            "Use paragraphs for body rhythm; reserve manual breaks for semantic title or quote splits.",
        ))

    headings = [line.lstrip("#").strip() for line in lines if line.startswith("#")]
    for heading in headings:
        if likely_short_tail(heading):
            findings.append(Finding(
                "heading_short_tail_risk",
                "info",
                "A heading may create an awkward 2-3 character tail on mobile.",
                heading,
                "Rewrite the heading or split it at a complete semantic boundary.",
            ))

    image_lines = [line for line in lines if re.search(r"!\[[^\]]*\]\([^)]+\)", line)]
    caption_lines = [line for line in lines if any(marker in line for marker in ("图注", "图片来源", "来源：", "来源:"))]
    if image_lines and len(caption_lines) < len(image_lines):
        findings.append(Finding(
            "image_caption_gap",
            "warn",
            "Some Markdown images may lack captions or evidence notes.",
            f"{len(image_lines)} images, {len(caption_lines)} caption/source lines",
            "Add a caption/source line and clarify which nearby claim each image proves.",
        ))

    short_bold = re.findall(r"\*\*([^*\n]{1,6})\*\*", text)
    short_bold = [item for item in short_bold if 1 <= chinese_len(item) <= 3]
    if len(short_bold) >= 3:
        findings.append(Finding(
            "fragmented_emphasis",
            "info",
            "Several bold fragments are very short.",
            " / ".join(short_bold[:6]),
            "Bold complete phrases or full judgement sentences instead of isolated words.",
        ))

    return findings


def render_markdown(findings: list[Finding], path: Path) -> str:
    if not findings:
        return f"OK: no mobile layout quality findings for {path}"

    lines = [f"# Layout quality findings for {path}", ""]
    for item in findings:
        lines.extend([
            f"## [{item.severity.upper()}] {item.code}",
            item.message,
            "",
            f"- Evidence: {item.evidence}",
            f"- Suggestion: {item.suggestion}",
            "",
        ])
    return "\n".join(lines).rstrip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Check mobile WeChat layout quality risks.")
    parser.add_argument("file", help="HTML or Markdown file to check")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args()

    path = Path(args.file)
    text = path.read_text(encoding="utf-8")
    is_html = path.suffix.lower() in {".html", ".htm"} or "<html" in text.lower() or "<section" in text.lower()
    findings = analyze_html(text) if is_html else analyze_markdown(text)

    if args.format == "json":
        print(json.dumps([asdict(item) for item in findings], ensure_ascii=False, indent=2))
    else:
        print(render_markdown(findings, path))

    return 1 if any(item.severity == "error" for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
