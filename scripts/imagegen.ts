import { writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

const IMAGES_URL = "https://api.openai.com/v1/images/generations";

export interface GenOpts {
  model?: string;
  size?: string;
  quality?: string;
  outPath?: string;
}

// Pick a sensible landscape size per model family.
function landscapeSize(model: string): string {
  if (model.startsWith("gpt-image-2")) return "1792x1024";
  if (model.startsWith("gpt-image-1")) return "1536x1024";
  return "1792x1024"; // dall-e-3
}

// Generate an image via OpenAI and save it as a file. Returns the file path.
export async function generateImage(prompt: string, apiKey: string, opts: GenOpts = {}): Promise<string> {
  const model = opts.model || "gpt-image-2";
  const isDalle = model.startsWith("dall-e");
  const body: Record<string, unknown> = {
    model,
    prompt,
    n: 1,
    size: opts.size || landscapeSize(model),
  };
  if (opts.quality) body.quality = opts.quality;
  else if (model.startsWith("gpt-image-2")) body.quality = "high";
  if (isDalle) body.response_format = "b64_json";

  let data: { data?: { b64_json?: string; url?: string }[]; error?: { message?: string } } | undefined;
  let lastErr: unknown;
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      const res = await fetch(IMAGES_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${apiKey}` },
        body: JSON.stringify(body),
      });
      data = (await res.json()) as typeof data;
      break;
    } catch (err) {
      lastErr = err;
      if (attempt < 3) await new Promise((r) => setTimeout(r, 2000 * attempt));
    }
  }
  if (!data) throw new Error(`OpenAI image request failed after retries: ${lastErr instanceof Error ? lastErr.message : String(lastErr)}`);
  if (data.error) throw new Error(`OpenAI image generation failed: ${data.error.message}`);
  const item = data.data?.[0];
  if (!item) throw new Error("OpenAI image response missing data");

  let buf: Buffer;
  if (item.b64_json) {
    buf = Buffer.from(item.b64_json, "base64");
  } else if (item.url) {
    const imgRes = await fetch(item.url);
    if (!imgRes.ok) throw new Error(`Failed to download generated image (${imgRes.status})`);
    buf = Buffer.from(await imgRes.arrayBuffer());
  } else {
    throw new Error("OpenAI image response missing b64_json and url");
  }

  const path = opts.outPath || join(tmpdir(), `wechat-img-${Date.now()}.png`);
  await writeFile(path, buf);
  return path;
}

// Backwards-compatible cover helper used by publish.ts.
export async function generateCover(prompt: string, apiKey: string, model = "gpt-image-2"): Promise<string> {
  return generateImage(prompt, apiKey, { model });
}

// Build a cover prompt from the article title. Aims for a clean, text-free editorial image.
export function coverPrompt(title: string): string {
  return [
    `A clean, modern editorial cover illustration for an article titled "${title}".`,
    "Flat design, soft tasteful color palette, generous negative space, minimalist composition.",
    "No text, no letters, no words anywhere in the image. Suitable as a WeChat article banner.",
  ].join(" ");
}
