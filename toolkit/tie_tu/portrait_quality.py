"""Deterministic checks for the portrait enhancement contract."""

from __future__ import annotations

from typing import Any, Dict

from .models import TieTuPlan


REQUIRED_FIELDS = ("route", "subject", "model_bible", "scene", "pose", "camera", "lighting", "negative_prompt")


def validate_portrait_plan(plan: TieTuPlan) -> Dict[str, Any]:
    errors = []
    warnings = []
    if not plan.portrait_enabled:
        return {"ok": True, "errors": errors, "warnings": warnings}
    if not plan.model_bible:
        errors.append("已启用人像增强，但缺少 model_bible")
    if not plan.portrait_route:
        errors.append("已启用人像增强，但缺少 portrait_route")
    for card in plan.cards:
        missing = [field for field in REQUIRED_FIELDS if not card.portrait_spec.get(field)]
        if missing:
            errors.append(f"第 {card.index} 张人像规格缺少: {', '.join(missing)}")
        negative = card.portrait_spec.get("negative_prompt", "").lower()
        if "watermark" not in negative or "text" not in negative:
            warnings.append(f"第 {card.index} 张未明确包含文字/水印过滤词")
    if len(plan.cards) > 1 and "same fictional adult model" not in str(plan.model_bible.get("continuity", "")):
        warnings.append("多张人像卡片未明确保持同一模特")
    return {"ok": not errors, "errors": errors, "warnings": warnings}
