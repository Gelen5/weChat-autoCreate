# 效果复盘流程

> 发布后的数据回填、分析和调整建议，形成"发布-反馈-优化"闭环。

---

## 流程概览

```
数据回填 → 数据分析 → 调整建议
```

---

## 步骤1：数据回填

### 1.1 需要回填的数据

| 数据项 | 来源 | 回填时机 |
|--------|------|----------|
| 阅读量 | 公众号后台 | 发布后24小时 |
| 完读率 | 公众号后台 | 发布后24小时 |
| 分享数 | 公众号后台 | 发布后24小时 |
| 收藏数 | 公众号后台 | 发布后24小时 |
| 评论数 | 公众号后台 | 发布后24小时 |
| 点赞数 | 公众号后台 | 发布后24小时 |
| 在看数 | 公众号后台 | 发布后24小时 |
| 长期阅读量 | 公众号后台 | 发布后7天 |
| 新增粉丝 | 公众号后台 | 发布后7天 |

### 1.2 数据格式

```yaml
article_metrics:
  article_id: "art_20250315_001"
  title: "为什么你总是存不下钱"
  publish_date: "2025-03-15"
  framework: "A痛点型"
  persona: "warm-editor"
  topic: "finance_invest"
  word_count: 2100

  metrics_24h:
    reads: 3500
    read_completion: 0.62        # 完读率
    shares: 180
    bookmarks: 95
    comments: 42
    likes: 210
    watches: 85

  metrics_7d:
    reads: 12000
    read_completion: 0.58
    shares: 520
    bookmarks: 280
    comments: 78
    likes: 580
    watches: 230
    new_followers: 35
```

### 1.3 回填触发

```yaml
metrics_collection:
  auto_remind:
    - "发布后24小时提醒回填24小时数据"
    - "发布后7天提醒回填7天数据"

  manual_trigger:
    - "/review 24h"   # 回填24小时数据
    - "/review 7d"    # 回填7天数据

  min_data_points:
    - "至少积累5篇文章的数据后才能做有效分析"
    - "不足5篇时给出单篇简评"
```

---

## 步骤2：数据分析

### 2.1 单篇文章分析

#### 核心指标评估

| 指标 | 计算方式 | 基准线 | 优秀线 |
|------|----------|--------|--------|
| 完读率 | 完读人数/阅读人数 | 50% | 70% |
| 分享率 | 分享数/阅读人数 | 3% | 8% |
| 评论率 | 评论数/阅读人数 | 1% | 3% |
| 点赞率 | 点赞数/阅读人数 | 4% | 8% |
| 收藏率 | 收藏数/阅读人数 | 2% | 5% |

#### 维度归因分析

| 维度 | 分析内容 | 方法 |
|------|----------|------|
| 标题效果 | 阅读量与平均阅读量的对比 | 高于平均=标题好，低于=标题差 |
| 内容质量 | 完读率与基准线对比 | 低于50%=内容问题 |
| 传播力 | 分享率与基准线对比 | 低于3%=传播力差 |
| 互动性 | 评论率与基准线对比 | 低于1%=互动差 |
| 价值感 | 收藏率与基准线对比 | 低于2%=价值感差 |

#### 异常指标诊断

| 异常 | 可能原因 | 验证方法 |
|------|----------|----------|
| 阅读量高+完读率低 | 标题党/开头弱 | 检查标题vs内容匹配度 |
| 完读率高+分享率低 | 内容好但无传播点 | 检查是否有社交货币元素 |
| 分享率高+完读率低 | 传播点在开头 | 分析分享发生在哪些位置 |
| 评论率高+阅读量低 | 受众精准但面窄 | 检查话题是否过于垂直 |
| 收藏率高+分享率低 | 实用但不值得炫耀 | 正常现象，持续做 |

### 2.2 跨文章对比分析

#### 框架对比

```yaml
framework_comparison:
  dimensions:
    - avg_read_completion: "各框架平均完读率"
    - avg_share_rate: "各框架平均分享率"
    - avg_comment_rate: "各框架平均评论率"

  analysis:
    - "哪个框架的完读率最高？"
    - "哪个框架的传播力最强？"
    - "哪个框架的互动最好？"
    - "是否有框架持续表现差？"

  recommendation:
    - "增加表现好的框架使用频率"
    - "减少或优化表现差的框架"
    - "尝试框架组合（如A+B混合）"
```

#### 人格对比

```yaml
persona_comparison:
  dimensions:
    - avg_metrics: "各人格的关键指标平均"
    - consistency: "各人格的表现稳定性"

  analysis:
    - "哪个人格的完读率最高？"
    - "哪个人格的传播力最强？"
    - "是否有人格不适合当前受众？"

  recommendation:
    - "增加表现好的人格使用频率"
    - "调整表现差的人格参数"
    - "尝试人格混搭"
```

#### 话题对比

