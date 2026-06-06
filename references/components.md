# 组件库 + 设计Token + SVG模板

> 融合 wechat-publisher 12基础组件 + md2wechat 布局模块理念 + 3种SVG信息图模板

---

## 一、设计Token

### 1.1 配色系统

**主色调（黑白灰）**

| Token | 值 | 用途 |
|-------|------|------|
| `--c-black` | `#1A1A1A` | 标题、强调文字 |
| `--c-gray-900` | `#2D2D2D` | 深色背景、卡片深色底 |
| `--c-gray-700` | `#4A4A4A` | 正文主色 |
| `--c-gray-500` | `#7A7A7A` | 次要文字、说明文字 |
| `--c-gray-300` | `#B0B0B0` | 分隔线、边框 |
| `--c-gray-100` | `#F2F2F2` | 浅色背景、代码块底 |
| `--c-white` | `#FFFFFF` | 卡片白底、文章背景 |

**强调色（按风格预设切换）**

| Token | 默认值 | 用途 |
|-------|--------|------|
| `--c-accent` | `#059669` | 主强调色，标题装饰、按钮 |
| `--c-accent-light` | `#10B981` | 浅强调色，标签、次要装饰 |
| `--c-accent-bg` | `#ECFDF5` | 强调色浅底，callout背景 |
| `--c-highlight` | `#FDE68A` | 高光色，金句框、重点标记 |

**语义色**

| Token | 值 | 用途 |
|-------|------|------|
| `--c-danger` | `#EF4444` | 警示、风险标注 |
| `--c-warning` | `#F59E0B` | 注意、提示 |
| `--c-info` | `#3B82F6` | 信息补充 |

### 1.2 字阶

| Token | 大小 | 行高 | 用途 |
|-------|------|------|------|
| `--f-h1` | 22px | 1.4 | 文章大标题 |
| `--f-h2` | 18px | 1.5 | 小节标题 |
| `--f-h3` | 16px | 1.5 | 子标题 |
| `--f-body` | 15px | 1.8 | 正文 |
| `--f-small` | 13px | 1.6 | 说明文字、caption |
| `--f-tiny` | 12px | 1.5 | 标签、脚注 |

### 1.3 间距

| Token | 值 | 用途 |
|-------|------|------|
| `--sp-xs` | 4px | 图标与文字间距 |
| `--sp-sm` | 8px | 元素内间距 |
| `--sp-md` | 16px | 段落间距 |
| `--sp-lg` | 24px | 区块间距 |
| `--sp-xl` | 32px | 大区块间距 |
| `--sp-2xl` | 48px | 文章最大留白 |

### 1.4 圆角与阴影

| Token | 值 | 用途 |
|-------|------|------|
| `--r-sm` | 4px | 小元素圆角 |
| `--r-md` | 8px | 卡片圆角 |
| `--r-lg` | 12px | 大卡片圆角 |
| `--shadow-card` | `0 2px 12px rgba(0,0,0,0.08)` | 卡片投影 |

---

## 二、12个基础组件

### 组件1：文章容器 (Article Container)

包裹整篇文章的最外层容器，设定最大宽度和基础排版。

```html
<section style="max-width:100%;box-sizing:border-box;padding:0;margin:0 auto;color:#4A4A4A;font-size:15px;line-height:1.8;font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue','PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;">
  <!-- 文章内容放这里 -->
</section>
```

### 组件2：封面卡 (Cover Card - 深色)

文章开头的深色背景卡片，展示标题、作者、日期。

```html
<section style="background:#2D2D2D;border-radius:12px;padding:32px 24px;margin:0 0 24px 0;">
  <p style="margin:0 0 8px 0;font-size:12px;color:#10B981;letter-spacing:2px;">CATEGORY</p>
  <h1 style="margin:0 0 16px 0;font-size:22px;line-height:1.4;color:#FFFFFF;font-weight:bold;">文章标题写在这里</h1>
  <p style="margin:0;font-size:13px;color:#B0B0B0;">作者名 · 2026年6月6日</p>
</section>
```

### 组件3：编号小标题 (Numbered Heading)

带编号和装饰线的小节标题。

```html
<section style="margin:32px 0 16px 0;">
  <p style="margin:0 0 4px 0;font-size:12px;color:#059669;font-weight:bold;letter-spacing:1px;">01</p>
  <h2 style="margin:0;font-size:18px;line-height:1.5;color:#1A1A1A;font-weight:bold;">小节标题</h2>
  <section style="margin-top:8px;width:40px;height:3px;background:#059669;border-radius:2px;"></section>
</section>
```

