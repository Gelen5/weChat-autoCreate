/**
 * 微信API封装
 * token缓存(5分钟缓冲) + 图片上传(正文+封面) + draft/add草稿 + 小绿书图片帖 + 多图文
 */

import * as fs from "fs";
import * as path from "path";
import * as https from "https";
import * as http from "http";
import axios from "axios";
import * as sharp from "sharp";

interface WeChatConfig {
  appid: string;
  secret: string;
}

interface DraftArticle {
  title: string;
  content: string;
  thumb_media_id: string;
  author?: string;
  digest?: string;
  content_source_url?: string;
  need_open_comment?: number;
  only_fans_can_comment?: number;
}

interface TokenCache {
  token: string;
  expiresAt: number; // Unix timestamp
}

const TOKEN_BUFFER = 5 * 60 * 1000; // 5分钟缓冲（毫秒）

export class WeChatAPI {
  private appid: string;
  private secret: string;
  private tokenCache: TokenCache | null = null;

  constructor(config?: WeChatConfig) {
    // 优先使用传入配置，否则从环境变量读取
    this.appid = config?.appid || process.env.WECHAT_APPID || "";
    this.secret = config?.secret || process.env.WECHAT_SECRET || "";

    if (!this.appid || !this.secret) {
      // 尝试从config.yaml加载
      this.loadConfigFromFile();
    }
  }

  private loadConfigFromFile(): void {
    const configPaths = [
      path.resolve(process.cwd(), "config.yaml"),
      path.resolve(process.cwd(), "config.yml"),
      path.resolve(process.cwd(), "config.json"),
    ];

    for (const configPath of configPaths) {
      if (fs.existsSync(configPath)) {
        try {
          const content = fs.readFileSync(configPath, "utf-8");
          let config: any;
          if (configPath.endsWith(".json")) {
            config = JSON.parse(content);
          } else {
            // 简单YAML解析
            config = this.parseSimpleYaml(content);
          }
          this.appid = this.appid || config?.wechat?.appid || "";
          this.secret = this.secret || config?.wechat?.secret || "";
          if (this.appid && this.secret) return;
        } catch (_) {}
      }
    }
  }

