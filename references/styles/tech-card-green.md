# 绿色技术卡片风 (tech-card-green)

> 视觉定位：技术教程 / SaaS文档 / AI工具介绍
> 适合读者：开发者、产品经理、技术决策者

---

## 一、视觉定位

| 维度 | 描述 |
|------|------|
| 语气 | 专业、清晰、可信赖 |
| 节奏 | 快节奏，信息密度高，可扫读 |
| 配色 | 绿色科技感 + 黑白灰骨架 + 黄色高光 |
| 字体 | 系统无衬线，偏几何感 |
| 留白 | 紧凑但不拥挤，代码块需额外留白 |

---

## 二、Color Token

### 2.1 主色调

| Token | 值 | 用途 |
|-------|------|------|
| `--c-black` | `#0F172A` | 标题、代码关键词 |
| `--c-gray-900` | `#1E293B` | 深色背景、终端底 |
| `--c-gray-700` | `#475569` | 正文主色 |
| `--c-gray-500` | `#94A3B8` | 次要文字、注释 |
| `--c-gray-300` | `#CBD5E1` | 分隔线、边框 |
| `--c-gray-100` | `#F1F5F9` | 浅底背景 |
| `--c-white` | `#FFFFFF` | 卡片白底 |

### 2.2 强调色

| Token | 值 | 用途 |
|-------|------|------|
| `--c-accent` | `#059669` | 主强调：标题装饰、按钮、标签 |
| `--c-accent-light` | `#10B981` | 浅强调：代码高亮、次要装饰 |
| `--c-accent-bg` | `#ECFDF5` | 浅底：callout背景、选中态 |
| `--c-highlight` | `#FDE68A` | 高光：重要数据、金句底色 |
| `--c-highlight-text` | `#92400E` | 高光上文字色 |

### 2.3 语义色

| Token | 值 | 用途 |
|-------|------|------|
| `--c-danger` | `#EF4444` | 报错、危险操作 |
| `--c-warning` | `#F59E0B` | 注意、弃用警告 |
| `--c-info` | `#3B82F6` | 信息补充、链接 |

---

## 三、组件变体

### 3.1 Hero承诺卡

文章开头的深色卡片，承诺读者读完能获得什么。

```html
<section style="background:linear-gradient(135deg,#0F172A 0%,#1E293B 100%);border-radius:12px;padding:32px 24px;margin:0 0 24px 0;">
  <p style="margin:0 0 6px 0;font-size:12px;color:#10B981;letter-spacing:2px;font-weight:bold;">🔧 TUTORIAL</p>
  <h1 style="margin:0 0 12px 0;font-size:22px;line-height:1.4;color:#FFFFFF;font-weight:bold;">用 LangChain 搭建 RAG 应用</h1>
  <p style="margin:0 0 16px 0;font-size:14px;line-height:1.6;color:#94A3B8;">从零到一，手把手教你实现文档问答系统</p>
  <section style="display:flex;gap:8px;flex-wrap:wrap;">
    <span style="display:inline-block;padding:4px 10px;background:#10B981;color:#FFFFFF;font-size:11px;border-radius:4px;font-weight:bold;">⏱ 30分钟</span>
    <span style="display:inline-block;padding:4px 10px;background:#1E293B;color:#94A3B8;font-size:11px;border-radius:4px;border:1px solid #334155;">中级难度</span>
    <span style="display:inline-block;padding:4px 10px;background:#1E293B;color:#94A3B8;font-size:11px;border-radius:4px;border:1px solid #334155;">Python</span>
  </section>
</section>
```

**注意**：由于微信不支持 `linear-gradient`，实际输出时改为纯色 `background:#0F172A`。此处展示设计意图。

### 3.2 横向导航卡

文章结构导航，3-4个卡片横向排列。

