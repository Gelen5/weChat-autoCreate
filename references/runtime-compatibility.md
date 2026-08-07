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
| Local image generation through the default host-first path | Yes | The skill writes a host request; the current AI host performs the image call |
| Direct image generation from Python/Node through a provider API | Optional | Only if an operator explicitly selects a provider and has its key |
| Image generation by the current host AI | Yes | The host product's own entitlement/session, not a key in this skill |
| Local HTML/mobile preview and validation | Yes | None |
| WeChat draft-box publishing | No | `WECHAT_APPID` and `WECHAT_SECRET` or equivalent configured credentials |

## Recommended no-key path

1. Ask the host AI to plan, write, review and generate image prompts.
2. Run `tie-tu pilot` without `--provider`; the skill writes a structured host
   request and does not try OpenAI or any other provider.
3. Let WorkBuddy, Claude Code, Codex or another host create the image using its
   own image capability, then record it with `tie-tu pilot --image`.
4. Run local validation and preview. Use manual copy/paste delivery if WeChat
   API credentials are not configured.

The skill never requires a user to paste a secret into the conversation. Keys,
when an operator explicitly enables an optional external path, are read from
environment variables or local configuration files.

## Important boundary

The Python script cannot directly invoke an arbitrary host's image-generation
tool. It outputs provider-neutral prompts and records supplied image paths. The
agent layer performs the host-specific image call, keeping the workflow portable
across WorkBuddy, Claude Code, Codex and other hosts.
