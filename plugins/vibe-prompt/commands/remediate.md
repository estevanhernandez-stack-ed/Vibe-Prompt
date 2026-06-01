---
description: Close the audit → fix loop. Reads cached audit + inventory + composer.json; generates per-finding diffs via category-mapped templates; routes by confidence (≥0.90 auto-write with backup, 0.70-0.89 stage, <0.70 inline-only). Supports backup + rollback, F12 handoff, per-finding review. Flags — `--apply-pending <id>`, `--reject-pending <id>`, `--rollback <ISO-timestamp>`, `--interactive`, `--auto-apply`, `--skip-f12`, `--apply-contradictions`, `--apply-voice-frame-fixes` (v0.6+), `--auto-handoff-vibe-sec` (v0.6+), `--apply-inline-to-registry` (v0.7+), `--apply-typed-renderer` (v0.7+), `--apply-model-consolidation` (v0.7+).
---

Invoke the `vibe-prompt:remediate` skill.

v0.6 adds two opt-in flags:

- `--apply-voice-frame-fixes` — enables auto-write routing for Category B
  `voice-frame-rewrite` sub-category diffs (default: always stage; flag opts into
  normal confidence-based routing). Independent of `--apply-contradictions`.
- `--auto-handoff-vibe-sec` — when F12 critical fires, automatically invoke
  `/vibe-sec:audit` via the Skill tool (scope: `user-input-boundary`). Default is
  the v0.5 banner-only handoff. Falls back to banner if vibe-sec is not installed.

v0.7 adds three opt-in Category D flags. Category D covers mechanical migration
templates (F1 inline-to-registry, F4 typed-renderer, F6 model-consolidation).
**Default behavior:** Category D diffs stage regardless of confidence — even at
≥0.90 — because the diffs touch architecture surfaces (registry shape, helper
signatures, shared config). Each opt-in flag flips its Category D sub-category
to normal confidence routing.

- `--apply-inline-to-registry` — enables auto-write for Category D-1 (F1 inline
  systemInstruction → registry migration). With flag, normal routing applies
  (auto-write at ≥0.90, stage at 0.70-0.89). Default: stage regardless of
  confidence.
- `--apply-typed-renderer` — enables auto-write for Category D-2 (F4 typed
  renderer addition with `requiredVars` + `renderPrompt` helper). With flag,
  normal routing applies. Default: stage regardless of confidence.
- `--apply-model-consolidation` — enables auto-write for Category D-3 (F6
  hardcoded-model-id consolidation into `src/config/ai.ts`'s `DEFAULT_MODEL`).
  D-3's confidence floor is 0.88, so the auto-write threshold under this flag is
  ≥0.88 (lower than the standard 0.90 because D-3 is mechanical with voice-risk
  1.0). Default: stage regardless of confidence.

The three Category D flags are independent — passing one does NOT enable the
others.
