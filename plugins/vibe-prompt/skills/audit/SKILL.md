---
name: vibe-prompt:audit
description: This skill should be used when the user says "/vibe-prompt:audit", "audit my prompts", "what's wrong with my prompts", "find prompt smells", "structural prompt review", or wants a structural audit of LLM prompts in their app. Reads `.vibe-prompt/state/inventory.json` (required prerequisite — created by `/vibe-prompt:scan`), applies the F1-F7 rubric, writes `.vibe-prompt/state/audit.json` and a human-readable `docs/vibe-prompt/audit-YYYY-MM-DD.md`. Read-only — no source mutation.
---

# /vibe-prompt:audit

Load `vibe-prompt:guide` first. Then load `references/smell-rubric-f1-f7.md` and `references/audit-report-template.md`.

Apply the F1-F7 rubric to the cached inventory. Emit machine-readable findings + human-readable dated report.

## Inputs

- `.vibe-prompt/state/inventory.json` in the target app — REQUIRED.
- No flags in v0.1.

## Workflow

1. **Pre-flight.** Invoke `session-logger` start. Read `.vibe-prompt/state/inventory.json`. If missing, instruct the user to run `/vibe-prompt:scan` first and exit. Validate inventory against `plugins/vibe-prompt/schemas/inventory.schema.json` — if invalid, friction-log `inventory-schema-violation` and abort.
2. **Apply rubric.** Walk `references/smell-rubric-f1-f7.md` in order F1 → F1b → F2 → F3 → F4 → F5 → F6 → F7. For each smell, run the detection rule against `inventory.json`. If it fires, build a finding object: `{ id, smell, severity, evidence[], recommendation }`. Use the recommendation template, filling in concrete values from inventory (file paths, IDs, counts).
3. **F2 semantic pass.** Voice-contradiction detection cannot run from inventory alone — it needs prompt content. Re-read each voice-bearing prompt's content from the target source. Compare global directive (if present in registry as a `*directive` / `*persona` entry) against each task prompt. Surface contradictions with specific file:line citations on BOTH the rule and the violation.
4. **F6 known-model lookup.** Compare each `modelIdentifiers[*].value` against the bundled known-models list (in `references/smell-rubric-f1-f7.md` §F6). If unrecognized, the suspect-model variant of F6 fires with elevated severity language and a "verify what's actually served" recommendation.
5. **Compose summary.** Count findings by severity → `summary.byCategory`. Total → `summary.totalFindings`.
6. **Write audit.json.** Atomic write to `.vibe-prompt/state/audit.json`. Validate against schema before write.
7. **Render report.** Apply `references/audit-report-template.md` to write `docs/vibe-prompt/audit-{YYYY-MM-DD}.md` in the target app. Date is today's date in the target's local time zone — but use UTC YYYY-MM-DD for the filename to keep ordering stable.
8. **Render banner.** ≤ 25 lines. Includes finding count by severity, the highest-severity finding's one-liner, the report path, the next recommended step.
9. **Post-flight.** `session-logger` terminal entry.

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
