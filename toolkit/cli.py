#!/usr/bin/env python3
"""CLI入口 - preview/publish/gallery/themes/image-post/learn-theme"""

import argparse
import json
import os
import sys
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def cmd_preview(args):
    """预览文章渲染效果"""
    from .converter import MarkdownConverter
    from .theme import load_theme, apply_theme

    file_path = args.file
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}", file=sys.stderr)
        return 1

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 提取frontmatter
    frontmatter = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            import yaml
            try:
                frontmatter = yaml.safe_load(parts[1]) or {}
            except Exception:
                pass
            content = parts[2]

    # 转换
    converter = MarkdownConverter()
    html = converter.convert(content)

    # 应用主题
    theme_name = frontmatter.get("theme", args.theme or "default")
    theme = load_theme(theme_name)
    html = apply_theme(html, theme)

    # 输出
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(html)
        logger.info(f"已保存: {args.output}")
    else:
        # 生成完整HTML预览
        full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{frontmatter.get('title', 'Preview')}</title>
<style>
body {{ max-width: 680px; margin: 0 auto; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
</style>
</head>
<body>
{html}
</body>
</html>"""
        output_path = os.path.splitext(file_path)[0] + "_preview.html"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_html)
        logger.info(f"预览已生成: {output_path}")

    return 0


def cmd_publish(args):
    """发布到微信草稿箱"""
    from .publisher import Publisher

    publisher = Publisher()
    result = publisher.publish(
        file_path=args.file,
        theme=args.theme,
        draft=not args.no_draft,
    )

    if result:
        logger.info(f"发布成功: media_id={result}")
        return 0
    else:
        logger.error("发布失败")
        return 1


def cmd_gallery(args):
    """生成小绿书图片帖"""
    from .publisher import Publisher

    publisher = Publisher()
    result = publisher.publish_image_post(
        image_paths=args.images,
        title=args.title,
        content=args.content or "",
    )

    if result:
        logger.info(f"小绿书发布成功: media_id={result}")
        return 0
    else:
        logger.error("小绿书发布失败")
        return 1


def cmd_themes(args):
    """列出可用主题"""
    from .theme import list_themes

    themes = list_themes()
    if not themes:
        print("未找到任何主题文件")
        return 0

    for name, theme in themes.items():
        print(f"  {name}: {theme.get('name', name)}")
        if theme.get("primary_color"):
            print(f"    主色: {theme['primary_color']}")
        if theme.get("accent_color"):
            print(f"    强调色: {theme['accent_color']}")

    return 0


def cmd_image_post(args):
    """小绿书图片帖"""
    return cmd_gallery(args)


def cmd_tie_tu_plan(args):
    """Create an independent Tie-Tu card-plan scaffold."""
    from .tie_tu import build_plan, recommend_types, save_plan

    if args.recommend:
        print(json.dumps(recommend_types(args.industry, args.topic, args.title or ""), ensure_ascii=False, indent=2))
        return 0
    plan = build_plan(
        industry=args.industry,
        topic=args.topic,
        title=args.title or "",
        content_type=args.content_type,
        image_count=args.count,
        style=args.style or "",
        audience=args.audience or "",
    )
    save_plan(plan, args.output)
    print(f"贴图号 card_plan 已生成: {args.output}")
    return 0


def cmd_tie_tu_preview(args):
    """Render an independent Tie-Tu preview HTML."""
    from .tie_tu import load_plan, render_preview

    plan = load_plan(args.plan)
    output = args.output or os.path.splitext(args.plan)[0] + "_preview.html"
    render_preview(plan, output)
    print(f"贴图号预览已生成: {output}")
    return 0


def cmd_tie_tu_validate(args):
    """Validate a Tie-Tu card plan and local image assets."""
    from .tie_tu import load_plan, validate_plan

    report = validate_plan(load_plan(args.plan))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


def cmd_tie_tu_publish(args):
    """Publish an independent Tie-Tu plan to the WeChat draft box."""
    from .tie_tu import TieTuPublisher, load_plan

    media_id = TieTuPublisher().publish_draft(load_plan(args.plan))
    if media_id:
        print(f"贴图号草稿已创建: media_id={media_id}")
        return 0
    print("贴图号草稿创建失败", file=sys.stderr)
    return 1


def cmd_learn_theme(args):
    """从URL学习排版主题"""
    # 调用learn_theme脚本
    import subprocess
    script_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "learn_theme.py")
    cmd = [sys.executable, script_path, args.url]
    if args.output:
        cmd.extend(["--output", args.output])
    if args.json:
        cmd.append("--json")

    result = subprocess.run(cmd, capture_output=False)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="微信公众号全链路自动化CLI",
        prog="wechat-toolkit",
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # preview
    preview_parser = subparsers.add_parser("preview", help="预览渲染效果")
    preview_parser.add_argument("file", help="Markdown/HTML文件路径")
    preview_parser.add_argument("--theme", "-t", help="主题名称")
    preview_parser.add_argument("--output", "-o", help="输出文件路径")

    # publish
    publish_parser = subparsers.add_parser("publish", help="发布到草稿箱")
    publish_parser.add_argument("file", help="Markdown/HTML文件路径")
    publish_parser.add_argument("--theme", "-t", help="主题名称")
    publish_parser.add_argument("--no-draft", action="store_true", help="直接发布（不放入草稿箱）")

    # gallery / image-post
    gallery_parser = subparsers.add_parser("gallery", help="小绿书图片帖")
    gallery_parser.add_argument("images", nargs="+", help="图片文件路径")
    gallery_parser.add_argument("--title", required=True, help="标题")
    gallery_parser.add_argument("--content", help="正文内容")

    # image-post (alias)
    image_post_parser = subparsers.add_parser("image-post", help="小绿书图片帖(别名)")
    image_post_parser.add_argument("images", nargs="+", help="图片文件路径")
    image_post_parser.add_argument("--title", required=True, help="标题")
    image_post_parser.add_argument("--content", help="正文内容")

    # tie-tu: independent image-led workflow; article commands remain unchanged
    tie_tu_parser = subparsers.add_parser("tie-tu", help="独立的微信贴图号流程")
    tie_tu_sub = tie_tu_parser.add_subparsers(dest="tie_tu_command", required=True)

    tie_tu_plan = tie_tu_sub.add_parser("plan", help="生成贴图号卡片策划骨架")
    tie_tu_plan.add_argument("--industry", required=True, help="行业")
    tie_tu_plan.add_argument("--topic", required=True, help="主题")
    tie_tu_plan.add_argument("--title", help="标题")
    tie_tu_plan.add_argument("--content-type", choices=[
        "tutorial", "before_after", "list", "industry_view", "city_change", "emotional_story"
    ])
    tie_tu_plan.add_argument("--count", type=int, default=5, help="图片数量，3-20")
    tie_tu_plan.add_argument("--style", help="视觉风格")
    tie_tu_plan.add_argument("--audience", help="目标读者")
    tie_tu_plan.add_argument("--output", default="card_plan.json", help="输出 JSON")
    tie_tu_plan.add_argument("--recommend", action="store_true", help="只输出六类内容类型推荐")

    tie_tu_preview = tie_tu_sub.add_parser("preview", help="生成贴图号手机预览 HTML")
    tie_tu_preview.add_argument("plan", help="card_plan.json")
    tie_tu_preview.add_argument("--output", "-o", help="预览 HTML 路径")

    tie_tu_validate = tie_tu_sub.add_parser("validate", help="检查贴图号卡片策划和图片")
    tie_tu_validate.add_argument("plan", help="card_plan.json")

    tie_tu_publish = tie_tu_sub.add_parser("publish", help="将贴图号写入公众号草稿箱")
    tie_tu_publish.add_argument("plan", help="card_plan.json")

    # themes
    themes_parser = subparsers.add_parser("themes", help="列出可用主题")

    # learn-theme
    learn_parser = subparsers.add_parser("learn-theme", help="从URL学习排版主题")
    learn_parser.add_argument("url", help="微信文章URL")
    learn_parser.add_argument("--output", "-o", help="输出YAML文件路径")
    learn_parser.add_argument("--json", action="store_true", help="JSON输出")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    command_map = {
        "preview": cmd_preview,
        "publish": cmd_publish,
        "gallery": cmd_gallery,
        "image-post": cmd_image_post,
        "themes": cmd_themes,
        "learn-theme": cmd_learn_theme,
    }

    if args.command == "tie-tu":
        tie_tu_handlers = {
            "plan": cmd_tie_tu_plan,
            "preview": cmd_tie_tu_preview,
            "validate": cmd_tie_tu_validate,
            "publish": cmd_tie_tu_publish,
        }
        handler = tie_tu_handlers.get(args.tie_tu_command)
        return handler(args) if handler else 1

    handler = command_map.get(args.command)
    if handler:
        return handler(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
