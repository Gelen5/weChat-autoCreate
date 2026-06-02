# Tech Card Green — 绿色技术卡片风

当用户想要「技术教程 / AI 工具 / SaaS 文档 / 产品更新 / 安装指南」类公众号排版时，读取本风格预设。它是 `wechat-publisher` 模式 A 的视觉覆盖层：先读 `references/components.md` 和 `references/article-template.html`，再用本文件的配色、字阶和组件片段覆盖默认黑白灰。下面的组件都是可直接复制、改字使用的内联 HTML。

## Visual DNA

- Mood: 移动端产品文档 / SaaS 更新日志 / 技术教程 / 干净的公众号文章。
- Canvas: 白底、居中、max-width 约 677px、移动端安全侧边距。
- Composition: 小标签、加粗承诺、带框截图、编号小节、终端卡片。
- 避免：繁复的公众号花边、重渐变、密集贴纸、营销大图 hero。

## Color Tokens

```text
accent:        #059669
accent-light:  #10B981
accent-soft:   #ECFDF5
highlight:     #FDE68A
ink:           #111827
body:          #374151
body-muted:    #4B5563
muted:         #9CA3AF
muted-light:   #D1D5DB
line:          #E5E7EB
line-soft:     #F3F4F6
surface:       #FFFFFF
surface-soft:  #FAFAFA
warning-bg:    #FEF3C7
warning-text:  #92400E
```

## Typography

```text
base family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif
article:     14px / 1.85 / letter-spacing 0.5px / text-align justify（中文段落）
hero title:  28px / 900 / line-height 1.05 / letter-spacing -2px
section no:  28px / 900 / line-height 1
section h2:  17px / 900
subheading:  15-16px / 800
caption:     10-12px / 600-700 / letter-spacing 1-2px
```

## Component Recipes（可直接复制 · 改字即用）

### Article Wrapper（最外层容器）

```html
<section style="max-width:677px;margin:0 auto;background:#ffffff;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;color:#374151;line-height:1.75;letter-spacing:0.5px;overflow-x:hidden;">
  ...
</section>
```

### Hero Card（开头用一次）

```html
<section style="margin:0 20px 32px;background:#fff;border:1.5px solid rgba(5,150,105,0.15);border-radius:20px;box-shadow:0 4px 20px rgba(0,0,0,0.06);overflow:hidden;"><div style="padding:32px 24px 28px;"><p style="margin:0 0 14px;font-size:11px;font-weight:700;letter-spacing:2px;color:#9CA3AF;">栏目 · LABEL</p><p style="margin:0;font-size:28px;font-weight:900;line-height:1.05;letter-spacing:-2px;color:#111827;">第一行黑色承诺</p><p style="margin:4px 0 0;font-size:28px;font-weight:900;line-height:1.05;letter-spacing:-2px;color:#059669;">第二行绿色承诺</p></div><div style="height:6px;background:linear-gradient(90deg,#059669,#10B981);"></div></section>
```

### Horizontal Part Navigation（首个大节前可放一排概览）

> 注意：`overflow-x:scroll` 在微信内置浏览器里不完全稳定，部分机型会压扁或铺开。不放心可省略此组件，或改用竖排概览列表。

```html
<section style="margin:0 20px 32px;"><div style="overflow-x:scroll;-webkit-overflow-scrolling:touch;white-space:nowrap;padding-bottom:8px;"><div style="display:inline-block;width:110px;border-radius:12px;padding:12px;margin-right:8px;background:linear-gradient(135deg,#059669,#10B981);vertical-align:top;white-space:normal;"><p style="margin:0;font-size:13px;font-weight:800;color:#fff;">01 概览</p></div><div style="display:inline-block;width:110px;border-radius:12px;padding:12px;margin-right:8px;background:#fff;border:1px solid #E5E7EB;box-shadow:0 2px 6px rgba(0,0,0,0.04);vertical-align:top;white-space:normal;"><p style="margin:0;font-size:13px;font-weight:800;color:#111827;">02 步骤</p></div></div></section>
```

### Section Header（每个大节开头）

