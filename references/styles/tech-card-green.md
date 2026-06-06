# Ink & Gold 高级质感风 (ink-gold)

> **前身：tech-card-green** — 已从多色科技绿重构为单色高级金系统
> 视觉定位：技术洞察 / 行业分析 / 深度思考 / SaaS文档
> 核心理念：**黑白灰骨架 + 暖金点缀，一篇文章只用一个accent色**

---

## 一、视觉定位

| 维度 | 描述 |
|------|------|
| 配色哲学 | Apple设计语言级别——99%的中性色支撑，1%的金色点缀制造高级感 |
| 质感 | 暖灰底 + 近黑Dark块 + 米白强调区，像一本精装书的排版 |
| 节奏 | 段落留白充裕，视觉组件位置克制，每屏幕1-2个锚点 |
| 字体 | 系统无衬线，偏PingFang/Helvetica Neue，字距自然 |

---

## 二、Color Token — Ink & Gold System

### 2.1 中性色（黑白灰骨架，95%的排面来自这些）

| Token | 值 | 用途 |
|-------|------|------|
| `--ink` | `#1D1D1F` | 标题、深色块、Hero背景、终端底、Section圆点 |
| `--body` | `#6E6E73` | 正文主色 |
| `--muted` | `#A1A1A6` | 次要文字、注释、caption、深色块文字 |
| `--line` | `#E5E5E5` | 细边框、分隔线 |
| `--line-soft` | `#D0D0D0` | 分隔线点缀、标签边框 |
| `--surface` | `#F7F7F5` | 浅底背景、步骤卡片底、文末总结底 |
| `--warm` | `#FBF8F1` | 暖米色底：金句框、强调callout、指标卡边框 |

### 2.2 强调色（Gold — 唯一的accent，5%的点睛之笔）

| Token | 值 | 用途 |
|-------|------|------|
| `--gold` | `#C9A962` | 主强调：Category标签、Section编号、Hero点缀、链接、accent边框 |
| `--gold-bg` | `#FBF8F1` | 金色浅底：callout背景、金句框底、指标卡底色 |

### 2.3 语义色（仅在表达真实风险时用，不用于装饰）

| Token | 值 | 用途 |
|-------|------|------|
| `--danger-bg` | `#F7F5F5` | 极轻微红底（不是大红色），仅在安全漏洞等真实风险场景用 |
| `--danger-text` | `#8B6B6B` | 暗红文字，不是鲜红色，克制表达风险 |

> ⚠️ **核心规则：不要在同一篇文章里使用绿、红、蓝、黄、橙等多种color token。**
> 区分层级靠的是**明度差异**（#1D1D1F vs #6E6E73 vs #A1A1A6），不是色相差异。
> 金色只在5%的位置出现，其余部分全部是黑白灰色系。

---

## 三、组件变体

### 3.1 Hero卡（深色+金色点缀）

```html
<section style="background:#1D1D1F;border-radius:12px;padding:32px 24px;margin:0 0 20px 0;">
  <p style="margin:0 0 6px 0;font-size:11px;color:#C9A962;letter-spacing:3px;font-weight:bold;">CATEGORY</p>
  <h1 style="margin:0 0 14px 0;font-size:21px;line-height:1.4;color:#FFFFFF;font-weight:bold;">文章标题写在这里</h1>
  <p style="margin:0 0 20px 0;font-size:14px;line-height:1.6;color:#A1A1A6;">副标题或一句话价值承诺</p>
  <section style="display:flex;gap:8px;flex-wrap:wrap;">
    <span style="display:inline-block;padding:4px 12px;background:#C9A962;color:#1D1D1F;font-size:11px;border-radius:4px;font-weight:bold;">5 min</span>
    <span style="display:inline-block;padding:4px 12px;background:transparent;color:#A1A1A6;font-size:11px;border-radius:4px;border:1px solid #3A3A3C;">标签</span>
  </section>
</section>
```

### 3.2 导航卡（边框勾勒，激活态强调）

```html
<section style="margin:0 0 24px 0;display:flex;gap:8px;">
  <section style="flex:1;border-radius:8px;padding:12px;text-align:center;border:1px solid #1D1D1F;">
    <p style="margin:0 0 2px 0;font-size:18px;color:#1D1D1F;font-weight:bold;">01</p>
    <p style="margin:0;font-size:12px;color:#6E6E73;">第一部分</p>
  </section>
  <section style="flex:1;border-radius:8px;padding:12px;text-align:center;border:1px solid #E5E5E5;">
    <p style="margin:0 0 2px 0;font-size:18px;color:#6E6E73;font-weight:bold;">02</p>
    <p style="margin:0;font-size:12px;color:#A1A1A6;">第二部分</p>
  </section>
  <section style="flex:1;border-radius:8px;padding:12px;text-align:center;border:1px solid #E5E5E5;">
    <p style="margin:0 0 2px 0;font-size:18px;color:#6E6E73;font-weight:bold;">03</p>
    <p style="margin:0;font-size:12px;color:#A1A1A6;">第三部分</p>
  </section>
</section>
```

