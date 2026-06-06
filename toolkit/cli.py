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

    handler = command_map.get(args.command)
    if handler:
        return handler(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
