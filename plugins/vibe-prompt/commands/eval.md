---
description: Behaviorally test the prompts inventoried by /vibe-prompt:scan. Runs each prompt against the production model + an in-session Claude baseline; surfaces drift mechanically + via LLM-judge with explicit cross-vendor evaluator-drift warnings. Cost-gated.
---

**Load the full instructions first:** read `${CLAUDE_PLUGIN_ROOT}/skills/eval/SKILL.md` in full and follow it. This file is only the entry point; the skill is the complete instruction set, and this command shadows it, so it will not load on its own.

Invoke the `vibe-prompt:eval` skill.
