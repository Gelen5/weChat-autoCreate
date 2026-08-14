"""微信推荐质量门禁：本地、无 API 依赖、可解释。"""

from __future__ import annotations

import difflib
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .contracts import SourceLedger, SourceRecord, utc_now
from .text_encoding import read_text

PASS = "pass"
NOTES = "pass_with_notes"
REVISION = "needs_revision"
BLOCKED = "blocked"

_FILLER = (
    "在这个时代", "不得不说", "众所周知", "相信大家", "其实很多人不知道",
    "说到底", "归根结底", "我们都知道", "值得一提的是", "这说明了一个问题",
    "总而言之", "从某种程度上来说", "毫无疑问", "不难发现",
)
_ABSOLUTES = (
    "最脏", "最毒", "最坑", "最差", "最好", "第一名", "绝对", "必然", "从来不",
    "人人", "千万别", "一定要", "全网第一", "百分之百", "100%", "永远", "致癌", "毒死",
)
_TITLE_REPAIRS = {
    "最脏": "购买时要重点留意的", "最毒": "存在风险争议的", "最坑": "容易踩坑的",
    "从来不": "通常不会", "人人": "不少人", "千万别": "建议谨慎", "一定要": "建议",
    "百分之百": "在特定条件下", "100%": "在特定条件下",
}
_CLAIM_MARKERS = re.compile(r"\d+(?:\.\d+)?")
_CLAIM_WORDS = ("据", "来源", "调查", "研究", "案例", "例如", "在我", "我家", "我们", "采访", "实测")
_SENTENCE_SPLIT = re.compile(r"[。！？!?；;\n]+")


def _clean(text: str) -> str:
    return re.sub(r"\s+", "", str(text or "")).lower()


def _ngrams(text: str, size: int = 4) -> set[str]:
    text = _clean(text)
    return {text[i:i + size] for i in range(max(0, len(text) - size + 1))}


def _finding(code: str, level: str, message: str, location: str = "", repair: str = "") -> dict[str, Any]:
    return {"code": code, "level": level, "message": message, "location": location, "repair": repair}


def _similarity(text: str, other: str) -> float:
    left, right = _ngrams(text), _ngrams(other)
    if not left or not right:
        return difflib.SequenceMatcher(None, _clean(text), _clean(other)).ratio()
    return len(left & right) / len(left | right)


def _title_coverage(title: str, body: str) -> float:
    compact_title = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", title).lower()
    compact_body = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", body).lower()
    if not compact_title:
        return 1.0
    if re.search(r"[\u4e00-\u9fff]", compact_title):
        units = {compact_title[i:i + 2] for i in range(max(1, len(compact_title) - 1))}
    else:
        units = set(re.findall(r"[a-z0-9]{3,}", title.lower()))
    return sum(unit in compact_body for unit in units) / len(units) if units else 1.0


def _history_texts(history_dir: str | Path | None) -> list[tuple[str, str]]:
    if not history_dir or not Path(history_dir).exists():
        return []
    result: list[tuple[str, str]] = []
    for path in Path(history_dir).rglob("*"):
        if path.suffix.lower() not in {".md", ".txt", ".json", ".jsonl"}:
            continue
        try:
            raw = read_text(path)
            if path.suffix.lower() == ".json":
                payload = json.loads(raw)
                for item in payload if isinstance(payload, list) else [payload]:
                    if isinstance(item, Mapping):
                        text = "\n".join(str(item.get(key, "")) for key in ("title", "content", "body", "copy"))
                        if text.strip():
                            result.append((str(item.get("title", path.name)), text))
            elif path.suffix.lower() == ".jsonl":
                for line in raw.splitlines():
                    try:
                        item = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if isinstance(item, Mapping):
                        text = "\n".join(str(item.get(key, "")) for key in ("title", "content", "body", "copy"))
                        if text.strip():
                            result.append((str(item.get("title", path.name)), text))
            else:
                result.append((path.name, raw))
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
    return result


def _records(sources: SourceLedger | Iterable[SourceRecord] | None) -> list[SourceRecord]:
    return list(sources.records) if isinstance(sources, SourceLedger) else list(sources or [])


def _finish(report: dict[str, Any], strict: bool) -> dict[str, Any]:
    levels = {item["level"] for item in report["findings"]}
    report["status"] = BLOCKED if "block" in levels else REVISION if "revision" in levels else NOTES if "note" in levels else PASS
    report["blocked"] = report["status"] == BLOCKED or (strict and report["status"] == REVISION)
    report["ok"] = not report["blocked"]
    report["repair_order"] = [item["repair"] for item in report["findings"] if item.get("repair")]
    return report


