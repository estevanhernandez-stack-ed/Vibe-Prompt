# Monotonic baseline — grade

Baseline = "best score so far," NOT "most recent run."

## State files

- `.vibe-prompt/grade/state/baseline.json` (validated against `baseline.schema.json`)
- `.vibe-prompt/grade/state/grade-<runId>.json` (validated against `grade-result.schema.json`)

## Algorithm

For each grade computation:

1. Read current per-prompt composites from this run's audit + eval scores.
2. Read `baseline.json` if it exists.

For each prompt:

a. If no prior baseline for this prompt:
   - Establish baseline at current composite
   - status = "no-prior-baseline"
   - delta = 0

b. If current >= baseline:
   - Advance baseline to current
   - status = "improved" (if >) or "stable" (if ==)
   - delta = current - baseline

c. If current < baseline:
   - Do NOT advance baseline
   - status = "regressed"
   - delta = current - baseline (negative)
   - Add to flaggedRegressions

For app composite: same logic.

3. Write updated baseline.json (with new advanced timestamps where applicable).
4. Write grade-result.json with status + delta per prompt + flaggedRegressions list.

## When a regression is flagged

If status = "regressed" with magnitude > 1 point on any dimension:
- Surface prominently in the dashboard with ⚠ icon
- Friction-log `regression-flagged` with high confidence (or `regression-flagged-and-accepted-as-baseline`
  if user explicitly overrides to advance the baseline anyway via `:grade --accept-regression`)
- Suggest user investigate: which finding caused the regression? Did a fix actually land?

## Why monotonic

Monotonic discipline prevents "gradual ratchet" failure — the scenario where fixing one bug
introduces another, the composite barely changes, and the team loses track of whether quality is
improving or decaying. "Best ever" is the only baseline that answers the question "are we better
than our best?"

The override path (`--accept-regression`) exists for legitimate cases: deliberate architectural
tradeoffs that sacrifice one dimension to improve another, or cases where the baseline was set on
a badly-configured scoring run. Every override friction-logs so evolve-prompt can detect when the
discipline is being overridden systematically (signal: the formula may need re-calibration).
