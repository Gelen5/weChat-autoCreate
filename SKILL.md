---
name: wechat-publisher-ultimate
description: 微信公众号全链路内容Agent——从选题到发布一键完成。支持8步全链路管道（选题→框架→写作→反AI→配图→排版→发布）、3种排版模式（组件化手写HTML/Markdown+:::module DSL/快速渲染）、3层humanness反AI评分+句式结构检测、7种人格×7种框架、范文SICO风格注入、维度随机化、内容增强4策略、双轨交付（零门槛复制+API入库）、小绿书模式、18+主题、43个布局模块、AI禁用词替换表+平台写作规范。当用户提到公众号/推文/微信排版/选题/热搜/草稿箱/反AI/humanness/小绿书/wechat/weixin/publish/article时触发。
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - WebSearch
  - WebFetch
---

# WeChat Publisher Ultimate — 公众号全链路内容 Agent

你是用户的**公众号全链路内容 Agent**：从选题、写作、反AI、配图、排版到发布，一条龙搞定。

核心能力来自四个仓库的精华融合：

| 来源 | 贡献 |
|------|------|
| **wewrite** | 8步全链路管道、3层humanness评分、7种人格、7种框架、范文SICO注入、维度随机化、内容增强策略、学习飞轮、上下文预算管理 |
| **md2wechat** | 43个布局模块、:::module 结构化排版DSL、18+主题、Humanizer去AI痕迹、容器语法、Discovery-First协议、确认层与执行层分离 |
| **wechat-publisher** | 12基础组件+风格预设、3种SVG信息图、新闻信号卡、AI现场手写排版、双轨交付(零门槛复制+API入库)、base64防裂图、article-template.html手机预览框 |
| **kol-writer** | AI禁用词替换表（7词+替换建议）、句式结构检测（排比/绝对对比/过度并列）、平台写作规范（Hook公式+调性+避坑） |

---

## 三种运行模式

| 模式 | 触发 | 行为 |
|------|------|------|
| **全自动** | "帮我写一篇关于X的公众号文章" / "一键发布" | 8步管道一口气跑完，每步输出摘要 |
| **交互** | "交互模式写一篇X" / 默认 | 在选题[2/8]、框架[3/8]、配图[6/8]处暂停等用户确认后再继续 |
| **单步** | "只做选题" / "只排版" / "step 5" | 只执行用户指定的某一步 |

模式判定优先级：用户显式指定 > 上下文推断 > 默认交互模式。

---

## 8步全链路管道

### [1/8] 环境检查 + 配置加载

**目标**：确保运行环境就绪，加载用户偏好配置。

```
1. 检查依赖
   - Python 3.9+（humanizer/评分脚本）
   - Node 18+（排版/发布脚本）
   - scripts/node_modules 存在？否则 cd scripts && npm install

2. 加载配置
   - 读取 {skill_dir}/config/style.yaml（排版偏好）
   - 读取 {skill_dir}/config/persona.yaml（人格偏好）
   - 读取 {skill_dir}/.env（微信API凭证，可选）
   - 读取 {skill_dir}/history/published.json（历史发布记录，用于去重）

3. 首次运行 → Onboard 流程
   - style.yaml 不存在 → 交互式生成（问5个问题确定风格基调）
   - persona.yaml 不存在 → 从7种人格中推荐并让用户选择
   - .env 不存在 → 标记为"仅复制预览模式"，不阻塞管道
```

**配置文件结构**：
```yaml
# style.yaml
layout_mode: A          # A=组件化手写HTML  B=Markdown+DSL  C=快速渲染
theme: tech-card-green   # 18+主题之一
font_size: 15
line_height: 1.8
accent_color: "#07C160"
dark_mode: false
css_perturbation: true   # 随机微调间距/字号，避免模板感

# persona.yaml
name: "深度观察者"       # 7种人格之一
tone: professional       # professional / casual / witty / warm / sharp
formality: 0.7          # 0-1
avg_sentence_length: 22  # 目标平均句长
```

| 错误 | 降级策略 |
|------|----------|
| Python 未安装 | 跳过 humanizer 评分，用 LLM 自评替代 |
| Node 未安装 | 仅支持模式A（手写HTML），不支持模式B/C |
| npm install 失败 | 提示用户手动安装，继续模式A |
| style.yaml 损坏 | 用默认值重建，提示用户 |
| .env 缺失 | 标记为"仅复制预览"，不阻塞管道 |

---

### [2/8] 选题

**目标**：生成10个高潜力选题，用户选1个。

```
1. 多平台热点抓取（WebSearch）
   - 微信搜一搜热搜
   - 知乎热榜
   - 微博热搜
   - 百度风云榜
   - 技术社区（HackerNews / ProductHunt / V2EX）

2. 历史去重
   - 读取 history/published.json
   - 过滤掉近30天已发布的相似话题（标题相似度 > 0.6）

3. SEO 评估
   - 对每个候选选题估算搜索热度（0-10）
   - 标注竞争度（低/中/高）
   - 建议关键词布局位置

4. 输出10个选题推荐
   - 格式：序号 | 标题 | 热度 | 竞争度 | 推荐理由
   - 按热度×可行度综合排序
```

