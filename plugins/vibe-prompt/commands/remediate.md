---
description: Close the audit → fix loop. Reads cached audit + inventory + composer.json; generates per-finding diffs via category-mapped templates; routes by confidence (≥0.90 auto-write with backup, 0.70-0.89 stage, <0.70 inline-only). Supports backup + rollback, F12 handoff, per-finding review. Flags — `--apply-pending <id>`, `--reject-pending <id>`, `--rollback <ISO-timestamp>`, `--interactive`, `--auto-apply`, `--skip-f12`, `--apply-contradictions`, `--apply-voice-frame-fixes` (v0.6+), `--auto-handoff-vibe-sec` (v0.6+).
---

Invoke the `vibe-prompt:remediate` skill.

v0.6 adds two opt-in flags:

- `--apply-voice-frame-fixes` — enables auto-write routing for Category B
  `voice-frame-rewrite` sub-category diffs (default: always stage; flag opts into
  normal confidence-based routing). Independent of `--apply-contradictions`.
- `--auto-handoff-vibe-sec` — when F12 critical fires, automatically invoke
  `/vibe-sec:audit` via the Skill tool (scope: `user-input-boundary`). Default is
  the v0.5 banner-only handoff. Falls back to banner if vibe-sec is not installed.
