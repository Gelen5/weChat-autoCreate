# 微信HTML/CSS支持与过滤规范

> 微信公众号编辑器对HTML/CSS有严格限制，本文档详细列出支持与不支持的标签、属性、CSS特性，帮助排版输出100%兼容。

---

## 一、核心原则

### 1.1 全内联样式

**必须将所有样式写在 `style` 属性中**，不使用 `<style>` 标签、`class`、`id`。

```html
<!-- ✅ 正确：全内联 -->
<section style="background:#2D2D2D;border-radius:8px;padding:16px;">
  <p style="color:#FFFFFF;font-size:14px;">内容</p>
</section>

<!-- ❌ 错误：使用class -->
<section class="dark-card">
  <p class="white-text">内容</p>
</section>

<!-- ❌ 错误：使用<style>标签 -->
<style>
.dark-card { background: #2D2D2D; }
</style>
```

### 1.2 禁止使用的特性

| 特性 | 原因 | 替代方案 |
|------|------|----------|
| `<style>` 标签 | 被过滤 | 全内联style属性 |
| `class` 属性 | 被过滤 | 内联样式 |
| `id` 属性 | 被过滤 | 不使用 |
| `position` 相关 | 被过滤 | 用margin/padding模拟 |
| `animation` | 被过滤 | 用SVG SMIL（有限支持） |
| `transform` | 被过滤 | 不使用变换效果 |
| `float` | 不稳定 | 用flex布局或table |
| `<script>` | 被过滤 | 不使用JavaScript |
| `<iframe>` | 被过滤 | 不使用 |
| `<form>` / `<input>` | 被过滤 | 不使用 |
| `data-*` 属性 | 被过滤 | 不使用 |
| `javascript:` 协议 | 被过滤 | 不使用 |
| `@font-face` | 被过滤 | 使用系统字体 |

---

## 二、支持的HTML标签

### 2.1 完全支持

| 标签 | 说明 |
|------|------|
| `<p>` | 段落，最常用的文本容器 |
| `<br>` | 换行 |
| `<strong>` | 加粗（比`<b>`更语义化） |
| `<em>` | 斜体（比`<i>`更语义化） |
| `<span>` | 行内容器，配合style使用 |
| `<section>` | 块级容器，**微信排版的万能容器** |
| `<h1>` ~ `<h6>` | 标题（建议只用h1-h3） |
| `<img>` | 图片（需注意域名限制） |
| `<a>` | 超链接（仅支持href，target无效） |
| `<ol>` / `<ul>` / `<li>` | 有序/无序列表 |
| `<blockquote>` | 引用块 |
| `<table>` / `<tr>` / `<td>` / `<th>` | 表格 |
| `<svg>` | SVG图形（有限制，见下文） |

### 2.2 部分支持

| 标签 | 限制 |
|------|------|
| `<div>` | 可用但`<section>`更推荐 |
| `<b>` | 可用但推荐`<strong>` |
| `<i>` | 可用但推荐`<em>` |
| `<u>` | 下划线，样式可能被覆盖 |
| `<s>` / `<del>` | 删除线，样式可能被覆盖 |
| `<sup>` / `<sub>` | 上下标 |
| `<hr>` | 分隔线，样式控制有限 |
| `<pre>` / `<code>` | 代码块，样式可能被覆盖 |
| `<figure>` / `<figcaption>` | 可能被过滤，用section替代 |
| `<details>` / `<summary>` | 部分版本支持，不稳定 |

### 2.3 被过滤或不支持

| 标签 | 说明 |
|------|------|
| `<style>` | 被完全过滤 |
| `<script>` | 被完全过滤 |
| `<link>` | 被完全过滤 |
| `<meta>` | 被完全过滤 |
| `<iframe>` | 被完全过滤 |
| `<embed>` / `<object>` | 被完全过滤 |
| `<video>` / `<audio>` | 需用微信自带媒体组件 |
| `<canvas>` | 不支持 |
| `<input>` / `<textarea>` | 被过滤 |
| `<button>` | 被过滤，用`<section>`+onclick模拟（但onclick也被过滤） |
| `<select>` | 被过滤 |
| `<map>` / `<area>` | 被过滤 |

---

## 三、支持的CSS属性

### 3.1 完全支持的内联样式属性

**文本相关**

