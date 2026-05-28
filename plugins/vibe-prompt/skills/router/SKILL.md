---
name: vibe-prompt:router
description: This skill should be used when the user says "/vibe-prompt" (bare, no subcommand). Reads target-app state (inventory + audit freshness), introduces Vibe-Prompt, and recommends the next move — never executes destructively without confirmation.
---

# /vibe-prompt (bare router)

Load `vibe-prompt:guide`. Then read target-app state and route.

## State checks

1. **No `.vibe-prompt/state/inventory.json`** → first run.
   - Render: "No inventory cached. Want me to run `/vibe-prompt:scan` to inventory your prompts? (read-only)"
   - Wait for confirm. If yes, hand off to scan. If no, exit.

2. **Inventory exists, no `audit.json`** → audit pending.
   - Render: inventory summary (counts) + "No audit yet. Want me to run `/vibe-prompt:audit` against the cached inventory?"
   - Wait for confirm. If yes, hand off to audit.

3. **Audit exists** → posture summary.
   - Read inventory + audit.
   - Render: ≤ 30 lines summary. Counts, top 3 findings, audit age (days since last run).
   - If audit > 14 days old, suggest `/vibe-prompt:scan` to refresh.
   - Otherwise close with: "All caught up. Re-run `/vibe-prompt:scan` after prompt changes to re-check."

## Workflow

1. Invoke `session-logger` start.
2. Read state. Pick branch.
3. Render banner.
4. If asking a question, use AskUserQuestion. Wait for response.
5. If handing off, defer to the target skill.
6. `session-logger` terminal entry.

## Never

- Run scan or audit without explicit user confirmation, even on first run.
- Suggest a state-mutating fix from inside the router. Routing only.
