#!/usr/bin/env python3
"""微信文章抓取 - 4级降级获取 + HTML转Markdown"""

import argparse
import json
import re
import sys
import logging
from typing import Optional, Dict, Any

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def level1_direct_fetch(url: str) -> Optional[str]:
    """第1级：直接请求"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        if "mp.weixin.qq.com" in resp.text or len(resp.text) > 1000:
            return resp.text
    except Exception as e:
        logger.debug(f"Level 1 失败: {e}")
    return None


def level2_mobile_fetch(url: str) -> Optional[str]:
    """第2级：移动端UA"""
    mobile_headers = {
        **HEADERS,
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    }
    try:
        resp = requests.get(url, headers=mobile_headers, timeout=15)
        resp.raise_for_status()
        if len(resp.text) > 1000:
            return resp.text
    except Exception as e:
        logger.debug(f"Level 2 失败: {e}")
    return None


def level3_cache_fetch(url: str) -> Optional[str]:
    """第3级：缓存服务"""
    cache_services = [
        f"https://webcache.googleusercontent.com/search?q=cache:{url}",
    ]
    for cache_url in cache_services:
        try:
            resp = requests.get(cache_url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            if len(resp.text) > 500:
                return resp.text
        except Exception as e:
            logger.debug(f"Level 3 缓存服务失败: {e}")
    return None


def level4_archive_fetch(url: str) -> Optional[str]:
    """第4级：归档服务"""
    try:
        # Wayback Machine
        api_url = f"https://archive.org/wayback/available?url={url}"
        resp = requests.get(api_url, timeout=10)
        data = resp.json()
        archive_url = data.get("archived_snapshots", {}).get("closest", {}).get("url")
        if archive_url:
            resp2 = requests.get(archive_url, headers=HEADERS, timeout=15)
            resp2.raise_for_status()
            return resp2.text
    except Exception as e:
        logger.debug(f"Level 4 失败: {e}")
    return None


def fetch_article(url: str) -> Optional[str]:
    """4级降级获取文章HTML"""
    levels = [
        ("直接请求", level1_direct_fetch),
        ("移动端UA", level2_mobile_fetch),
        ("缓存服务", level3_cache_fetch),
        ("归档服务", level4_archive_fetch),
    ]

    for name, fetcher in levels:
        logger.info(f"尝试: {name}")
        result = fetcher(url)
        if result:
            logger.info(f"成功: {name}")
            return result

    logger.error("所有级别均失败")
    return None


def extract_content(html: str) -> Dict[str, Any]:
    """从HTML提取文章内容"""
    result = {"title": "", "author": "", "content": "", "publish_time": ""}

    # 标题
    title_match = re.search(r'<h1[^>]*class="rich_media_title"[^>]*>(.*?)</h1>', html, re.DOTALL)
    if not title_match:
        title_match = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
    if title_match:
        result["title"] = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()

    # 作者
    author_match = re.search(r'class="rich_media_meta_nickname"[^>]*>.*?<a[^>]*>(.*?)</a>', html, re.DOTALL)
    if not author_match:
        author_match = re.search(r'var nickname = "(.*?)"', html)
    if author_match:
        result["author"] = re.sub(r'<[^>]+>', '', author_match.group(1)).strip()

    # 发布时间
    time_match = re.search(r'var ct = "(\d+)"', html)
    if time_match:
        import time as time_mod
        ts = int(time_match.group(1))
        result["publish_time"] = time_mod.strftime("%Y-%m-%d %H:%M:%S", time_mod.localtime(ts))

    # 正文内容
    content_match = re.search(
        r'<div[^>]*class="rich_media_content"[^>]*>(.*?)</div>\s*(?:<div|$)',
        html, re.DOTALL
    )
    if content_match:
        content_html = content_match.group(1)
        result["content"] = content_html.strip()
    else:
        # 降级：取body
        body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
        if body_match:
            result["content"] = body_match.group(1).strip()

    return result


def html_to_markdown(html: str) -> str:
    """简化的HTML转Markdown"""
    text = html

    # 移除script/style
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)

    # 标题
    for i in range(1, 7):
        text = re.sub(
            rf'<h{i}[^>]*>(.*?)</h{i}>',
            lambda m: '#' * i + ' ' + re.sub(r'<[^>]+>', '', m.group(1)).strip(),
            text, flags=re.DOTALL
        )

    # 段落
    text = re.sub(r'<p[^>]*>(.*?)</p>', lambda m: re.sub(r'<[^>]+>', '', m.group(1)).strip() + '\n\n', text, flags=re.DOTALL)

    # 加粗
    text = re.sub(r'<(?:strong|b)[^>]*>(.*?)</(?:strong|b)>', r'**\1**', text, flags=re.DOTALL)

    # 斜体
    text = re.sub(r'<(?:em|i)[^>]*>(.*?)</(?:em|i)>', r'*\1*', text, flags=re.DOTALL)

    # 链接
    text = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', text, flags=re.DOTALL)

    # 图片
    text = re.sub(r'<img[^>]*data-src="([^"]*)"[^>]*/?\s*>', r'![](\1)', text)
    text = re.sub(r'<img[^>]*src="([^"]*)"[^>]*/?\s*>', r'![](\1)', text)

    # 列表
    text = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1', text, flags=re.DOTALL)
    text = re.sub(r'</?[uo]l[^>]*>', '', text)

    # 换行
    text = re.sub(r'<br\s*/?>', '\n', text)

    # 清理剩余标签
    text = re.sub(r'<[^>]+>', '', text)

    # 清理HTML实体
    entities = {
        '&amp;': '&', '&lt;': '<', '&gt;': '>',
        '&quot;': '"', '&#39;': "'", '&nbsp;': ' ',
    }
    for entity, char in entities.items():
        text = text.replace(entity, char)

    # 清理多余空行
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def main():
    parser = argparse.ArgumentParser(description="微信文章抓取")
    parser.add_argument("url", help="微信文章URL")
    parser.add_argument("--markdown", "-m", action="store_true", help="输出Markdown")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--json", action="store_true", help="JSON输出")
    args = parser.parse_args()

    html = fetch_article(args.url)
    if not html:
        print("错误：无法获取文章", file=sys.stderr)
        sys.exit(1)

    article = extract_content(html)

    if args.markdown or args.output:
        markdown = html_to_markdown(article["content"])
        article["markdown"] = markdown

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            if args.markdown:
                f.write(f"# {article['title']}\n\n")
                f.write(f"> 作者: {article['author']}\n")
                if article["publish_time"]:
                    f.write(f"> 时间: {article['publish_time']}\n\n")
                f.write(article["markdown"])
            else:
                f.write(article["content"])
        logger.info(f"已保存: {args.output}")

    if args.json:
        print(json.dumps(article, ensure_ascii=False, indent=2))
    else:
        print(f"标题: {article['title']}")
        print(f"作者: {article['author']}")
        if article["publish_time"]:
            print(f"时间: {article['publish_time']}")
        if args.markdown:
            print(f"\n--- Markdown ---\n{article.get('markdown', '')[:500]}...")
        else:
            print(f"内容长度: {len(article['content'])} 字符")


if __name__ == "__main__":
    main()