| 属性 | 说明 | 示例 |
|------|------|------|
| `color` | 文字颜色 | `color:#1A1A1A` |
| `font-size` | 字号 | `font-size:15px` |
| `font-weight` | 字重 | `font-weight:bold` |
| `font-style` | 字体样式 | `font-style:italic` |
| `text-align` | 对齐 | `text-align:center` |
| `text-decoration` | 装饰线 | `text-decoration:underline` |
| `text-indent` | 缩进 | `text-indent:2em` |
| `line-height` | 行高 | `line-height:1.8` |
| `letter-spacing` | 字间距 | `letter-spacing:2px` |
| `white-space` | 空白处理 | `white-space:nowrap` |
| `word-break` | 断词 | `word-break:break-all` |

**盒模型**

| 属性 | 说明 | 示例 |
|------|------|------|
| `margin` | 外边距 | `margin:16px 0` |
| `margin-top/right/bottom/left` | 单侧外边距 | `margin-top:8px` |
| `padding` | 内边距 | `padding:16px 20px` |
| `padding-top/right/bottom/left` | 单侧内边距 | `padding-left:16px` |
| `width` | 宽度 | `width:100%` |
| `max-width` | 最大宽度 | `max-width:680px` |
| `height` | 高度 | `height:3px` |
| `box-sizing` | 盒模型 | `box-sizing:border-box` |

**背景**

| 属性 | 说明 | 示例 |
|------|------|------|
| `background` | 背景简写 | `background:#F2F2F2` |
| `background-color` | 背景色 | `background-color:#2D2D2D` |
| `background-image` | 背景图（有限） | `background-image:url(...)` |

**边框**

| 属性 | 说明 | 示例 |
|------|------|------|
| `border` | 边框简写 | `border:1px solid #B0B0B0` |
| `border-top/right/bottom/left` | 单侧边框 | `border-left:4px solid #059669` |
| `border-radius` | 圆角 | `border-radius:8px` |
| `border-collapse` | 表格边框合并 | `border-collapse:collapse` |

**显示与布局**

| 属性 | 说明 | 示例 |
|------|------|------|
| `display` | 显示类型 | `display:flex`, `display:inline-block`, `display:none` |
| `flex` | flex简写 | `flex:1` |
| `flex-direction` | flex方向 | `flex-direction:column` |
| `flex-wrap` | flex换行 | `flex-wrap:wrap` |
| `flex-shrink` | flex收缩 | `flex-shrink:0` |
| `justify-content` | 主轴对齐 | `justify-content:center` |
| `align-items` | 交叉轴对齐 | `align-items:center` |
| `gap` | 间距 | `gap:8px` |
| `overflow` | 溢出处理 | `overflow:hidden` |
| `vertical-align` | 垂直对齐 | `vertical-align:middle` |

**其他**

| 属性 | 说明 | 示例 |
|------|------|------|
| `opacity` | 透明度 | `opacity:0.8` |
| `border-spacing` | 边框间距 | `border-spacing:0` |
| `table-layout` | 表格布局 | `table-layout:fixed` |
| `list-style` | 列表样式 | `list-style:none` |

### 3.2 不支持或被过滤的CSS属性

| 属性 | 说明 |
|------|------|
| `position` | 被过滤，无法使用fixed/absolute/relative |
| `top/right/bottom/left` | 依赖position，不可用 |
| `z-index` | 依赖position，不可用 |
| `float` | 不稳定，部分场景被过滤 |
| `clear` | 依赖float，不可用 |
| `animation` / `@keyframes` | 被完全过滤 |
| `transition` | 被过滤 |
| `transform` | 被过滤 |
| `box-shadow` | 部分版本支持，不稳定 |
| `text-shadow` | 部分版本支持，不稳定 |
| `filter` | 被过滤 |
| `clip-path` | 被过滤 |
| `gradient` | 被过滤 |
| `::before` / `::after` | 伪元素被过滤 |
| `calc()` | 被过滤 |
| `var()` | 被过滤 |
| `min()` / `max()` / `clamp()` | 被过滤 |
| `cursor` | 被过滤 |
| `user-select` | 被过滤 |
| `-webkit-` 前缀属性 | 大部分被过滤 |

### 3.3 布局替代方案

