"""Host-first image generation helpers for pilot and batch stages.

Without an explicit provider or generator, this module writes a neutral request
for the current host AI. It never silently falls back to OpenAI or asks for a
user API key.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from ..image_gen import ImageGenerator
from ..recommendation_quality import check_generated_asset
from .models import CardPlan, TieTuPlan
from .portrait_prompt import render_portrait_prompt
from .workflow import record_batch, record_pilot


def _check_image_or_reject(plan: TieTuPlan, card: CardPlan, image_path: str) -> bool:
    report = check_generated_asset(image_path)
    plan.metadata.setdefault("generation_quality", {})[str(card.index)] = report
    if report["blocked"]:
        details = "; ".join(item["message"] for item in report["findings"])
        plan.generation_state.mark_card(card.index, "rejected", image_path, error=details)
        plan.generation_state.last_error = f"第 {card.index} 张图片未通过生成质量门禁: {details}"
        return False
    return True


def build_card_prompt(plan: TieTuPlan, card: CardPlan) -> str:
    if card.portrait_spec:
        return render_portrait_prompt(card.portrait_spec)
    return (
        f"Create a {plan.ratio} vertical image for a WeChat Tie-Tu post. "
        f"Topic: {plan.topic}. Card purpose: {card.purpose}. "
        f"Visual subject: {card.visual_subject}. Composition: {card.composition}. "
        "Keep one clear visual focus, leave a clean text-safe area, and do not render words, logos or watermarks."
    )


def _write_host_request(plan: TieTuPlan, card: CardPlan, output_dir: str) -> str:
    import json
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    request_path = target / f"tie-tu-card-{card.index:02d}.request.json"
    request_path.write_text(json.dumps({
        "mode": "host_image_generation",
        "topic": plan.topic,
        "card_index": card.index,
        "ratio": plan.ratio,
        "prompt": build_card_prompt(plan, card),
        "instruction": "Use the current host AI image tool and return a local image path; do not add text, logo or watermark.",
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    plan.metadata.setdefault("host_requests", {})[str(card.index)] = str(request_path)
    return str(request_path)


def generate_pilot(plan: TieTuPlan, output_dir: str, provider: Optional[str] = None,
                   generator: Optional[Any] = None) -> Optional[str]:
    if plan.approval_state.stages.get("card_plan") != "approved":
        raise RuntimeError("卡片策划未处于可生成状态")
    card = next((item for item in plan.cards if item.index == plan.generation_state.pilot_card), None)
    if card is None:
        raise RuntimeError("没有可试生成的卡片")
    if generator is None and provider is None:
        request_path = _write_host_request(plan, card, output_dir)
        plan.generation_state.mark_card(card.index, "awaiting_host", error=f"host request: {request_path}")
        plan.generation_state.last_error = ""
        return None
    service = generator or ImageGenerator()
    try:
        image_path = service.generate(build_card_prompt(plan, card), provider=provider, size="1024x1024", output_dir=output_dir)
    except Exception as exc:
        plan.generation_state.last_error = str(exc)
        plan.generation_state.pilot_status = "rejected"
        return None
    if image_path:
        if not _check_image_or_reject(plan, card, image_path):
            return None
        record_pilot(plan, card.index, image_path, "generated")
    else:
        plan.generation_state.pilot_status = "rejected"
    return image_path


def generate_batch(plan: TieTuPlan, output_dir: str, provider: Optional[str] = None,
                   generator: Optional[Any] = None) -> int:
    if plan.approval_state.stages.get("pilot_image") != "approved":
        raise RuntimeError("请先确认试生成图片：tie-tu approve --stage pilot_image --status approved")
    generated = 0
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    if generator is None and provider is None:
        record_batch(plan, "awaiting_host")
        for card in plan.cards:
            if card.image_path and Path(card.image_path).exists():
                generated += 1
                continue
            request_path = _write_host_request(plan, card, output_dir)
            plan.generation_state.mark_card(card.index, "awaiting_host", error=f"host request: {request_path}")
        return generated

    service = generator or ImageGenerator()
    record_batch(plan, "running")
    for card in plan.cards:
        if card.image_path and Path(card.image_path).exists():
            if not _check_image_or_reject(plan, card, card.image_path):
                record_batch(plan, "failed", plan.generation_state.last_error)
                return generated
            generated += 1
            continue
        try:
            image_path = service.generate(build_card_prompt(plan, card), provider=provider, size="1024x1024", output_dir=output_dir)
        except Exception as exc:
            plan.generation_state.mark_card(card.index, "failed", error=str(exc))
            continue
        if image_path:
            if not _check_image_or_reject(plan, card, image_path):
                record_batch(plan, "failed", plan.generation_state.last_error)
                return generated
            record_pilot(plan, card.index, image_path, "generated")
            generated += 1
        else:
            plan.generation_state.mark_card(card.index, "failed", error="图片生成器没有返回路径")
    record_batch(plan, "completed" if generated == len(plan.cards) else "failed",
                 "部分卡片生成失败" if generated != len(plan.cards) else "")
    return generated
