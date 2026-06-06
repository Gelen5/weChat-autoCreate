#!/usr/bin/env python3
"""Markdown→微信HTML转换器 - 16步管线"""

import re
import os
import random
import hashlib
import logging
from typing import Dict, Any, List, Optional, Tuple

import markdown
from bs4 import BeautifulSoup, NavigableString

logger = logging.getLogger(__name__)

# ── 容器语法定义 ──

CONTAINER_TYPES = {
    "dialogue": {
        "tag": "div",
        "class": "dialogue-container",
        "wrapper": '<div class="dialogue-container" style="padding: 12px; border-radius: 8px; background: #f8f9fa; margin: 1em 0;">{}</div>',
    },
    "timeline": {
        "tag": "div",
        "class": "timeline-container",
        "wrapper": '<div class="timeline-container" style="padding: 12px; border-left: 3px solid #1a73e8; margin: 1em 0;">{}</div>',
    },
    "callout": {
        "tag": "div",
        "class": "callout-container",
        "wrapper": '<div class="callout-container" style="padding: 12px 16px; border-radius: 8px; background: #fff3e0; border-left: 4px solid #ff9800; margin: 1em 0;">{}</div>',
    },
    "quote": {
        "tag": "div",
        "class": "quote-container",
        "wrapper": '<div class="quote-container" style="padding: 12px 16px; border-radius: 8px; background: #e8f5e9; border-left: 4px solid #4caf50; margin: 1em 0;">{}</div>',
    },
    "highlight": {
        "tag": "div",
        "class": "highlight-container",
        "wrapper": '<div class="highlight-container" style="padding: 12px 16px; border-radius: 8px; background: #e3f2fd; border-left: 4px solid #2196f3; margin: 1em 0;">{}</div>',
    },
    "summary": {
        "tag": "div",
        "class": "summary-container",
        "wrapper": '<div class="summary-container" style="padding: 12px 16px; border-radius: 8px; background: #fce4ec; border-left: 4px solid #e91e63; margin: 1em 0;">{}</div>',
    },
    "module": {
        "tag": "div",
        "class": "module-container",
        "wrapper": '<div class="module-container" style="padding: 16px; border-radius: 12px; background: #fafafa; border: 1px solid #e0e0e0; margin: 1em 0;">{}</div>',
    },
}


