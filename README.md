# weChat-autoCreate 2.0

微信公众号长文与贴图号 Skill。2.0 将长文从一份庞大的 8 步提示词改成可保存、可恢复、可检查的 7 节点状态机。

## 长文流程

```text
需求建模 → 选题与角度 → 研究与证据 → 框架与策略 → 一次成稿 → 读者模拟与局部修订 → 视觉排版与交付
```

状态文件保存用户目标、读者、作者画像、来源、主张、大纲、正文、修订、视觉和交付结果。宿主模型只处理当前节点的结构化请求；Python 负责状态、失败、证据边界和质量门禁。

```powershell
python -m toolkit.cli article init "写一篇关于本地老店关闭的公众号文章" --audience "本地生活读者" --goal "解释变化"
python -m toolkit.cli article run article-state.json
python -m toolkit.cli article status article-state.json
```

`article run` 返回退出码 2 时，把输出的 `request` 交给当前宿主模型，将其 JSON 保存后执行：

```powershell
python -m toolkit.cli article resume article-state.json intent intent-result.json
python -m toolkit.cli article run article-state.json
```

## 已有文章

```powershell
python -m toolkit.cli recommendation-check article.md --strict
python -m toolkit.cli preview article.md
python scripts/layout_quality_check.py article_preview.html
python scripts/wechat_compliance_check.py article_preview.html
```

预览支持复制 HTML 到公众号编辑器。草稿箱写入需要微信公众号凭证和明确执行意图：

```powershell
python -m toolkit.cli publish article.md
```

## Benchmark

```powershell
python -m toolkit.cli benchmark --old-dir tests/benchmarks/baseline --new-dir tests/benchmarks/candidate --output benchmark-report.json
```

自动指标只比较具体信息、来源标记、重复和少量模板信号。阅读欲望、作者感和洞察需要盲序 LLM Judge 与人工抽检。

## 贴图号

贴图号保持独立的策划、试生成、批量生成、预览、质量检查和发布审批状态：

```powershell
python -m toolkit.cli tie-tu plan --industry "本地生活" --topic "街区变化" --content-type city_change
```

## 验证

```powershell
python -m unittest discover -s tests -v
python scripts/source_lint.py
python D:/Download/codex/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
```

项目采用 MIT License。任何评分都不代表微信官方推荐、审核或实际传播结果。
