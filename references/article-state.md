# ArticleState 与节点契约

`ArticleState` 是长文流程唯一状态源。节点之间不得只靠对话记忆传递事实。

七个节点依次为 `intent`、`topic`、`research`、`strategy`、`draft`、`review`、`delivery`。节点状态为 `pending`、`running`、`awaiting_host`、`passed`、`blocked` 或 `failed`。

每个节点读取前置字段，做当前决策，写入声明字段，运行确定性门禁并记录显式降级。宿主模型缺少的关键材料不得静默生成。

```powershell
python -m toolkit.cli article init "写一篇关于本地小店变化的文章" --audience "本地生活读者" --goal "建立信任"
python -m toolkit.cli article run article-state.json
python -m toolkit.cli article resume article-state.json intent intent-result.json
python -m toolkit.cli article status article-state.json
```

退出码：`0` 完成，`1` 阻塞或失败，`2` 等待宿主模型结构化结果。
