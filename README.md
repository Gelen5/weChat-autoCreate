# 全宇宙最屌的微信公众号全链路自动化生成 Skill

> 从一个选题想法到一篇排版精美、原创度高、自动发布的微信公众号文章——只需一条指令。

---

## 三大核心创新

| # | 创新点 | 说明 |
|---|--------|------|
| 1 | **AI 现场手写排版** | 不是模板套壳，是 AI 根据文章语义实时生成排版指令——每篇文章的样式都是"手写"的、独一无二的 |
| 2 | **3 层反 AI 评分 + 学习飞轮** | base → authentic → publish 三层递进式去 AI 痕迹，每次发布后自动采集评分数据回灌提示词，形成越用越好的飞轮 |
| 3 | **43 模块 + 18 主题排版系统** | 43 个可组合排版组件 × 18 套预设主题 = 774 种风格组合，覆盖从极简到华丽的一切审美需求 |

---

## 功能特性：8 步全链路覆盖

```
选题 → 大纲 → 撰稿 → 去AI化 → 配图 → 排版 → 预览 → 发布
 ①      ②      ③       ④       ⑤      ⑥      ⑦      ⑧
```

| 步骤 | 功能 | 说明 |
|------|------|------|
| ① 选题 | 智能选题生成 | 基于热点、行业趋势、历史数据推荐选题，支持自定义选题方向 |
| ② 大纲 | 结构化大纲生成 | 自动生成逻辑清晰的文章大纲，支持多级标题和段落规划 |
| ③ 撰稿 | 全文创作 | 按大纲逐节生成，支持多种文体风格和语气调节 |
| ④ 去AI化 | 三层反AI检测 | base → authentic → publish 递进式改写，确保通过 AI 检测 |
| ⑤ 配图 | 9 大图片源自动配图 | 支持 Unsplash / Pexels / Pixabay / 千图网 / 摄图网等 9 个图源 |
| ⑥ 排版 | 43 模块智能排版 | AI 现场手写排版指令，18 主题 × 43 组件自由组合 |
| ⑦ 预览 | 实时预览 + 一键复制 | 浏览器内实时渲染，一键复制富文本到微信编辑器 |
| ⑧ 发布 | 自动化发布 | 通过 WeChat Publisher API 自动登录并发布，支持定时发布 |

---

## 三种排版模式对比

| 特性 | 纯内联模式 | CSS 主题模式 | AI 手写排版 |
|------|-----------|-------------|------------|
| **原理** | 所有样式写为 inline style | 外部 CSS class + 主题变量 | AI 根据文章语义实时生成排版指令 |
| **重复性** | 固定模板，千篇一律 | 主题切换，有限变化 | 每篇独一无二 |
| **微信兼容性** | ★★★★★ 完美 | ★★★★☆ 需转换 | ★★★★★ 完美 |
| **表现力** | ★★☆☆☆ 有限 | ★★★★☆ 丰富 | ★★★★★ 无限 |
| **上手难度** | 极低 | 中等 | 低（AI 代劳） |
| **适用场景** | 简单通知、公告 | 固定风格系列文章 | 追求差异化的精品内容 |
| **输出格式** | 纯 HTML + inline style | HTML + `<style>` 标签 | 纯 HTML + inline style |

---

## 双轨交付

| 轨道 | 说明 | 适用场景 |
|------|------|----------|
| **Skill 轨道** | 安装 Skill 后直接调用，全自动 8 步链路 | 日常批量生产，追求效率 |
| **提示词轨道** | 使用 `prompts/` 目录下的提示词，在任意 AI 网页版手动执行 | 无需安装，灵活使用单步功能 |

---

## 快速开始

### 1. 安装 Skill

```bash
# 在 CodeBuddy Code 中安装
/skill install wechat-auto-publisher
```

### 2. 一键生成

```
/wechat-auto "AI 时代，程序员如何保持竞争力"
```

### 3. 预览 & 发布

- 浏览器自动打开预览页面
- 一键复制富文本到微信编辑器
- 或使用自动发布功能直接推送

---

## 详细使用说明

### 基础用法