### 组件4：正文段落 (Body Paragraph)

标准正文段落，含首行缩进和段间距。

```html>
<p style="margin:0 0 16px 0;font-size:15px;line-height:1.8;color:#4A4A4A;text-align:justify;">这里是正文内容，每段之间用16px间距分隔。支持<strong style="color:#1A1A1A;">加粗强调</strong>和<span style="color:#059669;font-weight:bold;">彩色强调</span>。</p>
```

### 组件5：分隔线 (Divider)

带装饰的分隔线。

```html
<section style="margin:24px 0;text-align:center;">
  <section style="display:inline-block;width:60px;height:1px;background:#B0B0B0;vertical-align:middle;"></section>
  <span style="display:inline-block;margin:0 12px;color:#B0B0B0;font-size:12px;">◆</span>
  <section style="display:inline-block;width:60px;height:1px;background:#B0B0B0;vertical-align:middle;"></section>
</section>
```

### 组件6：Callout 浅灰信号框 (Light Callout)

浅灰色背景的提示框，用于补充说明、引用数据。

```html
<section style="background:#F2F2F2;border-radius:8px;padding:16px;margin:16px 0;">
  <p style="margin:0 0 4px 0;font-size:13px;color:#7A7A7A;font-weight:bold;">💡 提示</p>
  <p style="margin:0;font-size:14px;line-height:1.7;color:#4A4A4A;">这里是补充说明的内容，适合放数据引用、背景知识或注意事项。</p>
</section>
```

### 组件7：Callout 深色强调框 (Dark Callout)

深色背景的强提示框，用于核心观点、重要声明。

```html
<section style="background:#2D2D2D;border-radius:8px;padding:20px;margin:16px 0;">
  <p style="margin:0 0 4px 0;font-size:13px;color:#10B981;font-weight:bold;">⚡ 核心观点</p>
  <p style="margin:0;font-size:14px;line-height:1.7;color:#FFFFFF;">这里是必须被读者记住的核心信息，深色背景制造视觉停顿。</p>
</section>
```

### 组件8：金句框 (Quote Block)

带左侧色条的高亮引用框，适合名言、关键结论。

```html
<section style="margin:24px 0;padding:16px 20px;border-left:4px solid #059669;background:#ECFDF5;border-radius:0 8px 8px 0;">
  <p style="margin:0;font-size:16px;line-height:1.6;color:#1A1A1A;font-weight:bold;">"这里是一句值得被记住的金句，读者会截图分享的那种。"</p>
  <p style="margin:8px 0 0 0;font-size:13px;color:#7A7A7A;">—— 出出处</p>
</section>
```

### 组件9：步骤卡片 (Step Card)

带编号的步骤卡片，用于教程、流程说明。

```html
<section style="margin:16px 0;">
  <section style="display:flex;align-items:flex-start;">
    <section style="flex-shrink:0;width:28px;height:28px;background:#059669;border-radius:50%;text-align:center;line-height:28px;color:#FFFFFF;font-size:14px;font-weight:bold;">1</section>
    <section style="margin-left:12px;flex:1;">
      <p style="margin:0 0 4px 0;font-size:15px;font-weight:bold;color:#1A1A1A;">步骤标题</p>
      <p style="margin:0;font-size:14px;line-height:1.6;color:#4A4A4A;">步骤的详细描述，说明这一步要做什么。</p>
    </section>
  </section>
</section>
```

### 组件10：配图+Caption (Image with Caption)

图片容器带居中对齐和底部说明文字。

```html
<section style="margin:20px 0;text-align:center;">
  <img src="IMAGE_URL" style="width:100%;border-radius:8px;display:block;" />
  <p style="margin:8px 0 0 0;font-size:12px;color:#7A7A7A;text-align:center;">图片说明文字 / 来源标注</p>
</section>
```

### 组件11：文末总结块 (Summary Block)

文章结尾的总结区块，带视觉收束。

