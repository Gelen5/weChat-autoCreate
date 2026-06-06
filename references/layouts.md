# :::module 排版模块完整参考

> 从 md2wechat 的43个布局模块中精选最实用的30个，按6大类组织
> 每个模块包含完整的语法说明、使用场景和Markdown示例

---

## 模块分类总览

| 类别 | 英文 | 用途 | 模块数 |
|------|------|------|--------|
| 开场 | opening | 第一屏、破冰、建立期待 | 5 |
| 证据 | evidence | 引用、图说、对比、标注 | 5 |
| 信息图 | infographic | 数据、对比、步骤、时间线 | 5 |
| 判断 | judgment | 结论、适合人群、辟谣、宣言 | 5 |
| 转化 | conversion | CTA、FAQ、清单、总结 | 5 |
| 品牌 | brand | 作者卡、系列、订阅 | 5 |

---

## 一、Opening（开场）

### 1.1 hero

- **name**: hero
- **category**: opening
- **body_format**: 单行标题 + 可选副标题 + 可选标签
- **when_to_use**: 文章第一屏，建立气势和主题
- **when_not_to_use**: 短消息/快讯（太重）、已有一个封面图的文章
- **pairs_well_with**: toc、summary
- **anti_pattern**: hero内放超过3行文字，变成小作文

```markdown
:::hero
# 从零搭建AI应用的全栈指南

> 一篇文章讲透：从想法到上线的完整路径

TAGS: AI · 全栈 · 实战
:::
```

### 1.2 toc

- **name**: toc
- **category**: opening
- **body_format**: 有序列表，每项对应文章一节
- **when_to_use**: 长文（>2000字）、多章节文章、教程
- **when_not_to_use**: 短文（<800字）、观点文（不需要目录）
- **pairs_well_with**: hero、part
- **anti_pattern**: 目录项超过8个（说明文章结构太复杂）

```markdown
:::toc
1. 为什么需要全栈AI能力
2. 技术栈选型：从模型到前端
3. 核心架构设计
4. 从Demo到产品化
5. 上线与迭代
:::
```

### 1.3 cards

- **name**: cards
- **category**: opening
- **body_format**: 3-4个并列卡片，每个包含标题和简短描述
- **when_to_use**: 展示核心论点/关键发现、文章开头的"预告片"
- **when_not_to_use**: 论点之间有强顺序关系（用toc代替）、只有1-2个论点
- **pairs_well_with**: hero、verdict
- **anti_pattern**: 卡片描述超过2行（信息过载）

```markdown
:::cards
## 效率提升 3x
自动化排版节省90%手动调整时间

## 零格式丢失
全内联样式100%兼容微信编辑器

## AI智能排版
根据内容类型自动选择最佳组件
:::
```

### 1.4 part

- **name**: part
- **category**: opening
- **body_format**: 大号分部标记，包含编号和标题
- **when_to_use**: 长文分辑（上/中/下）、系列文章的某一部分
- **when_not_to_use**: 独立短文、不需要分辑的内容
- **pairs_well_with**: hero、toc、series
- **anti_pattern**: part标题与文章标题重复

```markdown
:::part
上篇
## 基础概念与环境搭建
:::
```

### 1.5 label-title

- **name**: label-title
- **category**: opening
- **body_format**: 标签（小字彩色）+ 标题（大字加粗）
- **when_to_use**: 小节标题、内容分类、增加层次感
- **when_not_to_use**: 文章最顶层标题（用hero）、只有标签没有标题
- **pairs_well_with**: hero、step
- **anti_pattern**: 标签文字太长（超过4个字）

```markdown
:::label-title
TUTORIAL
## LangChain RAG 实战
:::
```

---

## 二、Evidence（证据）

### 2.1 quote

- **name**: quote
- **category**: evidence
- **body_format**: 引用文字 + 可选出处
- **when_to_use**: 名人名言、数据引用、用户评价、专家观点
- **when_not_to_use**: 自己的观点（用callout）、长段文字（超过3行）
- **pairs_well_with**: hero、verdict
- **anti_pattern**: 引用无名之人的话（缺乏权威性）、引用过长

```markdown
:::quote
"AI不会取代人类，但使用AI的人会取代不使用AI的人。"

—— 李开复，《AI·未来》
:::
```

