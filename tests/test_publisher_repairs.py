import tempfile
import unittest
from pathlib import Path

from toolkit.briefs import build_article_brief
from toolkit.cli import cmd_preview
from toolkit.text_encoding import decode_text


class PublisherRepairTests(unittest.TestCase):
    def test_decodes_utf8_bom_utf16_and_gbk(self):
        self.assertEqual(decode_text("中文🙂".encode("utf-8")), "中文🙂")
        self.assertEqual(decode_text(b"\xef\xbb\xbf" + "中文".encode("utf-8")), "中文")
        self.assertEqual(decode_text(b"\xff\xfe" + "中文".encode("utf-16-le")), "中文")
        self.assertEqual(decode_text(bytes.fromhex("d6d0cec4")), "中文")

    def test_preview_contains_html_clipboard_and_plain_text_fallback(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "article.md"
            source.write_text("---\ntitle: 测试\n---\n正文", encoding="utf-8")
            args = type("Args", (), {"file": str(source), "theme": None, "output": None})()
            self.assertEqual(cmd_preview(args), 0)
            preview = source.with_name("article_preview.html").read_text(encoding="utf-8")
            self.assertIn("'text/html': new Blob([html]", preview)
            self.assertIn("'text/plain': new Blob([plain]", preview)
            self.assertIn("document.execCommand('copy')", preview)
            self.assertNotIn("'text/plain': new Blob([html]", preview)

    def test_brief_reads_gbk_article(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "article.md"
            source.write_bytes("---\ntitle: 中文\n---\n正文".encode("gb18030"))
            brief = build_article_brief(source)
            self.assertEqual(brief.metadata["title"], "中文")
            self.assertIn("正文", brief.facts[0]["text"])


if __name__ == "__main__":
    unittest.main()
