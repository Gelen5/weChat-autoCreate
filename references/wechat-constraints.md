# 微信平台限制

> 微信公众号平台的技术限制详解，所有生成内容必须遵守这些约束。

---

## 一、CSS 限制

### 1.1 禁止项

| 禁止项 | 说明 |
|--------|------|
| 外部CSS | 不允许引用外部CSS文件或`<link>`标签 |
| `<style>`标签 | 不允许在正文中使用`<style>`标签 |
| JavaScript | 不允许任何`<script>`标签或JS代码 |
| 内联style限制 | 仅支持部分CSS属性（见下方白名单） |

### 1.2 支持的内联CSS属性

| 属性 | 支持值 | 说明 |
|------|--------|------|
| `color` | 十六进制/rgb | 文字颜色 |
| `background-color` | 十六进制/rgb | 背景颜色 |
| `font-size` | px/em/rem | 字体大小 |
| `font-weight` | normal/bold/100-900 | 字体粗细 |
| `font-style` | normal/italic | 字体样式 |
| `text-align` | left/center/right/justify | 文本对齐 |
| `text-decoration` | none/underline/line-through | 文本装饰 |
| `text-indent` | px/em | 首行缩进 |
| `line-height` | 数值/px/em | 行高 |
| `letter-spacing` | px | 字间距 |
| `margin` | px/em | 外边距（部分支持） |
| `padding` | px/em | 内边距（部分支持） |
| `border` | 简写/分写 | 边框（部分支持） |
| `border-radius` | px/% | 圆角 |
| `width` | px/% | 宽度 |
| `max-width` | px/% | 最大宽度 |
| `box-shadow` | 标准语法 | 阴影 |
| `display` | block/inline/inline-block/flex | 显示方式 |
| `vertical-align` | top/middle/bottom | 垂直对齐 |
| `white-space` | normal/pre/nowrap | 空白处理 |

### 1.3 不支持的CSS属性

| 属性 | 替代方案 |
|------|----------|
| `position: fixed/sticky` | 使用`margin`模拟间距 |
| `float` | 使用`display: inline-block` |
| `transform` | 不支持，无法实现旋转/缩放 |
| `transition/animation` | 不支持，无法实现动画 |
| `filter` | 不支持，无法实现模糊/滤镜 |
| `backdrop-filter` | 不支持 |
| `grid` | 使用`flex`或`table` |
| `gap` | 使用`margin`替代 |
| `clip-path` | 不支持 |
| `writing-mode` | 部分支持 |

---

## 二、图片限制

### 2.1 封面图

| 限制项 | 规格 |
|--------|------|
| 主封面尺寸 | 900 × 383 px（2.35:1） |
| 次封面尺寸 | 200 × 200 px（1:1） |
| 文件大小 | ≤ 2MB |
| 格式 | JPG / PNG / GIF |
| 动图 | 支持GIF但不超过2MB |

### 2.2 内文图片

| 限制项 | 规格 |
|--------|------|
| 最大宽度 | 1080px（超出会被压缩） |
| 文件大小 | 单张 ≤ 10MB |
| 格式 | JPG / PNG / GIF |
| 数量 | 单篇建议 ≤ 20张 |
| 动图 | 支持，但建议 ≤ 2MB |

### 2.3 图片处理规则

```yaml
image_processing:
  cover:
    - "生成后自动裁剪为900×383"
    - "压缩至2MB以内"
    - "JPG格式（照片类）/ PNG格式（图形类）"

  inline:
    - "宽度统一为1080px"
    - "压缩至500KB以内（建议）"
    - "JPG格式为主，截图用PNG"
    - "GIF动图仅用于必要演示"

  alt_text:
    required: true
    format: "{图片内容描述} - {文章标题}"
```

---

## 三、代码块限制

### 3.1 代码块渲染

微信对代码块的支持非常有限，需特殊处理：

| 限制 | 说明 | 处理方案 |
|------|------|----------|
| 不支持`<code>`标签高亮 | 代码无语法高亮 | 使用背景色+等宽字体模拟 |
| 不支持`<pre>`标签 | 预格式化文本受限 | 使用内联样式模拟 |
| 行号不支持 | 无法显示行号 | 不显示行号或用文本模拟 |
| 长代码溢出 | 不自动换行 | 手动在合适位置换行 |
| 复制功能 | 部分客户端支持 | 在代码块后提示"长按复制" |

### 3.2 代码块样式方案

```html
<!-- 行内代码 -->
<span style="background-color: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-family: monospace; font-size: 14px; color: #e74c3c;">code_here</span>

<!-- 代码块 -->
<section style="background-color: #2d2d2d; border-radius: 8px; padding: 16px; margin: 16px 0; overflow-x: auto;">
  <pre style="margin: 0; font-family: 'Menlo', 'Consolas', monospace; font-size: 14px; line-height: 1.6; color: #f8f8f2; white-space: pre-wrap; word-wrap: break-word;"><code>code content here</code></pre>
</section>
```

