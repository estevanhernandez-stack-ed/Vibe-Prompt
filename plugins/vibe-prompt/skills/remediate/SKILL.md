---
name: vibe-prompt:remediate
description: This skill should be used when the user says "/vibe-prompt:remediate", "fix my prompts", "apply the audit recommendations", "remediate findings", or wants to close the audit → fix loop. Reads `.vibe-prompt/state/audit.json` + (optional) latest `run-result.json` + `inventory.json` + `composer.json`; generates per-finding diffs via category-mapped templates (A/B/C); routes by confidence (≥0.90 auto-write with backup, 0.70-0.89 stage in `.vibe-prompt/remediate/pending/`, <0.70 inline-only); supports backup + rollback, F12 handoff banner, per-finding interactive review.
---

# vibe-prompt:remediate

Load `vibe-prompt:guide` first. Then load `references/fix-categories.md`,
`references/confidence-rubric.md`, `references/delimiter-naming.md`,
`references/diff-patch-helpers.md`, `references/rollback-workflow.md`, and
(v0.6+) `references/voice-frame-detection.md`.

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

**v0.6 voice-rule extraction (Category B prerequisite).** Before generating
Category B diffs, run a voice-rule extraction pass against the global-directive
layer (per `composer.json.layers[]` where `type === "global-directive"`). The
extraction reads the directive content and returns:

- `bans` — explicit bans pulled by regex (`(?i)never (use|say|call|address)`,
  `(?i)not (a|the) X`, `(?i)avoid X`, `(?i)don'?t (use|say|address)`) plus
  implied bans projected by persona-affirmation patterns
- `positive guidance` — persona affirmations (`(?i)plain (modern|simple) language`,
  `(?i)contractions`, `(?i)warm.{1,30}friend`, `(?i)second person`,
  `(?i)conversational`, `(?i)direct`) — each affirmation projects an implied ban
  for the contradicting voice frame (e.g. plain modern language bans archaic)
- `globalConfidence` — mean of per-rule confidences (0-1)

Each extracted rule carries a `confidence` value derived from the matching pattern's
table in `references/voice-frame-detection.md` § "Voice-rule extraction from
global directive". Confidence per rule informs which voice-frame contradictions
are actionable in step 3b.

When `globalConfidence < 0.6`, friction-log
`category-b-voice-frame-detection-confidence-low` (medium) and SKIP the
voice-frame sub-category for this run — too noisy to act on. Banned-phrase
Category B (v0.5 behavior) continues unaffected.

When the global-directive layer is absent or empty, voice-rule extraction
returns zero rules; the voice-frame sub-category silently skips.

**v0.6 voice-frame phrase detection (Category B sub-category split).** After
voice-rule extraction, scan task prompt content for voice-frame phrase clusters
using the three pattern families documented in `references/voice-frame-detection.md`:

1. **Archaic vocabulary** — regex on known archaic patterns ("thou", "verily",
   "ancient", "veil", "mercury", "prophetic", "quatrain", "Fellow").
2. **Ritualistic framing** — phrases that frame the LLM as a sacred act
   ("the cosmos", "the divine", "the source", "sacred reading", "revealed unto").
3. **Capitalized abstract nouns** — `the Pilgrim`, `the Way`, `the Source`,
   `the Path`, `the Seeker`, `the Truth of ...`.

Each match emits a `{phrase, location, banSource}` triple. `phrase` is the
literal text matched; `location` is `{file, line, columnStart, columnEnd}` from
the inventory/registry locator; `banSource` is the extracted voice rule whose
ban (explicit or implied) the phrase contradicts.

Aggregate the triples into a `voiceFrameContradictions` array on the audit
finding (per `audit.schema.json` v0.6 extension). The audit emits the array;
:remediate consumes it to drive Category B sub-category routing in step 3a.

**Fixture coverage anchor.** The Celestia3 natal_interpretation prompt is the
canonical fixture: "quatrain-style narrative", "shattering of the veil", "ancient
dust", "mirrors of mercury", "prophetic shadows" all match the archaic-vocabulary
patterns above, each mapping its `banSource` to either an explicit ban or the
"plain modern language" persona-affirmation implied ban.

Voice-frame findings inside code fences, `[BRACKETS]` blocks, or templated vars
are suppressed (those are structural markup, not voice). The locator step
consults `inventory.json` to identify these structural zones.

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

F12 critical findings: `:remediate` does NOT propose a fix. The decision is intentional
— composition-order is an architecture-level concern (which layer receives the user var,
relative to the system instruction layer), not a prompt-level edit. Proposing a diff
inside the prompt would mask the real issue. Instead, emit the handoff banner:

> F12 fired critical on `<promptId>`. Composition-order fixes belong upstream in your
> composer architecture (`<composerPath>`), not in this prompt. Run `/vibe-sec:audit`
> for app-level user-input boundary review, then decide whether to restructure the
> composer or scope the user var into a [DATA] block.

The `<composerPath>` placeholder is filled from `composer.json.layers[]`'s source-file
reference (or the audit finding's `evidence.compositionStackLocation` when composer.json
is absent). The `<promptId>` placeholder comes from `audit.findings[].evidence.promptId`.

The banner records to `runs.jsonl` with action `inline-only` and findingCategory `F12-handoff`
so the dashboard can surface the handoff even though no file was touched.

`--skip-f12` flag suppresses the handoff banner when the user is intentionally not
fixing F12 in this pass — useful when the user is iterating on Category A/C fixes and
wants to defer the composer restructure until later.

**F12 high-severity Category C fallback:** when F12 fires at `high` severity
(confidence-degraded due to missing or low-confidence composer.json — see audit step 4e),
Category C still proposes a defense block. Because severity is non-critical, the additive
defense is a reasonable intermediate fix: it hardens the prompt now without committing
to the composer restructure. The banner labels these proposals with
`note: "F12 high — intermediate Category C fix; composer restructure deferred"` so the
user knows the fix is provisional.

**Cross-plugin coordination.** The F10/F11 `handoffHint: "vibe-sec:audit"` annotations
(emitted by the audit) remain advisory after `:remediate` applies a Category C fix —
vibe-sec still cares about app-level boundary review even after the prompt-level defense
is added. `:remediate` does NOT auto-invoke vibe-sec (boundary respected); the user
chooses when to dispatch the handoff.

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