```html
<section style="margin:0 0 24px 0;display:flex;gap:8px;">
  <section style="flex:1;background:#ECFDF5;border-radius:8px;padding:12px;text-align:center;">
    <p style="margin:0 0 2px 0;font-size:18px;color:#059669;font-weight:bold;">01</p>
    <p style="margin:0;font-size:12px;color:#475569;">环境配置</p>
  </section>
  <section style="flex:1;background:#F1F5F9;border-radius:8px;padding:12px;text-align:center;">
    <p style="margin:0 0 2px 0;font-size:18px;color:#475569;font-weight:bold;">02</p>
    <p style="margin:0;font-size:12px;color:#475569;">核心逻辑</p>
  </section>
  <section style="flex:1;background:#F1F5F9;border-radius:8px;padding:12px;text-align:center;">
    <p style="margin:0 0 2px 0;font-size:18px;color:#475569;font-weight:bold;">03</p>
    <p style="margin:0;font-size:12px;color:#475569;">部署上线</p>
  </section>
</section>
```

### 3.3 Section Header

带编号和绿色装饰线的小节标题。

```html
<section style="margin:28px 0 16px 0;display:flex;align-items:center;gap:12px;">
  <section style="flex-shrink:0;width:32px;height:32px;background:#059669;border-radius:8px;text-align:center;line-height:32px;color:#FFFFFF;font-size:14px;font-weight:bold;">1</section>
  <h2 style="margin:0;font-size:18px;line-height:1.4;color:#0F172A;font-weight:bold;">环境配置与依赖安装</h2>
</section>
```

### 3.4 正文段落

标准正文，代码关键词用绿色高亮。

```html
<p style="margin:0 0 16px 0;font-size:15px;line-height:1.8;color:#475569;">首先安装 <strong style="color:#059669;">langchain</strong> 核心包和 <strong style="color:#059669;">chromadb</strong> 向量数据库。确保你的 Python 版本 ≥ 3.9，推荐使用虚拟环境隔离依赖。</p>
```

### 3.5 终端卡

代码块/终端展示，深色背景 + 等宽字体。

```html
<section style="background:#0F172A;border-radius:8px;padding:16px;margin:16px 0;overflow-x:auto;">
  <section style="display:flex;gap:6px;margin-bottom:12px;">
    <section style="width:10px;height:10px;border-radius:50%;background:#EF4444;"></section>
    <section style="width:10px;height:10px;border-radius:50%;background:#F59E0B;"></section>
    <section style="width:10px;height:10px;border-radius:50%;background:#10B981;"></section>
  </section>
  <p style="margin:0;font-size:13px;line-height:1.7;color:#94A3B8;font-family:'SF Mono',SFMono-Regular,Consolas,'Liberation Mono',Menlo,monospace;white-space:pre-wrap;word-break:break-all;"><span style="color:#10B981;">$</span> pip install langchain chromadb openai<br/><br/><span style="color:#94A3B8;">Successfully installed langchain-0.1.0</span><br/><span style="color:#94A3B8;">Successfully installed chromadb-0.4.0</span></p>
</section>
```

### 3.6 Callout

技术向提示框，分信息/警告/提示三种。

```html
<!-- 信息型 -->
<section style="background:#ECFDF5;border-radius:8px;padding:14px 16px;margin:16px 0;border-left:3px solid #059669;">
  <p style="margin:0 0 4px 0;font-size:13px;color:#059669;font-weight:bold;">💡 Pro Tip</p>
  <p style="margin:0;font-size:14px;line-height:1.6;color:#475569;">使用 chunk_overlap 参数可以控制文档分块的重叠度，推荐设置为 chunk_size 的 10%。</p>
</section>

<!-- 警告型 -->
<section style="background:#FEF3C7;border-radius:8px;padding:14px 16px;margin:16px 0;border-left:3px solid #F59E0B;">
  <p style="margin:0 0 4px 0;font-size:13px;color:#92400E;font-weight:bold;">⚠️ 注意</p>
  <p style="margin:0;font-size:14px;line-height:1.6;color:#475569;">OpenAI API Key 不要硬编码在代码中，务必使用环境变量管理。</p>
</section>

<!-- 危险型 -->
<section style="background:#FEF2F2;border-radius:8px;padding:14px 16px;margin:16px 0;border-left:3px solid #EF4444;">
  <p style="margin:0 0 4px 0;font-size:13px;color:#EF4444;font-weight:bold;">🚫 危险</p>
  <p style="margin:0;font-size:14px;line-height:1.6;color:#475569;">切勿将 API Key 提交到 Git 仓库，即使私有仓库也不行。</p>
</section>
```

