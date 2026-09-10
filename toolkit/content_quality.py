"""Explainable soft editorial signals; these are not platform predictions."""

from __future__ import annotations

import re
from typing import Any, Dict

from .article_state import ArticleState


def assess_soft_quality(state: ArticleState) -> Dict[str, Any]:
    text = state.draft.strip()
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    sentences = [s.strip() for s in re.split(r"[。！？!?]", text) if s.strip()]
    concrete = len(re.findall(r"\d|年|月|日|来源[:：]|https?://|例如|具体", text))
    repeated = len(sentences) - len(set(sentences))
    sourced = sum(bool(c.source_ids) or c.kind in {"opinion", "inference", "hypothetical"}
                  for c in state.evidence_pack.claims)
    total = len(state.evidence_pack.claims)
    scores = {
        "information_density": min(100, 35 + concrete * 5),
        "specificity": min(100, 30 + concrete * 6),
        "evidence_quality": round(100 * sourced / total) if total else 50,
        "readability": max(0, min(100, 85 - int(max(0, len(text) / max(1, len(paragraphs)) - 260) / 4))),
        "redundancy": max(0, 100 - repeated * 15),
        "author_consistency": None,
        "opinion_strength": None,
        "reader_value": None,
        "narrative_flow": None,
        "ai_pattern_risk": max(0, 100 - sum(text.count(x) for x in ("综上所述", "值得注意的是", "首先", "其次")) * 10),
    }
    return {
        "scores": scores,
        "manual_review_required": [key for key, value in scores.items() if value is None],
        "disclaimer": "自动分数只描述可确定文本信号；作者感、洞察、叙事和读者价值需要宿主盲评与人工抽检。",
    }