```html
<section style="margin:32px 0 0 0;padding:20px;background:#F2F2F2;border-radius:8px;">
  <p style="margin:0 0 12px 0;font-size:15px;font-weight:bold;color:#1A1A1A;">📌 核心要点</p>
  <p style="margin:0 0 8px 0;font-size:14px;line-height:1.7;color:#4A4A4A;">1. 要点一</p>
  <p style="margin:0 0 8px 0;font-size:14px;line-height:1.7;color:#4A4A4A;">2. 要点二</p>
  <p style="margin:0;font-size:14px;line-height:1.7;color:#4A4A4A;">3. 要点三</p>
</section>
```

### 组件12：标签Chips (Tag Chips)

文末标签或分类标签。

```html
<section style="margin:16px 0;display:flex;flex-wrap:wrap;gap:8px;">
  <span style="display:inline-block;padding:4px 12px;background:#ECFDF5;color:#059669;font-size:12px;border-radius:20px;">标签一</span>
  <span style="display:inline-block;padding:4px 12px;background:#F2F2F2;color:#4A4A4A;font-size:12px;border-radius:20px;">标签二</span>
  <span style="display:inline-block;padding:4px 12px;background:#F2F2F2;color:#4A4A4A;font-size:12px;border-radius:20px;">标签三</span>
</section>
```

---

## 三、3个SVG信息图模板

### 模板A：双卡对比 (Compare Cards)

适合：A/B对比、优劣势分析、新旧方案对比。

```html
<section style="margin:20px 0;">
  <svg viewBox="0 0 680 260" style="width:100%;display:block;" xmlns="http://www.w3.org/2000/svg">
    <!-- 左卡 -->
    <rect x="10" y="10" width="320" height="240" rx="12" fill="#F2F2F2"/>
    <text x="30" y="50" font-size="14" font-weight="bold" fill="#059669">方案 A</text>
    <text x="30" y="80" font-size="18" font-weight="bold" fill="#1A1A1A">标题一</text>
    <text x="30" y="110" font-size="13" fill="#4A4A4A">描述文字第一行</text>
    <text x="30" y="132" font-size="13" fill="#4A4A4A">描述文字第二行</text>
    <text x="30" y="170" font-size="28" font-weight="bold" fill="#1A1A1A">85%</text>
    <text x="30" y="192" font-size="12" fill="#7A7A7A">关键指标</text>
    <!-- VS -->
    <text x="340" y="140" text-anchor="middle" font-size="16" font-weight="bold" fill="#B0B0B0">VS</text>
    <!-- 右卡 -->
    <rect x="350" y="10" width="320" height="240" rx="12" fill="#2D2D2D"/>
    <text x="370" y="50" font-size="14" font-weight="bold" fill="#10B981">方案 B</text>
    <text x="370" y="80" font-size="18" font-weight="bold" fill="#FFFFFF">标题二</text>
    <text x="370" y="110" font-size="13" fill="#B0B0B0">描述文字第一行</text>
    <text x="370" y="132" font-size="13" fill="#B0B0B0">描述文字第二行</text>
    <text x="370" y="170" font-size="28" font-weight="bold" fill="#FFFFFF">92%</text>
    <text x="370" y="192" font-size="12" fill="#7A7A7A">关键指标</text>
  </svg>
</section>
```

### 模板B：时间线/演变路径 (Timeline)

适合：发展历程、版本迭代、决策路径。

```html
<section style="margin:20px 0;">
  <svg viewBox="0 0 680 200" style="width:100%;display:block;" xmlns="http://www.w3.org/2000/svg">
    <!-- 主轴线 -->
    <line x1="40" y1="100" x2="640" y2="100" stroke="#B0B0B0" stroke-width="2"/>
    <!-- 节点1 -->
    <circle cx="120" cy="100" r="12" fill="#059669"/>
    <text x="120" y="104" text-anchor="middle" font-size="10" font-weight="bold" fill="#FFFFFF">1</text>
    <text x="120" y="78" text-anchor="middle" font-size="12" font-weight="bold" fill="#1A1A1A">阶段一</text>
    <text x="120" y="135" text-anchor="middle" font-size="11" fill="#7A7A7A">2024.Q1</text>
    <!-- 节点2 -->
    <circle cx="300" cy="100" r="12" fill="#059669"/>
    <text x="300" y="104" text-anchor="middle" font-size="10" font-weight="bold" fill="#FFFFFF">2</text>
    <text x="300" y="78" text-anchor="middle" font-size="12" font-weight="bold" fill="#1A1A1A">阶段二</text>
    <text x="300" y="135" text-anchor="middle" font-size="11" fill="#7A7A7A">2024.Q3</text>
    <!-- 节点3 -->
    <circle cx="480" cy="100" r="12" fill="#059669"/>
    <text x="480" y="104" text-anchor="middle" font-size="10" font-weight="bold" fill="#FFFFFF">3</text>
    <text x="480" y="78" text-anchor="middle" font-size="12" font-weight="bold" fill="#1A1A1A">阶段三</text>
    <text x="480" y="135" text-anchor="middle" font-size="11" fill="#7A7A7A">2025.Q1</text>
    <!-- 当前节点（高亮） -->
    <circle cx="600" cy="100" r="14" fill="#10B981" stroke="#ECFDF5" stroke-width="3"/>
    <text x="600" y="104" text-anchor="middle" font-size="10" font-weight="bold" fill="#FFFFFF">4</text>
    <text x="600" y="78" text-anchor="middle" font-size="12" font-weight="bold" fill="#059669">现在</text>
    <text x="600" y="135" text-anchor="middle" font-size="11" fill="#059669">2026.Q2</text>
  </svg>
</section>
```

