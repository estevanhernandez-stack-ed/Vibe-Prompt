---
name: vibe-prompt:eval
description: This skill should be used when the user says "/vibe-prompt:eval", "drift test my prompts", "test my prompts against gemini", "test parity for the new model", or wants behavioral testing of LLM prompts in their app. Runs each prompt in inventory against the production model AND an in-session agent baseline (drift mode) OR against a candidate model (upgrade-test mode). Surfaces drift mechanically + via LLM-judge with explicit evaluator-drift warnings. Writes `.vibe-prompt/eval/state/eval-<timestamp>.json` + `docs/vibe-prompt/eval-<timestamp>.md`. Cost-gated. Read-mostly with action gates on vendor API calls.
---

# /vibe-prompt:eval

Load `vibe-prompt:guide` first. Then load `references/composer-mimic.md`, `references/vendor-clients.md`, `references/fixture-synthesis.md`, `references/mechanical-comparator.md`, `references/llm-judge-prompt.md`, `references/dashboard-template.md`, `references/swap-and-discard.md`, and `vibe-prompt:guide/references/calibration-patterns.md`.

## Inputs

- `.vibe-prompt/state/inventory.json` (required)
- `.vibe-prompt/eval/config.json` (required)
- `.vibe-prompt/eval/composer.json` (required)
- `.vibe-prompt/eval/agent.json` (required)
- `.vibe-prompt/eval/fixtures/*.json` (optional user-provided)
- CLI flags:
  - `--mode drift` (default) or `--mode upgrade-test --candidate <model>`
  - `--no-judge` to skip the LLM-judge layer entirely (no judge calls, no drift findings, no scores)
  - `--no-swap` to skip the Swap-and-Discard second judge pass (runs judge once per pair instead of twice; cheaper but position-bias not mitigated)
  - `--no-baseline` to skip the in-session baseline call (only valid in upgrade-test mode)
  - `--parallel <N>` to allow N parallel vendor calls (default: 1)
  - `--inject-attacks` (optional) to run the inject-attack sub-workflow after the standard pipeline. When present, iterates each scoped prompt × user-input var × fixture × vendor, judges each output with `inject-attack-judge.md`, and writes `injectAttackResults` + `injectAttackSummary` to `run-result.json`. Cost-gated separately. Without this flag, existing v0.3 behavior is unchanged.

## Workflow

1. **Pre-flight.**
   - `session-logger` start.
   - First-run check: if any of `.vibe-prompt/eval/{config,composer,agent}.json` missing, hand off to `vibe-prompt:first-run-setup`. After setup returns, resume.
   - Security pre-scan: per `vibe-prompt:guide` posture, grep state files for vendor key patterns. Abort if any match.
   - Read inventory.json, config, composer, agent — validate against schemas. Abort with a clear message on any schema failure.
   - Verify required env vars are set per config's `vendors`. Abort with a clear message if missing.

2. **Synthesize/load fixtures.** For each prompt in inventory, per `references/fixture-synthesis.md`. Cache the result in memory.

3. **Compose prompts.** For each (prompt, fixture) pair, apply `references/composer-mimic.md` to produce the composed system prompt + user content.

4. **Cost estimate.** Per the cost-gate rules in `vibe-prompt:guide`, tally projected tokens and dollars. Present the estimate. Wait for user confirm.

5. **Execute eval.** For each (prompt, fixture):
   - Call prod model via `GeminiClient` (or appropriate vendor) per `references/vendor-clients.md`. Update running cost.
   - Call baseline via `InSessionAgentClient` (drift mode only).
   - Apply mechanical comparator per `references/mechanical-comparator.md`. Run all checks in order: hard-fail → both-failed → schema-shape → **value-type-drift** (v0.4 new: fires when key is present but value type differs between prod/baseline or deviates from OUTPUT_SCHEMA declared type; includes value-type-drift-both variant; positioned between schema-shape and length-delta per the comparator reference) → length-delta → token-delta → empty.
   - **LLM-judge with Swap-and-Discard** per `references/llm-judge-prompt.md` and `references/swap-and-discard.md` (unless `--no-judge`):
     - Run 1 (original order): dispatch judge with prod as Output A, baseline as Output B. Capture judgment (SWRS shape: strengths_A, weaknesses_A, strengths_B, weaknesses_B, reasoning, scores_A, scores_B, driftFindings).
     - Run 2 (swapped order): dispatch judge with baseline as Output A, prod as Output B. Capture judgment. Skip if `--no-swap` flag set.
     - Compare: if the judge favors the same POSITION in both runs (position-tied) → discard as position-bias artifact; set `swapAndDiscard.tiedAndDiscarded = true`; do not include drift findings for this pair; increment tie count. If the judge favors the same UNDERLYING CONTENT in both runs (content-consistent) → accept findings; set `swapAndDiscard.tiedAndDiscarded = false`; average `scores_A` and `scores_B` across both runs for the final per-dimension scores.
     - Attach the cross-vendor evaluator-drift footer (per `references/llm-judge-prompt.md` post-processing rules) to each accepted drift finding before storing.
   - Append to in-memory eval-result.
   - Check running cost vs ceiling. If exceeded, set `abortedByCostCeiling = true` and break.

