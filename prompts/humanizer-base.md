# 局部编辑提示词

用途：正文完成后的问题定位和局部修复。不要全文洗稿。

输入必须包含文章目标、目标读者、AuthorProfile、EvidencePack、正文和确定性检查结果。

检查套话与重复、标题兑现、无来源事实、虚构亲历、越界判断、机械结构和作者一致性。只修改命中的句子或段落，保留事实、数字、引用、限定条件和原作者有效表达。缺少证据时输出 `needs_evidence`，不要补写数字或故事。

输出 JSON：

```json
{"issues":[{"location":"段落标识","reason":"问题","severity":"block|revision|note"}],"edits":[{"location":"段落标识","before":"原文","after":"修订","reason":"原因"}],"unresolved":[]}
```
