---
name: vibe-prompt:router
description: This skill should be used when the user says "/vibe-prompt" (bare, no subcommand). Reads target-app state (inventory + audit + eval + radar freshness), introduces Vibe-Prompt, and recommends the next move — never executes destructively without confirmation.
---

# /vibe-prompt (bare router)

Load `vibe-prompt:guide`. Then read target-app state and route.

## State checks

1. **No `.vibe-prompt/state/inventory.json`** → first run (scan).
   - Render intro + "Want me to run `/vibe-prompt:scan` to inventory your prompts? (read-only, free)"
   - Wait for confirm. If yes, hand off to scan. If no, exit.

2. **Inventory exists, no `.vibe-prompt/state/audit.json`** → audit pending.
   - Render: inventory summary (counts) + "No audit yet. Run `/vibe-prompt:audit` against the cached inventory?"
   - Wait for confirm. If yes, hand off to audit.

3. **Audit exists, no `.vibe-prompt/eval/state/run-*.json`** → eval pending.
   - Render: audit summary (top findings) + "Now behaviorally test the prompts? `/vibe-prompt:eval` runs them against the prod model and surfaces drift. Costs ~$0.01–0.20 per full sweep — gated by a confirm step."
   - Wait for confirm. If yes, hand off to eval (which invokes first-run-setup if needed).

4. **All three states exist, radar cache > 7 days old** → model news refresh suggested.
   - Render posture summary (top 3 audit findings + top 3 eval findings) + "Radar cache is stale — `/vibe-prompt:radar` to refresh? (zero LLM cost)"
   - Wait for confirm. If yes, hand off to radar. If no, surface full summary anyway.

5. **All fresh** → full posture summary.
   - Read inventory + audit + latest run-result + radar cache.
   - Render: top 3 audit findings, top 3 eval findings (with evaluator-drift caveat: "LLM-judge findings — verify before acting; cross-vendor bias possible"), any new-model alerts from radar.
   - Suggest re-running `/vibe-prompt:scan` if a code change pushed prompts since last scan.

## Workflow

1. Invoke `session-logger` start.
2. Read state. Pick branch (1 through 5 in order — first match wins).
3. Render banner.
4. If asking a question, use AskUserQuestion. Wait for response.
5. If handing off, defer to the target skill.
6. `session-logger` terminal entry.

## Never

- Run scan, audit, eval, or radar without explicit user confirmation, even on first run.
- Suggest a state-mutating fix from inside the router. Routing only.