```bash
# 从选题开始，全自动执行全链路
/wechat-auto "你的选题关键词"

# 仅生成大纲
/wechat-auto --step outline "你的选题关键词"

# 从已有稿件开始，仅执行排版+去AI化
/wechat-auto --from-draft ./my-article.md

# 指定主题和风格
/wechat-auto --theme cyber-neon --style professional "你的选题关键词"
```

### 分步执行

```bash
# 步骤 1：选题
/wechat-auto --step topic --industry tech --count 5

# 步骤 2：大纲
/wechat-auto --step outline --topic "AI 编程的未来"

# 步骤 3：撰稿
/wechat-auto --step draft --outline ./outline.md

# 步骤 4：去AI化
/wechat-auto --step humanize --draft ./draft.md --level authentic

# 步骤 5：配图
/wechat-auto --step images --draft ./humanized.md --source unsplash

# 步骤 6：排版
/wechat-auto --step format --draft ./final.md --theme ink-elegance

# 步骤 7：预览
/wechat-auto --step preview --html ./formatted.html

# 步骤 8：发布
/wechat-auto --step publish --html ./formatted.html --schedule "2026-06-07 08:00"
```

### 高级选项

```bash
# 自定义去AI化强度（1-3，默认2）
/wechat-auto --humanize-level 3 "选题"

# 批量生成
/wechat-auto --batch topics.csv --theme random

# 导出为多种格式
/wechat-auto --export pdf,html,md "选题"

# 使用自定义排版组件
/wechat-auto --custom-components ./my-components/ "选题"
```

---

## 配置指南

### Skill 配置文件

在项目根目录创建 `.wechat-auto.yaml`：

```yaml
# 基础配置
default_theme: ink-elegance    # 默认主题
default_style: professional     # 默认风格（professional/casual/storytelling）
humanize_level: 2              # 去AI化强度（1-3）

# 图片配置
image:
  default_source: unsplash     # 默认图源
  fallback_source: pexels      # 备用图源
  min_width: 900               # 最小宽度
  max_count: 5                 # 每篇最多配图数

# 发布配置
publish:
  auto_preview: true           # 自动打开预览
  default_schedule: "08:00"    # 默认定时发布时间
  draft_mode: false            # 是否保存为草稿

# 去AI化配置
humanize:
  enable_base: true            # 启用基础层
  enable_authentic: true       # 启用真实层
  enable_publish: true         # 启用发布层
  learning_mode: true          # 启用学习飞轮
```

### 环境变量

```bash
# 图源 API Key（按需配置）
export UNSPLASH_ACCESS_KEY="your-key"
export PEXELS_API_KEY="your-key"
export PIXABAY_API_KEY="your-key"

# 微信公众号配置
export WECHAT_APP_ID="your-app-id"
export WECHAT_APP_SECRET="your-app-secret"
```

---

## 主题画廊：18 套预设主题

| # | 主题名 | 风格描述 |
|---|--------|----------|
| 1 | **ink-elegance** | 水墨风雅——中国传统水墨画意境，素雅留白 |
| 2 | **cyber-neon** | 赛博霓虹——未来科技感，深色底+荧光高亮 |
| 3 | **morning-mist** | 晨雾轻纱——柔和渐变，莫兰迪色调 |
| 4 | **red-classic** | 红色经典——政务/党建风格，庄重大气 |
| 5 | **tech-minimal** | 极简科技——黑白灰+蓝，工程师审美 |
| 6 | **autumn-harvest** | 金秋收获——暖橙棕色调，温暖厚重 |
| 7 | **ocean-depth** | 深海幽蓝——深蓝渐变，神秘深邃 |
| 8 | **forest-breathe** | 森林呼吸——绿色系，清新自然 |
| 9 | **sunset-glow** | 落日余晖——暖黄到橘红渐变，浪漫温馨 |
| 10 | **arctic-aurora** | 极地极光——冷色渐变+光晕效果 |
| 11 | **cherry-blossom** | 樱花物语——粉白渐变，日系少女风 |
| 12 | **midnight-gold** | 午夜鎏金——深色底+金色点缀，高端商务 |
| 13 | **peach-garden** | 桃园春色——粉绿撞色，活泼明快 |
| 14 | **ink-wash** | 泼墨山水——大胆墨迹纹理，艺术气质 |
| 15 | **desert-gold** | 大漠金沙——沙色暖调，辽阔苍茫 |
| 16 | **rain-city** | 雨城烟雨——灰蓝调，朦胧诗意 |
| 17 | **retro-typewriter** | 复古打字机——衬线字体+纸纹质感 |
| 18 | **glass-morphism** | 玻璃拟态——毛玻璃效果+半透明层叠 |

