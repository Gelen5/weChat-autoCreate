#!/usr/bin/env python3
"""微信草稿箱API + 小绿书"""

import json
import os
import sys
import logging
from typing import Dict, Any, List, Optional

import requests

from .config import get_config
from .converter import MarkdownConverter
from .theme import load_theme, apply_theme
from .wechat_api import WeChatAPI

logger = logging.getLogger(__name__)


class Publisher:
    """微信公众号发布器"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = get_config(config_path)
        self.api = WeChatAPI(self.config)
        self.converter = MarkdownConverter()

    def publish(
        self,
        file_path: str,
        theme: Optional[str] = None,
        draft: bool = True,
    ) -> Optional[str]:
        """发布文章到草稿箱"""
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return None

        # 读取文件
        ext = os.path.splitext(file_path)[1].lower()
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 解析frontmatter
        frontmatter = {}
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    import yaml
                    frontmatter = yaml.safe_load(parts[1]) or {}
                except Exception:
                    pass
                content = parts[2]

        # 转换内容
        if ext == ".md":
            html = self.converter.convert(content)
        else:
            html = content

        # 应用主题
        theme_name = frontmatter.get("theme", theme or "default")
        theme_data = load_theme(theme_name)
        html = apply_theme(html, theme_data)

        # 图片上传重写
        logger.info("上传图片...")
        html = self.api.rewrite_html_images(html)

        # 封面处理
        thumb_media_id = ""
        cover = frontmatter.get("cover")
        if cover:
            logger.info(f"上传封面: {cover}")
            thumb_media_id = self.api.upload_cover(cover) or ""

        # 创建草稿
        title = frontmatter.get("title", os.path.splitext(os.path.basename(file_path))[0])
        logger.info(f"创建草稿: {title}")

        media_id = self.api.add_draft(
            title=title,
            content=html,
            thumb_media_id=thumb_media_id,
            author=frontmatter.get("author", ""),
            digest=frontmatter.get("digest", ""),
            content_source_url=frontmatter.get("content_source_url", ""),
        )

        if media_id:
            logger.info(f"草稿已创建: {media_id}")
        else:
            logger.error("草稿创建失败")

        return media_id

    def publish_image_post(
        self,
        image_paths: List[str],
        title: str,
        content: str = "",
    ) -> Optional[str]:
        """发布小绿书图片帖"""
        # 上传图片
        media_ids = []
        for img_path in image_paths:
            if not os.path.exists(img_path):
                logger.warning(f"图片不存在: {img_path}")
                continue

            media_id = self.api.upload_image(img_path)
            if media_id:
                media_ids.append(media_id)

        if not media_ids:
            logger.error("没有成功上传的图片")
            return None

        # 构建HTML
        images_html = ""
        for media_id in media_ids:
            images_html += f'<img src="https://mmbiz.qpic.cn/mmbiz_jpg/{media_id}/0" style="max-width: 100%; margin: 0.5em 0;" />'

        full_content = images_html
        if content:
            full_content += f'<p style="margin-top: 1em;">{content}</p>'

        # 创建草稿
        logger.info(f"创建小绿书草稿: {title}")
        media_id = self.api.add_draft(
            title=title,
            content=full_content,
            thumb_media_id=media_ids[0],
            digest=content[:120] if content else "",
        )

        return media_id

    def publish_multi(
        self,
        file_paths: List[str],
        theme: Optional[str] = None,
    ) -> Optional[str]:
        """多图文发布"""
        articles = []

        for file_path in file_paths:
            if not os.path.exists(file_path):
                logger.warning(f"文件不存在: {file_path}")
                continue

            ext = os.path.splitext(file_path)[1].lower()
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            frontmatter = {}
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    try:
                        import yaml
                        frontmatter = yaml.safe_load(parts[1]) or {}
                    except Exception:
                        pass
                    content = parts[2]

            if ext == ".md":
                html = self.converter.convert(content)
            else:
                html = content

            theme_name = frontmatter.get("theme", theme or "default")
            theme_data = load_theme(theme_name)
            html = apply_theme(html, theme_data)
            html = self.api.rewrite_html_images(html)

            thumb_media_id = ""
            cover = frontmatter.get("cover")
            if cover:
                thumb_media_id = self.api.upload_cover(cover) or ""

            articles.append({
                "title": frontmatter.get("title", os.path.splitext(os.path.basename(file_path))[0]),
                "content": html,
                "thumb_media_id": thumb_media_id,
                "author": frontmatter.get("author", ""),
                "digest": frontmatter.get("digest", ""),
                "content_source_url": frontmatter.get("content_source_url", ""),
            })

        if not articles:
            logger.error("没有有效的文章")
            return None

        logger.info(f"创建多图文草稿: {len(articles)} 篇")
        media_id = self.api.add_draft_multi(articles)
        return media_id
