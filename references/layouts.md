# :::module 排版模块参考

## 概述

:::module 是一种结构化排版语法，在 Markdown 中嵌入排版组件声明。每个模块有特定的 body_format（fields/rows/json_object/json_array），由排版引擎渲染为微信兼容的 HTML。

## 模块分类（30 个精选模块）

### Opening（开篇类）— 帮读者判断是否值得读

#### hero
- **body_format**: fields
- **when_to_use**: 需要强力开场，首屏就抓住注意力
- **when_not_to_use**: 文章已以故事开头
- **markdown 示例**:
```markdown
:::hero
eyebrow: 深度解析
title: GPT-5 发布后的 72 小时
subtitle: 一切都变了，又好像什么都没变
:::
```

#### toc
- **body_format**: rows
- **when_to_use**: 长文（>2000字），帮助读者导航
- **markdown 示例**:
```markdown
:::toc
01 | 发生了什么 | 3分钟前还在传谣
02 | 关键变化 | 5个你必须知道的点
03 | 实际影响 | 对普通用户意味着什么
:::
```

#### cards
- **body_format**: json_array
- **when_to_use**: 多个并列要点需要同时展示
- **markdown 示例**:
```markdown
:::cards
[{"title": "速度提升", "desc": "响应速度提升3倍"}, {"title": "成本降低", "desc": "API价格下降60%"}, {"title": "多模态", "desc": "原生支持图片+音频"}]
:::
```

#### part
- **body_format**: fields
- **when_to_use**: 文章分Part，需要明确的分隔标识
- **markdown 示例**:
```markdown
:::part
number: "02"
title: 深入机制
:::
```

#### label-title
- **body_format**: fields
- **when_to_use**: 章节标题需要标签+标题组合
- **markdown 示例**:
```markdown
:::label-title
label: 核心观点
title: 不只是更快，而是不同的思考方式
:::
```

### Evidence（证据类）— 让内容可信

#### quote
- **body_format**: fields
- **when_to_use**: 需要引用名人/官方/数据
- **markdown 示例**:
```markdown
:::quote
text: AI不会取代你，但会用AI的人会。
author: 李开复
source: 《AI·未来》
:::
```

#### image-text
- **body_format**: fields
- **when_to_use**: 图文混排，图片配文字说明
- **markdown 示例**:
```markdown
:::image-text
image: https://example.com/photo.jpg
caption: GPT-5 发布会现场
text: OpenAI 在旧金山总部举行了发布会
:::
```

#### image-steps
- **body_format**: json_array
- **when_to_use**: 需要步骤图示+文字说明
- **markdown 示例**:
```markdown
:::image-steps
[{"step": 1, "title": "获取API Key", "desc": "在OpenAI后台创建"}, {"step": 2, "title": "配置环境", "desc": "设置环境变量"}]
:::
```

#### image-compare
- **body_format**: json_object
- **when_to_use**: 两张图片对比
- **markdown 示例**:
```markdown
:::image-compare
{"left_image": "url_a.jpg", "left_label": "优化前", "right_image": "url_b.jpg", "right_label": "优化后"}
:::
```

#### image-annotate
- **body_format**: fields
- **when_to_use**: 图片需要标注说明
- **markdown 示例**:
```markdown
:::image-annotate
image: screenshot.png
annotation: 红框部分是新增加的设置项
:::
```

### Infographic（信息图类）— 让信息可消化

#### metrics
- **body_format**: json_array
- **when_to_use**: 展示关键指标数据
- **markdown 示例**:
```markdown
:::metrics
[{"label": "速度提升", "value": "3x", "trend": "up"}, {"label": "成本降低", "value": "60%", "trend": "down"}, {"label": "准确率", "value": "97%", "trend": "up"}]
:::
```

#### compare
- **body_format**: json_array
- **when_to_use**: 两项或多维对比
- **markdown 示例**:
```markdown
:::compare
[{"name": "GPT-4", "speed": "1x", "cost": "$0.03"}, {"name": "GPT-5", "speed": "3x", "cost": "$0.01"}]
:::
```

#### steps
- **body_format**: json_array
- **when_to_use**: 流程/步骤展示
- **markdown 示例**:
```markdown
:::steps
[{"step": 1, "title": "安装", "desc": "npm install -g tool"}, {"step": 2, "title": "配置", "desc": "编辑 config.yaml"}, {"step": 3, "title": "运行", "desc": "tool run"}]
:::
```

#### timeline
- **body_format**: json_array
- **when_to_use**: 时间线/发展历程
- **markdown 示例**:
```markdown
:::timeline
[{"date": "2024-01", "event": "项目启动"}, {"date": "2024-06", "event": "首个版本发布"}, {"date": "2025-01", "event": "用户突破10万"}]
:::
```