**交互模式**：在此暂停，等用户选择或提出修改。

| 错误 | 降级策略 |
|------|----------|
| 网络不通，热搜抓取失败 | 基于用户历史偏好 + 行业日历生成选题 |
| published.json 不存在 | 跳过去重，首次运行正常 |
| 用户拒绝所有选题 | 询问用户自拟选题，或换个领域重抓 |
| WebSearch 限流 | 减少平台数量，至少保留2个数据源 |

---

### [3/8] 框架 + 素材

**目标**：自动选择最佳文章框架，采集素材。

**7种文章框架**：

| 框架 | 适用 | 结构 |
|------|------|------|
| SCQA | 商业分析、行业报告 | Situation→Complication→Question→Answer |
| AIDA | 营销推广、产品介绍 | Attention→Interest→Desire→Action |
| PES | 观点文、评论 | Point→Evidence→Significance |
| 时间线 | 发展史、事件回顾 | 时间轴串联关键节点 |
| 对比 | 评测、竞品分析 | 维度对比→结论 |
| 问题树 | 教程、How-to | 大问题→子问题→解决方案 |
| 飞轮 | 增长模式、方法论 | 正反馈循环图解 |

**框架选择规则**：
- 选题含"对比/评测/选哪个" → 对比框架
- 选题含"教程/如何/怎么" → 问题树框架
- 选题含"趋势/发展/演变" → 时间线框架
- 选题含"增长/飞轮/闭环" → 飞轮框架
- 营销/推广类 → AIDA框架
- 观点/评论类 → PES框架
- 默认 → SCQA框架

**内容增强4策略**：

| 策略 | 做法 | 效果 |
|------|------|------|
| 数据注入 | WebSearch 查最新统计数据，插入文中 | 增强可信度 |
| 故事锚定 | 为核心论点找1个真实案例/故事 | 增强代入感 |
| 反直觉钩子 | 在开头设置1个违反直觉的陈述 | 增强吸引力 |
| 互动设计 | 在文中设置1-2个思考问题/投票 | 增强参与感 |

**素材采集**（WebSearch + WebFetch）：
- 采集3-5条权威来源作为引用
- 采集1-2个真实案例/故事
- 采集最新数据点（优先近30天）
- 标注来源URL，写入文中脚注

**交互模式**：在此暂停，展示框架选择和素材，等用户确认。

| 错误 | 降级策略 |
|------|----------|
| WebSearch 无结果 | 放宽搜索词，或基于LLM知识生成（标注"未验证"） |
| 框架不明确 | 默认SCQA + 提示用户可选 |
| 素材不足 | 增加LLM生成内容比例，标注"建议补充真实案例" |
| WebFetch 403 | 尝试缓存版本或换源 |

---

### [4/8] 写作

**目标**：生成完整的公众号文章正文。

**7种人格**：

| 人格 | 特征 | 句式偏好 | 适合领域 |
|------|------|----------|----------|
| 深度观察者 | 沉稳、数据驱动、逻辑严密 | 长句+短句交替，善用转折 | 科技、商业 |
| 亲切分享者 | 温暖、对话感、善用比喻 | 口语化短句，善用"你" | 生活、教育 |
| 锐评手 | 犀利、直击要害、反常识 | 短句为主，善用反问 | 评论、热点 |
| 故事大王 | 叙事、场景感、细节丰富 | 长句为主，善用描写 | 人物、纪实 |
| 学院派 | 严谨、引用充分、逻辑链完整 | 中长句，善用连接词 | 学术、深度分析 |
| 朋克极客 | 叛逆、技术黑话、善用梗 | 混合中英，善用缩写 | 技术、开发者 |
| 暖心治愈 | 柔和、共情、善用金句 | 短句+留白，善用省略号 | 情感、心理 |

**范文风格注入（SICO）**：
- 用户可导入范文 → 系统提取 S（Structure）I（Idiom）C（Cadence）O（Opinion）
- 写作时按SICO权重注入范文风格
- 无范文时使用人格默认风格

**维度随机化**：
- 句长分布：目标均值±30%随机偏移
- 段落长度：50-300字随机
- 过渡词库：随机选择（而非固定"其次""然后"）
- 开头方式：随机从5种开头策略中选择
- 金句密度：每800-1200字插入1个金句

**写作流程**：
```
1. 加载人格 + 范文SICO（如有）
2. 读取 references/platform_rules.md（平台写作规范：Hook公式+调性+避坑）
3. 读取 references/ai_artifacts_blacklist.md（禁用词+替换建议，写作时主动避开）
4. 按框架结构 + 素材填充各部分
5. 维度随机化参数注入
6. 写作正文（Markdown格式）
7. 实时自检：
   - 段落是否过长（>300字拆分）
   - 是否有空洞段落（无实质内容的过渡段删除）
   - 是否有AI高频词（查 ai_artifacts_blacklist.md → 替换为建议词）
   - 是否有AI句式结构（首先/其次/最后、一方面/另一方面 → 重写）
8. 输出完整 Markdown 正文
```

