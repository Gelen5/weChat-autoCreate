"""Structured, provider-neutral portrait prompt generation for Tie-Tu."""

from __future__ import annotations

from typing import Any, Dict

from .models import CardPlan, TieTuPlan


ROUTE_DIRECTION = {
    "clean-lifestyle": "natural lifestyle portrait, candid everyday moment, soft daylight",
    "retro-hongkong": "retro Hong Kong street portrait, muted film colors, lived-in old neighborhood, subtle grain",
    "urban-fashion": "editorial urban fashion portrait, modern architecture, controlled street light",
    "ecommerce-tryon": "commercial clothing model photo, garment fit and material clearly visible, neutral pose",
    "gufeng-xianxia": "refined Chinese fantasy portrait, coherent traditional costume, restrained atmospheric depth",
    "new-chinese": "quiet new-Chinese portrait, wood, tea-room negative space, understated oriental palette",
    "ultra-close-real-face": "ultra-close realistic face portrait, natural pores, believable micro-expression",
    "low-key-cinematic-photography": "low-key cinematic portrait, readable shadows, one motivated light source",
}

NEGATIVES = (
    "text, Chinese characters, subtitles, watermark, logo, signature, poster typography, "
    "plastic skin, waxy face, generic AI beauty face, over-smoothed skin, uncanny eyes, "
    "deformed hands, extra fingers, fused fingers, broken anatomy, duplicate person, "
    "inconsistent face, inconsistent hair, excessive blur, harsh HDR, oversaturation, "
    "child, minor, ambiguous age, sexualized minor, explicit nudity"
)


def _pose_for(card: CardPlan) -> str:
    role = card.role
    if role in {"cover", "scene"}:
        return "three-quarter body direction, relaxed shoulders, one natural hand gesture, gaze slightly past the camera"
    if role in {"detail", "before", "past"}:
        return "quiet seated or leaning pose, hands naturally occupied by one small prop, restrained expression"
    if role in {"after", "present", "turning_point"}:
        return "gentle movement captured mid-action, believable weight shift, clear eye line and relaxed fingers"
    return "natural half-body portrait pose, coherent action chain, no stiff mannequin posture"


def build_portrait_spec(
    plan: TieTuPlan,
    card: CardPlan,
    route: str,
    model_bible: Dict[str, Any],
) -> Dict[str, Any]:
    direction = ROUTE_DIRECTION.get(route, ROUTE_DIRECTION["clean-lifestyle"])
    return {
        "route": route,
        "subject": model_bible["subject"],
        "model_bible": model_bible,
        "scene": card.visual_subject,
        "pose": _pose_for(card),
        "expression": "subtle, emotionally legible expression appropriate to the card purpose",
        "camera": "3:4 vertical portrait, 50mm or 85mm equivalent, f/1.8-f/2.8, face and key clothing detail sharp, background gently separated",
        "lighting": "motivated natural or practical light, realistic skin highlights, soft contact shadows, consistent direction across the series",
        "direction": direction,
        "composition": f"{card.composition}; keep a clean text-safe area without placing generated text in the image",
        "texture": "authentic photographic detail, natural skin pores, believable hair strands, fabric weave and physically plausible reflections",
        "negative_prompt": NEGATIVES,
    }


def render_portrait_prompt(spec: Dict[str, Any]) -> str:
    """Flatten a spec into a copy-ready prompt for any image provider."""
    return (
        f"Generate a 3:4 vertical image of a {spec['subject']}. "
        f"Visual direction: {spec['direction']}. Scene: {spec['scene']}. "
        f"Pose and action: {spec['pose']}. Expression: {spec['expression']}. "
        f"Camera: {spec['camera']}. Lighting: {spec['lighting']}. "
        f"Composition: {spec['composition']}. Texture and realism: {spec['texture']}. "
        "Create one coherent photographed moment, with no generated words, captions or watermarks."
    )