### 2.2 image-text

- **name**: image-text
- **category**: evidence
- **body_format**: 左图右文（或上图下文）+ 可选说明
- **when_to_use**: 产品截图+功能说明、人物+介绍、场景+分析
- **when_not_to_use**: 图片和文字没有直接关联、图片本身就是完整信息
- **pairs_well_with**: step、compare
- **anti_pattern**: 文字超过5行（应该拆分）

```markdown
:::image-text
![产品界面](image_url)
### 智能排版引擎
输入Markdown，输出精美微信文章。支持12种基础组件和3种SVG信息图模板。
:::
```

### 2.3 image-steps

- **name**: image-steps
- **category**: evidence
- **body_format**: 编号步骤 + 每步配图/说明
- **when_to_use**: 教程、操作流程、安装步骤
- **when_not_to_use**: 步骤少于2步（用正文即可）、步骤之间没有顺序关系
- **pairs_well_with**: hero、checklist
- **anti_pattern**: 步骤超过7个（应该拆分为多个模块）

```markdown
:::image-steps
1. **安装依赖** — `pip install langchain chromadb`
2. **配置API Key** — 设置环境变量 `OPENAI_API_KEY`
3. **初始化向量库** — 加载文档并生成embedding
4. **构建链路** — 连接检索器和生成器
5. **测试运行** — 输入查询验证效果
:::
```

### 2.4 image-compare

- **name**: image-compare
- **category**: evidence
- **body_format**: 两列对比，用 `---` 分隔
- **when_to_use**: 前后对比、新旧方案、竞品对比
- **when_not_to_use**: 超过2个对象对比（用表格代替）、没有对比意义的内容
- **pairs_well_with**: verdict、compare
- **anti_pattern**: 两列内容严重不对称

```markdown
:::image-compare
## 优化前
- 排版耗时2小时/篇
- 样式不统一
- 手动调CSS
---
## 优化后
- 排版耗时5分钟/篇
- 组件库统一风格
- AI自动选择组件
:::
```

### 2.5 image-annotate

- **name**: image-annotate
- **category**: evidence
- **body_format**: 图片 + 标注说明列表
- **when_to_use**: 截图标注功能点、架构图标注组件、UI设计稿标注
- **when_not_to_use**: 不需要标注的普通图片、文字本身足够清晰
- **pairs_well_with**: image-text、step
- **anti_pattern**: 标注点超过6个（信息过载）

```markdown
:::image-annotate
![架构图](image_url)
1. **API Gateway** — 统一入口，限流鉴权
2. **RAG Engine** — 检索增强生成核心
3. **Vector DB** — 向量存储与相似度搜索
4. **LLM Service** — 大语言模型调用层
:::
```

---

## 三、Infographic（信息图）

### 3.1 metrics

- **name**: metrics
- **category**: infographic
- **body_format**: 2-4个并列指标卡，大数字+说明
- **when_to_use**: 核心数据展示、KPI汇报、市场数据
- **when_not_to_use**: 数据之间没有并列关系、只有1个数据
- **pairs_well_with**: hero、compare
- **anti_pattern**: 数字没有单位、超过4个指标

```markdown
:::metrics
**¥2,400亿** | 市场规模 | ↑ 34% YoY
**1.2M** | GPU等效卡 | ↑ 67% YoY
**Top 3** | 市场集中度 | ↓ 5%
:::
```

### 3.2 compare

- **name**: compare
- **category**: infographic
- **body_format**: 双卡对比，用 `---` 分隔左右
- **when_to_use**: A/B方案对比、优劣势分析、新旧对比
- **when_not_to_use**: 3个以上对象对比、非对比场景
- **pairs_well_with**: verdict、metrics
- **anti_pattern**: 对比维度超过5个（用表格代替）

```markdown
:::compare
## 自建方案
- ✅ 完全可控
- ✅ 数据安全
- ❌ 开发成本高
- ❌ 维护负担重
---
## SaaS方案
- ✅ 快速上线
- ✅ 自动维护
- ❌ 定制性弱
- ❌ 数据在外部
:::
```

### 3.3 steps