### 模板C：飞轮/闭环 (Flywheel)

适合：增长飞轮、正反馈循环、商业模式闭环。

```html
<section style="margin:20px 0;">
  <svg viewBox="0 0 680 340" style="width:100%;display:block;" xmlns="http://www.w3.org/2000/svg">
    <!-- 中心圆 -->
    <circle cx="340" cy="170" r="60" fill="#ECFDF5" stroke="#059669" stroke-width="2"/>
    <text x="340" y="165" text-anchor="middle" font-size="14" font-weight="bold" fill="#059669">核心</text>
    <text x="340" y="183" text-anchor="middle" font-size="12" fill="#4A4A4A">驱动力</text>
    <!-- 节点1 - 顶部 -->
    <rect x="280" y="20" width="120" height="50" rx="8" fill="#2D2D2D"/>
    <text x="340" y="50" text-anchor="middle" font-size="13" font-weight="bold" fill="#FFFFFF">环节一</text>
    <!-- 节点2 - 右侧 -->
    <rect x="510" y="140" width="120" height="50" rx="8" fill="#2D2D2D"/>
    <text x="570" y="170" text-anchor="middle" font-size="13" font-weight="bold" fill="#FFFFFF">环节二</text>
    <!-- 节点3 - 底部 -->
    <rect x="280" y="260" width="120" height="50" rx="8" fill="#2D2D2D"/>
    <text x="340" y="290" text-anchor="middle" font-size="13" font-weight="bold" fill="#FFFFFF">环节三</text>
    <!-- 节点4 - 左侧 -->
    <rect x="50" y="140" width="120" height="50" rx="8" fill="#2D2D2D"/>
    <text x="110" y="170" text-anchor="middle" font-size="13" font-weight="bold" fill="#FFFFFF">环节四</text>
    <!-- 箭头：1→2 -->
    <path d="M400,45 Q470,45 510,140" fill="none" stroke="#059669" stroke-width="2" marker-end="url(#arrowhead)"/>
    <!-- 箭头：2→3 -->
    <path d="M570,190 Q570,260 400,275" fill="none" stroke="#059669" stroke-width="2" marker-end="url(#arrowhead)"/>
    <!-- 箭头：3→4 -->
    <path d="M280,285 Q210,285 170,190" fill="none" stroke="#059669" stroke-width="2" marker-end="url(#arrowhead)"/>
    <!-- 箭头：4→1 -->
    <path d="M110,140 Q110,45 280,45" fill="none" stroke="#059669" stroke-width="2" marker-end="url(#arrowhead)"/>
    <!-- 箭头定义 -->
    <defs>
      <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
        <polygon points="0 0, 8 3, 0 6" fill="#059669"/>
      </marker>
    </defs>
  </svg>
</section>
```

---

## 四、md2wechat 布局模块简化说明

md2wechat 将文章拆解为6大类布局模块，每类3-5个，用 `:::module-name` 语法在Markdown中声明。

### 4.1 模块分类概览

| 类别 | 英文 | 用途 | 模块数 |
|------|------|------|--------|
| 开场 | opening | 第一屏、破冰、建立期待 | 5 |
| 证据 | evidence | 引用、图说、对比、标注 | 5 |
| 信息图 | infographic | 数据、对比、步骤、时间线 | 5 |
| 判断 | judgment | 结论、适合人群、辟谣、宣言 | 5 |
| 转化 | conversion | CTA、FAQ、清单、总结 | 5 |
| 品牌 | brand | 作者卡、系列、订阅 | 5 |

