/**
 * Markdown渲染引擎
 * marked解析 + applyTheme()内联样式注入 + 多主题支持
 */

import { marked } from "marked";
import * as fs from "fs";
import * as path from "path";

export interface ThemeConfig {
  name?: string;
  primary_color?: string;
  secondary_color?: string;
  background_color?: string;
  accent_color?: string;
  fonts?: string[];
  // 完整的样式映射
  styles?: Record<string, Record<string, string>>;
}

// 自定义renderer
const renderer = new marked.Renderer();

// 段落
renderer.paragraph = (text: string) => {
  return `<p style="margin: 1em 0; line-height: 1.8;">${text}</p>`;
};

// 标题
renderer.heading = (text: string, level: number) => {
  const sizes = ["1.6em", "1.4em", "1.2em", "1.1em", "1em", "0.9em"];
  const weights = ["bold", "bold", "bold", "semibold", "semibold", "semibold"];
  return `<h${level} style="font-size: ${sizes[level - 1]}; font-weight: ${weights[level - 1]}; margin: 1.5em 0 0.8em; border-bottom: ${level <= 2 ? "1px solid #eee" : "none"}; padding-bottom: ${level <= 2 ? "0.3em" : "0"};">${text}</h${level}>`;
};

// 强调
renderer.strong = (text: string) => {
  return `<strong style="font-weight: bold; color: inherit;">${text}</strong>`;
};

renderer.em = (text: string) => {
  return `<em style="font-style: italic;">${text}</em>`;
};

// 代码块
renderer.code = (code: string, language: string | undefined) => {
  const lang = language || "text";
  return `<pre style="background: #f6f8fa; border-radius: 6px; padding: 16px; overflow-x: auto; font-size: 14px; line-height: 1.6;"><code class="language-${lang}" style="font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;">${escapeHtml(code)}</code></pre>`;
};

// 行内代码
renderer.codespan = (code: string) => {
  return `<code style="background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; font-family: 'SFMono-Regular', Consolas, monospace;">${code}</code>`;
};

// 链接
renderer.link = (href: string, title: string, text: string) => {
  const titleAttr = title ? ` title="${escapeHtml(title)}"` : "";
  return `<a href="${escapeHtml(href)}"${titleAttr} style="color: #576b95; text-decoration: none;">${text}</a>`;
};

// 图片
renderer.image = (href: string, title: string, text: string) => {
  const titleAttr = title ? ` title="${escapeHtml(title)}"` : "";
  return `<img src="${escapeHtml(href)}"${titleAttr} alt="${escapeHtml(text)}" style="max-width: 100%; height: auto; border-radius: 4px; margin: 0.5em 0;" />`;
};

// 列表
renderer.list = (body: string, ordered: boolean, start: number) => {
  const tag = ordered ? "ol" : "ul";
  const startAttr = ordered && start !== 1 ? ` start="${start}"` : "";
  return `<${tag}${startAttr} style="padding-left: 2em; margin: 1em 0; line-height: 1.8;">${body}</${tag}>`;
};

renderer.listitem = (text: string) => {
  return `<li style="margin: 0.3em 0;">${text}</li>`;
};

// 引用
renderer.blockquote = (quote: string) => {
  return `<blockquote style="border-left: 4px solid #ddd; padding: 0.5em 1em; margin: 1em 0; color: #666; background: #f9f9f9; border-radius: 0 4px 4px 0;">${quote}</blockquote>`;
};

// 水平线
renderer.hr = () => {
  return `<hr style="border: none; border-top: 1px solid #eee; margin: 2em 0;" />`;
};

// 表格
renderer.table = (header: string, body: string) => {
  return `<table style="border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 0.95em;"><thead>${header}</thead><tbody>${body}</tbody></table>`;
};

renderer.tablerow = (content: string) => {
  return `<tr style="border-bottom: 1px solid #eee;">${content}</tr>`;
};

