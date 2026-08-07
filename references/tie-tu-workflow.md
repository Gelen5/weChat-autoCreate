# 微信贴图号独立工作流

贴图号是图片主导的独立内容分支，不复用公众号长文的正文排版链路。

## 触发

`贴图号`、`贴图`、`小绿书`、`图文笔记`、`图片消息`。

## 交互顺序

1. 接收行业、主题或标题。
2. 研究热点，并把候选选题按相关性、时效性、可视化程度排序。
3. 推荐教程步骤型、前后对比型、清单推荐型、行业观点型、城市变化型、情绪故事型中的一种或多种。
4. 生成 `card_plan.json`，每张卡片只保留一个视觉重点。
5. 等用户确认选题和图片方案。
6. 获取用户图、公开来源图片或生成 AI 底图。
7. 统一裁切 3:4，并在本地叠加文字。
8. 验证图片、文字安全区、来源和短文案。
9. 输出手机预览 HTML。
10. 用户明确同意后才调用贴图号草稿发布器。

## 与长文流程的边界

- 长文继续使用 `Publisher.publish` 和原有 `[1/8]-[8/8]` 流程。
- 贴图号使用 `toolkit/tie_tu/` 和 `TieTuPublisher`。
- 贴图号发布使用 `add_draft_multi`，不调用长文发布方法。
- 贴图号的 `card_plan.json`、预览 HTML 和图片来源可以单独归档。

## 内容类型

| ID | 中文名 | 推荐卡片结构 |
|---|---|---|
| `tutorial` | 教程步骤型 | 封面 → 问题 → 步骤 → 步骤 → 总结 |
| `before_after` | 前后对比型 | 封面 → 过去 → 现在 → 对照 → 余味 |
| `list` | 清单推荐型 | 封面 → 清单项 → 清单项 → 清单项 → 总结 |
| `industry_view` | 行业观点型 | 封面 → 现象 → 证据 → 判断 → 结论 |
| `city_change` | 城市变化型 | 封面 → 旧景 → 今景 → 对比 → 记忆 |
| `emotional_story` | 情绪故事型 | 封面 → 场景 → 细节 → 转折 → 结尾 |

默认图片数量为 5 张，至少 1 张，不设置上限；默认比例为 3:4。

## 人像增强分支

当行业、主题、标题、风格或卡片视觉主体包含人像、美女、模特、写真、穿搭、妆容、复古女性等意图时，`portrait_mode=auto` 会自动启用独立的人像增强层。它不会改变长文流程，也不会替换贴图号的卡片结构。

增强层会为整组卡片生成 `model_bible`，并为每张卡片生成 `portrait_spec`，包含人物身份、年龄边界、路线、姿态、表情、镜头、光线、材质和负面提示词，重点保持多张图片中的同一虚构成年模特一致。

支持：

```bash
python -m toolkit.cli tie-tu plan --industry "生活方式" --topic "复古美女旧时光" --count 5 --portrait-mode auto --output card_plan.json
python -m toolkit.cli tie-tu validate card_plan.json
```

需要关闭时使用 `--portrait-mode off`；需要对没有明显关键词的主题强制使用时使用 `--portrait-mode required`。图片生成器应读取每张卡片的 `portrait_spec`，中文文字继续由贴图号渲染器后期叠加，不交给图片模型生成。

## 状态、来源与生成

每个计划都包含统一的 `ContentBrief`、`SourceLedger`、`ApprovalState`、`QualityGate`，并额外记录 `GenerationState`。来源可以通过 CLI 补充：

```bash
python -m toolkit.cli tie-tu source card_plan.json --source-id source-1 --kind web --title "来源标题" --url "https://example.com" --status verified
python -m toolkit.cli tie-tu approve card_plan.json --stage card_plan --status approved
python -m toolkit.cli tie-tu pilot card_plan.json --image ./assets/pilot.png
python -m toolkit.cli tie-tu batch card_plan.json --output-dir ./output/tie-tu
python -m toolkit.cli tie-tu status card_plan.json
```

`pilot` 可以记录已有试生成图片，也可以在配置图片提供商后调用现有 `ImageGenerator`；`batch` 只生成尚未有图片路径的卡片。所有生成方式、来源和审批状态都会写回 `card_plan.json`。
