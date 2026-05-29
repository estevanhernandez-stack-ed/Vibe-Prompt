---
description: Close the audit → fix loop. Reads cached audit + inventory + composer.json; generates per-finding diffs via category-mapped templates; routes by confidence (≥0.90 auto-write with backup, 0.70-0.89 stage, <0.70 inline-only). Supports backup + rollback, F12 handoff, per-finding review. Flags — `--apply-pending <id>`, `--reject-pending <id>`, `--rollback <ISO-timestamp>`, `--interactive`, `--auto-apply`, `--skip-f12`, `--apply-contradictions`.
---

Invoke the `vibe-prompt:remediate` skill.
