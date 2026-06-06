"""
主题系统 — 18 套预设主题 + 自定义主题加载
"""

from pathlib import Path
from typing import Any

import yaml


# 18 套内置主题定义
BUILTIN_THEMES = {
    "ink-elegance": {
        "name": "水墨风雅",
        "description": "中国传统水墨画意境，素雅留白",
        "tokens": {
            "color_primary": "#1a1a2e",
            "color_secondary": "#16213e",
            "color_accent": "#e94560",
            "color_text": "#333333",
            "color_text_secondary": "#666666",
            "color_text_light": "#999999",
            "color_bg": "#ffffff",
            "color_bg_soft": "#f7f8fa",
            "color_border": "#e8e8e8",
            "font_family_body": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif",
            "font_size_base": "15px",
        },
        "inline_styles": {
            "h1": "font-size:22px;font-weight:800;color:#1a1a2e;margin:24px 0 16px;line-height:1.4;text-align:center;",
            "h2": "font-size:19px;font-weight:700;color:#1a1a2e;margin:20px 0 12px;padding-left:12px;border-left:4px solid #e94560;line-height:1.4;",
            "h3": "font-size:17px;font-weight:700;color:#333;margin:16px 0 8px;line-height:1.4;",
            "h4": "font-size:16px;font-weight:700;color:#333;margin:12px 0 8px;line-height:1.4;",
            "p": "margin:8px 0;font-size:15px;color:#333;line-height:1.8;letter-spacing:0.5px;",
            "blockquote": "margin:16px 0;padding:12px 16px;background:#f7f8fa;border-left:4px solid #e94560;color:#666;font-size:14px;line-height:1.8;",
            "ul": "margin:8px 0;padding-left:24px;color:#333;",
            "ol": "margin:8px 0;padding-left:24px;color:#333;",
            "li": "margin:6px 0;font-size:15px;line-height:1.8;",
            "code_inline": "background:#f2f2f2;color:#c0341d;padding:2px 5px;border-radius:3px;font-size:13px;font-family:'SF Mono',Menlo,Consolas,monospace;",
            "code_block": "background:none;color:#333;padding:0;font-family:'SF Mono',Menlo,Consolas,monospace;",
            "pre": "margin:16px 0;padding:14px 16px;background:#f7f8fa;border-radius:6px;overflow-x:auto;font-size:13px;line-height:1.7;",
            "strong": "font-weight:700;color:#1a1a2e;",
            "em": "font-style:italic;",
            "a": "color:#e94560;text-decoration:none;",
            "hr": "border:none;border-top:1px solid #e8e8e8;margin:24px 0;",
            "table": "border-collapse:collapse;width:100%;margin:16px 0;font-size:13px;",
            "th": "border:1px solid #e8e8e8;padding:8px 12px;background:#f7f8fa;font-weight:700;text-align:left;",
            "td": "border:1px solid #e8e8e8;padding:8px 12px;",
            "img": "display:block;max-width:100%;margin:16px auto;border-radius:6px;",
        },
    },
    "cyber-neon": {
        "name": "赛博霓虹",
        "description": "未来科技感，深色底+荧光高亮",
        "tokens": {
            "color_primary": "#0f0f23",
            "color_secondary": "#1a1a3e",
            "color_accent": "#00d4ff",
            "color_text": "#e0e0e0",
            "color_text_secondary": "#a0a0b0",
            "color_bg": "#0f0f23",
            "color_bg_soft": "#1a1a3e",
            "color_border": "#2a2a4e",
        },
        "inline_styles": {
            "h1": "font-size:22px;font-weight:800;color:#00d4ff;margin:24px 0 16px;line-height:1.4;text-align:center;text-shadow:0 0 8px rgba(0,212,255,0.3);",
            "h2": "font-size:19px;font-weight:700;color:#00d4ff;margin:20px 0 12px;padding-left:12px;border-left:4px solid #00d4ff;line-height:1.4;",
            "p": "margin:8px 0;font-size:15px;color:#e0e0e0;line-height:1.8;",
            "blockquote": "margin:16px 0;padding:12px 16px;background:#1a1a3e;border-left:4px solid #00d4ff;color:#a0a0b0;font-size:14px;line-height:1.8;",
            "code_inline": "background:#1a1a3e;color:#00d4ff;padding:2px 5px;border-radius:3px;font-size:13px;font-family:'SF Mono',Menlo,Consolas,monospace;",
            "pre": "margin:16px 0;padding:14px 16px;background:#1a1a3e;border:1px solid #2a2a4e;border-radius:6px;overflow-x:auto;font-size:13px;line-height:1.7;",
            "code_block": "background:none;color:#e0e0e0;padding:0;font-family:'SF Mono',Menlo,Consolas,monospace;",
            "strong": "font-weight:700;color:#00d4ff;",
            "a": "color:#00d4ff;text-decoration:none;",
            "hr": "border:none;border-top:1px solid #2a2a4e;margin:24px 0;",
            "img": "display:block;max-width:100%;margin:16px auto;border-radius:6px;border:1px solid #2a2a4e;",
            "table": "border-collapse:collapse;width:100%;margin:16px 0;font-size:13px;color:#e0e0e0;",
            "th": "border:1px solid #2a2a4e;padding:8px 12px;background:#1a1a3e;font-weight:700;color:#00d4ff;text-align:left;",
            "td": "border:1px solid #2a2a4e;padding:8px 12px;background:#0f0f23;",
        },
    },
    "morning-mist": {
        "name": "晨雾轻纱",
        "description": "柔和渐变，莫兰迪色调",
        "tokens": {
            "color_primary": "#6b7b8d",
            "color_accent": "#a8b5c2",
            "color_text": "#4a5568",
            "color_bg": "#f5f0eb",
            "color_bg_soft": "#ede6de",
        },
        "inline_styles": {
            "h1": "font-size:22px;font-weight:800;color:#4a5568;margin:24px 0 16px;line-height:1.4;text-align:center;",
            "h2": "font-size:19px;font-weight:700;color:#6b7b8d;margin:20px 0 12px;padding-left:12px;border-left:4px solid #a8b5c2;line-height:1.4;",
            "p": "margin:8px 0;font-size:15px;color:#4a5568;line-height:1.8;",
            "blockquote": "margin:16px 0;padding:12px 16px;background:#ede6de;border-left:4px solid #a8b5c2;color:#6b7b8d;font-size:14px;line-height:1.8;",
            "strong": "font-weight:700;color:#4a5568;",
            "a": "color:#6b7b8d;text-decoration:none;",
            "hr": "border:none;border-top:1px solid #d4cdc4;margin:24px 0;",
        },
    },
    "red-classic": {
        "name": "红色经典",
        "description": "政务/党建风格，庄重大气",
        "tokens": {
            "color_primary": "#8b0000",
            "color_accent": "#dc143c",
            "color_text": "#333333",
            "color_bg": "#ffffff",
            "color_bg_soft": "#fff5f5",
        },
        "inline_styles": {
            "h1": "font-size:22px;font-weight:800;color:#8b0000;margin:24px 0 16px;line-height:1.4;text-align:center;",
            "h2": "font-size:19px;font-weight:700;color:#8b0000;margin:20px 0 12px;padding-left:12px;border-left:4px solid #dc143c;line-height:1.4;",
            "p": "margin:8px 0;font-size:15px;color:#333;line-height:1.8;",
            "blockquote": "margin:16px 0;padding:12px 16px;background:#fff5f5;border-left:4px solid #dc143c;color:#666;font-size:14px;line-height:1.8;",
            "strong": "font-weight:700;color:#8b0000;",
            "a": "color:#dc143c;text-decoration:none;",
        },
    },
    "tech-minimal": {
        "name": "极简科技",
        "description": "黑白灰+蓝，工程师审美",
        "tokens": {
            "color_primary": "#1a1a1a",
            "color_accent": "#2563eb",
            "color_text": "#1a1a1a",
            "color_bg": "#ffffff",
            "color_bg_soft": "#f8f9fa",
        },
        "inline_styles": {
            "h1": "font-size:22px;font-weight:800;color:#1a1a1a;margin:24px 0 16px;line-height:1.4;",
            "h2": "font-size:19px;font-weight:700;color:#1a1a1a;margin:20px 0 12px;padding-left:12px;border-left:4px solid #2563eb;line-height:1.4;",
            "p": "margin:8px 0;font-size:15px;color:#1a1a1a;line-height:1.8;",
            "blockquote": "margin:16px 0;padding:12px 16px;background:#f8f9fa;border-left:4px solid #2563eb;color:#666;font-size:14px;line-height:1.8;",
            "code_inline": "background:#f1f3f5;color:#e03131;padding:2px 5px;border-radius:3px;font-size:13px;font-family:'SF Mono',Consolas,monospace;",
            "pre": "margin:16px 0;padding:14px 16px;background:#f8f9fa;border-radius:6px;overflow-x:auto;font-size:13px;line-height:1.7;",
            "strong": "font-weight:700;color:#1a1a1a;",
            "a": "color:#2563eb;text-decoration:none;",
        },
    },
}


