# Fixture synthesis — eval

How vibe-prompt generates plausible test inputs per prompt at eval time.

## Inputs per prompt

From `.vibe-prompt/state/inventory.json`:
- `templatedVars`: list of variable names the prompt expects
- Prompt content (from registry source or inline literal): used to infer var shape and constraints

## Synthesis flow

1. **Check for user-provided fixture.** If `.vibe-prompt/eval/fixtures/<prompt-id>.json` exists, use it as-is. Skip synthesis. Mark `fixture.origin = "user-provided"`.

2. **Otherwise synthesize.** Dispatch a subagent (haiku model) with this prompt:

```
You are generating a test input for an LLM prompt. The prompt expects these variables filled in:

<list of templatedVars>

The prompt's text is:

<prompt content>

Produce a single test input as JSON, mapping each variable to a plausible value. The values should be realistic for the prompt's domain, not edge cases. Return ONLY the JSON object, no commentary.
```

3. **Validate the synthesized fixture.** Confirm:
   - JSON parses
   - Every `templatedVars` entry has a value
   - No value is empty/whitespace

   If validation fails, retry once with a clarifying instruction. On second failure, friction-log `fixture-synthesis-low-confidence` low and use placeholder values like `"<test value>"`.

4. **Record origin.** `fixture.origin = "synthesized"`.

## Concrete example: Celestia3 natal_interpretation

`templatedVars` from inventory: `["name", "chartData"]`

Synthesized fixture:

```json
{
  "name": "Maya Okafor",
  "chartData": "Sun in Sagittarius 18°, Moon in Pisces 4°, Ascendant in Virgo 27°. Mercury conjunct Venus in 4th house Sagittarius. Mars opposite Saturn (Aries/Libra). North Node in Cancer at 12°."
}
```

The chart data is plausible-looking but synthetic. The dashboard's fixture-realism summary should surface this so the user knows.

## Realism warning in dashboard

In the eval-result summary, count fixtures by origin:

```
Fixtures used:
  Synthesized: 12
  User-provided: 2
```

Surface this in the dashboard with a one-line warning when synthesized > 50%:

> *Most fixtures in this eval were synthesized by the agent. Synthesized inputs may not exercise the prompt the way real users would. For higher-fidelity drift detection, supply fixtures in `.vibe-prompt/eval/fixtures/<prompt-id>.json` and re-run.*

## Never

- Synthesize a fixture if a user-provided one exists (override pattern).
- Re-synthesize the same fixture mid-eval (deterministic per-eval).
- Embed PII in synthesized fixtures (avoid real-sounding emails, phone numbers, addresses).