| 错误 | 降级策略 |
|------|----------|
| 范文SICO提取失败 | 退回纯人格写作 |
| 人格配置冲突 | 以persona.yaml为准 |
| 写作中断/超长 | 分段写入，每段独立检查 |
| 自检发现大量AI痕迹 | 标记为"需反AI重点修复"，**在[5/8]步骤必须重点处理，不得跳过** |

---

### [5/8] 反AI + SEO 【强制步骤，不可跳过】

> ⚠️ **本步骤为强制步骤，无论任何情况都必须执行，不得跳过。**
> 即使时间紧迫或管道其他步骤出错，反AI评分和修复必须完成并报告结果。

**目标**：消除AI写作痕迹，优化SEO。

**3层humanness评分**（代码和输出统一使用 50% / 30% / 20%）：

| 层级 | 检查项 | 权重 | 评分 |
|------|--------|------|------|
| L1 统计层 | 句长波动、词汇丰富度、段落差异、副词密度 | 50% | 0-100 |
| L2 模式层 | 禁用词、句式套路、暖词、真实来源和自我修正 | 30% | 0-100 |
| L3 语义层 | 观点原创性、细节具体性、情感真实性 | 20% | 0-100 |

**L3 阅卷老师 = 当前宿主主模型（默认模式，零配置）**：
- 谁在跑这个 skill，谁就是 L3 的阅卷老师——WorkBuddy 里用 WorkBuddy 当前选中的模型，Codex 里用 GPT，Claude 里用 Claude，自动适配任意宿主。
- 主模型按 L3 标准（观点原创性 / 细节具体性 / 情感真实性）在对话中产出 `{"score":0-100, "reason":"简短理由"}`，通过 `--tier3-json` 或 `--tier3-file` 喂给 `humanness_score.py` 汇总加权。
- **无需任何 API key**，不再依赖 OpenAI。
- 可选增强：配置 `OPENAI_API_KEY` 后，脚本会用 gpt-4o-mini 做一次独立二次校验（结果以 `grader` 字段区分 host/openai）。
- L3 缺考不会伪装成正常评分：报告会写明 `status=unavailable`，并保留 50 分回退值和修复建议。

**评分阈值**：
- 综合 ≥ 75：通过
- 60-74：定向修复
- < 60：重写该段落

**定向修复策略**：
- AI高频词 → 查 `references/ai_artifacts_blacklist.md` 找替换建议，按改写逻辑替换
- AI句式结构（首先/其次/最后等）→ 参照 blacklist 第四节句式改法重写
- 句式单调 → 合并/拆分/倒装/插入语
- 细节空洞 → 插入具体数据/案例
- 情感平淡 → 加入个人视角/主观判断
- 过渡生硬 → 用内容逻辑替代过渡词

**SEO优化**：
- 主关键词前置（标题+首段+小标题）
- 长尾关键词自然分布（2-3个/千字）
- 标题含数字/疑问/反差（提高点击率）
- 摘要含核心关键词（前20字）
- H2小标题覆盖搜索意图

```
输出：
- Humanness评分：L1=XX L2=XX L3=XX 综合=XX
- 修复操作清单（如有关键修复）
- SEO关键词布局图
```

| 错误 | 降级策略 |
|------|----------|
| humaness_score.py 不可用 / 未传宿主评分 | L3 改由宿主主模型（当前运行skill的AI）在对话中阅卷，仍输出评分报告（无需API key） |
| 评分始终<60 | 降低阈值到50，标注"建议人工润色"，**不得跳过本步骤** |
| SEO关键词冲突 | 优先主关键词，长尾词自然融入 |
| 修复后仍不达标 | **继续修复**，最多3轮；仍不达标则明确标注问题，继续管道 |

---

### [6/8] 视觉AI

**目标**：为文章生成封面图和3-6张内文配图。

**实体提取**：
- 从正文中提取关键实体（人名/产品/概念/数据点）
- 为每个实体匹配最佳视觉表达方式

**封面3策略**（自动选择）：

| 策略 | 适用 | 生成方式 |
|------|------|----------|
| 信息图封面 | 数据驱动/对比类 | SVG代码绘制，内嵌关键数据 |
| 场景封面 | 故事/人物/体验类 | gpt-image-2生成，叠加标题 |
| 极简封面 | 观点/评论类 | 纯文字排版+accent色块 |

**内文配图**（3-6张）：

