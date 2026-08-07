"""Data contracts for the independent Tie-Tu workflow."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List


CONTENT_TYPES = {
    "tutorial": "教程步骤型",
    "before_after": "前后对比型",
    "list": "清单推荐型",
    "industry_view": "行业观点型",
    "city_change": "城市变化型",
    "emotional_story": "情绪故事型",
}


@dataclass
class CardPlan:
    index: int
    role: str
    purpose: str
    visual_subject: str
    composition: str
    overlay_text: str = ""
    caption: str = ""
    image_path: str = ""
    image_source: str = "ai"
    source_url: str = ""


@dataclass
class TieTuPlan:
    mode: str = "tie_tu"
    industry: str = ""
    topic: str = ""
    title: str = ""
    content_type: str = "industry_view"
    content_type_label: str = "行业观点型"
    audience: str = ""
    angle: str = ""
    style: str = ""
    ratio: str = "3:4"
    copy: str = ""
    cta: str = ""
    cards: List[CardPlan] = field(default_factory=list)
    sources: List[Dict[str, str]] = field(default_factory=list)
    research_notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "TieTuPlan":
        cards = [CardPlan(**card) for card in payload.get("cards", [])]
        data = dict(payload)
        data["cards"] = cards
        data.setdefault("mode", "tie_tu")
        data.setdefault("content_type_label", CONTENT_TYPES.get(data.get("content_type", ""), ""))
        return cls(**data)


def save_plan(plan: TieTuPlan, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


def load_plan(path: str | Path) -> TieTuPlan:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return TieTuPlan.from_dict(payload)
