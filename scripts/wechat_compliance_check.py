#!/usr/bin/env python3
"""Deterministic WeChat HTML compliance checker.

This complements ``scripts/layout_quality_check.py``. That script is heuristic:
it judges mobile reading quality (manual breaks, decoration overload, short-tail
headings, fragmented emphasis, captions). This one is deterministic: it enforces
the hard platform rules already documented in
``references/wechat-html-spec.md`` and the leaf-wrapping rule described in
``references/leaf-and-compliance.md``.

Two design rules keep the checker honest:

1. CSS patterns are matched against parsed ``style`` attribute values, never
   against raw source text. Scanning raw text produces false positives from HTML
   comments and from attribute strings that merely mention ``float:``.
2. Severity is explicit. ``error`` and ``warn_blocking`` always fail the run.
   ``warn_allowable`` can be waived with ``--allow CODE``, but the waiver is
   written to a record file so a human can audit it later.

Usage:
    python scripts/wechat_compliance_check.py article.html
    python scripts/wechat_compliance_check.py article.html --format json
    python scripts/wechat_compliance_check.py article.html --allow halfwidth_punct
    python scripts/wechat_compliance_check.py article.html --baseline
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable

CJK_RE = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf]")
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)

# Half-width punctuation that looks wrong next to CJK text.
HALFWIDTH_PUNCT_RE = re.compile(
    r"[\u4e00-\u9fff][,;!?]|[,;!?][\u4e00-\u9fff]"
)

# Styles that mark a region as code, so half-width punctuation is expected.
CODE_STYLE_RE = re.compile(
    r"monospace|consolas|courier|menlo|monaco|white-space\s*:\s*pre", re.I
)

# Tags whose text content must not be leaf-checked.
LEAF_EXEMPT_TAGS = {"svg", "style", "script"}

# Inline CSS ranges WeChat is documented to accept. Used for the numeric guards.
FONT_SIZE_RE = re.compile(r"font-size\s*:\s*([\d.]+)\s*(px|pt|em|rem)?", re.I)
LINE_HEIGHT_RE = re.compile(r"line-height\s*:\s*([\d.]+)\s*(px|pt|em|%)?", re.I)
LETTER_SPACING_RE = re.compile(r"letter-spacing\s*:\s*(-?[\d.]+)\s*px", re.I)


@dataclass(frozen=True)
class Rule:
    code: str
    severity: str  # error | warn_blocking | warn_allowable | info
    pattern: re.Pattern[str]
    message: str
    suggestion: str


@dataclass
class Finding:
    code: str
    severity: str
    message: str
    suggestion: str
    evidence: list[str] = field(default_factory=list)
    count: int = 0


SEVERITY_ORDER = {"error": 0, "warn_blocking": 1, "warn_allowable": 2, "info": 3}

RULES: list[Rule] = [
    # ---- Structural: things WeChat strips or rewrites -------------------
    Rule(
        "style_tag", "error", re.compile(r"<style[\s>]", re.I),
        "<style> tag is stripped by WeChat.",
        "Inline every style on the element itself.",
    ),
    Rule(
        "script_tag", "error", re.compile(r"<script[\s>]", re.I),
        "<script> tag is stripped by WeChat.",
        "Remove JavaScript; WeChat never executes it.",
    ),
    Rule(
        "link_tag", "error", re.compile(r"<link[\s>]", re.I),
        "<link> tag is stripped by WeChat.",
        "Remove it; external stylesheets never survive.",
    ),
    Rule(
        "iframe_tag", "error", re.compile(r"<iframe[\s>]", re.I),
        "<iframe> tag is stripped by WeChat.",
        "Replace with an image or a text block.",
    ),
    Rule(
        "form_control", "error", re.compile(r"<(input|textarea|select|button)[\s>]", re.I),
        "Form controls are stripped by WeChat.",
        "Replace with a static section or an image.",
    ),
    Rule(
        "js_protocol", "error", re.compile(r"(href|src)\s*=\s*[\"']?\s*javascript:", re.I),
        "javascript: URLs are stripped.",
        "Remove the handler.",
    ),

    # ---- CSS: filtered properties --------------------------------------
    Rule(
        "css_position", "error",
        re.compile(r"position\s*:\s*(fixed|absolute|sticky|relative)", re.I),
        "position is filtered by WeChat.",
        "Use flex, margin and padding to place elements.",
    ),
    Rule(
        "css_grid", "error", re.compile(r"display\s*:\s*grid", re.I),
        "display:grid is not supported.",
        "Use display:flex instead.",
    ),
    Rule(
        "css_var", "error", re.compile(r"var\s*\(\s*--", re.I),
        "CSS custom properties are not supported.",
        "Write the literal colour value.",
    ),
    Rule(
        "css_at_media", "error", re.compile(r"@media", re.I),
        "@media queries are stripped.",
        "Design for a fixed ~375-390px width.",
    ),
    Rule(
        "css_at_keyframes", "error", re.compile(r"@keyframes", re.I),
        "@keyframes is stripped.",
        "Use a static layout.",
    ),
    Rule(
        "css_at_import", "error", re.compile(r"@import", re.I),
        "@import is stripped.",
        "Inline everything.",
    ),
    Rule(
        "css_animation", "error",
        re.compile(r"(animation|transition)\s*:", re.I),
        "animation/transition are filtered.",
        "Remove the motion; it never renders.",
    ),
    Rule(
        "css_transform", "error", re.compile(r"transform\s*:", re.I),
        "transform is filtered.",
        "Lay out with flex instead of transforming.",
    ),
    Rule(
        "css_calc", "error", re.compile(r"calc\s*\(", re.I),
        "calc() is filtered.",
        "Use a fixed px value.",
    ),
    Rule(
        "css_clamp", "error",
        re.compile(r"\b(clamp|min|max)\s*\(", re.I),
        "clamp()/min()/max() are filtered.",
        "Use a fixed px value.",
    ),
    Rule(
        "css_viewport_unit", "error",
        re.compile(r":[^;{]*?\d+(?:\.\d+)?\s*(vw|vh|vmin|vmax)\b", re.I),
        "Viewport units do not survive the editor.",
        "Use px or %.",
    ),
    Rule(
        "css_rem_unit", "error",
        re.compile(r"font-size\s*:\s*[\d.]+\s*rem", re.I),
        "rem sizing is unreliable in WeChat.",
        "Use px.",
    ),
    Rule(
        "css_filter", "error", re.compile(r"(backdrop-)?filter\s*:", re.I),
        "filter is stripped.",
        "Use solid colours.",
    ),
    Rule(
        "css_clip_path", "error", re.compile(r"clip-path\s*:", re.I),
        "clip-path is stripped.",
        "Use a real element or an SVG shape.",
    ),
    Rule(
        "css_pseudo", "error", re.compile(r"::?(before|after|first-line|first-letter)", re.I),
        "Pseudo-elements are stripped.",
        "Add a real element with inline styles.",
    ),
    Rule(
        "css_webfont", "error",
        re.compile(r"url\s*\(\s*[\"']?https?://[^\"')]*\.(?:woff2?|ttf|otf|eot)", re.I),
        "External web fonts are not loaded.",
        "Use a system font stack.",
    ),

    # ---- CSS: unstable, explicit waiver allowed ------------------------
    Rule(
        "css_float", "warn_allowable", re.compile(r"float\s*:", re.I),
        "float is unstable in WeChat.",
        "Prefer display:flex. Waive only if you verified the render.",
    ),
    Rule(
        "css_box_shadow", "warn_allowable", re.compile(r"box-shadow\s*:", re.I),
        "box-shadow renders inconsistently across clients.",
        "Simulate depth with a light border or a background tint.",
    ),
    Rule(
        "css_gradient", "warn_allowable", re.compile(r"(linear|radial)-gradient\s*\(", re.I),
        "gradients are documented as filtered here, but other skills report them working.",
        "Verify in a real draft, or use a flat colour.",
    ),
    Rule(
        "css_gap", "warn_allowable", re.compile(r"(?:^|[;{\s])gap\s*:", re.I),
        "gap support is disputed: our spec lists it as supported, gzh-design bans it.",
        "Verify in a real draft, or replace with margin on children.",
    ),
    Rule(
        "css_white_space_pre", "warn_allowable",
        re.compile(r"white-space\s*:\s*(pre|pre-wrap)\b", re.I),
        "white-space:pre renders source indentation as a large left indent.",
        "Emit one <p style=\"margin:0\"> per line and indent with full-width spaces.",
    ),
    Rule(
        "img_width_100", "warn_allowable",
        re.compile(r"<img[^>]*?(?<![\w-])width\s*:\s*100%", re.I),
        "width:100% stretches small images and makes them blurry.",
        "Use max-width:100%;height:auto;display:block;margin:0 auto.",
    ),

    # ---- Structure advice ----------------------------------------------
    Rule(
        "div_tag", "warn_allowable", re.compile(r"</?div[\s>]", re.I),
        "<div> works but <section> is the reliable WeChat container.",
        "Rename every <div> to <section>.",
    ),
    Rule(
        "class_attr", "warn_allowable", re.compile(r"\sclass\s*=", re.I),
        "class attributes are stripped.",
        "Move the declarations into an inline style.",
    ),
    Rule(
        "id_attr", "warn_allowable", re.compile(r"\sid\s*=", re.I),
        "id attributes are stripped.",
        "Remove id unless it is a fragment anchor.",
    ),
    Rule(
        "data_attr", "info", re.compile(r"\sdata-[a-z-]+\s*=", re.I),
        "data-* attributes may be stripped.",
        "Only keep data-* if a renderer needs it (for example leaf=\"\").",
    ),
    Rule(
        "table_layout_suspect", "info",
        re.compile(r"<table[^>]*>\s*<tr[^>]*>\s*<td[^>]*>\s*<(?:section|div|p)", re.I),
        "A table appears to be used as a layout skeleton.",
        "Use table only for real tabular data; use flex for layout.",
    ),
]


class DocumentParser(HTMLParser):
    """Collects the structures the rules need, without keeping the whole DOM."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.styles: list[str] = []
        self.tags: list[str] = []
        self.attrs_by_tag: list[tuple[str, dict[str, str]]] = []
        self.comments: list[str] = []
        self.leaf_violations: list[str] = []
        self.halfwidth_hits: list[str] = []
        self.cjk_text_nodes = 0
        self.leaf_wrapped_nodes = 0
        self._stack: list[tuple[str, bool]] = []  # (tag, is_leaf)
        self._code_depth = 0
        self._svg_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key.lower(): (value or "") for key, value in attrs}
        self.tags.append(tag)
        self.attrs_by_tag.append((tag, attr_map))

        style = attr_map.get("style", "")
        if style:
            self.styles.append(style)

        is_leaf = "leaf" in attr_map
        is_code = bool(CODE_STYLE_RE.search(style))
        self._stack.append((tag, is_leaf))
        if is_code:
            self._code_depth += 1
        if tag == "svg":
            self._svg_depth += 1

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        # Self-closing tag: never wraps text, so it only matters for styles.
        attr_map = {key.lower(): (value or "") for key, value in attrs}
        self.tags.append(tag)
        self.attrs_by_tag.append((tag, attr_map))
        style = attr_map.get("style", "")
        if style:
            self.styles.append(style)

    def handle_endtag(self, tag: str) -> None:
        if not self._stack:
            return
        open_tag, _ = self._stack.pop()
        if open_tag == "svg" and self._svg_depth:
            self._svg_depth -= 1

    def handle_data(self, data: str) -> None:
        stripped = data.strip()
        if not stripped:
            return

        in_code = self._code_depth > 0
        in_svg = self._svg_depth > 0
        in_exempt_tag = bool(self._stack) and self._stack[-1][0] in LEAF_EXEMPT_TAGS

        if CJK_RE.search(stripped):
            self.cjk_text_nodes += 1
            if in_svg or in_exempt_tag:
                # SVG <text> and raw code samples are not leaf-wrapped.
                self.leaf_wrapped_nodes += 1
            else:
                leaf_ancestor = any(is_leaf for _, is_leaf in self._stack)
                if leaf_ancestor:
                    self.leaf_wrapped_nodes += 1
                else:
                    self.leaf_violations.append(_clip(stripped, 40))

        if not in_code and not in_svg:
            for match in HALFWIDTH_PUNCT_RE.finditer(stripped):
                self.halfwidth_hits.append(_clip(match.group(0), 24))

    def handle_comment(self, data: str) -> None:
        self.comments.append(data)


