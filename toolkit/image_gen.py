"""
图片生成 — 多图源适配器
支持 Unsplash / Pexels / Pixabay / AI 生成等 9 种图源
"""

import os
from typing import Any

import requests


class ImageProvider:
    """图片提供商基类"""

    name: str = "base"

    def search(self, keyword: str, count: int = 3) -> list[str]:
        """搜索图片，返回 URL 列表"""
        raise NotImplementedError


class UnsplashProvider(ImageProvider):
    name = "unsplash"
    base_url = "https://api.unsplash.com/search/photos"

    def search(self, keyword: str, count: int = 3) -> list[str]:
        api_key = os.environ.get("UNSPLASH_ACCESS_KEY", "")
        if not api_key:
            return []
        resp = requests.get(
            self.base_url,
            params={"query": keyword, "per_page": count, "client_id": api_key},
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        return [r["urls"]["regular"] for r in results[:count]]


class PexelsProvider(ImageProvider):
    name = "pexels"
    base_url = "https://api.pexels.com/v1/search"

    def search(self, keyword: str, count: int = 3) -> list[str]:
        api_key = os.environ.get("PEXELS_API_KEY", "")
        if not api_key:
            return []
        resp = requests.get(
            self.base_url,
            params={"query": keyword, "per_page": count},
            headers={"Authorization": api_key},
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json().get("photos", [])
        return [r["src"]["large"] for r in results[:count]]


class PixabayProvider(ImageProvider):
    name = "pixabay"
    base_url = "https://pixabay.com/api/"

    def search(self, keyword: str, count: int = 3) -> list[str]:
        api_key = os.environ.get("PIXABAY_API_KEY", "")
        if not api_key:
            return []
        resp = requests.get(
            self.base_url,
            params={"q": keyword, "per_page": count, "key": api_key, "image_type": "photo"},
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json().get("hits", [])
        return [r["largeImageURL"] for r in results[:count]]


class AIGeneratedProvider(ImageProvider):
    """AI 生成配图（OpenAI DALL-E / GPT Image）"""
    name = "ai-generated"

    def search(self, keyword: str, count: int = 3) -> list[str]:
        api_key = os.environ.get("OPENAI_API_KEY", "")
        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        model = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-2")

        if not api_key:
            return []

        urls = []
        for _ in range(count):
            try:
                resp = requests.post(
                    f"{base_url}/images/generations",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}",
                    },
                    json={
                        "model": model,
                        "prompt": f"A clean editorial illustration for: {keyword}. No text. Minimalist.",
                        "n": 1,
                        "size": "1792x1024",
                    },
                    timeout=60,
                )
                resp.raise_for_status()
                data = resp.json()
                if data.get("data") and data["data"][0].get("url"):
                    urls.append(data["data"][0]["url"])
            except Exception:
                continue

        return urls


class LocalProvider(ImageProvider):
    """本地文件图片"""
    name = "local"

    def search(self, keyword: str, count: int = 3) -> list[str]:
        # 本地文件不支持搜索，返回空列表
        return []


# 图源注册表
PROVIDERS: dict[str, type[ImageProvider]] = {
    "unsplash": UnsplashProvider,
    "pexels": PexelsProvider,
    "pixabay": PixabayProvider,
    "ai-generated": AIGeneratedProvider,
    "ai_generated": AIGeneratedProvider,
    "local": LocalProvider,
}


def get_provider(name: str) -> ImageProvider:
    """获取图片提供商实例"""
    provider_class = PROVIDERS.get(name.lower())
    if not provider_class:
        raise ValueError(f"不支持的图片源: {name}，可选: {', '.join(PROVIDERS.keys())}")
    return provider_class()


def generate_cover_image(text: str, source: str = "unsplash", cfg: dict[str, Any] | None = None) -> list[str]:
    """根据文章内容生成/搜索配图

    Args:
        text: 文章内容（用于提取关键词）
        source: 图片源名称
        cfg: 配置字典

    Returns:
        图片 URL 列表
    """
    cfg = cfg or {}

    # 从文章内容提取关键词（简单实现：取前 50 个字）
    import re
    # 去掉 Markdown 标记
    clean = re.sub(r"[#*`>\[\]()-]", " ", text)
    words = clean.split()[:20]
    keyword = " ".join(words[:5]) if words else "technology"

    provider = get_provider(source)
    count = cfg.get("image", {}).get("max_count", 3)

    try:
        urls = provider.search(keyword, count)
    except Exception:
        # 主图源失败，尝试备用
        fallback = cfg.get("image", {}).get("fallback_source", "pexels")
        if fallback != source:
            try:
                urls = get_provider(fallback).search(keyword, count)
            except Exception:
                urls = []
        else:
            urls = []

    return urls
