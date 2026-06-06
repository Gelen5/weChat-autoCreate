#!/usr/bin/env python3
"""范文风格提取 - SICO式few-shot提取 + 风格指纹分析 + 自动分类"""

import argparse
import json
import math
import re
import sys
import logging
from typing import List, Dict, Any, Optional
from collections import Counter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def split_sentences(text: str) -> List[str]:
    """分句"""
    sentences = re.split(r'[。！？；\n]+', text)
    return [s.strip() for s in sentences if s.strip()]


def split_paragraphs(text: str) -> List[str]:
    """分段"""
    paragraphs = re.split(r'\n\s*\n', text)
    return [p.strip() for p in paragraphs if p.strip()]


def analyze_sentence_patterns(text: str) -> Dict[str, Any]:
    """分析句式模式"""
    sentences = split_sentences(text)
    if not sentences:
        return {"avg_length": 0, "length_distribution": {}, "patterns": []}

    lengths = [len(s) for s in sentences]
    avg_length = sum(lengths) / len(lengths)

    # 句长分布
    bins = {"short": 0, "medium": 0, "long": 0, "very_long": 0}
    for l in lengths:
        if l < 10:
            bins["short"] += 1
        elif l < 25:
            bins["medium"] += 1
        elif l < 50:
            bins["long"] += 1
        else:
            bins["very_long"] += 1

    total = len(lengths)
    distribution = {k: round(v / total, 3) for k, v in bins.items()}

    # 开头模式
    starters = Counter()
    for s in sentences:
        if len(s) >= 2:
            starters[s[:2]] += 1

    top_starters = starters.most_common(10)

    return {
        "avg_length": round(avg_length, 2),
        "length_distribution": distribution,
        "top_starters": top_starters,
        "total_sentences": total,
    }


def analyze_paragraph_patterns(text: str) -> Dict[str, Any]:
    """分析段落模式"""
    paragraphs = split_paragraphs(text)
    if not paragraphs:
        return {"avg_length": 0, "count": 0}

    lengths = [len(p) for p in paragraphs]
    avg_length = sum(lengths) / len(lengths)

    # 段首模式
    para_starters = [p[:4] if len(p) >= 4 else p for p in paragraphs]

    return {
        "count": len(paragraphs),
        "avg_length": round(avg_length, 2),
        "starters": para_starters[:20],
    }


def analyze_vocabulary(text: str) -> Dict[str, Any]:
    """分析词汇特征"""
    # 中文词汇
    chars = re.findall(r'[\u4e00-\u9fff]', text)
    if not chars:
        return {"ttr": 0, "total_chars": 0}

    ttr = len(set(chars)) / len(chars)

    # 高频词（简单的2-4字词统计）
    bigrams = Counter()
    for i in range(len(chars) - 1):
        bigrams[chars[i] + chars[i + 1]] += 1

    # 情感词
    positive_words = ["好", "棒", "赞", "优秀", "精彩", "出色", "厉害", "妙"]
    negative_words = ["差", "烂", "糟", "糟糕", "失败", "遗憾", "失望", "痛"]

    pos_count = sum(text.count(w) for w in positive_words)
    neg_count = sum(text.count(w) for w in negative_words)
    sentiment_ratio = pos_count / max(pos_count + neg_count, 1)

    return {
        "ttr": round(ttr, 4),
        "total_chars": len(chars),
        "unique_chars": len(set(chars)),
        "top_bigrams": bigrams.most_common(20),
        "sentiment_ratio": round(sentiment_ratio, 3),
    }


def analyze_rhetoric(text: str) -> Dict[str, Any]:
    """分析修辞手法"""
    rhetoric = {}

    # 设问
    rhetoric["rhetorical_questions"] = len(re.findall(r'[吗呢吧？？]{1}', text))

    # 排比（连续3个以上相同句式）
    sentences = split_sentences(text)
    parallelism = 0
    for i in range(len(sentences) - 2):
        if len(sentences[i]) > 3 and len(sentences[i + 1]) > 3:
            # 句首2字相同视为排比
            if sentences[i][:2] == sentences[i + 1][:2]:
                parallelism += 1
    rhetoric["parallelism"] = parallelism

    # 比喻
    metaphor_markers = ["像", "如同", "仿佛", "好似", "犹如", "好比"]
    rhetoric["metaphors"] = sum(text.count(m) for m in metaphor_markers)

    # 引用
    quote_patterns = [r'"[^"]{2,}"', r'「[^」]{2,}」', r'《[^》]{2,}》']
    rhetoric["quotes"] = sum(len(re.findall(p, text)) for p in quote_patterns)

    return rhetoric


