import { readFile } from "node:fs/promises";
import { basename } from "node:path";

const TOKEN_URL = "https://api.weixin.qq.com/cgi-bin/token";
const UPLOADIMG_URL = "https://api.weixin.qq.com/cgi-bin/media/uploadimg";
const ADD_MATERIAL_URL = "https://api.weixin.qq.com/cgi-bin/material/add_material";
const DRAFT_ADD_URL = "https://api.weixin.qq.com/cgi-bin/draft/add";

interface WxError {
  errcode?: number;
  errmsg?: string;
}

function check<T extends WxError>(data: T, what: string): T {
  if (data.errcode && data.errcode !== 0) {
    throw new Error(`WeChat ${what} failed: errcode=${data.errcode} errmsg=${data.errmsg}`);
  }
  return data;
}

export async function getAccessToken(appId: string, appSecret: string): Promise<string> {
  const url = `${TOKEN_URL}?grant_type=client_credential&appid=${encodeURIComponent(appId)}&secret=${encodeURIComponent(appSecret)}`;
  const res = await fetch(url);
  const data = (await res.json()) as WxError & { access_token?: string };
  check(data, "token");
  if (!data.access_token) throw new Error("WeChat token response missing access_token");
  return data.access_token;
}

const MIME: Record<string, string> = {
  png: "image/png",
  jpg: "image/jpeg",
  jpeg: "image/jpeg",
  gif: "image/gif",
};

async function fileToBlob(path: string): Promise<{ blob: Blob; name: string; size: number }> {
  const buf = await readFile(path);
  const ext = (path.split(".").pop() || "png").toLowerCase();
  const name = basename(path);
  return { blob: new Blob([buf], { type: MIME[ext] || "image/png" }), name, size: buf.length };
}

// Upload an in-article image. Returns a WeChat-hosted URL. Limit: 1MB, jpg/png only.
export async function uploadBodyImage(path: string, accessToken: string): Promise<string> {
  const { blob, name, size } = await fileToBlob(path);
  if (size > 1024 * 1024) {
    throw new Error(`Body image too large (${(size / 1024 / 1024).toFixed(2)}MB > 1MB): ${path}`);
  }
  const form = new FormData();
  form.append("media", blob, name);
  const res = await fetch(`${UPLOADIMG_URL}?access_token=${accessToken}`, { method: "POST", body: form });
  const data = (await res.json()) as WxError & { url?: string };
  check(data, "uploadimg");
  if (!data.url) throw new Error("WeChat uploadimg response missing url");
  return data.url;
}

// Upload a permanent image material. Returns media_id (used as article cover thumb).
export async function uploadCoverMaterial(path: string, accessToken: string): Promise<string> {
  const { blob, name, size } = await fileToBlob(path);
  if (size > 10 * 1024 * 1024) {
    throw new Error(`Cover image too large (${(size / 1024 / 1024).toFixed(2)}MB > 10MB): ${path}`);
  }
  const form = new FormData();
  form.append("media", blob, name);
  const res = await fetch(`${ADD_MATERIAL_URL}?access_token=${accessToken}&type=image`, {
    method: "POST",
    body: form,
  });
  const data = (await res.json()) as WxError & { media_id?: string };
  check(data, "add_material");
  if (!data.media_id) throw new Error("WeChat add_material response missing media_id");
  return data.media_id;
}

export interface DraftArticle {
  title: string;
  author?: string;
  digest?: string;
  content: string;
  thumbMediaId: string;
  contentSourceUrl?: string;
  needOpenComment?: number;
  onlyFansCanComment?: number;
}

// Create a draft in the Official Account draft box. Returns media_id of the draft.
export async function addDraft(article: DraftArticle, accessToken: string): Promise<string> {
  const body = {
    articles: [
      {
        article_type: "news",
        title: article.title.slice(0, 64),
        author: article.author || "",
        digest: (article.digest || "").slice(0, 120),
        content: article.content,
        content_source_url: article.contentSourceUrl || "",
        thumb_media_id: article.thumbMediaId,
        need_open_comment: article.needOpenComment ?? 1,
        only_fans_can_comment: article.onlyFansCanComment ?? 0,
      },
    ],
  };
  const res = await fetch(`${DRAFT_ADD_URL}?access_token=${accessToken}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = (await res.json()) as WxError & { media_id?: string };
  check(data, "draft/add");
  if (!data.media_id) throw new Error("WeChat draft/add response missing media_id");
  return data.media_id;
}
