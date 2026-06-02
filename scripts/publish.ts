import { readFile, writeFile } from "node:fs/promises";
import { existsSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve, isAbsolute } from "node:path";
import { renderArticle, extractImageSrcs } from "./render.ts";
import { getAccessToken, uploadBodyImage, uploadCoverMaterial, addDraft } from "./wechat.ts";
import { generateCover, coverPrompt } from "./imagegen.ts";

interface Args {
  input: string;
  title?: string;
  author?: string;
  digest?: string;
  cover?: string;
  genCover: boolean;
  sourceUrl?: string;
  noComment: boolean;
  model?: string;
}

function parseArgs(argv: string[]): Args {
  const a: Args = { input: "", genCover: false, noComment: false };
  for (let i = 0; i < argv.length; i++) {
    const t = argv[i];
    if (t === "--gen-cover") a.genCover = true;
    else if (t === "--no-comment") a.noComment = true;
    else if (t === "--title") a.title = argv[++i];
    else if (t === "--author") a.author = argv[++i];
    else if (t === "--digest") a.digest = argv[++i];
    else if (t === "--cover") a.cover = argv[++i];
    else if (t === "--source-url") a.sourceUrl = argv[++i];
    else if (t === "--model") a.model = argv[++i];
    else if (!t.startsWith("--") && !a.input) a.input = t;
  }
  if (!a.input) throw new Error("Usage: publish.ts <article.html|article.md> [--title ..] [--cover <path> | --gen-cover] [--author ..] [--digest ..] [--no-comment]");
  return a;
}

