---
name: vibe-prompt:evolve-prompt
description: This skill should be used when the user says "/vibe-prompt:evolve-prompt" and wants Vibe-Prompt to reflect on past sessions and propose improvements to itself. L3 self-evolution loop. Reads ~/.claude/plugins/data/vibe-prompt/ session + friction logs covering scan + audit + eval + radar + grade + iterate invocations. Weights findings, writes proposed SKILL/rubric/heuristic edits to docs/proposed-changes.md in the Vibe-Prompt solo repo. Never auto-applies.
---

# /vibe-prompt:evolve-prompt

Reflect on the last N days of Vibe-Prompt usage and propose changes to the plugin itself.

## Inputs

- `~/.claude/plugins/data/vibe-prompt/sessions.jsonl`
- `~/.claude/plugins/data/vibe-prompt/friction.jsonl`
- `~/.claude/plugins/data/vibe-prompt/wins.jsonl` (if exists)
- Default window: last 30 days. CLI arg `--days N` overrides.

All six step-commands contribute to these logs: scan, audit, eval, radar, grade, and iterate. Eval-side friction (cost-ceiling hits, evaluator-drift dismissals, fixture-synthesis misses) and radar-side friction (stale cache, unreachable sources) are first-class inputs to the loop — evolution is consolidated here, not split into a separate command per step.

Grade-side friction triggers (weight overrides, regression handling, Swap-and-Discard tie rates) map to the `vibe-prompt:grade` SKILL and `references/scoring-dimensions.md` or `references/composite-formula.md` for proposed changes. Iterate-side friction triggers (off-domain suggestions, implemented suggestions) map to the `vibe-prompt:iterate` SKILL and `references/domain-detection.md` or `references/creative-discovery-prompt.md`.

**v0.4 trigger handler templates** — four new triggers added in v0.4 and their canonical change targets:

| Trigger code | Confidence | Handler: what to propose |
|---|---|---|
| `injection-attack-succeeded` | high | Map to `audit/SKILL.md` F10-F12 detection + `eval/references/inject-attack-fixtures.md`. Propose: (a) tighter defense-phrase matching in F11, OR (b) new fixture pattern added to the fixture library if the attack vector is novel, OR (c) weight increase for injectionResistance dimension in `audit/references/scoring-dimensions.md`. |
| `f9-fired-but-prompt-already-has-date-grounding` | low | Map to `audit/SKILL.md` step 4b (F9 detection, step B). Propose: extend step B's composition-stack temporal anchor heuristic to recognize the path the detection missed (e.g., a non-standard marker phrase or an indirect injection pattern). Low confidence — confirm with the user which path was missed before drafting the diff. |
| `value-type-drift-fired-but-types-are-compatible` | low | Map to `eval/references/mechanical-comparator.md` value-type-drift section. Propose: add a union-type escape hatch that reads OUTPUT_SCHEMA's union declarations before firing the check. Low confidence — require the user to provide the specific OUTPUT_SCHEMA that defines the union so the proposed detection rule is concrete. |
| `injection-resistance-dimension-flat-across-prompts` | medium | Map to `audit/references/scoring-dimensions.md` injectionResistance dimension definition. Propose: review score-impact calibration for F10-F12 (are the deductions large enough to differentiate?) OR flag that the app may genuinely have uniform composition (all prompts have zero user-input vars — expected flat score, not a calibration gap). Surface both hypotheses; let the user pick. |

**v0.5 trigger handler templates** — four new triggers added in v0.5 (`:remediate` + composer auto-gen) and their canonical change targets:

| Trigger code | Confidence | Handler: what to propose |
|---|---|---|
| `staged-fix-applied-and-eval-confirms-improvement` | high | Positive signal. Map to `remediate/references/fix-categories.md` + `remediate/references/confidence-rubric.md`. Propose: (a) raise default confidence for the affected category if multiple positive signals in window, OR (b) lift this template into a docs example so future runs anchor on the proven pattern. Do not propose changes to working rubric weights — absence-of-friction inference applies. |
| `staged-fix-rejected` | medium | Map to `remediate/references/confidence-rubric.md` + the affected category's diff template in `remediate/references/fix-categories.md`. Propose: (a) lower default confidence for the affected category, OR (b) tighten the diff template (e.g., Category B's find-and-rephrase rule needs better context), OR (c) add an app-specific override hook so the rubric reads from `.vibe-prompt/config/remediate-thresholds.json` for category-level tuning. Cluster rejections by category before proposing — a B-heavy rejection pattern needs different treatment than a C-heavy one. |
| `auto-write-rolled-back` | high | Map to `remediate/SKILL.md` routing section + `remediate/references/confidence-rubric.md`. Propose: (a) raise the `autoApplyThreshold` default (e.g., 0.90 → 0.93) if rollbacks cluster near the threshold, OR (b) move the affected category to always-stage by default (mirror the Category B treatment), OR (c) tune the locate-confidence weight in the rubric if rollbacks correlate with wrong-file edits. Surface the rollback-correlated rubric dimension with the proposal. |
| `composer-auto-generation-confidence-low` | medium | Map to `first-run-setup/references/composer-detection.md`. Propose: (a) add the app's actual composer pattern to the heuristic catalog (filename, SDK import, or layer regex), OR (b) lower the global confidence floor + surface a manual-verification prompt by default for new app types. Require the user to confirm which detection path missed before drafting the change. |

## Workflow

1. **Pre-flight.** session-logger start. If `sessions.jsonl` has zero entries in the window, friction-log `no-sessions-in-30-days` and exit.
2. **Weight friction.** Group by trigger code across all six commands (scan, audit, eval, radar, grade, iterate). Score: `count × confidenceWeight` where confidenceWeight = {high: 3, medium: 2, low: 1}.
3. **Surface patterns.** Top 5 triggers by score. For each, identify which SKILL/reference document needs revision. Note the source command (scan-side, audit-side, eval-side, radar-side, grade-side, iterate-side) to aid targeting.
4. **Propose changes.** Write `docs/proposed-changes.md` in the Vibe-Prompt solo repo (NOT the target app — this proposes changes to the plugin itself). One section per pattern:
   - **Pattern:** trigger code + count + score + source command
   - **Affected:** which SKILL or reference file
   - **Proposed change:** concrete prose diff (existing text → proposed text)
   - **Confidence:** the agent's self-confidence in the proposal
5. **Banner.** ≤ 20 lines. Top 3 patterns. Path to `proposed-changes.md`.
6. **Post-flight.** session-logger terminal.

## Rules

- **Never auto-apply.** Output is always a diff proposal for human review.
- If a pattern's score is below 5 (i.e., low signal), include in proposed-changes but flag as low-confidence.
- Respect the absence-of-friction-inference rule: if a SKILL fires zero friction in 30 days of regular use, that's a positive signal worth noting (don't propose changes to working SKILLs).
