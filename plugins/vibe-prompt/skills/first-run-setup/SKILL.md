---
name: vibe-prompt:first-run-setup
description: Internal SKILL invoked on first invocation of `:eval` or `:radar` in a target app. Captures the composer pattern + agent self-ID + initial config. Writes `.vibe-prompt/eval/composer.json` + `.vibe-prompt/eval/agent.json` + `.vibe-prompt/eval/config.json`. Idempotent — re-runnable to refresh stale captures.
---

# First-run setup (internal)

Load `vibe-prompt:guide`. Then walk the user through three captures.

## Inputs

- Target app: CWD (or path arg)
- `.vibe-prompt/state/inventory.json` (required input — used to identify vendors)

## Workflow

1. **Pre-flight.** `session-logger` start. Verify inventory exists — if not, friction-log `inventory-not-found` and exit with: *"Run /vibe-prompt:scan first, or point at a manual inventory file."*

2. **Composer capture** per `references/composer-interview.md`. Output: `.vibe-prompt/eval/composer.json`.

3. **Agent self-ID** per `references/agent-self-id.md`. Output: `.vibe-prompt/eval/agent.json`.

4. **Config bootstrap.** Generate a default `.vibe-prompt/eval/config.json`:

   ```json
   {
     "version": "0.1",
     "vendors": {
       "gemini": {
         "defaultModel": "<from inventory.modelIdentifiers[0].value or ask user>",
         "fallbackModel": null
       }
     },
     "costCeiling": 2.00
   }
   ```

   Show the user the default + ask: *"Cost ceiling defaults to $2.00 per eval. Override?"*

5. **Sanity check.** Verify the user has at least one working Gemini auth method:
   - **Preferred:** `gcloud auth print-access-token` returns a non-empty value (means `gcloud auth login` has been run). No env var needed.
   - **Fallback:** `VIBE_PROMPT_GEMINI_API_KEY` is set (plugin-namespaced — NOT the generic `GEMINI_API_KEY`, to avoid Firebase deploy collisions).
   - If neither: warn the user and suggest running `gcloud auth login` before `:eval`. Do NOT abort — setup itself doesn't require auth; only `:eval` does.

6. **Post-flight.** `session-logger` terminal entry.

## Banner template

```
═══ Vibe-Prompt first-run setup ═══
Inventory:      14 prompts found at .vibe-prompt/state/inventory.json
Composer:       captured (6 layers, kind=stacked)
                source: src/lib/gemini.ts
Agent:          Claude Code (claude-opus-4-7), detected via marker-file
Config:         .vibe-prompt/eval/config.json written
                vendors: gemini (default: gemini-3.5-flash)
                ceiling: $2.00

Auth check:     gcloud auth: ✓ (token available)
                VIBE_PROMPT_GEMINI_API_KEY: not set (OAuth path preferred — OK)

Ready: /vibe-prompt:eval
```

## Never

- Read API keys from any file.
- Run vendor calls during setup.
- Auto-confirm composer or agent identity — always require user confirmation.
