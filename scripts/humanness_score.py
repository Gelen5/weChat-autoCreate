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

LAYER_WEIGHTS = {
    "statistical": 0.50,
    "pattern": 0.30,
    "llm": 0.20,
}

# ── 统计层 ──────────────────────────────────────────────

FORBIDDEN_WORDS_AI = [
    # ── 原有禁用词（去重） ──
    "值得注意的是", "总而言之", "综上所述", "不可忽视", "至关重要",
    "不言而喻", "毋庸置疑", "由此可见", "换言之", "与此同时",
    "在此基础上", "从这个角度来看", "需要指出的是", "显而易见",
    "事实上", "实际上", "毋庸置疑地", "不可忽视地",
    "首先其次最后", "一方面另一方面", "此外另外",
    "深入探讨", "全面解析", "深度解读",
    "前沿技术", "颠覆性", "革命性", "划时代", "跨时代",
    "令人瞩目", "令人惊叹", "令人兴奋", "不可错过",
    "干货", "必读", "必看", "收藏", "转发",
    # ── 从 kol-writer 吸收的7个漏网词 ──
    "值得一提的是", "不得不说", "不可否认",
    "双刃剑", "扮演着重要的角色", "扮演着重要角色",
    "如前所述", "正如我们所知",
    # ── 补充高频AI腔 ──
    "说到底", "往往", "其实", "人性", "道德绑架",
    "综上所述地", "不可否认地",
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

# ── 句式结构检测（从 kol-writer 吸收） ──
# 这些模式不直接禁用，但在模式层扣分

AI_SENTENCE_STRUCTURES = [
    # 排比套路：首先…其次…最后（三段式AI最爱）
    {"pattern": r"首先[\s\S]{2,100}其次[\s\S]{2,100}最后", "name": "三段排比", "penalty": 20},
    # 绝对对比套路：虽然…但是…平衡
    {"pattern": r"虽然[\s\S]{2,80}但是[\s\S]{2,80}平衡", "name": "绝对对比", "penalty": 15},
    # 过度并列：不仅…而且 出现≥2次
    {"pattern": r"(不仅[\s\S]{2,60}而且)", "name": "过度并列", "penalty": 10, "min_count": 2},
    # AI式总结：总而言之/综上所述 出现在段首
    {"pattern": r"^[。\n]*(总而言之|综上所述|由此可见)", "name": "AI总结句", "penalty": 15},
    # 万能转折：然而值得注意的是
    {"pattern": r"然而(值得注意|需要指出|不容忽视)", "name": "AI转折", "penalty": 15},
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

    # ── 句式结构检测（从 kol-writer 吸收） ──
    structure_penalty = 0
    structure_hits = []
    for rule in AI_SENTENCE_STRUCTURES:
        matches = re.findall(rule["pattern"], text, re.MULTILINE)
        min_count = rule.get("min_count", 1)
        if len(matches) >= min_count:
            structure_penalty += rule["penalty"]
            structure_hits.append({
                "name": rule["name"],
                "count": len(matches),
                "penalty": rule["penalty"],
            })
    structure_score = max(0, 100 - structure_penalty)
    details["sentence_structure_hits"] = structure_hits
    details["structure_score"] = structure_score
    score += structure_score * 0.20

    # 重新归一化权重（现在6项各0.20=1.0 → 改为7项）
    # 原来: forbidden 0.25 + broken 0.20 + source 0.20 + warm 0.15 + correction 0.20 = 1.0
    # 现在: forbidden 0.20 + broken 0.15 + source 0.15 + warm 0.15 + correction 0.15 + structure 0.20 = 1.0
    # 但上面已经按旧权重加了分，需要重新计算
    # 实际上上面是累加的，我们需要重新调整
    # 为了不破坏现有逻辑，结构检测作为额外扣分项
    # 从总分中扣除结构惩罚的比例
    structure_deduction = structure_penalty * 0.15  # 结构问题最多扣15%总分
    score = max(0, score - structure_deduction)

    return {"score": round(score, 2), "details": details}


def calculate_llm_layer(text: str, api_key: Optional[str] = None,
                        host_score: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """LLM层评分 (20%)。

    阅卷老师 = 当前运行本 skill 的宿主主模型（即正在跑管道的 AI 本身）：
      - 在 WorkBuddy 里跑 → 阅卷老师就是 WorkBuddy 当前选中的模型
      - 在 Codex 里跑   → 阅卷老师就是 GPT
      - 在 Claude 里跑  → 阅卷老师就是 Claude
    无需任何 API key，自动适配任意宿主。这是默认模式。

    host_score: 宿主主模型在对话中按 L3 标准评判后传入的
                 {"score": 0-100, "reason": "简短理由"}
    api_key:    可选 OpenAI key，传入则额外做一次独立二次校验（gpt-4o-mini）。
    """
    # ── 模式1（默认）：宿主主模型阅卷 ──
    if host_score is not None:
        try:
            score = float(host_score.get("score", 50))
            reason = str(host_score.get("reason", ""))
            dimensions = host_score.get("dimensions", {}) if isinstance(host_score, dict) else {}
            return {
                "score": max(0.0, min(100.0, score)),
                "details": {
                    "reason": reason,
                    "dimensions": dimensions,
                    "skipped": False,
                    "status": "scored",
                    "grader": "host-model",
                },
            }
        except (ValueError, AttributeError, TypeError):
            logger.warning("host_score 格式非法，忽略，尝试下一模式")

    # ── 模式2（可选增强）：OpenAI 独立二次校验 ──
    if api_key:
        try:
            import requests as req

            prompt = f"""请作为内容质量阅卷老师评估以下中文文章的语义人性化程度。
请从观点原创性、细节具体性、情感真实性三个维度判断，输出0-100分。
不要因为文章使用了规范结构就直接判定为AI，也不要把无法验证的虚构经历当作真实。
只返回一个JSON：{{"score": 数字, "reason": "简短理由", "dimensions": {{"originality": 数字, "specificity": 数字, "emotion": 数字}}}}

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
                    "details": {"reason": result.get("reason", ""), "dimensions": result.get("dimensions", {}), "skipped": False, "status": "scored", "grader": "openai"},
                }
        except Exception as e:
            logger.warning(f"LLM评分失败: {e}")

    return {"score": 50, "details": {"skipped": True, "status": "unavailable", "reason": "Host score not supplied; external L3 is disabled by default", "effective_fallback": 50}}


def load_host_score(value: Optional[str] = None, file_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Load host-model L3 JSON without relying on shell-specific quoting."""
    raw = value
    if file_path:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            raw = f.read()
    elif value == "@-":
        raw = sys.stdin.read()
    elif value and value.startswith("@"):
        with open(value[1:], "r", encoding="utf-8-sig") as f:
            raw = f.read()

    if not raw:
        return None
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("host score must be a JSON object")
    if "score" not in parsed:
        raise ValueError("host score JSON must include score")
    return parsed


def build_repair_plan(stat_result: Dict[str, Any], pattern_result: Dict[str, Any],
                      llm_result: Dict[str, Any]) -> List[Dict[str, str]]:
    """Turn score evidence into concrete revision actions."""
    actions: List[Dict[str, str]] = []
    stat = stat_result.get("details", {})
    pattern = pattern_result.get("details", {})
    if stat.get("sent_stddev", 0) < 5 or stat.get("sent_range", 0) < 15:
        actions.append({"layer": "statistical", "action": "打散句长", "reason": "句长变化不足，合并部分短句并补充一处具体细节。"})
    if stat.get("ttr", 1) < 0.35:
        actions.append({"layer": "statistical", "action": "降低词汇重复", "reason": "词汇丰富度偏低，替换重复名词和同构表达。"})
    if pattern.get("forbidden_words_count", 0) > 0:
        actions.append({"layer": "pattern", "action": "替换AI高频词", "reason": f"命中{pattern['forbidden_words_count']}个禁用表达。"})
    if pattern.get("structure_score", 100) < 90:
        actions.append({"layer": "pattern", "action": "重写套路句式", "reason": "存在排比、万能转折或模板化总结结构。"})
    if pattern.get("warm_word_count", 0) == 0:
        actions.append({"layer": "pattern", "action": "补充作者视角", "reason": "全文缺少自然的主观判断或对话感。"})
    if llm_result.get("details", {}).get("status") == "unavailable":
        actions.append({"layer": "llm", "action": "补充L3阅卷", "reason": "当前没有宿主评分或独立LLM评分，语义层只使用回退分。"})
    else:
        dimensions = llm_result.get("details", {}).get("dimensions", {})
        if dimensions.get("originality", 100) < 60:
            actions.append({"layer": "llm", "action": "明确原创判断", "reason": "观点仍停留在通用结论，补充独立立场和取舍。"})
        if dimensions.get("specificity", 100) < 60:
            actions.append({"layer": "llm", "action": "补充可核验细节", "reason": "缺少具体事实、案例、时间或场景。"})
        if dimensions.get("emotion", 100) < 60:
            actions.append({"layer": "llm", "action": "增加真实情绪来源", "reason": "情绪表达较抽象，需要绑定人物、场景或具体感受。"})
    return actions


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
    parser.add_argument("--tier3", action="store_true", help="(兼容)启用LLM层，现已默认开启（宿主主模型阅卷）")
    parser.add_argument("--no-tier3", action="store_true", help="关闭LLM层评分")
    parser.add_argument("--tier3-json", help="宿主主模型L3评分JSON，如 '{\"score\":90,\"reason\":\"...\"}'")
    parser.add_argument("--tier3-file", help="从文件读取宿主主模型L3评分JSON")
    parser.add_argument("--api-key", help="OpenAI API Key（可选，用于L3独立二次校验）")
    parser.add_argument("--json", action="store_true", help="JSON输出")
    parser.add_argument("--no-calibration", action="store_true", help="不做钟形曲线校准")
    parser.add_argument("--tier3-score", type=float, help="Host-model L3 score; avoids JSON quoting on Windows")
    parser.add_argument("--tier3-reason", default="", help="Host-model L3 scoring reason")
    parser.add_argument("--external-l3", action="store_true", help="Enable the optional external OpenAI L3 check")
    args = parser.parse_args()

    # 读取文本
    if args.text:
        text = args.text
    elif args.file:
        with open(args.file, "r", encoding="utf-8-sig") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    if not text.strip():
        print("错误：空文本", file=sys.stderr)
        sys.exit(1)

    # 三层评分
    stat_result = calculate_statistical_layer(text)
    pattern_result = calculate_pattern_layer(text)

    # 宿主主模型阅卷结果（由运行skill的AI在对话中产出，无需任何API key）
    host_score = None
    host_score_error = None
    if args.tier3_score is not None:
        host_score = {"score": args.tier3_score, "reason": args.tier3_reason}
    elif args.tier3_json or args.tier3_file:
        try:
            host_score = load_host_score(args.tier3_json, args.tier3_file)
        except (OSError, json.JSONDecodeError, ValueError) as e:
            host_score = None
            host_score_error = str(e)
            logger.error(f"Host L3 score input is invalid: {e}")

    # External scoring is opt-in. A stale environment key must not affect the
    # host-model-first workflow or produce an unexpected network request.
    external_l3_enabled = args.external_l3 or bool(args.api_key)
    api_key = args.api_key or (os.environ.get("OPENAI_API_KEY") if external_l3_enabled else None)

    # L3 默认开启：宿主主模型永远在（谁跑skill谁阅卷）；--no-tier3 才关闭
    tier3_enabled = not args.no_tier3
    if tier3_enabled:
        llm_result = calculate_llm_layer(text, api_key=api_key, host_score=host_score)
        if host_score_error and llm_result["details"].get("status") == "unavailable":
            llm_result["details"]["reason"] = f"Host score input invalid: {host_score_error}; external L3 is disabled by default"
    else:
        llm_result = {"score": 50, "details": {"skipped": True, "status": "disabled", "reason": "Disabled by --no-tier3", "effective_fallback": 50}}

    # 加权汇总
    raw_score = sum((
        stat_result["score"] * LAYER_WEIGHTS["statistical"],
        pattern_result["score"] * LAYER_WEIGHTS["pattern"],
        llm_result["score"] * LAYER_WEIGHTS["llm"],
    ))

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
        "weights": LAYER_WEIGHTS,
        "repair_plan": build_repair_plan(stat_result, pattern_result, llm_result),
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