def _clip(text: str, limit: int) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"


SVG_BLOCK_RE = re.compile(r"<svg\b.*?</svg>", re.S | re.I)


def _scan_raw(source: str) -> dict[str, list[str]]:
    """Fallback scan on comment-free source.

    The parser misses content inside malformed markup, so structural rules run
    against raw text as well. CSS rules stay parser-only to avoid false hits.

    SVG subtrees are removed first: ids are legitimate there (markers, gradients)
    and the structural rules only concern the HTML layer.
    """
    cleaned = SVG_BLOCK_RE.sub(" ", COMMENT_RE.sub(" ", source))
    hits: dict[str, list[str]] = {}
    structural = {
        rule.code for rule in RULES
        if rule.code in {
            "style_tag", "script_tag", "link_tag", "iframe_tag",
            "form_control", "js_protocol", "div_tag", "class_attr",
            "id_attr", "data_attr", "table_layout_suspect",
            "img_width_100",
        }
    }
    for rule in RULES:
        if rule.code not in structural:
            continue
        matches = rule.pattern.findall(cleaned)
        if matches:
            hits[rule.code] = [_clip(str(m if isinstance(m, str) else m[0]), 40)
                               for m in matches[:5]]
    return hits


def _check_numeric_ranges(styles: Iterable[str]) -> list[Finding]:
    findings: list[Finding] = []
    bad_sizes, bad_heights, bad_spacing = [], [], []

    for style in styles:
        for match in FONT_SIZE_RE.finditer(style):
            value = float(match.group(1))
            unit = (match.group(2) or "px").lower()
            if unit == "px" and not (3 <= value <= 51):
                bad_sizes.append(match.group(0))
        for match in LINE_HEIGHT_RE.finditer(style):
            value = float(match.group(1))
            unit = (match.group(2) or "").lower()
            # The documented 0-3 safety range applies to unitless multipliers.
            # A px line-height is a vertical-centering trick (line-height == box
            # height) and any positive value is valid.
            if not unit and not (0 < value <= 3):
                bad_heights.append(match.group(0))
        for match in LETTER_SPACING_RE.finditer(style):
            value = float(match.group(1))
            if not (0 <= value <= 5):
                bad_spacing.append(match.group(0))

    if bad_sizes:
        findings.append(Finding(
            "font_size_out_of_range", "warn_allowable",
            "font-size outside the 3-51px range WeChat accepts.",
            "Clamp to 3-51px.",
            bad_sizes[:5], len(bad_sizes),
        ))
    if bad_heights:
        findings.append(Finding(
            "line_height_out_of_range", "warn_allowable",
            "line-height outside the 0-3 range WeChat accepts.",
            "Use a unitless value between 1.4 and 2.",
            bad_heights[:5], len(bad_heights),
        ))
    if bad_spacing:
        findings.append(Finding(
            "letter_spacing_out_of_range", "warn_allowable",
            "letter-spacing outside the 0-5px range WeChat accepts.",
            "Clamp to 0-5px.",
            bad_spacing[:5], len(bad_spacing),
        ))
    return findings