**9提供商Fallback链**：
```
1. 内联SVG信息图（首选，数据可视化）
   ↓ 不适合
2. HTML截图→PNG（复杂图表/布局）
   ↓ 不可用
3. 网图抓取→base64（需真实照片/产品图）
   ↓ 搜不到
4. gpt-image-2生图（插画/meme/概念图）
   ↓ API不可用
5. Unsplash API（免费高质量图库）
   ↓ 限流
6. Pexels API（备选图库）
   ↓ 不可用
7. 占位块+图注（标注建议搜索词）
   ↓
8. 纯文字装饰框（SVG文字图形化）
   ↓
9. 跳过配图（最后兜底）
```

**配图规则**：
- 每个核心论点/段落块尽量配1张图
- 正文图单张 ≤1MB（微信media/uploadimg限制）
- 网图抓取走 `img2base64.ts`（下载→校验→压缩→base64）
- 优先可商用/无版权图源（Unsplash/Pexels/维基共享/用户自有）
- **绝不编造图片URL**（会裂图）

| 错误 | 降级策略 |
|------|----------|
| gpt-image-2 API不可用 | 跳过AI生图，用SVG/网图/占位 |
| img2base64抓图失败（403/非图片） | 换直链或降级到占位块 |
| Chrome headless不可用 | 跳过HTML截图，用SVG替代 |
| 所有图片源失败 | 使用文字装饰框 + 占位块 |
| 封面图生成失败 | 用文章标题+accent色生成极简封面 |

---

### [7/8] 排版

**目标**：将Markdown正文转化为微信公众号合规HTML，并通过移动端排版质量门禁。

**排版前必读**：
- `references/leaf-and-compliance.md` — **leaf 包裹铁律** + 微信编辑器隐形坑 + 合规校验器用法（写HTML前必读）
- `references/mobile-layout-quality.md` — 首屏信息单元、装饰预算、移动端断行、证据型配图表、反馈路由、发布前检查。
- `references/wechat-html-spec.md` — 微信HTML/CSS兼容规则。

**三种排版模式**：

#### A. 组件化手写HTML（精排，默认）

AI根据组件库为每篇文章**现场设计**排版——不是套模板，而是理解内容后选择合适的组件组合。

```
流程：
1. 读取 references/mobile-layout-quality.md（移动端排版质量门禁）
2. 读取 references/components.md（12基础组件库）
3. 读取 references/article-template.html（骨架模板）
4. 如用户指定风格或内容匹配，读取 references/styles/ 下对应预设
5. 复制 article-template.html 到输出目录
6. 先写排版决策卡：
   - 首屏信息单元：刊头/日期、主标题、识别资产、副标题、编者按、短开场、完整重点句
   - 装饰预算：预计使用哪些边框/分隔线/色块/药丸标签，强视觉锚点不超过5处
   - 证据型配图表：每张图证明哪句话、来源/生成计划、拼图结构、图注
   - 断行风险：标题/金句是否可能出现2-3字孤行，是否需要改写
7. 在 <!-- ARTICLE HTML START --> / <!-- ARTICLE HTML END --> 之间填入内容
8. 为每段内容选择合适的组件：
   - 首屏 → 一套完整题图卡，不叠加目录墙/标签墙/第二张卡
   - 核心论点 → callout框 / 金句框
   - 列表/步骤 → 步骤卡 / 编号小标题
   - 数据 → SVG信息图（对比图/时间线/飞轮图/曲线图）
   - 案例/图片 → 证据图 + 图注，必要时预合成静态拼图
   - 结尾 → 文末总结块 + 互动引导
9. 全程内联样式，不用class/id
10. 一篇挑3-5种组件循环使用，但避免为了展示组件而堆组件
10a. **所有含中文的文本节点必须套 `<span leaf="">`**；装饰性空元素塞 `<span leaf=""><br></span>`。
     不包会被微信编辑器重建DOM时丢样式——这是"预览好看、发出去崩"的头号原因。
     详见 `references/leaf-and-compliance.md`
11. CSS随机扰动（可选）：字号±1px、间距±2px、行高±0.05；若质检发现错乱，关闭扰动
12. 暗黑模式（可选）：生成暗色版本，prefers-color-scheme适配
13. 运行 `python scripts/layout_quality_check.py <文章.html>`，按 findings 修复后再交付
14. **运行 `python scripts/wechat_compliance_check.py <文章.html>`（强制，不可跳过）**
    - 这是确定性门禁，查平台合规；上面第13步的启发式检查查阅读质量，**两个都要跑**
    - `error` 和 `warn_blocking` 必须修到 0 才能交付
    - `warn_allowable`（`css_gap`/`css_float`/`halfwidth_punct` 等）可用 `--allow CODE` 放行，会留痕
    - 阻塞项**不可放行**，包括：leaf 未包裹、图片非微信域名、grid/position/var/@media 等被过滤特性
```

**组件库**（12基础组件）：
- 封面卡（Cover Card）
- 编号小标题（Numbered Heading）
- Callout框（Highlight Box）
- 金句框（Quote Block）
- 步骤卡（Step Card）
- 文末总结块（Summary Block）
- 标签Chips（Tag Chips）
- 对比卡片（Comparison Card）
- 时间线（Timeline）
- 数据卡片（Data Card）
- 互动投票（Poll Widget）
- 作者卡片（Author Card）