class Theme:
    """主题对象"""

    def __init__(self, name: str, data: dict[str, Any]):
        self.name = name
        self.display_name = data.get("name", name)
        self.description = data.get("description", "")
        self.tokens = data.get("tokens", {})
        self.inline_styles = data.get("inline_styles", {})

    def get_style(self, element: str) -> str:
        """获取元素的 inline style"""
        return self.inline_styles.get(element, "")

    def get_token(self, key: str, default: str = "") -> str:
        """获取设计 token"""
        return self.tokens.get(key, default)


def load_theme(name: str, themes_dir: str | Path | None = None) -> Theme:
    """加载主题（内置优先，然后从文件加载）"""
    # 1. 内置主题
    if name in BUILTIN_THEMES:
        return Theme(name, BUILTIN_THEMES[name])

    # 2. 从文件加载
    if themes_dir is None:
        themes_dir = Path(__file__).parent.parent / "themes"
    else:
        themes_dir = Path(themes_dir)

    theme_file = themes_dir / f"{name}.yaml"
    if theme_file.exists():
        with open(theme_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return Theme(name, data)

    # 3. 找不到则回退到默认主题
    return Theme("ink-elegance", BUILTIN_THEMES["ink-elegance"])


def list_themes(themes_dir: str | Path | None = None) -> list[tuple[str, str]]:
    """列出所有可用主题"""
    themes = []

    # 内置主题
    for name, data in BUILTIN_THEMES.items():
        themes.append((name, data.get("description", "")))

    # 文件主题
    if themes_dir is None:
        themes_dir = Path(__file__).parent.parent / "themes"
    else:
        themes_dir = Path(themes_dir)

    if themes_dir.exists():
        for f in themes_dir.glob("*.yaml"):
            name = f.stem
            if name not in BUILTIN_THEMES:
                with open(f, "r", encoding="utf-8") as fh:
                    data = yaml.safe_load(fh) or {}
                desc = data.get("description", "(自定义主题)")
                themes.append((name, desc))

    return themes