### 3.3 Section Header（暗色圆块+金色编号）

```html
<section style="margin:28px 0 16px 0;display:flex;align-items:center;gap:12px;">
  <section style="flex-shrink:0;width:32px;height:32px;background:#1D1D1F;border-radius:8px;text-align:center;line-height:32px;color:#C9A962;font-size:14px;font-weight:bold;">1</section>
  <h2 style="margin:0;font-size:18px;line-height:1.4;color:#1D1D1F;font-weight:bold;">小节标题</h2>
</section>
```

### 3.4 正文段落

```html
<p style="margin:0 0 16px 0;font-size:15px;line-height:1.8;color:#6E6E73;">正文内容，关键词用 <strong style="color:#1D1D1F;">加粗强调</strong>，极少数可以用 <span style="color:#C9A962;font-weight:bold;">金色强调</span> 但每篇文章不超过3处。</p>
```

### 3.5 终端卡（深色+金色提示符）

```html
<section style="background:#1D1D1F;border-radius:8px;padding:16px;margin:16px 0;overflow-x:auto;">
  <section style="display:flex;gap:6px;margin-bottom:12px;">
    <section style="width:10px;height:10px;border-radius:50%;background:#6E6E73;"></section>
    <section style="width:10px;height:10px;border-radius:50%;background:#A1A1A6;"></section>
    <section style="width:10px;height:10px;border-radius:50%;background:#C9A962;"></section>
  </section>
  <p style="margin:0;font-size:13px;line-height:1.7;color:#A1A1A6;font-family:'SF Mono',SFMono-Regular,Consolas,'Liberation Mono',Menlo,monospace;white-space:pre-wrap;word-break:break-all;"><span style="color:#C9A962;">$</span> command --flag <span style="color:#C9A962;">"argument"</span></p>
</section>
```

### 3.6 Callout（暖米底+金色左边框，统一风格）

```html
<!-- 强调型（default） -->
<section style="background:#FBF8F1;border-radius:8px;padding:16px 18px;margin:16px 0;border-left:3px solid #C9A962;">
  <p style="margin:0 0 4px 0;font-size:13px;color:#1D1D1F;font-weight:bold;">⚡ 关键信息</p>
  <p style="margin:0;font-size:14px;line-height:1.7;color:#6E6E73;">补充说明内容。</p>
</section>

<!-- 信息型（中性） -->
<section style="background:#F7F7F5;border-radius:8px;padding:16px 18px;margin:16px 0;">
  <p style="margin:0 0 4px 0;font-size:13px;color:#6E6E73;font-weight:bold;">💡 参考信息</p>
  <p style="margin:0;font-size:14px;line-height:1.7;color:#6E6E73;">中性背景信息。</p>
</section>

<!-- 深色强调框 -->
<section style="background:#1D1D1F;border-radius:8px;padding:16px 18px;margin:16px 0;">
  <p style="margin:0 0 4px 0;font-size:13px;color:#C9A962;font-weight:bold;">⚠️ 注意事项</p>
  <p style="margin:0;font-size:14px;line-height:1.7;color:#A1A1A6;">重要的警示信息。</p>
</section>
```

### 3.7 金句框（暖米底+金色左边线）

```html
<section style="margin:20px 0;padding:16px 20px;border-left:3px solid #C9A962;background:#FBF8F1;border-radius:0 8px 8px 0;">
  <p style="margin:0;font-size:15px;line-height:1.7;color:#1D1D1F;font-weight:bold;">值得被截图分享的核心金句。</p>
  <p style="margin:8px 0 0 0;font-size:13px;color:#A1A1A6;">—— 出处</p>
</section>
```

### 3.8 SVG指标卡（柔和对比）

