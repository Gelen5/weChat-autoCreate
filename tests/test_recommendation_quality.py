import tempfile
import unittest
from pathlib import Path

from toolkit.contracts import SourceLedger, SourceRecord
from toolkit.recommendation_quality import check_article_file, check_content, check_generated_asset, repair_content


class RecommendationQualityTests(unittest.TestCase):
    def test_concrete_article_passes_strict_gate(self):
        body = "This market observation records a field visit in August 2026. I visited 3 markets and recorded 12 stalls, comparing prices and package dates. The notes include origins, storage advice, and receipts. Clearly labelled stalls made comparison easier. My judgement is that transparent information matters more than the lowest price. This is a local observation, not a universal claim. Shoppers can check labels, ask about storage, and compare prices before buying."
        report = check_content("market observation", body, sources=SourceLedger([SourceRecord("s1", kind="web", status="verified")]), strict=True)
        self.assertFalse(report["blocked"])

    def test_unsupported_claim_is_blocked(self):
        claim = "".join(chr(code) for code in (30740, 31350, 34920, 26126, 36825, 31181, 26041, 27861, 19968, 23450, 33021, 27835, 22909, 22833, 30496, 12290))
        report = check_content("health claim", claim, strict=True)
        self.assertTrue(report["blocked"])
        self.assertIn("unsupported_claim", [item["code"] for item in report["findings"]])

    def test_near_duplicate_is_blocked(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history = Path(temp_dir) / "history"
            history.mkdir()
            text = "A city street changed from old stalls to new shops in 2026, with the same local memories."
            (history / "old.md").write_text(text, encoding="utf-8")
            report = check_content("city street change", text, history_dir=history, strict=True)
            self.assertTrue(report["blocked"])
            self.assertIn("near_duplicate", [item["code"] for item in report["findings"]])

    def test_empty_history_is_explicit(self):
        report = check_content("city record", "A concrete scene in 2026 records 3 changes in a local street.")
        self.assertEqual(report["history"]["coverage"], "unknown")

    def test_safe_repair_does_not_invent_facts(self):
        title = "".join(chr(code) for code in (33756, 24066, 22330, 26368, 33039, 30340, 53, 31181, 33756))
        report = check_content(title, "A 2026 record lists 5 shopping checks.")
        repaired = repair_content(title, "A 2026 record lists 5 shopping checks.", report)
        self.assertNotEqual(repaired["title"], title)
        self.assertEqual(repaired["body"], "A 2026 record lists 5 shopping checks.")

    def test_tie_tu_empty_copy_requires_revision(self):
        report = check_content("city change", "", kind="tie_tu", strict=True)
        self.assertTrue(report["blocked"])
        self.assertIn("insufficient_tie_tu_copy", [item["code"] for item in report["findings"]])

    def test_generated_asset_gate_blocks_missing_asset(self):
        report = check_generated_asset("missing-generated-image.png")
        self.assertTrue(report["blocked"])

    def test_negated_advice_with_yiding_is_not_an_unsupported_fact(self):
        body = "选择工具时不要因为别人推荐，就觉得自己一定要买。先看真实需求和预算，再做决定。" * 4
        report = check_content("选择工具前先看需求", body)
        self.assertNotIn("unsupported_claim", [item["code"] for item in report["findings"]])

    def test_search_specific_image_text_check_is_opt_in(self):
        body = "![一](https://example.com/1.png)\n![二](https://example.com/2.png)\n![三](https://example.com/3.png)\n三张步骤图。"
        ordinary = check_content("步骤图", body)
        search = check_content("步骤图", body, search_intent={"enabled": True, "query": "怎么操作"})
        self.assertNotIn("image_only_search_page", [item["code"] for item in ordinary["findings"]])
        self.assertIn("image_only_search_page", [item["code"] for item in search["findings"]])

    def test_hidden_text_and_keyword_stuffing_are_located(self):
        report = check_content("本地服务", '<span style="display:none">隐藏词</span> 深圳搬家深圳搬家深圳搬家深圳搬家')
        self.assertTrue(report["blocked"])
        self.assertIn("hidden_text", [item["code"] for item in report["findings"]])
        self.assertIn("keyword_stuffing", [item["code"] for item in report["findings"]])

    def test_gated_answer_and_fake_entry_are_flagged(self):
        report = check_content("官方报名入口", "本文不是官方报名入口。想看完整名单请关注公众号，我们会私信发送。")
        codes = [item["code"] for item in report["findings"]]
        self.assertIn("misleading_entry_title", codes)
        self.assertIn("answer_gated", codes)

    def test_unchecked_assets_are_reported(self):
        report = check_content("观察", "2026年观察三处街区。")
        self.assertEqual(report["assets"]["coverage"], "not_checked")

    def test_css_example_does_not_trigger_hidden_text(self):
        report = check_content("CSS教程", "```html\n<span style=\"display:none\">例子</span>\n```\n这里解释这段代码的用途。")
        self.assertNotIn("hidden_text", [item["code"] for item in report["findings"]])

    def test_markdown_import_checks_search_intent_and_missing_image(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            article = Path(temp_dir) / "article.md"
            article.write_text('---\ntitle: "步骤图"\nsearch_intent:\n  enabled: true\n  query: "怎么操作"\n---\n![一](missing.png)\n![二](https://example.com/2.png)\n![三](https://example.com/3.png)\n三张步骤图。', encoding="utf-8")
            report = check_article_file(article, strict=True)
            codes = [item["code"] for item in report["findings"]]
            self.assertIn("image_only_search_page", codes)
            self.assertIn("missing_asset", codes)
            self.assertEqual(report["assets"]["checked"], 1)

    def test_markdown_import_checks_local_link_without_fetching_remote(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            article = Path(temp_dir) / "article.md"
            article.write_text("# 操作说明\n\n[本地附件](missing.pdf) 与 [官方说明](https://example.com/guide)。", encoding="utf-8")
            report = check_article_file(article, strict=True)
            self.assertIn("missing_local_link", [item["code"] for item in report["findings"]])
            self.assertEqual(report["links"]["checked"], 1)


if __name__ == "__main__":
    unittest.main()