### 3.3 代码块规则

```yaml
code_block_rules:
  max_lines: 30              # 代码块最大行数
  max_blocks_per_article: 3  # 每篇最多代码块数
  language_hint: true        # 标注语言类型
  copy_hint: true            # 添加复制提示
  line_break: true           # 自动在80字符处换行
```

---

## 四、表格限制

### 4.1 表格渲染

| 限制 | 说明 | 处理方案 |
|------|------|----------|
| 不支持`<table>`标签 | 微信会过滤table标签 | 使用内联样式模拟表格 |
| 不支持合并单元格 | 无法使用colspan/rowspan | 避免需要合并单元格的表格 |
| 列宽不可控 | 列宽由内容决定 | 用空格或`&nbsp;`控制最小宽度 |
| 宽表格溢出 | 不自动水平滚动 | 限制列数≤4，每列内容简短 |
| 复杂表格不支持 | 嵌套表格不支持 | 拆分为多个简单表格 |

### 4.2 表格样式方案

```html
<!-- 模拟表格 -->
<section style="border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; margin: 16px 0;">
  <!-- 表头 -->
  <section style="display: flex; background-color: #f5f5f5; padding: 10px 12px; font-weight: bold; border-bottom: 2px solid #e0e0e0;">
    <span style="flex: 1;">列1</span>
    <span style="flex: 1;">列2</span>
    <span style="flex: 1;">列3</span>
  </section>
  <!-- 数据行 -->
  <section style="display: flex; padding: 10px 12px; border-bottom: 1px solid #e0e0e0;">
    <span style="flex: 1;">数据1</span>
    <span style="flex: 1;">数据2</span>
    <span style="flex: 1;">数据3</span>
  </section>
</section>
```

### 4.3 表格规则

```yaml
table_rules:
  max_columns: 4             # 最大列数
  max_rows: 10               # 最大行数（不含表头）
  max_tables_per_article: 2  # 每篇最多表格数
  alternative: "如果表格超限，改用列表或图片呈现"
```

---

## 五、排版限制

### 5.1 字体限制

| 限制 | 说明 |
|------|------|
| 不支持自定义字体 | 只能使用系统字体 |
| 西文字体 | 默认 sans-serif |
| 中文字体 | 默认跟随系统（PingFang SC / 微软雅黑） |
| 等宽字体 | Menlo / Consolas（代码块用） |

### 5.2 段落限制

| 限制 | 说明 | 建议 |
|------|------|------|
| 段间距 | 需用margin/padding控制 | 段间距12-16px |
| 行间距 | 需用line-height控制 | 行高1.75-2.0 |
| 首行缩进 | 部分客户端支持 | 建议不缩进，用空行分段 |
| 文字颜色 | 不超过3种 | 主色+强调色+次要色 |

### 5.3 特殊元素限制

| 元素 | 限制 | 替代方案 |
|------|------|----------|
| 分割线`<hr>` | 部分客户端不支持 | 用带样式的`<section>`模拟 |
| 引用`<blockquote>` | 支持但样式有限 | 用带左边框的`<section>`模拟 |
| 列表`<ol>/<ul>` | 基本支持 | 简单列表可用，复杂列表用`<section>` |
| 链接`<a>` | 仅支持微信公众号内链接 | 超链接用阅读原文或二维码 |
| 视频 | 需上传到微信视频号 | 先传视频号再引用 |
| 音频 | 需上传到微信 | 先传音频再引用 |

---

## 六、内容长度限制

| 限制项 | 规格 |
|--------|------|
| 标题 | ≤64字节（约21个汉字） |
| 摘要 | ≤120字节（约40个汉字） |
| 正文 | ≤20000字符（约6600汉字） |
| 标签 | 5个，每个2-6字 |
| 留言 | ≤600字 |

---

## 七、完整检查清单

```yaml
wechat_constraints_check:
  css:
    - "无外部CSS引用"
    - "无<style>标签"
    - "无JavaScript"
    - "所有样式使用内联style"
    - "仅使用支持的CSS属性"

  images:
    - "封面图900×383"
    - "内文图宽度≤1080px"
    - "单图≤2MB(封面)/10MB(内文)"
    - "所有图片有alt描述"

  code:
    - "代码块≤30行"
    - "每篇代码块≤3个"
    - "代码块有语言标注"
    - "长代码已换行处理"

  tables:
    - "表格≤4列"
    - "表格≤10行"
    - "每篇表格≤2个"
    - "使用section模拟表格"

  layout:
    - "字体颜色≤3种"
    - "行高1.75-2.0"
    - "段间距12-16px"
    - "无自定义字体"

  content_length:
    - "标题≤21汉字"
    - "摘要≤40汉字"
    - "正文≤6600汉字"
    - "标签5个"
```