  private parseSimpleYaml(content: string): any {
    const result: any = {};
    let currentSection: any = result;
    const sectionStack: any[] = [result];

    for (const line of content.split("\n")) {
      const sectionMatch = line.match(/^(\w+):$/);
      if (sectionMatch) {
        const section: any = {};
        result[sectionMatch[1]] = section;
        currentSection = section;
        continue;
      }
      const kvMatch = line.match(/^\s+(\w+):\s*(.*)$/);
      if (kvMatch) {
        let value: any = kvMatch[2].trim();
        if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
          value = value.slice(1, -1);
        }
        currentSection[kvMatch[1]] = value;
      }
    }
    return result;
  }

  /**
   * 获取access_token（带缓存和5分钟缓冲）
   */
  async getAccessToken(): Promise<string> {
    const now = Date.now();

    if (this.tokenCache && this.tokenCache.expiresAt > now + TOKEN_BUFFER) {
      return this.tokenCache.token;
    }

    const url = "https://api.weixin.qq.com/cgi-bin/token";
    const resp = await axios.get(url, {
      params: {
        grant_type: "client_credential",
        appid: this.appid,
        secret: this.secret,
      },
      timeout: 10000,
    });

    const data = resp.data;
    if (data.errcode) {
      throw new Error(`获取token失败: ${data.errmsg} (${data.errcode})`);
    }

    this.tokenCache = {
      token: data.access_token,
      expiresAt: now + data.expires_in * 1000,
    };

    return data.access_token;
  }

  /**
   * 上传正文图片（永久素材）
   */
  async uploadImage(filePath: string): Promise<string> {
    const token = await this.getAccessToken();
    const url = `https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=${token}&type=image`;

    const buffer = fs.readFileSync(filePath);
    const filename = path.basename(filePath);

    const FormData = (await import("form-data")).default;
    const form = new FormData();
    form.append("media", buffer, {
      filename,
      contentType: this.getImageMimeType(filePath),
    });

    const resp = await axios.post(url, form, {
      headers: form.getHeaders(),
      timeout: 30000,
    });

    if (resp.data.errcode) {
      throw new Error(`图片上传失败: ${resp.data.errmsg}`);
    }

    return resp.data.url; // 返回微信图片URL
  }

  /**
   * 从URL上传正文图片
   */
  async uploadImageFromUrl(imageUrl: string): Promise<string | null> {
    try {
      // 下载图片
      const resp = await axios.get(imageUrl, {
        responseType: "arraybuffer",
        timeout: 15000,
      });

      const buffer = Buffer.from(resp.data);

      // 验证是否为真实图片
      if (!this.isValidImage(buffer)) {
        console.warn(`非有效图片: ${imageUrl}`);
        return null;
      }

      // 上传到微信
      const token = await this.getAccessToken();
      const url = `https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token=${token}`;

      const FormData = (await import("form-data")).default;
      const form = new FormData();
      const filename = this.extractFilename(imageUrl) || "image.jpg";
      form.append("media", buffer, {
        filename,
        contentType: resp.headers["content-type"] || "image/jpeg",
      });

      const uploadResp = await axios.post(url, form, {
        headers: form.getHeaders(),
        timeout: 30000,
      });

      if (uploadResp.data.errcode) {
        throw new Error(`图片上传失败: ${uploadResp.data.errmsg}`);
      }

      return uploadResp.data.url;
    } catch (e) {
      console.warn(`图片上传失败: ${imageUrl}`, e);
      return null;
    }
  }

  /**
   * 上传封面缩略图（临时素材）
   */
  async uploadThumb(filePath: string): Promise<string | null> {
    const token = await this.getAccessToken();

    // 确保图片不超过64KB
    let buffer = fs.readFileSync(filePath);
    buffer = await this.compressImage(buffer, { maxSize: 64 * 1024 });

    const url = `https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=${token}&type=thumb`;

    const FormData = (await import("form-data")).default;
    const form = new FormData();
    form.append("media", buffer, {
      filename: path.basename(filePath),
      contentType: this.getImageMimeType(filePath),
    });

    const resp = await axios.post(url, form, {
      headers: form.getHeaders(),
      timeout: 30000,
    });

    if (resp.data.errcode) {
      console.error(`封面上传失败: ${resp.data.errmsg}`);
      return null;
    }

    return resp.data.media_id;
  }

  /**
   * 从URL上传封面
   */
  async uploadThumbFromUrl(imageUrl: string): Promise<string | null> {
    try {
      const resp = await axios.get(imageUrl, {
        responseType: "arraybuffer",
        timeout: 15000,
      });
      const buffer = Buffer.from(resp.data);
      const compressed = await this.compressImage(buffer, { maxSize: 64 * 1024 });

      const token = await this.getAccessToken();
      const url = `https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=${token}&type=thumb`;

      const FormData = (await import("form-data")).default;
      const form = new FormData();
      form.append("media", compressed, {
        filename: this.extractFilename(imageUrl) || "cover.jpg",
        contentType: "image/jpeg",
      });

      const uploadResp = await axios.post(url, form, {
        headers: form.getHeaders(),
        timeout: 30000,
      });

      if (uploadResp.data.errcode) {
        return null;
      }

      return uploadResp.data.media_id;
    } catch (e) {
      console.warn(`封面上传失败: ${imageUrl}`, e);
      return null;
    }
  }

  /**
   * 添加单图文草稿
   */
  async addDraft(article: DraftArticle): Promise<string | null> {
    const token = await this.getAccessToken();
    const url = `https://api.weixin.qq.com/cgi-bin/draft/add?access_token=${token}`;

    const resp = await axios.post(url, {
      articles: [article],
    }, { timeout: 15000 });

    if (resp.data.errcode) {
      throw new Error(`创建草稿失败: ${resp.data.errmsg}`);
    }

    return resp.data.media_id;
  }

  /**
   * 添加多图文草稿
   */
  async addDraftMulti(articles: DraftArticle[]): Promise<string | null> {
    const token = await this.getAccessToken();
    const url = `https://api.weixin.qq.com/cgi-bin/draft/add?access_token=${token}`;

    const resp = await axios.post(url, {
      articles,
    }, { timeout: 30000 });

    if (resp.data.errcode) {
      throw new Error(`创建多图文草稿失败: ${resp.data.errmsg}`);
    }

    return resp.data.media_id;
  }

  /**
   * 小绿书图片帖
   */
  async publishImagePost(
    imagePaths: string[],
    title: string,
    content: string
  ): Promise<string | null> {
    const token = await this.getAccessToken();

    // 上传所有图片
    const mediaIds: string[] = [];
    for (const imgPath of imagePaths) {
      const absPath = path.resolve(imgPath);
      let buffer = fs.readFileSync(absPath);
      buffer = await this.compressImage(buffer, { maxSize: 1024 * 1024 });

      const url = `https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=${token}&type=image`;
      const FormData = (await import("form-data")).default;
      const form = new FormData();
      form.append("media", buffer, {
        filename: path.basename(absPath),
        contentType: this.getImageMimeType(absPath),
      });

      const resp = await axios.post(url, form, {
        headers: form.getHeaders(),
        timeout: 30000,
      });

      if (resp.data.media_id) {
        mediaIds.push(resp.data.media_id);
      }
    }

    // 创建小绿书草稿
    const draftUrl = `https://api.weixin.qq.com/cgi-bin/draft/add?access_token=${token}`;
    const imageHtml = mediaIds
      .map(id => `<img src="https://mmbiz.qpic.cn/mmbiz_jpg/${id}/0" />`)
      .join("");

    const resp = await axios.post(draftUrl, {
      articles: [{
        title,
        content: imageHtml + content,
        thumb_media_id: mediaIds[0] || "",
        author: "",
        digest: content.slice(0, 120),
      }],
    }, { timeout: 15000 });

    if (resp.data.errcode) {
      throw new Error(`小绿书发布失败: ${resp.data.errmsg}`);
    }

    return resp.data.media_id;
  }

  // ── 工具方法 ──

  private getImageMimeType(filePath: string): string {
    const ext = path.extname(filePath).toLowerCase();
    const mimeMap: Record<string, string> = {
      ".jpg": "image/jpeg",
      ".jpeg": "image/jpeg",
      ".png": "image/png",
      ".gif": "image/gif",
      ".webp": "image/webp",
      ".bmp": "image/bmp",
    };
    return mimeMap[ext] || "image/jpeg";
  }

  private extractFilename(url: string): string {
    try {
      const pathname = new URL(url).pathname;
      const basename = path.basename(pathname);
      return basename || "image.jpg";
    } catch {
      return "image.jpg";
    }
  }

  private isValidImage(buffer: Buffer): boolean {
    // 检查图片魔数
    if (buffer.length < 4) return false;

    const header = buffer.toString("hex", 0, 4).toUpperCase();
    // JPEG: FFD8
    if (header.startsWith("FFD8")) return true;
    // PNG: 89504E47
    if (header === "89504E47") return true;
    // GIF: 47494638
    if (header.startsWith("47494638")) return true;
    // WebP: 52494646
    if (header.startsWith("52494646")) return true;

    return false;
  }

  private async compressImage(
    buffer: Buffer,
    options: { maxSize: number }
  ): Promise<Buffer> {
    /** 使用sharp压缩图片（跨平台，不依赖sips） */
    if (buffer.length <= options.maxSize) {
      return buffer;
    }

    try {
      let quality = 80;
      let result = buffer;

      while (quality >= 20 && result.length > options.maxSize) {
        result = await sharp(buffer)
          .jpeg({ quality })
          .toBuffer();
        quality -= 10;
      }

      // 如果仍然过大，缩小尺寸
      if (result.length > options.maxSize) {
        const metadata = await sharp(buffer).metadata();
        const scale = Math.sqrt(options.maxSize / buffer.length);
        const newWidth = Math.floor((metadata.width || 800) * scale);

        result = await sharp(buffer)
          .resize(newWidth)
          .jpeg({ quality: 60 })
          .toBuffer();
      }

      return result;
    } catch (e) {
      console.warn(`图片压缩失败，使用原始图片: ${e}`);
      return buffer;
    }
  }
}