```html
<svg viewBox="0 0 680 150" style="width:100%;display:block;" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="10" width="210" height="130" rx="10" fill="#FBF8F1" stroke="#C9A962" stroke-width="1"/>
  <text x="30" y="52" font-size="32" font-weight="bold" fill="#1D1D1F">92%</text>
  <text x="30" y="78" font-size="13" fill="#6E6E73">数据描述1</text>
  <text x="30" y="100" font-size="11" fill="#C9A962">趋势标注</text>
  <rect x="235" y="10" width="210" height="130" rx="10" fill="#F7F7F5"/>
  <text x="255" y="52" font-size="32" font-weight="bold" fill="#1D1D1F">46%</text>
  <text x="255" y="78" font-size="13" fill="#6E6E73">数据描述2</text>
  <text x="255" y="100" font-size="11" fill="#A1A1A6">来源标注</text>
  <rect x="460" y="10" width="210" height="130" rx="10" fill="#F7F7F5"/>
  <text x="480" y="52" font-size="32" font-weight="bold" fill="#1D1D1F">$10B</text>
  <text x="480" y="78" font-size="13" fill="#6E6E73">数据描述3</text>
  <text x="480" y="100" font-size="11" fill="#C9A962">趋势标注</text>
</svg>
```

### 3.9 分隔线（最简化）

```html
<section style="margin:28px 0;text-align:center;">
  <section style="display:inline-block;width:40px;height:1px;background:#E5E5E5;vertical-align:middle;"></section>
  <span style="display:inline-block;margin:0 14px;color:#D0D0D0;font-size:8px;">●</span>
  <section style="display:inline-block;width:40px;height:1px;background:#E5E5E5;vertical-align:middle;"></section>
</section>
```

### 3.10 文末总结块（温和收束）

```html
<section style="margin:28px 0 0 0;padding:20px;background:#F7F7F5;border-radius:8px;border:1px solid #E5E5E5;">
  <p style="margin:0 0 12px 0;font-size:15px;font-weight:bold;color:#1D1D1F;">本篇要点</p>
  <p style="margin:0 0 6px 0;font-size:14px;line-height:1.7;color:#6E6E73;">✓ 要点一</p>
  <p style="margin:0 0 6px 0;font-size:14px;line-height:1.7;color:#6E6E73;">✓ 要点二</p>
  <p style="margin:0;font-size:14px;line-height:1.7;color:#6E6E73;">✓ 要点三</p>
</section>
```

### 3.11 标签Chips

```html
<section style="margin:16px 0;display:flex;flex-wrap:wrap;gap:8px;">
  <span style="display:inline-block;padding:4px 12px;background:#FBF8F1;color:#C9A962;font-size:12px;border-radius:20px;">主标签</span>
  <span style="display:inline-block;padding:4px 12px;background:#F7F7F5;color:#6E6E73;font-size:12px;border-radius:20px;">次标签</span>
  <span style="display:inline-block;padding:4px 12px;background:#F7F7F5;color:#6E6E73;font-size:12px;border-radius:20px;">次标签</span>
</section>
```

---

## 四、排版黄金规则

### 4.1 配色铁律

1. **一个页面只用一个accent色**（默认 #C9A962 暖金）
2. **95%的内容用中性色**：标题用 #1D1D1F，正文用 #6E6E73，注释用 #A1A1A6
3. **金色只在5%的位置出现**：Category标签、Section编号、Hero点缀、终端$符
4. **不要用绿/红/蓝/黄/橙去"丰富"文章**——明度层次足够制造视觉节奏
5. **危险内容（如安全漏洞）用深色块表达，而不是大面积红色**

### 4.2 组件使用节奏

```
[Hero] → 深色+金色，第一屏建立调性
[导航卡] → 3列边框，预告结构
[Section 01] → 暗块+金色编号
  [正文] → 2-3段纯文字
  [SVG指标卡] → 数据展示（最多1个）
  [Callout] → 暖底+金线，核心论点
[Section 02] → 同款暗块
  [正文] → 段落+列表
  [深色Callout] → AI Debt类警示
[Section 03] → 同款暗块
  [SVG对比图] → 双卡对比
[Section 04] → 同款暗块
  [步骤卡片×N] → 暖灰底+金线，一致风格
  [终端卡] → 深色代码块
  [金句框] → 暖底+金线
[分隔线] → 极简·点线
[结尾] → 收束段+深色判断框+总结块+标签
```

### 4.3 常见错误

- ❌ 用绿色标强调、用红色标风险、用蓝色标信息 → 彩虹感
- ❌ 每个Section用不同颜色 → 视觉碎片化
- ❌ 正文用纯黑 (#000) → 刺眼，用 #1D1D1F
- ❌ 过多深色块 → 压抑，深色块每篇最多3个
- ❌ 金色滥用 → 只在5%的位置出现，超过10%就土了
- ✓ 核心心法：**像排版一本书一样排版你的文章——文字本身就是内容，颜色只做最克制的提示**
