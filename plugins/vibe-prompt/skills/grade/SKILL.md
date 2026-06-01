---
name: vibe-prompt:grade
description: >
  Synthesize audit + latest eval into per-prompt + app composite grades. Tracks regression vs
  monotonic baseline. Writes .vibe-prompt/grade/state/grade-<runId>.json and
  docs/vibe-prompt/grade-YYYY-MM-DD.md. Trigger phrases: "/vibe-prompt:grade", "grade my
  prompts", "show me regression", "compute composite scores".
---

# vibe-prompt:grade

Load `vibe-prompt:guide` first. Then load `references/monotonic-baseline.md`,
`references/composite-formula.md`, `references/grade-dashboard-template.md`,
and `vibe-prompt:guide/references/calibration-patterns.md`.

## Inputs

| Input | Required | Notes |
|---|---|---|
| `.vibe-prompt/state/audit.json` | REQUIRED | Produced by `/vibe-prompt:audit`. Validated against `audit.schema.json`. |
| `.vibe-prompt/eval/state/run-*.json` (latest) | OPTIONAL | If absent, grade computes from audit only and notes the limitation in the dashboard. |
| `.vibe-prompt/grade/state/baseline.json` | OPTIONAL | Created on first run. If absent, first run establishes baseline. |
| `.vibe-prompt/grade/weights.json` | OPTIONAL | User dimension-weight overrides. Auto-normalized if weights don't sum to 1.0. |
| `--accept-regression` CLI flag | OPTIONAL | Overrides monotonic baseline discipline: advances baseline even on regression. Friction-logs `regression-flagged-and-accepted-as-baseline`. |

## Workflow

### 1. Pre-flight

Start session-logger. Read and validate `audit.json` against `audit.schema.json`. If validation
fails, surface the error and stop — do not compute grades from a malformed audit. Read the latest
`run-*.json` from `.vibe-prompt/eval/state/` if it exists. Note if eval results are absent (grades
will be audit-only composites; surface this limitation in the banner and dashboard).

### 2. Compute per-prompt composites

For each prompt in `audit.json.auditGrade.perPrompt`:

- Pull audit-side dimension scores (`schemaTightness`, `personaConsistency`, `instructionClarity`,
  `tokenEfficiency`, `injectionResistance`).
- If eval results exist, pull the corresponding `evalGrade.dimensions` from the latest run-result
  (including `injectionResistance` if present).
- Average audit and eval dimension scores per dimension (when both exist); use audit-only when eval
  is absent. This applies to all 5 dimensions including `injectionResistance`.
- Read user weights from `.vibe-prompt/grade/weights.json` if present. Auto-normalize if weights
  don't sum to 1.0. Fall back to equal weights (0.20 each, v0.4) if the file is absent.
- **Legacy 4-dim migration:** if `weights.json` has 4 dimensions (no `injectionResistance` key),
  add `injectionResistance: 0.20` and auto-normalize all 5 weights. Log a normalization warning
  in the banner.
- Compute per-prompt composite per `references/composite-formula.md`.

### 2a. Compute app composite — per-workspace partition (v0.7+)

Inspect the audit findings for `workspaceIdentifier` fields (added in v0.7):

- **Multi-workspace audit** (at least one finding carries a non-null `workspaceIdentifier`):
  - Partition the audit findings — and the prompts they reference — by `workspaceIdentifier`,
    grouping findings + prompts into per-workspace buckets.
  - For each workspace bucket, compute its per-workspace composite as the average of the
    per-prompt composites scoped to that workspace.
  - Emit `appComposite.perWorkspace[<workspaceName>]` as a number for each workspace with at
    least one finding-bearing prompt.
  - Workspaces with zero findings (or whose prompts produced no composite) get
    `perWorkspace[<workspaceName>] = null` AND their name appended to
    `appComposite.workspacesWithNoFindings[]`.
  - Compute `appComposite.aggregate` = arithmetic mean of all non-null per-workspace composites.
    `aggregate` preserves v0.6 single-number semantics for any back-compat consumer that reads
    `appComposite` and expects one number — they'll read `aggregate` going forward.
- **Single-workspace audit** (no finding carries a `workspaceIdentifier`, OR all values are
  null): emit `appComposite` as a flat number (v0.6 shape — preserved via the schema oneOf
  branch). Do NOT emit `perWorkspace` / `aggregate` / `workspacesWithNoFindings` keys in this
  case; downstream consumers continue to read `appComposite` as a single integer composite
  exactly as in v0.6. This is the back-compat path.

### 3. Compare vs monotonic baseline

Read `baseline.json` if it exists. Apply the monotonic algorithm per
`references/monotonic-baseline.md`:

**First run (no baseline.json):**
- Establish baseline at current composites for all prompts and app composite.
- status = "no-prior-baseline", delta = 0 for all.
- Write initial `baseline.json`.

**Subsequent runs:**
- For each prompt: compare current composite vs baseline composite.
  - current >= baseline: advance baseline to current; status = "improved" (if >) or "stable"
    (if ==).
  - current < baseline: do NOT advance baseline; status = "regressed"; delta = negative; add to
    `flaggedRegressions`.
- Apply same logic for `appComposite`.

**`--accept-regression` override:**
- Friction-log `regression-flagged-and-accepted-as-baseline` with medium confidence.
- Advance baseline to current composite even on regression. Note the override in the dashboard.

### 4. Write grade-result state file

Write `.vibe-prompt/grade/state/grade-<runId>.json` (runId = `grade-<YYYY-MM-DD>-<HHMM>`)
validated against `grade-result.schema.json`. Fields: `version`, `runId`, `computedAt`,
`sourceAuditRef`, `sourceEvalRunRef` (null if absent), `perPrompt` (composite + dimensions +
vsBaseline per prompt), `appComposite`, `appCompositeVsBaseline`, `flaggedRegressions`.

### 5. Write updated baseline.json

Write `.vibe-prompt/grade/state/baseline.json` validated against `baseline.schema.json`.
Update `lastAdvancedAt` and per-prompt `establishedInRunId` only where the baseline advanced.

### 6. Render dashboard

Render per `references/grade-dashboard-template.md` → `docs/vibe-prompt/grade-<YYYY-MM-DD>.md`.
Create `docs/vibe-prompt/` if absent.

### 7. Render banner

Surface in chat:

```
vibe-prompt:grade complete

App composite: <N>/10 <arrow> (<delta> vs baseline)
Status: <improved|stable|regressed|first-run>

<If regressed:>
⚠ Regressions detected: <N> prompts. Baseline NOT advanced. Investigate before re-running.
  → Flagged: <prompt-id> (<dimension> -<delta>)

<If improved:>
Baseline advanced. That's the new bar.

Dashboard: docs/vibe-prompt/grade-<YYYY-MM-DD>.md
Next: /vibe-prompt:iterate to surface new prompt opportunities.
```

### 8. Post-flight

Session-logger terminal.

## Outputs

| Output | Path |
|---|---|
| Grade result state | `.vibe-prompt/grade/state/grade-<runId>.json` |
| Updated baseline | `.vibe-prompt/grade/state/baseline.json` |
| Human dashboard | `docs/vibe-prompt/grade-<YYYY-MM-DD>.md` |

## Never

- No LLM calls in `:grade` — pure synthesis from audit.json + run-result.json inputs. If you find
  yourself reaching for a model call, stop and re-read the workflow.
- Never modify `audit.json` or any `run-result.json` — they are read-only inputs to `:grade`.
- `baseline.json` never decreases without the explicit `--accept-regression` flag. The monotonic
  property is the point — enforced, not advisory.