def _check_image_sources(parser: DocumentParser) -> list[Finding]:
    allowed = ("mmbiz.qpic.cn", "mmbiz.qlogo.cn", "wx.qlogo.cn", "thirdwx.qlogo.cn")
    bad = []
    for tag, attrs in parser.attrs_by_tag:
        if tag != "img":
            continue
        src = attrs.get("src", "")
        if not src or src.startswith("data:"):
            continue
        # Placeholders such as IMAGE_URL are template slots, not real hosts.
        if not src.lower().startswith(("http://", "https://")):
            continue
        if not any(host in src for host in allowed):
            bad.append(_clip(src, 40))
    if bad:
        return [Finding(
            "image_host_not_wechat", "warn_blocking",
            "Image host is not a WeChat image domain.",
            "Upload to the WeChat media API and use the returned mmbiz URL, or inline base64.",
            bad[:5], len(bad),
        )]
    return []


def analyze(text: str) -> list[Finding]:
    parser = DocumentParser()
    parser.feed(COMMENT_RE.sub(" ", text))
    parser.close()

    findings: list[Finding] = []

    # CSS rules run against parsed style values only.
    style_blob = "\n".join(parser.styles)
    css_codes = {
        "css_position", "css_grid", "css_var", "css_animation",
        "css_transform", "css_calc", "css_clamp", "css_viewport_unit",
        "css_rem_unit", "css_filter", "css_clip_path", "css_pseudo",
        "css_webfont", "css_float", "css_box_shadow", "css_gradient",
        "css_gap", "css_white_space_pre",
    }
    for rule in RULES:
        if rule.code not in css_codes:
            continue
        matches = rule.pattern.findall(style_blob)
        if matches:
            findings.append(Finding(
                rule.code, rule.severity, rule.message, rule.suggestion,
                [_clip(str(m if isinstance(m, str) else m[0]), 40) for m in matches[:5]],
                len(matches),
            ))

    # At-rules (@media/@keyframes/@import) can never appear in a style
    # attribute; they only live inside <style> blocks, whose contents the
    # parser does not collect as style values. Scan those contents directly:
    # code samples in <pre> stay exempt because they are outside <style>.
    style_tag_blob = "\n".join(
        re.findall(r"<style\b[^>]*>(.*?)</style>", text, re.S | re.I)
    )
    if style_tag_blob:
        for rule in RULES:
            if rule.code not in {"css_at_media", "css_at_keyframes", "css_at_import"}:
                continue
            matches = rule.pattern.findall(style_tag_blob)
            if matches:
                findings.append(Finding(
                    rule.code, rule.severity, rule.message, rule.suggestion,
                    [_clip(str(m if isinstance(m, str) else m[0]), 40) for m in matches[:5]],
                    len(matches),
                ))

    # Structural rules use the raw fallback scan.
    raw_hits = _scan_raw(text)
    for rule in RULES:
        if rule.code in raw_hits:
            findings.append(Finding(
                rule.code, rule.severity, rule.message, rule.suggestion,
                raw_hits[rule.code], len(raw_hits[rule.code]),
            ))

    findings.extend(_check_numeric_ranges(parser.styles))
    findings.extend(_check_image_sources(parser))

    # Leaf wrapping: the rule that stops styles vanishing after paste.
    if parser.cjk_text_nodes and parser.leaf_wrapped_nodes == 0:
        findings.append(Finding(
            "leaf_missing_all", "warn_blocking",
            "No CJK text node is wrapped in <span leaf=\"\">.",
            "Wrap every Chinese text node, for example <p><span leaf=\"\">正文</span></p>.",
            parser.leaf_violations[:5], len(parser.leaf_violations),
        ))
    elif parser.leaf_violations:
        findings.append(Finding(
            "leaf_missing_partial", "warn_blocking",
            "Some CJK text nodes are not leaf-wrapped.",
            "Wrap the remaining text nodes so the editor keeps their inline styles.",
            parser.leaf_violations[:5], len(parser.leaf_violations),
        ))

    if parser.halfwidth_hits:
        findings.append(Finding(
            "halfwidth_punct", "warn_allowable",
            "Half-width punctuation appears next to Chinese text.",
            "Use full-width ，。；！？ unless the text is code.",
            parser.halfwidth_hits[:5], len(parser.halfwidth_hits),
        ))

    findings.sort(key=lambda item: (SEVERITY_ORDER.get(item.severity, 9), item.code))
    return findings


