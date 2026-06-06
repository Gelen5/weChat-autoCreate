# 反AI写作规范

> 融合 wewrite 三层反AI写作规范，确保生成内容具备人类写作的统计特征、语言质感和内容深度。
> 每条规则映射到 `writing-config` 参数，供 Skill 运行时动态调控。

---

## 第一层：统计层（Statistical Layer）

统计层关注文本的数值特征，通过控制统计参数使生成文本在数据层面接近人类写作。

### 1.1 句长方差（Sentence Length Variance）

**规则**：人类写作的句长呈现显著波动，长短句交替使用。AI写作倾向均匀句长，需主动引入方差。

**参数映射**：`sentence_length_variance`

| 参数值 | 效果 | 适用场景 |
|--------|------|----------|
| `low` (0.3-0.5) | 句长较均匀 | 技术文档、学术分析 |
| `medium` (0.6-0.8) | 中等波动 | 常规公众号文章 |
| `high` (0.9-1.0) | 剧烈波动 | 情感文、故事型文章 |

**执行标准**：
- 相邻句子长度差 > 10字的比例不低于 30%
- 每500字内至少出现1句 ≤8字短句和1句 ≥35字长句
- 禁止连续3句长度差 <5字

**writing-config 参数**：
```yaml
sentence_length_variance: 0.75          # 句长方差系数
min_sentence_length: 4                  # 最短句字数
max_sentence_length: 55                 # 最长句字数
short_long_ratio: 0.3                   # 短句/长句比例下限
```

### 1.2 词汇温度（Vocabulary Temperature）

**规则**：人类用词有"温度"分布——常温词为主，穿插冷僻词和高频口语词。AI倾向中等温度词密集分布。

**参数映射**：`vocabulary_temperature`

| 温度区间 | 示例 | 占比建议 |
|----------|------|----------|
| 高温（口语/情绪词） | 离谱、炸裂、绝了、崩溃 | 15-20% |
| 常温（标准书面词） | 因此、需要、进行、发展 | 50-60% |
| 低温（冷僻/专业词） | 褫夺、滥觞、异质性、阈值 | 20-25% |

**执行标准**：
- 每500字至少出现1个高温词和1个低温词
- 禁止连续3句仅使用常温词
- 高温词优先用于情绪转折处

**writing-config 参数**：
```yaml
vocabulary_temperature: 0.7             # 整体温度系数（0=全冷 1=全热）
high_temp_ratio: 0.18                   # 高温词占比
low_temp_ratio: 0.22                    # 低温词占比
emotional_temp_boost: 0.15              # 情绪段落温度加成
```

### 1.3 段落节奏（Paragraph Rhythm）

**规则**：人类写作段落长度呈呼吸节奏——短段加速、长段舒缓、独立段制造停顿。

**参数映射**：`paragraph_rhythm`

| 段落类型 | 字数范围 | 功能 | 占比 |
|----------|----------|------|------|
| 独立段 | 1-15字 | 强调、转折、金句 | 10-15% |
| 短段 | 16-60字 | 加速推进、情绪爆发 | 25-30% |
| 中段 | 61-150字 | 主体论述 | 35-45% |
| 长段 | 151-300字 | 深度分析、故事铺陈 | 10-20% |

**执行标准**：
- 每500字至少1个独立段
- 禁止连续3段为同类型
- 文章开头前3段必须含独立段或短段
- 文末最后2段必须含独立段

**writing-config 参数**：
```yaml
paragraph_rhythm: "breathing"           # 节奏模式：breathing/steady/variable
standalone_paragraph_ratio: 0.12        # 独立段占比
short_paragraph_ratio: 0.28             # 短段占比
long_paragraph_ratio: 0.15              # 长段占比
rhythm_break_interval: 3                # 每N段必须节奏变化
```

### 1.4 情绪极性（Emotional Polarity）

**规则**：人类写作的情绪不是线性递进，而是波动前进。需控制情绪曲线的振幅和频率。

**参数映射**：`emotional_polarity`

| 极性 | 描述 | 信号词 |
|------|------|--------|
| 强正 | 激动、振奋 | 终于、居然、太 | 
| 弱正 | 温暖、认可 | 其实、还好、也不错 |
| 中性 | 客观、叙述 | 也就是说、具体来看 |
| 弱负 | 疑虑、不满 | 可是、但、总感觉 |
| 强负 | 愤怒、绝望 | 凭什么、离谱、崩溃 |

