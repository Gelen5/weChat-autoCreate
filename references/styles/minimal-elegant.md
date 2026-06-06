# 极简优雅风 (minimal-elegant)

> 视觉定位：深度思考 / 人文 / 哲学 / 生活方式
> 适合读者：知识分子、文艺青年、慢读者

---

## 一、视觉定位

| 维度 | 描述 |
|------|------|
| 语气 | 安静、沉思、有温度 |
| 节奏 | 慢节奏，大留白，一段一呼吸 |
| 配色 | 暖灰 + 米色 + 金色强调，拒绝一切冷色调 |
| 字体 | 系统衬线优先，行距宽裕 |
| 留白 | 充裕，段落间距大于其他风格，文字呼吸感 |

---

## 二、Color Token

### 2.1 主色调

| Token | 值 | 用途 |
|-------|------|------|
| `--c-ink` | `#2C2420` | 标题，墨色 |
| `--c-ink-light` | `#5C4A3E` | 正文主色，偏暖 |
| `--c-stone` | `#8C7E72` | 次要文字、说明 |
| `--c-mist` | `#B8ADA3` | 装饰线、弱化文字 |
| `--c-cream` | `#FAF6F1` | 页面底色、温暖背景 |
| `--c-linen` | `#F0EBE3` | 浅底卡片 |
| `--c-white` | `#FFFFFF` | 纯白底 |

### 2.2 强调色

| Token | 值 | 用途 |
|-------|------|------|
| `--c-gold` | `#B8860B` | 主强调：标题装饰、引用标记 |
| `--c-gold-light` | `#D4A843` | 浅金色：次级装饰 |
| `--c-gold-bg` | `#FFF8E7` | 金色浅底：高亮区 |
| `--c-terracotta` | `#C67B5C` | 次强调：重要但非核心 |
| `--c-sage` | `#8B9D77` | 辅助色：自然、安静 |

### 2.3 语义色

| Token | 值 | 用途 |
|-------|------|------|
| `--c-rose` | `#C4727F` | 温柔警示、标注 |
| `--c-sky` | `#7BA7BC` | 冷静补充（克制使用） |

---

## 三、组件变体

### 3.1 宽留白标题

文章标题，大量留白，标题如画。

```html
<section style="margin:0 0 40px 0;padding:48px 0 32px 0;text-align:center;">
  <p style="margin:0 0 16px 0;font-size:12px;color:#B8860B;letter-spacing:4px;">ESSAY</p>
  <h1 style="margin:0 0 16px 0;font-size:22px;line-height:1.6;color:#2C2420;font-weight:bold;">在喧嚣中寻找安静的力量</h1>
  <section style="margin:16px auto;width:40px;height:1px;background:#B8860B;"></section>
  <p style="margin:16px 0 0 0;font-size:13px;color:#8C7E72;">关于留白、呼吸与生活的节奏</p>
</section>
```

### 3.2 引用大字

大字引用，金句/名言的展示方式。

```html
<section style="margin:32px 0;padding:24px 0;text-align:center;">
  <p style="margin:0 0 8px 0;font-size:28px;color:#B8860B;line-height:1.2;">"</p>
  <p style="margin:0 0 12px 0;font-size:17px;line-height:1.8;color:#2C2420;font-weight:bold;letter-spacing:1px;">安静不是没有声音，<br/>而是内心的秩序。</p>
  <p style="margin:0;font-size:13px;color:#8C7E72;">—— 里尔克</p>
</section>
```

### 3.3 正文段落（宽行距）

比默认更宽的行距，衬线字体倾向。

```html
<p style="margin:0 0 24px 0;font-size:15px;line-height:2.0;color:#5C4A3E;text-align:justify;letter-spacing:0.5px;">在一个追求效率的时代，我们很少停下来思考"慢"本身的价值。效率让我们做更多的事，但不一定让我们做对的事。真正的思考需要留白——就像国画的韵味，不在笔墨，而在未着墨处。</p>
```

### 3.4 过渡句

段与段之间的过渡，制造呼吸感。

