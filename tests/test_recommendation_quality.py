import tempfile
import unittest
from pathlib import Path

from toolkit.contracts import SourceLedger, SourceRecord
from toolkit.recommendation_quality import check_content, check_generated_asset, repair_content


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


if __name__ == "__main__":
    unittest.main()
