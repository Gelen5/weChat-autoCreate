#!/usr/bin/env python3
"""三层反AI质量评分 - 统计层(50%) + 模式层(30%) + LLM层(20%)"""

import argparse
import json
import math
import os
import re
import sys
import statistics
import logging
from typing import List, Dict, Any, Tuple, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ── 统计层 ──────────────────────────────────────────────

FORBIDDEN_WORDS_AI = [
    "值得注意的是", "总而言之", "综上所述", "不可忽视", "至关重要",
    "不言而喻", "毋庸置疑", "由此可见", "换言之", "与此同时",
    "在此基础上", "从这个角度来看", "需要指出的是", "显而易见",
    "事实上", "实际上", "毋庸置疑地", "不可忽视地",
    "首先其次最后", "一方面另一方面", "此外另外",
    "值得注意的是", "深入探讨", "全面解析", "深度解读",
    "前沿技术", "颠覆性", "革命性", "划时代", "跨时代",
    "令人瞩目", "令人惊叹", "令人兴奋", "不可错过",
    "干货", "必读", "必看", "收藏", "转发",
]

BROKEN_SENTENCE_PATTERNS = [
    r"……[，。]",
    r"—[，。]",
    r"[，。]{2,}",
]

REAL_SOURCE_PATTERNS = [
    r"据[\u4e00-\u9fff]{2,8}(报道|消息|透露|表示)",
    r"[\u4e00-\u9fff]{2,6}数据显示",
    r"根据[\u4e00-\u9fff]{2,8}(调查|研究|报告)",
    r"[\u4e00-\u9fff]{2,6}统计",
    r"https?://",
]

SELF_CORRECTION_PATTERNS = [
    r"更准确地说",
    r"或者更确切地说",
    r"不对，",
    r"等等，",
    r"我想说的是",
    r"换个说法",
]

WARM_WORDS = [
    "吧", "呢", "嘛", "啊", "哈", "唉", "哎", "哦", "嗯",
    "说来", "说实话", "老实说", "坦白讲", "讲真",
    "我觉着", "我以为", "依我看", "个人感觉",
]

NEGATIVE_EMOTION_WORDS = [
    "遗憾", "失望", "担忧", "焦虑", "痛苦", "困惑",
    "不满", "无奈", "尴尬", "矛盾", "纠结", "挣扎",
    "可惜", "不安", "迷茫", "苦涩",
]


def split_sentences(text: str) -> List[str]:
    """分句"""
    sentences = re.split(r'[。！？；\n]+', text)
    return [s.strip() for s in sentences if s.strip()]


def split_paragraphs(text: str) -> List[str]:
    """分段"""
    paragraphs = re.split(r'\n\s*\n', text)
    return [p.strip() for p in paragraphs if p.strip()]


def count_adverbs(text: str) -> int:
    """统计副词密度"""
    adverb_patterns = [
        r'非常', r'极其', r'十分', r'特别', r'相当', r'格外',
        r'尤为', r'极为', r'无比', r'万分', r'超级',
        r'确实', r'真的', r'实在', r'的确',
        r'彻底', r'完全', r'绝对', r'必然',
        r'大大', r'深深', r'牢牢', r'紧紧',
    ]
    count = 0
    for pattern in adverb_patterns:
        count += len(re.findall(pattern, text))
    return count


def calculate_statistical_layer(text: str) -> Dict[str, Any]:
    """统计层评分 (50%)"""
    sentences = split_sentences(text)
    paragraphs = split_paragraphs(text)
    total_chars = len(text.replace('\n', '').replace(' ', ''))

    if not sentences or total_chars < 10:
        return {"score": 50, "details": {"error": "文本过短"}}

    # 句长标准差
    sent_lengths = [len(s) for s in sentences]
    try:
        sent_stddev = statistics.stdev(sent_lengths) if len(sent_lengths) > 1 else 0
    except statistics.StatisticsError:
        sent_stddev = 0

    # 句长范围
    sent_range = max(sent_lengths) - min(sent_lengths) if sent_lengths else 0

    # 段落长度方差
    para_lengths = [len(p) for p in paragraphs]
    try:
        para_variance = statistics.variance(para_lengths) if len(para_lengths) > 1 else 0
    except statistics.StatisticsError:
        para_variance = 0

    # 词汇丰富度 (type-token ratio)
    chars = re.findall(r'[\u4e00-\u9fff]', text)
    if chars:
        ttr = len(set(chars)) / len(chars)
    else:
        ttr = 0.5

    # 负面情绪比例
    neg_count = sum(text.count(w) for w in NEGATIVE_EMOTION_WORDS)
    neg_ratio = neg_count / max(total_chars / 100, 1)

    # 副词密度
    adverb_count = count_adverbs(text)
    adverb_density = adverb_count / max(total_chars / 100, 1)

    # ── 计算各维度得分 ──

    # 句长标准差：人类写作通常 > 5
    stddev_score = min(sent_stddev / 10 * 100, 100)

    # 句长范围：人类写作通常 > 15
    range_score = min(sent_range / 30 * 100, 100)

    # 段落方差：人类写作差异大
    var_score = min(para_variance / 500 * 100, 100)

    # 词汇丰富度：TTR > 0.4 为佳
    ttr_score = min(ttr / 0.5 * 100, 100)

    # 负面情绪：有则更人性化
    neg_score = min(neg_ratio * 50, 100) if neg_ratio > 0 else 30

    # 副词密度：适中最好（3-8次/百字）
    if 3 <= adverb_density <= 8:
        adverb_score = 80
    elif 1 <= adverb_density <= 12:
        adverb_score = 50
    else:
        adverb_score = 20

    weights = {
        "stddev": (stddev_score, 0.20),
        "range": (range_score, 0.10),
        "variance": (var_score, 0.10),
        "ttr": (ttr_score, 0.25),
        "negative": (neg_score, 0.15),
        "adverb": (adverb_score, 0.20),
    }

    total = sum(v[0] * v[1] for v in weights.values())

    return {
        "score": round(total, 2),
        "details": {
            "sent_stddev": round(sent_stddev, 2),
            "sent_range": sent_range,
            "para_variance": round(para_variance, 2),
            "ttr": round(ttr, 4),
            "neg_ratio": round(neg_ratio, 4),
            "adverb_density": round(adverb_density, 4),
            "subscores": {k: round(v[0], 2) for k, v in weights.items()},
        },
    }