- **name**: steps
- **category**: infographic
- **body_format**: 编号步骤列表，每步标题+说明
- **when_to_use**: 流程说明、实施路径、方法论步骤
- **when_not_to_use**: 步骤少于3步（用正文即可）、步骤没有先后顺序
- **pairs_well_with**: hero、checklist
- **anti_pattern**: 步骤说明超过3行

```markdown
:::steps
1. **需求定义** — 明确核心场景和用户画像
2. **技术选型** — 根据团队能力选择合适的技术栈
3. **MVP开发** — 2周内完成最小可行产品
4. **用户验证** — 找5个目标用户测试核心流程
5. **迭代优化** — 基于反馈快速迭代
:::
```

### 3.4 timeline

- **name**: timeline
- **category**: infographic
- **body_format**: 时间线节点列表，每个节点包含时间和事件
- **when_to_use**: 发展历程、版本迭代、项目里程碑
- **when_not_to_use**: 事件没有时间顺序、只有1-2个时间点
- **pairs_well_with**: hero、step
- **anti_pattern**: 超过8个时间节点（信息过载）

```markdown
:::timeline
**2023.Q1** | 项目立项，完成市场调研
**2023.Q3** | MVP开发完成，内测启动
**2024.Q1** | 正式版发布，首批1000用户
**2024.Q3** | B轮融资完成，团队扩展
**2025.Q1** | 国际化版本上线
:::
```

### 3.5 infographic

- **name**: infographic
- **category**: infographic
- **body_format**: 自定义SVG信息图，支持三种预设模板
- **when_to_use**: 飞轮模型、闭环逻辑、复杂关系图、对比信息图
- **when_not_to_use**: 简单数据展示（用metrics）、线性流程（用steps/timeline）
- **pairs_well_with**: hero、verdict
- **anti_pattern**: SVG中文字超过20个字（手机上无法阅读）

```markdown
:::infographic
type: compare
## 传统开发
- 周期：3-6个月
- 成本：50-200万
- 迭代：季度级
---
## AI驱动开发
- 周期：1-4周
- 成本：5-30万
- 迭代：周级
:::
```

支持的infographic类型：
- `type: compare` — 双卡对比（对应SVG模板A）
- `type: timeline` — 时间线（对应SVG模板B）
- `type: flywheel` — 飞轮/闭环（对应SVG模板C）

---

## 四、Judgment（判断）

### 4.1 verdict

- **name**: verdict
- **category**: judgment
- **body_format**: 结论框，一句话判断 + 可选展开说明
- **when_to_use**: 文章核心结论、分析后的最终判断、推荐/不推荐
- **when_not_to_use**: 文章开头（还没论证就给结论）、客观描述（不需要判断）
- **pairs_well_with**: compare、metrics、summary
- **anti_pattern**: 结论模糊（"看情况"、"因人而异"）

```markdown
:::verdict
**推荐自建**：团队规模>20人且数据敏感度高时，自建方案3年TCO更优。

对于10人以下团队，SaaS方案的综合ROI更高。
:::
```

### 4.2 audience-fit

- **name**: audience-fit
- **category**: judgment
- **body_format**: 适合/不适合的人群标注
- **when_to_use**: 产品推荐、方法论适用性、工具选型
- **when_not_to_use**: 通用内容（不需要区分人群）、纯信息类文章
- **pairs_well_with**: verdict、faq
- **anti_pattern**: 所有人都适合（说明判断没有价值）

```markdown
:::audience-fit
✅ **适合**：技术型创业团队、有Python基础的开发者、需要快速验证AI场景的产品经理

⚠️ **谨慎**：零技术背景的运营人员、对数据安全有极高要求的企业

❌ **不适合**：需要100%SLA保障的生产环境、需要多语言支持的国际团队
:::
```

### 4.3 myth-fact

- **name**: myth-fact
- **category**: judgment
- **body_format**: 误区→真相的配对展示
- **when_to_use**: 辟谣、常见误区纠正、概念澄清
- **when_not_to_use**: 没有常见误区的主题、主观观点（不是事实判断）
- **pairs_well_with**: verdict、summary
- **anti_pattern**: 误区和事实不是直接对立关系