def auto_classify(fingerprint: Dict[str, Any]) -> str:
    """自动分类文体"""
    avg_sent_len = fingerprint.get("sentence", {}).get("avg_length", 20)
    ttr = fingerprint.get("vocabulary", {}).get("ttr", 0.5)
    sentiment = fingerprint.get("vocabulary", {}).get("sentiment_ratio", 0.5)
    rhetoric = fingerprint.get("rhetoric", {})

    if avg_sent_len < 15 and rhetoric.get("rhetorical_questions", 0) > 3:
        return "casual"  # 随笔/对话
    elif avg_sent_len > 30 and ttr > 0.45:
        return "academic"  # 学术/深度
    elif rhetoric.get("metaphors", 0) > 3:
        return "literary"  # 文学/散文
    elif rhetoric.get("quotes", 0) > 5:
        return "journalistic"  # 新闻/报道
    elif sentiment < 0.3:
        return "critical"  # 批判/评论
    else:
        return "general"  # 通用


def generate_sico_prompts(text: str, fingerprint: Dict[str, Any]) -> Dict[str, str]:
    """生成SICO式few-shot提示词"""
    sentences = split_sentences(text)

    # 选3个代表性句子作为style exemplars
    if len(sentences) >= 3:
        # 短、中、长各选一个
        sorted_sents = sorted(sentences, key=len)
        exemplars = [
            sorted_sents[0],                                    # 短
            sorted_sents[len(sorted_sents) // 2],               # 中
            sorted_sents[-1],                                   # 长
        ]
    else:
        exemplars = sentences[:3]

    style_desc = fingerprint.get("category", "general")

    return {
        "system": f"""你是一个写作风格模仿专家。你需要按照以下风格特征写作：

文体类型：{style_desc}
平均句长：{fingerprint.get('sentence', {}).get('avg_length', 20)}字
句长分布：{json.dumps(fingerprint.get('sentence', {}).get('length_distribution', {}), ensure_ascii=False)}
情感倾向：{'积极' if fingerprint.get('vocabulary', {}).get('sentiment_ratio', 0.5) > 0.6 else '中性/批判'}
修辞偏好：设问{fingerprint.get('rhetoric', {}).get('rhetorical_questions', 0)}次，比喻{fingerprint.get('rhetoric', {}).get('metaphors', 0)}次，排比{fingerprint.get('rhetoric', {}).get('parallelism', 0)}次

风格样本：
1. {exemplars[0] if len(exemplars) > 0 else ''}
2. {exemplars[1] if len(exemplars) > 1 else ''}
3. {exemplars[2] if len(exemplars) > 2 else ''}

请严格模仿以上风格特征进行写作。""",
        "exemplars": exemplars,
    }


def main():
    parser = argparse.ArgumentParser(description="范文风格提取")
    parser.add_argument("file", nargs="?", help="范文文本文件")
    parser.add_argument("--text", help="直接传入文本")
    parser.add_argument("--json", action="store_true", help="JSON输出")
    parser.add_argument("--sico", action="store_true", help="生成SICO式few-shot提示词")
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

    # 风格指纹分析
    fingerprint = {
        "sentence": analyze_sentence_patterns(text),
        "paragraph": analyze_paragraph_patterns(text),
        "vocabulary": analyze_vocabulary(text),
        "rhetoric": analyze_rhetoric(text),
    }

    # 自动分类
    fingerprint["category"] = auto_classify(fingerprint)

    result = {"fingerprint": fingerprint}

    # SICO提示词
    if args.sico:
        result["sico_prompts"] = generate_sico_prompts(text, fingerprint)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"文体分类: {fingerprint['category']}")
        print(f"平均句长: {fingerprint['sentence']['avg_length']}字")
        print(f"句长分布: {fingerprint['sentence']['length_distribution']}")
        print(f"词汇丰富度(TTR): {fingerprint['vocabulary']['ttr']}")
        print(f"情感倾向: {fingerprint['vocabulary']['sentiment_ratio']}")
        if args.sico and "sico_prompts" in result:
            print(f"\n--- SICO System Prompt ---\n{result['sico_prompts']['system']}")


if __name__ == "__main__":
    main()