```yaml
topic_comparison:
  dimensions:
    - avg_reads: "各话题平均阅读量"
    - avg_engagement: "各话题平均互动率"

  analysis:
    - "哪个话题阅读量最高？"
    - "哪个话题互动最好？"
    - "是否有冷门话题可以放弃？"

  recommendation:
    - "增加热门话题产出频率"
    - "冷门话题尝试新角度"
    - "发现话题趋势变化"
```

### 2.3 趋势分析

```yaml
trend_analysis:
  time_windows:
    - weekly: "近7天趋势"
    - monthly: "近30天趋势"
    - quarterly: "近90天趋势"

  metrics:
    - reads_trend: "阅读量趋势"
    - completion_trend: "完读率趋势"
    - share_trend: "分享率趋势"
    - follower_trend: "粉丝增长趋势"

  patterns:
    - rising: "持续上升→保持策略"
    - declining: "持续下降→需调整"
    - stable: "稳定→尝试突破"
    - volatile: "波动大→找规律"
```

---

## 步骤3：调整建议

### 3.1 建议生成规则

| 条件 | 建议类型 | 示例 |
|------|----------|------|
| 完读率持续<50% | 内容结构调整 | "缩短段落，增加节奏锚点" |
| 分享率持续<3% | 传播力提升 | "增加社交货币元素（金句/数据/争议点）" |
| 评论率持续<1% | 互动性提升 | "增加提问CTA，降低评论门槛" |
| 阅读量持续下降 | 选题/标题优化 | "调整选题方向，测试新标题模板" |
| 某框架表现差 | 框架调整 | "减少{框架}使用，或调整{框架}参数" |
| 某人格表现差 | 人格调整 | "切换人格或调整人格参数" |

### 3.2 调整建议模板

```yaml
adjustment_suggestion:
  id: "sug_20250330_001"
  based_on: "最近10篇文章数据"
  priority: "high"

  findings:
    - finding: "完读率平均48%，低于基准线50%"
      severity: "medium"
      possible_cause: "段落过长，中间部分信息密度不足"

    - finding: "A痛点型框架完读率55%，C清单型仅40%"
      severity: "high"
      possible_cause: "C框架内容过于干瘪，缺少情感连接"

  recommendations:
    - action: "调整writing-config: paragraph_rhythm"
      detail: "增加独立段比例从12%到18%"
      expected_effect: "完读率提升3-5%"

    - action: "优化C清单型框架"
      detail: "每个清单项增加1个案例/故事"
      expected_effect: "C框架完读率提升8-10%"

    - action: "增加金句分布"
      detail: "每800字设置1个金句/数据冲击"
      expected_effect: "分享率提升1-2%"

  config_changes:
    - key: "paragraph_rhythm.standalone_paragraph_ratio"
      from: 0.12
      to: 0.18

    - key: "framework_config.C.case_per_item"
      from: 0
      to: 1
```

### 3.3 建议执行流程

```yaml
suggestion_execution:
  step_1_present:
    action: "向用户展示建议"
    format: "自然语言+数据支撑"

  step_2_confirm:
    action: "等待用户确认"
    options:
      - "全部接受"
      - "部分接受（选择哪些建议）"
      - "暂不调整"

  step_3_apply:
    action: "修改配置"
    scope: "仅修改用户确认的部分"

  step_4_track:
    action: "后续文章追踪效果"
    compare_window: "3-5篇"
    metric: "目标指标是否改善"

  step_5_report:
    action: "效果反馈"
    content:
      - "调整前 vs 调整后指标对比"
      - "是否达到预期效果"
      - "下一步建议"
```

### 3.4 调整优先级

| 优先级 | 调整类型 | 触发条件 |
|--------|----------|----------|
| P0 紧急 | 标题优化 | 阅读量持续低于平均50% |
| P1 高 | 内容结构调整 | 完读率持续低于基准线 |
| P2 中 | 传播力优化 | 分享率持续低于基准线 |
| P3 低 | 框架/人格微调 | 某维度持续略低于基准 |
| P4 观察 | 趋势性调整 | 趋势分析发现变化苗头 |

---

## 复盘报告模板

```yaml
review_report:
  period: "2025年3月"
  articles_count: 8
  avg_metrics:
    reads: 4200
    read_completion: 0.56
    share_rate: 0.042
    comment_rate: 0.015
    bookmark_rate: 0.028

  vs_last_period:
    reads: "+12%"
    read_completion: "+3%"
    share_rate: "-0.5%"
    comment_rate: "+0.3%"

  highlights:
    - "完读率提升3%，得益于段落节奏调整"
    - "A痛点型表现持续最好（完读率62%）"

  concerns:
    - "分享率略降，C清单型文章传播力不足"

  top_performer:
    title: "为什么你总是存不下钱"
    framework: "A痛点型"
    read_completion: 0.68
    share_rate: 0.065

  recommendations:
    - "增加A痛点型文章比例（从25%→35%）"
    - "C清单型增加案例段落"
    - "标题测试反常识模板"
```