**执行标准**：
- 全文情绪极性必须呈波动曲线，禁止单调递增或递减
- 情绪转折点（极性翻转）每800-1200字至少1次
- 开头和结尾极性差值 ≥2（如开头弱负→结尾弱正）
- 禁止连续3段同极性

**writing-config 参数**：
```yaml
emotional_polarity_range: 0.8          # 情绪振幅（0=平稳 1=剧烈）
polarity_flip_interval: 1000           # 极性翻转间隔（字数）
opening_polarity: "weak_negative"      # 开头极性偏好
closing_polarity: "weak_positive"      # 结尾极性偏好
```

### 1.5 副词密度（Adverb Density）

**规则**：AI写作的一个显著特征是副词过度使用（特别是程度副词和方式副词）。人类写作副词密度更低且分布不均。

**参数映射**：`adverb_density`

| 副词类别 | AI典型密度 | 人类典型密度 | 目标 |
|----------|-----------|-------------|------|
| 程度副词（非常、极其、十分） | 3.2% | 1.1% | ≤1.5% |
| 方式副词（认真地、仔细地） | 2.8% | 0.9% | ≤1.2% |
| 时间副词（已经、正在、曾经） | 2.1% | 1.5% | ≤1.8% |

**重点禁用/替换列表**：

| 禁用副词 | 替换方案 |
|----------|----------|
| 非常 | （直接删除或用具体描述替代） |
| 极其 | （改用数字/事实） |
| 十分 | （删除或用"够"替代） |
| 深刻地 | （改用动词：影响→重塑） |
| 有效地 | （删除，用事实证明） |
| 显著地 | （改用数字对比） |

**执行标准**：
- 程度副词密度 ≤1.5%
- 每500字程度副词不超过3个
- 优先用动词/名词替代副词+弱动词组合

**writing-config 参数**：
```yaml
adverb_density_max: 0.015              # 副词密度上限
degree_adverb_max_per_500: 3           # 每500字程度副词上限
adverb_replacement_enabled: true       # 启用副词自动替换
```

### 1.6 风格漂移（Style Drift）

**规则**：人类长文写作中风格会自然微漂（口语化↔书面化、严肃↔轻松），AI倾向于全程风格一致。需刻意引入风格漂移。

**参数映射**：`style_drift`

| 漂移类型 | 触发条件 | 效果 |
|----------|----------|------|
| 口语注入 | 论述3段后 | 插入口语化表达或反问句 |
| 书面回归 | 连续2段口语后 | 回归严谨论述 |
| 轻松调剂 | 深度分析2段后 | 插入类比或幽默 |
| 严肃拉升 | 连续轻松内容后 | 升格为价值判断 |

**执行标准**：
- 每1000字至少1次风格漂移
- 漂移幅度不宜过大（同段落内不漂移）
- 漂移位置优先在段落交接处

**writing-config 参数**：
```yaml
style_drift_enabled: true              # 启用风格漂移
style_drift_interval: 1000             # 漂移间隔（字数）
drift_intensity: "subtle"              # 漂移强度：subtle/moderate
```

---

## 第二层：语言层（Linguistic Layer）

语言层关注文本的用词和句式，通过词汇和语法层面的控制消除AI痕迹。

### 2.1 禁用词列表（Banned Words List）

**规则**：AI写作有大量高频"AI味"词汇，必须全面禁用或替换。

#### 2.1.1 绝对禁用词（Strict Ban）

以下词汇在任何语境下都不得出现：

| 禁用词 | 原因 |
|--------|------|
| 值得注意的是 | AI标志性转折 |
| 综上所述 | AI标志性总结 |
| 总的来说 | AI标志性总结 |
| 需要指出的是 | AI标志性强调 |
| 不可忽视 | AI标志性强调 |
| 毋庸置疑 | AI标志性肯定 |
| 与此同时 | AI标志性并列 |
| 在当今社会 | AI标志性开头 |
| 随着时代的发展 | AI标志性开头 |
| 众所周知 | AI标志性预设 |
| 毋庸讳言 | AI标志性预设 |
| 不难发现 | AI标志性推导 |
| 由此可见 | AI标志性推导 |
| 深刻地认识到 | AI标志性感悟 |
| 本质上 | AI标志性抽象 |
| 从根本上说 | AI标志性抽象 |
| 毋庸置疑地 | AI标志性肯定 |
| 在某种意义上 | AI标志性限定 |
| 归根结底 | AI标志性总结 |

#### 2.1.2 条件禁用词（Conditional Ban）

以下词汇在特定条件下需替换：

