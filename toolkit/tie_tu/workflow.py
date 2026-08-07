"""State transitions and quality gates for the Tie-Tu workflow."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..contracts import SourceRecord, utc_now
from .models import TieTuPlan


def set_approval(plan: TieTuPlan, stage: str, status: str, note: str = "") -> TieTuPlan:
    plan.approval_state.set(stage, status, note)
    plan.content_brief.approval.set(stage, status, note)
    return plan


def add_source(plan: TieTuPlan, source_id: str, kind: str, title: str = "", url: str = "",
               evidence: str = "", status: str = "unverified", license: str = "") -> TieTuPlan:
    record = SourceRecord(source_id, kind, title, url, evidence, utc_now(), license, status)
    plan.source_ledger.add(record)
    plan.content_brief.source_ledger.add(record)
    plan.sources = [
        {"name": item.title or item.source_id, "url": item.url, "kind": item.kind, "status": item.status}
        for item in plan.source_ledger.records
    ]
    return plan


def record_pilot(plan: TieTuPlan, index: int, image_path: str, status: str = "generated") -> TieTuPlan:
    if not any(card.index == index for card in plan.cards):
        raise ValueError(f"找不到卡片: {index}")
    card = next(card for card in plan.cards if card.index == index)
    card.image_path = image_path
    card.image_source = "ai" if not card.image_source else card.image_source
    plan.generation_state.mark_card(index, status, image_path)
    set_approval(plan, "pilot_image", "pending" if status == "generated" else status)
    return plan


def record_batch(plan: TieTuPlan, status: str, error: str = "") -> TieTuPlan:
    if status not in {"pending", "awaiting_host", "running", "completed", "failed"}:
        raise ValueError(f"不支持的批量生成状态: {status}")
    plan.generation_state.batch_status = status
    plan.generation_state.last_error = error
    if status == "completed":
        set_approval(plan, "batch_generation", "approved", "批量图片已记录")
    elif status == "failed":
        set_approval(plan, "batch_generation", "blocked", error)
    return plan


def validate_card_briefs(plan: TieTuPlan) -> Dict[str, Any]:
    errors = []
    warnings = []
    for card in plan.cards:
        required = ("message", "visual_proof", "text_plan", "source_plan")
        missing = [key for key in required if not card.card_brief.get(key)]
        if missing:
            errors.append(f"第 {card.index} 张 Card Brief 缺少: {', '.join(missing)}")
        if not card.image_path:
            warnings.append(f"第 {card.index} 张尚未生成图片")
        elif not Path(card.image_path).exists():
            errors.append(f"第 {card.index} 张图片路径不存在: {card.image_path}")
    return {"ok": not errors, "errors": errors, "warnings": warnings}