```html
<section style="margin:48px 0 32px;padding:0 20px;display:flex;align-items:center;gap:14px;"><div style="text-align:center;flex:0 0 auto;"><p style="margin:0;font-size:28px;font-weight:900;line-height:1;color:#059669;">01</p><p style="margin:2px 0 0;font-size:10px;font-weight:700;letter-spacing:2px;color:#9CA3AF;">PART</p></div><div style="width:1px;height:36px;background:#E5E7EB;flex:0 0 auto;"></div><div><p style="margin:0;font-size:17px;font-weight:900;color:#111827;">小节标题</p><p style="margin:2px 0 0;font-size:11px;color:#9CA3AF;">小节副标题</p></div></section>
```

### Body Paragraph（正文，含三种行内强调）

```html
<p style="margin:0 20px 20px;font-size:14px;line-height:1.85;letter-spacing:0.5px;color:#374151;text-align:justify;">正文。绿色强调 <strong style="color:#059669;font-weight:700;">这样</strong>；行内标签 <span style="background:#F3F4F6;color:#1F2937;padding:2px 6px;border-radius:4px;font-size:13px;font-weight:600;">tag</span>；黄色高光 <span style="background:linear-gradient(120deg,#FDE68A 0%,rgba(255,255,255,0) 100%);padding:0 4px;border-radius:2px;font-weight:600;color:#111827;">重点</span>。</p>
```

### Terminal Block（命令 / 代码）

```html
<section style="margin:0 20px 24px;border:1.5px solid #E5E7EB;border-radius:10px;overflow:hidden;background:#fff;"><div style="padding:10px 12px;background:#FAFAFA;border-bottom:1px solid #F3F4F6;"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#FF5F56;margin-right:5px;"></span><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#FFBD2E;margin-right:5px;"></span><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#27C93F;"></span></div><div style="padding:14px;font-family:'SF Mono',Consolas,Menlo,monospace;font-size:13px;line-height:1.8;color:#1F2937;word-break:break-all;">npx tsx publish.ts article.html --title "标题"</div></section>
```

### Callout（绿色提示 / 黄色警告）

```html
<section style="margin:0 20px 24px;padding:14px 16px;border-radius:10px;background:#ECFDF5;border-left:3px solid #059669;"><p style="margin:0;font-size:14px;line-height:1.8;color:#065F46;"><strong>提示</strong> — 一句关键信息。</p></section>
<section style="margin:0 20px 24px;padding:14px 16px;border-radius:10px;background:#FEF3C7;"><p style="margin:0;font-size:14px;line-height:1.8;color:#92400E;"><strong>注意</strong> — 一句提醒。</p></section>
```

### Image Frame（截图别裸放）

```html
<section style="margin:0 20px 24px;background:#FFF;border-radius:12px;padding:6px;border:1px solid #F3F4F6;box-shadow:0 4px 6px -1px rgba(0,0,0,0.05);"><figure style="margin:0;border-radius:8px;overflow:hidden;"><img style="width:100%;display:block;" src="图片地址或 base64" /></figure></section>
```

### SVG Infographic（数据/对比/时间线，绿色调，viewBox 0 0 335 H）

```html
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 335 120" style="width:100%;height:auto;display:block;border-radius:10px;"><rect width="335" height="120" rx="10" fill="#FAFAFA"/><text x="167" y="22" text-anchor="middle" font-size="11" font-weight="700" fill="#111827" font-family="system-ui">标题</text><line x1="45" y1="60" x2="290" y2="60" stroke="#E5E7EB" stroke-width="1.5"/><circle cx="70" cy="60" r="6" fill="#059669"/><text x="70" y="83" text-anchor="middle" font-size="9" fill="#059669" font-family="system-ui" font-weight="600">阶段一</text><circle cx="167" cy="60" r="6" fill="#059669"/><text x="167" y="83" text-anchor="middle" font-size="9" fill="#059669" font-family="system-ui" font-weight="600">阶段二</text><circle cx="265" cy="60" r="6" fill="#10B981"/><text x="265" y="83" text-anchor="middle" font-size="9" fill="#10B981" font-family="system-ui" font-weight="600">阶段三</text></svg>
```

## Layout Rules

- 段落容器统一 `padding:0 20px`，区块 `margin-bottom:16-24px`。
- 中文正文 `text-align:justify`。
- 装饰比普通公众号模板更少，让卡片和留白做事。
- 绿色只标结构和关键概念，不要每句都绿。
- 截图就近放在对应说明旁。
- 命令尽量短；过长靠 `word-break:break-all`。