def check_content(title: str, body: str, *, sources: SourceLedger | Iterable[SourceRecord] | None = None,
                  history_dir: str | Path | None = None, kind: str = "article",
                  assets: Sequence[str | Path] | None = None, ai_assisted: bool | None = None,
                  strict: bool = False) -> dict[str, Any]:
    text, title = str(body or "").strip(), str(title or "").strip()
    sentences = [item.strip() for item in _SENTENCE_SPLIT.split(text) if item.strip()]
    records = _records(sources)
    findings: list[dict[str, Any]] = []
    anchors = len(_CLAIM_MARKERS.findall(text)) + sum(text.count(word) for word in _CLAIM_WORDS)
    filler_hits = [phrase for phrase in _FILLER if phrase in text]
    filler_ratio = len(filler_hits) / max(1, len(sentences))
    scores: dict[str, int | None] = {
        "originality": None, "information_gain": min(100, round(35 + anchors * 8 - filler_ratio * 45)),
        "title_match": None, "asset_quality": None,
    }
    if len(text) < 180 and kind == "article":
        findings.append(_finding("insufficient_length", "revision", "正文过短，可能无法提供有效信息增量", "正文", "补充具体场景、事实、判断或可执行步骤，避免用套话填充。"))
    if len(_clean(text)) < 30 and kind == "tie_tu":
        findings.append(_finding("insufficient_tie_tu_copy", "revision", "贴图号缺少有效配文或卡片信息，存在低信息量风险", "配文/卡片", "补充每张图承担的独立信息、场景或情绪推进，避免只发重复图片。"))
    if filler_ratio >= 0.18:
        findings.append(_finding("filler_density", "revision", f"空泛套话占比偏高：{', '.join(filler_hits[:4])}", "正文", "删除不增加信息的句子，改为具体人物、时间、地点、过程或判断。"))
    if anchors == 0 and len(text) >= 180:
        findings.append(_finding("no_information_anchor", "revision", "没有发现足够的事实、案例、时间、数据或个人材料锚点", "正文", "为核心观点补充可核验事实、具体案例或明确标注的个人观察。"))
    absolute_hits = [word for word in _ABSOLUTES if word in title]
    if absolute_hits:
        findings.append(_finding("absolute_title", "revision", f"标题含缺少边界的绝对化表达：{'、'.join(absolute_hits)}", "标题", "补充范围、时间或条件，避免无依据的绝对结论。"))
    title_match = _title_coverage(title, text)
    scores["title_match"] = round(title_match * 100)
    if title and text and title_match < 0.18:
        findings.append(_finding("title_content_mismatch", "revision", "标题中的核心承诺在正文中没有明显对应内容", "标题/正文", "让正文首段回答标题问题，或缩小标题承诺。"))
    factual_terms = ("数据显示", "研究表明", "专家表示", "调查发现", "官方发布", "致癌", "能治", "一定")
    if any(term in text for term in factual_terms) and not records:
        findings.append(_finding("unsupported_claim", "block", "正文包含事实性或健康功效断言，但没有来源账本", "正文", "补充来源并核对结论；无法核验时改为观点或删除。"))
    elif records and any(record.status not in {"verified", "illustrative"} for record in records):
        findings.append(_finding("unverified_sources", "note", "来源账本中仍有未核验条目", "来源账本", "发布前核验关键来源，或明确标为未核验信息。"))
    template_hits = sum(text.count(phrase) for phrase in ("首先", "其次", "最后", "总的来说", "希望这篇文章"))
    if template_hits >= 5 and anchors <= 1:
        findings.append(_finding("low_value_aigc_pattern", "block" if ai_assisted is not False else "revision", "模板化推进词过多且缺少具体材料，存在低价值 AIGC 风险", "正文", "加入真实材料和作者判断，不能只替换同义词。"))
    elif ai_assisted is True:
        findings.append(_finding("ai_assistance_note", "note", "内容标记为 AI 辅助创作，请人工核验事实并补充原创材料", "创作元数据", "保留 AI 辅助记录并完成人工复读。"))
    history = _history_texts(history_dir)
    history_info = {"configured": bool(history_dir), "compared": len(history), "coverage": "local" if history else "unknown"}
    if history:
        best = max(((_similarity(f"{title}\n{text}", other), name) for name, other in history), default=(0.0, ""))
        scores["originality"] = max(0, round((1 - best[0]) * 100))
        if best[0] >= 0.82:
            findings.append(_finding("near_duplicate", "block", f"与历史内容高度相似：{best[1]}（{best[0]:.0%}）", "全文/标题", "更换核心材料和论证路径，不能只改标题。"))
        elif best[0] >= 0.62:
            findings.append(_finding("homogeneous_content", "revision", f"与历史内容相似度较高：{best[1]}（{best[0]:.0%}）", "全文/标题", "补充新的事实、案例或判断，并删除重复结构。"))
    else:
        findings.append(_finding("history_unavailable", "note", "未配置本地历史内容，无法证明与过往文章不重复", "历史索引", "配置 history_dir 或提供已发布内容索引。"))
    if assets is not None:
        asset_report = check_assets(assets)
        scores["asset_quality"] = asset_report["score"]
        findings.extend(asset_report["findings"])
    report = {"kind": kind, "scores": scores, "findings": findings, "history": history_info,
              "disclaimer": "本报告仅表示检查范围内未发现明显阻断项，不等同于微信官方推荐或审核结果。"}
    return _finish(report, strict)


