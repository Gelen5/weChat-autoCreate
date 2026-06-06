# AI新闻信号卡风 (ai-news-signal-green)

> 视觉定位：AI新闻 / 产品更新 / 分析师简报
> 适合读者：关注AI动态的从业者、投资人、产品经理

---

## 一、视觉定位

| 维度 | 描述 |
|------|------|
| 语气 | 紧迫、信号感、权威 |
| 节奏 | 快节奏，信息密度极高，第一屏就要给结论 |
| 配色 | 深色新闻底 + 绿色信号 + 白色数据 + 黄色警示 |
| 字体 | 系统无衬线，数字用等宽 |
| 留白 | 紧凑，像Bloomberg终端的信息密度 |

---

## 二、Color Token

### 2.1 主色调

| Token | 值 | 用途 |
|-------|------|------|
| `--c-black` | `#0A0A0A` | 深色背景、终极强调 |
| `--c-gray-900` | `#1A1A1A` | Hero底色、深色卡片 |
| `--c-gray-700` | `#3A3A3A` | 深色次要背景 |
| `--c-gray-500` | `#8A8A8A` | 次要文字、时间戳 |
| `--c-gray-300` | `#CCCCCC` | 浅色边框、分隔线 |
| `--c-gray-100` | `#F5F5F5` | 浅底背景 |
| `--c-white` | `#FFFFFF` | 深底上的文字、数据 |

### 2.2 强调色

| Token | 值 | 用途 |
|-------|------|------|
| `--c-accent` | `#059669` | 信号色：看涨、利好、增长 |
| `--c-accent-light` | `#34D399` | 浅信号：次要利好的标记 |
| `--c-accent-bg` | `#052E16` | 深绿底：信号卡背景 |
| `--c-signal-red` | `#EF4444` | 红色信号：看跌、风险、警告 |
| `--c-signal-red-bg` | `#450A0A` | 深红底 |
| `--c-highlight` | `#FDE68A` | 高光：核心数据、突发标记 |
| `--c-highlight-text` | `#78350F` | 高光上文字 |

### 2.3 语义色

| Token | 值 | 用途 |
|-------|------|------|
| `--c-verified` | `#3B82F6` | 已验证信息、官方来源 |
| `--c-rumor` | `#F59E0B` | 传闻、未经证实 |
| `--c-urgent` | `#EF4444` | 紧急、突发 |

---

## 三、独特组件

### 3.1 Dark News Hero

深色新闻头，紧迫感+核心信号。

```html
<section style="background:#0A0A0A;border-radius:12px;padding:28px 24px;margin:0 0 20px 0;">
  <section style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
    <section style="width:8px;height:8px;border-radius:50%;background:#EF4444;"></section>
    <span style="font-size:12px;color:#EF4444;font-weight:bold;letter-spacing:1px;">BREAKING</span>
    <span style="font-size:12px;color:#8A8A8A;">· 2小时前</span>
  </section>
  <h1 style="margin:0 0 12px 0;font-size:20px;line-height:1.4;color:#FFFFFF;font-weight:bold;">OpenAI 发布 GPT-5：多模态推理能力飞跃</h1>
  <p style="margin:0 0 16px 0;font-size:14px;line-height:1.6;color:#8A8A8A;">旗舰模型在数学推理和代码生成上超越人类专家水平</p>
  <section style="display:flex;gap:8px;flex-wrap:wrap;">
    <span style="display:inline-block;padding:4px 10px;background:#052E16;color:#34D399;font-size:11px;border-radius:4px;font-weight:bold;">↑ 利好 AI基础设施</span>
    <span style="display:inline-block;padding:4px 10px;background:#052E16;color:#34D399;font-size:11px;border-radius:4px;font-weight:bold;">↑ 利好 AI应用层</span>
    <span style="display:inline-block;padding:4px 10px;background:#450A0A;color:#FCA5A5;font-size:11px;border-radius:4px;font-weight:bold;">↓ 利空 传统SaaS</span>
  </section>
</section>
```

### 3.2 Real Image Frame

真图展示框，强调"这是真图不是AI生成"。

```html
<section style="margin:16px 0;border:2px solid #059669;border-radius:8px;overflow:hidden;">
  <section style="background:#059669;padding:6px 12px;display:flex;align-items:center;gap:6px;">
    <section style="width:6px;height:6px;border-radius:50%;background:#FFFFFF;"></section>
    <span style="font-size:11px;color:#FFFFFF;font-weight:bold;">真实截图 · 非AI生成</span>
  </section>
  <img src="IMAGE_URL" style="width:100%;display:block;" />
  <section style="padding:8px 12px;background:#F5F5F5;">
    <p style="margin:0;font-size:12px;color:#3A3A3A;">来源：OpenAI 官方博客 · 2026.06.06</p>
  </section>
</section>
```

### 3.3 Conclusion Callout

结论框，一句话给出判断。

```html
<section style="margin:20px 0;padding:16px 20px;border-left:4px solid #059669;background:#F5F5F5;">
  <p style="margin:0 0 4px 0;font-size:12px;color:#059669;font-weight:bold;letter-spacing:1px;">OUR TAKE</p>
  <p style="margin:0;font-size:15px;line-height:1.6;color:#0A0A0A;font-weight:bold;">GPT-5 将在6个月内重塑企业AI应用格局，基础设施厂商先受益。</p>
</section>
```

### 3.4 Three Signal Cards

三信号卡，红/绿/黄三个维度判断。

