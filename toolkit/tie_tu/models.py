"""Data contracts for the independent Tie-Tu workflow."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from ..contracts import ApprovalState, ContentBrief, GenerationState, QualityGate, SourceLedger, SourceRecord


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
    portrait_spec: Dict[str, Any] = field(default_factory=dict)
    card_brief: Dict[str, Any] = field(default_factory=dict)
    quality_gate: QualityGate = field(default_factory=lambda: QualityGate("card"))


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
    image_count: int = 5
    copy: str = ""
    cta: str = ""
    cards: List[CardPlan] = field(default_factory=list)
    sources: List[Dict[str, str]] = field(default_factory=list)
    research_notes: List[str] = field(default_factory=list)
    portrait_mode: str = "auto"
    portrait_enabled: bool = False
    portrait_route: str = ""
    model_bible: Dict[str, Any] = field(default_factory=dict)
    content_brief: ContentBrief = field(default_factory=ContentBrief)
    source_ledger: SourceLedger = field(default_factory=SourceLedger)
    approval_state: ApprovalState = field(default_factory=ApprovalState)
    generation_state: GenerationState = field(default_factory=GenerationState)
    quality_gate: QualityGate = field(default_factory=lambda: QualityGate("tie_tu"))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "TieTuPlan":
        cards = []
        for card in payload.get("cards", []):
            item = dict(card)
            gate = item.get("quality_gate", {}) or {}
            item["quality_gate"] = QualityGate(gate_id=gate.get("gate_id", "card"), required_checks=gate.get("required_checks", []), status=gate.get("status", "pending"), findings=gate.get("findings", []), evaluated_at=gate.get("evaluated_at", ""))
            cards.append(CardPlan(**item))
        data = dict(payload)
        data["cards"] = cards
        data.setdefault("mode", "tie_tu")
        data.setdefault("content_type_label", CONTENT_TYPES.get(data.get("content_type", ""), ""))
        data["content_brief"] = ContentBrief.from_dict(data.get("content_brief", {}))
        ledger = data.get("source_ledger", {})
        legacy_sources = data.get("sources", [])
        if not ledger and legacy_sources:
            ledger = {"records": [
                {
                    "source_id": f"legacy-{index}",
                    "kind": item.get("kind", "unknown"),
                    "title": item.get("name", ""),
                    "url": item.get("url", ""),
                    "status": item.get("status", "unverified"),
                }
                for index, item in enumerate(legacy_sources, 1)
            ]}
        data["source_ledger"] = SourceLedger(
            records=[SourceRecord(**item) for item in ledger.get("records", [])]
        )
        approval = data.get("approval_state", {}) or {}
        data["approval_state"] = ApprovalState(stages=approval.get("stages", ApprovalState().stages), history=approval.get("history", []))
        generation = data.get("generation_state", {}) or {}
        data["generation_state"] = GenerationState(pilot_card=generation.get("pilot_card", 1), pilot_status=generation.get("pilot_status", "pending"), batch_status=generation.get("batch_status", "pending"), cards=generation.get("cards", {}), last_error=generation.get("last_error", ""))
        gate = data.get("quality_gate", {}) or {}
        data["quality_gate"] = QualityGate(gate_id=gate.get("gate_id", "tie_tu"), required_checks=gate.get("required_checks", []), status=gate.get("status", "pending"), findings=gate.get("findings", []), evaluated_at=gate.get("evaluated_at", ""))
        if not data["content_brief"].source_ledger.records and data["source_ledger"].records:
            data["content_brief"].source_ledger = data["source_ledger"]
        data["image_count"] = len(cards) if "image_count" not in data else data["image_count"]
        return cls(**data)


def save_plan(plan: TieTuPlan, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


def load_plan(path: str | Path) -> TieTuPlan:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    plan = TieTuPlan.from_dict(payload)
    if plan.portrait_mode != "off":
        from .portrait_router import enhance_plan
        enhance_plan(plan)
    return plan
