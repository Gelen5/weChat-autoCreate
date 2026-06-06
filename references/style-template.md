# 风格配置字段 + 主题列表

> style.yaml 的完整字段说明和18个主题列表及描述。

---

## 一、style.yaml 字段说明

### 完整字段表

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `account_name` | string | 是 | - | 公众号名称 |
| `positioning` | string | 是 | - | 账号一句话定位 |
| `target_audience` | string | 是 | - | 目标读者描述 |
| `update_frequency` | string | 否 | "weekly" | 更新频率：daily/weekly/biweekly/monthly |
| `primary_persona` | string | 是 | "warm-editor" | 主写作人格ID |
| `secondary_persona` | string | 否 | null | 备选人格ID |
| `preferred_length` | string | 否 | "medium" | 文章长度偏好：short/medium/long |
| `preferred_length_range` | object | 否 | [1500,2500] | 字数范围 [min, max] |
| `core_topics` | array | 是 | [] | 核心话题领域（最多3个） |
| `oral_tolerance` | string | 否 | "moderate" | 口语化容忍度：low/moderate/high |
| `theme` | string | 否 | "default" | 视觉主题ID |
| `banned_topics` | array | 否 | [] | 禁止触及的话题 |
| `custom_banned_words` | array | 否 | [] | 自定义禁用词 |
| `signature_style` | string | 否 | "" | 标志性写作特征（如"每篇结尾有金句卡片"） |
| `cta_default` | string | 否 | "action" | 默认CTA类型：action/reflect/share/comment |
| `image_style` | string | 否 | "flat" | 配图风格：flat/illustration/photo/minimal |
| `color_scheme` | object | 否 | {} | 配色方案 |

### 字段详细说明

#### `primary_persona`（主写作人格）

可选值：
- `midnight-friend`：深夜朋友
- `warm-editor`：温暖主编
- `sharp-journalist`：锐利记者
- `cold-analyst`：冷静分析师
- `industry-observer`：行业观察者
- `humor-storyteller`：幽默说书人
- `tech-coder`：极客码农

#### `preferred_length`（文章长度偏好）

| 值 | 字数范围 | 适用场景 |
|----|----------|----------|
| `short` | 800-1500字 | 快读干货、热点速评 |
| `medium` | 1500-2500字 | 常规文章、深度分析 |
| `long` | 2500-4000字 | 深度长文、专题研究 |

#### `oral_tolerance`（口语化容忍度）

| 值 | 说明 | 词汇温度 |
|----|------|----------|
| `low` | 严格书面，几乎不口语 | 0.5 |
| `moderate` | 适度口语，不影响专业感 | 0.65 |
| `high` | 大量口语，轻松随意 | 0.8 |

#### `core_topics`（核心话题领域）

从18个主题列表中选择，最多3个。

#### `color_scheme`（配色方案）

```yaml
color_scheme:
  primary: "#1a1a2e"      # 主色调（背景/标题）
  secondary: "#16213e"    # 辅助色（副标题/边框）
  accent: "#e94560"       # 强调色（CTA/关键信息）
  text: "#333333"         # 正文文字色
  text_light: "#666666"   # 次要文字色
  background: "#ffffff"   # 背景色
  code_bg: "#2d2d2d"      # 代码块背景
  highlight: "#fff3cd"    # 高亮背景
```

### style.yaml 示例

```yaml
account_name: "AI工具测评站"
positioning: "专注AI工具的实测和推荐"
target_audience: "对AI工具感兴趣的职场人，25-40岁"
update_frequency: "weekly"
primary_persona: "warm-editor"
secondary_persona: "tech-coder"
preferred_length: "medium"
preferred_length_range: [1500, 2500]
core_topics:
  - "ai_tech"
  - "workplace_efficiency"
  - "industry_business"
oral_tolerance: "moderate"
theme: "tech_blue"
banned_topics: []
custom_banned_words: []
signature_style: "每篇结尾有1个金句卡片"
cta_default: "action"
image_style: "flat"
color_scheme:
  primary: "#1a1a2e"
  secondary: "#16213e"
  accent: "#e94560"
  text: "#333333"
  text_light: "#666666"
  background: "#ffffff"
  code_bg: "#2d2d2d"
  highlight: "#fff3cd"
```

---

## 二、18个主题列表

### 1. ai_tech（AI/科技）

| 属性 | 说明 |
|------|------|
| ID | `ai_tech` |
| 名称 | AI/科技 |
| 描述 | 人工智能技术、AI工具、科技趋势、技术应用 |
| 关键词 | AI、GPT、机器学习、深度学习、自动化、科技 |
| 适配人格 | tech-coder、industry-observer |
| 适配框架 | C清单型、E热点解读、D对比型 |
| 热度趋势 | 持续上升 |
| 更新频率建议 | 高频（每周1-2篇） |

### 2. workplace_efficiency（职场效率）

