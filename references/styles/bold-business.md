# 商务锐利风 (bold-business)

> 视觉定位：商业分析 / 投资研究 / 行业报告
> 适合读者：投资人、高管、商业分析师、创业者

---

## 一、视觉定位

| 维度 | 描述 |
|------|------|
| 语气 | 锐利、果断、数据驱动 |
| 节奏 | 中等节奏，核心观点反复出现，信息密度高但结构清晰 |
| 配色 | 深蓝权威 + 金色价值 + 红色警示，冷色为主 |
| 字体 | 系统无衬线，数据用等宽，标题用加粗窄体感 |
| 留白 | 商务级别，不过度也不拥挤，数据区域紧凑 |

---

## 二、Color Token

### 2.1 主色调

| Token | 值 | 用途 |
|-------|------|------|
| `--c-navy` | `#0C2340` | 主色：标题、深色背景、权威感 |
| `--c-navy-light` | `#1B3A5C` | 次深色：卡片深底 |
| `--c-slate` | `#334155` | 正文主色 |
| `--c-gray` | `#64748B` | 次要文字、说明 |
| `--c-silver` | `#94A3B8` | 辅助说明、注释 |
| `--c-frost` | `#E2E8F0` | 浅底背景、分隔线 |
| `--c-white` | `#FFFFFF` | 卡片白底 |

### 2.2 强调色

| Token | 值 | 用途 |
|-------|------|------|
| `--c-gold` | `#D4A017` | 价值标记：关键数据、核心结论、高光 |
| `--c-gold-light` | `#F0D060` | 浅金色：次要高光 |
| `--c-gold-bg` | `#FFFBEB` | 金色浅底：数据框 |
| `--c-blue` | `#2563EB` | 行动色：链接、可点击元素 |
| `--c-blue-light` | `#DBEAFE` | 蓝色浅底 |

### 2.3 警示色

| Token | 值 | 用途 |
|-------|------|------|
| `--c-red` | `#DC2626` | 风险标注、下降指标、警示 |
| `--c-red-bg` | `#FEF2F2` | 红色浅底 |
| `--c-orange` | `#EA580C` | 注意、待观察 |
| `--c-orange-bg` | `#FFF7ED` | 橙色浅底 |

---

## 三、组件变体

### 3.1 报告头卡

深蓝背景的报告头部，标题+核心指标预览。

```html
<section style="background:#0C2340;border-radius:10px;padding:28px 24px;margin:0 0 24px 0;">
  <section style="display:flex;align-items:center;margin-bottom:12px;">
    <section style="width:4px;height:20px;background:#D4A017;border-radius:2px;margin-right:8px;"></section>
    <span style="font-size:12px;color:#D4A017;letter-spacing:2px;font-weight:bold;">INDUSTRY REPORT</span>
  </section>
  <h1 style="margin:0 0 16px 0;font-size:20px;line-height:1.4;color:#FFFFFF;font-weight:bold;"><span leaf="">2026年中国AI基础设施市场深度分析</span></h1>
  <section style="display:flex;flex-wrap:wrap;">
    <section>
      <p style="margin:0;font-size:22px;color:#D4A017;font-weight:bold;"><span leaf="">¥2,400亿</span></p>
      <p style="margin:2px 0 0 0;font-size:11px;color:#94A3B8;"><span leaf="">市场规模</span></p>
    </section>
    <section style="margin-left:16px;">
      <p style="margin:0;font-size:22px;color:#FFFFFF;font-weight:bold;">+34%</p>
      <p style="margin:2px 0 0 0;font-size:11px;color:#94A3B8;"><span leaf="">YoY增长</span></p>
    </section>
    <section style="margin-left:16px;">
      <p style="margin:0;font-size:22px;color:#FFFFFF;font-weight:bold;"><span leaf="">3-5年</span></p>
      <p style="margin:2px 0 0 0;font-size:11px;color:#94A3B8;"><span leaf="">投资周期</span></p>
    </section>
  </section>
</section>
```

### 3.2 数据指标卡

单行或双行数据展示，大数字+说明。