```html
<section style="margin:28px 0;text-align:center;">
  <p style="margin:0;font-size:13px;color:#B8ADA3;font-style:italic;letter-spacing:1px;">· · ·</p>
</section>
```

或带文字的过渡：

```html
<section style="margin:28px 0;text-align:center;">
  <p style="margin:0;font-size:14px;color:#8C7E72;font-style:italic;letter-spacing:1px;">然而，真正的转折发生在那个安静的午后。</p>
</section>
```

### 3.5 思考卡

浅色背景的思考引导框，不压迫。

```html
<section style="background:#FFF8E7;border-radius:8px;padding:20px 24px;margin:24px 0;">
  <p style="margin:0 0 8px 0;font-size:12px;color:#B8860B;letter-spacing:2px;font-weight:bold;">💭 思考</p>
  <p style="margin:0;font-size:14px;line-height:1.8;color:#5C4A3E;">如果今天只做一件事，你会选择什么？这个问题的答案，往往就是你应该投入最多时间的地方。</p>
</section>
```

### 3.6 注解框

深色但温暖的注释框。

```html
<section style="background:#2C2420;border-radius:8px;padding:20px 24px;margin:24px 0;">
  <p style="margin:0 0 8px 0;font-size:12px;color:#D4A843;letter-spacing:2px;font-weight:bold;">注</p>
  <p style="margin:0;font-size:14px;line-height:1.8;color:#B8ADA3;">此处的"安静"并非物理意义上的无声，而是一种内心的状态。正如庄子所言"大音希声"。</p>
</section>
```

### 3.7 配图+诗文caption

图片配诗意说明。

```html
<section style="margin:24px 0;text-align:center;">
  <img src="IMAGE_URL" style="width:100%;border-radius:8px;display:block;" />
  <p style="margin:12px 0 0 0;font-size:12px;color:#8C7E72;font-style:italic;letter-spacing:1px;">光影之间，时间静止</p>
</section>
```

### 3.8 文末签名

带作者签名的结尾。

```html
<section style="margin:40px 0 0 0;padding:24px 0;border-top:1px solid #E8DFD5;text-align:center;">
  <p style="margin:0 0 8px 0;font-size:14px;color:#5C4A3E;font-style:italic;">生活不是等待暴风雨过去，而是学会在雨中起舞。</p>
  <section style="margin:16px auto;width:24px;height:1px;background:#B8860B;"></section>
  <p style="margin:8px 0 4px 0;font-size:13px;color:#2C2420;font-weight:bold;">写作者名</p>
  <p style="margin:0;font-size:12px;color:#8C7E72;">某处 · 安静地活着</p>
</section>
```

---

## 四、排版建议

### 4.1 节奏控制

```
[宽留白标题]
（48px留白）
[正文段落]
（24px留白）
[过渡句]
（28px留白）
[引用大字]
（32px留白）
[正文段落]
（24px留白）
[思考卡]
（24px留白）
[正文段落]
（40px留白）
[文末签名]
```

### 4.2 用字原则

1. **少即是多**：每段不超过150字
2. **一句一行**：关键句子独占一行
3. **留白即节奏**：段落间距 > 其他风格
4. **不连用视觉组件**：两个组件之间必须有至少一段正文
5. **慎用粗体**：整篇文章粗体不超过3处

### 4.3 推荐文章结构

| 段落 | 组件 | 字数 |
|------|------|------|
| 开头 | 宽留白标题 | 0 |
| 引入 | 正文段落 × 2 | 300 |
| 转折 | 过渡句 + 引用大字 | 50 |
| 展开 | 正文段落 + 思考卡 | 400 |
| 深入 | 正文段落 + 注解框 | 300 |
| 收束 | 正文段落 × 1 | 150 |
| 结尾 | 文末签名 | 0 |

### 4.4 配图规则

1. 全文配图不超过3张
2. 图片色调偏暖，避免冷色
3. 必须有诗意caption
4. 不使用SVG信息图（与风格不符）
5. 不使用表情符号（用标点替代）
