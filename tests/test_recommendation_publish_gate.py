import tempfile
import unittest
from pathlib import Path

from toolkit.publisher import Publisher
from toolkit.tie_tu import build_plan
from toolkit.tie_tu.publisher import TieTuPublisher


class _NoUploadAPI:
    def __init__(self):
        self.calls = 0

    def __getattr__(self, _name):
        def fail_if_called(*_args, **_kwargs):
            self.calls += 1
            raise AssertionError("quality gate must run before WeChat upload")
        return fail_if_called


class RecommendationPublishGateTests(unittest.TestCase):
    def test_long_form_blocks_before_upload(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            article = Path(temp_dir) / "article.md"
            article.write_text("---\ntitle: short article\n---\nToo short.", encoding="utf-8")
            publisher = Publisher.__new__(Publisher)
            publisher.config = type("Config", (), {"get": lambda self, key, default=None: default})()
            publisher.api = _NoUploadAPI()
            publisher.converter = None
            self.assertIsNone(publisher.publish(str(article)))
            self.assertEqual(publisher.api.calls, 0)

    def test_tie_tu_blocks_before_upload(self):
        plan = build_plan("city", "city change", image_count=1, portrait_mode="off")
        publisher = TieTuPublisher(api=_NoUploadAPI())
        with self.assertRaisesRegex(ValueError, "推荐质量"):
            publisher.publish_draft(plan)
        self.assertEqual(publisher.api.calls, 0)


if __name__ == "__main__":
    unittest.main()
