#!/usr/bin/env python3
"""SEO关键词分析 - 百度+360搜索建议，合并去重+SEO评分"""

import argparse
import json
import sys
import time
import logging
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
}


def fetch_baidu_suggestions(keyword: str) -> List[str]:
    """获取百度搜索建议"""
    url = "https://suggestion.baidu.com/su"
    params = {"wd": keyword, "cb": ""}

    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        # 百度返回JSONP格式，去掉回调
        text = resp.text.strip()
        if text.startswith("(") and text.endswith(")"):
            text = text[1:-1]
        data = json.loads(text)
        return data.get("s", [])
    except Exception as e:
        logger.warning(f"百度建议获取失败: {e}")
        return []


def fetch_360_suggestions(keyword: str) -> List[str]:
    """获取360搜索建议"""
    url = "https://sug.so.360.cn/suggest"
    params = {"word": keyword, "encodein": "utf-8", "encodeout": "utf-8"}

    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        suggestions = []
        for item in data.get("result", []):
            if isinstance(item, dict):
                suggestions.append(item.get("word", ""))
            elif isinstance(item, str):
                suggestions.append(item)
        return suggestions
    except Exception as e:
        logger.warning(f"360建议获取失败: {e}")
        return []


def calculate_seo_score(keyword: str, position: int, source_count: int) -> Dict[str, Any]:
    """SEO评分算法"""
    score = 0
    details = {}

    # 长度评分 (2-8字最佳)
    length = len(keyword)
    if 4 <= length <= 8:
        length_score = 30
    elif 2 <= length <= 12:
        length_score = 20
    else:
        length_score = 10
    details["length_score"] = length_score
    score += length_score

    # 排名评分
    rank_score = max(0, 25 - position * 2)
    details["rank_score"] = rank_score
    score += rank_score

    # 来源评分（双引擎出现加分）
    source_score = min(source_count * 20, 25)
    details["source_score"] = source_score
    score += source_score

    # 是否包含数字（数字标题CTR高）
    has_number = any(c.isdigit() for c in keyword)
    number_score = 10 if has_number else 0
    details["number_score"] = number_score
    score += number_score

    # 疑问词加分
    question_words = ["如何", "怎么", "为什么", "什么", "哪", "吗", "多少"]
    has_question = any(w in keyword for w in question_words)
    question_score = 10 if has_question else 0
    details["question_score"] = question_score
    score += question_score

    return {"total": min(score, 100), "details": details}


def merge_and_score(
    baidu_results: List[str], qihu_results: List[str]
) -> List[Dict[str, Any]]:
    """合并去重并计算SEO评分"""
    word_sources: Dict[str, List[str]] = {}
    word_positions: Dict[str, int] = {}

    for i, word in enumerate(baidu_results):
        word = word.strip()
        if not word:
            continue
        if word not in word_sources:
            word_sources[word] = []
            word_positions[word] = i
        if "baidu" not in word_sources[word]:
            word_sources[word].append("baidu")

    for i, word in enumerate(qihu_results):
        word = word.strip()
        if not word:
            continue
        if word not in word_sources:
            word_sources[word] = []
            word_positions[word] = i
        if "360" not in word_sources[word]:
            word_sources[word].append("360")

    results = []
    for word, sources in word_sources.items():
        position = word_positions[word]
        seo = calculate_seo_score(word, position, len(sources))
        results.append({
            "keyword": word,
            "sources": sources,
            "seo_score": seo["total"],
            "seo_details": seo["details"],
        })

    return sorted(results, key=lambda x: x["seo_score"], reverse=True)


def main():
    parser = argparse.ArgumentParser(description="SEO关键词分析")
    parser.add_argument("keyword", help="种子关键词")
    parser.add_argument("--json", action="store_true", help="JSON输出")
    args = parser.parse_args()

    keyword = args.keyword
    logger.info(f"分析关键词: {keyword}")

    with ThreadPoolExecutor(max_workers=2) as executor:
        baidu_future = executor.submit(fetch_baidu_suggestions, keyword)
        qihu_future = executor.submit(fetch_360_suggestions, keyword)

        baidu_results = baidu_future.result()
        qihu_results = qihu_future.result()

    logger.info(f"百度建议: {len(baidu_results)} 条")
    logger.info(f"360建议: {len(qihu_results)} 条")

    results = merge_and_score(baidu_results, qihu_results)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for i, item in enumerate(results, 1):
            sources = "+".join(item["sources"])
            print(f"{i:2d}. [{sources}] {item['keyword']} (SEO={item['seo_score']})")


if __name__ == "__main__":
    main()
