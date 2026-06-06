#!/usr/bin/env python3
"""学习飞轮 - diff分析 + 模式提取 + 置信度评分 + playbook自动更新"""

import argparse
import difflib
import json
import os
import re
import sys
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

PLAYBOOK_FILE = "playbook.json"
LESSONS_FILE = "lessons.json"


def load_json(filepath: str) -> Any:
    """加载JSON文件"""
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_json(filepath: str, data: Any) -> None:
    """保存JSON文件"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def compute_diff(original: str, revised: str) -> List[Dict[str, Any]]:
    """计算文本差异"""
    orig_lines = original.splitlines()
    rev_lines = revised.splitlines()

    diff = list(difflib.unified_diff(orig_lines, rev_lines, lineterm=""))

    changes = []
    for line in diff:
        if line.startswith("+") and not line.startswith("+++"):
            changes.append({"type": "add", "content": line[1:].strip()})
        elif line.startswith("-") and not line.startswith("---"):
            changes.append({"type": "remove", "content": line[1:].strip()})

    return changes


def extract_patterns(changes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """从diff中提取编辑模式"""
    patterns = []

    for change in changes:
        content = change["content"]
        if not content or len(content) < 2:
            continue

        pattern = {"raw": content, "type": change["type"], "categories": []}

        # 分类：词汇替换
        if change["type"] == "add" and len(content) <= 8:
            pattern["categories"].append("word_replacement")

        # 分类：句式调整
        if any(w in content for w in ["但是", "然而", "不过", "其实", "实际上"]):
            pattern["categories"].append("transition_change")

        # 分类：去AI化
        ai_markers = [
            "值得注意的是", "综上所述", "总而言之", "不可或缺",
            "至关重要", "不言而喻", "毋庸置疑", "显而易见",
        ]
        if change["type"] == "remove" and any(m in content for m in ai_markers):
            pattern["categories"].append("deai_removal")

        # 分类：增加细节
        if change["type"] == "add" and any(
            w in content for w in ["具体", "例如", "比如", "实际上", "数据显示"]
        ):
            pattern["categories"].append("add_detail")

        # 分类：语气调整
        tone_words = ["吧", "呢", "嘛", "啊", "哈", "唉", "哎"]
        if change["type"] == "add" and any(w in content for w in tone_words):
            pattern["categories"].append("tone_softening")

        # 分类：删减冗余
        if change["type"] == "remove" and len(content) > 20:
            pattern["categories"].append("redundancy_removal")

        if pattern["categories"]:
            patterns.append(pattern)

    return patterns


def calculate_confidence(pattern: Dict[str, Any], all_patterns: List[Dict[str, Any]]) -> float:
    """计算模式置信度 - 出现频率越高置信度越高"""
    category = pattern.get("categories", ["unknown"])[0] if pattern.get("categories") else "unknown"

    # 同类模式出现次数
    same_category_count = sum(
        1 for p in all_patterns if category in p.get("categories", [])
    )

    # 基础置信度
    base = 0.3

    # 频率加分（对数增长）
    freq_bonus = min(0.4, 0.1 * (1 + same_category_count ** 0.5))

    # 多类别加分
    multi_bonus = 0.1 * max(0, len(pattern.get("categories", [])) - 1)

    # 内容长度合理性
    length = len(pattern.get("raw", ""))
    if 5 <= length <= 50:
        length_bonus = 0.1
    else:
        length_bonus = 0

    confidence = base + freq_bonus + multi_bonus + length_bonus
    return round(min(confidence, 1.0), 3)


def update_playbook(lessons: List[Dict[str, Any]], playbook: Dict[str, Any]) -> Dict[str, Any]:
    """每5个lesson更新playbook"""
    if "rules" not in playbook:
        playbook["rules"] = []
    if "stats" not in playbook:
        playbook["stats"] = {"total_lessons": 0, "updates": 0}

    # 按类别聚合
    category_rules: Dict[str, List[Dict[str, Any]]] = {}
    for lesson in lessons:
        for cat in lesson.get("categories", []):
            if cat not in category_rules:
                category_rules[cat] = []
            category_rules[cat].append(lesson)

    # 为每个类别生成规则
    new_rules = []
    for cat, cat_lessons in category_rules.items():
        avg_confidence = sum(l["confidence"] for l in cat_lessons) / len(cat_lessons)
        if avg_confidence >= 0.5:
            rule = {
                "category": cat,
                "confidence": round(avg_confidence, 3),
                "examples": [l["raw"] for l in cat_lessons[:3]],
                "count": len(cat_lessons),
                "updated_at": datetime.now().isoformat(),
            }
            new_rules.append(rule)

    # 合并到playbook（更新已有规则或添加新规则）
    existing_cats = {r["category"]: i for i, r in enumerate(playbook["rules"])}
    for rule in new_rules:
        if rule["category"] in existing_cats:
            idx = existing_cats[rule["category"]]
            old = playbook["rules"][idx]
            # 加权更新置信度
            old_count = old.get("count", 1)
            new_count = rule["count"]
            merged_confidence = (
                old["confidence"] * old_count + rule["confidence"] * new_count
            ) / (old_count + new_count)
            playbook["rules"][idx] = {
                **rule,
                "confidence": round(merged_confidence, 3),
                "count": old_count + new_count,
            }
        else:
            playbook["rules"].append(rule)

    playbook["stats"]["total_lessons"] += len(lessons)
    playbook["stats"]["updates"] += 1
    playbook["stats"]["last_update"] = datetime.now().isoformat()

    return playbook


def main():
    parser = argparse.ArgumentParser(description="学习飞轮")
    parser.add_argument("--original", required=True, help="原始文本文件")
    parser.add_argument("--revised", required=True, help="修订后文本文件")
    parser.add_argument("--playbook", default=PLAYBOOK_FILE, help="playbook文件路径")
    parser.add_argument("--lessons", default=LESSONS_FILE, help="lessons文件路径")
    parser.add_argument("--json", action="store_true", help="JSON输出")
    parser.add_argument("--no-update", action="store_true", help="不更新playbook")
    args = parser.parse_args()

    # 读取文本
    with open(args.original, "r", encoding="utf-8") as f:
        original = f.read()
    with open(args.revised, "r", encoding="utf-8") as f:
        revised = f.read()

    # 计算差异
    changes = compute_diff(original, revised)
    logger.info(f"发现 {len(changes)} 处变更")

    # 提取模式
    patterns = extract_patterns(changes)
    logger.info(f"提取 {len(patterns)} 个编辑模式")

    # 计算置信度
    lessons = []
    for pattern in patterns:
        confidence = calculate_confidence(pattern, patterns)
        lesson = {
            **pattern,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
        }
        lessons.append(lesson)

    # 保存lessons
    existing_lessons = load_json(args.lessons)
    if "lessons" not in existing_lessons:
        existing_lessons["lessons"] = []
    existing_lessons["lessons"].extend(lessons)
    save_json(args.lessons, existing_lessons)

    # 每5个lesson更新playbook
    total_lessons = len(existing_lessons["lessons"])
    result = {"lessons_added": len(lessons), "total_lessons": total_lessons, "patterns": patterns}

    if not args.no_update and total_lessons % 5 < len(lessons):
        playbook = load_json(args.playbook)
        playbook = update_playbook(lessons, playbook)
        save_json(args.playbook, playbook)
        result["playbook_updated"] = True
        result["playbook_rules"] = len(playbook.get("rules", []))
        logger.info(f"Playbook已更新，共 {len(playbook.get('rules', []))} 条规则")
    else:
        result["playbook_updated"] = False

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"新增模式: {len(lessons)}")
        print(f"累计模式: {total_lessons}")
        for lesson in lessons:
            cats = ", ".join(lesson.get("categories", []))
            print(f"  [{cats}] conf={lesson['confidence']} {lesson['raw'][:50]}")
        if result.get("playbook_updated"):
            print(f"Playbook已更新!")


if __name__ == "__main__":
    main()
