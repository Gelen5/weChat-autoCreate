# 非管道命令调度表

以下命令不触发8步全链路管道，而是执行特定功能。

| 触发词 | 动作 | 脚本/文件 |
|--------|------|----------|
| 重新设置风格 / 重新onboard | 重新运行 Onboard 流程 | references/onboard.md |
| 学习我的修改 | 运行 learn_edits.py，对比初稿+终稿 | scripts/learn_edits.py |
| 学习排版 | 运行 learn_theme.py，从URL提取排版主题 | scripts/learn_theme.py |
| 导入范文 / 学习这篇文章 | 运行 extract_exemplar.py，提取范文风格 | scripts/extract_exemplar.py |
| 查看范文库 | 列出 corpus/ 目录和 exemplars/index.yaml | — |
| 看看文章数据 / 数据复盘 | 运行 fetch_stats.py + 效果复盘 | scripts/fetch_stats.py + references/effect-review.md |
| 主题画廊 / 排版主题 | 列出所有可用主题及描述 | references/style-template.md |
| 小绿书 / 图片帖子 | 运行 image-post 流程 | toolkit/publisher.py |
| 诊断检查 / 检查一下 | 运行 diagnose.py，生成配置完备度报告 | scripts/diagnose.py |
| 更新 / git pull | 从远程拉取最新版本 | git pull |
| 去AI痕迹 / humanize | 运行 Humanizer 流程 | prompts/humanizer-base.md |
| 生成封面 | 运行图片生成流程 | scripts/imagegen.ts |
| 生成信息图 | 运行SVG信息图生成流程 | references/components.md |
