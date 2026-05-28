---
name: vibe-prompt:session-logger
description: Internal SKILL — not a slash command. Two-phase append-only session log for Vibe-Prompt. Invoked by every command SKILL at start (sentinel entry, outcome=in_progress) and at end (terminal entry, paired by sessionUUID). Part of Level 2 (session memory) of the Self-Evolving Plugin Framework.
---

# Session logger (internal)

Append-only JSONL log of every command invocation. Two phases: sentinel at start, terminal at end. Paired by `sessionUUID`.

## Storage

File path: `~/.claude/plugins/data/vibe-prompt/sessions.jsonl`. Create directory if missing. Append-only — never truncate.

## Sentinel entry shape (written at command start)

```json
{
  "sessionUUID": "<uuid v4>",
  "timestamp": "<ISO 8601>",
  "command": "scan | audit | router | evolve-prompt",
  "targetApp": "<basename of cwd>",
  "outcome": "in_progress"
}
```

## Terminal entry shape (written at command end)

```json
{
  "sessionUUID": "<same uuid>",
  "timestamp": "<ISO 8601>",
  "command": "...",
  "targetApp": "...",
  "outcome": "completed | aborted | error",
  "durationMs": <integer>,
  "summary": {
    "findingsCount": <integer or null>,
    "stackDetected": "...",
    "inlineCount": <integer or null>
  }
}
```

## Workflow (per command using it)

1. **At command start:** generate UUID, write sentinel entry. Stash UUID + start time in agent memory for the duration.
2. **At command end:** write terminal entry with the same UUID. Outcome reflects what actually happened.

## Rules

- Atomic append: open file with `a` flag (single open + write + close). Never rewrite.
- If write fails, do NOT abort the command — log to stderr and continue.
- No PII. No source content. Just shape + count + UUID.
