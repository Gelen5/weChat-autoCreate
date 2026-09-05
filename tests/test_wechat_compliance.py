"""Tests for the deterministic WeChat compliance checker.

Two kinds of tests live here:

* Forward tests — a known violation must produce the expected rule code.
* Reverse tests (marked with a star) — a *correct* or *exempt* document must
  produce no finding. These exist so the checker cannot pass vacuously: a
  regex typo that silently matches nothing would keep every forward test red,
  but only the reverse tests catch a checker that got too strict or too loose
  in a way nobody noticed.
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wechat_compliance_check import analyze  # noqa: E402


def codes(html: str) -> set[str]:
    return {finding.code for finding in analyze(html)}


class StructuralRuleTests(unittest.TestCase):
    def test_style_script_and_link_tags_are_errors(self):
        self.assertIn("style_tag", codes("<style>.a{color:red}</style><p><span leaf=\"\">正文</span></p>"))
        self.assertIn("script_tag", codes("<script>alert(1)</script>"))
        self.assertIn("link_tag", codes("<link rel=\"stylesheet\" href=\"a.css\">"))

    def test_class_and_id_attributes_are_warned(self):
        found = codes("<section class=\"card\" id=\"main\"><p><span leaf=\"\">正文</span></p></section>")
        self.assertIn("class_attr", found)
        self.assertIn("id_attr", found)

    def test_javascript_url_is_error(self):
        self.assertIn("js_protocol", codes("<a href=\"javascript:void(0)\">x</a>"))

    def test_form_controls_are_errors(self):
        self.assertIn("form_control", codes("<input type=\"text\">"))
        self.assertIn("form_control", codes("<button>点我</button>"))


class CssRuleTests(unittest.TestCase):
    def test_filtered_properties_are_errors(self):
        cases = {
            "css_grid": "<section style=\"display:grid;\"></section>",
            "css_position": "<section style=\"position:absolute;top:0;\"></section>",
            "css_var": "<section style=\"color:var(--main);\"></section>",
            "css_calc": "<section style=\"width:calc(100% - 20px);\"></section>",
            "css_animation": "<section style=\"animation:fade 2s;\"></section>",
            "css_transform": "<section style=\"transform:rotate(5deg);\"></section>",
            "css_at_media": "<style>@media (max-width:375px){p{color:red}}</style>",
            "css_rem_unit": "<section style=\"font-size:1.2rem;\"></section>",
        }
        for expected, html in cases.items():
            with self.subTest(rule=expected):
                self.assertIn(expected, codes(html))

    def test_viewport_units_are_errors(self):
        self.assertIn("css_viewport_unit", codes("<section style=\"width:50vw;\"></section>"))

    def test_disputed_properties_are_waivable_warnings(self):
        findings = {f.code: f for f in analyze(
            "<section style=\"float:left;box-shadow:0 2px 4px #000;gap:8px;\"></section>"
        )}
        for code in ("css_float", "css_box_shadow", "css_gap"):
            with self.subTest(rule=code):
                self.assertIn(code, findings)
                self.assertEqual(findings[code].severity, "warn_allowable")

    def test_gradient_is_waivable_warning(self):
        findings = {f.code: f for f in analyze(
            "<section style=\"background:linear-gradient(90deg,#000,#fff);\"></section>"
        )}
        self.assertEqual(findings["css_gradient"].severity, "warn_allowable")

    def test_numeric_ranges_are_enforced(self):
        self.assertIn("font_size_out_of_range", codes("<section style=\"font-size:80px;\"></section>"))
        self.assertIn("line_height_out_of_range", codes("<section style=\"line-height:5;\"></section>"))
        self.assertIn("letter_spacing_out_of_range", codes("<section style=\"letter-spacing:9px;\"></section>"))


class LeafRuleTests(unittest.TestCase):
    def test_unwrapped_chinese_text_is_blocking(self):
        findings = {f.code: f for f in analyze("<p style=\"color:#333;\">这是没有包裹的中文。</p>")}
        self.assertIn("leaf_missing_all", findings)
        self.assertEqual(findings["leaf_missing_all"].severity, "warn_blocking")

    def test_partial_wrapping_is_blocking(self):
        html = (
            "<p><span leaf=\"\">已包裹</span></p>"
            "<p style=\"color:#333;\">未包裹的中文</p>"
        )
        self.assertIn("leaf_missing_partial", codes(html))

    def test_wrapped_document_has_no_leaf_finding(self):
        html = "<section><p style=\"color:#333;\"><span leaf=\"\">全部包好了。</span></p></section>"
        self.assertNotIn("leaf_missing_all", codes(html))
        self.assertNotIn("leaf_missing_partial", codes(html))

    def test_nested_leaf_ancestor_counts(self):
        html = "<section leaf=\"\"><p><span><strong>嵌套在 leaf 祖先下</strong></span></p></section>"
        self.assertNotIn("leaf_missing_all", codes(html))
        self.assertNotIn("leaf_missing_partial", codes(html))


class ExemptionTests(unittest.TestCase):
    """Reverse tests: correct documents the checker must stay quiet about."""

    def test_svg_text_is_exempt_from_leaf_wrapping(self):
        html = (
            "<section><svg viewBox=\"0 0 680 200\">"
            "<text x=\"10\" y=\"20\">图形里的中文标题</text>"
            "</svg></section>"
        )
        self.assertNotIn("leaf_missing_all", codes(html))

    def test_svg_internal_id_is_not_flagged(self):
        html = (
            "<section><svg viewBox=\"0 0 10 10\">"
            "<defs><marker id=\"arrowhead\"><polygon points=\"0 0,8 3,0 6\"/></marker></defs>"
            "</svg></section>"
        )
        self.assertNotIn("id_attr", codes(html))

    def test_code_block_halfwidth_punctuation_is_exempt(self):
        html = (
            "<section style=\"font-family:monospace;\">"
            "<p style=\"margin:0;\"><span leaf=\"\">const a = 1, b = 2;</span></p>"
            "</section>"
        )
        self.assertNotIn("halfwidth_punct", codes(html))

    def test_prose_halfwidth_punctuation_is_flagged(self):
        html = "<p><span leaf=\"\">今天天气不错,我们出去走走。</span></p>"
        self.assertIn("halfwidth_punct", codes(html))

    def test_html_comment_does_not_trigger_css_rules(self):
        html = (
            "<!-- 说明: 这里提到 float:left 只是举例 -->"
            "<section><p><span leaf=\"\">正文内容。</span></p></section>"
        )
        self.assertNotIn("css_float", codes(html))

    def test_max_width_is_not_confused_with_width_100(self):
        html = "<img src=\"https://mmbiz.qpic.cn/a.png\" style=\"max-width:100%;height:auto;\">"
        self.assertNotIn("img_width_100", codes(html))

    def test_px_line_height_is_not_range_checked(self):
        html = "<section style=\"line-height:28px;\"><span leaf=\"\">1</span></section>"
        self.assertNotIn("line_height_out_of_range", codes(html))

    def test_clean_document_produces_no_findings(self):
        html = (
            "<section style=\"max-width:100%;box-sizing:border-box;font-size:15px;line-height:1.8;\">"
            "<h2 style=\"font-size:18px;\"><span leaf=\"\">小节标题</span></h2>"
            "<p style=\"margin:0 0 16px 0;\"><span leaf=\"\">这是一段正确包裹的正文，标点也是全角的。</span></p>"
            "<img src=\"https://mmbiz.qpic.cn/mmbiz_png/x/0\" style=\"max-width:100%;height:auto;display:block;\" />"
            "</section>"
        )
        self.assertEqual(analyze(html), [])


class ImageHostTests(unittest.TestCase):
    def test_non_wechat_host_is_blocking(self):
        findings = {f.code: f for f in analyze(
            "<img src=\"https://example.com/a.png\" style=\"max-width:100%;\">"
        )}
        self.assertIn("image_host_not_wechat", findings)
        self.assertEqual(findings["image_host_not_wechat"].severity, "warn_blocking")

    def test_wechat_hosts_pass(self):
        for host in ("mmbiz.qpic.cn", "mmbiz.qlogo.cn", "wx.qlogo.cn", "thirdwx.qlogo.cn"):
            with self.subTest(host=host):
                html = f"<img src=\"https://{host}/a.png\" style=\"max-width:100%;\">"
                self.assertNotIn("image_host_not_wechat", codes(html))

    def test_placeholder_source_is_not_flagged(self):
        html = "<img src=\"IMAGE_URL\" style=\"max-width:100%;\">"
        self.assertNotIn("image_host_not_wechat", codes(html))

    def test_base64_source_is_not_flagged(self):
        html = "<img src=\"data:image/png;base64,iVBORw0KGgo=\" style=\"max-width:100%;\">"
        self.assertNotIn("image_host_not_wechat", codes(html))


class SeverityTests(unittest.TestCase):
    def test_every_finding_carries_a_known_severity(self):
        known = {"error", "warn_blocking", "warn_allowable", "info"}
        html = (
            "<style>.a{}</style><div class=\"x\" style=\"display:grid;float:left;gap:8px;\">"
            "<p>未包裹的中文,还带半角逗号。</p>"
            "<img src=\"https://example.com/a.png\" style=\"width:100%;\">"
            "</div>"
        )
        findings = analyze(html)
        self.assertTrue(findings)
        for finding in findings:
            self.assertIn(finding.severity, known)
            self.assertTrue(finding.suggestion)
            self.assertGreater(finding.count, 0)

    def test_only_allowable_severity_can_be_waived(self):
        from wechat_compliance_check import ALLOWABLE_SEVERITY
        html = (
            "<div class=\"x\" style=\"gap:8px;display:grid;\">"
            "<p>未包裹的中文,半角逗号。</p>"
            "</div>"
        )
        waivable = {f.code for f in analyze(html) if f.severity == ALLOWABLE_SEVERITY}
        self.assertIn("css_gap", waivable)
        # grid and leaf problems are never waivable.
        self.assertNotIn("css_grid", waivable)
        self.assertNotIn("leaf_missing_all", waivable)


class ComponentLibraryBaselineTests(unittest.TestCase):
    """The component library must comply with the rules it teaches."""

    def test_every_html_block_in_components_md_is_clean(self):
        import re

        source = (REPO_ROOT / "references" / "components.md").read_text(encoding="utf-8")
        blocks = re.findall(r"```html\n(.*?)```", source, re.S)
        self.assertGreater(len(blocks), 5, "component blocks were not extracted")

        offenders = []
        for index, block in enumerate(blocks, 1):
            blocking = [
                f.code for f in analyze(block)
                if f.severity in ("error", "warn_blocking")
            ]
            if blocking:
                offenders.append((index, blocking))
        self.assertEqual(offenders, [], f"blocking findings in components.md: {offenders}")

    def test_component_library_has_no_gap(self):
        import re

        source = (REPO_ROOT / "references" / "components.md").read_text(encoding="utf-8")
        blocks = re.findall(r"```html\n(.*?)```", source, re.S)
        offenders = [i for i, b in enumerate(blocks, 1) if "css_gap" in codes(b)]
        self.assertEqual(offenders, [], f"gap found in component blocks: {offenders}")


class SourceLintTests(unittest.TestCase):
    """Source lint: every ```html snippet in references/ must be compliant."""

    def test_all_reference_snippets_are_clean(self):
        from source_lint import lint_markdown

        offenders = []
        for md in sorted((REPO_ROOT / "references").rglob("*.md")):
            for index, blocking in lint_markdown(md):
                offenders.append((md.name, index, blocking))
        self.assertEqual(offenders, [], f"blocking snippets in references/: {offenders}")

    def test_counter_example_blocks_are_skipped(self):
        import tempfile

        from source_lint import lint_markdown

        with tempfile.TemporaryDirectory() as tmp:
            marked = Path(tmp) / "marked.md"
            marked.write_text(
                "```html\n<!-- \u274c \u9519\u8bef\u793a\u4f8b -->\n"
                '<p style="font-size:15px;">\u6ca1\u6709leaf\u5305\u88f9\u7684\u4e2d\u6587</p>\n```\n',
                encoding="utf-8",
            )
            self.assertEqual(lint_markdown(marked), [])

            plain = Path(tmp) / "plain.md"
            plain.write_text(
                "```html\n"
                '<p style="font-size:15px;">\u6ca1\u6709leaf\u5305\u88f9\u7684\u4e2d\u6587</p>\n```\n',
                encoding="utf-8",
            )
            self.assertEqual(len(lint_markdown(plain)), 1)


