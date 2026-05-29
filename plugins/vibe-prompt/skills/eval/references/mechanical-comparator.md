# Mechanical comparator — eval

Deterministic, free, fast checks. Catch gross drift before the LLM-judge layer.

## Inputs

Two output strings: `outputProd` and `outputBaseline`. Both may be empty/null if errors occurred.

## Checks

Run all checks against both outputs; record each finding's severity and whether it fired.

### check.hard-fail (severity: high)

```
fires if (outputProd is null/empty) XOR (outputBaseline is null/empty)
```

If one model errored and the other produced output, that's drift (model-error drift).

### check.both-failed (severity: high)

```
fires if outputProd is null/empty AND outputBaseline is null/empty
```

If both errored, that's a prompt-side problem, not a drift. Still surface high.

### check.schema-shape (severity: high)

If either output STARTS with `{` or `[` (after trimming whitespace), try parsing both as JSON.

```
fires if (outputProd parses as JSON) XOR (outputBaseline parses as JSON)
```

If both parse, compare top-level key sets:

```
fires if topLevelKeys(outputProd) !== topLevelKeys(outputBaseline)
```

### check.required-keys (severity: high)

If the prompt content includes a JSON schema declaration (regex: matches an `OUTPUT_SCHEMA` block or a `Return ONLY a JSON object with these keys:` pattern), parse the schema's required keys.

```
fires per output if any required key is missing from the parsed JSON output
```

### check.length-delta (severity: medium)

```
delta = abs(outputProd.length - outputBaseline.length) / max(outputProd.length, outputBaseline.length)
fires if delta > 0.5
```

### check.token-delta (severity: medium)

Same logic on estimated token counts:

```
fires if abs(prodTokens - baselineTokens) / max(prodTokens, baselineTokens) > 1.0
```

### check.empty (severity: high)

```
fires per output if output trims to empty
```

## Output shape

For each check, record into `prompts[*].comparator.mechanical[]`:

```json
{
  "check": "schema-shape",
  "severity": "high",
  "fired": true,
  "detail": "prod output parses as JSON; baseline output is prose"
}
```

`detail` is short, factual, names what diverged.

## Rules

- Run ALL checks unconditionally; don't short-circuit. The full mechanical layer goes into the eval-result.
- Never compare content semantically here — that's the LLM-judge's job.
- Cheap to compute (no API calls); ALL checks together should run in < 100ms per prompt.
