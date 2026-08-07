"""Deterministic scaffolding for AI-assisted Tie-Tu planning.

The LLM or the interactive Skill supplies researched copy and image prompts.
This module supplies stable content-type routing and card roles so rendering
and validation do not depend on prose parsing.
"""

from __future__ import annotations

import re
from typing import Dict, List

from .models import CONTENT_TYPES, CardPlan, TieTuPlan


TYPE_KEYWORDS: Dict[str, tuple[str, ...]] = {
    "tutorial": ("教程", "步骤", "怎么", "如何", "入门", "流程", "方法"),
    "before_after": ("对比", "区别", "以前", "如今", "前后", "变化", "升级"),
    "list": ("清单", "推荐", "盘点", "值得", "必备", "合集", "选购"),
    "industry_view": ("趋势", "行业", "观点", "为什么", "分析", "判断", "未来"),
    "city_change": ("深圳", "城市", "街区", "老街", "地标", "建筑", "变迁"),
    "emotional_story": ("怀念", "青春", "故事", "回忆", "情绪", "一个人", "告别"),
}


ROLE_TEMPLATES = {
    "tutorial": ["cover", "problem", "step", "step", "summary"],
    "before_after": ["cover", "before", "after", "comparison", "reflection"],
    "list": ["cover", "item", "item", "item", "summary"],
    "industry_view": ["cover", "phenomenon", "evidence", "view", "conclusion"],
    "city_change": ["cover", "past", "present", "contrast", "memory"],
    "emotional_story": ["cover", "scene", "detail", "turning_point", "ending"],
}


def _text_blob(industry: str, topic: str, title: str) -> str:
    return " ".join(value for value in (industry, topic, title) if value).lower()


def recommend_types(industry: str, topic: str, title: str = "") -> List[Dict[str, object]]:
    """Return all six types ranked by keyword fit.

    This is a transparent fallback for the interactive Skill. The AI can
    replace scores after hotspot research while keeping the same contract.
    """
    blob = _text_blob(industry, topic, title)
    results = []
    for type_id, keywords in TYPE_KEYWORDS.items():
        hits = [keyword for keyword in keywords if keyword.lower() in blob]
        score = min(100, 35 + len(hits) * 18)
        results.append({
            "type": type_id,
            "label": CONTENT_TYPES[type_id],
            "score": score,
            "matched_keywords": hits,
            "reason": "命中关键词：" + "、".join(hits) if hits else "适合作为通用备选结构",
        })
    return sorted(results, key=lambda item: (item["score"], item["type"]), reverse=True)


def _default_card_text(type_id: str, index: int) -> tuple[str, str, str]:
    roles = ROLE_TEMPLATES[type_id]
    role = roles[min(index - 1, len(roles) - 1)]
    labels = {
        "cover": ("主题封面", "第一眼讲清楚这组贴图在说什么"),
        "problem": ("问题场景", "让读者看见具体痛点"),
        "step": (f"步骤 {index - 1}", "只呈现一个可执行动作"),
        "summary": ("最后一张", "把观点收束成一句可记住的话"),
        "before": ("过去", "呈现变化前的状态"),
        "after": ("现在", "呈现变化后的状态"),
        "comparison": ("变化对照", "把差异放在同一张画面里"),
        "reflection": ("余味", "留下情绪或个人判断"),
        "item": (f"清单项 {index - 1}", "用一张图说明一个推荐点"),
        "phenomenon": ("现象", "展示正在发生的变化"),
        "evidence": ("证据", "放入案例、数据或可核验事实"),
        "view": ("判断", "明确表达一个观点"),
        "conclusion": ("结论", "给出读者下一步行动"),
        "past": ("旧景", "保留历史或旧状态的生活细节"),
        "present": ("今景", "呈现今天的空间和人物活动"),
        "contrast": ("前后对比", "统一机位或统一视觉锚点"),
        "memory": ("记忆", "把城市变化落回人的感受"),
        "scene": ("场景", "先交代人物和环境"),
        "detail": ("细节", "用一个小物件或动作承载情绪"),
        "turning_point": ("转折", "让情绪或叙事发生变化"),
        "ending": ("结尾", "留下克制的情绪回声"),
    }
    return role, labels[role][0], labels[role][1]


def build_plan(
    industry: str,
    topic: str,
    title: str = "",
    content_type: str | None = None,
    image_count: int = 5,
    style: str = "",
    audience: str = "",
) -> TieTuPlan:
    if not 3 <= image_count <= 20:
        raise ValueError("贴图号图片数量必须在 3 到 20 张之间")

    selected = content_type or str(recommend_types(industry, topic, title)[0]["type"])
    if selected not in CONTENT_TYPES:
        raise ValueError(f"不支持的贴图号内容类型: {selected}")

    cards: List[CardPlan] = []
    for index in range(1, image_count + 1):
        role, label, purpose = _default_card_text(selected, index)
        cards.append(CardPlan(
            index=index,
            role=role,
            purpose=purpose,
            visual_subject=f"围绕“{topic}”的{label}画面",
            composition="3:4 竖幅，主体明确，预留文字安全区，避免文字遮挡主体",
            overlay_text="",
            caption="",
        ))

    return TieTuPlan(
        industry=industry,
        topic=topic,
        title=title or topic,
        content_type=selected,
        content_type_label=CONTENT_TYPES[selected],
        audience=audience,
        angle="待热点研究后补充内容角度",
        style=style,
        cards=cards,
        research_notes=["这是结构化策划草案；热点、事实和图片来源由上层 Skill 补充。"],
    )
