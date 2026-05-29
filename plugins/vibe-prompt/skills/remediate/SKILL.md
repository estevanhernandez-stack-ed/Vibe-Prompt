---
name: vibe-prompt:remediate
description: This skill should be used when the user says "/vibe-prompt:remediate", "fix my prompts", "apply the audit recommendations", "remediate findings", or wants to close the audit → fix loop. Reads `.vibe-prompt/state/audit.json` + (optional) latest `run-result.json` + `inventory.json` + `composer.json`; generates per-finding diffs via category-mapped templates (A/B/C); routes by confidence (≥0.90 auto-write with backup, 0.70-0.89 stage in `.vibe-prompt/remediate/pending/`, <0.70 inline-only); supports backup + rollback, F12 handoff banner, per-finding interactive review.
---

# vibe-prompt:remediate

Load `vibe-prompt:guide` first. Then load `references/fix-categories.md`,
`references/confidence-rubric.md`, `references/delimiter-naming.md`,
`references/diff-patch-helpers.md`, and `references/rollback-workflow.md`.

This is the sixth step-command in the vibe-prompt pipeline — it closes the gap between
"the audit told us what's wrong" and "the prompts are actually fixed." Confidence-routed
like `/vibe-sec:fix`, with structural-edit-aware staging.

## Inputs

| Input | Required | Notes |
|---|---|---|
| `.vibe-prompt/state/audit.json` | REQUIRED | Produced by `/vibe-prompt:audit`. Validated against `audit.schema.json`. |
| `.vibe-prompt/state/inventory.json` | REQUIRED | Produced by `/vibe-prompt:scan`. Source of truth for prompt locations + var origin. |
| `.vibe-prompt/eval/composer.json` | OPTIONAL | When present, Category A confidence floors at 0.92; absent floors at 0.80. |
| `.vibe-prompt/eval/state/run-*.json` (latest) | OPTIONAL | Eval signal informs which findings already correlate with regression. |
| `.vibe-prompt/config/remediate-thresholds.json` | OPTIONAL | User overrides for auto-write + stage thresholds. |
| `--apply-pending <findingId>` | OPTIONAL | Apply a previously-staged diff after review. |
| `--reject-pending <findingId>` | OPTIONAL | Delete a staged diff; friction-log `staged-fix-rejected`. |
| `--rollback <ISO-timestamp>` | OPTIONAL | Restore files from a backup batch. |
| `--interactive` | OPTIONAL | Per-finding y/n review. |
| `--auto-apply` | OPTIONAL | CI mode — bypass user gate, write all ≥0.90 diffs. |
| `--skip-f12` | OPTIONAL | Suppress the F12 handoff banner for this run. |
| `--apply-contradictions` | OPTIONAL | Opt-in to auto-write Category B diffs (voice contradictions). |

## Workflow

### 1. Read state

Start `session-logger`. Read and validate `.vibe-prompt/state/audit.json` against
`audit.schema.json`. Read `.vibe-prompt/state/inventory.json` and validate against
`inventory.schema.json`. Read `.vibe-prompt/eval/composer.json` if present (validates
against `composer.schema.json`). Read latest `.vibe-prompt/eval/state/run-*.json` if
present.

If `audit.json` missing, instruct user to run `/vibe-prompt:audit` first and exit.

Read `.vibe-prompt/config/remediate-thresholds.json` if present; otherwise use defaults
(autoApplyThreshold 0.90, stageThreshold 0.70, backupRetentionDays 30).

### 2. Group findings by fix category

Walk `audit.json.findings`. Map each finding to a fix category per
`references/fix-categories.md`:

- **Category A — Composer-level additions** → F9 findings
- **Category B — Contradiction removal** → F2 findings
- **Category C — Defense addition** → F10 and F11 findings; F12 high-severity (confidence-degraded) fallback
- **F12 critical** → handoff banner only, NOT proposed (see §F12 handoff below)
- **Other findings (F1, F1b, F3, F4, F5, F6, F7)** → inline recommendation only in v0.5 (deferred to future versions)

Skip findings already flagged `originFilteredOut: true` in the audit (system-injected
vars; not user-controlled — no Category C target).

### 3. Generate proposed diff + score confidence

For each grouped finding:

1. Locate the target file + range using:
   - Category A: `composer.json.layers[]` → identify master-directive composer file + line
     where `masterSystemInstruction` is assembled
   - Category B: `audit.findings[].evidence.promptLocation` → registry entry or inline
     prompt file:line
   - Category C: `audit.findings[].evidence.promptLocation` plus
     `inventory.inlinePrompts[].templatedVars[]` to know which user-var to wrap