#### infographic
- **body_format**: json_object
- **when_to_use**: 综合信息图，需要自定义布局
- **markdown 示例**:
```markdown
:::infographic
{"title": "AI 发展全景", "sections": [{"heading": "技术", "items": ["GPT", "Claude"]}], "source": "综合整理"}
:::
```

### Judgment（判断类）— 让立场明确

#### verdict
- **body_format**: fields
- **when_to_use**: 给出明确结论/推荐
- **markdown 示例**:
```markdown
:::verdict
title: 值得升级吗？
verdict: 推荐升级
reason: 速度和成本的改进远超预期，性价比极高
:::
```

#### audience-fit
- **body_format**: json_array
- **when_to_use**: 说明适合/不适合哪些人
- **markdown 示例**:
```markdown
:::audience-fit
[{"audience": "独立开发者", "fit": "强烈推荐", "reason": "成本大幅降低"}, {"audience": "企业用户", "fit": "建议观望", "reason": "私有化部署方案尚未明确"}]
:::
```

#### myth-fact
- **body_format**: json_array
- **when_to_use**: 澄清常见误解
- **markdown 示例**:
```markdown
:::myth-fact
[{"myth": "AI会取代所有程序员", "fact": "AI更多是增强工具，复杂架构仍需人类"}, {"myth": "GPT-5会写完美代码", "fact": "代码质量提升但仍需审查"}]
:::
```

#### manifesto
- **body_format**: fields
- **when_to_use**: 表达立场/宣言
- **markdown 示例**:
```markdown
:::manifesto
title: 我们的立场
points: AI应该是工具而非替代; 人类创造力不可替代; 技术应该为所有人服务
:::
```

#### bridge
- **body_format**: fields
- **when_to_use**: 从问题过渡到方案
- **markdown 示例**:
```markdown
:::bridge
from: 传统方案效率低下
to: AI驱动的新工作流
transition: 关键在于改变思维方式
:::
```

### Conversion（转化类）— 引导行动

#### cta
- **body_format**: fields
- **when_to_use**: 引导读者采取行动
- **markdown 示例**:
```markdown
:::cta
title: 开始使用
desc: 免费试用 14 天，无需信用卡
button_text: 立即注册
link: https://example.com
:::
```

#### faq
- **body_format**: json_array
- **when_to_use**: 常见问题解答
- **markdown 示例**:
```markdown
:::faq
[{"q": "支持哪些模型？", "a": "GPT-4/5, Claude, Gemini"}, {"q": "数据安全吗？", "a": "所有数据端到端加密"}]
:::
```

#### checklist
- **body_format**: json_array
- **when_to_use**: 行动清单/检查清单
- **markdown 示例**:
```markdown
:::checklist
[{"item": "获取API Key", "checked": true}, {"item": "配置环境变量", "checked": false}, {"item": "运行测试", "checked": false}]
:::
```

#### notice
- **body_format**: fields
- **when_to_use**: 重要提示/警告
- **markdown 示例**:
```markdown
:::notice
type: warning
title: 注意
text: API调用有频率限制，请合理使用
:::
```

#### summary
- **body_format**: json_array
- **when_to_use**: 文末总结
- **markdown 示例**:
```markdown
:::summary
[{"point": "GPT-5速度提升3倍"}, {"point": "API成本降低60%"}, {"point": "建议开发者尽快适配"}]
:::
```

### Brand（品牌类）— 品牌锚点

#### author-card
- **body_format**: fields
- **when_to_use**: 文末作者介绍
- **markdown 示例**:
```markdown
:::author-card
name: 张三
title: AI 产品经理
avatar: avatar.jpg
bio: 5年AI行业经验，关注大模型应用
:::
```

#### people
- **body_format**: json_array
- **when_to_use**: 团队介绍
- **markdown 示例**:
```markdown
:::people
[{"name": "张三", "role": "CEO"}, {"name": "李四", "role": "CTO"}]
:::
```

#### series
- **body_format**: json_array
- **when_to_use**: 系列文章导航
- **markdown 示例**:
```markdown
:::series
[{"title": "AI入门", "link": "#", "current": true}, {"title": "进阶实战", "link": "#", "current": false}]
:::
```

#### subscribe
- **body_format**: fields
- **when_to_use**: 引导关注/订阅
- **markdown 示例**:
```markdown
:::subscribe
title: 觉得有用？
desc: 关注获取更多AI实践干货
:::
```

## 模块纪律

1. 一篇文章最多 **1个 hero**、**1个 verdict**、**1个 cta**
2. 不要堆砌同类模块
3. opening → evidence → infographic → judgment → conversion → brand 的顺序排列
4. 每个模块之间用普通段落过渡
