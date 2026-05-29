# Inline prompt detection — var detection patterns

> v0.5 reference. Closes the v0.4 gap that missed template-literal vars (Oneirocriton's `dreamText`).
> Companion to `detection-heuristics.md` §4. Where detection-heuristics describes *finding the prompt site*, this file describes *capturing the templated vars inside it* once the site is found.

This file declares the four var-detection patterns the `:scan` SKILL applies to every inline prompt site. Each pattern produces an entry in `inlinePrompts[].templatedVars[]`. Object-form output is required for any non-handlebars pattern; handlebars output stays as a plain string for v0.4 backward compatibility.

## Output shape — backward-compatible

The inventory schema's `templatedVar` is `oneOf: [string, object]`.

| Pattern detected | Output form |
|---|---|
| handlebars-only (v0.4 behavior) | plain string, e.g., `"{{name}}"` |
| template-literal, concat, jsx-attr | object form: `{name, source, declaredAt, ...}` |
| mixed in same prompt | string entries for handlebars, object entries for new patterns |

The object form must include `name`. It should include `source` (enum: handlebars | template-literal | concat | jsx-attr) and `declaredAt` (string of the form `<relative-file>:L<lineNumber>`). It may include `origin` + `originConfidence` once Tasks 10-11 land.

When the v0.5 detection layer emits an object even for a handlebars hit (because the prompt has mixed patterns and we want consistent shape), that's allowed by the schema — but for handlebars-only prompts, prefer the string form so v0.4 round-trip artifacts don't diff for cosmetic reasons.

## Pattern 1 — handlebars (v0.4 baseline, unchanged)

Regex: `\{\{(\w+)\}\}` on prompt content.

Capture: var name only. Source: `handlebars` (implicit when emitted as object).

Emits as plain string in inventory: `"{{name}}"` (v0.4 shape) or `{name, source: "handlebars", declaredAt}` (object shape, only when emitted alongside other patterns in the same prompt).

## Pattern 2 — template-literal interpolation (NEW v0.5)

Regex: `\$\{\s*([A-Za-z_$][\w$]*)\s*\}` inside backtick-delimited template literals.

```ts
// Source
const userPrompt = `Dream: "${dreamText}"`;
// Captured
{name: "dreamText", source: "template-literal", declaredAt: "src/Oneirocriton.tsx:L72"}
```

Apply only inside backtick template literals that are assigned to a const/let/var whose name matches `(?i)(prompt|system|user|content|instruction|message)` OR that flow into an AI-call site within the same scope. This filter avoids false positives on non-prompt template literals.

Multiple `${var}` interpolations in the same literal produce one entry per unique var name (dedupe within a prompt). `declaredAt` records the source-file line where the literal opens (the backtick line), not where the var name appears, so downstream tools can navigate to the prompt source consistently.

Object form is always emitted for this pattern.

## Pattern 3 — string concatenation (NEW v0.5)

Regex: detect a binary `+` chain where at least one operand is a string literal containing prompt-language signals (`You are`, `User said`, `Respond`, etc.) and at least one operand is a bare identifier.

```ts
// Source
const prompt = 'You are X. User said: ' + userMessage + ' Respond as Y.';
// Captured
{name: "userMessage", source: "concat", declaredAt: "src/lib/llm.ts:L45"}
```

Source: `concat`.

Conservative scope: apply only when the resulting variable is used as a prompt argument (`systemInstruction`, `system`, `messages: [{content}]`, etc.) within the same function scope.

Object form is always emitted for this pattern.

## Pattern 4 — JSX attribute interpolation (NEW v0.5)

Regex: detect JSX attributes whose name matches `(?i)(prompt|system|user|instruction|message)` and whose value is a curly-brace expression containing a template literal with `${var}` interpolations.

```tsx
// Source
<DreamComponent
  systemPrompt={`You are ${persona}. Respond carefully.`}
  userPrompt={`Dream: "${dreamText}"`}
/>
// Captured
[
  {name: "persona",   source: "jsx-attr", declaredAt: "src/DreamComponent.tsx:L12"},
  {name: "dreamText", source: "jsx-attr", declaredAt: "src/DreamComponent.tsx:L13"},
]
```

Source: `jsx-attr`.

Apply only inside `.tsx` / `.jsx` files. The detection runs over each prompt-named attribute independently; each attribute contributes its own `declaredAt` line.

Object form is always emitted for this pattern.

## Field details

### `name`
The bare identifier captured inside `${...}`, between `+ … +`, or inside a JSX attribute's template literal. No surrounding whitespace, no dotted-path access (`user.bio` truncates to `user` for v0.5 — full path tracking is a v0.6 candidate).

### `source`
One of:
- `handlebars` — `{{var}}` syntax (v0.4 baseline)
- `template-literal` — `${var}` inside backticks
- `concat` — `'...' + var + '...'` chains
- `jsx-attr` — JSX attribute template literals

Schema enum is locked; do not invent new values without updating `inventory.schema.json`.

### `declaredAt`
Format: `<relative-file-path>:L<lineNumber>`. The line where the prompt site opens (the backtick, the opening string-literal, or the JSX attribute name). Used by `:remediate` to locate edits.

### `origin` + `originConfidence` (Tasks 10-11)
Filled by var-origin-detection.md. This file does not classify; it only captures the syntactic site.

## Detection order

Per inline prompt:
1. Identify the prompt literal range (per `detection-heuristics.md` §4).
2. Walk the range:
   - Match Pattern 1 (handlebars `{{...}}`) on the literal content.
   - If the literal is a template-literal, match Pattern 2 (`${...}`) on the literal content.
   - If the literal is concat-shaped, match Pattern 3 across operands.
3. For surrounding context (JSX containing the prompt site), match Pattern 4.
4. Dedupe by `(name, source)` within the prompt.
5. Emit handlebars as string when it's the only pattern; emit object form otherwise.

## False-positive guards

- Skip `${var}` inside literals that are clearly not prompts (e.g., SQL templates, URL builders) — heuristic: the literal does not contain any of `You are`, `Respond`, `Output`, `Dream`, `Format`, `Task`, `Instructions`, persona markers (see `persona-extraction.md`).
- Skip concat chains shorter than 2 string operands (likely not prompt assembly).
- Skip JSX attrs whose name does not match the prompt-attr regex (no false positives on `className`, `key`, `onClick`).

## Friction triggers

Add to friction-triggers catalog when:
- `template-literal-var-captured-but-no-ai-call-nearby` — medium. May indicate a false positive; let `:audit` review.
- `concat-pattern-without-clear-prompt-shape` — low. Logged once per scan as aggregate.
- `jsx-attr-prompt-detected` — informational. Recorded but not flagged.

## Cross-references

- Schema: `plugins/vibe-prompt/schemas/inventory.schema.json` — `templatedVar` definition.
- Sibling reference: `var-origin-detection.md` (Tasks 10-11) classifies the captured vars as user-controlled vs system-injected.
- Audit consumer: F10/F11/F12 detection reads `templatedVars[].origin` to filter system-injected vars from injection-resistance scoring.
- Remediate consumer: Category C diffs target `origin: "user-controlled"` vars only.
