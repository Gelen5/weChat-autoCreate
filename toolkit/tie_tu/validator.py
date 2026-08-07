"""Quality checks for Tie-Tu card plans and local assets."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .models import TieTuPlan
from .workflow import validate_card_briefs


def _image_size(path: Path):
    try:
        from PIL import Image
        with Image.open(path) as image:
            return image.size
    except Exception:
        return None


def validate_plan(plan: TieTuPlan) -> Dict[str, Any]:
    errors = []
    warnings = []
    if plan.mode != "tie_tu":
        errors.append("mode 必须为 tie_tu")
    if len(plan.cards) < 1:
        errors.append("贴图号至少需要 1 张卡片；不设置图片数量上限")
    if plan.ratio != "3:4":
        warnings.append("建议使用 3:4 竖幅贴图比例")
    if len(plan.copy) > 300:
        warnings.append("短文案超过 300 字，建议压缩")
    seen = set()
    for card in plan.cards:
        if card.index in seen:
            errors.append(f"卡片序号重复: {card.index}")
        seen.add(card.index)
        if len(card.overlay_text) > 60:
            warnings.append(f"第 {card.index} 张叠加文字较长")
        if card.image_path:
            path = Path(card.image_path)
            if not path.exists():
                errors.append(f"第 {card.index} 张图片不存在: {card.image_path}")
            else:
                size = _image_size(path)
                if size and abs((size[0] / size[1]) - (3 / 4)) > 0.03:
                    warnings.append(f"第 {card.index} 张图片不是接近 3:4: {size[0]}x{size[1]}")
    if not plan.sources:
        warnings.append("尚未记录图片或事实来源")
    from .portrait_quality import validate_portrait_plan
    portrait_report = validate_portrait_plan(plan)
    errors.extend(portrait_report["errors"])
    warnings.extend(portrait_report["warnings"])
    brief_report = validate_card_briefs(plan)
    errors.extend(brief_report["errors"])
    warnings.extend(brief_report["warnings"])
    plan.quality_gate.findings = [
        {"check": "card_briefs", "passed": brief_report["ok"], "detail": "; ".join(brief_report["errors"] + brief_report["warnings"])}
    ]
    plan.quality_gate.status = "passed" if not errors else "failed"
    return {"ok": not errors, "errors": errors, "warnings": warnings}