| 禁用词 | 替换方案 | 适用条件 |
|--------|----------|----------|
| 然而 | 但/可/只是 | 非正式文章 |
| 此外 | 另外/还有/再说 | 非正式文章 |
| 因此 | 所以/这就/于是 | 口语化段落 |
| 并且 | 而且/另外 | 口语化段落 |
| 通过这种方式 | 这样一来/这么搞 | 口语化段落 |
| 在此基础上 | 在这之上/接着 | 口语化段落 |
| 显然 | 一看就知道/谁都明白 | 轻松段落 |
| 事实上 | 其实/说真的 | 非学术文章 |

**writing-config 参数**：
```yaml
banned_words_strict: true              # 启用绝对禁用词检查
banned_words_conditional: true         # 启用条件禁用词检查
banned_words_custom: []                # 自定义禁用词（用户可扩展）
```

### 2.2 碎句注入（Fragment Injection）

**规则**：人类写作会使用不完整句（碎句）制造节奏感和强调效果。AI几乎不生成碎句。

**碎句类型**：

| 类型 | 示例 | 使用频率 |
|------|------|----------|
| 名词碎句 | 三天。三个月。三百万。 | 每800字1-2个 |
| 动词碎句 | 走。现在就走。 | 每1000字1个 |
| 感叹碎句 | 绝了。真的绝了。 | 每800字1个 |
| 反问碎句 | 凭什么？ | 每1200字1个 |
| 顿号碎句 | 没有犹豫，没有退缩，没有。 | 每1500字1个 |

**执行标准**：
- 每1000字至少1个碎句
- 碎句必须独立成段或紧跟在长句之后
- 禁止连续2个碎句（除非刻意制造排比效果）

**writing-config 参数**：
```yaml
fragment_injection_enabled: true       # 启用碎句注入
fragment_density: 0.001                # 碎句密度（每字碎句数）
fragment_types_allowed:                # 允许的碎句类型
  - noun_fragment
  - verb_fragment
  - exclamation_fragment
  - rhetorical_fragment
  - pause_fragment
```

### 2.3 意外词汇（Unexpected Vocabulary）

**规则**：人类写作会在正式文本中偶然出现"非预期"词汇（俚语、古词、方言、行话），这种意外感是AI写作缺失的。

**意外词汇来源**：

| 来源 | 示例 | 注入场景 |
|------|------|----------|
| 网络俚语 | 社死、摆烂、卷王、润了 | 年轻受众文章 |
| 古文残词 | 殊不知、诚然、呜呼 | 严肃评论文章 |
| 方言表达 | 搞不赢、得不偿失咧 | 故事型/生活类文章 |
| 行话术语 | 底层逻辑、颗粒度、对齐 | 职场/行业文章 |
| 反常搭配 | 柔软的刀、沉默的爆炸 | 文学性较强的文章 |

**执行标准**：
- 每1500字至少1个意外词汇
- 意外词汇必须与上下文语境兼容（语义不冲突）
- 同一意外词汇全文不重复

**writing-config 参数**：
```yaml
unexpected_vocab_enabled: true         # 启用意外词汇
unexpected_vocab_interval: 1500        # 意外词汇间隔（字数）
unexpected_vocab_sources:              # 意外词汇来源权重
  slang: 0.3
  archaic: 0.2
  dialect: 0.2
  jargon: 0.2
  novel_collocation: 0.1
```

### 2.4 连贯性断裂（Coherence Break）

**规则**：人类写作偶尔出现轻微的逻辑跳跃或话题转移（"对了"、"说起来"、"另外提一嘴"），AI写作过于丝滑。

**断裂类型**：

| 类型 | 标记词 | 示例 |
|------|--------|------|
| 话题跳跃 | 对了、说起来 | "说起来，这让我想到..." |
| 补充插入 | 顺便说一句、插一句 | "顺便说一句，这个数据..." |
| 自我打断 | 等一下、不对 | "等一下，我重新想了一下..." |
| 话题回归 | 刚才说到哪了 | "扯远了，回到正题..." |

**执行标准**：
- 每2000字允许1-2次轻微连贯性断裂
- 断裂必须在前2句内回归主线
- 文章前1/3和最后1/4不使用断裂
- 禁止使用断裂来掩盖逻辑缺陷

**writing-config 参数**：
```yaml
coherence_break_enabled: true          # 启用连贯性断裂
coherence_break_interval: 2000         # 断裂间隔（字数）
coherence_break_max_per_article: 3     # 每篇断裂上限
coherence_break_return_within: 2       # 断裂后N句内回归
```

---

## 第三层：内容层（Content Layer）

