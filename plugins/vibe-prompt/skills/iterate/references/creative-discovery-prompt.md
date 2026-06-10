# Creative discovery prompt — iterate

Dispatched via the Agent tool at **tier: `creative-divergent`** — brainstorm/ideation where breadth
beats rigor, so it routes to the cheap/fast tier (the session maps tier→model; no model ID pinned here).
Temperature=0.9 (divergent).

## Template

```
You are helping a developer extend their app with new AI-powered features. They've inventoried
their existing prompts and want suggestions for what's missing.

## Their app

{{domain.summary}}

## Existing prompts

{{ for each prompt in inventory }}
- {{prompt.id}} — {{prompt.name or prompt.purpose summary}}
{{ end for }}

## Current audit findings (gaps)

{{ for each finding in audit.findings where severity == "high" }}
- {{finding.smell}}: {{finding.recommendation}}
{{ end for }}

## Your task

Generate 3-5 new prompts the app COULD add that would surface new value. Each should:
- Fit the app's domain (don't suggest stuff outside scope)
- Complement existing prompts (don't duplicate)
- Address gaps the audit findings hint at (where appropriate)
- Be specific and buildable (not vague concepts)

Return ONLY a JSON array of suggestions. Each:

{
  "name": "snake_case_prompt_id",
  "purpose": "1-sentence statement of what this prompt does",
  "targetPersona": "Which existing persona, or 'extend existing voice' or 'new persona: X'",
  "exampleOutputShape": "Brief JSON or prose shape example",
  "whyValuable": "2-3 sentences explaining why this adds value given the app's domain",
  "handoffHint": "Suggested next step: /vibe-cartographer:scope OR /vibe-iterate:feature-add OR direct prompt drafting"
}

Avoid suggestions that:
- Add new vendors / SDKs the app doesn't already use
- Require infrastructure the app likely doesn't have (DB tables, etc.)
- Duplicate existing prompts under a different name
- Are obviously out of domain
```

## Invocation parameters

| Parameter | Value | Reason |
|---|---|---|
| tier | creative-divergent | Brainstorm/ideation — breadth beats rigor; the session maps tier→model (cheap/fast), no model ID pinned |
| temperature | 0.9 | Divergent — we want creative suggestions, not the most obvious answer |
| max_tokens | 2048 | Enough for 5 well-formed suggestions; shouldn't need more |

## Validation after dispatch

After the Agent call returns, validate the JSON output against `iterate-suggestions.schema.json`.

If invalid (schema mismatch, malformed JSON, wrong array shape):
- Retry once with this appended instruction: "Return ONLY a valid JSON array. No preamble.
  No postamble. No markdown fences around the JSON."
- If still invalid after one retry: surface the raw output to the user with:
  "The discovery model returned an invalid format. Review the raw output below — if it's
  close, I can help you shape it into the suggestions schema manually."

## Cost note

One Agent call at the creative-divergent (cheap/fast) tier ≈ $0.01-0.03 total (input + output tokens combined at that tier's pricing).
This is the full per-run cost for `:iterate`. No vendor API key required — uses the in-session
model budget.
