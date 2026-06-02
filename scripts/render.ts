import { marked } from "marked";

const ACCENT = "#07c160";

const S = {
  container: `font-size:15px;color:#3f3f3f;line-height:1.8;letter-spacing:0.5px;word-break:break-word;padding:0 2px;`,
  h1: `font-size:20px;font-weight:800;color:#1a1a1a;margin:8px 0;line-height:1.4;`,
  h2: `font-size:16px;font-weight:700;color:#1a1a1a;margin:8px 0;padding-left:10px;border-left:4px solid ${ACCENT};line-height:1.4;`,
  h3: `font-size:15px;font-weight:700;color:#1a1a1a;margin:8px 0;line-height:1.4;`,
  h4: `font-size:15px;font-weight:700;color:#1a1a1a;margin:8px 0;line-height:1.4;`,
  p: `margin:8px 0;font-size:15px;color:#3f3f3f;line-height:1.8;letter-spacing:0.5px;`,
  blockquote: `margin:8px 0;padding:10px 14px;background:#f7f7f7;border-left:4px solid ${ACCENT};color:#888;font-size:13px;line-height:1.8;`,
  list: `margin:8px 0;padding-left:24px;color:#3f3f3f;`,
  li: `margin:8px 0;font-size:15px;line-height:1.8;`,
  a: `color:${ACCENT};text-decoration:none;`,
  strong: `font-weight:700;color:#1a1a1a;`,
  em: `font-style:italic;`,
  codeInline: `background:#f2f2f2;color:#c0341d;padding:2px 5px;border-radius:3px;font-size:13px;font-family:Menlo,Consolas,monospace;`,
  pre: `margin:8px 0;padding:12px 14px;background:#f7f7f7;border-radius:6px;overflow-x:auto;font-size:13px;line-height:1.7;`,
  codeBlock: `background:none;color:#3f3f3f;padding:0;font-family:Menlo,Consolas,monospace;`,
  img: `display:block;max-width:100%;margin:8px auto;border-radius:6px;`,
  hr: `border:none;border-top:1px solid #e5e5e5;margin:16px 0;`,
  table: `border-collapse:collapse;width:100%;margin:8px 0;font-size:13px;`,
  cell: `border:1px solid #e5e5e5;padding:6px 9px;`,
  th: `border:1px solid #e5e5e5;padding:6px 9px;background:#f7f7f7;font-weight:700;`,
};

// Turn plain semantic HTML from marked into WeChat-compliant inline-styled HTML.
// WeChat strips <style>/<link>/class/id — every style must live on a style attribute.
function applyTheme(html: string): string {
  let out = html;
  // code blocks first (must run before inline <code>)
  out = out.replace(/<pre><code[^>]*>/g, `<pre style="${S.pre}"><code style="${S.codeBlock}">`);
  out = out.replace(/<code>/g, `<code style="${S.codeInline}">`);
  out = out.replace(/<h1>/g, `<h1 style="${S.h1}">`);
  out = out.replace(/<h2>/g, `<h2 style="${S.h2}">`);
  out = out.replace(/<h3>/g, `<h3 style="${S.h3}">`);
  out = out.replace(/<h([456])>/g, `<h$1 style="${S.h4}">`);
  out = out.replace(/<p>/g, `<p style="${S.p}">`);
  out = out.replace(/<blockquote>/g, `<blockquote style="${S.blockquote}">`);
  out = out.replace(/<ul>/g, `<ul style="${S.list}">`);
  out = out.replace(/<ol>/g, `<ol style="${S.list}">`);
  out = out.replace(/<li>/g, `<li style="${S.li}">`);
  out = out.replace(/<strong>/g, `<strong style="${S.strong}">`);
  out = out.replace(/<em>/g, `<em style="${S.em}">`);
  out = out.replace(/<hr\s*\/?>/g, `<hr style="${S.hr}">`);
  out = out.replace(/<table>/g, `<table style="${S.table}">`);
  out = out.replace(/<th>/g, `<th style="${S.th}">`);
  out = out.replace(/<td>/g, `<td style="${S.cell}">`);
  out = out.replace(/<a /g, `<a style="${S.a}" `);
  out = out.replace(/<img /g, `<img style="${S.img}" `);
  return out;
}

export function renderArticle(markdown: string): string {
  marked.setOptions({ gfm: true, breaks: false });
  const body = marked.parse(markdown, { async: false }) as string;
  return `<section style="${S.container}">${applyTheme(body)}</section>`;
}

// Extract image src values from rendered HTML (used to find local files to upload).
export function extractImageSrcs(html: string): string[] {
  const srcs: string[] = [];
  const re = /<img[^>]*\ssrc="([^"]+)"/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(html)) !== null) srcs.push(m[1]);
  return srcs;
}
