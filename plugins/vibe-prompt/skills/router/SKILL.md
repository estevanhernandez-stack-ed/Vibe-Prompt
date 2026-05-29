---
name: vibe-prompt:router
description: This skill should be used when the user says "/vibe-prompt" (bare, no subcommand). Reads target-app state (inventory + audit + eval + radar + grade + iterate freshness), introduces Vibe-Prompt, and recommends the next move — never executes destructively without confirmation.
---

# /vibe-prompt (bare router)

Load `vibe-prompt:guide`. Then read target-app state and route. Branches 5 (grade) and 6 (iterate) are new in v0.3.

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

3b. **Eval state exists with non-empty `injectAttackResults`** → review-injection-attack-results branch.
   - Triggered when the latest `.vibe-prompt/eval/state/run-*.json` contains a non-empty `injectAttackResults` array (i.e., `--inject-attacks` was run and produced results).
   - Render: inject-attack summary from `injectAttackSummary` — `successfulAttacks` count, `resistanceRate`, and the highest-severity fixture that succeeded (if any).
   - Offer three next actions:
     1. **Review per-fixture results** — open the run-result file and walk through each fixture's `honoredAttack` field + `judgeReasoning`.
     2. **Dispatch `/vibe-prompt:evolve-prompt`** — use the `injection-attack-succeeded` friction signal to propose hardening changes to the audit detection or fixture library.
     3. **Run `/vibe-sec:audit` handoff** — F10/F11/F12 already emitted `handoffHint: "vibe-sec:audit"`; if any attack succeeded, cross-plugin handoff to vibe-sec for app-level user-input-handling review is recommended.
   - Wait for the user to choose. If no action selected, surface the summary and continue.

3c. **Pending remediation diffs exist** → review-pending-remediations branch (v0.5).
   - Triggered when `.vibe-prompt/remediate/pending/*.diff` is non-empty (at least one staged finding diff is awaiting review). Look for the glob `.vibe-prompt/remediate/pending/<finding-id>.diff`.
   - Render: a list of pending findings — `findingId`, `findingCategory` (A/B/C), `confidence`, `targetFile`, and `targetRange` read from each diff's YAML front-matter. Group by category for at-a-glance review.
   - Offer four next actions:
     1. **Review per-finding** — open one pending `.diff` file and walk through its front-matter + unified-diff body.
     2. **Apply a staged diff** — `/vibe-prompt:remediate --apply-pending <findingId>` writes the diff to the target file after confirming the backup path. Recommended workflow: review first, then apply.
     3. **Reject a staged diff** — `/vibe-prompt:remediate --reject-pending <findingId>` deletes the pending file and friction-logs `staged-fix-rejected` so `:evolve-prompt` can tune the confidence rubric for that category.
     4. **Re-run `/vibe-prompt:remediate`** — generates a fresh plan against the latest audit. Existing pending files are preserved; only new findings get appended.
   - Wait for the user to choose. If no action is selected, surface the summary and continue to branches 4-7.

4. **All three states exist, radar cache > 7 days old** → model news refresh suggested.
   - Render posture summary (top 3 audit findings + top 3 eval findings) + "Radar cache is stale — `/vibe-prompt:radar` to refresh? (zero LLM cost)"
   - Wait for confirm. If yes, hand off to radar. If no, surface full summary anyway.

5. **Eval exists, no `.vibe-prompt/grade/state/grade-*.json`** → grade pending.
   - Render: eval summary (top drift findings, tie rate if Swap-and-Discard ran) + "Run `/vibe-prompt:grade` to compute composite scores + check vs baseline?"
   - Wait for confirm. If yes, hand off to grade.

6. **Grade exists, no `.vibe-prompt/iterate/suggestions-*.json`** → iterate pending.
   - Render: grade summary (app composite + flagged regressions list) + "Want me to suggest new prompts your app could add? `/vibe-prompt:iterate` is creative discovery — runs one cheap LLM call (~$0.02) and proposes 3-5 ideas."
   - Wait for confirm. If yes, hand off to iterate.

7. **All fresh** → full posture summary.
   - Read inventory + audit + latest run-result + radar cache + latest grade-result + latest iterate suggestions.
   - Render: top 3 audit findings, top 3 eval findings (with evaluator-drift caveat: "LLM-judge findings — verify before acting; cross-vendor bias possible"), any new-model alerts from radar, app composite grade + trend (delta vs prior run), count of most recent iterate suggestions with "last run: YYYY-MM-DD."
   - Suggest re-running `/vibe-prompt:scan` if a code change pushed prompts since last scan.

## Workflow

1. Invoke `session-logger` start.
2. Read state. Pick branch (1 through 7 in order — first match wins).
3. Render banner.
4. If asking a question, use AskUserQuestion. Wait for response.
5. If handing off, defer to the target skill.
6. `session-logger` terminal entry.

## Never

- Run scan, audit, eval, radar, grade, or iterate without explicit user confirmation, even on first run.
- Suggest a state-mutating fix from inside the router. Routing only.
