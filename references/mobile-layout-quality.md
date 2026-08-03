# Mobile Layout Quality Gate

> Use this before fine layout and again before delivery. The goal is not to add more components, but to make the article feel intentional on a WeChat mobile screen.

## Why This Exists

`weChat-autoCreate` already has components, themes, image generation, and publishing paths. This gate adds the editorial judgement layer that decides what should not be rendered, what should be simplified, and what must be checked in a real mobile viewport.

Do not treat these rules as a new visual template. Use them as constraints around the existing `components.md`, `layouts.md`, `visual-prompts.md`, and `wechat-html-spec.md`.

## 1. First Screen Information Unit

The first mobile screen should be one complete idea, not a stack of decorative modules.

Keep the first screen to:

1. masthead or date,
2. main title,
3. user-owned identity asset when available,
4. one subtitle or promise,
5. editor note label when useful,
6. two or three short opening paragraphs,
7. one complete emphasis sentence.

Avoid adding all of these at once: table of contents, tag wall, second cover card, quote card, divider, and image gallery. If the first screen needs scrolling before the reader understands the article, simplify it.

## 2. Decoration Budget

Every border, divider, pill, color block, highlight, and vertical line spends attention. A strong article normally needs fewer visible anchors than a component demo.

Default budget:

- use no more than five strong visual anchors in a normal article;
- use one accent color family for emphasis;
- do not put a horizontal divider directly under a section title;
- avoid left-side vertical timelines in narrative/case articles unless the article is genuinely chronological;
- do not wrap every small paragraph or case in a card;
- use borders to define a real region, not to decorate every module.

If removing a line makes the structure collapse, fix the heading hierarchy first. The line was doing work the layout should do.

## 3. Mobile Line-Break Discipline

WeChat is read on narrow screens, so text rhythm matters.

Rules:

- body paragraphs should not use manual `<br>` line breaks;
- headings and quote lines may be manually split only at semantic boundaries;
- avoid a heading or quote whose final line is likely to contain only two or three Chinese characters;
- do not highlight only half of a sentence;
- do not stack bold, underline, and background color on the same phrase;
- one paragraph should carry one point, not three.

When a title breaks badly, rewrite the title. Do not pad it with spaces.

## 4. Evidence-Based Image Table

Before generating or collecting body images, create a small table. Images are evidence, not filler.

```yaml
image_evidence_table:
  - section: ""
    claim_to_prove: ""
    image_must_show: ""
    source_or_generation_plan: ""
    composition: "single / two-up / collage / annotated screenshot"
    caption: ""
    rights_note: "user-owned / official source / licensed / generated / needs review"
```

Selection rules:

- each image must prove or clarify a nearby claim;
- product images must make the product and key action large enough to inspect;
- people images must show the relevant person, posture, outfit, or context clearly;
- multi-image groups should be pre-composed into one static collage before final HTML when alignment matters;
- captions should name the visual content and source;
- do not use an image only because a section looks empty.

## 5. Component Selection Rules

Use components to express article logic:

| Content need | Prefer | Avoid |
|---|---|---|
| opening promise | cover/hero plus one editor note | hero plus TOC plus tag wall |
| new section | numbered heading with generous top spacing | heading plus divider plus extra label |
| core judgement | one complete quote/callout | multiple small highlights in one paragraph |
| case or example | label, case title, body, evidence image, short judgement | a full card around every paragraph |
| chronological process | timeline only when time order matters | vertical line as decoration |
| ending | summary, author note, simple CTA | complex SVG/icon CTA that may fail when pasted |

## 6. Feedback Routing

When the user comments on a layout, classify the issue before editing. Change only the affected layer unless the user asks for a redesign.

| User feedback | Layer | First action |
|---|---|---|
| "structure is weak" | hierarchy | adjust section size, weight, color, and spacing |
| "too crowded" | spacing | split long blocks and increase adjacent module spacing |
| "too empty" | rhythm | shorten first screen or restore one useful anchor |
| "too many lines" | decoration | remove dividers, vertical rules, and unnecessary borders |
| "title looks awkward" | text | rewrite or semantically split heading |
| "highlight feels weird" | emphasis | expand to a complete phrase or sentence |
| "images are ordinary" | image evidence | replace with product/action/context proof |
| "images are messy" | image composition | pre-compose collage and normalize crop/spacing |
| "paste broke it" | platform compatibility | fix paths, unsupported tags, style attributes, and complex icons |
| "previous version was better" | rollback | restore the accepted component only |

Stable feedback should be written back only when it appears across multiple articles, the user says "use this from now on", or it fixes a confirmed WeChat platform issue.

## 7. Pre-Delivery Checks

Run `scripts/layout_quality_check.py` on the generated HTML or Markdown whenever possible.

Manual checks:

- the first mobile screen communicates one complete idea;
- section starts are obvious without relying on divider lines;
- no title or quote has an ugly short tail line;
- emphasis covers complete semantics;
- each image has a nearby caption or evidence role;
- no external or local temporary image path will break in WeChat;
- preview has been inspected at 375-390px width;
- copy/paste delivery has no missing image, mojibake, layout drift, or abnormal blank space.

Passing this gate does not mean the design is beautiful. It means the layout has avoided the common mobile WeChat failures before final human taste judgement.