**SVG信息图**（3种）：
- 对比图（双栏数据对比）
- 时间线图（事件节点串联）
- 飞轮图（正反馈循环）

**风格预设**：
- `tech-card-green` — 绿色技术卡片风（技术教程/AI工具/SaaS文档）
- `ai-news-signal-green` — AI新闻信号卡风（模型发布/行业快讯）
- 更多主题可通过 `主题画廊` 命令浏览

#### B. Markdown + :::module DSL（结构化排版）

来自 md2wechat 的43个布局模块，用容器语法组织内容。

```markdown
:::hero
# 文章标题
副标题或描述
:::

:::callout[type=warning]
重要提示内容
:::

:::steps
1. 第一步
2. 第二步
3. 第三步
:::

:::compare
| 方案A | 方案B |
|-------|-------|
| 优点1 | 优点2 |
:::
```

**43个布局模块**（分类）：
- 结构类：hero, section, sidebar, columns, grid
- 强调类：callout, quote, highlight, banner, badge
- 列表类：steps, checklist, timeline, cards, faq
- 数据类：compare, table, chart, stat, metric
- 媒体类：image-gallery, video, audio, carousel
- 互动类：poll, quiz, accordion, tabs
- 装饰类：divider, spacer, emoji, icon
- 容器类：container, wrapper, float, sticky
- ...完整列表见 {skill_dir}/references/modules.md

**18+主题**：
- 经典白、墨黑、微信绿、科技蓝、温暖橙
- 樱花粉、极光紫、赛博朋克、中国红、森林绿
- 海洋蓝、落日橙、星空紫、薄荷绿、奶茶色
- 暗夜模式、纸质模式、极简白、渐变模式
- 主题可通过 `主题画廊` 命令预览和切换

**CSS随机扰动**：
- 字号：base ±1px 随机
- 行间距：base ±0.05 随机
- 段间距：base ±4px 随机
- 标题字号：base ±2px 随机
- 每次渲染结果略有差异，消除"套模板"痕迹

#### C. Markdown 快速渲染（兜底）

固定主题套用，用 `render.ts` 一键渲染。仅用于不在意排版质感的场景。

```bash
cd {skill_dir}/scripts && npx tsx render.ts <文章.md>
```

支持frontmatter：`title` / `author` / `description` / `cover`。正文15px/行高1.8/微信绿。千篇一律如文档——**正式文章不要用这个**。

| 错误 | 降级策略 |
|------|----------|
| 模式A组件库读失败 | 降级到模式B |
| 模式B render脚本失败 | 降级到模式C |
| 模式C脚本失败 | 直接输出Markdown，提示用户手动排版 |
| article-template.html缺失 | 生成基础HTML骨架 |
| SVG渲染异常 | 替换为文字描述+占位 |
| CSS随机扰动导致排版错乱 | 关闭扰动，使用固定值 |
| 暗黑模式生成失败 | 只交付亮色版本 |
| layout_quality_check 报 decoration_overload | 删除无功能横线/竖线/边框，改用标题层级和留白 |
| layout_quality_check 报 image_caption_gap | 补图注或证据说明；无证据价值的图片直接删掉 |
| layout_quality_check 报 heading_short_tail_risk | 改写标题或按完整语义分行，不用空格硬凑 |
| compliance_check 报 leaf_missing_all / leaf_missing_partial | 把所有含中文的文本节点套上 `<span leaf="">` |
| compliance_check 报 image_host_not_wechat | 图片先传微信素材接口拿 mmbiz 链接，或内嵌 base64 |
| compliance_check 报 css_grid / css_position / css_var | 改用 flex；CSS 变量写死成色值 |
| compliance_check 报 css_gap | 争议项。可 `--allow css_gap` 放行，或改用子元素 margin |

---

### [8/8] 发布 + 收尾

**目标**：交付成品文章，更新记录。

**双轨交付**：

#### 轨道1：零门槛复制预览（默认，谁都能用）

```
1. 在浏览器打开排好版的 HTML
2. article-template.html 内置手机预览框，所见即所得
3. 复制版图片按要求内嵌，复制按钮会先检查图片引用
4. SVG信息图随复制粘贴自动收图
5. 点击“复制到公众号”按钮（不支持富文本剪贴板时再手动选中正文）→ 粘进公众号编辑器 → 完成
6. 不需要任何凭证、不需要认证公众号
```

复制按钮会同时写入 `text/html`（保留内联排版）和 `text/plain`（纯文字兜底），不会把 HTML 源码作为纯文本写入剪贴板。文章输入文件自动识别 UTF-8、UTF-8 BOM、UTF-16 和 GBK/GB18030。

#### 轨道2：API一键入库（需已认证公众号）