ALLOWABLE_SEVERITY = "warn_allowable"


def render_markdown(findings: list[Finding], path: Path, waived: list[str]) -> str:
    blocking = [f for f in findings if f.severity in ("error", "warn_blocking")]
    allowed = [
        f.code for f in findings
        if f.severity == ALLOWABLE_SEVERITY and f.code in waived
    ]

    lines = [f"# WeChat compliance report for {path}", ""]
    if not findings:
        lines.append("OK: no compliance findings.")
        return "\n".join(lines).rstrip()

    if blocking:
        lines.append(f"**Blocking: {len(blocking)} finding(s) must be fixed before delivery.**")
        lines.append("")

    for item in findings:
        marker = "FAIL" if item.severity in ("error", "warn_blocking") else "WARN"
        if item.severity == "info":
            marker = "INFO"
        if item.code in waived:
            marker = "WAIVED"
        lines.extend([
            f"## [{marker}] {item.code}",
            item.message,
            "",
            f"- Count: {item.count}",
            f"- Evidence: {', '.join(item.evidence) if item.evidence else 'n/a'}",
            f"- Fix: {item.suggestion}",
            "",
        ])

    if allowed:
        lines.append(f"_Waived this run: {', '.join(allowed)}_")
    return "\n".join(lines).rstrip()


