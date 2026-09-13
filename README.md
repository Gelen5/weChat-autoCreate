# 宇宙第一公众号skill 2.0

> 微信公众号长文与贴图号生成 Skill。从一个主题，到一篇有作者判断、证据可靠、排版过关的公众号文章，再到草稿箱。

![Version](https://img.shields.io/badge/version-2.1.0-002FA7) ![License](https://img.shields.io/badge/license-MIT-green) ![Python](https://img.shields.io/badge/python-3.10%2B-blue)

## 这是什么

**宇宙第一公众号skill**（内部名 `wechat-publisher-ultimate`）是一条完整的公众号内容生产流水线：

- **长文流程**：把主题、材料和目标推进为可交付的公众号长文，支持结构化研究、作者风格、质量复核、预览和草稿箱交付
- **贴图号流程**：小绿书图片帖的策划、试生成、批量生成、预览、质量检查和发布审批，独立状态管理
- **已有文章**：直接改稿、排版或入草稿箱

2.0 的核心变化：把长文从一份庞大的 8 步提示词，改成**可保存、可恢复、可检查的 7 节点状态机**。状态由 Python 管理，宿主模型只处理当前节点的结构化请求。

## 长文状态机

```text
需求建模 → 选题与角度 → 研究与证据 → 框架与策略 → 一次成稿 → 读者模拟与局部修订 → 视觉排版与交付
```

状态文件保存用户目标、读者、作者画像、来源、主张、大纲、正文、修订、视觉和交付结果。运行模式：

| 模式 | 行为 |
|------|------|
| `auto` | 自动推进到等待、阻塞或完成 |
| `interactive` | 默认模式，逐节点确认 |
| `step` | 只运行指定节点 |

### 快速开始

```bash
# 1. 初始化一篇长文
python -m toolkit.cli article init "写一篇关于本地老店关闭的公众号文章" \
    --audience "本地生活读者" --goal "解释变化"

# 2. 运行流水线
python -m toolkit.cli article run article-state.json

# 3. 查看进度
python -m toolkit.cli article status article-state.json
```

当 `article run` 返回退出码 2 时，说明某个节点需要宿主模型介入：把输出的 `request` 交给模型，将返回的 JSON 保存后合并，继续运行。

```bash
python -m toolkit.cli article resume article-state.json intent intent-result.json
python -m toolkit.cli article run article-state.json
```

## 已有文章

改稿、排版、入草稿箱，都有对应的门禁检查：

```bash
# 推荐质量检查（strict 模式不通过则阻断发布）
python -m toolkit.cli recommendation-check article.md --strict

# 生成可复制到公众号编辑器的 HTML 预览
python -m toolkit.cli preview article.md

# 排版质量 + 微信合规检查
python scripts/layout_quality_check.py article_preview.html
python scripts/wechat_compliance_check.py article_preview.html

# 写入草稿箱（需要微信公众号凭证和明确执行意图）
python -m toolkit.cli publish article.md
```

## 贴图号流程

贴图号与小绿书图片帖走独立状态，不与长文混用：

```bash
python -m toolkit.cli tie-tu plan --industry "本地生活" --topic "街区变化" --content-type city_change
```

完整覆盖策划 → 试生成 → 批量生成 → 预览 → 质量检查 → 发布审批，内置人像封面路由与图片反向校验。

## Benchmark

```bash
python -m toolkit.cli benchmark --old-dir tests/benchmarks/baseline \
    --new-dir tests/benchmarks/candidate --output benchmark-report.json
```

自动指标只比较具体信息、来源标记、重复和少量模板信号。阅读欲望、作者感和洞察需要盲序 LLM Judge 与人工抽检，任何评分都不代表真实传播结果。

## 能力一览

| 模块 | 说明 |
|------|------|
| `toolkit/article_*` | 7 节点长文状态机与质量协议 |
| `toolkit/tie_tu/` | 贴图号全流程（策划/生成/人像/校验/发布） |
| `toolkit/publisher.py` | 草稿箱写入与修复 |
| `toolkit/benchmark.py` | 新旧版本文章质量对比 |
| `toolkit/content_quality.py` | 推荐质量门禁 |
| `personas/` | 14 种作者人格（深夜朋友、锋利记者、行业 Insider 等） |
| `prompts/` | Humanizer 与微信排版提示词 |
| `references/` | 30+ 份参考协议（证据边界、合规、移动端排版、风格模板等） |

## 不可破坏的边界

- 区分用户材料、作者经历、公开事实、案例、观点、推断和假设场景。未核验材料不能写成确定事实
- 时效性内容研究失败时阻塞；普通观点文可降级，但必须记录限制并告知用户
- 不编造来源、数字、测试经历、作者身份、产品体验或发布效果
- Humanizer 只做定位和局部修复，不故意制造语病、逻辑跳跃或虚假细节
- 图片必须有明确角色和来源，没有作用的图片不生成
- `preview` 与 `publish` 必须通过推荐质量和微信合规门禁

## 测试

```bash
python -m unittest discover -s tests -v
python scripts/source_lint.py
```

## License

MIT。本项目与微信官方无关，任何评分不代表微信推荐、审核或实际传播结果。