内容层关注文本的信息质量和深度，通过内容层面的控制确保生成内容具备真实感和信息密度。

### 3.1 真实信息锚定（Real Information Anchoring）

**规则**：AI写作最大破绽是信息空洞——缺乏具体人名、地名、数字、时间。必须用真实信息锚点"钉住"内容。

**锚点类型**：

| 锚点类型 | 要求 | 示例 |
|----------|------|------|
| 人物锚点 | 具体人名+身份 | "字节跳动CEO梁汝波"而非"某大厂负责人" |
| 数据锚点 | 具体数字+来源 | "2025年Q1财报显示营收增长23%" |
| 时间锚点 | 具体日期/时段 | "2025年3月"而非"近年来" |
| 地点锚点 | 具体地点名 | "深圳南山科技园"而非"某科技园区" |
| 事件锚点 | 具体事件名 | "微信公开课PRO"而非"某行业大会" |

**执行标准**：
- 每500字至少2个信息锚点
- 核心论点必须包含至少1个数据锚点
- 人物锚点优先使用可验证的公开信息
- 如无法确认具体信息，使用 WebSearch 查证

**writing-config 参数**：
```yaml
info_anchor_enabled: true              # 启用信息锚定
info_anchor_density: 2                 # 每500字锚点数下限
info_anchor_types_required:            # 必须包含的锚点类型
  - data_anchor                        # 数据锚点（必选）
  - person_anchor                      # 人物锚点
  - time_anchor                        # 时间锚点
info_anchor_web_search: true           # 允许WebSearch查证锚点
```

### 3.2 具体性注入（Specificity Injection）

**规则**：AI写作倾向于抽象概括，人类写作偏好具体描述。需将抽象表述转化为具体可感的细节。

**转化规则**：

| 抽象表述 | 具体化方案 | 示例 |
|----------|-----------|------|
| "很多人" | 给出数量或比例 | "超过3000万用户" |
| "最近" | 给出时间范围 | "过去30天" |
| "大幅增长" | 给出具体数字 | "增长了47%" |
| "某知名企业" | 给出企业名 | "华为" |
| "显著提升" | 给出对比数据 | "从12%提升到31%" |
| "取得了不错的效果" | 给出量化指标 | "转化率翻了一倍" |

**五感具体化**：

| 感官 | 触发场景 | 示例 |
|------|----------|------|
| 视觉 | 描述场景 | "办公室只剩3盏灯亮着" |
| 听觉 | 描述氛围 | "键盘声此起彼伏" |
| 触觉 | 描述体验 | "手机烫得像暖手宝" |
| 味觉 | 描述感受 | "苦得像第一口黑咖啡" |
| 嗅觉 | 描述环境 | "空气里弥漫着咖啡豆的焦香" |

**执行标准**：
- 抽象表述具体化率 ≥60%
- 故事型/体验型文章五感具体化 ≥3处
- 每500字具体性注入 ≥2处

**writing-config 参数**：
```yaml
specificity_injection_enabled: true    # 启用具体性注入
abstraction_to_specific_ratio: 0.6     # 抽象→具体转化率下限
five_senses_enabled: true              # 启用五感具体化
five_senses_min_per_article: 3         # 每篇五感描述下限
```

### 3.3 信息密度波（Information Density Wave）

**规则**：人类写作的信息密度呈波浪形——有信息密集的"硬核段"和信息稀疏的"呼吸段"。AI写作信息密度过于均匀。

**密度分布**：

| 段落位置 | 密度目标 | 描述 |
|----------|----------|------|
| 开头1-2段 | 中等(0.6) | 用具体场景引入，不过度堆砌 |
| 第3-5段 | 高(0.9) | 核心论据密集呈现 |
| 中间过渡 | 低(0.3) | 让读者消化，类比/故事 |
| 主体论述 | 高(0.85) | 信息密集 |
| 金句前 | 低(0.2) | 为金句蓄势 |
| 金句 | 高(1.0) | 信息极致浓缩 |
| 结尾前1段 | 低(0.3) | 回味/展望 |
| 结尾段 | 中高(0.7) | 升华但不空洞 |

**执行标准**：
- 信息密度波必须与段落节奏和情绪极性联动
- 禁止连续3段高密度（≥0.8）或低密度（≤0.3）
- 金句段的密度必须为前后局部最大值

**writing-config 参数**：
```yaml
density_wave_enabled: true             # 启用信息密度波
density_wave_pattern: "pulse"          # 波形模式：pulse/escalate/breathe
high_density_threshold: 0.8            # 高密度阈值
low_density_threshold: 0.3             # 低密度阈值
max_consecutive_high: 2                # 连续高密度段上限
max_consecutive_low: 2                 # 连续低密度段上限
```

