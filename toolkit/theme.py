#!/usr/bin/env python3
"""YAML主题引擎"""

import json
import os
import re
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

THEMES_DIR = "themes"

# 默认主题
DEFAULT_THEME: Dict[str, Any] = {
    "name": "default",
    "primary_color": "#333333",
    "secondary_color": "#666666",
    "background_color": "#ffffff",
    "accent_color": "#1a73e8",
    "font_family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    "code_theme": "dark",
    "aigc_declaration": False,
}


def _load_yaml(filepath: str) -> Dict[str, Any]:
    """加载YAML文件"""
    try:
        import yaml
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        return _parse_simple_yaml(filepath)


def _parse_simple_yaml(filepath: str) -> Dict[str, Any]:
    """简单YAML解析（无PyYAML依赖时的降级方案）"""
    result: Dict[str, Any] = {}
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            match = re.match(r'^(\w[\w_]*):\s*(.*)$', line)
            if match:
                key = match.group(1)
                value = match.group(2).strip()
                # 去引号
                if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                # 类型转换
                if value.lower() == "true":
                    value = True
                elif value.lower() == "false":
                    value = False
                elif re.match(r'^\d+$', value):
                    value = int(value)
                elif re.match(r'^\d+\.\d+$', value):
                    value = float(value)
                result[key] = value
    return result


def load_theme(name: str) -> Dict[str, Any]:
    """加载指定主题"""
    if name == "default":
        return DEFAULT_THEME.copy()

    # 搜索路径
    search_paths = [
        os.path.join(THEMES_DIR, f"{name}.yaml"),
        os.path.join(THEMES_DIR, f"{name}.yml"),
        os.path.join(THEMES_DIR, f"{name}.json"),
        os.path.join(os.path.dirname(__file__), "..", THEMES_DIR, f"{name}.yaml"),
        os.path.join(os.path.dirname(__file__), "..", THEMES_DIR, f"{name}.yml"),
        os.path.join(os.path.dirname(__file__), "..", THEMES_DIR, f"{name}.json"),
    ]

    for theme_path in search_paths:
        if os.path.exists(theme_path):
            try:
                if theme_path.endswith(".json"):
                    with open(theme_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                else:
                    data = _load_yaml(theme_path)

                # 合并默认主题
                merged = DEFAULT_THEME.copy()
                merged.update(data)
                merged["name"] = name
                return merged
            except Exception as e:
                logger.warning(f"加载主题 {name} 失败: {e}")

    logger.warning(f"主题 {name} 未找到，使用默认主题")
    return DEFAULT_THEME.copy()


def list_themes() -> Dict[str, Dict[str, Any]]:
    """列出所有可用主题"""
    themes: Dict[str, Dict[str, Any]] = {"default": DEFAULT_THEME.copy()}

    # 搜索主题目录
    theme_dirs = [
        THEMES_DIR,
        os.path.join(os.path.dirname(__file__), "..", THEMES_DIR),
    ]

    for theme_dir in theme_dirs:
        if not os.path.isdir(theme_dir):
            continue

        for filename in os.listdir(theme_dir):
            if filename.endswith((".yaml", ".yml", ".json")):
                name = os.path.splitext(filename)[0]
                filepath = os.path.join(theme_dir, filename)
                try:
                    if filename.endswith(".json"):
                        with open(filepath, "r", encoding="utf-8") as f:
                            data = json.load(f)
                    else:
                        data = _load_yaml(filepath)
                    themes[name] = data
                except Exception as e:
                    logger.warning(f"加载主题 {filename} 失败: {e}")

    return themes


def apply_theme(html: str, theme: Dict[str, Any]) -> str:
    """将主题应用到HTML"""
    primary = theme.get("primary_color", "#333333")
    secondary = theme.get("secondary_color", "#666666")
    accent = theme.get("accent_color", "#1a73e8")
    background = theme.get("background_color", "#ffffff")
    font_family = theme.get("font_family", "-apple-system, sans-serif")

    # 替换颜色
    color_map = {
        "#333333": primary,
        "#666666": secondary,
        "#1a73e8": accent,
        "#ffffff": background,
    }

    for old_color, new_color in color_map.items():
        html = html.replace(old_color, new_color)

    # 替换字体
    html = re.sub(
        r"font-family:\s*[^;]+;?",
        f"font-family: {font_family};",
        html,
    )

    return html


def create_theme_file(name: str, data: Dict[str, Any], output_dir: str = THEMES_DIR) -> str:
    """创建主题文件"""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"{name}.yaml")

    try:
        import yaml
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    except ImportError:
        # 降级到手动YAML
        with open(filepath, "w", encoding="utf-8") as f:
            for key, value in data.items():
                if isinstance(value, str):
                    f.write(f"{key}: '{value}'\n")
                elif isinstance(value, bool):
                    f.write(f"{key}: {'true' if value else 'false'}\n")
                elif isinstance(value, (int, float)):
                    f.write(f"{key}: {value}\n")
                else:
                    f.write(f"{key}: '{value}'\n")

    return filepath
