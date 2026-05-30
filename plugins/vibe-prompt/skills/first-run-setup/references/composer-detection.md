# Composer detection — file discovery + layer tracing + classification

> v0.5 reference. Closes the v0.4 gap that left composer.json absent in most target apps, degrading F12 from critical to high and blocking `:remediate` Category A fixes.

This file declares how `:first-run-setup` automatically discovers composer files, traces composition layers within them, classifies each layer, and emits `composer.json` with per-layer and global confidence. The detection is autonomous-first: run heuristics, emit the file, surface confidence in the banner. The user can confirm or correct before `:audit` consumes it.

## Workflow stages

1. **File detection** — heuristic catalog of filenames + SDK imports.
2. **Layer tracing** — walk concatenation / template-literal segments in the composer function.
3. **Layer classification** — assign each segment a layer type (global-directive | format-directive | knowledge-context | task-instruction | user-data).
4. **Emission** — write `composer.json` with `globalConfidence` and per-layer `confidence`.
5. **Banner** — surface confidence; if below threshold, prompt user to verify.

## Stage 1 — Composer file detection

### Heuristic A — Filename match

Walk the target app source tree (excluding `node_modules/`, `.venv/`, `dist/`, etc., per scan exclusions). Candidate files match these names (case-insensitive on the basename):

| Filename | Vendor signal |
|---|---|
| `gemini.ts` / `gemini.js` | Gemini |
| `openai.ts` / `openai.js` | OpenAI |
| `anthropic.ts` / `anthropic.js` | Anthropic |
| `llm.ts` / `llm.js` | Vendor-agnostic |
| `ai.ts` / `ai.js` | Vendor-agnostic |
| `chat.ts` / `chat.js` | Vendor-agnostic |

Each filename match becomes a candidate with `reason: "filename match: <filename>"`.

### Heuristic B — SDK import match

For every TS/JS file in the source tree, check for imports of known LLM SDKs:

| Import path | Vendor signal |
|---|---|
| `@google/genai` | Gemini |
| `@google/generative-ai` | Gemini (legacy) |
| `@anthropic-ai/sdk` | Anthropic |
| `openai` | OpenAI |

Each file with a matching import becomes a candidate with `reason: "imports <sdk>"`.

### Multi-candidate output

A repo may have multiple composer files (e.g., separate `gemini.ts` for chat + `gemini-embeddings.ts` for vectors). Each candidate is recorded; the user picks one as primary during setup confirmation. Layer-tracing runs on the chosen primary; secondary composers are listed in `composer.json` metadata for future passes.

When the same file matches both heuristics (e.g., `gemini.ts` AND imports `@google/genai`), merge candidates and concatenate reasons: `reason: "filename match: gemini.ts; imports @google/genai"`. Increases candidate confidence weight in Stage 4.

### Candidate output shape

```json
{
  "candidates": [
    {
      "file": "src/lib/gemini.ts",
      "reason": "filename match: gemini.ts; imports @google/genai",
      "vendor": "gemini",
      "matchCount": 2
    },
    {
      "file": "src/lib/llm.ts",
      "reason": "filename match: llm.ts",
      "vendor": null,
      "matchCount": 1
    }
  ]
}
```

If zero candidates: emit `globalConfidence: 0.0`, write a stub `composer.json` with `kind: "identity"`, prompt the user to point at the composer manually.

## Stage 2 — Layer tracing

For the chosen primary composer file:

1. Find the function that calls the LLM SDK. Heuristic call sites:
   - `await <model>.generateContent({...})` (Gemini)
   - `await <client>.messages.create({...})` (Anthropic)
   - `await <client>.chat.completions.create({...})` (OpenAI)

2. Walk backwards from the call site to find the construction of the system instruction. Common patterns:

   ```ts
   // Pattern A: += accumulation
   let systemInstruction = '';
   systemInstruction += `[PERSONA]\n${directive.persona}\n\n`;
   systemInstruction += `[MASTER DIRECTIVE]\n${directive.masterDirective}\n\n`;
   ```

   ```ts
   // Pattern B: template literal with multi-line interpolations
   const systemInstruction = `
   ${directive.persona}

   [MASTER DIRECTIVE]
   ${directive.masterDirective}

   [DEFAULT FORMAT]
   ${directive.defaultFormat}
   `;
   ```

   ```ts
   // Pattern C: array of strings joined
   const parts = [
     directive.persona,
     `[MASTER DIRECTIVE]\n${directive.masterDirective}`,
     ...
   ];
   const systemInstruction = parts.join('\n\n');
   ```

