"""
微信发布 — 草稿提交和定时发布
"""

import json
import os
from typing import Any

import requests

from .wechat_api import WeChatAPI


def publish_draft(
    html: str,
    title: str = "",
    author: str = "",
    digest: str = "",
    cover_path: str = "",
    schedule: str | None = None,
    cfg: dict[str, Any] | None = None,
) -> str:
    """发布文章到微信公众号草稿箱

    Args:
        html: 排版后的 HTML 内容
        title: 文章标题
        author: 作者名
        digest: 摘要
        cover_path: 封面图路径
        schedule: 定时发布时间 (ISO 8601)
        cfg: 配置字典

    Returns:
        media_id: 草稿的 media_id
    """
    cfg = cfg or {}
    api = WeChatAPI(cfg)

    # 获取 access_token
    token = api.get_access_token()

    # 上传正文中的图片并替换 URL
    html = api.upload_inline_images(html, token)

    # 上传封面
    thumb_media_id = ""
    if cover_path and os.path.exists(cover_path):
        thumb_media_id = api.upload_cover(cover_path, token)

    # 自动提取标题和摘要
    if not title:
        import re
        h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.DOTALL)
        if h1_match:
            title = re.sub(r"<[^>]+>", "", h1_match.group(1)).strip()[:64]

    if not digest:
        import re
        plain = re.sub(r"<[^>]+>", "", html).strip()
        digest = plain[:120]

    if not thumb_media_id:
        # 尝试从 HTML 中提取第一张图作为封面
        import re
        img_match = re.search(r'<img[^>]*src="([^"]*)"', html)
        if img_match:
            img_src = img_match.group(1)
            if os.path.exists(img_src):
                thumb_media_id = api.upload_cover(img_src, token)

    # 创建草稿
    article = {
        "title": title[:64],
        "author": author,
        "digest": digest[:120],
        "content": html,
        "thumb_media_id": thumb_media_id,
        "need_open_comment": 1,
        "only_fans_can_comment": 0,
    }

    media_id = api.add_draft(article, token)

    # 定时发布
    if schedule:
        api.schedule_publish(media_id, schedule, token)

    return media_id