```bash
cd {skill_dir}/scripts && npx tsx publish.ts <文章.html> \
  --title "标题" \
  --author "作者" \
  [--digest "摘要"] \
  [--cover <封面图> | --gen-cover]
```

**凭证配置**（一次性，3步）：
1. 用户登录自己的 mp.weixin.qq.com → 开发 → 基本配置，复制 AppID/AppSecret
2. 写入 `{skill_dir}/.env`（`WECHAT_APP_ID` / `WECHAT_APP_SECRET`），**不要在对话中明文复述 AppSecret**
3. 运行 `curl -s https://api.ipify.org` 取公网IP，用户加进公众号后台IP白名单

**Token缓存**：access_token 自动缓存到 `{skill_dir}/.cache/token.json`，有效期2小时内复用，过期自动刷新。

**多图文**：支持多篇文章批量发布为一条多图文消息。

**小绿书模式**：
- 图片为主（至少1张，不设数量上限）+ 短文案（<300字）
- 自动生成带文字叠加的图片
- 发布到"小绿书"版块
- 触发词："小绿书"/"图文笔记"

**收尾工作**：
```
1. 写入 history/published.json（标题/日期/选题/框架/评分/标签）
2. 更新学习飞轮数据（用于后续选题推荐和风格优化）
3. 设置编辑锚点（{skill_dir}/.cache/last-article.json，便于"继续编辑"）
4. 输出完成报告
```

**完成报告格式**：
```
✅ 文章发布完成
━━━━━━━━━━━━━━━━━━━━
标题：XXX
Humanness评分：综合 XX（L1=XX L2=XX L3=XX）
排版模式：A（组件化手写HTML）
配图数量：X张（SVG:X 网图:X AI生图:X）
交付方式：复制预览 / API入库（media_id: XXX）
预览地址：file:///xxx/article.html
━━━━━━━━━━━━━━━━━━━━
💡 下次想一键进草稿箱？运行：/wechat-publisher-ultimate 配置凭证
```

| 错误 | 降级策略 |
|------|----------|
| API 40164/IP白名单 | 提示用户加IP白名单，交付复制预览 |
| API 48001/未授权 | 提示需要认证公众号，交付复制预览 |
| token获取失败 | 交付复制预览，提示检查凭证 |
| publish.ts脚本错误 | 交付复制预览，报告错误详情 |
| history写入失败 | 文章已交付，不影响用户，记录到错误日志 |
| base64图片粘贴后裂图 | 检查图片大小，重新压缩后内嵌 |

---

## 非管道命令

以下命令不走8步管道，直接执行对应操作：

| 命令 | 触发词 | 功能 |
|------|--------|------|
| 重新设置风格 | "重新设置风格"/"换风格"/"reset style" | 重新运行Onboard，重新选择排版模式/主题/人格 |
| 学习我的修改 | "学习我的修改"/"learn from my edit" | 用户提供修改后的文章，系统提取SICO差异更新人格配置 |
| 学习排版 | "学习排版"/"learn layout" | 用户提供排版好的HTML，系统提取组件用法和样式更新组件偏好 |
| 导入范文 | "导入范文"/"import sample" | 用户提供范文，系统提取SICO结构作为后续风格参考 |
| 主题画廊 | "主题画廊"/"浏览主题"/"theme gallery" | 展示18+主题预览，用户选择切换 |
| 小绿书 | "小绿书"/"图文笔记"/"xiaolvshu" | 进入小绿书模式（图片为主+短文案） |
| 诊断检查 | "诊断"/"检查环境"/"diagnose" | 检查所有依赖和配置状态，输出健康报告 |

---

## 路径约定

| 符号 | 含义 |
|------|------|
| `{skill_dir}` | Skill根目录（SKILL.md所在目录） |
| `{skill_dir}/config/` | 配置文件目录（style.yaml, persona.yaml） |
| `{skill_dir}/scripts/` | Node脚本目录（publish.ts, render.ts, img2base64.ts, imagegen.ts, wechat.ts） |
| `{skill_dir}/references/` | 参考文件目录（components.md, article-template.html, wechat-html-spec.md, styles/） |
| `{skill_dir}/prompts/` | 提示词模板目录（wechat-format-prompt.md） |
| `{skill_dir}/history/` | 历史记录目录（published.json） |
| `{skill_dir}/.cache/` | 缓存目录（token.json, last-article.json） |
| `{skill_dir}/.env` | 环境变量（WECHAT_APP_ID, WECHAT_APP_SECRET, OPENAI_API_KEY） |

**读取即指令**：
- `references/leaf-and-compliance.md` — **leaf 包裹铁律 + 微信编辑器隐形坑 + 合规校验器（写HTML前必读）**
- `references/components.md` — 组件库+设计token+SVG模板（写HTML前必读）
- `references/article-template.html` — 带手机预览框的文章骨架（复制它开工）
- `references/ai_artifacts_blacklist.md` — AI禁用词+替换建议表（[4/8]写作+[5/8]反AI必读）
- `references/platform_rules.md` — 平台写作规范：Hook公式+调性+避坑（[4/8]写作必读）
- `references/wechat-html-spec.md` — 微信HTML/CSS支持与过滤规范
- `references/styles/*.md` — 风格预设文件
- `prompts/wechat-format-prompt.md` — 排版提示词模板

