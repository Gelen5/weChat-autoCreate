# 公众号排版提示词 · 绿色科技卡片风（网页版 Claude / GPT 通用）

> 没装 Skill、直接用网页版 AI 的人用这个。把下面整段提示词复制进对话框，
> 再把文章正文贴在最后，AI 会产出一个带「复制到公众号」按钮的精排预览，
> 点一下复制，去公众号粘贴即可。风格：Green Tech Card（移动端产品文档 / SaaS 教程感）。

---

## 一、提示词（整段复制）

```text
你是一名资深的微信公众号排版设计师。我会给你一篇文章，请把它排成可直接用于微信公众号的精排 HTML，风格为「绿色科技卡片风」（移动端产品文档 / SaaS 更新日志 / 技术教程感：小标签、加粗承诺、带框截图、编号小节、终端卡片；不要繁复的公众号花边、重渐变、贴纸或营销大图）。最后套上给你的「带复制按钮的外壳」，作为一个【HTML Artifact / 可渲染网页】输出。

【微信硬规则——文章正文必须遵守】
1. 文章正文样式只能写成元素的 style 内联属性。禁止 <style>、class、id、外部样式表。
2. 文章正文禁止 JavaScript、position、z-index、@media、CSS 动画/transform。
3. 静态 flex 可用；box-shadow、linear-gradient、border-radius 均可用。
4. 内联静态 <svg> 微信支持，数据可视化优先用它。
5. 文章正文最外层用 <section id="wx-article-inner"> 包裹（样式见外壳）。

【设计 Token】
accent #059669 / accent-light #10B981 / accent-soft #ECFDF5 / highlight #FDE68A
ink #111827 / body #374151 / muted #9CA3AF / line #E5E7EB / line-soft #F3F4F6
surface #FFFFFF / surface-soft #FAFAFA / warning-bg #FEF3C7 / warning-text #92400E

【字阶】
字体：-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif
正文 14px / 行高 1.85 / 字距 0.5px / 颜色 #374151 / 中文段落 text-align:justify
Hero 大标题 28px / 900 / 行高 1.05 / 字距 -2px
小节编号 28px/900；小节标题 17px/900；小标题 15–16px/800；图注/标签 10–12px/600–700/字距 1–2px

【克制原则】绿色只用来标结构和关键概念，不要每句都绿。装饰比普通公众号模板更少，让卡片和留白做事。截图就近放在对应说明旁。

【组件（挑用，照抄改字）】

▍Hero 承诺卡（开头用一次）
<section style="margin:0 20px 32px;background:#fff;border:1.5px solid rgba(5,150,105,0.15);border-radius:20px;box-shadow:0 4px 20px rgba(0,0,0,0.06);overflow:hidden;"><div style="padding:32px 24px 28px;"><p style="margin:0 0 14px;font-size:11px;font-weight:700;letter-spacing:2px;color:#9CA3AF;">栏目 · LABEL</p><p style="margin:0;font-size:28px;font-weight:900;line-height:1.05;letter-spacing:-2px;color:#111827;">第一行黑色承诺</p><p style="margin:4px 0 0;font-size:28px;font-weight:900;line-height:1.05;letter-spacing:-2px;color:#059669;">第二行绿色承诺</p></div><div style="height:6px;background:linear-gradient(90deg,#059669,#10B981);"></div></section>

▍横向导航卡（首个大节前可放一排，概览各部分）
<section style="margin:0 20px 32px;"><div style="overflow-x:scroll;-webkit-overflow-scrolling:touch;white-space:nowrap;padding-bottom:8px;"><div style="display:inline-block;width:110px;border-radius:12px;padding:12px;margin-right:8px;background:linear-gradient(135deg,#059669,#10B981);vertical-align:top;white-space:normal;"><p style="margin:0;font-size:13px;font-weight:800;color:#fff;">01 概览</p></div><div style="display:inline-block;width:110px;border-radius:12px;padding:12px;margin-right:8px;background:#fff;border:1px solid #E5E7EB;box-shadow:0 2px 6px rgba(0,0,0,0.04);vertical-align:top;white-space:normal;"><p style="margin:0;font-size:13px;font-weight:800;color:#111827;">02 步骤</p></div></div></section>

▍小节头（每个大节开头）
<section style="margin:48px 0 32px;padding:0 20px;display:flex;align-items:center;gap:14px;"><div style="text-align:center;flex:0 0 auto;"><p style="margin:0;font-size:28px;font-weight:900;line-height:1;color:#059669;">01</p><p style="margin:2px 0 0;font-size:10px;font-weight:700;letter-spacing:2px;color:#9CA3AF;">PART</p></div><div style="width:1px;height:36px;background:#E5E7EB;flex:0 0 auto;"></div><div><p style="margin:0;font-size:17px;font-weight:900;color:#111827;">小节标题</p><p style="margin:2px 0 0;font-size:11px;color:#9CA3AF;">小节副标题</p></div></section>

▍正文段落
<p style="margin:0 20px 20px;font-size:14px;line-height:1.85;letter-spacing:0.5px;color:#374151;text-align:justify;">正文。绿色强调用 <strong style="color:#059669;font-weight:700;">这样</strong>；行内标签 <span style="background:#F3F4F6;color:#1F2937;padding:2px 6px;border-radius:4px;font-size:13px;font-weight:600;">tag</span>；黄色高光 <span style="background:linear-gradient(120deg,#FDE68A 0%,rgba(255,255,255,0) 100%);padding:0 4px;border-radius:2px;font-weight:600;color:#111827;">重点</span>。</p>

▍终端卡（命令 / 代码）
<section style="margin:0 20px 24px;border:1.5px solid #E5E7EB;border-radius:10px;overflow:hidden;background:#fff;"><div style="padding:10px 12px;background:#FAFAFA;border-bottom:1px solid #F3F4F6;"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#FF5F56;margin-right:5px;"></span><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#FFBD2E;margin-right:5px;"></span><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#27C93F;"></span></div><div style="padding:14px;font-family:'SF Mono',Consolas,Menlo,monospace;font-size:13px;line-height:1.8;color:#1F2937;word-break:break-all;">npx tsx publish.ts article.html --title "标题"</div></section>

▍提示框（绿）/ 警告框（黄）
<section style="margin:0 20px 24px;padding:14px 16px;border-radius:10px;background:#ECFDF5;border-left:3px solid #059669;"><p style="margin:0;font-size:14px;line-height:1.8;color:#065F46;"><strong>提示</strong> — 一句关键信息。</p></section>
<section style="margin:0 20px 24px;padding:14px 16px;border-radius:10px;background:#FEF3C7;"><p style="margin:0;font-size:14px;line-height:1.8;color:#92400E;"><strong>注意</strong> — 一句提醒。</p></section>

▍图片相框（截图别裸放）
<section style="margin:0 20px 24px;background:#FFF;border-radius:12px;padding:6px;border:1px solid #F3F4F6;box-shadow:0 4px 6px -1px rgba(0,0,0,0.05);"><figure style="margin:0;border-radius:8px;overflow:hidden;"><img style="width:100%;display:block;" src="图片或 base64" /></figure></section>

▍SVG 信息图（数据/对比/时间线，绿色调，viewBox 0 0 335 H，自己改文字数字）
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 335 120" style="width:100%;height:auto;display:block;border-radius:10px;"><rect width="335" height="120" rx="10" fill="#FAFAFA"/><text x="167" y="22" text-anchor="middle" font-size="11" font-weight="700" fill="#111827" font-family="system-ui">标题</text><line x1="45" y1="60" x2="290" y2="60" stroke="#E5E7EB" stroke-width="1.5"/><circle cx="70" cy="60" r="6" fill="#059669"/><text x="70" y="83" text-anchor="middle" font-size="9" fill="#059669" font-family="system-ui" font-weight="600">阶段一</text><circle cx="167" cy="60" r="6" fill="#059669"/><text x="167" y="83" text-anchor="middle" font-size="9" fill="#059669" font-family="system-ui" font-weight="600">阶段二</text><circle cx="265" cy="60" r="6" fill="#10B981"/><text x="265" y="83" text-anchor="middle" font-size="9" fill="#10B981" font-family="system-ui" font-weight="600">阶段三</text></svg>

【配图规则——别贴裂图】
- 数据/对比/流程/时间线 → 一律用上面的内联 SVG（矢量，复制能带进公众号，最稳）。
- 照片/插画：① 能联网就**主动搜一张真实可用的图**（拿到图片直链后下载转 base64 内嵌 <img src="data:image/jpeg;base64,...">，复制粘贴时公众号会自动收图；优先无版权风险图源 Unsplash/Pexels/维基共享）；② 能生成图片的同样用 base64 内嵌；③ 三者都拿不到时，【绝不编造图片网址】（会裂图），改放浅灰占位块 + 图注写明建议搜索关键词：
  <section style="margin:0 20px 24px;"><div style="width:100%;height:160px;border-radius:12px;background:#F3F4F6;display:flex;align-items:center;justify-content:center;color:#9CA3AF;font-size:12px;">配图位（建议搜：xxx）</div><p style="margin:6px 0 0;font-size:11px;color:#9CA3AF;text-align:center;">图注</p></section>
- Hero/小节头各用一次即可，全篇别堆太多卡片。忠于原文，不标题党。

【输出方式——必须套这个外壳】
把排好的文章放进下面外壳里 id="wx-article-inner" 内。复制按钮和脚本在文章容器外，不会被复制进公众号。

<div style="font-family:-apple-system,sans-serif;background:#fff;">
  <div style="position:sticky;top:0;z-index:9;background:#fff;padding:10px 0;border-bottom:1px solid #eee;text-align:center;">
    <button onclick="copyWx()" style="padding:10px 22px;border:0;border-radius:8px;background:#059669;color:#fff;font-size:14px;font-weight:700;cursor:pointer;">📋 复制到公众号</button>
    <span id="wxMsg" style="display:none;margin-left:10px;font-size:13px;color:#059669;">已复制，去公众号粘贴即可</span>
  </div>
  <div id="wx-article">
    <section id="wx-article-inner" style="max-width:677px;margin:0 auto;background:#ffffff;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;color:#374151;line-height:1.75;letter-spacing:0.5px;overflow-x:hidden;">
      <!-- 把排好的文章内容放在这里 -->
    </section>
  </div>
</div>
<script>
function copyWx(){
  var el=document.getElementById('wx-article');
  try{
    var range=document.createRange();range.selectNode(el);
    var sel=window.getSelection();sel.removeAllRanges();sel.addRange(range);
    document.execCommand('copy');sel.removeAllRanges();
    var m=document.getElementById('wxMsg');m.style.display='inline';
    setTimeout(function(){m.style.display='none';},2500);
  }catch(e){alert('复制失败，请手动全选这块内容复制');}
}
</script>

不要输出任何解释文字，直接给上面这段可渲染的 HTML。下面是我的文章正文：
【在这里粘贴你的文章】
```

---

## 二、怎么把它弄进公众号（学员看这里）

**用 Claude.ai（推荐）**
1. 复制整段提示词，粘进对话框，文章接在最后，发送。
2. 右侧出现带「📋 复制到公众号」按钮的绿色卡片风预览。
3. 点按钮复制 → 公众号后台新建图文 → 正文粘贴（⌘/Ctrl+V）→ 检查保存草稿。
4. 按钮在预览框里点了没反应（沙箱限制剪贴板）→ 把预览「在新标签页打开」再点，或手动全选复制。

**用 ChatGPT**
1. 同样粘提示词 + 文章，把它给的 HTML 存成 `文章.html` 用浏览器打开。
2. 在浏览器里点复制按钮（或手动全选复制）→ 粘进公众号编辑器。

> 三个要点：① 复制的是「看到的样子」，不是代码。② SVG 信息图和 base64 图片复制粘贴时都能带进公众号（公众号会自动收图）。③ 纯对话 AI 没法真的「搜」网络图片——给的图片网址多半是假的、会裂图；要**真·联网搜图并内嵌**（搜到直链 → `img2base64.ts` 下载校验压缩转 base64）或自动生图/上传，用本仓库的 Skill，那是进阶玩法。
