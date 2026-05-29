# LLM-judge prompt — eval

The semantic comparator. Dispatches an in-session subagent to read both outputs and name differences. Every finding ships with the evaluator-drift footer.

## Dispatch

Subagent type: `general-purpose`. Model: `haiku` (this is judge work; tighter cost). Prompt template below.

## Prompt template

```
You are {{agent.name}} ({{agent.model}}). You are reading two LLM outputs and identifying differences. You may be biased toward outputs that match your own training style — name this risk explicitly in any finding where it matters.

## Inputs

The same prompt was sent to two models:

- Output A: from {{prod.model}} (the production model)
- Output B: from {{baseline.model}} (the baseline — that's you, in this case)

### Output A ({{prod.model}}):
```
{{outputProd}}
```

### Output B ({{baseline.model}}):
```
{{outputBaseline}}
```

## Your task

Identify semantic differences along these dimensions:

1. **Persona drift** — does one output address the user differently? (e.g., "Pilgrim" vs "you")
2. **Voice tone** — formality, mysticism, warmth, conciseness
3. **Topic adherence** — does one drift from the task?
4. **Output structure** — headers, lists, paragraph density
5. **Length appropriateness** — does one violate explicit length constraints in the original prompt?

Return ONLY a JSON array of findings, each shaped:

```json
{
  "category": "persona-drift | voice-tone | topic-adherence | output-structure | length",
  "severity": "high | medium | low",
  "text": "1-2 sentence description naming what diverged and citing specific text"
}
```

Empty array if no notable differences.

## Important

- Be specific. Quote phrases from the outputs to ground each finding.
- Do NOT score which output is "better". Drift, not preference.
- Where the divergence might just be "Output A doesn't sound like me", say so honestly — that's evaluator drift, not real product drift.
```

## Post-processing: append evaluator-drift footer

After receiving the judge's findings, for EACH finding, append a footer:

For cross-vendor cases (agent.vendor !== prod.vendor):

> *Note: This finding came from {{agent.name}} ({{agent.model}}) reading both outputs. The evaluator is a different vendor than your production model and may be biased toward outputs that match its own training style. Verify high-severity flags with a sample user, an A/B test, or by reading the outputs yourself before acting.*

For intra-vendor cases (agent.vendor === prod.vendor):

> *Note: This finding came from {{agent.name}} ({{agent.model}}), which is the same vendor as your production model. The drift signal reflects intra-vendor version differences rather than cross-vendor bias. Interpret accordingly.*

For unknown agent cases:

> *Note: This finding came from an evaluator we couldn't identify. Interpret with full skepticism and verify against a sample user before acting.*

## Skip conditions

The LLM-judge layer is skipped if:

- User passed `--no-judge`
- `outputBaseline` is null (one of the models failed — judge would have nothing to compare)
- `outputProd` is null (same reason)

When skipped, set `comparator.llmJudge.skipped = true` and the `findings` array stays empty.
