import json
import tempfile
import unittest
from pathlib import Path

from toolkit.article_state import ClaimRecord, SourceRecord, load_article_state, save_article_state
from toolkit.article_workflow import WorkflowBlocked, apply_host_result, new_article_state, run_node, run_until_wait
from toolkit.benchmark import compare_directories, measure
from toolkit.converter import MarkdownConverter
from toolkit.leaf import wrap_cjk_leaf


class ArticleWorkflowTests(unittest.TestCase):
    def test_state_round_trip_and_host_request(self):
        state = new_article_state("写本地小店变化", audience="本地读者", goal="建立信任")
        run_until_wait(state)
        self.assertEqual(state.nodes["intent"].status, "passed")
        self.assertEqual(state.nodes["topic"].status, "awaiting_host")
        self.assertEqual(state.nodes["topic"].request["read"], ["references/content-workflow.md"])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.json"
            save_article_state(state, path)
            restored = load_article_state(path)
        self.assertEqual(restored.task_id, state.task_id)
        self.assertEqual(restored.nodes["topic"].status, "awaiting_host")

    def test_time_sensitive_research_failure_blocks(self):
        state = new_article_state("评论今天发布的平台规则", audience="创作者", goal="解释变化", timely=True)
        state.intent.update({"content_type": "commentary"})
        state.angle = "规则对小创作者的实际影响"
        state.nodes["intent"].status = "passed"
        state.nodes["topic"].status = "passed"
        state.evidence_pack.research_status = "failed"
        with self.assertRaises(WorkflowBlocked):
            run_node(state, "research")
        self.assertEqual(state.nodes["research"].status, "blocked")

    def test_key_fact_requires_traceable_source(self):
        state = new_article_state("解释一项研究", audience="普通读者", goal="解释")
        state.nodes["intent"].status = "passed"
        state.nodes["topic"].status = "passed"
        state.evidence_pack.research_status = "complete"
        state.evidence_pack.claims.append(ClaimRecord("c1", "样本增长30%", kind="fact", status="verified", materiality="key"))
        with self.assertRaises(WorkflowBlocked):
            run_node(state, "research")

    def test_host_result_merges_evidence_pack(self):
        state = new_article_state("解释一项研究")
        apply_host_result(state, "research", {"evidence_pack": {
            "sources": {"records": [{"source_id": "s1", "kind": "web", "url": "https://example.com", "status": "verified"}]},
            "claims": [{"claim_id": "c1", "text": "公开事实", "kind": "fact", "source_ids": ["s1"], "status": "verified", "materiality": "key"}],
            "research_status": "complete", "limitations": []
        }})
        self.assertEqual(state.evidence_pack.sources.ids(), ["s1"])
        self.assertEqual(state.evidence_pack.claims[0].source_ids, ["s1"])

    def test_complete_state_delivers_markdown(self):
        state = new_article_state("街区老店为什么关闭", audience="本地读者", goal="解释")
        state.intent["content_type"] = "observation"
        state.angle = "从租金和客流变化解释老店关闭"
        state.evidence_pack.research_status = "complete"
        state.outline = [{"purpose": "给出现场与判断"}]
        state.writing_strategy = {"opening": "scene", "ending": "judgment"}
        state.selected_title = "街区老店为什么关闭"
        state.draft = ("# 街区老店为什么关闭\n\n2026年3月，这家开了12年的店贴出停业通知。店主给出的原因很具体：晚间客流减少，租金却没有下降。\n\n"
                       "这不是一句‘消费降级’能够解释的事。附近3个路口的业态在两年内换了一轮，留下来的店都缩短了营业时间。这里写的是现场观察，不把它冒充官方统计。\n\n"
                       "对本地读者来说，真正值得关注的是街区服务正在变少。判断一家老店为何关闭，需要把租金、客流和经营者选择分开看，也要承认目前没有完整行业数据。")
        state.reader_simulation = [{"reader": "target", "continue": True}]
        state.visual_plan = [{"role": "evidence", "purpose": "展示停业通知", "required": False}]
        for name in ("intent", "topic", "research", "strategy", "draft"):
            state.nodes[name].status = "passed"
        run_node(state, "review")
        with tempfile.TemporaryDirectory() as tmp:
            run_node(state, "delivery", output_dir=tmp)
            self.assertTrue(Path(state.formatted_output).exists())
        self.assertEqual(state.nodes["delivery"].status, "passed")

    def test_benchmark_reports_only_deterministic_regressions(self):
        with tempfile.TemporaryDirectory() as old_tmp, tempfile.TemporaryDirectory() as new_tmp:
            Path(old_tmp, "case.md").write_text("具体内容。", encoding="utf-8")
            Path(new_tmp, "case.md").write_text("综上所述。具体内容。", encoding="utf-8")
            report = compare_directories([{"id": "case", "type": "观点"}], old_tmp, new_tmp)
        self.assertEqual(report["regressions"][0]["metric"], "ai_pattern_hits")

    def test_converter_leaf_wrap_is_default_and_idempotent(self):
        rendered = MarkdownConverter().convert("# 中文标题\n\n中文正文。")
        self.assertIn('<span leaf="">中文标题</span>', rendered)
        self.assertEqual(wrap_cjk_leaf(rendered), rendered)


if __name__ == "__main__":
    unittest.main()