```html
<section style="margin:20px 0;display:flex;gap:8px;">
  <!-- 绿色信号 -->
  <section style="flex:1;background:#052E16;border-radius:8px;padding:14px;text-align:center;">
    <p style="margin:0 0 4px 0;font-size:22px;color:#34D399;font-weight:bold;">看多</p>
    <p style="margin:0;font-size:12px;color:#34D399;">AI基础设施</p>
    <p style="margin:4px 0 0 0;font-size:11px;color:#8A8A8A;">GPU需求持续增长</p>
  </section>
  <!-- 黄色信号 -->
  <section style="flex:1;background:#422006;border-radius:8px;padding:14px;text-align:center;">
    <p style="margin:0 0 4px 0;font-size:22px;color:#FDE68A;font-weight:bold;">观望</p>
    <p style="margin:0;font-size:12px;color:#FDE68A;">AI Agent赛道</p>
    <p style="margin:4px 0 0 0;font-size:11px;color:#8A8A8A;">商业模式待验证</p>
  </section>
  <!-- 红色信号 -->
  <section style="flex:1;background:#450A0A;border-radius:8px;padding:14px;text-align:center;">
    <p style="margin:0 0 4px 0;font-size:22px;color:#FCA5A5;font-weight:bold;">看空</p>
    <p style="margin:0;font-size:12px;color:#FCA5A5;">传统SaaS</p>
    <p style="margin:4px 0 0 0;font-size:11px;color:#8A8A8A;">被AI原生替代</p>
  </section>
</section>
```

### 3.5 Evidence Warning

证据等级标注框。

```html
<section style="margin:16px 0;padding:12px 16px;background:#FEF3C7;border-radius:6px;border-left:3px solid #F59E0B;">
  <section style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
    <span style="font-size:12px;color:#92400E;font-weight:bold;">⚠️ 证据等级：B</span>
    <span style="font-size:11px;color:#78350F;">行业传闻 + 多方交叉验证</span>
  </section>
  <p style="margin:0;font-size:13px;line-height:1.6;color:#78350F;">此消息来自三个独立信源，但官方尚未确认。发布时间可能调整。</p>
</section>
```

---

## 四、写作规则

### 4.1 第一屏必须回答

读者打开文章3秒内必须看到：

1. **这事是什么** — 一句话说清
2. **和我有什么关系** — 利好/利空谁
3. **确定性多高** — 证据等级

```html
<!-- 第一屏结构 -->
[Dark News Hero] → 包含标题+信号标签+时间
[Conclusion Callout] → 一句话判断
[Three Signal Cards] → 看多/观望/看空
```

### 4.2 信息分层

| 层级 | 位置 | 内容 | 详细度 |
|------|------|------|--------|
| L0 信号 | 第一屏 | 一句话结论 + 方向判断 | 极简 |
| L1 要点 | 前30% | 3-5个关键事实 | 精炼 |
| L2 分析 | 中50% | 数据支撑 + 逻辑推理 | 中等 |
| L3 附录 | 后20% | 来源链接 + 方法论说明 | 详细 |

### 4.3 证据等级

每个关键声明必须标注证据等级：

| 等级 | 标签 | 含义 |
|------|------|------|
| A | ✅ 已确认 | 官方公告/财报/一手信息 |
| B | ⚠️ 高可信 | 多信源交叉验证 |
| C | 🟡 待验证 | 单一信源/行业传闻 |
| D | 🔴 未经证实 | 社交媒体/匿名消息 |

### 4.4 真图优先

1. **优先使用真实截图**，而非AI生成图
2. 所有截图必须用 Real Image Frame 包裹
3. 明确标注来源和时间
4. 如果没有真图，用SVG信息图替代，不使用AI生成图
5. 禁止在图片中暗示未经验证的信息

---

## 五、完整文章结构模板

```
[Dark News Hero] → 突发/核心标题 + 信号标签
[Conclusion Callout] → 一句话判断
[Three Signal Cards] → 方向性判断
---分隔---
[Section Header] → 事件详情
  [正文段落] → 事实描述
  [Evidence Warning] → 证据等级标注
  [Real Image Frame] → 官方截图
[Section Header] → 影响分析
  [正文段落] → 分析逻辑
  [Callout深色] → 核心洞察
  [SVG指标卡] → 数据展示
[Section Header] → 后续展望
  [正文段落] → 预判
[文末总结块] → 行动建议
[标签Chips] → 话题标签
```

---

## 六、排版建议

### 6.1 字数控制

| 类型 | 建议字数 | 阅读时间 |
|------|----------|----------|
| 快讯 | 500-800字 | 2分钟 |
| 深度分析 | 1500-2500字 | 5-8分钟 |
| 周报汇总 | 2000-3000字 | 8-12分钟 |

### 6.2 信号标签使用

- 🔴 BREAKING — 突发新闻
- 📊 DATA — 数据发布
- 📢 ANNOUNCEMENT — 官方公告
- 🔍 ANALYSIS — 深度分析
- ⚡ ALERT — 紧急提醒
- 📅 RECURRING — 定期更新（周报/月报）

### 6.3 数字呈现规则

1. 核心数字用等宽字体 + 加粗
2. 百分比变化用绿色（增长）/红色（下降）+ ↑↓箭头
3. 金额统一用一种货币标注
4. 大数字用K/M/B简写（如5.2M, 1.3B）
5. 对比数据必须放在同一行/同一卡
