# AI News Signal Green — AI 新闻信号卡风

用于「AI 模型发布 / 产品更新新闻 / 真假消息拆解 / 行业快讯解读」类公众号文章。它继承 `tech-card-green.md` 的清爽技术文档气质，但更强调新闻判断、证据分层和读者快速扫读。

## Visual DNA

- Mood: AI newsroom, product changelog, analyst note, signal dashboard.
- Canvas: white article body with a dark navy hero block, green as confirmed-signal accent.
- Composition: first-screen conclusion, real official images, small evidence chips, section numbers, compact SVG explainers.
- Best for: Claude/OpenAI/AI 工具发布、模型版本更新、传闻澄清、媒体报道汇总、产品安全事件。
- Avoid: 夸张营销标题、无来源大图、纯装饰渐变、过多彩色标签。

## Color Tokens

```text
hero-bg:       #111827
accent:        #059669
accent-light:  #10B981
accent-bright: #34D399
accent-soft:   #ECFDF5
ink:           #111827
body:          #374151
muted:         #9CA3AF
line:          #E5E7EB
line-soft:     #F3F4F6
surface:       #FFFFFF
surface-soft:  #FAFAFA
warning-bg:    #FEF3C7
warning-text:  #92400E
```

## Typography

```text
article:      15px / 1.78 / letter-spacing 0.4px
hero label:   11px / 700 / letter-spacing 2.5px
hero title:   26px / 900 / line-height 1.12
section no:   26px / 900 / line-height 1
section h2:   17px / 900
card body:    14-15px / 1.35-1.8
caption:      11px / 1.6 / muted
```

Do not use viewport-scaled fonts. Keep letter spacing non-negative.

## Structure Pattern

Use this order for news articles:

1. Dark hero with topic and one-line status.
2. Real source image close to the top.
3. Green conclusion callout: what is confirmed.
4. Three-card signal row: confirmed / key capability / pending.
5. Numbered sections: news, stack, benchmark, risk/context, rumor.
6. SVG explainers: timeline, signal layers, capability axes.
7. Source list with official links and media links.

## Component Recipes

### Article Wrapper

```html
<section style="max-width:677px;margin:0 auto;background:#ffffff;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;color:#374151;line-height:1.78;letter-spacing:0.4px;overflow-x:hidden;font-size:15px;">
  ...
</section>
```

### Dark News Hero

```html
<section style="margin:0;padding:26px 20px 18px;background:#111827;color:#ffffff;">
  <p style="margin:0 0 8px;font-size:11px;line-height:1.6;color:rgba(255,255,255,0.48);font-weight:700;letter-spacing:2.5px;">AI NEWS · TOPIC</p>
  <p style="margin:0;font-size:26px;line-height:1.12;color:#ffffff;font-weight:900;">主标题<br><span style="color:#34D399;">关键词</span></p>
  <p style="margin:12px 0 0;font-size:14px;line-height:1.65;color:rgba(255,255,255,0.72);">一句状态判断。</p>
</section>
```

### Real Image Frame

Use official screenshots, official hero images, product UI screenshots, or publication screenshots. Keep every body image under 1MB.

```html
<section style="margin:0 20px 18px;padding-top:18px;">
  <section style="background:#ffffff;border-radius:12px;padding:6px;border:1px solid #F3F4F6;box-shadow:0 4px 12px rgba(17,24,39,0.06);">
    <figure style="margin:0;border-radius:8px;overflow:hidden;">
      <img src="assets/example.jpg" style="width:100%;display:block;" />
    </figure>
  </section>
  <p style="margin:7px 0 0;font-size:11px;line-height:1.6;color:#9CA3AF;text-align:center;">图源：官方页面 / 媒体页面</p>
</section>
```

### Conclusion Callout

```html
<section style="margin:0 20px 20px;padding:14px 16px;border-radius:12px;background:#ECFDF5;border-left:4px solid #059669;">
  <p style="margin:0;font-size:15px;line-height:1.8;color:#111827;"><strong>先把结论说清楚：</strong>一句明确判断，重点用 <span style="color:#059669;font-weight:800;">绿色强调</span>。</p>
</section>
```