```markdown
:::myth-fact
❌ **误区**：AI会取代所有程序员
✅ **事实**：AI取代的是重复性编码工作，但系统设计、架构决策等高层能力仍然稀缺

❌ **误区**：用了AI就不需要学编程了
✅ **事实**：AI工具需要编程知识才能有效使用和验证输出
:::
```

### 4.4 manifesto

- **name**: manifesto
- **category**: judgment
- **body_format**: 声明式文字，短句排列
- **when_to_use**: 立场声明、品牌宣言、价值观表达
- **when_not_to_use**: 信息类内容、教程类内容、需要论证的观点
- **pairs_well_with**: hero、author-card
- **anti_pattern**: 宣言超过6条（失去冲击力）

```markdown
:::manifesto
我们相信：

- 内容不应该被排版绑架
- 工具应该适应人，而非人适应工具
- AI是放大器，不是替代品
- 开源是最佳的合作方式
:::
```

### 4.5 bridge

- **name**: bridge
- **category**: judgment
- **body_format**: 过渡性文字，连接上下文
- **when_to_use**: 章节间过渡、逻辑转折、引出新话题
- **when_not_to_use**: 文章开头（没有上文）、每段都用（失去过渡效果）
- **pairs_well_with**: part、label-title
- **anti_pattern**: 桥段太长（超过3行就不是桥了）

```markdown
:::bridge
了解了基础概念后，我们来看看如何在真实项目中应用这些知识。
:::
```

---

## 五、Conversion（转化）

### 5.1 cta

- **name**: cta
- **category**: conversion
- **body_format**: 行动号召，标题+说明+按钮文字
- **when_to_use**: 引导下载、注册、关注、购买
- **when_not_to_use**: 纯信息文章（不需要行动）、文章中间（应该放在文末）
- **pairs_well_with**: summary、author-card
- **anti_pattern**: CTA没有明确动作（"了解更多"太模糊）

```markdown
:::cta
## 获取完整模板库
12种基础组件 + 3种SVG模板 + 4套风格预设

[下载模板库 →]
:::
```

### 5.2 faq

- **name**: faq
- **category**: conversion
- **body_format**: Q&A对列表
- **when_to_use**: 常见问题解答、售前咨询、概念澄清
- **when_not_to_use**: FAQ少于3个（用正文说明即可）、主观问题（不是"常见"问题）
- **pairs_well_with**: cta、notice
- **anti_pattern**: 回答超过5行（应该写成独立段落）

```markdown
:::faq
**Q: 支持哪些编辑器？**
A: 支持微信公众号编辑器、秀米、135编辑器。核心组件全内联样式，兼容所有编辑器。

**Q: 免费吗？**
A: 基础组件库完全免费开源。高级模板和AI排版功能需要订阅。

**Q: SVG在微信上显示正常吗？**
A: 经过测试，基础SVG图形在微信全平台正常显示。SMIL动画会被过滤。

**Q: 可以自定义风格吗？**
A: 可以。修改Color Token即可切换整体风格，参考styles目录下的预设文件。
:::
```

### 5.3 checklist

- **name**: checklist
- **category**: conversion
- **body_format**: 勾选项列表
- **when_to_use**: 上线前检查清单、准备事项、评估维度
- **when_not_to_use**: 项目没有先后顺序（用bullet list）、主观评价（用audience-fit）
- **pairs_well_with**: summary、steps
- **anti_pattern**: 清单项超过10个（拆分为多个checklist）

```markdown
:::checklist
- [x] 确认文章内容无误
- [x] 上传图片到微信图床
- [x] 测试SVG在手机端显示
- [ ] 添加文末引导关注
- [ ] 设置原文链接
- [ ] 定时发布设置
:::
```

### 5.4 notice

- **name**: notice
- **category**: conversion
- **body_format**: 公告/通知框
- **when_to_use**: 版本更新通知、功能变更、重要公告
- **when_not_to_use**: 普通内容（不是公告性质）、营销信息（用CTA）
- **pairs_well_with**: summary、subscribe
- **anti_pattern**: 公告内容超过5行

```markdown
:::notice
📢 **v2.0 更新通知**

新增3种SVG信息图模板，优化移动端显示效果。已订阅用户自动获取更新。

生效日期：2026年7月1日
:::
```

### 5.5 summary

