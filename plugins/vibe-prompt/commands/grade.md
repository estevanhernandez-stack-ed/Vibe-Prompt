---
description: Synthesize audit + latest eval into per-prompt + app composite grades. Tracks regression vs monotonic baseline. Writes .vibe-prompt/grade/state/grade-<runId>.json and docs/vibe-prompt/grade-YYYY-MM-DD.md.
---

**Load the full instructions first:** read `${CLAUDE_PLUGIN_ROOT}/skills/grade/SKILL.md` in full and follow it. This file is only the entry point; the skill is the complete instruction set, and this command shadows it, so it will not load on its own.

Invoke the `vibe-prompt:grade` skill.
