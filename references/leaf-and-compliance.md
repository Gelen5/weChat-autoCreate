# Leaf 包裹铁律 + 合规校验说明

> 配套工具：`scripts/wechat_compliance_check.py`
> 本文档只讲**为什么**和**怎么写**；完整标签/CSS 支持清单见 `wechat-html-spec.md`。

---

## 一、为什么要 leaf 包裹

公众号编辑器在保存和重新打开文章时，会**重写它不认识的节点结构**。最典型的症状是：

- 排版时看着好好的，粘贴进编辑器一保存，内联样式整片消失；
- 同一段文字里，前面几个字是金色、后面变回默认色；
- 加粗/高亮在预览里有，发出去没了。

根因是：**孤立的中文文本节点没有被显式标记为"叶子"**，编辑器把它当成可合并的临时文本，重建 DOM 时丢掉了挂在父级或自身上的 style。

**解法**：所有含中文的文本节点，外套一层 `<span leaf="">`。

```html
<!-- ❌ 裸文本节点：保存后样式可能蒸发 -->
<p style="font-size:15px;color:#6E6E73;">这是正文内容。</p>

<!-- ✅ 叶子包裹：编辑器把它当稳定节点保留 -->
<p style="font-size:15px;color:#6E6E73;"><span leaf="">这是正文内容。</span></p>
```

### 包裹的判定规则

| 位置 | 要不要包 | 说明 |
|------|----------|------|
| 任意含中文的文本节点 | **必须包** | 包括 `<p>`、`<h1>`-`<h6>`、`<span>`、`<strong>`、`<section>` 里的文字 |
| 装饰性空元素 | **必须包** | 见下方「空元素占位」 |
| `<svg>` 内部 `<text>` | 不需要 | 校验器自动豁免 |
| 代码块内部 | 不需要（但建议包） | 校验器按 `monospace`/`consolas`/`white-space:pre` 识别并豁免标点检查；包了更保险 |
| 纯数字/英文节点 | 不需要 | 无中文则无风险 |

**嵌套时包一层就够**：祖先链上任意一级有 `leaf` 属性即算通过，不必每层都包。

```html

<section style="background:#F7F7F5;">
  <p style="margin:0;"><span leaf="">重点内容</span></p>
</section>
```

### 空元素占位

只有装饰作用、不含文字的元素（分隔线、色块、留白），微信会当成空标签清掉。必须塞一个空的 leaf 占位：

```html

<section style="margin:24px 0;text-align:center;">
  <span leaf=""><br></span>
  <section style="display:inline-block;width:40px;height:1px;background:#E5E5E5;"></section>
</section>
```

---

## 二、微信编辑器的隐形坑

这几条不在"标签支持清单"里，但踩中必翻车，是实测积累的。

### 2.1 不要在 `<strong>` 上打 `font-size`

编辑器会"纠正"它认为不合理的嵌套，把样式重写掉。

```html
<!-- ❌ 同一段混多个 font-size，且 font-size 挂在 strong 上 -->
<p style="font-size:15px;">
  这是正文，<strong style="font-size:18px;color:#C9A962;">这是强调</strong>，又回到正文。
</p>

<!-- ✅ 拆成多个 <p>，高亮挂在外层 <span> -->
<p style="font-size:15px;margin:0 0 8px 0;"><span leaf="">这是正文，</span></p>
<p style="font-size:18px;margin:0 0 8px 0;color:#C9A962;font-weight:bold;">
  <span leaf="">这是强调</span>
</p>
<p style="font-size:15px;margin:0;"><span leaf="">又回到正文。</span></p>
```

**规则：一个 `<p>` 只用一个字号。**

### 2.2 不用 `position:absolute` 做划线或高亮

删除线用 `text-decoration:line-through`，高亮用背景色。

```html
<span style="text-decoration:line-through;"><span leaf="">原价 199</span></span>
```

### 2.3 代码块不用 `white-space:pre`