### 3.7 图片相框

带边框和说明的图片展示。

```html
<section style="margin:20px 0;border:1px solid #CBD5E1;border-radius:8px;overflow:hidden;">
  <img src="IMAGE_URL" style="width:100%;display:block;" />
  <section style="padding:10px 14px;background:#F1F5F9;">
    <p style="margin:0;font-size:12px;color:#475569;">图：RAG 架构流程图 — 查询 → 检索 → 生成</p>
  </section>
</section>
```

### 3.8 SVG信息图 - 指标卡

大数字+说明的指标展示。

```html
<section style="margin:20px 0;">
  <svg viewBox="0 0 680 160" style="width:100%;display:block;" xmlns="http://www.w3.org/2000/svg">
    <!-- 卡片1 -->
    <rect x="10" y="10" width="210" height="140" rx="10" fill="#ECFDF5"/>
    <text x="30" y="60" font-size="32" font-weight="bold" fill="#059669">3.2s</text>
    <text x="30" y="85" font-size="13" fill="#475569">平均响应时间</text>
    <text x="30" y="110" font-size="11" fill="#10B981">↓ 比上版快 40%</text>
    <!-- 卡片2 -->
    <rect x="235" y="10" width="210" height="140" rx="10" fill="#F1F5F9"/>
    <text x="255" y="60" font-size="32" font-weight="bold" fill="#0F172A">97%</text>
    <text x="255" y="85" font-size="13" fill="#475569">检索准确率</text>
    <text x="255" y="110" font-size="11" fill="#10B981">↑ 提升 12 个百分点</text>
    <!-- 卡片3 -->
    <rect x="460" y="10" width="210" height="140" rx="10" fill="#F1F5F9"/>
    <text x="480" y="60" font-size="32" font-weight="bold" fill="#0F172A">5K</text>
    <text x="480" y="85" font-size="13" fill="#475569">日活用户</text>
    <text x="480" y="110" font-size="11" fill="#10B981">↑ 月增长 200%</text>
  </svg>
</section>
```

### 3.9 文末总结块

带勾选标记的要点总结。

```html
<section style="margin:28px 0 0 0;padding:20px;background:#F1F5F9;border-radius:8px;border:1px solid #CBD5E1;">
  <p style="margin:0 0 12px 0;font-size:15px;font-weight:bold;color:#0F172A;">✅ 本篇要点</p>
  <p style="margin:0 0 6px 0;font-size:14px;line-height:1.7;color:#475569;">✓ LangChain + ChromaDB 搭建 RAG 核心流程</p>
  <p style="margin:0 0 6px 0;font-size:14px;line-height:1.7;color:#475569;">✓ 文档分块策略与重叠参数调优</p>
  <p style="margin:0;font-size:14px;line-height:1.7;color:#475569;">✓ API Key 安全管理的最佳实践</p>
</section>
```

---

## 四、排版建议

### 4.1 文章结构模板

```
[Hero承诺卡] → 读完能获得什么
[横向导航卡] → 文章结构
[Section Header 01] → 环境配置
  [终端卡] → 安装命令
  [Callout信息] → Pro Tip
[Section Header 02] → 核心逻辑
  [正文段落] → 代码说明
  [终端卡] → 核心代码
  [Callout警告] → 注意事项
[Section Header 03] → 部署上线
  [图片相框] → 架构图
  [正文段落] → 部署步骤
[文末总结块] → 要点回顾
[标签Chips] → 技术标签
```

### 4.2 节奏控制

- 每300-400字穿插一个视觉组件
- 代码块前必有一段文字说明上下文
- 超过15行的代码考虑拆分为多个终端卡
- SVG信息图最多1个，放在核心数据展示处

### 4.3 技术写作规则

1. **代码可复制**：终端卡内的代码必须可直接运行
2. **版本明确**：依赖包必须标注版本号
3. **环境说明**：Python版本、OS、依赖在前文说明
4. **错误处理**：关键步骤必须有Callout说明常见报错
5. **渐进复杂度**：从最简示例开始，逐步添加功能
