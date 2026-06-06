#!/usr/bin/env python3
"""微信API封装 - access_token缓存 + 图片上传"""

import json
import os
import re
import sys
import time
import logging
import tempfile
from typing import Dict, Any, List, Optional
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from .config import get_config, Config

logger = logging.getLogger(__name__)

TOKEN_BUFFER = 5 * 60  # 5分钟缓冲（秒）


class WeChatAPI:
    """微信API封装"""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or get_config()
        self._token_cache: Dict[str, Any] = {}

    @property
    def appid(self) -> str:
        return self.config.wechat_appid

    @property
    def secret(self) -> str:
        return self.config.wechat_secret

    def get_access_token(self) -> str:
        """获取access_token（带缓存和5分钟缓冲）"""
        now = time.time()

        cached = self._token_cache.get("token")
        if cached and cached.get("expires_at", 0) > now + TOKEN_BUFFER:
            return cached["access_token"]

        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.appid,
            "secret": self.secret,
        }

        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()

        if "errcode" in data and data["errcode"] != 0:
            raise RuntimeError(f"获取token失败: {data.get('errmsg', 'unknown')} (errcode={data['errcode']})")

        token = data["access_token"]
        expires_in = data.get("expires_in", 7200)

        self._token_cache["token"] = {
            "access_token": token,
            "expires_at": now + expires_in,
        }

        logger.debug(f"access_token已更新，有效期 {expires_in}s")
        return token

    def upload_image(self, file_path: str) -> Optional[str]:
        """上传正文图片（返回微信URL）"""
        token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={token}"

        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path):
            logger.error(f"文件不存在: {abs_path}")
            return None

        with open(abs_path, "rb") as f:
            files = {"media": (os.path.basename(abs_path), f)}
            resp = requests.post(url, files=files, timeout=30)

        data = resp.json()
        if "errcode" in data and data["errcode"] != 0:
            logger.error(f"图片上传失败: {data.get('errmsg', 'unknown')}")
            return None

        return data.get("url")

    def upload_image_from_url(self, image_url: str) -> Optional[str]:
        """从URL上传图片"""
        try:
            # 下载图片
            resp = requests.get(image_url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0.0.0"
            })
            resp.raise_for_status()

            # 保存到临时文件
            suffix = ".jpg"
            if "png" in resp.headers.get("content-type", ""):
                suffix = ".png"
            elif "gif" in resp.headers.get("content-type", ""):
                suffix = ".gif"

            fd, tmp_path = tempfile.mkstemp(suffix=suffix)
            try:
                with os.fdopen(fd, "wb") as f:
                    f.write(resp.content)

                return self.upload_image(tmp_path)
            finally:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

        except Exception as e:
            logger.warning(f"从URL上传图片失败: {e}")
            return None

    def upload_cover(self, cover_path: str) -> Optional[str]:
        """上传封面缩略图"""
        token = self.get_access_token()

        # 支持URL和本地路径
        if cover_path.startswith("http://") or cover_path.startswith("https://"):
            return self._upload_cover_from_url(cover_path, token)

        abs_path = os.path.abspath(cover_path)
        if not os.path.exists(abs_path):
            logger.error(f"封面文件不存在: {abs_path}")
            return None

        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=thumb"

        with open(abs_path, "rb") as f:
            files = {"media": (os.path.basename(abs_path), f)}
            resp = requests.post(url, files=files, timeout=30)

        data = resp.json()
        if "errcode" in data and data["errcode"] != 0:
            logger.error(f"封面上传失败: {data.get('errmsg', 'unknown')}")
            return None

        return data.get("media_id")

    def _upload_cover_from_url(self, url: str, token: str) -> Optional[str]:
        """从URL上传封面"""
        try:
            resp = requests.get(url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0.0.0"
            })
            resp.raise_for_status()

            suffix = ".jpg"
            fd, tmp_path = tempfile.mkstemp(suffix=suffix)
            try:
                with os.fdopen(fd, "wb") as f:
                    f.write(resp.content)

                api_url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=thumb"
                with open(tmp_path, "rb") as f:
                    files = {"media": (os.path.basename(tmp_path), f)}
                    upload_resp = requests.post(api_url, files=files, timeout=30)

                data = upload_resp.json()
                if "errcode" in data and data["errcode"] != 0:
                    return None
                return data.get("media_id")
            finally:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

        except Exception as e:
            logger.warning(f"从URL上传封面失败: {e}")
            return None

    def add_draft(
        self,
        title: str,
        content: str,
        thumb_media_id: str = "",
        author: str = "",
        digest: str = "",
        content_source_url: str = "",
        need_openComment: int = 0,
        only_fans_can_comment: int = 0,
    ) -> Optional[str]:
        """添加草稿"""
        token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"

        article = {
            "title": title,
            "content": content,
            "thumb_media_id": thumb_media_id,
            "author": author,
            "digest": digest,
            "content_source_url": content_source_url,
            "need_open_comment": needOpenComment,
            "only_fans_can_comment": only_fans_can_comment,
        }

        resp = requests.post(url, json={"articles": [article]}, timeout=15)
        data = resp.json()

        if "errcode" in data and data["errcode"] != 0:
            logger.error(f"创建草稿失败: {data.get('errmsg', 'unknown')}")
            return None

        return data.get("media_id")

    def add_draft_multi(self, articles: List[Dict[str, Any]]) -> Optional[str]:
        """添加多图文草稿"""
        token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"

        resp = requests.post(url, json={"articles": articles}, timeout=30)
        data = resp.json()

        if "errcode" in data and data["errcode"] != 0:
            logger.error(f"创建多图文草稿失败: {data.get('errmsg', 'unknown')}")
            return None

        return data.get("media_id")

    def rewrite_html_images(self, html: str) -> str:
        """重写HTML中的图片URL为微信图片"""
        soup = BeautifulSoup(html, "html.parser")

        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src")
            if not src:
                continue

            # 跳过微信域名
            if "mmbiz.qpic.cn" in src or "mmbiz.qlogo.cn" in src:
                continue

            # 跳过base64
            if src.startswith("data:"):
                continue

            # 上传图片
            wx_url = self.upload_image_from_url(src)
            if wx_url:
                img["src"] = wx_url
                img["data-src"] = wx_url

        return str(soup)