---

## 图片提供商支持

| 提供商 | 类型 | 免费 | 说明 |
|--------|------|------|------|
| **Unsplash** | 图片 | 部分免费 | 高质量摄影作品，API 限速 |
| **Pexels** | 图片 | 免费 | 高质量摄影作品，API 友好 |
| **Pixabay** | 图片 | 免费 | 图片素材库，支持中文搜索 |
| **千图网** | 图片 | 部分免费 | 国内图库，更符合中文语境 |
| **摄图网** | 图片 | 部分免费 | 国内图库，正版商用 |
| **Flaticon** | 图标 | 部分免费 | 矢量图标库 |
| **IconFont** | 图标 | 免费 | 阿里巴巴图标库，中文生态 |
| **AI Generated** | AI 图片 | 按量付费 | AI 生成配图，高度定制化 |
| **Local** | 本地文件 | 免费 | 使用本地图片文件 |

---

## 与同类工具对比

| 特性 | 本 Skill | mdnice | doocs/md | wechat-publisher | wewrite | md2wechat |
|------|----------|--------|----------|-----------------|---------|-----------|
| **排版方式** | AI 手写排版 | CSS 模板 | CSS 模板 | CSS 模板 | 固定模板 | CSS 模板 |
| **主题数量** | 18 | ~30 | ~20 | ~10 | ~5 | ~8 |
| **排版组件** | 43 | ~15 | ~10 | ~8 | ~5 | ~12 |
| **去AI化** | 三层递进 | 无 | 无 | 无 | 无 | 两层 |
| **AI 检测评分** | 有 | 无 | 无 | 无 | 无 | 有 |
| **自动配图** | 9 大图源 | 无 | 无 | 无 | 无 | 无 |
| **全链路自动化** | 8 步 | 仅排版 | 仅排版 | 排版+发布 | 仅排版 | 排版+去AI |
| **自动发布** | 支持 | 不支持 | 不支持 | 支持 | 不支持 | 不支持 |
| **学习飞轮** | 有 | 无 | 无 | 无 | 无 | 部分 |
| **微信兼容性** | ★★★★★ | ★★★★☆ | ★★★★☆ | ★★★★☆ | ★★★☆☆ | ★★★★☆ |
| **离线使用** | 支持 | 不支持 | 支持 | 支持 | 不支持 | 支持 |
| **批量生产** | 支持 | 有限 | 有限 | 不支持 | 不支持 | 不支持 |
| **开源** | MIT | 部分 | MIT | MIT | MIT | MIT |

---

## 架构说明

```
┌─────────────────────────────────────────────────────────┐
│                    用户输入（选题/稿件）                    │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  8 步全链路流水线                         │
│                                                         │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────────┐ ┌─────┐ ┌─────┐ │
│  │选题  │→│大纲  │→│撰稿  │→│去AI化   │→│配图  │→│排版  │ │
│  └─────┘ └─────┘ └─────┘ └─────────┘ └─────┘ └─────┘ │
│                                     │                   │
│                              ┌──────┴──────┐            │
│                              │ 三层反AI引擎  │            │
│                              │ base        │            │
│                              │ authentic   │            │
│                              │ publish     │            │
│                              └──────┬──────┘            │
│                                     │                   │
│                              ┌──────┴──────┐            │
│                              │  学习飞轮    │            │
│                              │ 评分→回灌    │            │
│                              └─────────────┘            │
└──────────────────────┬──────────────────────────────────┘
                       │
              ┌────────┴────────┐
              ▼                 ▼
     ┌──────────────┐  ┌──────────────┐
     │  预览 + 复制  │  │  自动发布     │
     │  (浏览器)     │  │  (API)       │
     └──────────────┘  └──────────────┘
```

### 排版引擎架构

