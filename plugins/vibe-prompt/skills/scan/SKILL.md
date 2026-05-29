---
name: vibe-prompt:scan
description: This skill should be used when the user says "/vibe-prompt:scan", "scan my prompts", "inventory my LLM prompts", "find all my prompt sites", or wants a full prompt inventory across an app. Reads source files autonomously, detects registry + inline prompt sites, extracts personas, identifies hardcoded model identifiers, and writes `.vibe-prompt/state/inventory.json` in the target app. Read-only. Defers structural analysis to `/vibe-prompt:audit`.
---

# /vibe-prompt:scan

Load `vibe-prompt:guide` first.

Inventory every LLM prompt site in the target app. Writes one machine-readable state file + a short banner.

## Inputs

- Target app: the current working directory (or path argument if provided).
- No flags in v0.1. Always full scan.

## Workflow

1. **Pre-flight.** Invoke `session-logger` (sentinel start entry). Verify there's a recognized stack (`package.json` or `pyproject.toml`). If none, friction-log `no-recognized-stack` and abort with a clean message.
2. **Stack + provider detection.** Per `references/detection-heuristics.md` §1-2. Record `targetApp.stack` and `targetApp.aiProviders`.
3. **Registry detection.** Per `references/detection-heuristics.md` §3. If found, extract every entry: id, name, category, version, outputShape (inferred from content — look for JSON schemas, "return only JSON", "respond in markdown"), templatedVars (regex `\{\{(\w+)\}\}` on content), voiceBearing (true if content includes "You are" / "Act as" / persona declaration), personaLabel (per `references/persona-extraction.md`).
4. **Inline prompt detection.** Per `references/detection-heuristics.md` §4. For each hit, capture the same fields as registry entries plus `hasFallback` (look at the enclosing try/catch — if there's a fallback value returned in the catch block, true) and `estimatedTokens` (rough: characters / 4).
4a. **Templated var extraction.** Per `references/inline-prompt-detection.md`. v0.5 captures four patterns: handlebars (v0.4 baseline), template-literal `${var}` interpolations, string-concat `'...' + var + '...'` chains, and JSX-attr `prompt={\`...${var}...\`}` interpolations. Handlebars-only prompts emit `templatedVars` as a string array (v0.4 shape). Prompts using template-literal, concat, or jsx-attr patterns emit object form: `{name, source, declaredAt}` plus `origin` + `originConfidence` when var-origin detection classifies them.
4b. **Var origin classification.** Per `references/var-origin-detection.md`. For each captured var (object form), apply Signal 1 (naming heuristic — user-keyword vs system-keyword regex) then Signal 2 (call-graph proximity — service-call assignment vs form-input assignment). Write the result to `templatedVars[].origin` (`user-controlled` | `system-injected` | `unknown`) plus `originConfidence` (0-1). Conservative fallback: when unable to determine, classify as `unknown` so downstream F10 still fires by default; user can override via `audit.varOriginOverrides` config.
5. **Persona collection.** Dedupe per `references/persona-extraction.md`. Write to `personas` top-level array.
6. **Model identifier collection.** Grep for known model name patterns across all detected provider call sites: `gemini-[\d.]+-(flash|pro|ultra)`, `claude-[\d.]+-(opus|sonnet|haiku)(-\d+)?`, `gpt-[\d.]+(-turbo)?`, `o[\d]+(-mini)?`. Record every occurrence with file + line. Group by `value`.
7. **Write inventory.** Atomic write to `.vibe-prompt/state/inventory.json`. Validate against `plugins/vibe-prompt/schemas/inventory.schema.json` before write.
8. **Render banner.** ≤ 25 lines. Includes: stack, providers, registry detected?, registered count, inline count, persona count, model identifiers count, confidence summary. End with the suggestion: *"Run `/vibe-prompt:audit` to surface structural smells."*
9. **Post-flight.** `session-logger` terminal entry.

## Banner template

```
═══ Vibe-Prompt scan ═══
Stack:      typescript + python
Providers:  gemini, anthropic

Registry:   detected (src/lib/ConfigService.ts, default-export-record)
            6 entries
Inline:     10 sites
Personas:   8 distinct labels
Models:     1 identifier in use ("gemini-3.5-flash") across 4 sites

Confidence: 14/16 sites high-confidence, 2 medium
Written:    .vibe-prompt/state/inventory.json (45 KB)

Next: /vibe-prompt:audit
```

## Friction triggers

See `friction-triggers.md`. Highlights:
- `registry-detected-but-empty-entries` — confidence: high
- `model-identifier-unrecognized` (matches no known published model name) — confidence: high
- `inline-prompt-without-fallback` (only logged once per scan, as aggregate)
- `low-confidence-detections-over-40pct` — confidence: medium

## Never

- Run any prompt.
- Modify any source file.
- Re-write `inventory.json` after a partial scan (must be atomic — write to tempfile, rename).
