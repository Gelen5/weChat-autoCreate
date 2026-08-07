"""Optional image generation helpers for pilot and batch stages.

The provider remains the existing ImageGenerator; this module only manages
Tie-Tu prompts and lifecycle state. It is safe to use with a fake generator in
tests, so planning and state tests do not require an API key.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from ..image_gen import ImageGenerator
from .models import CardPlan, TieTuPlan
from .portrait_prompt import render_portrait_prompt
from .workflow import record_batch, record_pilot


def build_card_prompt(plan: TieTuPlan, card: CardPlan) -> str:
    if card.portrait_spec:
        return render_portrait_prompt(card.portrait_spec)
    return (
        f"Create a {plan.ratio} vertical image for a WeChat Tie-Tu post. "
        f"Topic: {plan.topic}. Card purpose: {card.purpose}. "
        f"Visual subject: {card.visual_subject}. Composition: {card.composition}. "
        "Keep one clear visual focus, leave a clean text-safe area, and do not render words, logos or watermarks."
    )


def generate_pilot(plan: TieTuPlan, output_dir: str, provider: Optional[str] = None,
                   generator: Optional[Any] = None) -> Optional[str]:
    if plan.approval_state.stages.get("card_plan") != "approved":
        raise RuntimeError("卡片策划未处于可生成状态")
    card = next((item for item in plan.cards if item.index == plan.generation_state.pilot_card), None)
    if card is None:
        raise RuntimeError("没有可试生成的卡片")
    service = generator or ImageGenerator()
    try:
        image_path = service.generate(build_card_prompt(plan, card), provider=provider, size="1024x1024", output_dir=output_dir)
    except Exception as exc:
        plan.generation_state.last_error = str(exc)
        plan.generation_state.pilot_status = "rejected"
        return None
    if image_path:
        record_pilot(plan, card.index, image_path, "generated")
    else:
        plan.generation_state.pilot_status = "rejected"
    return image_path


def generate_batch(plan: TieTuPlan, output_dir: str, provider: Optional[str] = None,
                   generator: Optional[Any] = None) -> int:
    if plan.approval_state.stages.get("pilot_image") != "approved":
        raise RuntimeError("请先确认试生成图片：tie-tu approve --stage pilot_image --status approved")
    service = generator or ImageGenerator()
    record_batch(plan, "running")
    generated = 0
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    for card in plan.cards:
        if card.image_path and Path(card.image_path).exists():
            generated += 1
            continue
        try:
            image_path = service.generate(build_card_prompt(plan, card), provider=provider, size="1024x1024", output_dir=output_dir)
        except Exception as exc:
            plan.generation_state.mark_card(card.index, "failed", error=str(exc))
            continue
        if image_path:
            record_pilot(plan, card.index, image_path, "generated")
            generated += 1
        else:
            plan.generation_state.mark_card(card.index, "failed", error="图片生成器没有返回路径")
    record_batch(plan, "completed" if generated == len(plan.cards) else "failed",
                 "部分卡片生成失败" if generated != len(plan.cards) else "")
    return generated
