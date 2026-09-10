---
name: wechat-publisher-ultimate
description: 把主题或素材推进为可信、可读、可排版交付的微信公众号长文；支持结构化研究、作者风格、质量复核、预览和草稿箱交付。已有文章可直接改稿或排版；贴图号走独立流程。
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - WebSearch
  - WebFetch
---

# WeChat Publisher Ultimate 2.0

把主题、材料和目标变成一篇有作者判断、有可靠证据、适合微信移动端阅读的文章。第一次成稿就使用作者、读者、证据和观点约束；写后只诊断并局部修复，不先生产模板文再全文“去 AI”。

## 路由

- 从主题开始：走 7 节点长文流程，先读 [ArticleState 协议](references/article-state.md)。
- 已有文章，只需改稿：读 [质量协议](references/quality-protocol.md) 和 [写作协议](references/writing-protocol.md)。
- 已有 Markdown，只需排版或入草稿箱：读 [移动端排版](references/mobile-layout-quality.md)、[leaf 与合规](references/leaf-and-compliance.md) 和 [命令](references/commands.md)。
- 微信贴图号、小绿书图片帖：读 [贴图号流程](references/tie-tu-workflow.md)，不要混入长文状态。
- 学习历史文章：读 [作者模型](references/author-model.md)。不得把推断写成作者经历。

## 长文状态机

```text
需求建模 → 选题与角度 → 研究与证据 → 框架与策略 → 一次成稿 → 读者模拟与局部修订 → 视觉排版与交付
```

用 `python -m toolkit.cli article init ...` 创建状态，随后运行 `article run`。节点返回 `awaiting_host` 时，只读取请求中列出的 reference，把 JSON 结果通过 `article resume` 合并后继续。不要一次加载所有参考文件。

运行模式：`auto` 自动推进到等待、阻塞或完成；`interactive` 是默认模式；`step` 只运行指定节点。

## 不可破坏的边界

- 区分用户材料、作者经历、公开事实、案例、观点、推断和假设场景。未核验材料不能写成确定事实。
- 时效性内容研究失败时阻塞。普通观点文可降级，但必须记录限制并告知用户。
- 不编造来源、数字、测试经历、作者身份、产品体验或发布效果。
- Humanizer 只做定位和局部修复；不得故意制造语病、逻辑跳跃、随机情绪或虚假细节。
- SEO 只在目标包含搜索获取时启用，不能破坏标题兑现和阅读体验。
- 图片必须有明确角色和来源。没有解释、证据、场景或情绪作用的图片不生成。
- `preview` 与 `publish` 必须通过推荐质量和微信合规门禁。API 草稿箱操作需要真实凭证和用户明确意图。

## 交付

至少交付文章 Markdown、来源与限制、质量报告、视觉计划和可复制预览。启发式评分不得描述成微信推荐概率、阅读量预测或发布证明。