### Three Signal Cards

Use when a news item has different evidence levels. Keep all three cards visible in one row.

```html
<section style="margin:0 20px 24px;">
  <section style="white-space:nowrap;">
    <section style="display:inline-block;vertical-align:top;width:31.5%;margin-right:1.8%;border-radius:12px;padding:12px 8px;background:linear-gradient(135deg,#059669,#10B981);">
      <p style="margin:0;font-size:11px;color:rgba(255,255,255,0.72);font-weight:800;">已官宣</p>
      <p style="margin:6px 0 0;font-size:14px;line-height:1.35;color:#fff;font-weight:900;white-space:normal;">Opus 4.8</p>
    </section>
    <section style="display:inline-block;vertical-align:top;width:31.5%;margin-right:1.8%;border-radius:12px;padding:12px 8px;background:#fff;border:1px solid #E5E7EB;box-shadow:0 2px 6px rgba(0,0,0,0.04);">
      <p style="margin:0;font-size:11px;color:#9CA3AF;font-weight:800;">重点能力</p>
      <p style="margin:6px 0 0;font-size:14px;line-height:1.35;color:#111827;font-weight:900;white-space:normal;">长任务代理</p>
    </section>
    <section style="display:inline-block;vertical-align:top;width:31.5%;border-radius:12px;padding:12px 8px;background:#fff;border:1px solid #E5E7EB;box-shadow:0 2px 6px rgba(0,0,0,0.04);">
      <p style="margin:0;font-size:11px;color:#9CA3AF;font-weight:800;">仍待确认</p>
      <p style="margin:6px 0 0;font-size:14px;line-height:1.35;color:#111827;font-weight:900;white-space:normal;">Sonnet 4.8</p>
    </section>
  </section>
</section>
```

### Section Header

```html
<section style="margin:34px 20px 16px;display:flex;align-items:flex-start;">
  <section style="width:44px;min-width:44px;">
    <p style="margin:0;color:#059669;font-size:26px;line-height:1;font-weight:900;">01</p>
    <p style="margin:5px 0 0;color:#9CA3AF;font-size:10px;line-height:1;font-weight:800;letter-spacing:1.5px;">NEWS</p>
  </section>
  <section style="width:1px;height:42px;background:#D1D5DB;margin:1px 12px 0 0;"></section>
  <section>
    <p style="margin:0;font-size:17px;line-height:1.45;color:#111827;font-weight:900;">小标题</p>
    <p style="margin:3px 0 0;font-size:11px;line-height:1.5;color:#9CA3AF;">一句副标题。</p>
  </section>
</section>
```

### Evidence Warning

Use yellow for rumor / not-yet-confirmed / version caveats. Only use once or twice per article.

```html
<section style="margin:0 20px 24px;padding:14px 16px;border-radius:12px;background:#FEF3C7;border-left:4px solid #F59E0B;">
  <p style="margin:0;font-size:15px;line-height:1.8;color:#92400E;"><strong>一句话避坑：</strong>明确说明哪些还不是官宣。</p>
</section>
```

## SVG Visualization Defaults

- `viewBox="0 0 335 H"` for mobile-safe width.
- Background `#FAFAFA`, radius 12.
- Text font family `system-ui`.
- Use green only for confirmed facts; gray for pending/unknown; navy for current focal point.
- Useful templates: timeline, three-layer evidence stack, three-axis capability cards.

## Writing Rules

- 第一屏必须回答「到底发生了什么」。
- 将信息分为：已官宣 / 官方文档 / 媒体报道 / 社区传闻。
- 每个事实段最好有一条来源线索：官方发布、文档、系统卡、媒体报道。
- 不把泄露字符串、社区截图、预测市场写成确定事实。
- 真图优先：官方图、产品截图、文档截图、媒体截图；AI 生图只做封面或氛围，不用于事实图。
- 标题可以有冲击力，正文必须把证据等级说清楚。
