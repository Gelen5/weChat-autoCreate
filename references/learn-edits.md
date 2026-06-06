# 学习飞轮流程

> 从编辑记录中持续学习用户偏好，形成"写作-反馈-学习"的飞轮闭环。

---

## 流程概览

```
获取初稿+终稿 → diff分析 → 模式提取 → 置信度评分 → 每5个lesson更新playbook
```

---

## 步骤1：获取初稿+终稿

### 数据来源

| 来源 | 说明 | 获取方式 |
|------|------|----------|
| 用户编辑记录 | 用户对AI初稿的修改 | 保存初稿和修改后终稿 |
| 用户直接提供的样本 | 用户手动提供的"理想文稿" | 用户上传/粘贴 |
| 历史发布文章 | 已发布的公众号文章 | 用户授权导入 |

### 数据格式

```yaml
edit_pair:
  id: "edit_20250315_001"
  article_title: "为什么你总是存不下钱"
  framework: "A痛点型"
  persona: "warm-editor"

  draft: |
    [AI生成的初稿全文]

  final: |
    [用户修改后的终稿全文]

  metadata:
    edit_date: "2025-03-15"
    word_count_draft: 2100
    word_count_final: 1850
    edit_ratio: 0.12    # 修改字数/总字数
```

### 采集规则

| 规则 | 说明 |
|------|------|
| 最小修改量 | edit_ratio ≥ 5% 才采集（微调不算） |
| 最大修改量 | edit_ratio ≤ 70%（超过说明初稿完全不可用） |
| 成对保存 | 初稿和终稿必须完整保存，不可只保存diff |
| 元数据完整 | 必须包含框架类型和人格信息 |

---

## 步骤2：diff分析

### 分析维度

#### 2.1 词汇级diff

**分析内容**：哪些词被替换了

```yaml
word_diff:
  replacements:
    - original: "值得注意的是"
      replaced: "注意"
      category: "banned_word_fix"

    - original: "非常"
      replaced: "够"
      category: "adverb_simplification"

    - original: "深刻地"
      replaced: "（删除）"
      category: "adverb_removal"

  additions:
    - added: "说真的"
      position: "段落开头"
      category: "oral_insertion"

    - added: "凌晨3点"
      position: "场景描述"
      category: "specificity_injection"

  deletions:
    - deleted: "综上所述"
      category: "banned_word_removal"
```

#### 2.2 句式级diff

**分析内容**：句式结构如何改变

```yaml
syntax_diff:
  - type: "long_to_short"
    original: "虽然这个方法在大多数情况下都是有效的，但是也有一些例外情况需要考虑"
    changed: "这方法管用。但有例外。"
    pattern: "长复合句→碎句组合"

  - type: "statement_to_question"
    original: "这说明方法很重要"
    changed: "方法重要吗？太重要了。"
    pattern: "陈述→设问"

  - type: "abstract_to_concrete"
    original: "很多人都有这样的经历"
    changed: "10个打工人里8个有过这种经历"
    pattern: "抽象→具体数字"
```

#### 2.3 结构级diff

**分析内容**：段落/结构如何调整

```yaml
structure_diff:
  paragraph_changes:
    - type: "split"
      original: "1个长段(180字)"
      changed: "1个短段(60字) + 1个独立段(12字)"
      pattern: "长段拆分+独立段插入"

    - type: "reorder"
      original: "论据A → 论据B → 结论"
      changed: "结论 → 论据B → 论据A"
      pattern: "结论前置"

    - type: "insert"
      position: "第3段后"
      content: "插入了一个个人经历段(80字)"
      pattern: "personal_experience_insertion"
```

#### 2.4 情绪级diff

**分析内容**：情绪表达如何变化

```yaml
emotion_diff:
  - type: "intensity_increase"
    original: "这个现象值得关注"
    changed: "这事儿不能忍"
    pattern: "弱化→强化情绪"

  - type: "add_conflict"
    position: "第5段"
    original: "纯客观分析"
    changed: "插入1句反问，增加情绪张力"
    pattern: "客观→张力增加"
```

---

## 步骤3：模式提取

### 提取方法

从diff分析中提取**可复用的写作模式**，每个模式包含：

```yaml
lesson:
  id: "lesson_001"
  category: "vocabulary"        # vocabulary/syntax/structure/emotion/style
  pattern: "副词删除倾向"        # 模式名称
  description: "用户倾向于删除程度副词而非替换"
  examples:
    - "非常→（删除）"
    - "极其→（删除）"
    - "十分→（删除）"
  confidence: 0.9               # 置信度
  frequency: 5                  # 出现次数
  source_edits:                 # 来源编辑记录
    - "edit_20250315_001"
    - "edit_20250318_002"
    - "edit_20250320_003"
    - "edit_20250322_004"
    - "edit_20250325_005"
```

### 模式分类

