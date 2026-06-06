# 微信平台限制（开发参考）

## HTML/CSS 限制

### 禁止
- `<style>` 标签：所有样式必须内联
- `class` 属性：会被过滤
- `id` 属性：会被过滤
- `<script>` 及任何 JavaScript
- `<iframe>`, `<object>`, `<embed>`, `<form>`, `<input>`
- `position: fixed/absolute/sticky`
- `z-index`
- `@media` 媒体查询
- `@keyframes` / `animation` / `transition`
- `transform`
- `float`
- `::before` / `::after` 伪元素

### 支持的 HTML 标签
`p`, `h1`-`h6`, `strong`, `b`, `em`, `i`, `u`, `span`, `br`, `ul`, `ol`, `li`, `div`, `section`, `a`, `img`, `table`, `thead`, `tbody`, `tr`, `th`, `td`, `blockquote`, `pre`, `code`, `hr`

### 支持的 CSS 属性
- 文字：`font-size`, `font-weight`, `font-family`, `color`, `line-height`, `letter-spacing`, `text-align`, `text-decoration`, `text-indent`
- 盒模型：`margin`, `padding`, `background`, `background-color`, `border`, `border-radius`, `box-shadow`
- 布局：`display`（block/inline/inline-block/flex）, `overflow`, `width`, `max-width`, `height`
- 其他：`opacity`, `vertical-align`, `white-space`, `word-break`

## 图片限制

- 正文图片必须是微信域名 URL（`mmbiz.qpic.cn`）
- base64 图片在复制粘贴时会被微信自动收图转为微信域名
- 外链图片不渲染
- 单张正文图片限 1MB
- 封面图限 10MB（永久素材）
- SVG：支持内联静态 SVG，SMIL 动画被 `draft/add` 接口过滤

## 代码块限制

- 只能用内联样式模拟
- 推荐用 `background-color` + `border-radius` + `padding` + `font-family: monospace`

## 表格限制

- 支持基本表格，但样式有限
- 不支持合并单元格
- 推荐用 CSS Grid/Flex 布局模拟复杂表格

## 链接限制

- 外链在公众号内不跳转
- 推荐转为脚注格式（上标编号 + 文末参考链接）

## 草稿箱 API

- `draft/add` 需要**已认证**服务号/订阅号
- 个人订阅号通常没有此权限
- 需要配置 IP 白名单
- access_token 有效期 7200 秒，建议缓存
