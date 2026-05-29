---
name: vibe-prompt:eval
description: This skill should be used when the user says "/vibe-prompt:eval", "drift test my prompts", "test my prompts against gemini", "test parity for the new model", or wants behavioral testing of LLM prompts in their app. Runs each prompt in inventory against the production model AND an in-session agent baseline (drift mode) OR against a candidate model (upgrade-test mode). Surfaces drift mechanically + via LLM-judge with explicit evaluator-drift warnings. Writes `.vibe-prompt/eval/state/eval-<timestamp>.json` + `docs/vibe-prompt/eval-<timestamp>.md`. Cost-gated. Read-mostly with action gates on vendor API calls.
---

# /vibe-prompt:eval

Load `vibe-prompt:guide` first. Then load `references/composer-mimic.md`, `references/vendor-clients.md`, `references/fixture-synthesis.md`, `references/mechanical-comparator.md`, `references/llm-judge-prompt.md`, `references/dashboard-template.md`.

## Inputs

- `.vibe-prompt/state/inventory.json` (required)
- `.vibe-prompt/eval/config.json` (required)
- `.vibe-prompt/eval/composer.json` (required)
- `.vibe-prompt/eval/agent.json` (required)
- `.vibe-prompt/eval/fixtures/*.json` (optional user-provided)
- CLI flags:
  - `--mode drift` (default) or `--mode upgrade-test --candidate <model>`
  - `--no-judge` to skip the LLM-judge layer
  - `--no-baseline` to skip the in-session baseline call (only valid in upgrade-test mode)
  - `--parallel <N>` to allow N parallel vendor calls (default: 1)

## Workflow

1. **Pre-flight.**
   - `session-logger` start.
   - First-run check: if any of `.vibe-prompt/eval/{config,composer,agent}.json` missing, hand off to `vibe-prompt:first-run-setup`. After setup returns, resume.
   - Security pre-scan: per `vibe-prompt:guide` posture, grep state files for vendor key patterns. Abort if any match.
   - Read inventory.json, config, composer, agent — validate against schemas. Abort with a clear message on any schema failure.
   - Verify required env vars are set per config's `vendors`. Abort with a clear message if missing.

2. **Synthesize/load fixtures.** For each prompt in inventory, per `references/fixture-synthesis.md`. Cache the result in memory.

3. **Compose prompts.** For each (prompt, fixture) pair, apply `references/composer-mimic.md` to produce the composed system prompt + user content.

4. **Cost estimate.** Per `references/cost-gates.md` (in the guide), tally projected tokens and dollars. Present the estimate. Wait for user confirm.

5. **Execute eval.** For each (prompt, fixture):
   - Call prod model via `GeminiClient` (or appropriate vendor) per `references/vendor-clients.md`. Update running cost.
   - Call baseline via `InSessionAgentClient` (drift mode only).
   - Apply mechanical comparator per `references/mechanical-comparator.md`.
   - Run LLM-judge per `references/llm-judge-prompt.md` (unless `--no-judge`).
   - Append to in-memory eval-result.
   - Check running cost vs ceiling. If exceeded, set `abortedByCostCeiling = true` and break.

6. **Write eval-result.** Atomic write `.vibe-prompt/eval/state/eval-<runId>.json`. Validate against schema.

7. **Render dashboard.** Apply `references/dashboard-template.md` to write `docs/vibe-prompt/eval-<runId>.md` in the target app.

8. **Render banner.** ≤ 30 lines. Includes finding counts, cost spent, ceiling status, path to report, next-step suggestion.

9. **Post-flight.** `session-logger` terminal entry with full summary.

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
