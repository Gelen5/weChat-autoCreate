# 命令

## 2.0 长文

- `article init REQUEST`：创建 ArticleState。
- `article run STATE`：推进到完成、硬阻塞或等待宿主。
- `article step STATE NODE`：运行一个节点。
- `article resume STATE NODE RESULT.json`：合并宿主 JSON。
- `article status STATE`：查看节点、降级和交付结果。
- `benchmark --old-dir DIR --new-dir DIR`：比较固定任务输出。

## 兼容命令

- `brief FILE`：从已有文章生成旧版 ContentBrief。
- `recommendation-check FILE --strict`：运行推荐质量门禁。
- `preview FILE`：生成可复制预览。
- `publish FILE`：写入草稿箱；需要凭证。
- `themes`、`learn-theme`：查看或学习排版主题。
- `tie-tu ...`：独立贴图号流程。

完整参数以 `python -m toolkit.cli --help` 和子命令 `--help` 为准，文档不维护不存在的斜杠命令。
