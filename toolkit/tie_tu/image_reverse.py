"""Measured image-reference analysis for Tie-Tu visual planning."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def analyze_reference_image(path: str | Path) -> Dict[str, Any]:
    target = Path(path)
    if not target.exists():
        raise FileNotFoundError(str(target))
    try:
        from PIL import Image, ImageStat
    except ImportError as exc:
        raise RuntimeError("图片反向分析需要 Pillow") from exc
    with Image.open(target) as image:
        bands = image.getbands()
        rgb = image.convert("RGB")
        width, height = rgb.size
        stat = ImageStat.Stat(rgb)
        colors = rgb.quantize(colors=8).convert("RGB").getcolors(width * height) or []
        colors.sort(reverse=True)
        palette = [{"rgb": list(color), "share": round(count / (width * height), 4)} for count, color in colors[:8]]
    return {
        "path": str(target.resolve()),
        "measurement_status": "measured",
        "dimensions": {"width": width, "height": height},
        "aspect_ratio": round(width / height, 4) if height else 0,
        "orientation": "portrait" if height > width else "landscape" if width > height else "square",
        "dominant_palette": palette,
        "brightness_mean": round(sum(stat.mean) / 3, 2),
        "contrast_stddev": round(sum(stat.stddev) / 3, 2),
        "has_alpha": "A" in bands,
        "layout_observation": "需要人工或视觉模型补充主体、文字安全区和视线动线",
        "limitations": ["不执行OCR", "不臆测图片中的文字、来源或事实", "主体与版式语义需结合视觉模型复核"],
    }


def attach_reference_analysis(plan: Any, path: str | Path) -> Dict[str, Any]:
    analysis = analyze_reference_image(path)
    plan.content_brief.metadata["reference_image"] = analysis
    plan.metadata = getattr(plan, "metadata", {})
    plan.metadata["reference_image"] = analysis
    return analysis
