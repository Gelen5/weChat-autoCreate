/**
 * 图片转base64
 * Windows兼容（用sharp代替sips）+ 真实图片校验 + 自动压缩
 */

import * as fs from "fs";
import * as path from "path";
import * as sharp from "sharp";

interface Img2Base64Options {
  input: string;
  maxWidth?: number;
  maxHeight?: number;
  quality?: number;
  maxSize?: number; // bytes
}

interface Img2Base64Result {
  base64: string;
  mimeType: string;
  width: number;
  height: number;
  size: number;
}

const IMAGE_MIME_MAP: Record<string, string> = {
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".png": "image/png",
  ".gif": "image/gif",
  ".webp": "image/webp",
  ".bmp": "image/bmp",
  ".svg": "image/svg+xml",
};

/**
 * 验证是否为真实图片（通过文件头魔数）
 */
function isValidImage(buffer: Buffer): boolean {
  if (buffer.length < 4) return false;

  const header = buffer.toString("hex", 0, 4).toUpperCase();

  // JPEG: FFD8FF
  if (header.startsWith("FFD8")) return true;
  // PNG: 89504E47
  if (header === "89504E47") return true;
  // GIF: 47494638
  if (header.startsWith("47494638")) return true;
  // WebP: 52494646 (RIFF)
  if (header.startsWith("52494646")) return true;
  // BMP: 424D
  if (header.startsWith("424D")) return true;

  return false;
}

/**
 * 将图片转换为base64，支持自动压缩
 * 使用sharp代替sips，确保Windows兼容
 */
export async function img2base64(options: Img2Base64Options): Promise<Img2Base64Result> {
  const {
    input,
    maxWidth = 2048,
    maxHeight = 2048,
    quality = 80,
    maxSize = 2 * 1024 * 1024, // 2MB
  } = options;

  // 读取文件
  const absPath = path.resolve(input);
  if (!fs.existsSync(absPath)) {
    throw new Error(`文件不存在: ${absPath}`);
  }

  let buffer = fs.readFileSync(absPath);

  // 验证是否为真实图片
  if (!isValidImage(buffer)) {
    throw new Error(`不是有效的图片文件: ${absPath}`);
  }

  // 获取MIME类型
  const ext = path.extname(absPath).toLowerCase();
  const mimeType = IMAGE_MIME_MAP[ext] || "image/jpeg";

  // 使用sharp处理图片（跨平台，替代macOS的sips）
  let pipeline = sharp(buffer);
  const metadata = await pipeline.metadata();

  // 缩放尺寸
  let width = metadata.width || maxWidth;
  let height = metadata.height || maxHeight;
  let needResize = false;

  if (width > maxWidth) {
    height = Math.round(height * (maxWidth / width));
    width = maxWidth;
    needResize = true;
  }
  if (height > maxHeight) {
    width = Math.round(width * (maxHeight / height));
    height = maxHeight;
    needResize = true;
  }

  if (needResize) {
    pipeline = sharp(buffer).resize(width, height, {
      fit: "inside",
      withoutEnlargement: true,
    });
  }

  // 转换为JPEG以获得更好的压缩（除非原始是PNG且需要透明度）
  if (metadata.hasAlpha) {
    buffer = await pipeline.png({ quality }).toBuffer();
  } else {
    buffer = await pipeline.jpeg({ quality }).toBuffer();
  }

  // 自动压缩到目标大小
  if (buffer.length > maxSize) {
    let currentQuality = quality;
    while (currentQuality >= 20 && buffer.length > maxSize) {
      currentQuality -= 10;
      if (metadata.hasAlpha) {
        // PNG无法通过quality参数控制，改用调色板
        buffer = await sharp(buffer)
          .resize(Math.round(width * 0.9), Math.round(height * 0.9), { fit: "inside" })
          .png({ palette: true, quality: currentQuality })
          .toBuffer();
      } else {
        buffer = await sharp(buffer)
          .jpeg({ quality: currentQuality })
          .toBuffer();
      }
    }
  }

  // 获取最终尺寸
  const finalMeta = await sharp(buffer).metadata();

  return {
    base64: buffer.toString("base64"),
    mimeType: metadata.hasAlpha ? "image/png" : "image/jpeg",
    width: finalMeta.width || width,
    height: finalMeta.height || height,
    size: buffer.length,
  };
}

/**
 * 生成data URI
 */
export async function img2DataUri(options: Img2Base64Options): Promise<string> {
  const result = await img2base64(options);
  return `data:${result.mimeType};base64,${result.base64}`;
}

// CLI入口
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log("用法: ts-node img2base64.ts <image_path>");
    console.log("  --max-width <px>    最大宽度 (默认2048)");
    console.log("  --max-height <px>   最大高度 (默认2048)");
    console.log("  --quality <1-100>   JPEG质量 (默认80)");
    console.log("  --max-size <bytes>  最大文件大小 (默认2MB)");
    console.log("  --data-uri          输出data URI");
    process.exit(0);
  }

  let input = "";
  let maxWidth = 2048;
  let maxHeight = 2048;
  let quality = 80;
  let maxSize = 2 * 1024 * 1024;
  let dataUri = false;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--max-width" && args[i + 1]) {
      maxWidth = parseInt(args[++i]);
    } else if (args[i] === "--max-height" && args[i + 1]) {
      maxHeight = parseInt(args[++i]);
    } else if (args[i] === "--quality" && args[i + 1]) {
      quality = parseInt(args[++i]);
    } else if (args[i] === "--max-size" && args[i + 1]) {
      maxSize = parseInt(args[++i]);
    } else if (args[i] === "--data-uri") {
      dataUri = true;
    } else if (!args[i].startsWith("--")) {
      input = args[i];
    }
  }

  if (!input) {
    console.error("请提供图片路径");
    process.exit(1);
  }

  try {
    if (dataUri) {
      const result = await img2DataUri({ input, maxWidth, maxHeight, quality, maxSize });
      console.log(result);
    } else {
      const result = await img2base64({ input, maxWidth, maxHeight, quality, maxSize });
      console.log(`MIME: ${result.mimeType}`);
      console.log(`尺寸: ${result.width}x${result.height}`);
      console.log(`大小: ${(result.size / 1024).toFixed(1)}KB`);
      console.log(`Base64长度: ${result.base64.length}`);
      console.log(`\n${result.base64.slice(0, 100)}...`);
    }
  } catch (e) {
    console.error("转换失败:", e);
    process.exit(1);
  }
}

main();