function loadEnv(scriptDir: string): Record<string, string> {
  const env: Record<string, string> = { ...process.env } as Record<string, string>;
  const candidates = [join(process.cwd(), ".env"), resolve(scriptDir, "..", ".env")];
  for (const file of candidates) {
    if (!existsSync(file)) continue;
    for (const line of readFileSync(file, "utf8").split("\n")) {
      const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/);
      if (m) env[m[1]] = m[2].replace(/^["']|["']$/g, "");
    }
  }
  return env;
}

interface Front {
  data: Record<string, string>;
  body: string;
}

function parseFrontmatter(raw: string): Front {
  const m = raw.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/);
  if (!m) return { data: {}, body: raw };
  const data: Record<string, string> = {};
  for (const line of m[1].split("\n")) {
    const kv = line.match(/^\s*([A-Za-z0-9_]+)\s*:\s*(.*)\s*$/);
    if (kv) data[kv[1].toLowerCase()] = kv[2].replace(/^["']|["']$/g, "").trim();
  }
  return { data, body: raw.slice(m[0].length) };
}

function autoTitle(body: string): string {
  const h = body.match(/^#{1,3}\s+(.+)$/m);
  return h ? h[1].trim() : "";
}

function autoDigest(body: string): string {
  const plain = body
    .replace(/^#{1,6}\s+.*$/gm, "")
    .replace(/[*_`>#-]/g, "")
    .replace(/!?\[[^\]]*\]\([^)]*\)/g, "")
    .replace(/\s+/g, " ")
    .trim();
  return plain.slice(0, 120);
}

// Resolve any image src (local path, remote URL, or data URI) to a local file path.
async function resolveImageToFile(src: string, articleDir: string): Promise<string> {
  if (src.startsWith("data:image/")) {
    const m = src.match(/^data:image\/([a-z]+);base64,(.+)$/i);
    if (!m) throw new Error("Malformed data URI image");
    const path = join(tmpdir(), `wechat-img-${Date.now()}-${Math.random().toString(36).slice(2)}.${m[1]}`);
    await writeFile(path, Buffer.from(m[2], "base64"));
    return path;
  }
  if (/^https?:\/\//.test(src)) {
    const res = await fetch(src);
    if (!res.ok) throw new Error(`Failed to download image: ${src} (${res.status})`);
    const buf = Buffer.from(await res.arrayBuffer());
    const ext = (src.split(".").pop() || "png").split(/[?#]/)[0].toLowerCase();
    const path = join(tmpdir(), `wechat-img-${Date.now()}-${Math.random().toString(36).slice(2)}.${/^(png|jpe?g|gif)$/.test(ext) ? ext : "png"}`);
    await writeFile(path, buf);
    return path;
  }
  const local = isAbsolute(src) ? src : resolve(articleDir, src);
  if (!existsSync(local)) throw new Error(`Image file not found: ${local}`);
  return local;
}

function isWechatHosted(src: string): boolean {
  return /^https?:\/\/(mmbiz\.qpic\.cn|mmbiz\.qlogo\.cn)/.test(src);
}

// For hand-written .html input: pull out the article content.
function extractArticleHtml(raw: string): string {
  const m = raw.match(/<!--\s*ARTICLE HTML START\s*-->([\s\S]*?)<!--\s*ARTICLE HTML END\s*-->/i);
  if (m) return m[1].trim();
  if (/<html[\s>]/i.test(raw)) {
    throw new Error(
      "HTML file looks like a full document. Wrap the article content in\n" +
        "<!-- ARTICLE HTML START --> ... <!-- ARTICLE HTML END --> markers.",
    );
  }
  return raw.trim();
}

function stripTags(html: string): string {
  return html
    .replace(/<[^>]+>/g, " ")
    .replace(/&[a-z]+;/gi, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function htmlTitle(html: string): string {
  const h = html.match(/<h1[^>]*>([\s\S]*?)<\/h1>/i);
  return h ? stripTags(h[1]) : "";
}

function htmlDigest(html: string): string {
  return stripTags(html).slice(0, 120);
}

async function main() {
  const scriptDir = dirname(new URL(import.meta.url).pathname);
  const args = parseArgs(process.argv.slice(2));
  const env = loadEnv(scriptDir);

  const appId = env.WECHAT_APP_ID;
  const appSecret = env.WECHAT_APP_SECRET;
  if (!appId || !appSecret) {
    throw new Error("Missing WECHAT_APP_ID / WECHAT_APP_SECRET. Set them in .env (see .env.example).");
  }

  const inputPath = resolve(process.cwd(), args.input);
  if (!existsSync(inputPath)) throw new Error(`Input file not found: ${inputPath}`);
  const articleDir = dirname(inputPath);
  const raw = await readFile(inputPath, "utf8");
  const { data: fm, body } = parseFrontmatter(raw);
  const isHtml = /\.html?$/i.test(inputPath);

  let html: string;
  if (isHtml) {
    html = extractArticleHtml(body);
    console.log("▶ Using hand-written HTML article (component layout)...");
  } else {
    html = renderArticle(body);
    console.log("▶ Rendering markdown → WeChat-compliant HTML (fallback theme)...");
  }

  const title = args.title || fm.title || (isHtml ? htmlTitle(html) : autoTitle(body));
  if (!title) throw new Error("No title found. Pass --title or add a frontmatter title.");
  const author = args.author || fm.author || "";
  const digest =
    args.digest || fm.description || fm.summary || fm.digest || (isHtml ? htmlDigest(html) : autoDigest(body));

  console.log(`▶ Title: ${title}`);

  // Authenticate.
  console.log("▶ Fetching WeChat access token...");
  const token = await getAccessToken(appId, appSecret);

  // Upload inline images and rewrite their src to WeChat-hosted URLs.
  const srcs = [...new Set(extractImageSrcs(html))].filter((s) => !isWechatHosted(s));
  if (srcs.length) console.log(`▶ Uploading ${srcs.length} inline image(s) to WeChat...`);
  for (const src of srcs) {
    const file = await resolveImageToFile(src, articleDir);
    const url = await uploadBodyImage(file, token);
    html = html.split(`src="${src}"`).join(`src="${url}"`);
    console.log(`  ✓ ${src} → ${url}`);
  }

  // Resolve the cover image.
  let coverPath = args.cover ? resolve(process.cwd(), args.cover) : "";
  if (coverPath && !existsSync(coverPath)) throw new Error(`Cover image not found: ${coverPath}`);
  if (!coverPath && fm.cover) {
    const c = resolve(articleDir, fm.cover);
    if (existsSync(c)) coverPath = c;
  }
  if (!coverPath && args.genCover) {
    const key = env.OPENAI_API_KEY;
    if (!key) throw new Error("--gen-cover needs OPENAI_API_KEY in .env");
    console.log("▶ Generating cover image via OpenAI...");
    coverPath = await generateCover(coverPrompt(title), key, args.model || env.OPENAI_IMAGE_MODEL || "gpt-image-2");
    console.log(`  ✓ Cover saved: ${coverPath}`);
  }
  if (!coverPath) {
    throw new Error("A cover image is required. Pass --cover <path> or --gen-cover.");
  }

  console.log("▶ Uploading cover to WeChat material library...");
  const thumbMediaId = await uploadCoverMaterial(coverPath, token);

  console.log("▶ Creating draft...");
  const draftId = await addDraft(
    {
      title,
      author,
      digest,
      content: html,
      thumbMediaId,
      contentSourceUrl: args.sourceUrl,
      needOpenComment: args.noComment ? 0 : 1,
    },
    token,
  );

  console.log("\n✅ Draft created in WeChat Official Account draft box");
  console.log(`   Title:    ${title}`);
  console.log(`   Author:   ${author || "(none)"}`);
  console.log(`   Digest:   ${digest}`);
  console.log(`   draft media_id: ${draftId}`);
  console.log("   Open https://mp.weixin.qq.com → 内容管理 → 草稿箱 to preview & publish.");
}

main().catch((err) => {
  console.error(`\n❌ ${err instanceof Error ? err.message : String(err)}`);
  process.exit(1);
});