```
┌──────────────────────────────────────┐
│         AI 排版指令生成器              │
│   (根据文章语义实时生成排版指令)        │
└──────────────┬───────────────────────┘
               │
       ┌───────┴───────┐
       ▼               ▼
┌─────────────┐ ┌─────────────┐
│ 18 主题预设  │ │ 43 排版组件  │
│ (色彩/字体/  │ │ (标题/引用/  │
│  间距/装饰)  │ │  列表/卡片/  │
│             │ │  分隔线/…)   │
└──────┬──────┘ └──────┬──────┘
       │               │
       └───────┬───────┘
               ▼
┌──────────────────────────────────────┐
│       样式合成引擎                     │
│  主题变量 + 组件模板 → inline style    │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│    微信兼容性适配器                     │
│  过滤不支持的 CSS / 自动降级           │
└──────────────┬───────────────────────┘
               │
               ▼
       纯 HTML + inline style
       (微信完美渲染)
```

---

## 常见问题

### Q: 排版在微信编辑器里显示异常？

A: 本 Skill 所有输出均为纯 inline style，已通过微信编辑器兼容性验证。如遇异常，请检查：
1. 是否使用了复制按钮一键复制（而非手动选择复制）
2. 是否在微信后台的"图文"编辑器中粘贴（非"草稿"编辑器）
3. 如问题仍然存在，请提 Issue 并附上渲染截图

### Q: 去 AI 化后文章质量会不会下降？

A: 不会。三层去 AI 化不是简单的"替换同义词"，而是：
- **base 层**：消除 AI 常见写作模式（如"值得注意的是"、"总而言之"）
- **authentic 层**：注入真实写作特征（不完美句式、口语化表达、个人观点）
- **publish 层**：终检微调，确保流畅自然

每层改写后会进行质量评分，低于阈值会自动重写。

### Q: 可以只用排版功能，不执行全链路吗？

A: 可以。使用 `--step format` 参数即可单独执行排版步骤，也支持 `--from-draft` 从已有稿件开始。

### Q: 支持哪些微信账号类型？

A: 支持订阅号和服务号。自动发布功能需要已认证的服务号（需要 API 权限）。未认证账号可使用"预览 + 手动复制"方式。

### Q: 学习飞轮的数据存在哪里？

A: 存储在本地 `.wechat-auto/learning/` 目录下，包含历史评分数据和提示词优化记录。不会上传任何数据到外部服务器。

### Q: 可以自定义主题吗？

A: 可以。在 `.wechat-auto/themes/` 目录下创建 YAML 主题文件即可，格式参考内置主题。也支持在运行时通过 `--theme-override` 参数覆盖单个样式变量。

---

## 贡献指南

欢迎贡献！以下是参与方式：

1. **Fork 本仓库** → 创建特性分支（`git checkout -b feature/amazing-theme`）
2. **提交改动** → 遵循 Conventional Commits 规范
3. **发起 Pull Request** → 描述改动内容和动机

### 贡献方向

- 新主题：在 `themes/` 目录添加 YAML 主题文件
- 新排版组件：在 `components/` 目录添加组件模板
- 去AI化规则：改进 `prompts/humanizer-*.md` 中的检测规则
- 图源适配：在 `providers/` 目录添加新的图片提供商适配器
- Bug 修复：提 Issue 或直接 PR

### 代码规范

- Markdown 文件使用 2 空格缩进
- YAML 文件使用 2 空格缩进
- 提交信息格式：`type(scope): description`
- 类型：feat / fix / docs / style / refactor / test / chore

---

## 致谢

本项目站在三个优秀开源项目的肩膀上：

1. **[wechat-publisher](https://github.com/spacingly/wechat-publisher)** — 微信公众号自动发布能力，提供了稳定的 API 交互和发布流程
2. **[md2wechat](https://github.com/yingjieweb/md2wechat)** — Markdown 转微信排版 + 去 AI 痕迹引擎，提供了排版系统和 humanizer 核心逻辑
3. **[Doocs](https://github.com/doocs/md)** — 微信 Markdown 编辑器，提供了 CSS 主题系统和微信兼容性方案

感谢以上项目的作者和贡献者，没有他们的开源精神，就没有本项目的诞生。

---

## License

[MIT License](./LICENSE)

Copyright (c) 2026 wechat-auto-publisher contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
