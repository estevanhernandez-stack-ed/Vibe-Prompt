---
name: vibe-prompt:audit
description: This skill should be used when the user says "/vibe-prompt:audit", "audit my prompts", "what's wrong with my prompts", "find prompt smells", "structural prompt review", or wants a structural audit of LLM prompts in their app. Reads `.vibe-prompt/state/inventory.json` (required prerequisite — created by `/vibe-prompt:scan`), applies the F1-F12 rubric (F1-F9 active; F10-F12 Phase 4), writes `.vibe-prompt/state/audit.json` and a human-readable `docs/vibe-prompt/audit-YYYY-MM-DD.md`. Read-only — no source mutation.
---

# /vibe-prompt:audit

Load `vibe-prompt:guide` first. Then load `references/smell-rubric-f1-f12.md`, `references/audit-report-template.md`, `references/scoring-dimensions.md`, and `vibe-prompt:guide/references/calibration-patterns.md`.

Apply the F1-F12 rubric (F1-F9 active in v0.4; F10-F12 are Phase 4) to the cached inventory. Emit machine-readable findings + human-readable dated report.

## Inputs

- `.vibe-prompt/state/inventory.json` in the target app — REQUIRED.
- No flags in v0.1.

## Workflow

1. **Pre-flight.** Invoke `session-logger` start. Read `.vibe-prompt/state/inventory.json`. If missing, instruct the user to run `/vibe-prompt:scan` first and exit. Validate inventory against `plugins/vibe-prompt/schemas/inventory.schema.json` — if invalid, friction-log `inventory-schema-violation` and abort.
2. **Apply rubric.** Walk `references/smell-rubric-f1-f12.md` in order F1 → F1b → F2 → F3 → F4 → F5 → F6 → F7 → F9. (F10-F12 are Phase 4; not yet active.) For each smell, run the detection rule against `inventory.json`. If it fires, build a finding object: `{ id, smell, severity, evidence[], recommendation }`. Use the recommendation template, filling in concrete values from inventory (file paths, IDs, counts).
3. **F2 semantic pass.** Voice-contradiction detection cannot run from inventory alone — it needs prompt content. Re-read each voice-bearing prompt's content from the target source. Compare global directive (if present in registry as a `*directive` / `*persona` entry) against each task prompt. Surface contradictions with specific file:line citations on BOTH the rule and the violation.
4. **F6 known-model lookup.** Compare each `modelIdentifiers[*].value` against the bundled known-models list (in `references/smell-rubric-f1-f12.md` §F6). If unrecognized, the suspect-model variant of F6 fires with elevated severity language and a "verify what's actually served" recommendation.
4b. **F9 date-grounding check.** For each prompt in inventory (registry entries + inline prompts):
   - **Step A — Date-intent match:** scan the prompt's content + any `templatedVars` entries. Check for:
     - Keyword regex: `\b(?:birth ?date|birthday|birth ?day|transit|natal|nativity|current|today|now|year|month|age|when)\b` (case-insensitive)
     - Templated date vars: matches `{{[^}]*[Dd]ate[^}]*}}`, `{{[^}]*[Dd]ob[^}]*}}`, or `{{[^}]*[Bb]irth[^}]*}}`
     - If step A produces no match, skip this prompt for F9.
   - **Step B — Composition-stack temporal anchor:** inspect the composition stack (global directive from composer.json or inventory + this prompt's content + any wrapping layers). Check for:
     - Literal markers: `[CURRENT DATE]`, `[TODAY]`, `[NOW]`, `[CURRENT_TIMESTAMP]`
     - Phrase markers (case-insensitive): `today is`, `current date`, `as of`
     - Injected templated date vars at the global layer (composer-mimic already identifies these layers)
   - **Fire when:** step A matched AND step B found nothing. Build finding `{ id: "F9", severity: "high", evidence: { promptId, promptLocation, dateKeywords[], compositionStackLocation }, recommendation: <template from rubric> }`.
   - **Confidence degrade:** if composer-mimic confidence is < 0.6 for this app (check `.vibe-prompt/eval/composer.json` `confidence` field if available), set severity to `"medium"` instead of `"high"` and add `"composition stack detection low-confidence; verify manually"` to evidence.
   - **False-positive escape:** if `--ignore-finding F9 --on-prompt <id>` was passed in the CLI flags, skip F9 for that specific prompt id.
5. **Compose summary.** Count findings by severity → `summary.byCategory`. Total → `summary.totalFindings`.
6. **Compute per-prompt scores.** Per `references/scoring-dimensions.md` and the Score impact sections in `references/smell-rubric-f1-f12.md`:
   - For each prompt in inventory, start each dimension (schemaTightness, personaConsistency, instructionClarity, tokenEfficiency) at 10.
   - For each fired finding that targets this prompt, apply its Score impact deductions to the affected dimensions.
   - Floor each dimension at 1 (no dimension goes below 1).
   - Compute per-prompt composite: weighted average of the 4 dimension scores. Default equal weights (0.25 each). Check `.vibe-prompt/grade/weights.json` for user overrides; apply if present.
   - Write all per-prompt dimension scores + composite to `audit.json`'s `auditGrade.perPrompt` map.
   - Compute `auditGrade.appComposite` as the average of all per-prompt composites.
7. **Check for agent-suggested weight overrides.** Heuristics per `references/scoring-dimensions.md` Agent-suggested weight overrides section:
   - If 4+ prompts in the inventory have F2 (voice contradiction) findings → suggest weighting persona-consistency at 2× the base weight.
   - If 4+ prompts have schema-related findings (F1b or F4) → suggest weighting schema-tightness at 2×.
   - If average prompt token count across the inventory exceeds 4000 tokens → suggest weighting token-efficiency at 2×.
   - Present each triggered suggestion to the user via AskUserQuestion (one question, listing all triggered suggestions). If accepted, write the confirmed weights to `.vibe-prompt/grade/weights.json` and recompute all per-prompt composites and appComposite with the new weights before writing audit.json.
8. **Write audit.json.** Atomic write to `.vibe-prompt/state/audit.json`. Validate against schema before write.
9. **Render report.** Apply `references/audit-report-template.md` to write `docs/vibe-prompt/audit-{YYYY-MM-DD}.md` in the target app. Date is today's date in the target's local time zone — but use UTC YYYY-MM-DD for the filename to keep ordering stable.
10. **Render banner.** ≤ 25 lines. Includes finding count by severity, the highest-severity finding's one-liner, the report path, the next recommended step.
11. **Post-flight.** `session-logger` terminal entry.

## Banner template

```
═══ Vibe-Prompt audit ═══
Findings:   7 total
  High:     4 (F1, F2, F4, F6)
  Medium:   2 (F3, F7)
  Low:      1 (F5)

Headline:   Registry exists but 10 inline sites bypass it (F1, high)
Report:     docs/vibe-prompt/audit-2026-05-28.md
State:      .vibe-prompt/state/audit.json

Suggested first move: F6 verify-model (cheapest, highest signal).
```

## Friction triggers

See `friction-triggers.md`. Highlights:
- `f6-suspect-model-detected` — high confidence
- `f2-contradiction-cross-file-attempted` (when v0.1 1-hop trace surfaced what looks like a deeper conflict but couldn't resolve it) — medium
- `rubric-default-recommendation-felt-generic` (heuristic — the agent's own read of whether the recommendation it just emitted is specific enough)

## Never

- Run any prompt.
- Re-scan from within audit. Audit reads cached inventory; scan owns inventory.
- Modify source.
