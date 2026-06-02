#!/usr/bin/env -S npx tsx
/**
 * img2base64.ts —— 把一张图片（网络 URL 或本地路径）变成可直接内嵌的 base64 data URI。
 *
 * 用途：组件化排版「复制预览」交付时，把联网搜到的真实配图内嵌进 <img>，
 * 复制粘贴进公众号编辑器时会被自动收图、正常显示。
 *
 * 关键约束：
 *  - 微信正文单图 ≤1MB；base64 还会膨胀 ~33%，所以下载后会自动压到阈值内。
 *  - 抓到的不是真图片（被反爬返回 HTML、404 页面等）会立刻报错退出，
 *    好让上层换一张，绝不把垃圾字节塞进 base64。
 *
 * 用法：
 *   npx tsx img2base64.ts <图片URL或本地路径> [--max-kb 980] [--max-px 1080]
 *
 * 输出：stdout 打印 data:image/...;base64,...（可直接拼进 HTML）
 *       stderr 打印体积/格式等诊断信息
 *
 * 依赖：curl + macOS 自带 sips（无需 npm 安装）
 */
import { execFileSync } from "node:child_process";
import { readFileSync, existsSync, mkdtempSync, statSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const BROWSER_UA =
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 " +
  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36";

function die(msg: string): never {
  process.stderr.write(`✗ ${msg}\n`);
  process.exit(1);
}

function parseArgs() {
  const args = process.argv.slice(2);
  let src = "";
  let maxKb = 980; // 留一点余量，base64 后仍稳稳 <1MB 经压缩前的字节阈值
  let maxPx = 1080; // 公众号正文宽度足够；过大无意义只会撑体积
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === "--max-kb") maxKb = Number(args[++i]);
    else if (a === "--max-px") maxPx = Number(args[++i]);
    else if (!a.startsWith("--")) src = a;
  }
  if (!src) die("用法: npx tsx img2base64.ts <图片URL或本地路径> [--max-kb 980] [--max-px 1080]");
  return { src, maxKb, maxPx };
}

/** 用 file 命令判断真实 mime，杜绝把 HTML/JSON 当图片 */
function mimeOf(path: string): string {
  try {
    return execFileSync("file", ["--brief", "--mime-type", path]).toString().trim();
  } catch {
    return "";
  }
}

function sizeKb(path: string): number {
  return statSync(path).size / 1024;
}

function fetchToFile(src: string, dir: string): string {
  const out = join(dir, "in.bin");
  if (existsSync(src)) {
    // 本地文件：拷一份进工作目录
    execFileSync("cp", [src, out]);
    return out;
  }
  if (!/^https?:\/\//i.test(src)) die(`既不是有效 URL 也不是存在的本地路径: ${src}`);
  process.stderr.write(`↓ 下载 ${src}\n`);
  try {
    execFileSync("curl", [
      "-sSL", "--fail",
      "-A", BROWSER_UA,
      "--max-time", "30",
      "-o", out,
      src,
    ]);
  } catch {
    die(`下载失败（404 / 反爬 / 超时）。换一张图，或换一个直链。`);
  }
  return out;
}

function main() {
  const { src, maxKb, maxPx } = parseArgs();
  const dir = mkdtempSync(join(tmpdir(), "img2b64-"));
  const raw = fetchToFile(src, dir);

  const mime = mimeOf(raw);
  if (!mime.startsWith("image/")) {
    die(`抓到的不是图片（mime=${mime || "未知"}）——多半是反爬返回了网页。换一张真实图片直链。`);
  }
  process.stderr.write(`✓ 是图片: ${mime}, ${sizeKb(raw).toFixed(0)}KB\n`);

  let finalPath = raw;
  let finalMime = mime;

  // 超阈值就压缩：转 jpg + 限制最长边 + 递减质量
  if (sizeKb(raw) > maxKb || mime === "image/png" || mime === "image/webp") {
    const jpg = join(dir, "out.jpg");
    for (const q of [85, 72, 60, 48, 35]) {
      execFileSync("sips", [
        "-s", "format", "jpeg",
        "-s", "formatOptions", String(q),
        "-Z", String(maxPx),
        raw, "--out", jpg,
      ]);
      process.stderr.write(`  压缩 q=${q} → ${sizeKb(jpg).toFixed(0)}KB\n`);
      if (sizeKb(jpg) <= maxKb) break;
    }
    if (sizeKb(jpg) > maxKb) {
      die(`压到最低质量仍 >${maxKb}KB（${sizeKb(jpg).toFixed(0)}KB）。换一张更小/更简单的图。`);
    }
    finalPath = jpg;
    finalMime = "image/jpeg";
  }

  const b64 = readFileSync(finalPath).toString("base64");
  process.stderr.write(`✓ 完成: ${finalMime}, base64 长度 ${(b64.length / 1024).toFixed(0)}KB\n`);
  // 只有 data URI 走 stdout，方便上层直接捕获拼进 <img src="...">
  process.stdout.write(`data:${finalMime};base64,${b64}\n`);
}

main();
