"""Shared workflow contracts for long-form articles and Tie-Tu posts.

The contracts are deliberately provider-neutral. They describe intent, facts,
sources, quality gates and approval state without forcing either workflow to
share its renderer or publisher.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class SourceRecord:
    source_id: str
    kind: str = "unknown"  # web, user, ai, reference, claim
    title: str = ""
    url: str = ""
    evidence: str = ""
    retrieved_at: str = ""
    license: str = ""
    status: str = "unverified"  # verified, illustrative, unverified, rejected
    notes: str = ""


@dataclass
class SourceLedger:
    records: List[SourceRecord] = field(default_factory=list)

    def add(self, record: SourceRecord) -> None:
        existing = {item.source_id for item in self.records}
        if record.source_id not in existing:
            self.records.append(record)

    def ids(self) -> List[str]:
        return [item.source_id for item in self.records]


@dataclass
class QualityGate:
    gate_id: str
    required_checks: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, passed, failed, skipped
    findings: List[Dict[str, Any]] = field(default_factory=list)
    evaluated_at: str = ""

    def record(self, check: str, passed: bool, detail: str = "") -> None:
        self.findings.append({"check": check, "passed": passed, "detail": detail})
        self.status = "passed" if all(item["passed"] for item in self.findings) else "failed"
        self.evaluated_at = utc_now()


@dataclass
class ApprovalState:
    stages: Dict[str, str] = field(default_factory=lambda: {
        "topic": "pending",
        "brief": "pending",
        "card_plan": "pending",
        "pilot_image": "pending",
        "batch_generation": "pending",
        "preview": "pending",
        "publish": "pending",
    })
    history: List[Dict[str, Any]] = field(default_factory=list)

    def set(self, stage: str, status: str, note: str = "") -> None:
        if status not in {"pending", "approved", "rejected", "blocked"}:
            raise ValueError(f"不支持的审批状态: {status}")
        self.stages[stage] = status
        self.history.append({"stage": stage, "status": status, "note": note, "at": utc_now()})


@dataclass
class GenerationState:
    pilot_card: int = 1
    pilot_status: str = "pending"  # pending, generated, approved, rejected
    batch_status: str = "pending"  # pending, running, completed, failed
    cards: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    last_error: str = ""

    def mark_card(self, index: int, status: str, image_path: str = "", error: str = "") -> None:
        self.cards[str(index)] = {"status": status, "image_path": image_path, "error": error, "at": utc_now()}
        if index == self.pilot_card:
            self.pilot_status = status


@dataclass
class ContentBrief:
    mode: str = "long_form"  # long_form, tie_tu
    intent: str = ""
    audience: str = ""
    deliverable: str = ""
    content_type: str = ""
    style: str = ""
    facts: List[Dict[str, Any]] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    quality_gates: List[QualityGate] = field(default_factory=list)
    source_ledger: SourceLedger = field(default_factory=SourceLedger)
    approval: ApprovalState = field(default_factory=ApprovalState)
    assumptions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "ContentBrief":
        data = dict(payload or {})
        data["quality_gates"] = [QualityGate(gate_id=item.get("gate_id", "brief"), required_checks=item.get("required_checks", []), status=item.get("status", "pending"), findings=item.get("findings", []), evaluated_at=item.get("evaluated_at", "")) for item in data.get("quality_gates", [])]
        ledger = data.get("source_ledger", {})
        data["source_ledger"] = SourceLedger(
            records=[SourceRecord(**item) for item in ledger.get("records", [])]
        )
        approval = data.get("approval", {}) or {}
        data["approval"] = ApprovalState(stages=approval.get("stages", ApprovalState().stages), history=approval.get("history", []))
        return cls(**data)
