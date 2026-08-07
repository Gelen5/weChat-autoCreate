import json
import tempfile
import unittest
from pathlib import Path

from toolkit.tie_tu import build_plan, recommend_types, render_preview, validate_plan


class TieTuWorkflowTests(unittest.TestCase):
    def test_city_topic_prefers_city_change(self):
        ranked = recommend_types("城市生活", "深圳老街变化")
        self.assertEqual(ranked[0]["type"], "city_change")

    def test_build_plan_has_stable_schema(self):
        plan = build_plan("AI工具", "AI写作流程", image_count=5)
        self.assertEqual(plan.mode, "tie_tu")
        self.assertEqual(plan.ratio, "3:4")
        self.assertEqual(len(plan.cards), 5)
        self.assertEqual([card.index for card in plan.cards], [1, 2, 3, 4, 5])

    def test_count_boundaries(self):
        with self.assertRaises(ValueError):
            build_plan("AI", "主题", image_count=2)
        with self.assertRaises(ValueError):
            build_plan("AI", "主题", image_count=21)

    def test_preview_and_validation(self):
        plan = build_plan("职场", "新人入职清单", content_type="list", image_count=3)
        report = validate_plan(plan)
        self.assertTrue(report["ok"])
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "preview.html"
            render_preview(plan, output)
            html = output.read_text(encoding="utf-8")
            self.assertIn("贴图号独立预览", html)
            self.assertEqual(html.count('class="card"'), 3)


if __name__ == "__main__":
    unittest.main()
