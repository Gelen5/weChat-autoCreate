# 公众号文章组件库

手写组件化 HTML 时照此设计。所有片段都是**内联样式、无 class/id**，可直接复制进文章。
配合 `article-template.html`（带手机预览框的骨架）使用。

---

## 设计 token

**配色（克制的黑白灰，高级感来源）**

| 用途 | 色值 |
|------|------|
| 主文字 | `#1d1d1f` |
| 次级文字 | `#6b7280` |
| 浅辅助 / caption | `#9ca3af` |
| 深色块背景 | `#111` |
| 浅灰底 | `#f9fafb` / `#fafafa` |
| 边框 | `#e5e7eb` / `#eee` |
| chip 底 | `#f3f4f6` |

主题色默认不用彩色；需要点缀时再引入**一个**强调色，全篇统一。

**字号 / 间距**

- 正文 15px，行高 1.8，色 `#1d1d1f`
- 小标题 16px / 700，大标题（封面）20px / 800
- caption、标签、辅助文字 11–13px，色 `#9ca3af`
- 所有文字块段前段后 `margin:8px 0`，区块之间 `margin:8px 0 28px`

**字体**：`-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif`

---

## 硬规则

- 全内联样式。`<style>`、`class`、`id` 在微信全部失效。
- `position`、`@media`、CSS 动画失效。`flex` 静态布局（数字徽章行、标签行）可用，但别依赖 `gap` 做关键间距，必要时用 `margin`。
- **内联 `<svg>` 静态信息图：微信支持，直接写进正文**，矢量清晰、不占图片配额——优先用它做数据可视化。
- 配图用 `<img src="本地路径或URL">`，publish.ts 会自动上传微信并替换 src。正文图单张 ≤1MB。
- 文章最外层用一个 `<section>` 容器包裹（见下）。

---

## 组件

### 1. 文章容器（最外层）

```html
<section style="margin:0 auto;padding:24px 20px 32px;max-width:677px;background:#fff;color:#1d1d1f;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif;font-size:15px;line-height:1.8;letter-spacing:0.2px;">
  <!-- 所有内容放这里 -->
</section>
```

### 2. 封面卡（深色）

```html
<section style="margin:0 0 20px;padding:28px 20px;border-radius:14px;background:#111;text-align:center;">
  <p style="margin:0 0 6px;font-size:11px;line-height:1.6;color:rgba(255,255,255,0.35);font-weight:500;letter-spacing:3px;">品牌名 · 栏目</p>
  <p style="margin:0 0 10px;font-size:20px;line-height:1.4;color:#fff;font-weight:800;">文章主标题</p>
  <p style="margin:0;font-size:14px;line-height:1.6;color:rgba(255,255,255,0.55);">一句话副标题</p>
</section>
```

### 3. 编号小标题

```html
<section style="display:flex;align-items:center;gap:10px;margin:8px 0 12px;">
  <span style="display:inline-flex;align-items:center;justify-content:center;width:26px;height:26px;border-radius:50%;background:#1d1d1f;color:#fff;font-size:13px;font-weight:800;">1</span>
  <p style="margin:0;font-size:16px;line-height:1.5;color:#1d1d1f;font-weight:700;">小标题文字</p>
</section>
```

普通小标题（无编号）：`<p style="margin:8px 0 12px;font-size:16px;font-weight:700;color:#1d1d1f;">…</p>`

### 4. 正文段落

```html
<p style="margin:8px 0;font-size:15px;line-height:1.8;color:#1d1d1f;">正文……重点用 <strong>加粗</strong>。</p>
```

### 5. 分隔线

```html
<hr style="margin:24px 0;border:0;border-top:1px solid #eee;" />
```

### 6. callout — 浅灰信号框

```html
<section style="margin:12px 0;padding:14px 16px;border-radius:10px;background:#f9fafb;border-left:3px solid #d1d5db;">
  <p style="margin:0;font-size:15px;line-height:1.8;color:#1d1d1f;"><strong>提示标题</strong> — 一句关键信息。</p>
</section>
```

### 7. callout — 深色强调框

```html
<section style="margin:16px 0;padding:16px 18px;border-radius:10px;background:#111;color:#fff;">
  <p style="margin:0 0 8px;font-size:14px;line-height:1.8;color:rgba(255,255,255,0.5);font-weight:600;">小标</p>
  <p style="margin:8px 0;font-size:15px;line-height:1.8;color:rgba(255,255,255,0.9);">强调正文。</p>
</section>
```

### 8. 金句框（深色 blockquote）

```html
<blockquote style="margin:12px 0;padding:14px 18px;background:#111;color:#fff;border-radius:10px;border-left:0;font-size:15px;line-height:1.8;">
  <p style="margin:0;color:rgba(255,255,255,0.9);font-weight:600;">金句第一行。</p>
  <p style="margin:8px 0 0;color:rgba(255,255,255,0.5);">收尾的轻一句。</p>
</blockquote>
```