def check_assets(paths: Sequence[str | Path]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    scores: list[int] = []
    fingerprints: dict[str, str] = {}
    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            findings.append(_finding("missing_asset", "block", f"图片不存在：{path}", str(path), "补齐图片或移除该引用。"))
            continue
        try:
            from PIL import Image, ImageStat
            with Image.open(path) as image:
                digest = hashlib.sha256(image.convert("L").resize((16, 16)).tobytes()).hexdigest()
                if digest in fingerprints:
                    findings.append(_finding("duplicate_asset", "revision", f"图片与另一张素材重复：{fingerprints[digest]}", str(path), "替换为承担不同信息作用的图片。"))
                fingerprints[digest] = str(path)
                width, height = image.size
                if width < 600 or height < 400:
                    findings.append(_finding("low_resolution_asset", "revision", f"图片分辨率偏低：{width}x{height}", str(path), "替换为清晰原图。"))
                variance = ImageStat.Stat(image.convert("L")).var[0]
                scores.append(min(100, round(40 + math.log1p(max(0, variance)) * 8)))
                if variance < 18:
                    findings.append(_finding("blurry_asset_risk", "revision", "图片疑似模糊或空白", str(path), "重新生成或替换图片。"))
        except ImportError:
            findings.append(_finding("asset_check_limited", "note", "未安装 Pillow，未执行图片清晰度检查", str(path), "安装 Pillow 后复检。"))
        except Exception as exc:
            findings.append(_finding("asset_unreadable", "block", f"图片无法读取：{exc}", str(path), "重新导出为 PNG/JPEG。"))
    return {"score": round(sum(scores) / len(scores)) if scores else None, "findings": findings}


def check_generated_asset(path: str | Path) -> dict[str, Any]:
    """Run the strict asset gate immediately after a generated image exists."""
    asset_report = check_assets([path])
    report = {
        "kind": "tie_tu_asset_generation",
        "scores": {"asset_quality": asset_report["score"]},
        "findings": asset_report["findings"],
        "history": {"configured": False, "compared": 0, "coverage": "not_applicable"},
        "disclaimer": "图片生成质量门禁只检查当前图片文件，不等同于微信官方推荐或审核结果。",
    }
    return _finish(report, strict=True)


def repair_content(title: str, body: str, report: Mapping[str, Any]) -> dict[str, Any]:
    repaired_title, repaired_body = str(title or ""), str(body or "")
    changes: list[dict[str, str]] = []
    codes = {item.get("code") for item in report.get("findings", [])}
    if "absolute_title" in codes:
        for source, target in _TITLE_REPAIRS.items():
            if source in repaired_title:
                repaired_title = repaired_title.replace(source, target)
                changes.append({"location": "标题", "before": source, "after": target})
    if "filler_density" in codes:
        for phrase in _FILLER:
            if phrase in repaired_body:
                repaired_body = repaired_body.replace(phrase, "")
                changes.append({"location": "正文", "before": phrase, "after": "删除"})
    automatic = {"absolute_title", "filler_density", "history_unavailable", "ai_assistance_note"}
    manual = [item for item in report.get("findings", []) if item.get("code") not in automatic]
    return {"title": repaired_title, "body": repaired_body, "changes": changes, "manual_findings": manual}


def check_article_file(path: str | Path, *, history_dir: str | Path | None = None, strict: bool = False) -> dict[str, Any]:
    source = read_text(path)
    title = source.splitlines()[0].lstrip("# ").strip() if source else Path(path).stem
    body, ai_assisted, ledger = source, None, SourceLedger()
    if source.startswith("---"):
        parts = source.split("---", 2)
        if len(parts) == 3:
            try:
                import yaml
                meta = yaml.safe_load(parts[1]) or {}
                title, ai_assisted = str(meta.get("title", title)), meta.get("ai_assisted")
                raw_sources = meta.get("sources", [])
                if isinstance(raw_sources, str):
                    raw_sources = [raw_sources]
                for index, item in enumerate(raw_sources or [], 1):
                    if isinstance(item, str):
                        ledger.add(SourceRecord(f"frontmatter-{index}", kind="web", url=item, status="unverified"))
                    elif isinstance(item, Mapping):
                        ledger.add(SourceRecord(str(item.get("source_id", f"frontmatter-{index}")), kind=str(item.get("kind", "web")), title=str(item.get("title", "")), url=str(item.get("url", "")), evidence=str(item.get("evidence", "")), status=str(item.get("status", "unverified"))))
            except Exception:
                pass
            body = parts[2]
    for index, url in enumerate(re.findall(r"https?://[^\s)\]>]+", body), 1):
        ledger.add(SourceRecord(f"body-url-{index}", kind="web", url=url, status="unverified"))
    return check_content(title, body, sources=ledger, history_dir=history_dir, ai_assisted=ai_assisted, strict=strict)
