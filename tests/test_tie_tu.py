import json
import tempfile
import unittest
from pathlib import Path
from toolkit.tie_tu.models import load_plan

from toolkit.tie_tu import build_plan, recommend_types, render_preview, render_portrait_prompt, validate_plan


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
        plan = build_plan("生活方式", "复古美女肖像", image_count=1)
        self.assertTrue(plan.portrait_enabled)
        self.assertEqual(plan.portrait_route, "retro-hongkong")
        self.assertIn("watermark", plan.cards[0].portrait_spec["negative_prompt"])
        self.assertIn("same fictional adult model", plan.model_bible["continuity"])
        self.assertIn("3:4 vertical", render_portrait_prompt(plan.cards[0].portrait_spec))
        self.assertEqual(len(build_plan("AI", "主题", image_count=21).cards), 21)
        with self.assertRaises(ValueError):
            build_plan("AI", "主题", image_count=0)

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

    def test_portrait_can_be_forced_or_disabled(self):
        forced = build_plan("摄影", "人物故事", image_count=2, portrait_mode="required")
        self.assertTrue(validate_plan(forced)["ok"])
        disabled = build_plan("生活方式", "复古美女", image_count=2, portrait_mode="off")
        self.assertFalse(disabled.portrait_enabled)
        self.assertEqual(disabled.cards[0].portrait_spec, {})

    def test_loading_legacy_portrait_plan_enhances_it(self):
        legacy = {
            "mode": "tie_tu",
            "industry": "生活方式",
            "topic": "复古美女旧时光",
            "title": "复古美女旧时光",
            "cards": [{
                "index": 1,
                "role": "cover",
                "purpose": "封面",
                "visual_subject": "复古美女在老街回头",
                "composition": "3:4 竖幅",
            }],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "legacy.json"
            path.write_text(json.dumps(legacy, ensure_ascii=False), encoding="utf-8")
            loaded = load_plan(path)
            self.assertTrue(loaded.portrait_enabled)
            self.assertEqual(loaded.portrait_route, "retro-hongkong")


if __name__ == "__main__":
    unittest.main()