class LeafAutofixTests(unittest.TestCase):
    """leaf_autofix must wrap bare CJK nodes, be idempotent, skip teaching blocks."""

    SAMPLE = (
        "```html\n"
        '<p style="font-size:15px;">\u88f8\u4e2d\u6587\u6b63\u6587</p>\n'
        "```\n"
        "```html\n"
        "<!-- \u274c \u53cd\u4f8b\uff1a\u4e0d\u5305\u88f9 -->\n"
        "<p>\u53cd\u4f8b\u4e2d\u6587</p>\n"
        "```\n"
    )

    def _write(self, path: Path) -> None:
        path.write_text(self.SAMPLE, encoding="utf-8")

    def test_wraps_and_is_idempotent_and_skips_counter_examples(self):
        import tempfile

        from leaf_autofix import process_file

        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / "sample.md"
            self._write(md)

            self.assertTrue(process_file(md, False))   # first pass: fixed
            fixed = md.read_text(encoding="utf-8")
            self.assertIn('<span leaf="">\u88f8\u4e2d\u6587\u6b63\u6587</span>', fixed)
            self.assertIn("<p>\u53cd\u4f8b\u4e2d\u6587</p>", fixed)  # \u274c block untouched

            self.assertFalse(process_file(md, False))  # second pass: idempotent

            self.assertFalse(process_file(md, True))   # check-only reports clean

            # fixed output must satisfy the compliance checker
            import re

            block = re.findall(r"```html\n(.*?)```", fixed, re.S)[0]
            blocking = [f.code for f in analyze(block)
                        if f.severity in ("error", "warn_blocking")]
            self.assertEqual(blocking, [])


if __name__ == "__main__":
    unittest.main()
