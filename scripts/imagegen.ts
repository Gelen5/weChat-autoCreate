/**
 * AI图片生成
 * OpenAI gpt-image-2/dall-e-3 + 3次重试机制
 */

import * as fs from "fs";
import * as path from "path";
import axios from "axios";

interface ImageGenOptions {
  prompt: string;
  model?: "gpt-image-2" | "dall-e-3";
  size?: "1024x1024" | "1792x1024" | "1024x1792";
  quality?: "standard" | "hd";
  n?: number;
  outputDir?: string;
}

interface ImageGenResult {
  paths: string[];
  revised_prompt?: string;
}

const MAX_RETRIES = 3;
const RETRY_DELAYS = [1000, 3000, 5000]; // 递增延迟

export async function generateImage(options: ImageGenOptions): Promise<ImageGenResult> {
  const {
    prompt,
    model = "dall-e-3",
    size = "1024x1024",
    quality = "standard",
    n = 1,
    outputDir = "./output",
  } = options;

  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    throw new Error("OPENAI_API_KEY 环境变量未设置");
  }

  // 确保输出目录存在
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  let lastError: Error | null = null;

  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    try {
      console.log(`生成图片 (尝试 ${attempt + 1}/${MAX_RETRIES}): ${prompt.slice(0, 50)}...`);

      const requestBody: any = {
        model,
        prompt,
        n,
        size,
      };

      // dall-e-3 支持 quality 参数
      if (model === "dall-e-3") {
        requestBody.quality = quality;
      }

      // gpt-image-2 使用新的API格式
      if (model === "gpt-image-2") {
        const resp = await axios.post(
          "https://api.openai.com/v1/images/generations",
          requestBody,
          {
            headers: {
              Authorization: `Bearer ${apiKey}`,
              "Content-Type": "application/json",
            },
            timeout: 120000,
          }
        );

        const data = resp.data;
        const paths: string[] = [];

        for (let i = 0; i < data.data.length; i++) {
          const item = data.data[i];

          if (item.b64_json) {
            // base64响应
            const buffer = Buffer.from(item.b64_json, "base64");
            const filename = `gen_${Date.now()}_${i}.png`;
            const filepath = path.join(outputDir, filename);
            fs.writeFileSync(filepath, buffer);
            paths.push(filepath);
          } else if (item.url) {
            // URL响应 - 下载图片
            const imgResp = await axios.get(item.url, {
              responseType: "arraybuffer",
              timeout: 30000,
            });
            const filename = `gen_${Date.now()}_${i}.png`;
            const filepath = path.join(outputDir, filename);
            fs.writeFileSync(filepath, Buffer.from(imgResp.data));
            paths.push(filepath);
          }
        }

        return {
          paths,
          revised_prompt: data.data[0]?.revised_prompt,
        };
      }

      // dall-e-3
      const resp = await axios.post(
        "https://api.openai.com/v1/images/generations",
        requestBody,
        {
          headers: {
            Authorization: `Bearer ${apiKey}`,
            "Content-Type": "application/json",
          },
          timeout: 120000,
        }
      );

      const data = resp.data;
      const paths: string[] = [];

      for (let i = 0; i < data.data.length; i++) {
        const item = data.data[i];

        if (item.url) {
          const imgResp = await axios.get(item.url, {
            responseType: "arraybuffer",
            timeout: 30000,
          });
          const filename = `gen_${Date.now()}_${i}.png`;
          const filepath = path.join(outputDir, filename);
          fs.writeFileSync(filepath, Buffer.from(imgResp.data));
          paths.push(filepath);
        } else if (item.b64_json) {
          const buffer = Buffer.from(item.b64_json, "base64");
          const filename = `gen_${Date.now()}_${i}.png`;
          const filepath = path.join(outputDir, filename);
          fs.writeFileSync(filepath, buffer);
          paths.push(filepath);
        }
      }

      return {
        paths,
        revised_prompt: data.data[0]?.revised_prompt,
      };
    } catch (e: any) {
      lastError = e;
      const isRateLimit = e?.response?.status === 429;
      const isServerError = e?.response?.status >= 500;

      if (isRateLimit || isServerError) {
        const delay = RETRY_DELAYS[attempt] || 5000;
        console.warn(`请求失败 (${e?.response?.status || "unknown"})，${delay / 1000}s后重试...`);
        await sleep(delay);
        continue;
      }

      // 其他错误不重试
      throw e;
    }
  }

  throw lastError || new Error("图片生成失败");
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// CLI入口
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log("用法: ts-node imagegen.ts <prompt>");
    console.log("  --model <model>      模型: gpt-image-2 | dall-e-3 (默认)");
    console.log("  --size <size>        尺寸: 1024x1024 | 1792x1024 | 1024x1792");
    console.log("  --quality <quality>  质量: standard | hd");
    console.log("  --output <dir>       输出目录");
    process.exit(0);
  }

  let prompt = "";
  let model: "gpt-image-2" | "dall-e-3" = "dall-e-3";
  let size: "1024x1024" | "1792x1024" | "1024x1792" = "1024x1024";
  let quality: "standard" | "hd" = "standard";
  let outputDir = "./output";

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--model" && args[i + 1]) {
      model = args[++i] as any;
    } else if (args[i] === "--size" && args[i + 1]) {
      size = args[++i] as any;
    } else if (args[i] === "--quality" && args[i + 1]) {
      quality = args[++i] as any;
    } else if (args[i] === "--output" && args[i + 1]) {
      outputDir = args[++i];
    } else if (!args[i].startsWith("--")) {
      prompt = args[i];
    }
  }

  if (!prompt) {
    console.error("请提供图片描述");
    process.exit(1);
  }

  try {
    const result = await generateImage({ prompt, model, size, quality, outputDir });
    console.log("生成完成:");
    for (const p of result.paths) {
      console.log(`  ${p}`);
    }
    if (result.revised_prompt) {
      console.log(`优化后的提示: ${result.revised_prompt}`);
    }
  } catch (e) {
    console.error("生成失败:", e);
    process.exit(1);
  }
}

main();
