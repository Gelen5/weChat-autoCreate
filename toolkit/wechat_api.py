"""
微信 API 封装 — Access Token、图片上传、草稿管理
"""

import os
import re
import tempfile
from pathlib import Path
from typing import Any

import requests


class WeChatAPI:
    """微信公众号 API 客户端"""

    BASE_URL = "https://api.weixin.qq.com/cgi-bin"

    def __init__(self, cfg: dict[str, Any] | None = None):
        cfg = cfg or {}
        wechat_cfg = cfg.get("wechat", {})
        self.app_id = wechat_cfg.get("app_id") or os.environ.get("WECHAT_APP_ID", "")
        self.app_secret = wechat_cfg.get("app_secret") or os.environ.get("WECHAT_APP_SECRET", "")
        self._token = None

    def _check_error(self, data: dict, action: str) -> dict:
        """检查微信 API 返回的错误"""
        if data.get("errcode", 0) != 0:
            raise RuntimeError(
                f"微信 API 错误 ({action}): errcode={data['errcode']}, errmsg={data.get('errmsg', '')}"
            )
        return data

    def get_access_token(self) -> str:
        """获取 access_token"""
        if self._token:
            return self._token

        if not self.app_id or not self.app_secret:
            raise ValueError(
                "缺少 WECHAT_APP_ID 或 WECHAT_APP_SECRET，请在 .env 或配置文件中设置"
            )

        url = f"{self.BASE_URL}/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret,
        }
        resp = requests.get(url, params=params, timeout=10)
        data = self._check_error(resp.json(), "获取token")

        self._token = data["access_token"]
        return self._token

    def upload_body_image(self, image_path: str, token: str) -> str:
        """上传正文图片，返回微信托管的 URL

        限制：1MB 以内，jpg/png 格式
        """
        url = f"{self.BASE_URL}/media/uploadimg"
        with open(image_path, "rb") as f:
            files = {"media": f}
            resp = requests.post(
                f"{url}?access_token={token}",
                files=files,
                timeout=30,
            )
        data = self._check_error(resp.json(), "上传正文图片")
        return data.get("url", "")

    def upload_cover(self, image_path: str, token: str) -> str:
        """上传封面图片到素材库，返回 media_id

        限制：10MB 以内
        """
        url = f"{self.BASE_URL}/material/add_material"
        with open(image_path, "rb") as f:
            files = {"media": f}
            resp = requests.post(
                f"{url}?access_token={token}&type=image",
                files=files,
                timeout=30,
            )
        data = self._check_error(resp.json(), "上传封面素材")
        return data.get("media_id", "")

    def add_draft(self, article: dict, token: str) -> str:
        """创建草稿，返回 media_id"""
        url = f"{self.BASE_URL}/draft/add"
        body = {
            "articles": [
                {
                    "article_type": "news",
                    "title": article.get("title", "")[:64],
                    "author": article.get("author", ""),
                    "digest": article.get("digest", "")[:120],
                    "content": article.get("content", ""),
                    "content_source_url": article.get("content_source_url", ""),
                    "thumb_media_id": article.get("thumb_media_id", ""),
                    "need_open_comment": article.get("need_open_comment", 1),
                    "only_fans_can_comment": article.get("only_fans_can_comment", 0),
                }
            ]
        }
        resp = requests.post(
            f"{url}?access_token={token}",
            json=body,
            timeout=30,
        )
        data = self._check_error(resp.json(), "创建草稿")
        return data.get("media_id", "")

    def upload_inline_images(self, html: str, token: str) -> str:
        """上传 HTML 中所有非微信托管的图片，替换 src 为微信 URL"""
        # 匹配非微信域名的图片 src
        pattern = r'<img[^>]*src="(?!https?://mmbiz\.qpic\.cn)(?!https?://mmbiz\.qlogo\.cn)([^"]*)"'

        def replace_src(match):
            src = match.group(1)
            if src.startswith("data:image/"):
                # base64 图片先保存到临时文件
                try:
                    import base64
                    header, b64data = src.split(",", 1)
                    ext = header.split("/")[1].split(";")[0]
                    ext = "jpg" if ext == "jpeg" else ext
                    tmp = tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False)
                    tmp.write(base64.b64decode(b64data))
                    tmp.close()
                    local_path = tmp.name
                except Exception:
                    return match.group(0)
            elif src.startswith(("http://", "https://")):
                # 下载远程图片到临时文件
                try:
                    resp = requests.get(src, timeout=15)
                    resp.raise_for_status()
                    ext = Path(src).suffix.lstrip(".") or "png"
                    ext = "jpg" if ext == "jpeg" else ext
                    tmp = tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False)
                    tmp.write(resp.content)
                    tmp.close()
                    local_path = tmp.name
                except Exception:
                    return match.group(0)
            elif os.path.exists(src):
                local_path = src
            else:
                return match.group(0)

            # 上传并替换
            try:
                wx_url = self.upload_body_image(local_path, token)
                return f'src="{wx_url}"'
            except Exception:
                return match.group(0)

        return re.sub(pattern, replace_src, html)

    def schedule_publish(self, media_id: str, schedule_time: str, token: str) -> dict:
        """定时发布（需已认证服务号）"""
        url = f"{self.BASE_URL}/freepublish/submit"
        # 微信免费发布接口，实际定时需通过第三方或微信后台操作
        # 这里仅做草稿提交记录
        return {"media_id": media_id, "scheduled": schedule_time}
