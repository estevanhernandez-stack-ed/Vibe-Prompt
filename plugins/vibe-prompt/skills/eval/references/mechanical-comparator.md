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

### check.value-type-drift (severity: medium)

Fires when two outputs share the same top-level key set (schema-shape passed) but the value type at a specific key differs between prod and baseline, especially when one of the types diverges from the type declared in `OUTPUT_SCHEMA`.

**Prerequisites:** both outputs parse as JSON (or can be coerced per schema-shape logic). Schema-shape check already passed. The prompt's `OUTPUT_SCHEMA` is available for declared-type lookup.

**Type enum:** classify each value at key K as one of: `string`, `number`, `boolean`, `array<string>`, `array<object>`, `array<other>`, `object`, `null`.

**Detection rule:**

```
for each key K in OUTPUT_SCHEMA.declaredKeys:
  prodType = classifyType(outputProd[K])
  baselineType = classifyType(outputBaseline[K])
  declaredType = OUTPUT_SCHEMA.type(K)

  if prodType !== baselineType:
    if declaredType matches prodType:
      fire value-type-drift { driftedSide: "baseline" }
    elif declaredType matches baselineType:
      fire value-type-drift { driftedSide: "prod" }
    else:
      fire value-type-drift-both (both wrong; schema is the ground truth)
```

**Special case — `array<string>` vs `array<object>` always fires:** even if the outer array type matches the declared type, if one output emits an array of strings and the other emits an array of objects (or vice versa), the structural shape inside the array differs and `value-type-drift` fires regardless. The inner element shape is load-bearing for downstream consumers.

**Union-schema escape hatch:** if `OUTPUT_SCHEMA` declares a union type for key K (e.g., `oneOf: [string, array<object>]`), both values satisfy the declared contract. Do NOT fire `value-type-drift` for union-typed keys. Fire only when the schema has a single declared type and one or both outputs deviate from it.

**Evidence shape:**

```json
{
  "check": "value-type-drift",
  "severity": "medium",
  "fired": true,
  "category": "value-type-drift",
  "evidence": {
    "keyPath": "bigThree",
    "declaredType": "string",
    "prodType": "array<object>",
    "baselineType": "string",
    "driftedSide": "prod",
    "snippet": "[{\"sun\": \"Aries\"}, {\"moon\": \"Cancer\"} ...]  (first 200 chars)"
  },
  "detail": "prod emitted array<object>; baseline and OUTPUT_SCHEMA declare string"
}
```

For `value-type-drift-both`:
```json
{
  "check": "value-type-drift-both",
  "severity": "medium",
  "fired": true,
  "category": "value-type-drift-both",
  "evidence": {
    "keyPath": "themes",
    "declaredType": "array<string>",
    "prodType": "object",
    "baselineType": "array<object>",
    "driftedSide": "both",
    "snippet": "..."
  },
  "detail": "both outputs deviate from OUTPUT_SCHEMA declared type; schema is ground truth"
}
```

**`snippet` rule:** first 200 characters of the drifted value. Truncate with `...` if longer. Never echo API keys or auth tokens — if the snippet value looks like a key (regex `[A-Za-z0-9_\\-]{32,}`), redact to `[REDACTED]`.

**Recommendation template (for report rendering):**
> Key `{keyPath}` declared as `{declaredType}` in OUTPUT_SCHEMA but `{vendor}` emitted `{actualType}`. The mechanical schema-shape check passed because the key was present; the drift was inside the value shape. Two fixes (pick one): (1) tighten OUTPUT_SCHEMA to specify the exact value structure, OR (2) add a post-processing validator that coerces or rejects values matching the wrong type.

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
