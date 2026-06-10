---
name: vibe-prompt:iterate
description: >
  Discover new AI-feature opportunities for your app. Reads inventory + audit findings + app
  domain, dispatches a creative-divergent LLM call, returns 3-5 prompts you could add with
  handoff hints to /vibe-cartographer:scope or /vibe-iterate:feature-add. Trigger phrases:
  "/vibe-prompt:iterate", "what should I add", "suggest new prompts", "iterate round",
  "AI feature discovery". Cost: ~$0.02 per run (one creative-divergent LLM call).
---

# vibe-prompt:iterate

Load `vibe-prompt:guide` first. Then load `references/domain-detection.md`,
`references/creative-discovery-prompt.md`, and `references/iterate-dashboard-template.md`.

## Inputs

| Input | Required | Notes |
|---|---|---|
| `.vibe-prompt/state/inventory.json` | REQUIRED | Produced by `/vibe-prompt:scan`. |
| `.vibe-prompt/state/audit.json` | OPTIONAL | High-severity findings inform what's missing. |
| `.vibe-prompt/iterate/domain.json` | OPTIONAL | Cached domain from prior run. Read if present and `--refresh-domain` not passed. |
| `--refresh-domain` CLI flag | OPTIONAL | Bypasses cached domain.json and re-runs the detection cascade. |

## Workflow

### 1. Pre-flight

Start session-logger.

### 2. Domain detection

Per `references/domain-detection.md`. If `.vibe-prompt/iterate/domain.json` exists and user
did not pass `--refresh-domain`, read it and use the cached domain summary. Skip to step 3.

Otherwise, walk the cascade:
1. Read `<target-app>/CLAUDE.md` if it exists. Extract: app purpose, persona, domain, brand voice.
   Verify with user via one-line AskUserQuestion: "I read your CLAUDE.md — your app is [summary].
   Look right? (Y/n)"
2. If CLAUDE.md absent or user pushes back: check vibe-tool artifacts in priority order (see
   `references/domain-detection.md`).
3. If artifacts insufficient: read package.json + README.
4. Last resort: short interview via AskUserQuestion.

Cache result to `.vibe-prompt/iterate/domain.json`.

### 3. Read inventory + audit gap signals

Read `inventory.json` — extract prompt IDs, names, purposes, persona assignments.

If `audit.json` exists, extract high-severity findings (severity = "high") as gap signals to pass
to the discovery prompt. These focus suggestions on areas the audit already flagged as weak.

### 4. Dispatch creative-discovery LLM call

Per `references/creative-discovery-prompt.md`. Use the Agent tool at **dispatch tier: `creative-divergent`** —
brainstorm/ideation where breadth beats rigor, so it routes to the cheap/fast tier (the session maps
tier→model; never pin a model ID here). Set temperature=0.9 (divergent).

Pass:
- `domain.summary` from domain.json
- Inventory list (prompt ID + purpose per prompt)
- High-severity audit findings (recommendations, not full finding text)

Expect the model to return a JSON array of 3-5 suggestion objects.

### 5. Validate output

Validate against `iterate-suggestions.schema.json`. If invalid, retry once with a stricter format
instruction appended to the prompt: "Return ONLY a valid JSON array. No preamble. No postamble.
No markdown fences." If still invalid after one retry, surface the raw output and ask the user
to review it manually.

### 6. Write suggestions state file

Write `.vibe-prompt/iterate/state/suggestions-<runId>.json` (runId = `iterate-<YYYY-MM-DD>-<HHMM>`)
validated against `iterate-suggestions.schema.json`.

### 7. Render dashboard

Per `references/iterate-dashboard-template.md` → `docs/vibe-prompt/iterate-<YYYY-MM-DD>.md`.
Create `docs/vibe-prompt/` if absent.

### 8. Render banner

Surface in chat — the 3-5 suggestions by name + one-line purpose + handoff hint:

```
vibe-prompt:iterate — {{N}} suggestions for {{targetApp.name}}

Domain: {{domain.summary}} (source: {{domain.source}})

1. {{suggestion[0].name}} — {{suggestion[0].purpose}}
   Handoff: {{suggestion[0].handoffHint}}

2. {{suggestion[1].name}} — {{suggestion[1].purpose}}
   Handoff: {{suggestion[1].handoffHint}}

...

Dashboard: docs/vibe-prompt/iterate-<YYYY-MM-DD>.md
Next: pick one above and run its handoff command.
```

### 9. Post-flight

Session-logger terminal.

## Outputs

| Output | Path |
|---|---|
| Domain cache | `.vibe-prompt/iterate/domain.json` |
| Suggestions state | `.vibe-prompt/iterate/state/suggestions-<runId>.json` |
| Human dashboard | `docs/vibe-prompt/iterate-<YYYY-MM-DD>.md` |

## Never

- No vendor API calls in `:iterate` — uses in-session subagent only (Agent tool). This falls in
  the $0 cost bucket against external vendor budgets (the in-session call bills against the user's
  session, not the plugin's vendor budget ceiling). Do not call Gemini or any other external API
  from `:iterate`.
- Never modify `inventory.json` or `audit.json` — read-only inputs.
- `domain.json` is cached but the user can refresh it anytime with `--refresh-domain`. Never
  silently skip the user's explicit refresh request.