| 类别 | 示例模式 | 检测方法 |
|------|----------|----------|
| vocabulary | 副词偏好、禁用词补充、口语词偏好 | 词汇替换diff统计 |
| syntax | 碎句偏好、设问偏好、句长偏好 | 句式diff统计 |
| structure | 段落长度偏好、结构重排偏好 | 结构diff统计 |
| emotion | 情绪强度偏好、转折偏好 | 情绪diff统计 |
| style | 人格偏移、调性偏好 | 综合diff分析 |

### 模式提取规则

| 规则 | 说明 |
|------|------|
| 最小样本 | 同一模式出现≥3次才提取 |
| 模式粒度 | 不太粗（"用户喜欢改东西"）也不太细（"用户把X改成Y"） |
| 可操作性 | 每个模式必须能转化为具体写作规则 |
| 不冲突 | 新模式不能与已有模式矛盾 |

---

## 步骤4：置信度评分

### 评分维度

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 频率 | 30% | 出现次数：1次=10, 2次=30, 3次=50, 5次=70, 10次+=90 |
| 一致性 | 30% | 是否每次都做相同修改：全部一致=90, 80%一致=70, 60%=50 |
| 广泛性 | 20% | 是否跨文章类型：仅1类=40, 2类=60, 3类+=80 |
| 近期性 | 20% | 最近5篇出现=90, 10篇内=70, 20篇内=50, 更早=30 |

### 置信度等级

| 等级 | 分值 | 处理方式 |
|------|------|----------|
| 高置信 | ≥80 | 直接写入playbook |
| 中置信 | 60-79 | 写入playbook但标记为"待验证" |
| 低置信 | 40-59 | 暂不写入，继续观察 |
| 待观察 | <40 | 不记录，等更多数据 |

### 置信度衰减

```yaml
confidence_decay:
  rule: "每30天未再次验证，置信度下降10分"
  min_confidence: 30    # 低于30分自动移除
  revalidation:
    trigger: "下次编辑中出现相同模式"
    action: "置信度恢复到60（中置信）"
```

---

## 步骤5：每5个lesson更新playbook

### 更新触发

| 触发条件 | 动作 |
|----------|------|
| 新增5个lesson | 执行playbook更新 |
| 现有lesson置信度变化 | 执行playbook更新 |
| 用户手动请求 | 执行playbook更新 |

### 更新流程

```yaml
playbook_update:
  step_1_aggregate:
    action: "汇总所有lesson"
    filter: "置信度≥60"

  step_2_conflict_check:
    action: "检查新模式与现有规则的冲突"
    resolution:
      - "新模式覆盖旧规则（如果新模式置信度更高）"
      - "保留两条规则但标注优先级"
      - "合并为更通用的规则"

  step_3_categorize:
    action: "按类别整理规则"
    categories:
      - vocabulary_rules    # 词汇偏好规则
      - syntax_rules        # 句式偏好规则
      - structure_rules     # 结构偏好规则
      - emotion_rules       # 情绪偏好规则
      - style_rules         # 风格偏好规则

  step_4_generate_playbook:
    action: "生成更新后的playbook"
    format: "YAML"
    output: "config/playbook.yaml"

  step_5_validate:
    action: "用最近1篇编辑验证playbook效果"
    metric: "修改率降低（目标：修改率从12%降至8%以下）"

  step_6_report:
    action: "向用户报告更新内容"
    content:
      - "新增规则N条"
      - "修改规则N条"
      - "删除规则N条"
      - "预期效果"
```

### playbook 格式

```yaml
playbook:
  version: "1.3"
  last_updated: "2025-03-30"
  total_lessons: 15

  vocabulary_rules:
    - rule: "删除程度副词而非替换"
      confidence: 92
      source: "lesson_001, lesson_003, lesson_007"
      action: "遇到'非常/极其/十分'等程度副词时直接删除"

    - rule: "偏好口语化转折"
      confidence: 85
      source: "lesson_002, lesson_005"
      action: "将'然而'替换为'但'或'可'"

  syntax_rules:
    - rule: "偏好碎句"
      confidence: 78
      source: "lesson_004, lesson_006, lesson_008"
      action: "长复合句拆分为2-3个短句"

    - rule: "偏好设问句"
      confidence: 72
      source: "lesson_009, lesson_010"
      action: "将部分陈述句改为设问句"
      status: "待验证"

  structure_rules:
    - rule: "偏好结论前置"
      confidence: 88
      source: "lesson_011, lesson_013, lesson_014"
      action: "先给结论，再展开论据"

  emotion_rules:
    - rule: "偏好中等偏强情绪"
      confidence: 80
      source: "lesson_012, lesson_015"
      action: "情绪极性范围调高至0.85"

  style_rules: []
```

---

## 飞轮加速策略

| 策略 | 说明 | 效果 |
|------|------|------|
| 主动求反馈 | 写完后主动询问"这个表达你觉得如何？" | 增加edit_pair数量 |
| A/B测试 | 同一段落提供2种写法，让用户选择 | 快速积累偏好数据 |
| 对比引导 | "我注意到你上次把X改成了Y，这次也这样吗？" | 验证模式一致性 |
| 周期回顾 | 每10篇文章做一次用户偏好回顾 | 用户感知到学习效果 |