```html
<section style="margin:16px 0;padding:16px 20px;background:#FFFBEB;border:1px solid #E2E8F0;border-radius:8px;">
  <p style="margin:0 0 4px 0;font-size:12px;color:#64748B;"><span leaf="">GPU算力需求（中国区）</span></p>
  <section style="display:flex;align-items:baseline;">
    <span style="font-size:28px;color:#0C2340;font-weight:bold;margin-right:8px;">1.2M</span>
    <span style="font-size:14px;color:#D4A017;font-weight:bold;">↑ 67% YoY</span>
  </section>
  <p style="margin:4px 0 0 0;font-size:12px;color:#64748B;"><span leaf="">单位：H100等效卡 · 数据来源：IDC 2026Q1</span></p>
</section>
```

### 3.3 编号标题（商务版）

带蓝色标记的小节标题。

```html
<section style="margin:28px 0 14px 0;display:flex;align-items:center;">
  <section style="flex-shrink:0;width:28px;height:28px;background:#0C2340;border-radius:4px;text-align:center;line-height:28px;color:#D4A017;font-size:13px;font-weight:bold;margin-right:10px;">01</section>
  <h2 style="margin:0;font-size:17px;line-height:1.4;color:#0C2340;font-weight:bold;"><span leaf="">市场格局与竞争态势</span></h2>
</section>
```

### 3.4 正文段落

商务向正文，数据关键词用金色高亮。

```html
<p style="margin:0 0 16px 0;font-size:15px;line-height:1.8;color:#334155;"><span leaf="">2026年Q1，中国AI基础设施市场规模达到</span><strong style="color:#D4A017;"><span leaf="">¥600亿</span></strong><span leaf="">，同比增长</span><strong style="color:#D4A017;">34%</strong><span leaf="">。其中GPU算力占比首次超过</span><strong style="color:#D4A017;">60%</strong><span leaf="">，标志着算力需求的结构性转变。</span></p>
```

### 3.5 对比表格

简化的商务对比表。

```html
<section style="margin:16px 0;border:1px solid #E2E8F0;border-radius:8px;overflow:hidden;">
  <table style="width:100%;border-collapse:collapse;font-size:13px;">
    <tr style="background:#0C2340;">
      <td style="padding:10px 14px;color:#FFFFFF;font-weight:bold;"><span leaf="">维度</span></td>
      <td style="padding:10px 14px;color:#D4A017;font-weight:bold;text-align:center;"><span leaf="">华为云</span></td>
      <td style="padding:10px 14px;color:#D4A017;font-weight:bold;text-align:center;"><span leaf="">阿里云</span></td>
    </tr>
    <tr style="background:#FFFFFF;">
      <td style="padding:10px 14px;color:#334155;"><span leaf="">GPU算力</span></td>
      <td style="padding:10px 14px;color:#0C2340;font-weight:bold;text-align:center;">★★★★</td>
      <td style="padding:10px 14px;color:#0C2340;font-weight:bold;text-align:center;">★★★★☆</td>
    </tr>
    <tr style="background:#F8FAFC;">
      <td style="padding:10px 14px;color:#334155;"><span leaf="">生态开放度</span></td>
      <td style="padding:10px 14px;color:#0C2340;font-weight:bold;text-align:center;">★★★</td>
      <td style="padding:10px 14px;color:#0C2340;font-weight:bold;text-align:center;">★★★★★</td>
    </tr>
    <tr style="background:#FFFFFF;">
      <td style="padding:10px 14px;color:#334155;"><span leaf="">价格竞争力</span></td>
      <td style="padding:10px 14px;color:#0C2340;font-weight:bold;text-align:center;">★★★★</td>
      <td style="padding:10px 14px;color:#0C2340;font-weight:bold;text-align:center;">★★★☆</td>
    </tr>
  </table>
</section>
```

### 3.6 评级框

投资评级/推荐等级展示。

```html
<section style="margin:20px 0;display:flex;border-radius:8px;overflow:hidden;">
  <section style="flex:1;background:#0C2340;padding:16px;text-align:center;">
    <p style="margin:0 0 4px 0;font-size:11px;color:#94A3B8;letter-spacing:1px;">INFRA</p>
    <p style="margin:0;font-size:20px;color:#D4A017;font-weight:bold;"><span leaf="">增持</span></p>
  </section>
  <section style="flex:1;background:#1B3A5C;padding:16px;text-align:center;">
    <p style="margin:0 0 4px 0;font-size:11px;color:#94A3B8;letter-spacing:1px;">APPLICATION</p>
    <p style="margin:0;font-size:20px;color:#FFFFFF;font-weight:bold;"><span leaf="">中性</span></p>
  </section>
  <section style="flex:1;background:#0C2340;padding:16px;text-align:center;">
    <p style="margin:0 0 4px 0;font-size:11px;color:#94A3B8;letter-spacing:1px;">TRADITION</p>
    <p style="margin:0;font-size:20px;color:#DC2626;font-weight:bold;"><span leaf="">减持</span></p>
  </section>
</section>
```

