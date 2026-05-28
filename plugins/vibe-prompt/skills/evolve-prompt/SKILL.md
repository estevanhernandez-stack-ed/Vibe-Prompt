---
name: vibe-prompt:evolve-prompt
description: This skill should be used when the user says "/vibe-prompt:evolve-prompt" and wants Vibe-Prompt to reflect on past sessions and propose improvements to itself. Reads ~/.claude/plugins/data/vibe-prompt/ session + friction logs, weights findings, writes proposed SKILL/rubric/heuristic edits to docs/proposed-changes.md in the Vibe-Prompt solo repo. Never auto-applies. L3 self-evolution.
---

# /vibe-prompt:evolve-prompt

Reflect on the last N days of Vibe-Prompt usage and propose changes to the plugin itself.

## Inputs

- `~/.claude/plugins/data/vibe-prompt/sessions.jsonl`
- `~/.claude/plugins/data/vibe-prompt/friction.jsonl`
- `~/.claude/plugins/data/vibe-prompt/wins.jsonl` (if exists in v0.2+)
- Default window: last 30 days. CLI arg `--days N` overrides.

## Workflow

1. **Pre-flight.** session-logger start. If `sessions.jsonl` has zero entries in the window, friction-log `no-sessions-in-30-days` and exit.
2. **Weight friction.** Group by trigger code. Score: `count × confidenceWeight` where confidenceWeight = {high: 3, medium: 2, low: 1}.
3. **Surface patterns.** Top 5 triggers by score. For each, identify which SKILL/reference document needs revision.
4. **Propose changes.** Write `docs/proposed-changes.md` in the Vibe-Prompt solo repo (NOT the target app — this proposes changes to the plugin itself). One section per pattern:
   - **Pattern:** trigger code + count + score
   - **Affected:** which SKILL or reference file
   - **Proposed change:** concrete prose diff (existing text → proposed text)
   - **Confidence:** the agent's self-confidence in the proposal
5. **Banner.** ≤ 20 lines. Top 3 patterns. Path to `proposed-changes.md`.
6. **Post-flight.** session-logger terminal.

## Rules

- **Never auto-apply.** Output is always a diff proposal for human review.
- If a pattern's score is below 5 (i.e., low signal), include in proposed-changes but flag as low-confidence.
- Respect the absence-of-friction-inference rule: if a SKILL fires zero friction in 30 days of regular use, that's a positive signal worth noting (don't propose changes to working SKILLs).