### 4.2 各类模块列表

**Opening（开场）**
- `hero` — 全幅大标题+副标题，首屏建立气势
- `toc` — 目录卡，预告文章结构
- `cards` — 3列卡片，展示核心论点
- `part` — 分部标记，长文分辑
- `label-title` — 标签+标题组合，分类感强

**Evidence（证据）**
- `quote` — 引用块，名人/数据引用
- `image-text` — 图文混排，左图右文
- `image-steps` — 图解步骤，配图+说明
- `image-compare` — 图像对比，前后/左右
- `image-annotate` — 图像标注，截图+红框说明

**Infographic（信息图）**
- `metrics` — 数据指标卡，大数字+说明
- `compare` — 双卡对比，A vs B
- `steps` — 步骤流程，编号卡
- `timeline` — 时间线，演变历程
- `infographic` — 综合信息图，自定义SVG

**Judgment（判断）**
- `verdict` — 结论框，最终判定
- `audience-fit` — 适合人群，红绿灯标注
- `myth-fact` — 辟谣/正误对比
- `manifesto` — 宣言，立场声明
- `bridge` — 过渡桥段，连接上下文

**Conversion（转化）**
- `cta` — 行动号召，按钮+链接
- `faq` — 常见问题，折叠式Q&A
- `checklist` — 清单，打勾项
- `notice` — 公告/更新通知
- `summary` — 文末总结，要点回顾

**Brand（品牌）**
- `author-card` — 作者卡片，头像+简介
- `people` — 团队/人物介绍
- `series` — 系列文章导航
- `subscribe` — 订阅引导

### 4.3 :::module 语法说明

从 md2wechat 移植的语法，在Markdown中用围栏式语法声明模块：

```markdown
:::hero
# 文章标题
副标题或描述文字
:::

:::toc
- 第一部分：概念解析
- 第二部分：实操步骤
- 第三部分：总结建议
:::

:::compare
## 方案A
- 优点1
- 优点2
---
## 方案B
- 优点1
- 优点2
:::

:::verdict
最终结论：推荐方案B
:::
```

**语法规则：**
1. `:::module-name` 必须独占一行，开头三个冒号
2. 模块名必须是已注册的模块名（见上方列表）
3. 模块内容支持标准Markdown格式
4. `---` 在模块内用作分隔符（如compare的左右分栏）
5. `:::` 结束标记必须独占一行
6. 模块可以嵌套（最多2层）

**编译时行为：**
- `:::module-name` 会被编译为对应的HTML组件
- 模块内的Markdown会正常解析
- 未识别的模块名会被当作普通div处理
- 缺少结束 `:::` 会报错

---

## 五、写作建议

### 5.1 组件使用节奏

一篇文章不要使用超过5种组件类型。推荐组合：

| 文章类型 | 推荐组件组合 |
|----------|-------------|
| 技术教程 | 封面卡 + 编号小标题 + 步骤卡片 + Callout浅灰 + 文末总结 |
| 行业分析 | 封面卡 + 编号小标题 + 金句框 + SVG对比图 + 标签Chips |
| 产品发布 | 封面卡 + Callout深色 + SVG时间线 + 配图+Caption + 文末总结 |
| 深度思考 | 封面卡 + 正文段落 + 金句框 + 分隔线 + 文末总结 |
| 新闻快讯 | 封面卡 + Callout深色 + SVG对比图 + 标签Chips |

### 5.2 视觉节奏法则

1. **开头30%**：用封面卡+编号标题建立结构感
2. **中间50%**：每2-3段正文穿插一个视觉组件（callout/金句/配图），避免纯文字墙
3. **结尾20%**：用文末总结块+标签chips收束，制造完成感
4. **分隔线**用于大段落切换，不要每段都用
5. **SVG信息图**一篇文章最多1个，放在核心论点处

### 5.3 常见错误

- 全篇只用正文段落 → 读者无法扫读
- 每段都用callout → 视觉噪音太大，失去强调作用
- 深色组件超过3个 → 压抑感过重
- SVG信息图文字太多 → 手机上无法阅读
- 标签chips放在文章中间 → 应该放在文末