2. Generate the diff body using the category-specific template from
   `references/fix-categories.md`. Substitute concrete values:
   - Category A: detect `currentDateExpr` from existing patterns in the composer file
     (`new Date().toISOString().split('T')[0]`, `dayjs().format('YYYY-MM-DD')`); fall
     back to vanilla `new Date().toISOString().split('T')[0]`
   - Category B: pull banned phrases from F2 evidence; apply find-and-rephrase rules
   - Category C: pull user-var name from F10 evidence; derive delimiter name per
     `references/delimiter-naming.md`

3. Score confidence per the 5-dimension rubric in `references/confidence-rubric.md`:
   locate-confidence (0.30) + diff-shape (0.25) + voice-risk (0.20) + schema-impact (0.15)
   + version-bump (0.10). Weighted-average to a single 0-1 confidence.

### 4. Route by confidence

Apply the routing thresholds (override-aware):

| Confidence | Route |
|---|---|
| ≥ 0.90 (or `--auto-apply` for any confidence) | **auto-write** to source file with backup |
| 0.70 – 0.89 | **stage** to `.vibe-prompt/remediate/pending/<finding-id>.diff` |
| < 0.70 | **inline-only** — emit recommendation text only, no file action |

**Category B override:** Category B always stages by default regardless of confidence.
Auto-write requires `--apply-contradictions` opt-in (voice-drift risk is non-trivial).

**`--auto-apply` semantics:** in CI mode, every Category A + C diff at ≥0.90 writes
without user gate. Category B still stages unless `--apply-contradictions` is ALSO
passed.

### 5. Present plan + user gate

Render the summary banner:

```
═══ Vibe-Prompt remediate ═══
Total findings: N
  Category A (composer):       <a> diffs (avg conf <ac>)
  Category B (contradiction):  <b> diffs (avg conf <bc>)
  Category C (defense):        <c> diffs (avg conf <cc>)

Routing:
  Auto-write (≥0.90):  <aw> diffs
  Stage (0.70-0.89):   <st> diffs
  Inline-only (<0.70): <il> diffs

F12 handoffs emitted: <f12>

Default action: stage and review (no auto-write).
Pass --auto-apply to write all ≥0.90 confidence diffs.
```

Then ask the user:
- Bare run: `Proceed with the staged plan? (y/n)` — applies the routing as-is.
- `--interactive` run: per-finding `y/n/skip` for each Category A + C diff.

### 6. Apply or stage

Create the backup batch dir: `.vibe-prompt/remediate/backup/<ISO-timestamp>/`. For each
auto-write diff:
1. Copy target file → `<backup-batch>/<relative-source-path>.bak` (preserves
   directory structure).
2. Apply diff via line-context match (see `references/diff-patch-helpers.md`). On
   conflict, skip + friction-log `auto-write-conflict`.
3. Log the apply event to `.vibe-prompt/remediate/state/runs.jsonl` (see §State files
   below).

For each staged diff:
1. Write to `.vibe-prompt/remediate/pending/<finding-id>.diff` as YAML front-matter +
   unified-diff body. Front-matter validates against `pending-fix.schema.json`.
2. Log the stage event to `runs.jsonl`.

For inline-only diffs: emit the recommendation text in the banner; log to `runs.jsonl`
with action `inline-only`.

### 7. Post-apply guidance

For each applied auto-write diff, append `postApplyRecommendation` to the dashboard:

> Re-run `/vibe-prompt:eval --prompts <promptId>` to confirm the fix moved the
> composite forward. Then `/vibe-prompt:grade` to update the monotonic baseline.

For staged diffs, the same recommendation lands in the pending file's
`postApplyRecommendation` front-matter field.

For Category A composer-level fixes: ALSO recommend a fresh `/vibe-prompt:audit` since
the global directive layer changed.

### 8. Friction-log

For each event below, append to `.vibe-prompt/state/friction.jsonl` via the friction
trigger catalog (see `friction-logger/references/friction-triggers.md`):

- User rejected an auto-write proposal → `staged-fix-rejected` (medium) → tune confidence rubric
- User rolled back an auto-applied diff → `auto-write-rolled-back` (high) → lower threshold OR tune category routing
- Composer.json absent and Category A fell back to 0.80 floor → `composer-auto-generation-confidence-low` (medium)
- After apply + re-eval, baseline advanced → `staged-fix-applied-and-eval-confirms-improvement` (positive)

End with `session-logger` terminal entry.

## F12 handoff banner

F12 critical findings: `:remediate` does NOT propose a fix. Instead emits:

> F12 fired critical on `<promptId>`. Composition-order fixes belong upstream in your
> composer architecture (`<composerPath>`), not in this prompt. Run `/vibe-sec:audit`
> for app-level user-input boundary review, then decide whether to restructure the
> composer or scope the user var into a [DATA] block.

`--skip-f12` flag suppresses the handoff banner when the user is intentionally not
fixing F12 in this pass.

**F12 high-severity fallback:** when F12 fires at `high` severity (confidence-degraded
due to missing or low-confidence composer.json), Category C still proposes a defense
block — because severity is non-critical, the additive defense is a reasonable
intermediate fix.

## State files

The `.vibe-prompt/remediate/` directory holds three persistent surfaces. All paths are
relative to the target app root.

### `.vibe-prompt/remediate/state/runs.jsonl` — append-only ledger

Every apply / stage / reject / rollback / inline-only event appends one JSON line.
Schema per entry:

```json
{
  "timestamp": "2026-05-30T09:00:00Z",
  "runId": "remediate-2026-05-30-0900",
  "action": "applied" | "staged" | "rejected" | "rolled-back" | "inline-only",
  "findingIds": ["F9-arithmancy_natal-2026-05-29"],
  "confidence": 0.94,
  "fileTouched": "src/lib/gemini.ts",
  "backupPath": ".vibe-prompt/remediate/backup/2026-05-30-0900/src/lib/gemini.ts.bak"
}
```

Append-only — never rewrite. The dashboard reads this to surface remediate history.

### `.vibe-prompt/remediate/backup/<ISO-timestamp>/` — per-batch backup dir

One subdirectory per remediate run that wrote at least one file. ISO timestamp matches
the `runId` minute precision (`YYYY-MM-DD-HHMM`). Mirrors the source tree:

```
.vibe-prompt/remediate/backup/2026-05-30-0900/
  src/
    lib/
      gemini.ts.bak
      ConfigService.ts.bak
```

`.bak` files are byte-for-byte copies of the pre-application source. Rollback restores
from these (see `references/rollback-workflow.md`).

Backups older than `remediate.backupRetentionDays` (config schema; default 30) MAY be
pruned by a future maintenance command; v0.5 does not prune automatically.

### `.vibe-prompt/remediate/pending/<finding-id>.diff` — staged fix file

YAML front-matter (validated against `pending-fix.schema.json`) + unified-diff body.
Front-matter fields:

```yaml
---
findingId: F2-natal_interpretation-2026-05-29
findingCategory: B
confidence: 0.75
targetFile: src/lib/ConfigService.ts
targetRange: L67-L102
backupPath: .vibe-prompt/remediate/backup/2026-05-30-0900/ConfigService.ts.bak
recommendationSource: audit-2026-05-29-1830
postApplyRecommendation: "Re-run /vibe-prompt:eval --prompts natal_interpretation to confirm Pilgrim leak no longer fires."
versionBumpRequired: true
suggestedVersion: "3.6.0"
stagedAt: "2026-05-30T09:00:00Z"
---
@@ -76,1 +76,1 @@
- 1. **THE REVELATION (The Prophecy):** A cryptic, poetic quatrain-style narrative that welcomes the Fellow Pilgrim to their path.
+ 1. **THE REVELATION (The Prophecy):** A cryptic, poetic quatrain-style narrative that welcomes {{name}} to their path. Address them in second person, per the global voice rule.
```

`--apply-pending <findingId>` reads this file, applies the diff, logs to `runs.jsonl`,
and deletes the pending entry. `--reject-pending <findingId>` deletes the pending entry
and friction-logs `staged-fix-rejected`.

## Banner template

```
═══ Vibe-Prompt remediate ═══
Findings remediated:   <N>
  Applied (auto-write): <a>
  Staged:               <s>
  Inline-only:          <i>
  F12 handoffs:         <f>

Backup batch:   .vibe-prompt/remediate/backup/<timestamp>/
Pending dir:    .vibe-prompt/remediate/pending/
Ledger:         .vibe-prompt/remediate/state/runs.jsonl

Suggested next step: /vibe-prompt:eval --prompts <impactedPromptIds>
```

## Never

- Apply a diff at confidence below the auto-write threshold without explicit user
  approval or `--auto-apply` in CI mode.
- Auto-write a Category B (contradiction-removal) diff without `--apply-contradictions`.
- Propose a Category C fix for a `system-injected` var (would be a non-bug fix).
- Propose ANY fix for an F12 critical finding — emit the handoff banner instead.
- Prune backup batches automatically in v0.5. Retention is policy-only for now.
- Mutate source files without writing the backup first. Order is: backup → apply →
  ledger entry.