### 3.4 维度随机化（Dimension Randomization）

**规则**：AI写作的论述维度过于规律（总是从宏观到微观，或总是从A到B到C）。人类写作的维度切换更随机。

**维度类型**：

| 维度 | 视角 | 示例 |
|------|------|------|
| 时间维度 | 过去/现在/未来 | "十年前...而现在...未来可能..." |
| 空间维度 | 此地/彼地/全局 | "在深圳...在硅谷...全球范围..." |
| 角色维度 | 用户/平台/监管 | "对用户来说...对平台而言...从监管角度..." |
| 层级维度 | 个体/组织/行业 | "一个产品经理...一家公司...整个行业..." |
| 情理维度 | 理性/感性/直觉 | "逻辑上...情感上...直觉告诉我..." |

**随机化规则**：

| 规则 | 描述 |
|------|------|
| 起始维度随机 | 文章开始的论述维度不固定 |
| 跳跃允许 | 允许跨维度跳跃（如从角色直接跳到时间） |
| 非对称分布 | 维度占比不必均匀 |
| 回旋增强 | 可在文章后段回旋到起始维度，形成闭环 |

**执行标准**：
- 每篇文章至少覆盖3个维度
- 维度切换间隔不超过800字
- 禁止按固定顺序遍历所有维度

**writing-config 参数**：
```yaml
dimension_random_enabled: true         # 启用维度随机化
dimension_min_coverage: 3              # 最少维度覆盖数
dimension_switch_interval: 800         # 维度切换间隔上限（字数）
dimension_order: "random"              # 维度顺序：random/fixed/partial
dimension_types:                       # 可用维度
  - time
  - space
  - role
  - level
  - reason_emotion
```

---

## writing-config 完整参数汇总

以下是18个核心 writing-config 参数及其说明：

| # | 参数名 | 类型 | 默认值 | 说明 |
|---|--------|------|--------|------|
| 1 | `sentence_length_variance` | float | 0.75 | 句长方差系数，控制长短句交替强度 |
| 2 | `vocabulary_temperature` | float | 0.7 | 词汇温度系数，0=全冷僻 1=全口语 |
| 3 | `paragraph_rhythm` | string | "breathing" | 段落节奏模式：breathing/steady/variable |
| 4 | `emotional_polarity_range` | float | 0.8 | 情绪振幅，控制情绪波动剧烈程度 |
| 5 | `adverb_density_max` | float | 0.015 | 副词密度上限 |
| 6 | `style_drift_enabled` | bool | true | 是否启用风格漂移 |
| 7 | `banned_words_strict` | bool | true | 是否启用严格禁用词检查 |
| 8 | `banned_words_conditional` | bool | true | 是否启用条件禁用词检查 |
| 9 | `fragment_injection_enabled` | bool | true | 是否启用碎句注入 |
| 10 | `unexpected_vocab_enabled` | bool | true | 是否启用意外词汇 |
| 11 | `coherence_break_enabled` | bool | true | 是否启用连贯性断裂 |
| 12 | `info_anchor_enabled` | bool | true | 是否启用信息锚定 |
| 13 | `info_anchor_density` | int | 2 | 每500字信息锚点数下限 |
| 14 | `specificity_injection_enabled` | bool | true | 是否启用具体性注入 |
| 15 | `density_wave_enabled` | bool | true | 是否启用信息密度波 |
| 16 | `dimension_random_enabled` | bool | true | 是否启用维度随机化 |
| 17 | `info_anchor_web_search` | bool | true | 是否允许WebSearch查证锚点 |
| 18 | `style_drift_interval` | int | 1000 | 风格漂移间隔（字数） |

### writing-config 示例配置

```yaml
writing-config:
  # 统计层
  sentence_length_variance: 0.75
  vocabulary_temperature: 0.7
  paragraph_rhythm: "breathing"
  emotional_polarity_range: 0.8
  adverb_density_max: 0.015
  style_drift_enabled: true
  style_drift_interval: 1000

  # 语言层
  banned_words_strict: true
  banned_words_conditional: true
  fragment_injection_enabled: true
  unexpected_vocab_enabled: true
  coherence_break_enabled: true

  # 内容层
  info_anchor_enabled: true
  info_anchor_density: 2
  specificity_injection_enabled: true
  density_wave_enabled: true
  dimension_random_enabled: true
  info_anchor_web_search: true
```
