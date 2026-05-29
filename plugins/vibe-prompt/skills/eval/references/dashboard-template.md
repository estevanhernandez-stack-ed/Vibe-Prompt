# Dashboard template — eval

The human-readable report rendered from `eval-result.json` to `docs/vibe-prompt/eval-<timestamp>.md`.

## Structure

````markdown
# Vibe-Prompt drift report — {{targetApp.name}}

**Run ID:** {{runId}}
**Started:** {{startedAt}}
**Completed:** {{completedAt}}
**Mode:** {{mode}} ({if upgrade-test: candidate {{candidateModel}}})
**Evaluator:** {{agentIdentity.name}} ({{agentIdentity.model}})
**Total cost:** ${{summary.totalCostUsd}}{{ if abortedByCostCeiling: " ⚠ ABORTED at cost ceiling"}}

## Verdict

{{ one-sentence headline derived from summary.highSeverityCount }}

For example: "5 of 14 prompts show high-severity drift between {{prod.model}} and {{baseline.model}}. natal_interpretation and synastry_report are the biggest gaps."

## Headline drift findings

| Prompt | Mechanical (high) | LLM-judge (high) | Notes |
|---|---|---|---|
{{ for each prompts[*] where any high-severity finding exists }}
| {{prompts[i].id}} | {{count of mechanical high}} | {{count of llmJudge findings high}} | {{first finding's text, truncated}} |

## Per-prompt detail

{{ for each prompts[*] }}

### {{prompts[i].id}}

**Source:** {{prompts[i].source}}
**Fixture origin:** {{prompts[i].fixture.origin}}

#### Outputs

**{{prompts[i].outputs.prod.model}} ({{prompts[i].outputs.prod.tokens}} tokens, ${{prompts[i].outputs.prod.costUsd}})**

{{ if error: error message; else: outputs.prod.text truncated to ~500 chars with "..." }}

**{{prompts[i].outputs.baseline.model}} (baseline; tokens, no API cost)**

{{ same shape }}

#### Mechanical findings

{{ for each comparator.mechanical[*] where fired = true }}
- **{{check}}** ({{severity}}): {{detail}}

{{ if all mechanical not fired: "No mechanical drift detected." }}

#### LLM-judge findings

{{ if comparator.llmJudge.skipped: "LLM-judge skipped (--no-judge or output failure)." }}
{{ else for each llmJudge.findings[*] }}
- **{{category}}** ({{severity}}): {{text}}
  > {{the evaluator-drift footer for this eval}}

{{ end for }}

---

## Summary

- Total prompts run: {{summary.totalPrompts}}
- High-severity findings: {{summary.highSeverityCount}}
- Total cost: ${{summary.totalCostUsd}}
- Fixtures: {{count where synthesized}} synthesized, {{count where user-provided}} user-provided

{{ if synthesized > 50%: }}
> *Most fixtures were synthesized. For higher-fidelity drift detection, supply fixtures in `.vibe-prompt/eval/fixtures/<prompt-id>.json` and re-run.*

## Recommended next moves

{{ derived from highest-severity findings; sample: }}
1. **{{first high finding prompt}}**: review the {{check or category}} divergence; consider updating the prompt or accepting the drift as expected.
2. **Persona drift across N prompts**: if a recurring pattern (e.g., the baseline addresses user as "you" but prod uses "Pilgrim"), the global directive may be losing to the per-prompt persona. See vibe-prompt audit for F2 root cause.
3. **Schema drift on N JSON-out prompts**: the prod model may be drifting from declared schemas; verify by spot-checking real production outputs.

## Per-prompt eval scores

| Prompt | Prod Schema | Prod Persona | Prod Clarity | Prod Tokens | Baseline Schema | Baseline Persona | Baseline Clarity | Baseline Tokens | Composite (Prod) | Composite (Baseline) |
|---|---|---|---|---|---|---|---|---|---|---|
{{ for each prompts[*] }}
| {{prompts[i].id}} | {ind(evalGrade.dimensions.prod.schemaTightness)} {{evalGrade.dimensions.prod.schemaTightness}} | {ind(evalGrade.dimensions.prod.personaConsistency)} {{evalGrade.dimensions.prod.personaConsistency}} | {ind(evalGrade.dimensions.prod.instructionClarity)} {{evalGrade.dimensions.prod.instructionClarity}} | {ind(evalGrade.dimensions.prod.tokenEfficiency)} {{evalGrade.dimensions.prod.tokenEfficiency}} | {ind(evalGrade.dimensions.baseline.schemaTightness)} {{evalGrade.dimensions.baseline.schemaTightness}} | {ind(evalGrade.dimensions.baseline.personaConsistency)} {{evalGrade.dimensions.baseline.personaConsistency}} | {ind(evalGrade.dimensions.baseline.instructionClarity)} {{evalGrade.dimensions.baseline.instructionClarity}} | {ind(evalGrade.dimensions.baseline.tokenEfficiency)} {{evalGrade.dimensions.baseline.tokenEfficiency}} | {ind(evalGrade.composite.prod)} {{evalGrade.composite.prod}} | {ind(evalGrade.composite.baseline)} {{evalGrade.composite.baseline}} |
{{ end for }}

Score indicators: ✓ = 9–10 (healthy), · = 5–8 (watch), ⚠ = 1–4 (needs attention). `{ind(n)}` resolves to the appropriate indicator at render time.

## Swap-and-Discard summary

- **Pairs evaluated:** {{summary.swapAndDiscard.totalPairs}}
- **Tied (discarded):** {{summary.swapAndDiscard.tiedCount}} ({{summary.swapAndDiscard.tieRatePct}}%)
- **Net findings (accepted):** {{summary.swapAndDiscard.acceptedFindings}}

{{ if summary.swapAndDiscard.tieRatePct > 30 }}
> ⚠ More than 30% of comparison pairs were position-bias ties and discarded. The net finding count may understate real drift. Consider tightening the judge prompt or switching the judge model. Friction-logged as `swap-and-discard-tie-rate-over-30pct` for `/vibe-prompt:evolve-prompt` review.
{{ end if }}

---

## Auditor note

This dashboard was Generated by Vibe-Prompt v{{plugin.version}}. The LLM-judge layer was driven by {{agentIdentity.name}} ({{agentIdentity.model}}). Re-run `/vibe-prompt:eval` after prompt changes to verify drift findings clear (or stay).
````

## Rendering rules

- Cite file paths + prompt IDs explicitly for grep-ability.
- LLM-judge findings always include the footer (mandatory).
- Aborted-by-cost-ceiling evals render the partial report with a warning banner above the verdict.
- Per-prompt detail sections collapse the output text to ~500 chars + ellipsis (full text in the JSON state file).
- If `comparator.mechanical[]` has zero fired AND `llmJudge.findings[]` is empty, render: *"No drift detected on this prompt."*
