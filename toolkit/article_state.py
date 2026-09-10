"""Persistent state for the long-form WeChat article workflow."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from .contracts import SourceLedger, SourceRecord, utc_now


ARTICLE_NODES = (
    "intent",
    "topic",
    "research",
    "strategy",
    "draft",
    "review",
    "delivery",
)


@dataclass
class AuthorProfile:
    name: str = ""
    background: List[str] = field(default_factory=list)
    expertise: List[str] = field(default_factory=list)
    experience_claims: List[Dict[str, Any]] = field(default_factory=list)
    values: List[str] = field(default_factory=list)
    strong_opinions: List[str] = field(default_factory=list)
    evidence_preference: List[str] = field(default_factory=list)
    language_habits: List[str] = field(default_factory=list)
    sentence_preferences: List[str] = field(default_factory=list)
    paragraph_rhythm: str = ""
    narrative_distance: str = ""
    humor_style: str = ""
    argument_style: str = ""
    reader_relationship: str = ""
    typical_examples: List[str] = field(default_factory=list)
    taboo_expressions: List[str] = field(default_factory=list)
    inferred_traits: List[str] = field(default_factory=list)


@dataclass
class ClaimRecord:
    claim_id: str
    text: str
    kind: str = "opinion"  # fact, author_experience, public_case, opinion, inference, hypothetical
    source_ids: List[str] = field(default_factory=list)
    status: str = "unverified"  # verified, user_provided, illustrative, unverified, rejected
    materiality: str = "supporting"  # key, supporting


@dataclass
class EvidencePack:
    sources: SourceLedger = field(default_factory=SourceLedger)
    claims: List[ClaimRecord] = field(default_factory=list)
    research_status: str = "not_started"  # not_started, complete, partial, failed
    limitations: List[str] = field(default_factory=list)


@dataclass
class NodeState:
    status: str = "pending"  # pending, running, awaiting_host, passed, blocked, failed
    started_at: str = ""
    completed_at: str = ""
    message: str = ""
    request: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ArticleState:
    version: str = "2.0"
    task_id: str = ""
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    user_request: str = ""
    mode: str = "interactive"
    intent: Dict[str, Any] = field(default_factory=dict)
    audience: Dict[str, Any] = field(default_factory=dict)
    author_profile: AuthorProfile = field(default_factory=AuthorProfile)
    topic: str = ""
    angle: str = ""
    evidence_pack: EvidencePack = field(default_factory=EvidencePack)
    outline: List[Dict[str, Any]] = field(default_factory=list)
    writing_strategy: Dict[str, Any] = field(default_factory=dict)
    title_candidates: List[Dict[str, Any]] = field(default_factory=list)
    selected_title: str = ""
    draft: str = ""
    quality_report: Dict[str, Any] = field(default_factory=dict)
    reader_simulation: List[Dict[str, Any]] = field(default_factory=list)
    revision_plan: List[Dict[str, Any]] = field(default_factory=list)
    visual_plan: List[Dict[str, Any]] = field(default_factory=list)
    formatted_output: str = ""
    nodes: Dict[str, NodeState] = field(default_factory=lambda: {name: NodeState() for name in ARTICLE_NODES})
    degradations: List[Dict[str, Any]] = field(default_factory=list)
    audit_log: List[Dict[str, Any]] = field(default_factory=list)

    def log(self, event: str, detail: str = "") -> None:
        self.updated_at = utc_now()
        self.audit_log.append({"at": self.updated_at, "event": event, "detail": detail})

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "ArticleState":
        data = dict(payload)
        data["author_profile"] = AuthorProfile(**data.get("author_profile", {}))
        raw_pack = data.get("evidence_pack", {}) or {}
        ledger = raw_pack.get("sources", {}) or {}
        data["evidence_pack"] = EvidencePack(
            sources=SourceLedger([SourceRecord(**item) for item in ledger.get("records", [])]),
            claims=[ClaimRecord(**item) for item in raw_pack.get("claims", [])],
            research_status=raw_pack.get("research_status", "not_started"),
            limitations=raw_pack.get("limitations", []),
        )
        raw_nodes = data.get("nodes", {}) or {}
        data["nodes"] = {name: NodeState(**raw_nodes.get(name, {})) for name in ARTICLE_NODES}
        return cls(**data)


def save_article_state(state: ArticleState, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(state.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return target


def load_article_state(path: str | Path) -> ArticleState:
    return ArticleState.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
