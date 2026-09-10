"""Deterministic orchestration for the host-assisted long-form workflow."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Dict, Iterable

from .article_state import ARTICLE_NODES, ArticleState
from .recommendation_quality import check_content


NODE_REFERENCES = {
    "intent": ["references/article-state.md"],
    "topic": ["references/content-workflow.md"],
    "research": ["references/evidence-protocol.md"],
    "strategy": ["references/author-model.md", "references/content-workflow.md"],
    "draft": ["references/writing-protocol.md"],
    "review": ["references/quality-protocol.md"],
    "delivery": ["references/visual-prompts.md", "references/mobile-layout-quality.md", "references/leaf-and-compliance.md"],
}


class WorkflowBlocked(RuntimeError):
    pass


def new_article_state(user_request: str, *, mode: str = "interactive", topic: str = "",
                      audience: str = "", goal: str = "", timely: bool = False) -> ArticleState:
    task_id = hashlib.sha256(user_request.encode("utf-8")).hexdigest()[:12]
    state = ArticleState(task_id=task_id, user_request=user_request.strip(), mode=mode, topic=topic.strip())
    if audience:
        state.audience = {"description": audience.strip(), "status": "user_provided"}
    if goal:
        state.intent["goal"] = goal.strip()
    state.intent["timeliness"] = "time_sensitive" if timely else "evergreen_or_unspecified"
    state.log("created", "ArticleState initialized")
    return state


def _host_request(state: ArticleState, node: str, purpose: str, output_contract: Dict[str, Any]) -> None:
    item = state.nodes[node]
    item.status = "awaiting_host"
    item.message = purpose
    item.request = {
        "purpose": purpose,
        "read": NODE_REFERENCES[node],
        "state_fields": _relevant_state(state, node),
        "output_contract": output_contract,
        "rules": [
            "只使用状态中可追溯的事实；推断和假设必须显式标记",
            "返回 JSON 对象；不要静默补全缺失的关键事实",
        ],
    }


def _relevant_state(state: ArticleState, node: str) -> Dict[str, Any]:
    shared = {"user_request": state.user_request, "intent": state.intent, "audience": state.audience,
              "topic": state.topic, "angle": state.angle}
    if node in {"strategy", "draft", "review", "delivery"}:
        shared["author_profile"] = state.author_profile.__dict__
        shared["evidence_pack"] = state.evidence_pack.__dict__
    if node in {"draft", "review", "delivery"}:
        shared["outline"] = state.outline
        shared["writing_strategy"] = state.writing_strategy
    if node in {"review", "delivery"}:
        shared["selected_title"] = state.selected_title
        shared["draft"] = state.draft
    return shared


def _finish(state: ArticleState, node: str, message: str) -> None:
    from .contracts import utc_now
    item = state.nodes[node]
    item.status = "passed"
    item.completed_at = utc_now()
    item.message = message
    item.request = {}
    state.log(f"node:{node}:passed", message)


def _block(state: ArticleState, node: str, message: str) -> None:
    item = state.nodes[node]
    item.status = "blocked"
    item.message = message
    state.log(f"node:{node}:blocked", message)
    raise WorkflowBlocked(message)


def run_node(state: ArticleState, node: str, *, output_dir: str | Path | None = None) -> ArticleState:
    if node not in ARTICLE_NODES:
        raise ValueError(f"Unknown article node: {node}")
    index = ARTICLE_NODES.index(node)
    for prior in ARTICLE_NODES[:index]:
        if state.nodes[prior].status != "passed":
            _block(state, node, f"前置节点 {prior} 尚未通过")

    if node == "intent":
        if not state.user_request:
            _block(state, node, "缺少用户请求")
        if not state.intent.get("goal") or not state.audience:
            _host_request(state, node, "识别写作目的、读者、内容类型、时效和转化目标", {
                "intent": "object", "audience": "object", "topic": "string", "assumptions": "array"
            })
        else:
            state.topic = state.topic or state.user_request
            _finish(state, node, "意图与受众已结构化")
    elif node == "topic":
        if not state.angle:
            _host_request(state, node, "选择具体、有素材支撑且符合作者资格的文章角度", {
                "topic": "string", "angle": "string", "title_candidates": "array<object>"
            })
        else:
            _finish(state, node, "主题与角度已确定")
    elif node == "research":
        key_claims = [c for c in state.evidence_pack.claims if c.materiality == "key" and c.kind in {"fact", "public_case", "author_experience"}]
        unsupported = [c.claim_id for c in key_claims if c.status not in {"verified", "user_provided", "illustrative"} or (c.kind in {"fact", "public_case"} and not c.source_ids)]
        if unsupported:
            _block(state, node, "关键主张缺少可追溯证据: " + ", ".join(unsupported))
        if state.evidence_pack.research_status == "not_started":
            _host_request(state, node, "建立来源账本和主张账本；优先一手、最新、可交叉核验的材料", {
                "evidence_pack": "object with sources, claims, research_status, limitations"
            })
        elif state.evidence_pack.research_status == "failed" and state.intent.get("timeliness") == "time_sensitive":
            _block(state, node, "时效性内容研究失败，不能用模型记忆替代")
        else:
            if state.evidence_pack.research_status != "complete":
                state.degradations.append({"node": node, "reason": "研究材料不完整", "user_visible": True})
            _finish(state, node, "证据包已建立")
    elif node == "strategy":
        if not state.outline or not state.writing_strategy:
            _host_request(state, node, "根据读者认知、证据形态和作者判断设计文章结构；框架只是工具", {
                "outline": "array<object>", "writing_strategy": "object", "selected_title": "string"
            })
        else:
            _finish(state, node, "结构与写作策略已确定")
    elif node == "draft":
        if not state.draft:
            _host_request(state, node, "直接生成有作者、有证据、有取舍的第一稿，不做模板文再全文洗稿", {
                "draft": "markdown string", "selected_title": "string", "used_claim_ids": "array<string>"
            })
        else:
            _finish(state, node, "正文第一稿已生成")
    elif node == "review":
        from .content_quality import assess_soft_quality
        sources = state.evidence_pack.sources
        report = check_content(state.selected_title or state.topic, state.draft, sources=sources, strict=True)
        state.quality_report = {"hard_gate": report, "soft_quality": assess_soft_quality(state)}
        if report["blocked"]:
            state.revision_plan = [{"source": "hard_gate", "finding": finding} for finding in report["findings"]]
            _block(state, node, "正文硬门禁未通过")
        if not state.reader_simulation:
            _host_request(state, node, "模拟目标读者、知情者、怀疑者和快速浏览者，输出局部修订计划", {
                "reader_simulation": "array<object>", "revision_plan": "array<object>", "revised_draft": "optional markdown string"
            })
        else:
            _finish(state, node, "读者模拟和质量复核已完成")
    elif node == "delivery":
        from .converter import MarkdownConverter
        if not state.visual_plan:
            state.visual_plan = [{"role": "cover", "purpose": "呈现标题的核心信息增量", "required": True}]
        if not output_dir:
            _block(state, node, "交付节点需要 output_dir")
        target_dir = Path(output_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        markdown_path = target_dir / "article.md"
        markdown_path.write_text(state.draft, encoding="utf-8")
        html_path = target_dir / "article.html"
        html_path.write_text(MarkdownConverter().convert(state.draft), encoding="utf-8")
        state.formatted_output = str(html_path)
        state.writing_strategy["markdown_output"] = str(markdown_path)
        _finish(state, node, "已生成 Markdown 与微信 HTML；发布继续使用最终确定性门禁")
    return state


def apply_host_result(state: ArticleState, node: str, result: Dict[str, Any]) -> ArticleState:
    if node not in ARTICLE_NODES:
        raise ValueError(f"Unknown article node: {node}")
    allowed = {
        "intent": ("intent", "audience", "topic"),
        "topic": ("topic", "angle", "title_candidates"),
        "research": ("evidence_pack",),
        "strategy": ("outline", "writing_strategy", "selected_title"),
        "draft": ("draft", "selected_title"),
        "review": ("reader_simulation", "revision_plan", "revised_draft"),
        "delivery": ("visual_plan",),
    }[node]
    for key in allowed:
        if key not in result:
            continue
        value = result[key]
        if key == "revised_draft":
            state.draft = value
        elif key == "evidence_pack":
            from .article_state import ArticleState as _State
            payload = state.to_dict()
            payload["evidence_pack"] = value
            state.evidence_pack = _State.from_dict(payload).evidence_pack
        else:
            setattr(state, key, value)
    state.nodes[node].status = "pending"
    state.nodes[node].request = {}
    state.log(f"node:{node}:host_result", "宿主结果已合并并等待确定性复检")
    return state


def run_until_wait(state: ArticleState, *, output_dir: str | Path | None = None) -> ArticleState:
    for node in ARTICLE_NODES:
        if state.nodes[node].status == "passed":
            continue
        run_node(state, node, output_dir=output_dir)
        if state.nodes[node].status in {"awaiting_host", "blocked", "failed"}:
            break
    return state