| 属性 | 说明 |
|------|------|
| ID | `workplace_efficiency` |
| 名称 | 职场效率 |
| 描述 | 工作方法、效率工具、时间管理、职场技能 |
| 关键词 | 效率、工具、时间管理、职场、方法论 |
| 适配人格 | warm-editor、tech-coder |
| 适配框架 | A痛点型、C清单型、G复盘/体验型 |
| 热度趋势 | 稳定 |
| 更新频率建议 | 中频（每周1篇） |

### 3. career_growth（职业发展）

| 属性 | 说明 |
|------|------|
| ID | `career_growth` |
| 名称 | 职业发展 |
| 描述 | 职业规划、跳槽转行、升职加薪、职业瓶颈 |
| 关键词 | 职业规划、跳槽、升职、转型、职业瓶颈 |
| 适配人格 | warm-editor、midnight-friend |
| 适配框架 | A痛点型、B故事型、D对比型 |
| 热度趋势 | 稳定 |
| 更新频率建议 | 中频 |

### 4. finance_invest（财务投资）

| 属性 | 说明 |
|------|------|
| ID | `finance_invest` |
| 名称 | 财务投资 |
| 描述 | 理财入门、投资策略、财务自由、消费观 |
| 关键词 | 理财、投资、财务自由、消费、攒钱 |
| 适配人格 | cold-analyst、warm-editor |
| 适配框架 | A痛点型、D对比型、C清单型 |
| 热度趋势 | 稳定偏高 |
| 更新频率建议 | 中频 |

### 5. personal_growth（个人成长）

| 属性 | 说明 |
|------|------|
| ID | `personal_growth` |
| 名称 | 个人成长 |
| 描述 | 读书方法、思维模型、自律习惯、认知升级 |
| 关键词 | 成长、认知、自律、读书、思维模型 |
| 适配人格 | midnight-friend、warm-editor |
| 适配框架 | A痛点型、B故事型、G复盘/体验型 |
| 热度趋势 | 稳定 |
| 更新频率建议 | 中低频 |

### 6. startup_business（创业商业）

| 属性 | 说明 |
|------|------|
| ID | `startup_business` |
| 名称 | 创业商业 |
| 描述 | 创业故事、商业模式、融资、商业案例 |
| 关键词 | 创业、商业模式、融资、案例、复盘 |
| 适配人格 | industry-observer、sharp-journalist |
| 适配框架 | B故事型、E热点解读、G复盘/体验型 |
| 热度趋势 | 波动 |
| 更新频率建议 | 中频 |

### 7. industry_analysis（行业分析）

| 属性 | 说明 |
|------|------|
| ID | `industry_analysis` |
| 名称 | 行业分析 |
| 描述 | 行业趋势、竞争格局、政策解读、行业报告 |
| 关键词 | 行业趋势、竞争、政策、报告、数据 |
| 适配人格 | industry-observer、cold-analyst |
| 适配框架 | E热点解读、D对比型、F纯观点型 |
| 热度趋势 | 稳定 |
| 更新频率建议 | 中频 |

### 8. product_design（产品设计）

| 属性 | 说明 |
|------|------|
| ID | `product_design` |
| 名称 | 产品设计 |
| 描述 | 产品思维、用户体验、设计方法、产品案例 |
| 关键词 | 产品经理、用户体验、设计、需求、迭代 |
| 适配人格 | warm-editor、tech-coder |
| 适配框架 | A痛点型、C清单型、G复盘/体验型 |
| 热度趋势 | 稳定 |
| 更新频率建议 | 低频 |

### 9. programming（编程开发）

| 属性 | 说明 |
|------|------|
| ID | `programming` |
| 名称 | 编程开发 |
| 描述 | 编程语言、开发框架、最佳实践、代码案例 |
| 关键词 | 编程、代码、框架、最佳实践、开发 |
| 适配人格 | tech-coder |
| 适配框架 | C清单型、G复盘/体验型、E热点解读 |
| 热度趋势 | 稳定 |
| 更新频率建议 | 中频 |

### 10. data_analytics（数据分析）

| 属性 | 说明 |
|------|------|
| ID | `data_analytics` |
| 名称 | 数据分析 |
| 描述 | 数据思维、分析方法、数据工具、可视化 |
| 关键词 | 数据、分析、可视化、指标、BI |
| 适配人格 | cold-analyst、tech-coder |
| 适配框架 | C清单型、E热点解读、D对比型 |
| 热度趋势 | 上升 |
| 更新频率建议 | 中频 |

### 11. marketing_brand（营销品牌）

| 属性 | 说明 |
|------|------|
| ID | `marketing_brand` |
| 名称 | 营销品牌 |
| 描述 | 营销策略、品牌建设、内容营销、增长黑客 |
| 关键词 | 营销、品牌、增长、内容、传播 |
| 适配人格 | industry-observer、warm-editor |
| 适配框架 | A痛点型、D对比型、G复盘/体验型 |
| 热度趋势 | 稳定 |
| 更新频率建议 | 中低频 |