会把 HTML 源码的缩进和换行渲染成一大片左缩进 + 空行。改成每行一个 `<p style="margin:0">`，缩进用**全角空格**。

```html
<section style="background:#2D2D2D;border-radius:8px;padding:16px;font-family:monospace;">
  <p style="margin:0;color:#E5E5E5;font-size:13px;"><span leaf="">function hello() {</span></p>
  <p style="margin:0;color:#E5E5E5;font-size:13px;"><span leaf="">　　console.log("hi");</span></p>
  <p style="margin:0;color:#E5E5E5;font-size:13px;"><span leaf="">}</span></p>
</section>
```

### 2.4 图片用 `max-width`，不用 `width:100%`

`width:100%` 会把小图强行拉伸变糊。

```html
<img src="https://mmbiz.qpic.cn/..." style="max-width:100%;height:auto;display:block;margin:0 auto;" />
```

> ⚠️ 本 skill 的 `wechat-html-spec.md:253` 曾建议 `width:100%`，与本条冲突。
> 现以本条为准：`max-width:100%` 更稳。校验器对 `width:100%` 报 `img_width_100`（可放行）。

---

## 三、半角标点

中文正文里混半角 `,;!?` 是最常见的人工返工项。统一用全角 `，。；！？`。

**豁免**：代码块、`<svg>` 内部。校验器自动识别，不会误报。

---

## 四、校验器使用

```bash
# 常规检查（有阻塞项则退出码 1）
python scripts/wechat_compliance_check.py article.html

# JSON 输出，便于 CI 消费
python scripts/wechat_compliance_check.py article.html --format json

# 基线模式：只出报告，永不失败（审计存量文章用）
python scripts/wechat_compliance_check.py article.html --baseline

# 放行某个可放行项（会写入 .cache/wechat_compliance_allowance.json 留痕）
python scripts/wechat_compliance_check.py article.html --allow css_gap
```

### 严重度分级

| 级别 | 含义 | 能否放行 | 典型项 |
|------|------|----------|--------|
| `error` | 微信确定会过滤/破坏 | ❌ 否 | `css_grid`、`css_position`、`css_var`、`@media`、`style_tag` |
| `warn_blocking` | 会导致交付事故 | ❌ 否 | `leaf_missing_all`、`leaf_missing_partial`、`image_host_not_wechat` |
| `warn_allowable` | 不稳定或存在争议，人工确认后可放行 | ✅ 是 | `css_gap`、`css_float`、`css_box_shadow`、`halfwidth_punct`、`div_tag` |
| `info` | 提示，不影响交付 | — | `data_attr`、`table_layout_suspect` |

### 与 `layout_quality_check.py` 的分工

| 脚本 | 性质 | 判什么 |
|------|------|--------|
| `wechat_compliance_check.py` | **确定性** | 平台合规：标签/CSS 是否被过滤、leaf 是否包裹、图片域名、标点 |
| `layout_quality_check.py` | **启发式** | 阅读质量：手动换行、装饰过载、短尾标题、碎片强调、图注缺失 |

**两个都要跑。** 前者保证"发出去不崩"，后者保证"手机上好读"。

---

## 五、争议项：待实测确认

| 项 | 我方规范 | gzh-design | 当前处理 |
|----|----------|-----------|----------|
| `gap` | `wechat-html-spec.md:165` 列为支持 | `theme-generator.md:283` 明确禁用 | 报 `css_gap`（WARN，可放行）。**需实测一篇带 flex+gap 的文章确认** |
| `linear-gradient` | `wechat-html-spec.md:194` 说被过滤 | Patrick 版 spec-02 说安全 | 报 `css_gradient`（WARN，可放行） |
| `table/ul/ol/blockquote` | 我方列为支持 | Patrick 版禁用（只用 7 个标签） | 不报错；仅当 table 疑似用作布局骨架时报 `table_layout_suspect`（INFO） |

**实测方法**：把带该特性的 HTML 粘进公众号编辑器 → 保存 → 手机预览 → 对比。结果回填本表并调整规则级别。
