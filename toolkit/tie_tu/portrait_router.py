"""Portrait routing and continuity scaffolding for Tie-Tu cards.

This adapter borrows the director's stable concepts without coupling the
independent Tie-Tu workflow to a particular image provider or long-form path.
"""

from __future__ import annotations

from typing import Any, Dict

from .models import TieTuPlan
from .portrait_prompt import build_portrait_spec


PORTRAIT_KEYWORDS = (
    "人像", "肖像", "美女", "美人", "模特", "写真", "女性", "女生", "女孩",
    "穿搭", "妆容", "妆造", "复古美女", "港风美女", "人物故事", "女性形象",
)

ROUTE_KEYWORDS = {
    "retro-hongkong": ("复古", "港风", "旧香港", "胶片", "老照片"),
    "urban-fashion": ("都市", "街拍", "通勤", "西装", "风衣", "时尚"),
    "ecommerce-tryon": ("电商", "试衣", "服装展示", "商品模特", "穿搭推荐"),
    "gufeng-xianxia": ("古风", "仙侠", "唐风", "古装", "披帛"),
    "new-chinese": ("新中式", "茶室", "东方美学", "旗袍"),
    "ultra-close-real-face": ("怼脸", "超近景", "毛孔", "未修图", "真实皮肤"),
    "low-key-cinematic-photography": ("电影感", "暗调", "低照度", "叙事人像"),
}


def _text_blob(plan: TieTuPlan) -> str:
    card_text = " ".join(
        f"{card.visual_subject} {card.caption} {card.overlay_text}" for card in plan.cards
    )
    return " ".join((plan.industry, plan.topic, plan.title, plan.style, card_text)).lower()


def is_portrait_request(plan: TieTuPlan) -> bool:
    blob = _text_blob(plan)
    return any(keyword in blob for keyword in PORTRAIT_KEYWORDS)


def select_route(plan: TieTuPlan) -> str:
    blob = _text_blob(plan)
    for route, keywords in ROUTE_KEYWORDS.items():
        if any(keyword in blob for keyword in keywords):
            return route
    return "clean-lifestyle"


def build_model_bible(plan: TieTuPlan, route: str) -> Dict[str, Any]:
    return {
        "subject": "fictional clearly adult East Asian woman",
        "age_range": "25-30, unmistakably adult",
        "face_direction": "natural facial asymmetry, expressive eyes, realistic proportions, no generic plastic beauty face",
        "skin_direction": "natural skin texture, subtle pores and fine detail, refined but not waxy",
        "hair_direction": "coherent dark hair shape and believable flyaway strands across the card set",
        "temperament": "natural, restrained, visually consistent with the topic",
        "route": route,
        "continuity": "same fictional adult model across all portrait cards; keep face, age, hair and palette stable",
        "reference_policy": "use uploaded identity references only when the user owns or has authorization to use them",
    }


def enhance_plan(plan: TieTuPlan) -> TieTuPlan:
    """Populate portrait specs when auto detection or explicit requirement matches."""
    enabled = plan.portrait_mode == "required" or (
        plan.portrait_mode == "auto" and is_portrait_request(plan)
    )
    plan.portrait_enabled = enabled
    if not enabled:
        return plan

    plan.portrait_route = select_route(plan)
    plan.model_bible = build_model_bible(plan, plan.portrait_route)
    for card in plan.cards:
        card.portrait_spec = build_portrait_spec(plan, card, plan.portrait_route, plan.model_bible)
    return plan