3. Each `+=` segment, each `${...}` interpolation in Pattern B's template literal, and each array entry in Pattern C becomes a **layer candidate**.

4. Per layer candidate, capture:
   - `text` — the literal string content (for static segments)
   - `field` — the field name being interpolated (`directive.persona`, `KnowledgeService.get(...)`)
   - `sourceLine` — line in the composer file where the segment appears
   - `condition` — null for unconditional layers; `If <expr>` when wrapped in `if (...)` blocks

## Stage 2b — apiParameter detection (v0.6+)

For every traced layer candidate, identify **which API parameter** the layer's text is destined for in the SDK call. This drives F12 API-parameter-aware detection: when user-var layers are at `apiParameter: "contents"` and system-instruction layers are at `apiParameter: "systemInstruction"`, the API enforces structural separation regardless of layer order, so F12 does NOT need to fire.

Heuristics catalog:

| Call-site pattern | `apiParameter` | Confidence |
|---|---|---|
| Layer concatenated into `systemInstruction:` arg of `generateContent({...})` (Gemini) or accumulated into a `systemInstruction` variable passed there | `systemInstruction` | 0.95 |
| Layer concatenated into a `system:` arg of `messages.create({...})` (Anthropic) | `systemInstruction` | 0.90 |
| Layer interpolated into `contents[].parts[].text` (Gemini) — i.e. the user-turn `parts` array | `contents` | 0.85 |
| Layer interpolated into `messages[].content` (OpenAI / Anthropic chat completions) | `messages` | 0.85 |
| Layer interpolated into the single `prompt:` string passed to OpenAI **completions** (legacy text-completion endpoint) | `prompt` | 0.85 |
| Layer interpolated into an `instructions:` arg (vendor-specific instructions parameter) | `instructions` | 0.80 |
| Call pattern unknown / could not be traced to a named API parameter | `null` (unknown) | 0.0 |

### How to apply

