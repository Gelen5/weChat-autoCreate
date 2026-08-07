"""Render a self-contained local preview for a Tie-Tu plan."""

from __future__ import annotations

import html
from pathlib import Path

from .models import TieTuPlan


def _asset_src(image_path: str, output_path: Path) -> str:
    if not image_path:
        return ""
    try:
        return Path(image_path).resolve().relative_to(output_path.parent.resolve()).as_posix()
    except ValueError:
        return Path(image_path).resolve().as_uri()


def render_preview(plan: TieTuPlan, output_path: str | Path) -> Path:
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    cards = []
    for card in plan.cards:
        image = ""
        if card.image_path:
            src = html.escape(_asset_src(card.image_path, target), quote=True)
            image = f'<img src="{src}" alt="{html.escape(card.caption or card.purpose, quote=True)}">'
        else:
            image = '<div class="placeholder">等待生成图片</div>'
        overlay = html.escape(card.overlay_text)
        cards.append(f"""
        <section class="card">
          <div class="poster">{image}<span class="index">{card.index:02d}</span>{f'<strong class="overlay">{overlay}</strong>' if overlay else ''}</div>
          <div class="card-meta"><b>{html.escape(card.role)}</b><span>{html.escape(card.purpose)}</span></div>
          {f'<p>{html.escape(card.caption)}</p>' if card.caption else ''}
        </section>""")

    source_rows = "".join(
        f'<li>{html.escape(item.get("name", "来源"))}: {html.escape(item.get("url", ""))}</li>'
        for item in plan.sources
    ) or "<li>尚未记录来源</li>"
    document = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(plan.title)}</title>
<style>
:root {{ --ink:#1f2328; --muted:#6b7280; --line:#e5e7eb; --paper:#f5f4f1; --accent:#111827; }}
* {{ box-sizing:border-box; }} body {{ margin:0; color:var(--ink); background:var(--paper); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif; }}
main {{ width:min(900px,100%); margin:auto; padding:28px 16px 56px; }} header {{ padding:8px 2px 26px; }} h1 {{ margin:0 0 8px; font-size:30px; }} .sub {{ color:var(--muted); line-height:1.7; }}
.badge {{ display:inline-block; margin:14px 0 0; padding:5px 9px; border:1px solid #cfd4dc; font-size:12px; color:#4b5563; background:#fff; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:18px; }} .card {{ background:#fff; border:1px solid var(--line); }} .poster {{ position:relative; aspect-ratio:3/4; background:#ecebe7; overflow:hidden; }} .poster img {{ display:block; width:100%; height:100%; object-fit:cover; }} .placeholder {{ display:grid; place-items:center; height:100%; color:#9ca3af; font-size:14px; }} .index {{ position:absolute; top:10px; left:10px; padding:3px 6px; color:#fff; background:rgba(0,0,0,.52); font-size:11px; }} .overlay {{ position:absolute; left:14px; right:14px; bottom:16px; color:#fff; font-size:20px; line-height:1.35; text-shadow:0 1px 4px rgba(0,0,0,.8); }} .card-meta {{ display:flex; gap:8px; align-items:baseline; padding:12px 12px 2px; }} .card-meta b {{ font-size:14px; }} .card-meta span {{ color:var(--muted); font-size:12px; }} .card p {{ margin:5px 12px 14px; color:#4b5563; font-size:13px; line-height:1.65; }} .panel {{ margin-top:28px; padding:18px; background:#fff; border:1px solid var(--line); }} .panel h2 {{ margin:0 0 10px; font-size:18px; }} .copy {{ white-space:pre-wrap; line-height:1.9; }} li {{ color:var(--muted); font-size:13px; line-height:1.7; overflow-wrap:anywhere; }}
@media (max-width:520px) {{ main {{ padding:18px 10px 40px; }} h1 {{ font-size:25px; }} .grid {{ grid-template-columns:1fr 1fr; gap:10px; }} .card-meta {{ display:block; }} .card-meta span {{ display:block; margin-top:3px; }} .overlay {{ font-size:16px; }} }}
</style></head><body><main>
<header><h1>{html.escape(plan.title)}</h1><div class="sub">{html.escape(plan.industry)} · {html.escape(plan.content_type_label)} · {html.escape(plan.ratio)}</div><span class="badge">贴图号独立预览，不影响公众号长文流程</span></header>
<div class="grid">{''.join(cards)}</div>
<section class="panel"><h2>配套文案</h2><div class="copy">{html.escape(plan.copy or "等待补充短文案")}</div></section>
<section class="panel"><h2>图片来源</h2><ul>{source_rows}</ul></section>
</main></body></html>"""
    target.write_text(document, encoding="utf-8")
    return target
