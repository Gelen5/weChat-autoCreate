# 微信公众号 HTML 排版规范（speedref）

`publish.ts` 的渲染器（`render.ts`）已按此规范产出合规 HTML。改主题时务必遵守。

## 核心原则

微信编辑器有白名单过滤机制。**所有样式必须写成元素的 `style` 内联属性。**

- `<style>` 标签、`<link>` 外部样式表、`class` 选择器、`id` 选择器 —— 全部失效。
- 不能用任何 JavaScript（`<script>` 被剔除）。

## 标签支持

- ✅ `<p> <h1>~<h6> <strong> <b> <em> <i> <u> <span> <br> <ul> <ol> <li> <div> <section> <a> <img> <table> <tr> <td> <th> <blockquote> <pre> <code> <hr>`
- ❌ `<script> <iframe> <object> <embed> <form> <input>`

## CSS 属性

- ✅ `font-size color font-weight font-style line-height letter-spacing text-align text-decoration text-indent margin padding width height max-width background background-color border border-radius box-shadow opacity display(block/inline-block) vertical-align overflow`
- ❌ `position`（连同 `z-index` 一起失效）、`@media`、`@keyframes`/`animation`、`transform`（不稳定）。`float` 在折叠长图文里有坑。

## 图片

- 正文 `<img>` 的 `src` 必须是微信域名 URL（`mmbiz.qpic.cn`）。base64、外链都不渲染。
- `publish.ts` 已自动处理：本地文件 / 远程 URL / base64 → 调 `media/uploadimg` 上传 → 替换 src。
- `media/uploadimg` 限制：单张 ≤1MB，jpg/png/gif。封面走 `material/add_material`，≤10MB。

## 排版数值（内置默认主题）

- 正文 15px / 行高 1.8 / 字间距 0.5px / 颜色 `#3f3f3f`
- 大标题 H1 20px/800、小标题 H2 16px/700（左侧绿色色条）、H3 15px/700
- 辅助文字（引用块 / 表格 / 代码）13px
- 所有文字块段前段后距 8px
- 主题色 `#07c160`（微信绿）

## SVG 互动（本 skill 暂不含）

公众号互动靠 SVG SMIL 动画（`<animate>` `<animateTransform>`，`begin="click"`）。
draft/add 接口会过滤掉 SVG 动画 —— 互动效果只能走「浏览器注入编辑器」路线，无法走 API。属于后续版本。
