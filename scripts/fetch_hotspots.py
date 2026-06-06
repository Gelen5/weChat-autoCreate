#!/usr/bin/env python3
"""多平台热点抓取 - 微博热搜、头条热榜、百度热搜"""

import argparse
import json
import sys
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
}

MAX_RETRIES = 3
BASE_DELAY = 1.0  # seconds, exponential backoff base


def exponential_backoff_retry(func, *args, max_retries=MAX_RETRIES, **kwargs):
    """指数退避重试"""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                logger.warning(f"Failed after {max_retries} retries: {e}")
                return None
            delay = BASE_DELAY * (2 ** attempt)
            logger.debug(f"Retry {attempt + 1}/{max_retries} after {delay:.1f}s: {e}")
            time.sleep(delay)


def fetch_weibo_hotspots() -> List[Dict[str, Any]]:
    """抓取微博热搜"""
    url = "https://weibo.com/ajax/side/hotSearch"

    def _fetch():
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = []
        realtime = data.get("data", {}).get("realtime", [])
        for item in realtime[:50]:
            results.append({
                "title": item.get("note", ""),
                "hot": item.get("num", 0),
                "category": item.get("category", ""),
                "source": "weibo",
            })
        return results

    result = exponential_backoff_retry(_fetch)
    return result or []


def fetch_toutiao_hotspots() -> List[Dict[str, Any]]:
    """抓取头条热榜"""
    url = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"

    def _fetch():
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for item in data.get("data", [])[:50]:
            results.append({
                "title": item.get("Title", ""),
                "hot": item.get("HotValue", 0),
                "url": item.get("Url", ""),
                "source": "toutiao",
            })
        return results

    result = exponential_backoff_retry(_fetch)
    return result or []


def fetch_baidu_hotspots() -> List[Dict[str, Any]]:
    """抓取百度热搜"""
    url = "https://top.baidu.com/board?tab=realtime"

    def _fetch():
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        # Baidu returns HTML with embedded JSON
        import re
        match = re.search(r'<!--s-data:(.*?)-->', resp.text, re.DOTALL)
        if not match:
            logger.warning("Failed to extract Baidu data from HTML")
            return []
        data = json.loads(match.group(1))
        results = []
        cards = data.get("data", {}).get("cards", [])
        for card in cards:
            for item in card.get("content", [])[:50]:
                results.append({
                    "title": item.get("query", ""),
                    "hot": item.get("hotScore", 0),
                    "desc": item.get("desc", ""),
                    "source": "baidu",
                })
        return results

    result = exponential_backoff_retry(_fetch)
    return result or []


def exponential_decay_normalize(items: List[Dict[str, Any]], key: str = "hot") -> List[Dict[str, Any]]:
    """指数衰减归一化打分 - 排名越高分数衰减越慢"""
    if not items:
        return items

    sorted_items = sorted(items, key=lambda x: x.get(key, 0), reverse=True)
    decay_rate = 0.95

    for i, item in enumerate(sorted_items):
        original = item.get(key, 0)
        rank_score = (len(sorted_items) - i) / len(sorted_items)
        decay_score = decay_rate ** i
        normalized = round((rank_score * 0.4 + decay_score * 0.6) * 100, 2)
        item["score"] = normalized

    return sorted_items


def merge_and_deduplicate(all_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """合并去重 - 相同标题合并来源"""
    title_map: Dict[str, Dict[str, Any]] = {}
    for item in all_items:
        title = item["title"].strip()
        if not title:
            continue
        if title in title_map:
            title_map[title]["sources"].append(item["source"])
            title_map[title]["score"] = round(
                title_map[title]["score"] * 0.7 + item.get("score", 0) * 0.3, 2
            )
        else:
            title_map[title] = {
                "title": title,
                "sources": [item["source"]],
                "score": item.get("score", 0),
                "hot": item.get("hot", 0),
                "desc": item.get("desc", ""),
            }
    return sorted(title_map.values(), key=lambda x: x["score"], reverse=True)


def main():
    parser = argparse.ArgumentParser(description="多平台热点抓取")
    parser.add_argument("--limit", type=int, default=20, help="输出数量")
    parser.add_argument("--source", choices=["weibo", "toutiao", "baidu", "all"], default="all", help="数据源")
    parser.add_argument("--json", action="store_true", help="JSON输出")
    args = parser.parse_args()

    fetchers = {
        "weibo": ("微博热搜", fetch_weibo_hotspots),
        "toutiao": ("头条热榜", fetch_toutiao_hotspots),
        "baidu": ("百度热搜", fetch_baidu_hotspots),
    }

    if args.source != "all":
        fetchers = {args.source: fetchers[args.source]}

    all_items = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {}
        for key, (name, fetcher) in fetchers.items():
            future = executor.submit(fetcher)
            futures[future] = name

        for future in as_completed(futures):
            name = futures[future]
            try:
                items = future.result()
                logger.info(f"{name}: 获取 {len(items)} 条")
                all_items.extend(items)
            except Exception as e:
                logger.error(f"{name} 获取失败: {e}")

    # 归一化打分
    all_items = exponential_decay_normalize(all_items)
    # 合并去重
    merged = merge_and_deduplicate(all_items)
    # 截断
    results = merged[: args.limit]

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for i, item in enumerate(results, 1):
            sources = "+".join(item["sources"])
            print(f"{i:2d}. [{sources}] {item['title']} (score={item['score']})")


if __name__ == "__main__":
    main()
