# Composer mimic — eval

How vibe-prompt applies the captured composer at eval time to produce the actual composed prompt the model receives.

## Inputs

- `.vibe-prompt/eval/composer.json` (validated against composer schema)
- For each prompt being tested: its `systemInstruction` text + fixture vars

## Workflow

1. **If `composer.kind === "identity"`:** the composed prompt IS the prompt content (registry entry text with vars filled, OR inline literal). Return as-is.

2. **If `composer.kind === "stacked"`:** apply layers in `order` field ascending:

   For each layer:
   - **`literal`** type: append the layer's `text` to the running composed prompt
   - **`directive-field`** type: append the cached `text` (this was captured verbatim at first-run; the live directive value is not re-fetched)
   - **`knowledge-injection`** type: append the cached `text`
   - **`task-instruction`** type: append the call's actual `systemInstruction` argument (per-call, not from cache)
   - **`conditional`** type: evaluate the `condition` field against the call's inputs (e.g., "if systemInstruction or contents contains 'json'") and append the corresponding text branch

3. **Output:** one single composed system prompt string. This is what gets sent to the model's `systemInstruction` field (or equivalent).

## Concrete example: Celestia3 natal_interpretation

Inputs:
- Prompt content from inventory: the `natal_interpretation` text with `{{name}}` and `{{chartData}}` replaced
- Fixture: `{name: "Maya Okafor", chartData: <synthesized sample chart text>}`
- Cached composer with 6 layers

After composition, the model receives:

```
<directive-persona text from cache>

[MASTER DIRECTIVE]
<directive-master text from cache>

[FORMAT DIRECTIVE]
Structure your response as a valid JSON object. Maintain your Hermetic persona within the text values.

<knowledge-smart text from cache, ~4000 tokens of focused planetary lore>

[TASK SPECIFIC INSTRUCTIONS]
<the natal_interpretation prompt text with vars filled>
```

That's what gets sent to gemini-3.5-flash. NOT the raw `natal_interpretation` content.

## Trade-offs

- Captured layer text can go stale if the app's source changes after the composer was captured. Suggest re-running `/vibe-prompt:first-run-setup` if confidence drops.
- Conditional branches evaluated mechanically may diverge from the app's runtime logic if the condition is complex (e.g., depends on user state). v0.1: capture the dominant branch and friction-log the simplification.

## Validation

After producing the composed prompt, log:
- Composed prompt length (chars + estimated tokens)
- Which layers fired
- Any conditional decisions made

This goes into the eval-result's `prompts[*]` entry for transparency.
