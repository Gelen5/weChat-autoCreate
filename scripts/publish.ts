/**
 * 微信公众号发布入口
 * 支持 .html 和 .md，Frontmatter解析，图片上传重写（DOM解析），封面处理，多图文
 */

import * as fs from "fs";
import * as path from "path";
import { JSDOM } from "jsdom";
import { WeChatAPI } from "./wechat";
import { renderMarkdown } from "./render";
import { applyTheme, loadTheme } from "../toolkit/theme";

interface Frontmatter {
  title?: string;
  author?: string;
  digest?: string;
  cover?: string;
  content_source_url?: string;
  need_open_comment?: number;
  only_fans_can_comment?: number;
  theme?: string;
  [key: string]: any;
}

interface PublishOptions {
  file: string;
  theme?: string;
  draft?: boolean;
  multi?: boolean;
}

function parseFrontmatter(content: string): { frontmatter: Frontmatter; body: string } {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/);
  if (!match) {
    return { frontmatter: {}, body: content };
  }

  const yamlStr = match[1];
  const body = match[2];
  const frontmatter: Frontmatter = {};

  // 简单YAML解析
  for (const line of yamlStr.split("\n")) {
    const kvMatch = line.match(/^(\w[\w_]*):\s*(.*)$/);
    if (kvMatch) {
      const key = kvMatch[1];
      let value: any = kvMatch[2].trim();
      // 去引号
      if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
        value = value.slice(1, -1);
      }
      // 布尔值
      if (value === "true") value = true;
      if (value === "false") value = false;
      // 数字
      if (/^\d+$/.test(value)) value = parseInt(value);
      frontmatter[key] = value;
    }
  }

  return { frontmatter, body };
}

async function rewriteImageSources(
  html: string,
  api: WeChatAPI
): Promise<string> {
  /** 用DOM解析代替字符串替换，修复图片上传 */
  const dom = new JSDOM(html);
  const document = dom.window.document;

  const images = document.querySelectorAll("img");
  for (const img of images) {
    const src = img.getAttribute("src") || img.getAttribute("data-src");
    if (!src) continue;

    // 跳过已经是微信域名的图片
    if (src.includes("mmbiz.qpic.cn") || src.includes("mmbiz.qlogo.cn")) {
      continue;
    }

    // 跳过base64图片
    if (src.startsWith("data:")) {
      continue;
    }

    try {
      // 下载图片并上传到微信
      const mediaId = await api.uploadImageFromUrl(src);
      if (mediaId) {
        const wxUrl = `https://mmbiz.qpic.cn/mmbiz_jpg/${mediaId}/0`;
        img.setAttribute("src", wxUrl);
        img.setAttribute("data-src", wxUrl);
        // 移除data-src以避免冲突
        img.removeAttribute("data-src");
      }
    } catch (e) {
      console.warn(`图片上传失败: ${src}`, e);
    }
  }

  return dom.serialize();
}

async function uploadCover(
  coverPath: string,
  api: WeChatAPI
): Promise<string | null> {
  /** 处理封面图片上传 */
  if (!coverPath) return null;

  // 支持URL和本地路径
  if (coverPath.startsWith("http://") || coverPath.startsWith("https://")) {
    return await api.uploadThumbFromUrl(coverPath);
  }

  // 本地文件
  const absPath = path.resolve(coverPath);
  if (!fs.existsSync(absPath)) {
    console.warn(`封面文件不存在: ${absPath}`);
    return null;
  }

  return await api.uploadThumb(absPath);
}