### 3.7 风险提示框

红色边框的风险提示。

```html
<section style="margin:16px 0;padding:14px 16px;background:#FEF2F2;border-left:3px solid #DC2626;border-radius:0 8px 8px 0;">
  <p style="margin:0 0 6px 0;font-size:13px;color:#DC2626;font-weight:bold;"><span leaf="">⚠️ 风险提示</span></p>
  <p style="margin:0;font-size:13px;line-height:1.7;color:#334155;"><span leaf="">GPU出口管制政策可能影响供应，建议关注替代方案。此判断基于当前政策环境，政策变化可能导致评级调整。</span></p>
</section>
```

### 3.8 行动CTA

明确的行动号召。

```html
<section style="margin:24px 0;padding:20px;background:#0C2340;border-radius:8px;text-align:center;">
  <p style="margin:0 0 8px 0;font-size:16px;color:#FFFFFF;font-weight:bold;"><span leaf="">获取完整报告</span></p>
  <p style="margin:0 0 14px 0;font-size:13px;color:#94A3B8;"><span leaf="">52页PDF · 含数据附录和模型说明</span></p>
  <section style="display:inline-block;padding:10px 28px;background:#D4A017;border-radius:6px;">
    <span style="font-size:14px;color:#0C2340;font-weight:bold;"><span leaf="">立即下载 →</span></span>
  </section>
</section>
```

---

## 四、排版建议

### 4.1 报告文章结构

```
[报告头卡] → 标题+3个核心指标
[编号标题01] → 市场格局
  [数据指标卡] → 市场规模
  [对比表格] → 竞品对比
  [正文段落] → 分析
[编号标题02] → 投资逻辑
  [正文段落] → 核心论点
  [评级框] → 方向性判断
  [风险提示框] → 风险
[编号标题03] → 行动建议
  [正文段落] → 具体建议
[行动CTA] → 下载/联系
[文末总结块] → 核心要点
```

### 4.2 数据呈现规则

1. **数字必须标注来源**：来源名+时间
2. **对比数据必须有同一基线**：同一时间范围、同一口径
3. **增长率用箭头+颜色**：↑绿 / ↓红
4. **评级必须有有效期**：评级基于某时点信息
5. **大数字单独占一行**：28px加粗

### 4.3 商务写作规则

1. **先结论后论证**：每段第一句是结论
2. **数据驱动**：每个判断必须有数据支撑
3. **标注置信度**：对判断标注确定性
4. **风险前置**：机会和风险一起呈现
5. **可操作性**：建议必须具体到"做什么"

### 4.4 禁止事项

- 不使用表情符号（用文字替代）
- 不使用口语化表达
- 不使用未标注来源的数据
- 不给出没有时效性的评级
- 不省略风险提示

---

## 附：文章类型 × 组件配方表

> **先判断文章类型，再按配方选组件**——本风格的主战场是研报和商业分析。数字必须落在数据指标卡或对比表格里，禁止裸奔在正文段落中。同屏组件种类 ≤ 4。

| 文章类型 | 开场 | 正文骨架 | 数据/结论组件 | 收尾 | 禁用 |
|---|---|---|---|---|---|
| 行业报告（主场景） | 报告头卡 | （编号标题 → 正文段落 → 数据指标卡或对比表格）×N | 评级框 | 风险提示框 → 行动CTA | — |
| 深度分析 | 报告头卡 | （编号标题 → 正文段落）×N | 数据指标卡×1-2 | 风险提示框 | 评级框、对比表格>1 |
| 测评对比 | 报告头卡 | 对比表格（先给结论总表）→（编号标题 → 正文段落）×N | 评级框 | 行动CTA | — |
| 新闻快讯 | 报告头卡 | 正文段落×3 | 数据指标卡×1 | 行动CTA | 对比表格、评级框 |
| 清单盘点 | 报告头卡 | （编号标题 → 正文段落）×N | — | 行动CTA | 评级框、对比表格 |
| 观点锐评 | 不推荐本风格（报告腔会吃掉锐度） | — | — | — | 改用 minimal-elegant |
