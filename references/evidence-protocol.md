# EvidencePack 协议

来源账本记录来源，主张账本记录文章准备表达的内容，两者通过 `source_ids` 连接。

主张类型：`fact`、`author_experience`、`public_case`、`opinion`、`inference`、`hypothetical`。状态：`verified`、`user_provided`、`illustrative`、`unverified`、`rejected`。

- 关键事实和公开案例必须有可追溯来源。
- 作者经历只能来自用户明确提供或授权的材料。
- 推断保留条件与不确定性；假设场景要明确标记。
- 时效性事实优先当前一手来源，重要结论尽量交叉核验。
- 搜索失败记录为 `failed` 或 `partial`，不得用模型记忆伪装搜索结果。

医疗、财经、法律、教育政策等高风险内容提高来源强度，并保留日期、适用范围和限制。