### 9. 步骤卡片

```html
<section style="margin:8px 0;">
  <section style="margin:8px 0;padding:10px 14px;border-radius:8px;background:#f9fafb;border:1px solid #e5e7eb;">
    <p style="margin:0;font-size:15px;line-height:1.8;color:#1d1d1f;"><span style="color:#6b7280;font-weight:700;margin-right:6px;">第一</span>这一步做什么</p>
  </section>
  <!-- 重复：第二、第三 -->
</section>
```

### 10. 配图 + caption

```html
<section style="margin:14px 0 16px;">
  <img src="images/xxx.png" style="display:block;width:100%;border-radius:10px;" />
  <p style="margin:6px 0 0;font-size:11px;line-height:1.6;color:#9ca3af;text-align:center;">图注：一句说明。</p>
</section>
```

### 11. 文末总结块

```html
<section style="margin:8px 0 20px;padding:18px;border-radius:10px;background:#111;">
  <p style="margin:0 0 8px;font-size:16px;line-height:1.5;color:#fff;font-weight:700;">写在最后</p>
  <p style="margin:8px 0;font-size:15px;line-height:1.8;color:rgba(255,255,255,0.8);">总结正文……</p>
</section>
```

### 12. 标签 chips

```html
<section style="margin:16px 0 0;display:flex;gap:6px;flex-wrap:wrap;">
  <span style="display:inline-block;padding:4px 10px;border-radius:20px;background:#f3f4f6;color:#9ca3af;font-size:11px;">#标签</span>
</section>
```

---

## 内联 SVG 信息图（重点）

数据可视化优先用内联 SVG，不要调 AI 生图。`viewBox` 用 `0 0 335 H`（335 贴合手机正文宽度），
`style="width:100%;height:auto;display:block;border-radius:10px;"`，外层套配图 section。
文字 `font-family="system-ui"`，标题 11px/700，正文 8–9px，配色用上面的灰阶。

**模板 A — 双卡对比**

```html
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 335 155" style="width:100%;height:auto;display:block;border-radius:10px;">
  <rect width="335" height="155" rx="10" fill="#fafafa"/>
  <text x="167" y="22" text-anchor="middle" font-size="11" font-weight="700" fill="#374151" font-family="system-ui">对比标题</text>
  <rect x="20" y="40" width="140" height="95" rx="8" fill="#fff" stroke="#e5e7eb"/>
  <text x="90" y="60" text-anchor="middle" font-size="10" font-weight="700" fill="#374151" font-family="system-ui">左方案</text>
  <text x="90" y="80" text-anchor="middle" font-size="8.5" fill="#9ca3af" font-family="system-ui">要点一</text>
  <rect x="175" y="40" width="140" height="95" rx="8" fill="#fff" stroke="#1d1d1f" stroke-width="1.5"/>
  <text x="245" y="60" text-anchor="middle" font-size="10" font-weight="700" fill="#1d1d1f" font-family="system-ui">右方案</text>
  <text x="245" y="80" text-anchor="middle" font-size="8.5" fill="#6b7280" font-family="system-ui">要点一</text>
</svg>
```

**模板 B — 时间线 / 演变路径**

```html
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 335 120" style="width:100%;height:auto;display:block;border-radius:10px;">
  <rect width="335" height="120" rx="10" fill="#fafafa"/>
  <text x="167" y="22" text-anchor="middle" font-size="11" font-weight="700" fill="#374151" font-family="system-ui">演变路径</text>
  <line x1="45" y1="60" x2="290" y2="60" stroke="#d1d5db" stroke-width="1.5"/>
  <circle cx="70" cy="60" r="6" fill="#1d1d1f"/>
  <text x="70" y="83" text-anchor="middle" font-size="9" fill="#1d1d1f" font-family="system-ui" font-weight="600">阶段一</text>
  <circle cx="167" cy="60" r="6" fill="#1d1d1f"/>
  <text x="167" y="83" text-anchor="middle" font-size="9" fill="#1d1d1f" font-family="system-ui" font-weight="600">阶段二</text>
  <circle cx="265" cy="60" r="6" fill="#1d1d1f"/>
  <text x="265" y="83" text-anchor="middle" font-size="9" fill="#1d1d1f" font-family="system-ui" font-weight="600">阶段三</text>
</svg>
```

**模板 C — 飞轮 / 闭环**：中心 `<circle>` + 四角 `<rect>` 卡片 + `<line>`/`<path>` 连接 + `<polygon>` 箭头。

复杂图也可以用 HTML/CSS 写好，再用 Chrome headless 截图成 PNG 当配图（见 SKILL.md「Step 3 — 配图」）。

---

## 写作建议

- 一篇文章挑 3–5 种组件循环用，别每段都换花样。
- 每个核心论点尽量配一张图（SVG 信息图或截图），是和「套模板」拉开差距的关键。
- 深色块（封面 / 强调框 / 总结块）全篇控制在 3–4 个，多了发闷。