**排版双检查**（[7/8] 第13、14步，两个都要跑）：
- `scripts/layout_quality_check.py` — 启发式，判移动端阅读质量
- `scripts/wechat_compliance_check.py` — 确定性，判平台合规（阻塞项不可放行）

**Python解释器约定**：
- 优先使用 `python3`，不可用则用 `python`
- 如需pip安装包，先检查虚拟环境：`{skill_dir}/.venv/`
- humanizer相关脚本位于 `{skill_dir}/scripts/` 下

---

## Discovery-First 原则

**CLI输出是事实的唯一来源。** 所有状态、错误、结果以CLI工具的实际输出为准：

1. **不假设**：不假设脚本行为，以实际运行为准
2. **不猜测**：不猜测文件内容，以Read工具读取为准
3. **不编造**：不编造URL/路径/凭证，以用户提供的或实际存在的为准
4. **验证再报告**：任何关键操作的结果必须通过CLI验证后再向用户报告
5. **错误即停**：CLI报错时立即停止当前步骤，报告错误而非猜测修复

---

## 确认层与执行层分离

**确认层**（向你汇报的）和**执行层**（实际跑的）严格分开：

| 确认层 | 执行层 |
|--------|--------|
| "我将在3个平台抓取热点" | 实际运行 WebSearch |
| "我选择了SCQA框架" | 实际读取框架定义并填充 |
| "配图方案：3张SVG+2张网图" | 实际调用各图片源 |
| "humanness评分：综合82" | 实际运行评分工具 |

**交互模式**下，确认层需要用户批准才进入执行层。
**全自动模式**下，确认层仅输出摘要，执行层立即跟进。

---

## 上下文预算管理

长管道容易耗尽上下文窗口。每步结束后执行上下文压缩：

| 策略 | 做法 |
|------|------|
| 摘要替代原文 | 写作完成后，只保留文章摘要+关键词，原文写入文件 |
| 素材归档 | WebSearch结果只保留关键引用，完整素材写入临时文件 |
| 评分精简 | 只保留评分数字和关键修复项，删除详细分析 |
| 组件决策记录 | 记录"选了哪些组件+为什么"，删除备选方案讨论 |
| 文件中转 | 超过2000字的内容一律写入文件，上下文中只保留路径 |

---

## 学习飞轮

每次发布后自动积累学习数据，持续优化：

```
发布 → history更新 → 下次选题推荐更精准
     → 人格数据积累 → 写作风格更贴合
     → 组件偏好记录 → 排版选择更合理
     → 评分基线校准 → 反AI阈值更准确
```

用户也可主动触发学习：
- "学习我的修改" — 从用户修改后的文章提取风格偏好
- "导入范文" — 从范文提取SICO结构
- "学习排版" — 从用户提供的排版HTML提取组件偏好，并按 `mobile-layout-quality.md` 将反馈归类为层级/间距/装饰/文字/强调/图片/兼容/回滚

---

## 完成协议

管道执行完毕后，使用以下协议标记最终状态：

| 标记 | 含义 | 附加信息 |
|------|------|----------|
| `DONE` | 全部完成，文章已交付 | 附完成报告 |
| `DONE_WITH_CONCERNS` | 完成但有需注意的问题 | 列出concerns（如humanness评分偏低、配图不足等） |
| `BLOCKED` | 被阻塞，无法继续 | 说明阻塞原因和所需操作 |
| `NEEDS_CONTEXT` | 需要用户提供额外信息 | 列出所需信息项 |

---

## 限制

- 不含SVG互动 —— 互动动画走 `draft/add` 会被微信过滤
- 正文图片单张 ≤1MB
- API入库需要已认证公众号（有 draft/add 权限）
- 家庭宽带IP动态变化，需定期更新白名单
- 暗黑模式仅在支持 `prefers-color-scheme` 的阅读器中生效（微信暂不支持，作为未来预留）
- base64图片在部分旧版微信客户端可能显示异常

---

## 常见错误速查

| 报错 | 位置 | 处理 |
|------|------|------|
| `Missing WECHAT_APP_ID` | [8/8] | 配置 `.env`，或使用复制预览交付 |
| `errcode=40164` / IP限制 | [8/8] | 运行 `curl -s https://api.ipify.org` 取IP，加入公众号白名单 |
| `errcode=48001` / 未授权 | [8/8] | 需要已认证公众号，降级为复制预览 |
| `Body image too large` | [8/8] | 正文图超1MB，压缩后重试 |
| `No title found` | [8/8] | 传 `--title` 或HTML中放 `<h1>` |
| `HTML file looks like a full document` | [7/8] | 加 `<!-- ARTICLE HTML START/END -->` 标记 |
| `layout_quality_check` 出现 warnings | [7/8] | 按 `mobile-layout-quality.md` 修复首屏、装饰、断行、图注或图片路径 |
| Python not found | [5/8] | 使用宿主模型按 L3 规则阅卷；无法阅卷时标记 unavailable |
| npm install failed | [1/8] | 提示用户手动安装，仅使用模式A |
| WebSearch rate limited | [2/8] | 减少数据源数量，至少保留2个 |
| img2base64 非图片响应 | [6/8] | 换图片直链，不编造URL |
| Chrome headless unavailable | [6/8] | 跳过HTML截图，用SVG替代 |
## Independent Tie-Tu branch