def calculate_pattern_layer(text: str) -> Dict[str, Any]:
    """模式层评分 (30%)"""
    score = 0
    details = {}

    # 禁用词检测
    forbidden_count = sum(1 for w in FORBIDDEN_WORDS_AI if w in text)
    forbidden_score = max(0, 100 - forbidden_count * 15)
    details["forbidden_words_count"] = forbidden_count
    details["forbidden_score"] = forbidden_score
    score += forbidden_score * 0.25

    # 碎句检测（短句<5字占比）
    sentences = split_sentences(text)
    if sentences:
        short_sents = sum(1 for s in sentences if len(s) < 5)
        short_ratio = short_sents / len(sentences)
        broken_score = min(short_ratio * 200, 100)
    else:
        broken_score = 50
    details["broken_sentence_score"] = round(broken_score, 2)
    score += broken_score * 0.20

    # 真实来源
    real_source_count = sum(len(re.findall(p, text)) for p in REAL_SOURCE_PATTERNS)
    source_score = min(real_source_count * 25, 100)
    details["real_source_count"] = real_source_count
    details["source_score"] = source_score
    score += source_score * 0.20

    # 词汇温度
    warm_count = sum(text.count(w) for w in WARM_WORDS)
    warm_score = min(warm_count * 15, 100)
    details["warm_word_count"] = warm_count
    details["warm_score"] = warm_score
    score += warm_score * 0.15

    # 自我纠正
    correction_count = sum(len(re.findall(p, text)) for p in SELF_CORRECTION_PATTERNS)
    correction_score = min(correction_count * 30, 100)
    details["correction_count"] = correction_count
    details["correction_score"] = correction_score
    score += correction_score * 0.20

    return {"score": round(score, 2), "details": details}


def calculate_llm_layer(text: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """LLM层评分 (20%) - 使用LLM判断文本是否像AI生成"""
    if not api_key:
        return {"score": 50, "details": {"skipped": True, "reason": "No API key"}}

    try:
        import requests as req

        prompt = f"""请判断以下中文文章是否像AI生成的。评分0-100，100=完全像人类，0=完全像AI。
只返回一个JSON：{{"score": 数字, "reason": "简短理由"}}

文章：
{text[:2000]}"""

        resp = req.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 200,
            },
            timeout=30,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]

        # 提取JSON
        match = re.search(r'\{[^}]+\}', content)
        if match:
            result = json.loads(match.group())
            return {
                "score": result.get("score", 50),
                "details": {"reason": result.get("reason", ""), "skipped": False},
            }
    except Exception as e:
        logger.warning(f"LLM评分失败: {e}")

    return {"score": 50, "details": {"skipped": True, "reason": "API call failed"}}


def bell_curve_calibration(score: float) -> float:
    """钟形曲线校准 - 将原始分数映射到正态分布"""
    # 均值55, 标准差18的正态分布
    mu, sigma = 55, 18
    # Sigmoid变换
    z = (score - mu) / sigma
    calibrated = 1 / (1 + math.exp(-z * 1.5))
    return round(calibrated * 100, 2)


def main():
    parser = argparse.ArgumentParser(description="三层反AI质量评分")
    parser.add_argument("file", nargs="?", help="待评分文本文件（默认stdin）")
    parser.add_argument("--text", help="直接传入文本")
    parser.add_argument("--tier3", action="store_true", help="启用LLM层评分")
    parser.add_argument("--api-key", help="OpenAI API Key（用于LLM层）")
    parser.add_argument("--json", action="store_true", help="JSON输出")
    parser.add_argument("--no-calibration", action="store_true", help="不做钟形曲线校准")
    args = parser.parse_args()

    # 读取文本
    if args.text:
        text = args.text
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    if not text.strip():
        print("错误：空文本", file=sys.stderr)
        sys.exit(1)

    # 三层评分
    stat_result = calculate_statistical_layer(text)
    pattern_result = calculate_pattern_layer(text)

    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if args.tier3 and api_key:
        llm_result = calculate_llm_layer(text, api_key)
    else:
        llm_result = {"score": 50, "details": {"skipped": True, "reason": "Not enabled"}}

    # 加权汇总
    raw_score = (
        stat_result["score"] * 0.50
        + pattern_result["score"] * 0.30
        + llm_result["score"] * 0.20
    )

    # 钟形曲线校准
    final_score = raw_score if args.no_calibration else bell_curve_calibration(raw_score)

    result = {
        "final_score": round(final_score, 2),
        "raw_score": round(raw_score, 2),
        "layers": {
            "statistical": stat_result,
            "pattern": pattern_result,
            "llm": llm_result,
        },
        "calibrated": not args.no_calibration,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"人性化评分: {result['final_score']}/100")
        print(f"  统计层(50%): {stat_result['score']}")
        print(f"  模式层(30%): {pattern_result['score']}")
        print(f"  LLM层(20%): {llm_result['score']}")
        if result["calibrated"]:
            print(f"  原始分: {result['raw_score']} → 校准分: {result['final_score']}")


if __name__ == "__main__":
    main()
