"""Deterministic content-regression measurements for frozen article outputs."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List


AI_PATTERNS = ("在这个时代", "随着", "综上所述", "值得注意的是", "毋庸置疑", "让我们一起")


def load_tasks(path: str | Path) -> List[Dict[str, Any]]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def measure(text: str) -> Dict[str, Any]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    sentences = [part.strip() for part in re.split(r"[。！？!?]", text) if part.strip()]
    concrete = len(re.findall(r"(?:20\d{2}年?|\d+(?:\.\d+)?%|\d+个|\d+次|https?://)", text))
    citations = len(re.findall(r"https?://|来源[:：]|据.{0,12}(?:报告|公告|数据)", text))
    repeats = len(sentences) - len(set(sentences))
    ai_hits = sum(text.count(item) for item in AI_PATTERNS)
    opening = text[:200]
    return {
        "chars": len(text),
        "paragraphs": len(paragraphs),
        "concrete_markers": concrete,
        "source_markers": citations,
        "repeated_sentences": repeats,
        "ai_pattern_hits": ai_hits,
        "opening_specificity": len(re.findall(r"\d|年|月|日|：|“|『", opening)),
    }


def compare_directories(tasks: Iterable[Dict[str, Any]], old_dir: str | Path, new_dir: str | Path) -> Dict[str, Any]:
    rows = []
    regressions = []
    for task in tasks:
        filename = task["id"] + ".md"
        old_path, new_path = Path(old_dir) / filename, Path(new_dir) / filename
        row = {"id": task["id"], "type": task["type"], "old": None, "new": None, "notes": []}
        if old_path.exists():
            row["old"] = measure(old_path.read_text(encoding="utf-8"))
        if new_path.exists():
            row["new"] = measure(new_path.read_text(encoding="utf-8"))
        if not row["old"] or not row["new"]:
            row["notes"].append("missing_output")
        else:
            if row["new"]["ai_pattern_hits"] > row["old"]["ai_pattern_hits"]:
                regressions.append({"id": task["id"], "metric": "ai_pattern_hits"})
            if row["new"]["repeated_sentences"] > row["old"]["repeated_sentences"]:
                regressions.append({"id": task["id"], "metric": "repeated_sentences"})
        rows.append(row)
    return {"tasks": rows, "regressions": regressions,
            "boundary": "这些指标只测可确定的文本信号，不代表阅读量、完读率或内容优劣。"}