| 需求 | 不可用方案 | 推荐替代 |
|------|-----------|----------|
| 水平居中 | `margin:0 auto` + `width` | `display:flex;justify-content:center` |
| 垂直居中 | `position:absolute` + `transform` | `display:flex;align-items:center` |
| 左右分栏 | `float:left/right` | `display:flex` |
| 文字环绕 | `float` | `display:flex` 或 table |
| 装饰元素 | `::before/::after` | 真实HTML元素 + 内联样式 |
| 阴影 | `box-shadow` | 用浅色边框或背景色差模拟 |
| 渐变 | `linear-gradient` | 用纯色或SVG背景 |
| 响应式 | `@media` | 固定375px宽度设计 |

---

## 四、图片规范

### 4.1 图片域名限制

微信公众号只允许以下图片域名：

| 域名 | 说明 |
|------|------|
| `mmbiz.qpic.cn` | 微信图片服务器（主要） |
| `mmbiz.qlogo.cn` | 微信头像/Logo |
| `wx.qlogo.cn` | 微信头像 |
| `thirdwx.qlogo.cn` | 第三方微信头像 |

**重要限制：**
- 外部图片URL（如imgur、unsplash等）会被微信过滤或替换
- 图片必须先上传到微信图片服务器，获取`mmbiz.qpic.cn`链接
- 图片大小建议不超过2MB
- 图片宽度建议不超过900px（公众号显示区域约677px）

### 4.2 图片格式

| 格式 | 支持 | 说明 |
|------|------|------|
| JPG/JPEG | ✅ | 照片类推荐 |
| PNG | ✅ | 截图、带透明度的图片 |
| GIF | ✅ | 动图，但体积需控制 |
| WebP | ⚠️ | 部分版本支持，不推荐 |
| SVG | ⚠️ | 通过`<svg>`标签内嵌，不支持`<img src="*.svg">` |
| BMP | ❌ | 不支持 |
| TIFF | ❌ | 不支持 |

### 4.3 `<img>` 标签注意事项

```html
<!-- ✅ 正确用法 -->
<img src="https://mmbiz.qpic.cn/mmbiz_png/xxx/0" style="width:100%;display:block;border-radius:8px;" />

<!-- 必须的属性和样式 -->
<!-- 1. src必须为微信域名 -->
<!-- 2. style中必须包含display:block消除底部间隙 -->
<!-- 3. width建议用百分比 -->
<!-- 4. 不需要alt（会被部分版本过滤） -->
```

---

## 五、SVG支持规范

### 5.1 内嵌SVG

微信支持通过`<svg>`标签直接内嵌SVG图形，但有严格限制。

**支持的SVG元素：**

| 元素 | 说明 |
|------|------|
| `<svg>` | 根元素，需设置viewBox |
| `<rect>` | 矩形 |
| `<circle>` | 圆形 |
| `<ellipse>` | 椭圆 |
| `<line>` | 直线 |
| `<polyline>` | 折线 |
| `<polygon>` | 多边形 |
| `<path>` | 路径 |
| `<text>` | 文本 |
| `<tspan>` | 文本片段 |
| `<g>` | 分组 |
| `<defs>` | 定义 |
| `<linearGradient>` | 线性渐变 |
| `<radialGradient>` | 径向渐变 |
| `<stop>` | 渐变停止点 |
| `<marker>` | 标记（箭头等） |

**不支持/被过滤的SVG元素：**

| 元素 | 说明 |
|------|------|
| `<use>` | 被过滤 |
| `<symbol>` | 被过滤 |
| `<pattern>` | 被过滤 |
| `<clipPath>` | 被过滤 |
| `<mask>` | 被过滤 |
| `<filter>` | 被过滤 |
| `<foreignObject>` | 被过滤 |
| `<image>` (SVG内) | 被过滤 |

### 5.2 SVG SMIL动画

**SVG SMIL动画会被微信过滤。** 以下元素不可用：

- `<animate>`
- `<animateTransform>`
- `<animateMotion>`
- `<set>`

**这意味着所有SVG动画效果在微信公众号中都不会显示。** 如果需要动画效果，只能通过GIF图片或视频实现。

### 5.3 SVG注意事项

1. **必须设置viewBox**：`<svg viewBox="0 0 680 200">`
2. **宽度用100%**：`style="width:100%;display:block;"`
3. **字号不能太小**：手机上13px以下无法阅读，建议SVG内文字最小14px
4. **颜色必须用具体值**：不支持currentColor，用具体hex值
5. **不支持外部字体**：SVG内文字使用系统字体
6. **测试兼容性**：复杂SVG建议在手机端测试

