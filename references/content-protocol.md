# 统一内容协议

长文和微信贴图号共享四个底层对象，但不共享渲染器和发布器：

```text
ContentBrief   任务目标、受众、交付物、事实边界和约束
SourceLedger   来源、证据、授权和可追溯状态
QualityGate    必须通过的检查项、结果和问题
ApprovalState  选题、方案、试生成、批量生成、预览和发布状态
```

贴图号额外使用 `GenerationState` 管理第一张试生成和批量生成；长文可以通过：

```bash
python -m toolkit.cli brief article.md --output article.brief.json
```

生成统一 `ContentBrief`。协议只描述内容生产状态，不替换长文转换器、公众号发布器或贴图号渲染器。

## 事实边界

- 用户提供的材料标记为 `provided`。
- 公开网页需要来源 URL 和核验状态。
- AI 生成的案例只能标记为 `illustrative`，不得伪装成真实经历。
- 未确认的信息进入 `unverified`，不能在正文中写成确定事实。
- 用户素材、参考图片和第三方图片需要记录使用权限或授权说明。

## 状态顺序

```text
topic → brief → card_plan → pilot_image → batch_generation → preview → publish
```

长文默认在生成 Brief 时确认 `brief`；贴图号在方案、试图、批量生成和发布前保留人工确认点。
