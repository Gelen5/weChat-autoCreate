"""Brief builders shared by long-form and Tie-Tu workflows."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Optional

from .contracts import ContentBrief, QualityGate, SourceLedger, SourceRecord
from .text_encoding import read_text


def _frontmatter(content: str) -> tuple[Dict[str, Any], str]:
    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    try:
        import yaml
        return yaml.safe_load(parts[1]) or {}, parts[2]
    except Exception:
        return {}, parts[2]


def build_article_brief(file_path: str | Path) -> ContentBrief:
    path = Path(file_path)
    text = read_text(path)
    frontmatter, body = _frontmatter(text)
    title = str(frontmatter.get("title", path.stem))
    source_ledger = SourceLedger()
    for index, url in enumerate(re.findall(r"https?://[^\s)]+", body), 1):
        source_ledger.add(SourceRecord(source_id=f"url-{index}", kind="web", url=url, status="unverified"))
    brief = ContentBrief(
        mode="long_form",
        intent=str(frontmatter.get("intent", "围绕主题完成一篇可发布的微信公众号文章")),
        audience=str(frontmatter.get("audience", "公众号读者")),
        deliverable="微信公众号长文",
        content_type=str(frontmatter.get("content_type", "article")),
        style=str(frontmatter.get("style", frontmatter.get("persona", ""))),
        facts=[{"type": "user_material", "text": body.strip(), "status": "provided"}],
        constraints=["事实与虚构经历分开标记", "发布前完成反AI和微信排版检查"],
        quality_gates=[QualityGate("article", ["intent", "sources", "humanness", "layout", "recommendation_quality"])],
        source_ledger=source_ledger,
        assumptions=["未提供独立受众信息时，使用公众号通用读者作为默认受众"],
        metadata={"path": str(path), "title": title, "body_chars": len(body)},
    )
    brief.approval.set("brief", "approved", "由现有文章文件生成初始 Brief")
    return brief


def build_tie_tu_brief(industry: str, topic: str, title: str, content_type: str,
                       audience: str = "", style: str = "") -> ContentBrief:
    return ContentBrief(
        mode="tie_tu",
        intent=f"围绕{topic}制作图片主导的微信贴图号内容",
        audience=audience or "微信读者",
        deliverable="微信贴图号图片组、短文案和手机预览",
        content_type=content_type,
        style=style,
        constraints=["图片文字后期叠加", "图片来源或生成方式必须可追溯", "发布前通过贴图号质量门禁"],
        quality_gates=[QualityGate("tie_tu", ["card_briefs", "sources", "assets", "mobile_preview", "recommendation_quality"])],
        assumptions=[f"行业：{industry}", f"标题：{title or topic}"],
        metadata={"industry": industry, "topic": topic},
    )
