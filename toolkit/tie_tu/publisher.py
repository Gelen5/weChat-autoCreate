"""Optional draft-box publishing for Tie-Tu plans.

This module does not call the long-form Publisher.publish method. It uploads
card images and creates one independent draft article through add_draft_multi.
"""

from __future__ import annotations

import html
from typing import Optional

from ..wechat_api import WeChatAPI
from .models import TieTuPlan
from .validator import validate_plan


class TieTuPublisher:
    def __init__(self, api: Optional[WeChatAPI] = None):
        self.api = api or WeChatAPI()

    def build_content(self, plan: TieTuPlan) -> tuple[str, str]:
        image_urls = []
        for card in plan.cards:
            if not card.image_path:
                continue
            url = self.api.upload_image(card.image_path)
            if url:
                image_urls.append((url, card))
        if not image_urls:
            raise RuntimeError("没有成功上传任何贴图图片")

        blocks = []
        for url, card in image_urls:
            caption = html.escape(card.caption)
            blocks.append(
                '<p style="margin:0 0 16px; line-height:1.6;">'
                f'<img src="{html.escape(url, quote=True)}" '
                'style="display:block;width:100%;height:auto;margin:0 auto 8px;" />'
                f'{f"<span style=\"color:#666;font-size:14px;\">{caption}</span>" if caption else ""}'
                '</p>'
            )
        if plan.copy:
            blocks.append(f'<p style="margin:16px 0;line-height:1.85;">{html.escape(plan.copy)}</p>')
        if plan.cta:
            blocks.append(f'<p style="margin:16px 0;line-height:1.85;">{html.escape(plan.cta)}</p>')
        return "".join(blocks), image_urls[0][0]

    def publish_draft(self, plan: TieTuPlan) -> Optional[str]:
        report = validate_plan(plan)
        if not report["ok"]:
            raise ValueError("贴图号质量检查失败: " + "; ".join(report["errors"]))
        content, _first_image_url = self.build_content(plan)
        first_image_path = next((card.image_path for card in plan.cards if card.image_path), "")
        thumb_media_id = self.api.upload_cover(first_image_path) if first_image_path else ""
        article = {
            "title": plan.title,
            "content": content,
            "thumb_media_id": thumb_media_id or "",
            "author": "",
            "digest": plan.copy[:120],
            "content_source_url": "",
        }
        return self.api.add_draft_multi([article])
