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
        if any(word in goal.lower() for word in ("搜索", "搜一搜", "seo")):
            state.intent["search_intent"] = {"enabled": True}
    state.intent["timeliness"] = "time_sensitive" if timely else "evergreen_or_unspecified"
    state.log("created", "ArticleState initialized")
    return state


def _host_request(state: ArticleState, node: str, purpose: str, output_contract: Dict[str, Any]) -> None:
    item = state.nodes[node]
    item.status = "awaiting_host"
    item.message = purpose
    item.request = {
        "purpose": purpose,
        "read": NODE_REFERENCES[node] + (["references/seo-rules.md"] if state.intent.get("search_intent", {}).get("enabled") and node in {"topic", "strategy", "review"} else []),
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


def _local_assets(state: ArticleState, base_dir: str | Path | None = None) -> list[Path] | None:
    paths: list[Path] = []
    image_refs = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", state.draft)
    image_refs += re.findall(r"<img\b[^>]*\bsrc=[\"']([^\"']+)[\"']", state.draft, re.I)
    image_refs += [str(item["path"]) for item in state.visual_plan if item.get("path")]
    root = Path(state.intent.get("asset_base_dir") or base_dir) if state.intent.get("asset_base_dir") or base_dir else None
    for raw in image_refs:
        ref = raw.strip().split("#", 1)[0].split("?", 1)[0]
        if not ref or re.match(r"^(?:https?:|data:|//)", ref, re.I):
            continue
        path = Path(ref)
        if path.is_absolute():
            paths.append(path)
        elif root is not None:
            paths.append(root / path)
    return paths or None


def _local_links(state: ArticleState, base_dir: str | Path | None = None) -> list[Path] | None:
    root = Path(state.intent.get("asset_base_dir") or base_dir) if state.intent.get("asset_base_dir") or base_dir else None
    if root is None:
        return None
    refs = re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", state.draft)
    paths = [root / ref.split("#", 1)[0].split("?", 1)[0] for ref in refs
             if ref.strip() and not re.match(r"^(?:https?:|mailto:|tel:|#|//)", ref.strip(), re.I)]
    return paths or None


def _quality_report(state: ArticleState, *, base_dir: str | Path | None = None) -> Dict[str, Any]:
    return check_content(
        state.selected_title or state.topic, state.draft,
        sources=state.evidence_pack.sources,
        history_dir=state.intent.get("history_dir"),
        assets=_local_assets(state, base_dir),
        local_links=_local_links(state, base_dir),
        search_intent=state.intent.get("search_intent"),
        strict=True,
    )


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
            _host_request(state, node, "识别写作目的、读者、内容类型、时效和转化目标；仅当用户要求搜索流量时，在 intent.search_intent 中设 enabled=true", {
                "intent": "object with optional search_intent: {enabled, query, expected_answer}", "audience": "object", "topic": "string", "assumptions": "array"
            })
        else:
            state.topic = state.topic or state.user_request
            _finish(state, node, "意图与受众已结构化")
    elif node == "topic":
        search = state.intent.get("search_intent", {})
        if not state.angle or (search.get("enabled") and (not search.get("query") or not search.get("expected_answer"))):
            contract = {"topic": "string", "angle": "string", "title_candidates": "array<object>"}
            if state.intent.get("search_intent", {}).get("enabled"):
                contract["search_intent"] = "object with enabled=true, query=reader question, expected_answer=answer article can provide"
            _host_request(state, node, "选择具体、有素材支撑且符合作者资格的文章角度；有搜索目标时记录读者问题与可交付答案", contract)
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
        report = _quality_report(state)
        state.quality_report = {"hard_gate": report, "soft_quality": assess_soft_quality(state)}
        if report["blocked"]:
            state.revision_plan = [{"source": "hard_gate", "finding": finding} for finding in report["findings"]]
            _block(state, node, "正文硬门禁未通过")
        if not state.reader_simulation:
            _host_request(state, node, "模拟目标读者、知情者、怀疑者和快速浏览者；有搜索目标时核对正文是否直接、完整回答问题，输出局部修订计划", {
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
        report = _quality_report(state, base_dir=output_dir)
        state.quality_report["hard_gate"] = report
        if report["blocked"]:
            state.revision_plan = [{"source": "hard_gate", "finding": finding} for finding in report["findings"]]
            _block(state, node, "交付前质量门禁未通过")
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
        "topic": ("topic", "angle", "title_candidates", "search_intent"),
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
        elif key == "intent":
            state.intent.update(value)
        elif key == "search_intent":
            state.intent["search_intent"] = value
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
