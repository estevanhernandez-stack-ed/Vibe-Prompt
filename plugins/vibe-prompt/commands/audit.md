---
description: Audit your prompts for the F1-F14 smells, including F14 model-migration API breakage and retired or retiring model ids. Reads cached inventory, writes findings + a dated markdown report. Read-only.
---

**Load the full instructions first:** read `${CLAUDE_PLUGIN_ROOT}/skills/audit/SKILL.md` in full and follow it. This file is only the entry point; the skill is the complete instruction set, and this command shadows it, so it will not load on its own.

Invoke the `vibe-prompt:audit` skill.
