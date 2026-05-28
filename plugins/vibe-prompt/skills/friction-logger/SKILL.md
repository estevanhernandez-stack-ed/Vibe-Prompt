---
name: vibe-prompt:friction-logger
description: Internal SKILL — not a slash command. Append-only friction capture for Vibe-Prompt. Invoked by every command SKILL at the triggers listed in `references/friction-triggers.md`. Part of Level 2 of the Self-Evolving Plugin Framework.
---

# Friction logger (internal)

Append-only JSONL log of friction events. Used by `/vibe-prompt:evolve-prompt` to propose improvements.

## Storage

File path: `~/.claude/plugins/data/vibe-prompt/friction.jsonl`. Append-only.

## Entry shape

```json
{
  "timestamp": "<ISO 8601>",
  "sessionUUID": "<from session-logger>",
  "command": "scan | audit | router | evolve-prompt",
  "trigger": "<one of the codes in friction-triggers.md>",
  "confidence": "low | medium | high",
  "context": {
    "<trigger-specific fields>"
  }
}
```

## Workflow

1. When a command hits one of the triggers in `references/friction-triggers.md`, append a friction entry.
2. Confidence is set per trigger in that reference file — agents do NOT tune per-call.

## Rules

- Atomic append.
- No source content. Only paths, counts, and trigger codes.
- If a single command fires the same trigger multiple times, log once with `context.occurrences` count.
