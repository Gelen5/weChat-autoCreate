import json
import tempfile
import unittest
from pathlib import Path

from toolkit.briefs import build_article_brief
from toolkit.contracts import ContentBrief, SourceRecord
from toolkit.tie_tu import (add_source, analyze_reference_image, build_plan,
                             generate_batch, generate_pilot, record_batch,
                             record_pilot, set_approval, validate_plan)


class SharedContractTests(unittest.TestCase):
    def test_tie_tu_has_shared_protocol_and_legacy_round_trip(self):
        plan = build_plan("城市", "长沙老街变化", image_count=2)
        self.assertEqual(plan.content_brief.mode, "tie_tu")
        self.assertIn("card_plan", plan.approval_state.stages)
        self.assertEqual(plan.generation_state.batch_status, "pending")
        add_source(plan, "ai-1", "ai", title="AI生成底图", status="illustrative")
        set_approval(plan, "card_plan", "approved")
        self.assertEqual(plan.source_ledger.records[0].source_id, "ai-1")
        self.assertEqual(plan.approval_state.stages["card_plan"], "approved")
        self.assertTrue(validate_plan(plan)["ok"])

    def test_generation_state_tracks_pilot_and_batch(self):
        plan = build_plan("生活方式", "复古美女", image_count=2)
        with tempfile.TemporaryDirectory() as temp_dir:
            image = Path(temp_dir) / "pilot.png"
            image.write_bytes(b"placeholder")
            record_pilot(plan, 1, str(image))
            self.assertEqual(plan.generation_state.pilot_status, "generated")
            record_batch(plan, "completed")
            self.assertEqual(plan.generation_state.batch_status, "completed")
            self.assertEqual(plan.approval_state.stages["batch_generation"], "approved")

    def test_article_brief_extracts_sources(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "article.md"
            path.write_text("---\ntitle: 测试文章\naudience: AI从业者\n---\n正文 https://example.com/source", encoding="utf-8")
            brief = build_article_brief(path)
            self.assertEqual(brief.mode, "long_form")
            self.assertEqual(brief.metadata["title"], "测试文章")
            self.assertEqual(brief.source_ledger.records[0].url, "https://example.com/source")

    def test_image_reverse_analysis_and_generation_gates(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow unavailable")
        plan = build_plan("生活方式", "复古美女", image_count=1)
        with tempfile.TemporaryDirectory() as temp_dir:
            image_path = Path(temp_dir) / "reference.png"
            Image.new("RGB", (300, 400), (180, 120, 90)).save(image_path)
            analysis = analyze_reference_image(image_path)
            self.assertEqual(analysis["dimensions"], {"width": 300, "height": 400})
            self.assertEqual(analysis["orientation"], "portrait")

            class FakeGenerator:
                def generate(self, prompt, provider=None, size=None, output_dir=None):
                    result = Path(output_dir) / "generated.png"
                    result.write_bytes(b"image")
                    return str(result)

            with self.assertRaises(RuntimeError):
                generate_pilot(plan, temp_dir, generator=FakeGenerator())
            set_approval(plan, "card_plan", "approved")
            generated = generate_pilot(plan, temp_dir, generator=FakeGenerator())
            self.assertTrue(generated)
            with self.assertRaises(RuntimeError):
                generate_batch(plan, temp_dir, generator=FakeGenerator())
            set_approval(plan, "pilot_image", "approved")
            self.assertEqual(generate_batch(plan, temp_dir, generator=FakeGenerator()), 1)


if __name__ == "__main__":
    unittest.main()
