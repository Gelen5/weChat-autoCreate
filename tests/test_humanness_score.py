import importlib.util
import json
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "humanness_score.py"
SPEC = importlib.util.spec_from_file_location("humanness_score", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class HumannessTests(unittest.TestCase):
    def test_host_score_loader_accepts_inline_json(self):
        result = MODULE.load_host_score('{"score":82,"reason":"具体场景"}')
        self.assertEqual(result["score"], 82)

    def test_host_score_loader_rejects_non_object(self):
        with self.assertRaises(ValueError):
            MODULE.load_host_score('[82]')

    def test_host_l3_is_scored_and_has_status(self):
        result = MODULE.calculate_llm_layer("这是一段有具体细节的文章。", host_score={
            "score": 82,
            "reason": "有明确判断",
            "dimensions": {"originality": 80, "specificity": 85, "emotion": 78},
        })
        self.assertEqual(result["score"], 82)
        self.assertEqual(result["details"]["status"], "scored")
        self.assertEqual(result["details"]["grader"], "host-model")

    def test_missing_l3_is_explicit_not_silent(self):
        result = MODULE.calculate_llm_layer("短文")
        self.assertEqual(result["details"]["status"], "unavailable")
        self.assertEqual(result["details"]["effective_fallback"], 50)

    def test_repair_plan_is_actionable(self):
        stat = {"details": {"sent_stddev": 1, "sent_range": 3, "ttr": 0.2}}
        pattern = {"details": {"forbidden_words_count": 1, "structure_score": 70, "warm_word_count": 0}}
        llm = {"details": {"status": "unavailable"}}
        actions = MODULE.build_repair_plan(stat, pattern, llm)
        self.assertGreaterEqual(len(actions), 4)
        self.assertTrue(all("action" in item and "reason" in item for item in actions))


if __name__ == "__main__":
    unittest.main()