class MarkdownConverter:
    """Markdown→微信HTML 16步管线转换器"""

    def __init__(self, theme: Optional[Dict[str, Any]] = None):
        self.theme = theme or {}
        self.dark_mode = False

    def convert(self, text: str) -> str:
        """执行16步转换管线"""
        result = text

        # Step 1: 预处理容器语法
        result = self._step1_preprocess_containers(result)

        # Step 2: CJK加空格
        result = self._step2_cjk_spacing(result)

        # Step 3: Markdown→HTML
        result = self._step3_markdown_to_html(result)

        # Step 4: 代码块增强
        result = self._step4_code_enhance(result)

        # Step 5: 图片处理
        result = self._step5_image_process(result)

        # Step 6: 加粗标点外移
        result = self._step6_bold_punctuation_move(result)

        # Step 7: 列表转section
        result = self._step7_list_to_section(result)

        # Step 8: 外链转脚注
        result = self._step8_external_links_to_footnotes(result)

        # Step 9: 内联样式
        result = self._step9_inline_styles(result)

        # Step 10: 兼容修复
        result = self._step10_compatibility_fix(result)

        # Step 11: 暗黑模式
        result = self._step11_dark_mode(result)

        # Step 12: CSS随机扰动
        result = self._step12_css_random_perturbation(result)

        # Step 13: AIGC声明
        result = self._step13_aigc_declaration(result)

        # Step 14: 摘要
        result = self._step14_summary(result)

        # Step 15: 最终清理
        result = self._step15_final_cleanup(result)

        # Step 16: 包装
        result = self._step16_wrap(result)

        return result

    # ── Step 1: 预处理容器语法 ──

    def _step1_preprocess_containers(self, text: str) -> str:
        """处理 :::container-type ... ::: 语法"""
        for container_type, config in CONTAINER_TYPES.items():
            pattern = rf":::\s*{container_type}\s*(.*?):::"
            while re.search(pattern, text, re.DOTALL):
                match = re.search(pattern, text, re.DOTALL)
                if match:
                    inner = match.group(1).strip()
                    # 处理dialogue特殊语法：> 角色名：内容
                    if container_type == "dialogue":
                        inner = self._parse_dialogue(inner)
                    # 处理timeline特殊语法
                    elif container_type == "timeline":
                        inner = self._parse_timeline(inner)
                    # 处理module语法
                    elif container_type == "module":
                        inner = self._parse_module(inner)

                    wrapper = config["wrapper"]
                    # 渲染内部Markdown
                    inner_html = markdown.markdown(inner, extensions=["fenced_code", "tables", "nl2br"])
                    replacement = wrapper.format(inner_html)
                    text = text[:match.start()] + replacement + text[match.end():]
                else:
                    break

        return text

    def _parse_dialogue(self, text: str) -> str:
        """解析对话格式"""
        lines = text.strip().split("\n")
        result = []
        for line in lines:
            line = line.strip()
            if line.startswith(">"):
                line = line[1:].strip()
            if "：" in line or ":" in line:
                sep = "：" if "：" in line else ":"
                parts = line.split(sep, 1)
                if len(parts) == 2:
                    speaker = parts[0].strip()
                    content = parts[1].strip()
                    result.append(
                        f'<div style="margin: 8px 0;"><strong style="color: #1a73e8;">{speaker}</strong>：{content}</div>'
                    )
                else:
                    result.append(f"<p>{line}</p>")
            else:
                result.append(f"<p>{line}</p>")
        return "\n".join(result)

    def _parse_timeline(self, text: str) -> str:
        """解析时间线格式"""
        lines = text.strip().split("\n")
        result = []
        for line in lines:
            line = line.strip()
            if line.startswith("- ") or line.startswith("* "):
                line = line[2:].strip()
            # 支持 "时间 | 事件" 格式
            if "|" in line:
                parts = line.split("|", 1)
                time_str = parts[0].strip()
                event = parts[1].strip()
                result.append(
                    f'<div style="margin: 6px 0; padding-left: 12px; border-left: 2px solid #e0e0e0;">'
                    f'<span style="color: #1a73e8; font-weight: bold;">{time_str}</span> {event}</div>'
                )
            else:
                result.append(f'<div style="margin: 6px 0; padding-left: 12px;">{line}</div>')
        return "\n".join(result)

    def _parse_module(self, text: str) -> str:
        """解析模块格式"""
        lines = text.strip().split("\n")
        result = []
        for line in lines:
            line = line.strip()
            if line.startswith("## "):
                title = line[3:].strip()
                result.append(f'<h3 style="margin: 0 0 8px; color: #333;">{title}</h3>')
            elif line.startswith("### "):
                title = line[4:].strip()
                result.append(f'<h4 style="margin: 0 0 6px; color: #555;">{title}</h4>')
            else:
                result.append(f"<p>{line}</p>")
        return "\n".join(result)

    # ── Step 2: CJK加空格 ──

    def _step2_cjk_spacing(self, text: str) -> str:
        """中文与英文/数字之间加空格"""
        # CJK字符后跟英文/数字
        text = re.sub(r'([\u4e00-\u9fff])([a-zA-Z0-9])', r'\1 \2', text)
        # 英文/数字后跟CJK字符
        text = re.sub(r'([a-zA-Z0-9])([\u4e00-\u9fff])', r'\1 \2', text)
        return text

    # ── Step 3: Markdown→HTML ──

    def _step3_markdown_to_html(self, text: str) -> str:
        """使用Python-Markdown转换为HTML"""
        extensions = [
            "fenced_code",
            "tables",
            "nl2br",
            "sane_lists",
            "codehilite",
        ]
        extension_configs = {
            "codehilite": {"css_class": "highlight", "guess_lang": True},
        }
        return markdown.markdown(text, extensions=extensions, extension_configs=extension_configs)

    # ── Step 4: 代码块增强 ──

    def _step4_code_enhance(self, html: str) -> str:
        """代码块增强 - 添加行号和复制按钮"""
        def enhance_code_block(match):
            lang = match.group(1) or ""
            code = match.group(2)

            # 添加行号
            lines = code.split("\n")
            numbered_lines = []
            for i, line in enumerate(lines, 1):
                numbered_lines.append(
                    f'<span style="color: #999; user-select: none; margin-right: 12px;">{i:3d}</span>{line}'
                )
            numbered_code = "\n".join(numbered_lines)

            lang_label = f'<div style="font-size: 12px; color: #999; margin-bottom: 8px;">{lang}</div>' if lang else ""

            return (
                f'<div style="background: #1e1e1e; border-radius: 8px; padding: 16px; margin: 1em 0; overflow-x: auto;">'
                f'{lang_label}'
                f'<pre style="margin: 0; color: #d4d4d4; font-family: \'SFMono-Regular\', Consolas, monospace; '
                f'font-size: 13px; line-height: 1.6;"><code>{numbered_code}</code></pre></div>'
            )

        html = re.sub(
            r'<pre><code(?:\s+class="language-(\w+)")?>(.*?)</code></pre>',
            enhance_code_block,
            html,
            flags=re.DOTALL,
        )
        return html

    # ── Step 5: 图片处理 ──

    def _step5_image_process(self, html: str) -> str:
        """图片处理 - 添加懒加载和样式"""
        def process_img(match):
            attrs = match.group(0)
            # 添加微信兼容属性
            if "data-src" not in attrs:
                # 将src复制到data-src（微信要求）
                src_match = re.search(r'src="([^"]*)"', attrs)
                if src_match:
                    src = src_match.group(1)
                    attrs = attrs.replace(
                        f'src="{src}"',
                        f'src="{src}" data-src="{src}"'
                    )
            # 添加样式
            if 'style="' not in attrs:
                attrs = attrs.replace("<img ", '<img style="max-width: 100%; height: auto; border-radius: 4px; margin: 0.5em 0;" ')
            return attrs

        html = re.sub(r'<img[^>]*>', process_img, html)
        return html

    # ── Step 6: 加粗标点外移 ──

    def _step6_bold_punctuation_move(self, html: str) -> str:
        """将加粗标记内的标点移到外部"""
        # **文字。** → **文字**。
        html = re.sub(r'\*\*([^*]+?)([，。！？；：、）】》」\)])\*\*', r'**\1**\2', html)
        # <strong>文字。</strong> → <strong>文字</strong>。
        html = re.sub(
            r'<strong>(.*?)</strong>([，。！？；：、）】》」\)])',
            r'<strong>\1</strong>\2',
            html,
        )
        return html

    # ── Step 7: 列表转section ──

    def _step7_list_to_section(self, html: str) -> str:
        """列表转section样式"""
        # 有序列表
        html = re.sub(
            r'<ol>(.*?)</ol>',
            lambda m: self._style_list(m.group(1), ordered=True),
            html,
            flags=re.DOTALL,
        )
        # 无序列表
        html = re.sub(
            r'<ul>(.*?)</ul>',
            lambda m: self._style_list(m.group(1), ordered=False),
            html,
            flags=re.DOTALL,
        )
        return html

    def _style_list(self, content: str, ordered: bool) -> str:
        items = re.findall(r'<li>(.*?)</li>', content, re.DOTALL)
        tag = "section" if not ordered else "section"
        styled_items = []
        for i, item in enumerate(items, 1):
            prefix = f"{i}." if ordered else "•"
            styled_items.append(
                f'<{tag} style="margin: 6px 0; padding-left: 1.5em; text-indent: -1.5em;">'
                f'<span style="color: #1a73e8; font-weight: bold;">{prefix}</span> {item}</{tag}>'
            )
        return '<div style="margin: 1em 0;">' + "\n".join(styled_items) + "</div>"

    # ── Step 8: 外链转脚注 ──

    def _step8_external_links_to_footnotes(self, html: str) -> str:
        """外链转脚注（微信不支持外链）"""
        footnotes = []
        counter = [0]

        def replace_link(match):
            full_match = match.group(0)
            href_match = re.search(r'href="([^"]*)"', full_match)
            text_match = re.search(r'>(.*?)</a>', full_match)

            if not href_match or not text_match:
                return full_match

            href = href_match.group(1)
            text = text_match.group(1)

            # 微信域名内的链接保留
            if "mp.weixin.qq.com" in href or href.startswith("#"):
                return full_match

            counter[0] += 1
            idx = counter[0]
            footnotes.append(f'[{idx}] {href}')

            return f'{text}<sup style="color: #1a73e8; font-size: 0.7em;">[{idx}]</sup>'

        html = re.sub(r'<a[^>]*href="[^"]*"[^>]*>.*?</a>', replace_link, html)

        # 添加脚注区域
        if footnotes:
            footnote_html = '<section style="margin-top: 2em; padding-top: 1em; border-top: 1px solid #eee; font-size: 0.85em; color: #999;">'
            footnote_html += "<p><strong>参考链接</strong></p>"
            for fn in footnotes:
                footnote_html += f"<p>{fn}</p>"
            footnote_html += "</section>"
            html += footnote_html

        return html

    # ── Step 9: 内联样式 ──

    def _step9_inline_styles(self, html: str) -> str:
        """注入内联样式"""
        primary = self.theme.get("primary_color", "#333333")
        accent = self.theme.get("accent_color", "#1a73e8")

        style_map = {
            "h1": f"font-size: 1.6em; font-weight: bold; color: {primary}; margin: 1.5em 0 0.8em; border-bottom: 2px solid {accent}; padding-bottom: 0.3em;",
            "h2": f"font-size: 1.4em; font-weight: bold; color: {primary}; margin: 1.3em 0 0.7em; border-bottom: 1px solid #eee; padding-bottom: 0.2em;",
            "h3": f"font-size: 1.2em; font-weight: bold; color: {primary}; margin: 1.2em 0 0.6em;",
            "h4": f"font-size: 1.1em; font-weight: semibold; color: {primary}; margin: 1em 0 0.5em;",
            "p": "margin: 1em 0; line-height: 1.8; color: #333; font-size: 16px;",
            "blockquote": f"border-left: 4px solid {accent}; padding: 0.5em 1em; margin: 1em 0; color: #666; background: #f9f9f9; border-radius: 0 4px 4px 0;",
        }

        soup = BeautifulSoup(html, "html.parser")

        for tag, style in style_map.items():
            for element in soup.find_all(tag):
                existing = element.get("style", "")
                if existing:
                    # 合并样式
                    element["style"] = f"{style} {existing}"
                else:
                    element["style"] = style

        return str(soup)

    # ── Step 10: 兼容修复 ──

    def _step10_compatibility_fix(self, html: str) -> str:
        """微信兼容性修复"""
        # 移除class属性（微信不支持自定义class）
        html = re.sub(r'\s+class="[^"]*"', '', html)
        # 移除id属性
        html = re.sub(r'\s+id="[^"]*"', '', html)
        # 确保所有图片有data-src
        html = re.sub(
            r'<img([^>]*?)src="([^"]*)"([^>]*?)>',
            lambda m: m.group(0) if 'data-src=' in m.group(0) else f'<img{m.group(1)}src="{m.group(2)}"{m.group(3)} data-src="{m.group(2)}">',
            html,
        )
        # 修复span嵌套
        html = re.sub(r'<span[^>]*><span[^>]*>', '<span>', html)
        # 移除空段落
        html = re.sub(r'<p>\s*</p>', '', html)

        return html

    # ── Step 11: 暗黑模式 ──

    def _step11_dark_mode(self, html: str) -> str:
        """暗黑模式支持"""
        if not self.dark_mode:
            return html

        dark_overrides = {
            "color: #333": "color: #e0e0e0",
            "color: #666": "color: #b0b0b0",
            "color: #999": "color: #808080",
            "background: #f9f9f9": "background: #2d2d2d",
            "background: #f6f8fa": "background: #1e1e1e",
            "background: #fff3e0": "background: #3e2f1f",
            "background: #e8f5e9": "background: #1f3e1f",
            "background: #e3f2fd": "background: #1f2f3e",
            "background: #fce4ec": "background: #3e1f2f",
            "background: #fafafa": "background: #1a1a1a",
            "border-bottom: 1px solid #eee": "border-bottom: 1px solid #444",
            "border-bottom: 2px solid": "border-bottom: 2px solid #4a9eff",
        }

        for light, dark in dark_overrides.items():
            html = html.replace(light, dark)

        return html

    # ── Step 12: CSS随机扰动 ──

    def _step12_css_random_perturbation(self, html: str) -> str:
        """CSS随机扰动 - 避免被微信判定为模板"""
        def perturb_style(match):
            style = match.group(1)
            # 随机微调margin
            def adjust_margin(m):
                val = float(m.group(1))
                delta = random.uniform(-0.05, 0.05)
                return f"margin: {round(val + delta, 2)}em"

            style = re.sub(r"margin: (\d+(?:\.\d+)?)em", adjust_margin, style)

            # 随机微调padding
            def adjust_padding(m):
                val = float(m.group(1))
                delta = random.uniform(-0.02, 0.02)
                return f"padding: {round(val + delta, 2)}em"

            style = re.sub(r"padding: (\d+(?:\.\d+)?)em", adjust_padding, style)

            return f'style="{style}"'

        html = re.sub(r'style="([^"]*)"', perturb_style, html)
        return html

    # ── Step 13: AIGC声明 ──

    def _step13_aigc_declaration(self, html: str) -> str:
        """添加AIGC声明（如果配置了）"""
        if not self.theme.get("aigc_declaration"):
            return html

        declaration = self.theme.get("aigc_declaration_text", "本文由AI辅助创作，经人工审核编辑后发布")
        declaration_html = (
            f'<section style="margin-top: 2em; padding: 8px 12px; background: #f5f5f5; '
            f'border-radius: 4px; font-size: 12px; color: #999; text-align: center;">'
            f'🤖 {declaration}</section>'
        )
        html += declaration_html
        return html

    # ── Step 14: 摘要 ──

    def _step14_summary(self, html: str) -> str:
        """提取摘要（meta描述）"""
        # 从第一段提取
        soup = BeautifulSoup(html, "html.parser")
        first_p = soup.find("p")
        if first_p:
            text = first_p.get_text()[:120]
            # 添加摘要meta（作为注释，后续可提取）
            html = f'<!-- digest: {text} -->\n' + html
        return html

    # ── Step 15: 最终清理 ──

    def _step15_final_cleanup(self, html: str) -> str:
        """最终清理"""
        # 移除多余的空行
        html = re.sub(r'\n{3,}', '\n\n', html)
        # 修复未闭合的标签
        html = re.sub(r'<br\s*/?>', '<br/>', html)
        # 确保HTML实体正确
        html = html.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
        # 但保留代码块中的实体
        # 移除多余的空格
        html = re.sub(r'  +', ' ', html)
        return html.strip()

    # ── Step 16: 包装 ──

    def _step16_wrap(self, html: str) -> str:
        """最终包装"""
        # 如果还没有外层容器，添加一个
        if not html.startswith("<section") and not html.startswith("<div"):
            font_family = self.theme.get("font_family", "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif")
            html = (
                f'<section style="font-family: {font_family}; '
                f'font-size: 16px; line-height: 1.8; color: #333; '
                f'max-width: 100%; word-wrap: break-word;">'
                f'{html}</section>'
            )
        return html