renderer.tablecell = (content: string, flags: { header: boolean; align: string | null }) => {
  const tag = flags.header ? "th" : "td";
  const align = flags.align ? `text-align: ${flags.align};` : "";
  const weight = flags.header ? "font-weight: bold;" : "";
  return `<${tag} style="padding: 8px 12px; ${align} ${weight}">${content}</${tag}>`;
};

// 配置marked
marked.setOptions({
  renderer,
  gfm: true,
  breaks: true,
});

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

/**
 * 渲染Markdown为微信兼容HTML
 */
export function renderMarkdown(markdown: string, theme?: ThemeConfig): string {
  let html = marked.parse(markdown) as string;

  if (theme) {
    html = applyTheme(html, theme);
  }

  return html;
}

/**
 * 应用主题内联样式注入
 */
export function applyTheme(html: string, theme: ThemeConfig): string {
  const primary = theme.primary_color || "#333333";
  const secondary = theme.secondary_color || "#666666";
  const background = theme.background_color || "#ffffff";
  const accent = theme.accent_color || "#1a73e8";

  // 注入主题颜色到HTML元素
  html = html.replace(
    /style="([^"]*?)color:\s*inherit;([^"]*?)"/g,
    (match, before, after) => {
      return `style="${before}color: ${primary};${after}"`;
    }
  );

  // 标题颜色
  html = html.replace(
    /(<h[1-6][^>]*style="[^"]*?)"/g,
    (match, stylePart) => {
      if (!stylePart.includes("color:")) {
        return `${stylePart}; color: ${primary};"`;
      }
      return match;
    }
  );

  // 链接颜色
  html = html.replace(
    /(<a[^>]*style="[^"]*?color:\s*)#576b95/g,
    `$1${accent}`
  );

  // 引用边框颜色
  html = html.replace(
    /border-left:\s*4px\s*solid\s*#ddd/g,
    `border-left: 4px solid ${accent}`
  );

  // 代码块背景
  html = html.replace(
    /background:\s*#f6f8fa/g,
    `background: ${background === "#ffffff" ? "#f6f8fa" : background}`
  );

  // 自定义样式覆盖
  if (theme.styles) {
    for (const [selector, properties] of Object.entries(theme.styles)) {
      const cssProps = Object.entries(properties)
        .map(([prop, val]) => `${prop}: ${val}`)
        .join("; ");

      // 简单的标签选择器替换
      const tagMatch = selector.match(/^(\w+)$/);
      if (tagMatch) {
        const tag = tagMatch[1];
        const regex = new RegExp(`<${tag}([^>]*style="[^"]*?)"`, "g");
        html = html.replace(regex, `<${tag} $1; ${cssProps}"`);
      }
    }
  }

  return html;
}

/**
 * 从文件加载主题
 */
export function loadTheme(name: string): ThemeConfig {
  const themePaths = [
    path.resolve(process.cwd(), "themes", `${name}.yaml`),
    path.resolve(process.cwd(), "themes", `${name}.yml`),
    path.resolve(process.cwd(), "themes", `${name}.json`),
    path.resolve(__dirname, "..", "themes", `${name}.yaml`),
    path.resolve(__dirname, "..", "themes", `${name}.yml`),
    path.resolve(__dirname, "..", "themes", `${name}.json`),
  ];

  for (const themePath of themePaths) {
    if (fs.existsSync(themePath)) {
      const content = fs.readFileSync(themePath, "utf-8");
      if (themePath.endsWith(".json")) {
        return JSON.parse(content);
      }
      // 简单YAML解析
      return parseSimpleYaml(content);
    }
  }

  // 返回默认主题
  return {
    name: name,
    primary_color: "#333333",
    secondary_color: "#666666",
    background_color: "#ffffff",
    accent_color: "#1a73e8",
  };
}

function parseSimpleYaml(content: string): ThemeConfig {
  const result: ThemeConfig = {};
  for (const line of content.split("\n")) {
    const match = line.match(/^(\w[\w_]*):\s*(.*)$/);
    if (match) {
      const key = match[1];
      let value: any = match[2].trim();
      if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
        value = value.slice(1, -1);
      }
      (result as any)[key] = value;
    }
  }
  return result;
}
