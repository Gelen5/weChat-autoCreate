# Runtime Compatibility and Credentials

This skill is host-model first. The same `SKILL.md` and Python toolkit can be
used from WorkBuddy, Claude Code, Codex, ChatGPT or another agent that can read
the repository and run Python. No vendor SDK is required for the core content
workflow.

## Capability matrix

| Capability | Works without API key | Credential needed only for the external execution path |
|---|---:|---|
| Topic planning, intent modeling, fact boundaries | Yes | None |
| Article writing, SICO structure, anti-AI scoring and repair plan | Yes | Optional `OPENAI_API_KEY` for a second L3 check; host-model scoring is default |
| Tie-Tu planning, Card Brief, source ledger, reverse-image measurement | Yes | None |
| Prompt generation and portrait routing | Yes | None |
| Local image generation from Python/Node | No | One selected provider key, such as `GEMINI_API_KEY`, `DOUBAO_API_KEY` or `OPENAI_API_KEY` |
| Image generation by the current host AI | Yes | The host product's own entitlement/session, not a key in this skill |
| Local HTML/mobile preview and validation | Yes | None |
| WeChat draft-box publishing | No | `WECHAT_APPID` and `WECHAT_SECRET` or equivalent configured credentials |

## Recommended no-key path

1. Ask the host AI to plan, write, review and generate image prompts.
2. Let WorkBuddy, Claude Code, Codex or another host create the image using its
   own image capability, or provide an existing image with `tie-tu pilot --image`.
3. Run local validation and preview.
4. Use manual copy/paste delivery if WeChat API credentials are not configured.

The skill never requires a user to paste a secret into the conversation. Keys,
when needed for optional local image generation or publishing, are read from
environment variables or local configuration files.

## Important boundary

The Python script cannot directly invoke an arbitrary host's image-generation
tool. It outputs provider-neutral prompts and records supplied image paths. The
agent layer performs the host-specific image call, keeping the workflow portable
across WorkBuddy, Claude Code, Codex and other hosts.