### 12. life_philosophy（生活哲学）

| 属性 | 说明 |
|------|------|
| ID | `life_philosophy` |
| 名称 | 生活哲学 |
| 描述 | 生活态度、人生思考、生活方式、价值观 |
| 关键词 | 生活、态度、思考、价值观、选择 |
| 适配人格 | midnight-friend、humor-storyteller |
| 适配框架 | B故事型、F纯观点型、G复盘/体验型 |
| 热度趋势 | 稳定偏低 |
| 更新频率建议 | 低频 |

### 13. emotional_intelligence（情感心理）

| 属性 | 说明 |
|------|------|
| ID | `emotional_intelligence` |
| 名称 | 情感心理 |
| 描述 | 情绪管理、人际交往、心理洞察、情感故事 |
| 关键词 | 情绪、心理、人际关系、共情、沟通 |
| 适配人格 | midnight-friend、warm-editor |
| 适配框架 | A痛点型、B故事型、F纯观点型 |
| 热度趋势 | 稳定 |
| 更新频率建议 | 中频 |

### 14. education_learning（教育学习）

| 属性 | 说明 |
|------|------|
| ID | `education_learning` |
| 名称 | 教育学习 |
| 描述 | 学习方法、教育趋势、考试备考、知识管理 |
| 关键词 | 学习、教育、考试、知识管理、备考 |
| 适配人格 | warm-editor、cold-analyst |
| 适配框架 | A痛点型、C清单型、D对比型 |
| 热度趋势 | 季节性波动 |
| 更新频率建议 | 中频 |

### 15. health_wellness（健康生活）

| 属性 | 说明 |
|------|------|
| ID | `health_wellness` |
| 名称 | 健康生活 |
| 描述 | 健康管理、运动健身、饮食营养、睡眠心理 |
| 关键词 | 健康、运动、饮食、睡眠、压力 |
| 适配人格 | warm-editor、midnight-friend |
| 适配框架 | A痛点型、C清单型、G复盘/体验型 |
| 热度趋势 | 稳定 |
| 更新频率建议 | 低频 |

### 16. side_hustle（副业赚钱）

| 属性 | 说明 |
|------|------|
| ID | `side_hustle` |
| 名称 | 副业赚钱 |
| 描述 | 副业选择、赚钱方法、自由职业、收入多元化 |
| 关键词 | 副业、赚钱、自由职业、收入、变现 |
| 适配人格 | sharp-journalist、warm-editor |
| 适配框架 | A痛点型、D对比型、G复盘/体验型 |
| 热度趋势 | 高 |
| 更新频率建议 | 中高频 |

### 17. social_observation（社会观察）

| 属性 | 说明 |
|------|------|
| ID | `social_observation` |
| 名称 | 社会观察 |
| 描述 | 社会现象、热点事件、社会趋势、文化观察 |
| 关键词 | 社会、现象、趋势、文化、争议 |
| 适配人格 | sharp-journalist、industry-observer |
| 适配框架 | E热点解读、F纯观点型、D对比型 |
| 热度趋势 | 波动大 |
| 更新频率建议 | 热点驱动 |

### 18. digital_life（数字生活）

| 属性 | 说明 |
|------|------|
| ID | `digital_life` |
| 名称 | 数字生活 |
| 描述 | 数字工具、信息管理、数字断舍离、效率生活 |
| 关键词 | 数字化、工具、信息管理、断舍离、效率 |
| 适配人格 | tech-coder、warm-editor |
| 适配框架 | C清单型、A痛点型、G复盘/体验型 |
| 热度趋势 | 稳定上升 |
| 更新频率建议 | 中频 |

---

## 主题关联矩阵

| 主题 | 高关联主题 | 可混搭主题 |
|------|-----------|-----------|
| ai_tech | programming, data_analytics | workplace_efficiency, digital_life |
| workplace_efficiency | career_growth, digital_life | ai_tech, personal_growth |
| career_growth | personal_growth, finance_invest | workplace_efficiency |
| finance_invest | side_hustle, career_growth | data_analytics |
| personal_growth | career_growth, emotional_intelligence | education_learning |
| startup_business | industry_analysis, marketing_brand | finance_invest |
| industry_analysis | startup_business, ai_tech | data_analytics |
| product_design | programming, marketing_brand | ai_tech |
| programming | ai_tech, data_analytics | product_design |
| data_analytics | ai_tech, programming | industry_analysis |
| marketing_brand | startup_business, industry_analysis | content_creation |
| life_philosophy | emotional_intelligence, health_wellness | personal_growth |
| emotional_intelligence | personal_growth, life_philosophy | career_growth |
| education_learning | personal_growth, data_analytics | ai_tech |
| health_wellness | life_philosophy, emotional_intelligence | workplace_efficiency |
| side_hustle | finance_invest, career_growth | digital_life |
| social_observation | industry_analysis, life_philosophy | startup_business |
| digital_life | ai_tech, workplace_efficiency | side_hustle |
