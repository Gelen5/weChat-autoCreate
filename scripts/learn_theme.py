#!/usr/bin/env python3
"""排版主题学习 - 从URL提取排版主题 + 颜色系统推断 + 生成theme YAML"""

import argparse
import json
import re
import sys
import logging
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
}


def fetch_html(url: str) -> str:
    """获取网页HTML"""
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.text


def extract_colors(html: str) -> Dict[str, List[str]]:
    """从HTML中提取颜色"""
    colors = {
        "hex": [],
        "rgb": [],
        "named": [],
    }

    # HEX颜色
    hex_pattern = r'#(?:[0-9a-fA-F]{3}){1,2}\b'
    colors["hex"] = re.findall(hex_pattern, html)

    # RGB颜色
    rgb_pattern = r'rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)'
    for match in re.finditer(rgb_pattern, html):
        colors["rgb"].append(f"rgb({match.group(1)},{match.group(2)},{match.group(3)})")

    # 内联样式中的颜色
    style_pattern = r'style="[^"]*color:\s*([^;"]+)[^"]*"'
    for match in re.finditer(style_pattern, html):
        color_val = match.group(1).strip()
        if color_val.startswith("#"):
            colors["hex"].append(color_val)
        elif color_val.startswith("rgb"):
            colors["rgb"].append(color_val)

    # 背景色
    bg_pattern = r'background(?:-color)?:\s*([^;"]+)'
    for match in re.finditer(bg_pattern, html):
        color_val = match.group(1).strip()
        if color_val.startswith("#"):
            colors["hex"].append(color_val)
        elif color_val.startswith("rgb"):
            colors["rgb"].append(color_val)

    return colors


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """HEX转RGB"""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hsl(r: int, g: int, b: int) -> Tuple[float, float, float]:
    """RGB转HSL"""
    r, g, b = r / 255, g / 255, b / 255
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    l = (max_c + min_c) / 2

    if max_c == min_c:
        h = s = 0
    else:
        d = max_c - min_c
        s = d / (2 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
        if max_c == r:
            h = (g - b) / d + (6 if g < b else 0)
        elif max_c == g:
            h = (b - r) / d + 2
        else:
            h = (r - g) / d + 4
        h /= 6

    return round(h * 360, 1), round(s * 100, 1), round(l * 100, 1)


def classify_colors(hex_colors: List[str]) -> Dict[str, Any]:
    """颜色系统推断 - 分类主色、辅色、背景色等"""
    if not hex_colors:
        return {"primary": "#333333", "secondary": "#666666", "background": "#ffffff"}

    # 统计频率
    color_freq = Counter(hex_colors)
    # 标准化为6位HEX
    normalized = Counter()
    for color, count in color_freq.items():
        c = color.lstrip("#")
        if len(c) == 3:
            c = "".join(x * 2 for x in c)
        normalized[f"#{c.lower()}"] += count

    # 按HSL分类
    dark_colors = []
    mid_colors = []
    light_colors = []
    accent_colors = []

    for color, count in normalized.most_common(20):
        try:
            rgb = hex_to_rgb(color)
            h, s, l = rgb_to_hsl(*rgb)

            if l < 30:
                dark_colors.append((color, count, (h, s, l)))
            elif l > 80:
                light_colors.append((color, count, (h, s, l)))
            elif s > 40:
                accent_colors.append((color, count, (h, s, l)))
            else:
                mid_colors.append((color, count, (h, s, l)))
        except (ValueError, IndexError):
            continue

    primary = dark_colors[0][0] if dark_colors else "#333333"
    secondary = mid_colors[0][0] if mid_colors else "#666666"
    background = light_colors[0][0] if light_colors else "#ffffff"
    accent = accent_colors[0][0] if accent_colors else secondary

    return {
        "primary": primary,
        "secondary": secondary,
        "background": background,
        "accent": accent,
        "dark_palette": [c[0] for c in dark_colors[:5]],
        "light_palette": [c[0] for c in light_colors[:5]],
        "accent_palette": [c[0] for c in accent_colors[:5]],
    }


def extract_typography(html: str) -> Dict[str, Any]:
    """提取排版信息"""
    typography = {
        "font_families": [],
        "font_sizes": [],
        "line_heights": [],
    }

    # 字体
    font_pattern = r'font-family:\s*([^;"]+)'
    for match in re.finditer(font_pattern, html):
        typography["font_families"].append(match.group(1).strip())

    # 字号
    size_pattern = r'font-size:\s*(\d+(?:\.\d+)?)(px|em|rem)'
    for match in re.finditer(size_pattern, html):
        value = float(match.group(1))
        unit = match.group(2)
        typography["font_sizes"].append(f"{value}{unit}")

    # 行高
    lh_pattern = r'line-height:\s*(\d+(?:\.\d+)?)(px|em|rem|%)?'
    for match in re.finditer(lh_pattern, html):
        typography["line_heights"].append(match.group(0).split(":")[1].strip())

    return typography


def extract_spacing(html: str) -> Dict[str, Any]:
    """提取间距信息"""
    spacing = {"margins": [], "paddings": []}

    margin_pattern = r'margin(?:-(?:top|right|bottom|left))?:\s*(\d+(?:\.\d+)?)(px|em|rem)'
    for match in re.finditer(margin_pattern, html):
        spacing["margins"].append(f"{match.group(1)}{match.group(2)}")

    padding_pattern = r'padding(?:-(?:top|right|bottom|left))?:\s*(\d+(?:\.\d+)?)(px|em|rem)'
    for match in re.finditer(padding_pattern, html):
        spacing["paddings"].append(f"{match.group(1)}{match.group(2)}")

    return spacing


def generate_theme_yaml(colors: Dict[str, Any], typography: Dict[str, Any], spacing: Dict[str, Any]) -> str:
    """生成theme YAML"""
    yaml_lines = [
        "# 自动提取的排版主题",
        f"primary_color: '{colors.get('primary', '#333333')}'",
        f"secondary_color: '{colors.get('secondary', '#666666')}'",
        f"background_color: '{colors.get('background', '#ffffff')}'",
        f"accent_color: '{colors.get('accent', '#1a73e8')}'",
        "",
        "colors:",
    ]

    for palette_name in ["dark_palette", "light_palette", "accent_palette"]:
        palette = colors.get(palette_name, [])
        if palette:
            yaml_lines.append(f"  {palette_name}:")
            for c in palette:
                yaml_lines.append(f"    - '{c}'")

    # 字体
    font_families = list(set(typography.get("font_families", [])))
    if font_families:
        yaml_lines.append("")
        yaml_lines.append("fonts:")
        for f in font_families[:5]:
            yaml_lines.append(f"  - '{f}'")
    else:
        yaml_lines.extend([
            "",
            "fonts:",
            "  - 'system-ui'",
            "  - '-apple-system'",
            "  - 'sans-serif'",
        ])

    # 间距
    margins = list(set(spacing.get("margins", [])))
    paddings = list(set(spacing.get("paddings", [])))
    if margins or paddings:
        yaml_lines.append("")
        yaml_lines.append("spacing:")
        if margins:
            yaml_lines.append(f"  common_margins: {json.dumps(margins[:5])}")
        if paddings:
            yaml_lines.append(f"  common_paddings: {json.dumps(paddings[:5])}")

    return "\n".join(yaml_lines)


def main():
    parser = argparse.ArgumentParser(description="排版主题学习")
    parser.add_argument("url", help="微信文章URL")
    parser.add_argument("--output", "-o", help="输出YAML文件路径")
    parser.add_argument("--json", action="store_true", help="JSON输出")
    args = parser.parse_args()

    logger.info(f"获取: {args.url}")
    html = fetch_html(args.url)

    # 提取颜色
    colors_raw = extract_colors(html)
    logger.info(f"提取颜色: HEX={len(colors_raw['hex'])}, RGB={len(colors_raw['rgb'])}")

    # 颜色系统推断
    color_system = classify_colors(colors_raw["hex"])
    logger.info(f"主色: {color_system['primary']}, 辅色: {color_system['secondary']}")

    # 排版
    typography = extract_typography(html)
    spacing = extract_spacing(html)

    # 生成YAML
    yaml_content = generate_theme_yaml(color_system, typography, spacing)

    result = {
        "url": args.url,
        "colors": color_system,
        "typography": typography,
        "spacing": spacing,
        "yaml": yaml_content,
    }

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(yaml_content)
        logger.info(f"主题已保存: {args.output}")

    if args.json:
        # 不输出yaml字段到JSON（冗余）
        display = {k: v for k, v in result.items() if k != "yaml"}
        print(json.dumps(display, ensure_ascii=False, indent=2))
    else:
        print(f"主色: {color_system['primary']}")
        print(f"辅色: {color_system['secondary']}")
        print(f"背景色: {color_system['background']}")
        print(f"强调色: {color_system['accent']}")
        if not args.output:
            print(f"\n--- Theme YAML ---\n{yaml_content}")


if __name__ == "__main__":
    main()