- **name**: summary
- **category**: conversion
- **body_format**: 要点列表，带编号或勾选
- **when_to_use**: 文末总结、要点回顾、核心收获
- **when_not_to_use**: 文章开头（用hero/toc）、文章中间（打断阅读）
- **pairs_well_with**: hero、verdict
- **anti_pattern**: 总结项超过7个（说明文章太散）、总结与正文完全重复

```markdown
:::summary
1. 全内联样式是微信排版的第一原则
2. 12个基础组件覆盖90%排版需求
3. SVG信息图增强视觉冲击力
4. 一篇文章选用3-5种组件即可
5. 每篇文章测试手机端显示效果
:::
```

---

## 六、Brand（品牌）

### 6.1 author-card

- **name**: author-card
- **category**: brand
- **body_format**: 头像 + 姓名 + 简介 + 可选社交链接
- **when_to_use**: 文末作者介绍、团队文章署名、专栏作者展示
- **when_not_to_use**: 匿名文章、机构官方号（用品牌卡代替）
- **pairs_well_with**: summary、subscribe
- **anti_pattern**: 简介超过3行（太长）

```markdown
:::author-card
![头像](avatar_url)
### 张三
AI工程化研究者 | 前 Google 工程师
专注LLM应用落地，公众号「AI工程笔记」主理人
:::
```

### 6.2 people

- **name**: people
- **category**: brand
- **body_format**: 多人卡片，每人头像+姓名+职位
- **when_to_use**: 团队介绍、项目贡献者、嘉宾介绍
- **when_not_to_use**: 只有1人（用author-card）、人数超过6人（太长）
- **pairs_well_with**: author-card、series
- **anti_pattern**: 每人介绍超过2行

```markdown
:::people
![头像1](url) | **李四** | 产品负责人
![头像2](url) | **王五** | 技术负责人
![头像3](url) | **赵六** | 设计负责人
:::
```

### 6.3 series

- **name**: series
- **category**: brand
- **body_format**: 系列文章导航，当前篇高亮
- **when_to_use**: 系列文章文末导航、分辑文章互相引荐
- **when_not_to_use**: 独立文章、系列只有2篇（用链接即可）
- **pairs_well_with**: part、subscribe
- **anti_pattern**: 系列超过7篇（只展示最近的）

```markdown
:::series
📖 **AI全栈实战系列**

1. ~~基础概念与环境搭建~~
2. ~~RAG应用开发~~
3. **Agent架构设计** ← 当前
4. 多模态应用（待发布）
5. 部署与运维（待发布）
:::
```

### 6.4 subscribe

- **name**: subscribe
- **category**: brand
- **body_format**: 关注引导 + 价值主张
- **when_to_use**: 文末关注引导、涨粉、价值说明
- **when_not_to_use**: 文章中间（打断阅读）、已关注用户看到的重复内容
- **pairs_well_with**: summary、author-card
- **anti_pattern**: 关注理由太模糊（"关注不迷路"没有信息量）

```markdown
:::subscribe
**关注「AI工程笔记」**

每周1篇深度实操，从概念到代码，讲透AI工程化。

👆 长按关注，获取最新技术文章
:::
```

---

## 附录：模块速查表

### 按文章类型推荐模块组合

| 文章类型 | 推荐模块组合 |
|----------|-------------|
| 技术教程 | hero → toc → image-steps → quote → summary |
| 产品分析 | hero → metrics → compare → verdict → cta |
| 新闻快讯 | hero → metrics → verdict → notice → subscribe |
| 深度思考 | hero → quote → bridge → manifesto → author-card |
| 商业报告 | hero → toc → metrics → compare → verdict → cta |
| 教程合集 | hero → toc → image-steps → checklist → summary → series |
| 辟谣/澄清 | hero → myth-fact → quote → verdict → summary |
| 版本更新 | hero → notice → steps → faq → subscribe |
| 行业趋势 | hero → timeline → metrics → verdict → summary |
| 产品发布 | hero → cards → image-text → audience-fit → cta |

### 模块间搭配关系

```
hero ← → toc ← → part
hero ← → cards ← → verdict
image-steps ← → checklist ← → summary
compare ← → verdict ← → audience-fit
metrics ← → compare ← → infographic
summary ← → author-card ← → subscribe
cta ← → faq ← → notice
```