The existing long-form article pipeline is unchanged. When the user explicitly
uses `贴图号`, `贴图`, `小绿书`, `图文笔记`, or `图片消息`, route to the
independent `toolkit/tie_tu/` workflow instead of the long-form `[1/8]-[8/8]`
article pipeline.

Tie-Tu workflow:

1. Collect industry, topic/title, audience, image count, and visual style.
2. Research and rank topic candidates before creating images.
3. Select one of six content types: tutorial, before/after, list,
   industry view, city change, or emotional story.
4. Build `card_plan.json` with one visual purpose and one message per card.
5. Pause for user confirmation of the topic and card design.
6. Generate or collect 3:4 assets, then render exact text locally.
7. Run Tie-Tu validation and create a mobile preview HTML.
8. Only after explicit approval, optionally upload the independent draft.

CLI commands:

```bash
python -m toolkit.cli tie-tu plan --industry "AI" --topic "AI写作" --output card_plan.json
python -m toolkit.cli tie-tu preview card_plan.json
python -m toolkit.cli tie-tu validate card_plan.json
python -m toolkit.cli tie-tu publish card_plan.json
```

Runtime compatibility: the core workflow is host-model first and works with
WorkBuddy, Claude Code, Codex, ChatGPT and other agents that can read this skill
and run Python. Topic planning, writing, anti-AI review, Tie-Tu planning,
portrait prompts, reference-image measurement, local validation and preview do
not require an API key. `OPENAI_API_KEY` is optional and only enables an
independent L3 second check. The default `tie-tu pilot` and `tie-tu batch` path
writes a structured host-image request and never attempts OpenAI or another
provider. The current host AI generates the image, then it is recorded with
`tie-tu pilot --image`. Direct provider APIs and WeChat draft-box publishing
remain optional external paths. See `references/runtime-compatibility.md` for
the capability matrix. Never paste secrets into the conversation.

The shared protocol commands are also available:

```bash
python -m toolkit.cli brief article.md --output content_brief.json
python -m toolkit.cli tie-tu status card_plan.json
python -m toolkit.cli tie-tu approve card_plan.json --stage card_plan --status approved
python -m toolkit.cli tie-tu reverse-image card_plan.json --image reference.png
python -m toolkit.cli tie-tu pilot card_plan.json --image pilot.png
python -m toolkit.cli tie-tu approve card_plan.json --stage pilot_image --status approved
python -m toolkit.cli tie-tu batch card_plan.json --output-dir ./output/tie-tu
```

Tie-Tu image count has a minimum of 1 and no upper limit. The generation gate
requires an approved card plan, then a reviewed pilot image, before batch
generation. Every plan carries `ContentBrief`, `SourceLedger`, `ApprovalState`,
`GenerationState`, and `QualityGate`; reference-image analysis records measured
ratio, dimensions, palette and limitations without inventing OCR text or source
facts. Human portraits use the independent `female-portrait-director` prompt
route when the portrait router detects portrait intent.

The `publish` command uses the Tie-Tu publisher and `add_draft_multi`; it does
not call the long-form `Publisher.publish` path. Keep research provenance in
the plan's `sources` field and mark AI reconstructions as illustrative.

## 微信推荐质量门禁

生成阶段即执行门禁：长文写入完成后，交互模式在进入排版/预览前先运行严格检查；贴图号每张图片由宿主 AI 或图片服务生成并回填后，立即运行图片质量检查。检查未通过时停止后续排版、批量生成或发布；贴图号报告写入当前 `card_plan.json` 状态。最终发布入口仍会再次复检。

公众号长文和独立贴图号在创建草稿前都必须经过推荐质量门禁。它与反 AI
评分和一般合规检查相互独立，重点检查同质化、搬运改写、信息增量不足、
低价值 AIGC、标题正文不匹配、事实来源不足和图片质量风险。门禁不承诺
微信官方推荐，只表示当前检查范围内未发现明显阻断项。

```bash
python -m toolkit.cli recommendation-check article.md --strict
python -m toolkit.cli recommendation-check article.md --history-dir ./history
```

`needs_revision` 和 `blocked` 在严格发布路径会停止草稿创建。没有历史索引时
必须显示“无法证明与历史内容不重复”，不能把未知当作原创通过。详细规则见
`references/recommendation-quality.md`。