async function publishSingle(
  options: PublishOptions
): Promise<string | null> {
  const { file, theme, draft } = options;

  // 读取文件
  const ext = path.extname(file).toLowerCase();
  const rawContent = fs.readFileSync(file, "utf-8");

  let html: string;
  let frontmatter: Frontmatter = {};

  if (ext === ".md") {
    const parsed = parseFrontmatter(rawContent);
    frontmatter = parsed.frontmatter;
    html = renderMarkdown(parsed.body);
  } else if (ext === ".html") {
    const parsed = parseFrontmatter(rawContent);
    frontmatter = parsed.frontmatter;
    html = parsed.body;
  } else {
    console.error(`不支持的文件格式: ${ext}`);
    return null;
  }

  // 应用主题
  const themeName = frontmatter.theme || theme || "default";
  try {
    const themeData = loadTheme(themeName);
    html = applyTheme(html, themeData);
  } catch (e) {
    console.warn(`主题加载失败 (${themeName})，使用默认样式`);
  }

  // 初始化API
  const api = new WeChatAPI();

  // 图片上传重写
  console.log("上传图片...");
  html = await rewriteImageSources(html, api);

  // 封面处理
  let thumbMediaId: string | null = null;
  if (frontmatter.cover) {
    console.log(`上传封面: ${frontmatter.cover}`);
    thumbMediaId = await uploadCover(frontmatter.cover, api);
  }

  // 创建草稿
  const title = frontmatter.title || path.basename(file, ext);
  const digest = frontmatter.digest || "";
  const contentSourceUrl = frontmatter.content_source_url || "";
  const needOpenComment = frontmatter.need_open_comment ?? 0;
  const onlyFansCanComment = frontmatter.only_fans_can_comment ?? 0;

  console.log(`创建草稿: ${title}`);
  const mediaId = await api.addDraft({
    title,
    content: html,
    thumb_media_id: thumbMediaId || "",
    author: frontmatter.author || "",
    digest,
    content_source_url: contentSourceUrl,
    need_open_comment: needOpenComment,
    only_fans_can_comment: onlyFansCanComment,
  });

  return mediaId;
}

async function publishMulti(files: string[], options: PublishOptions): Promise<string | null> {
  /** 多图文发布 */
  const api = new WeChatAPI();
  const articles: any[] = [];

  for (const file of files) {
    const ext = path.extname(file).toLowerCase();
    const rawContent = fs.readFileSync(file, "utf-8");
    let html: string;
    let frontmatter: Frontmatter = {};

    if (ext === ".md") {
      const parsed = parseFrontmatter(rawContent);
      frontmatter = parsed.frontmatter;
      html = renderMarkdown(parsed.body);
    } else {
      const parsed = parseFrontmatter(rawContent);
      frontmatter = parsed.frontmatter;
      html = parsed.body;
    }

    // 应用主题
    const themeName = frontmatter.theme || options.theme || "default";
    try {
      const themeData = loadTheme(themeName);
      html = applyTheme(html, themeData);
    } catch (_) {}

    // 图片上传
    html = await rewriteImageSources(html, api);

    // 封面
    let thumbMediaId: string | null = null;
    if (frontmatter.cover) {
      thumbMediaId = await uploadCover(frontmatter.cover, api);
    }

    articles.push({
      title: frontmatter.title || path.basename(file, ext),
      content: html,
      thumb_media_id: thumbMediaId || "",
      author: frontmatter.author || "",
      digest: frontmatter.digest || "",
      content_source_url: frontmatter.content_source_url || "",
      need_open_comment: frontmatter.need_open_comment ?? 0,
      only_fans_can_comment: frontmatter.only_fans_can_comment ?? 0,
    });
  }

  console.log(`创建多图文草稿: ${articles.length} 篇`);
  const mediaId = await api.addDraftMulti(articles);
  return mediaId;
}

// CLI入口
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log("用法: ts-node publish.ts <file1.md> [file2.md ...]");
    console.log("  --theme <name>   指定主题");
    console.log("  --multi          多图文模式");
    process.exit(0);
  }

  let theme: string | undefined;
  let multi = false;
  const files: string[] = [];

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--theme" && args[i + 1]) {
      theme = args[++i];
    } else if (args[i] === "--multi") {
      multi = true;
    } else {
      files.push(args[i]);
    }
  }

  if (files.length === 0) {
    console.error("请指定要发布的文件");
    process.exit(1);
  }

  try {
    if (multi && files.length > 1) {
      const mediaId = await publishMulti(files, { file: files[0], theme });
      if (mediaId) {
        console.log(`多图文草稿已创建: ${mediaId}`);
      }
    } else {
      for (const file of files) {
        const mediaId = await publishSingle({ file, theme });
        if (mediaId) {
          console.log(`草稿已创建: ${mediaId}`);
        }
      }
    }
  } catch (e) {
    console.error("发布失败:", e);
    process.exit(1);
  }
}

main();