6. **Compute evalGrade per prompt.** After all judge calls complete:
   - For each prompt: average the prod dimension scores across both Swap-and-Discard runs (or the single run if `--no-swap`). Same for baseline. Store in the run-result's `evalGrade.dimensions.prod` and `evalGrade.dimensions.baseline`.
   - Compute per-prompt composite: weighted average of prod dimension scores (default equal weights). Apply overrides from `.vibe-prompt/grade/weights.json` if present.
   - Store `evalGrade.composite.prod` and `evalGrade.composite.baseline` per prompt.
   - Compute tie rate: `tiedCount / totalPairs`. If > 30%, friction-log `swap-and-discard-tie-rate-over-30pct` (medium confidence).

7. **Write eval-result.** Atomic write `.vibe-prompt/eval/state/eval-<runId>.json`. Validate against schema.

7.5. **Inject-attack sub-workflow (only when `--inject-attacks` flag is present).** After the standard eval result is written, execute `references/inject-attack-eval-workflow.md` in full:
   - Compute cost estimate (prompts × user-input vars × fixtures × vendors × $0.001 per judge call).
   - Present estimate; require user confirmation (or auto-proceed if `--auto` set).
   - Iterate: for each (scoped prompt × user-input var × fixture in `config.eval.injectAttack.fixtures` × vendor), substitute the fixture pattern into the var, call prod vendor, call in-session Claude baseline, invoke `references/inject-attack-judge.md` per output.
   - Aggregate into `injectAttackResults` (per-entry array) and `injectAttackSummary` (`successfulAttacks`, `resistanceRate`, `vendorBreakdown`).
   - Merge both fields into the same `run-result.json` (atomic re-write with inject-attack fields appended).
   - If `successfulAttacks > 0`: friction-log `injection-attack-succeeded` (high severity, `recommendedHandoff: "vibe-sec:audit"`).
   - Without `--inject-attacks`: skip this step entirely. v0.3 behavior is unchanged.

8. **Render dashboard.** Apply `references/dashboard-template.md` to write `docs/vibe-prompt/eval-<runId>.md` in the target app.

9. **Render banner.** ≤ 30 lines. Includes finding counts, cost spent, ceiling status, evalGrade composite (prod), Swap-and-Discard tie rate, path to report, next-step suggestion.

10. **Post-flight.** `session-logger` terminal entry with full summary.

## Banner template

```
═══ Vibe-Prompt eval ═══
Mode:           drift
Evaluator:      Claude Code (claude-opus-4-7)
Prompts:        14 run, 14 succeeded, 0 errored

Drift detected:
  High:         5 prompts (natal_interpretation, synastry_report, tarot_spread, dream_oracle, daily_tarot)
  Medium:       3 prompts
  Low:          2 prompts
  No drift:     4 prompts

Eval grade (prod avg):   6.2 / 10  [schema 7 · persona 4 · clarity 7 · tokens 7]
Swap-and-Discard:        14 pairs · 2 tied/discarded (14% tie rate)

Cost spent:     $0.17 of $2.00 ceiling
Fixtures:       12 synthesized, 2 user-provided

Report:         docs/vibe-prompt/eval-2026-05-28-1430.md
State:          .vibe-prompt/eval/state/eval-2026-05-28-1430.json

Suggested next: review natal_interpretation (5 findings); root cause likely in F2 voice contradiction (see vibe-prompt audit).
```

## Friction triggers

See `friction-triggers.md`. The eval command is the highest-volume friction emitter — cost overruns, vendor errors, judge dismissals.

## Never

- Read API keys from any file.
- Echo a key value (even last-4-chars rule applies; even in error output).
- Persist any key.
- Re-run a fixture mid-eval (deterministic per-eval).
- Run vendor calls before user confirms the cost estimate.