def write_allowance_record(path: Path, waived: list[str], findings: list[Finding]) -> Path:
    record_dir = path.parent / ".cache"
    record_dir.mkdir(parents=True, exist_ok=True)
    record_path = record_dir / "wechat_compliance_allowance.json"
    payload = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "target": str(path),
        "waived_codes": waived,
        "waived_findings": [
            {"code": f.code, "count": f.count, "message": f.message}
            for f in findings if f.code in waived
        ],
    }
    record_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return record_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check WeChat HTML for platform compliance and leaf wrapping."
    )
    parser.add_argument("file", help="HTML file to check")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument(
        "--allow", action="append", default=[], metavar="CODE",
        help="Waive a warn_allowable code for this run (repeatable).",
    )
    parser.add_argument(
        "--baseline", action="store_true",
        help="Report only. Never fails, useful for auditing existing articles.",
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="Treat warn_allowable findings as failures too.",
    )
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"ERROR: file not found: {path}")
        return 2

    text = path.read_text(encoding="utf-8", errors="replace")
    findings = analyze(text)

    # Only warn_allowable codes can be waived. Blocking findings are never
    # waivable, no matter what the caller passes.
    waivable = {f.code for f in findings if f.severity == ALLOWABLE_SEVERITY}
    waived = [code for code in args.allow if code in waivable]
    rejected = [code for code in args.allow if code and code not in waivable]

    if waived:
        write_allowance_record(path, waived, findings)
    if rejected and args.format == "markdown":
        print(f"NOT WAIVABLE (blocking or unknown, ignored): {', '.join(rejected)}")
        print("")

    if waived:
        write_allowance_record(path, waived, findings)

    if args.format == "json":
        print(json.dumps(
            {
                "target": str(path),
                "waived": waived,
                "findings": [
                    {
                        "code": f.code,
                        "severity": f.severity,
                        "message": f.message,
                        "suggestion": f.suggestion,
                        "evidence": f.evidence,
                        "count": f.count,
                    }
                    for f in findings
                ],
            },
            ensure_ascii=False, indent=2,
        ))
    else:
        print(render_markdown(findings, path, waived))

    if args.baseline:
        return 0

    blocking = any(
        f.severity in ("error", "warn_blocking") and f.code not in waived
        for f in findings
    )
    loose = args.strict and any(
        f.severity == "warn_allowable" and f.code not in waived for f in findings
    )
    return 1 if (blocking or loose) else 0


if __name__ == "__main__":
    raise SystemExit(main())