1. From Stage 2's traced call site, identify which **named argument** of the SDK function receives the layer's text. Walk the assignment chain backwards if necessary (e.g., layer appends to a local variable `systemPart`, which is then passed as `systemInstruction: systemPart`).
2. Match the named argument against the table above.
3. Write `apiParameter` + `apiParameterConfidence` on the layer record.
4. If no match (e.g., the layer feeds a custom wrapper, the destination is computed dynamically, or the SDK pattern wasn't recognized), emit `apiParameter: null` and `apiParameterConfidence: 0.0`. F12 detection treats `null` as "unknown" and degrades to v0.5 layer-order behavior for that layer.

### Worked examples

Gemini systemInstruction layer (confidence 0.95):
```ts
let systemInstruction = `[PERSONA]\n${directive.persona}\n\n`;
systemInstruction += `[MASTER DIRECTIVE]\n${directive.masterDirective}\n\n`;
await technomancerModel.generateContent({
  systemInstruction,
  contents: [{ role: 'user', parts: [{ text: dreamText }] }],
});
```
The `[PERSONA]` + `[MASTER DIRECTIVE]` layers → `apiParameter: "systemInstruction"`. The `dreamText` user-data layer → `apiParameter: "contents"` (interpolated into `contents[].parts[].text`).

OpenAI messages layer (confidence 0.85):
```ts
const messages = [
  { role: 'system', content: persona },
  { role: 'user', content: userInput },
];
await client.chat.completions.create({ messages, model });
```
The `persona` layer (system role) → `apiParameter: "messages"` with confidence 0.85 (the role discriminator further distinguishes it as the system message inside `messages[]`). The `userInput` layer (user role) → `apiParameter: "messages"`. F12 will note both layers share `apiParameter: "messages"` and fall through to v0.5 layer-order analysis — appropriate, since messages-array order DOES matter.

OpenAI completions prompt (legacy):
```ts
const promptStr = `${systemPart}\n\n${userInput}`;
await client.completions.create({ prompt: promptStr, model });
```
Both `systemPart` and `userInput` → `apiParameter: "prompt"`. F12 falls through to layer-order analysis — the legacy completions endpoint has no structural separation.

### Confidence calibration

| Match quality | Confidence |
|---|---|
| Named-arg match + direct variable trace (no intermediate computation) | 0.95 |
| Named-arg match + traced through one local variable | 0.85-0.90 |
| Named-arg match + traced through 2+ variables OR helper function | 0.65-0.80 |
| Unknown call pattern OR computed property destination | 0.0 (null) |

### Friction trigger

When any layer in a composer.json emits `apiParameter: null`, friction-log `f12-api-parameter-detection-low-confidence` (medium) at composer.json emission time. This surfaces to `/evolve-prompt` so detection patterns can be tuned via friction-driven SKILL edits.

---

## Stage 3 — Layer classification

Apply heuristics to each layer candidate to assign `type`:

| Signal | Layer type |
|---|---|
| Field name contains `persona`, `directive`, `brand`, or content matches `(?i)You are` | `global-directive` |
| Field name contains `format`, `style`, `output`, `schema`, or content matches `(?i)respond in|format as|output:` | `format-directive` |
| Field is a `knowledge`/`lore`/`context` service call (e.g., `KnowledgeService.get`, `LoreCache.read`) with system-injected origin | `knowledge-context` |
| Field is a function parameter named `systemInstruction`, `taskPrompt`, `instructionContent`, `prompt` | `task-instruction` |
| Field interpolates a var classified as `user-controlled` per var-origin-detection.md | `user-data` |

Confidence per layer (`layers[].confidence`):

| Match quality | Confidence |
|---|---|
| Exact field-name match + content signal | 0.95 |
| Field-name match only | 0.80 |
| Content signal only (no field name match) | 0.65 |
| Heuristic guess (last-resort fallback) | 0.40 |

Maintain layer order from source-file appearance (top-to-bottom in the composer function).

## Stage 4 — Emission

Write `.vibe-prompt/eval/composer.json`. Schema (see `composer.schema.json`):

```json
{
  "version": "0.1",
  "kind": "stacked",
  "sourceFile": "src/lib/gemini.ts",
  "globalConfidence": 0.78,
  "regenerationSource": "auto-detected",
  "layers": [
    {
      "id": "directive-persona",
      "type": "global-directive",
      "text": "<verbatim persona text>",
      "order": 1,
      "confidence": 0.95,
      "apiParameter": "systemInstruction",
      "apiParameterConfidence": 0.95
    },
    {
      "id": "directive-master",
      "type": "directive-field",
      "text": "<verbatim master directive>",
      "order": 2,
      "confidence": 0.95
    },
    {
      "id": "format-default",
      "type": "directive-field",
      "text": "<format text>",
      "order": 3,
      "confidence": 0.85
    },
    {
      "id": "knowledge",
      "type": "knowledge-injection",
      "text": "<knowledge text or token placeholder>",
      "order": 4,
      "confidence": 0.75
    },
    {
      "id": "task",
      "type": "task-instruction",
      "text": "",
      "order": 5,
      "confidence": 0.90
    }
  ]
}
```

`globalConfidence` is the weighted average of per-layer confidences. v0.6+ extends the weighted average to incorporate `apiParameterConfidence` as a co-equal signal alongside `confidence` (per-layer formula: `(confidence + apiParameterConfidence) / 2`). When ≥4 layers classify cleanly with apiParameter resolved, target is ≥0.7. Layers with `apiParameter: null` drag globalConfidence down (their contribution is `(confidence + 0) / 2`).

`regenerationSource`:
- `auto-detected` — all layers found via heuristics, no user edits.
- `hybrid` — user corrected at least one layer; remainder auto-detected.
- `manual` — user wrote `composer.json` directly; no auto-detection.

## Stage 5 — Confidence floor + user prompt

When fewer than 2 layers resolve OR `globalConfidence < 0.40`:

- Emit `composer.json` with `globalConfidence: 0.40` (or actual value, whichever is lower).
- Surface a warning banner: *"Composer detection produced low-confidence layer map (N layers, globalConfidence X). Run `/vibe-prompt:first-run-setup --regenerate-composer` after editing the composer to retry, or hand-edit `.vibe-prompt/eval/composer.json` directly."*
- Friction-log `composer-auto-generation-confidence-low` per spec §Friction-triggers.

When ≥4 layers resolve cleanly with `globalConfidence ≥ 0.7`:

- Emit `composer.json` with the computed confidence.
- Banner: *"Composer captured: 5 layers, globalConfidence 0.78. Run `/vibe-prompt:audit` to consume."*
- No friction trigger.

## Layer-type → composer.schema.json type mapping

The spec uses semantic layer names (`global-directive`, `format-directive`, etc.). The v0.6 composer.schema.json `layers[].type` enum is `literal | directive-field | global-directive | knowledge-injection | task-instruction | conditional`. Map as follows when writing the composer.json:

| Spec semantic layer | composer.schema.json `type` (v0.6+) | v0.5 legacy emission |
|---|---|---|
| `global-directive` | `global-directive` | `directive-field` |
| `format-directive` | `directive-field` | `directive-field` |
| `knowledge-context` | `knowledge-injection` | `knowledge-injection` |
| `task-instruction` | `task-instruction` | `task-instruction` |
| `user-data` | `literal` (treated as user-interpolated literal for downstream consumers) | `literal` |

**Migration note:** `directive-field` is **deprecated for persona / master-directive layers in v0.6+** — fresh detections emit `global-directive` directly so F12 detection and remediate logic don't need to guess intent from the layer `id`. The schema enum still accepts `directive-field` for backward compat (legacy v0.5 composer.json files continue to validate without re-generation), but `:first-run-setup --regenerate-composer` will rewrite them to `global-directive` on next run.

The semantic label is preserved in the layer `id` (e.g., `id: "directive-persona"`, `id: "format-default"`) so consumers can recover the semantic grouping when needed.

## Concrete walkthrough — Celestia3 gemini.ts

Composer file: `src/lib/gemini.ts` (matches `filename: gemini.ts` + `imports @google/genai` → matchCount: 2).

Layers traced from the `technomancerModel.generateContent` function:

| Order | id | Semantic | composer type | Source | Confidence |
|---|---|---|---|---|---|
| 1 | `directive-persona` | global-directive | directive-field | `directive.persona` (ConfigService.ts:33) | 0.95 |
| 2 | `directive-master` | global-directive | directive-field | `directive.masterDirective` (ConfigService.ts:34) | 0.95 |
| 3 | `format-default` / `format-json` | format-directive | conditional → directive-field | conditional on `systemInstruction` content | 0.85 |
| 4 | `knowledge-smart` / `knowledge-primer` | knowledge-context | knowledge-injection | conditional on `isKnowledgeSyncEnabled` | 0.75 |
| 5 | `task-instruction` | task-instruction | task-instruction | call's `systemInstructionContent` arg | 0.90 |
| 6 | `chaos-protocol` | global-directive | conditional | conditional on `allowEntropy === true` | 0.70 |

globalConfidence: weighted average → ~0.86.

## What NOT to do

- Don't auto-confirm without showing the user the rendered composed prompt — even when confidence is high, prompt for confirmation (this is a load-bearing artifact).
- Don't write `composer.json` with `kind: "stacked"` and `layers: []` — if zero layers traced, fall back to `kind: "identity"`.
- Don't classify a layer as `knowledge-context` when the var's origin is unknown — only when var-origin-detection.md confirms `system-injected` for the interpolated field.
- Don't bump confidence above 0.95 for any single layer; reserve >0.95 for manually confirmed layers (`regenerationSource: "manual"` or `"hybrid"`).

## Re-generation

Users can re-run via `:first-run-setup --regenerate-composer`. Behavior:
- Reads existing `composer.json` if present.
- Re-runs Stages 1-4.
- If existing layers match new detection: preserves user-edited fields (`text` overrides, `condition` corrections), regenerates `confidence`.
- If layers diverge: prompts user to confirm replacement.
- `regenerationSource` is set to `hybrid` when partial user-edited content is preserved.

## Cross-references

- Schema: `plugins/vibe-prompt/schemas/composer.schema.json` — layer type enum + confidence fields.
- Sibling reference: `composer-interview.md` — interactive interview workflow (used when auto-detection confidence is low).
- Audit consumer: F12 detection reads `composer.json` to identify layer order; full critical severity requires `globalConfidence ≥ 0.7`.
- Remediate consumer: Category A diffs target the composer file identified in `sourceFile`; placement uses layer boundaries.