### 5.4 SVG模板示例

```html
<section style="margin:20px 0;">
  <svg viewBox="0 0 680 200" style="width:100%;display:block;" xmlns="http://www.w3.org/2000/svg">
    <rect x="10" y="10" width="320" height="180" rx="12" fill="#F2F2F2"/>
    <text x="30" y="50" font-size="14" font-weight="bold" fill="#059669">标签</text>
    <text x="30" y="80" font-size="18" font-weight="bold" fill="#1A1A1A">标题</text>
    <text x="30" y="110" font-size="13" fill="#4A4A4A">内容描述</text>
  </svg>
</section>
```

---

## 六、微信编辑器特殊行为

### 6.1 样式覆盖

微信编辑器会自动覆盖某些样式：

| 行为 | 说明 |
|------|------|
| `<p>` 默认margin | 微信会设置默认margin，需要显式覆盖 |
| `<h1>` ~ `<h6>` | 默认样式可能与预期不同，建议全内联 |
| `<a>` 颜色 | 微信可能覆盖链接颜色，需显式设置color |
| `<table>` 默认样式 | 需要显式设置border-collapse和间距 |
| 行内空白 | 连续空白字符可能被合并 |

### 6.2 复制粘贴行为

1. **从浏览器复制粘贴到微信编辑器**：
   - 内联样式会被保留
   - `<style>`标签内容会被过滤
   - `<script>`标签会被过滤
   - `class`和`id`会被过滤
   - 外部图片可能无法加载

2. **从微信编辑器复制粘贴**：
   - 会丢失部分样式
   - 图片链接会保留
   - 布局可能错乱

### 6.3 安全过滤

微信会过滤以下内容：

- JavaScript代码（包括onclick等事件）
- 外部链接跳转（仅支持微信认证域名）
- iframe嵌入
- 表单元素
- 自定义数据属性
- CSS表达式
- URL中的特殊字符

---

## 七、最佳实践清单

### 7.1 DO（推荐做法）

- [x] 所有样式写在 `style` 属性中
- [x] 使用 `<section>` 作为块级容器
- [x] 使用 `<span>` 作为行内容器
- [x] 图片使用微信域名URL
- [x] `<img>` 添加 `display:block` 消除底部间隙
- [x] SVG设置 `viewBox` 和 `width:100%`
- [x] 使用 `display:flex` 布局
- [x] 显式设置所有文字的 `font-size` 和 `color`
- [x] 显式设置所有元素的 `margin` 和 `padding`
- [x] 测试时使用375px宽度的视口

### 7.2 DON'T（禁止做法）

- [ ] 不使用 `<style>` 标签
- [ ] 不使用 `class` 或 `id` 属性
- [ ] 不使用 `position` 属性
- [ ] 不使用 `animation` 或 `transition`
- [ ] 不使用 `transform`
- [ ] 不使用 `float`（不稳定）
- [ ] 不使用伪元素 `::before/::after`
- [ ] 不使用 `calc()` 或 `var()`
- [ ] 不使用外部图片URL
- [ ] 不使用 `<script>` 标签
- [ ] 不使用 `<iframe>` 标签
- [ ] 不使用 `data-*` 属性
- [ ] 不使用 SVG SMIL 动画
- [ ] 不使用 `gradient` 渐变（被过滤）
- [ ] 不依赖 `box-shadow`（不稳定）

---

## 八、兼容性测试方法

### 8.1 基础测试流程

1. 在浏览器中预览（375px宽度）
2. 全选文章HTML，复制
3. 在微信公众号后台编辑器中粘贴
4. 检查所有样式是否正确
5. 在手机端预览确认

### 8.2 常见问题排查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 样式丢失 | 使用了class/style标签 | 改为全内联 |
| 布局错乱 | 使用了float/position | 改用flex |
| 图片不显示 | 使用了外部URL | 上传到微信图片服务器 |
| SVG空白 | 缺少viewBox | 添加viewBox属性 |
| 字体不对 | 使用了自定义字体 | 使用系统字体 |
| 间距异常 | 微信默认margin覆盖 | 显式设置margin:0 |
| 圆角丢失 | border-radius被过滤 | 通常不会，检查语法 |
| 渐变消失 | gradient被过滤 | 用纯色替代 |
