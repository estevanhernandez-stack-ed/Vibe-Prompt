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
1a. **Workspace detection (v0.7+).** Per `references/workspace-detection.md`. Classify the target into one of four `workspaceKind` values: `single-workspace` (one `package.json`, no `workspaces` field), `npm-workspaces` (top-level `package.json` declares `workspaces`; expand globs like `packages/*` / `apps/*` against the filesystem), `nested-projects` (≥2 nested `package.json` files outside `node_modules/` without a top-level `workspaces` declaration — friction-log `workspace-detection-confidence-low` for user confirmation), or `unknown` (no `package.json` at all — pure-Python target or empty repo). Read `config.scan.workspaceDetection` (`auto` | `force-single` | `force-monorepo`) to allow overriding inference. Record `workspaceKind` for later emission; if npm-workspaces or nested-projects, record `workspaces[]` entries (`{name, path, packageJsonPath, inventoryFile}`).
1b. **Scan excludes (v0.7+).** Read `config.scan.excludes` — a string array of **glob** patterns. Merge with built-in defaults (`vibe-*/`, `*-main/`, `_ARCHIVE_*/`, `node_modules/`, `.git/`, `dist/`, `build/`) per `references/workspace-detection.md` §"Exclude defaults". The merged result is the **effective** exclude set written to `inventory.scanExcludes[]` later. Apply excludes during the file walk — every directory matching any glob is **skipped**; matched files do NOT appear in `inlinePrompts[]` or contribute to `registry.entries`. **Auto-detect candidates:** if any top-level directory matches `vibe-*/`, `*-main/`, or `_ARCHIVE_*/` AND it is NOT in `config.scan.excludes`, friction-log `scan-excludes-recommended-but-not-applied` (low) so the next scan can adopt the suggestion. The friction record names the exact candidate paths; user can copy them into `config.scan.excludes` once.
2. **Stack + provider detection.** Per `references/detection-heuristics.md` §1-2. Record `targetApp.stack` and `targetApp.aiProviders`.
3. **Registry detection.** Per `references/detection-heuristics.md` §3. If found, extract every entry: id, name, category, version, outputShape (inferred from content — look for JSON schemas, "return only JSON", "respond in markdown"), templatedVars (regex `\{\{(\w+)\}\}` on content), voiceBearing (true if content includes "You are" / "Act as" / persona declaration), personaLabel (per `references/persona-extraction.md`).
3a. **Registry-kind classification (v0.7+).** Per `references/registry-kind-classification.md`. If a registry was detected in step 3, classify it into one of four `registry.kind` values: `prompt-content` (string-valued PROMPTS-style registries — F1 fires when bypassed), `model-routing` (model-id-valued MODELS-style registries — F1 does NOT fire on inline systemInstruction because the table doesn't carry prompts; F6 model-consolidation reads it for canonical model-id source), `task-mapping` (object-descriptor TASKS-style registries — task IO schemas, not prompt content), or `hybrid` (mixed value shapes — strings AND objects, or strings carrying both prompt text and model IDs; treated like prompt-content for F1 purposes; safe fallback when signals are ambiguous). Apply Signal 1 (value type), Signal 2 (key + filename naming), Signal 3 (inline content heuristic) per the reference. Write the result to `inventory.registry.kind`. The audit step F1 will gate on this field.
4. **Inline prompt detection.** Per `references/detection-heuristics.md` §4. For each hit, capture the same fields as registry entries plus `hasFallback` (look at the enclosing try/catch — if there's a fallback value returned in the catch block, true) and `estimatedTokens` (rough: characters / 4).
4a. **Templated var extraction.** Per `references/inline-prompt-detection.md`. v0.5 captures four patterns: handlebars (v0.4 baseline), template-literal `${var}` interpolations, string-concat `'...' + var + '...'` chains, and JSX-attr `prompt={\`...${var}...\`}` interpolations. Handlebars-only prompts emit `templatedVars` as a string array (v0.4 shape). Prompts using template-literal, concat, or jsx-attr patterns emit object form: `{name, source, declaredAt}` plus `origin` + `originConfidence` when var-origin detection classifies them.
4b. **Var origin classification.** Per `references/var-origin-detection.md`. For each captured var (object form), apply Signal 1 (naming heuristic — user-keyword vs system-keyword regex) then Signal 2 (call-graph proximity — service-call assignment vs form-input assignment). Write the result to `templatedVars[].origin` (`user-controlled` | `system-injected` | `unknown`) plus `originConfidence` (0-1). Conservative fallback: when unable to determine, classify as `unknown` so downstream F10 still fires by default; user can override via `audit.varOriginOverrides` config.
5. **Persona collection.** Dedupe per `references/persona-extraction.md`. Write to `personas` top-level array.
6. **Model identifier collection.** Grep for known model name patterns across all detected provider call sites: `gemini-[\d.]+-(flash|pro|ultra)`, `claude-[\d.]+-(opus|sonnet|haiku)(-\d+)?`, `gpt-[\d.]+(-turbo)?`, `o[\d]+(-mini)?`. Record every occurrence with file + line. Group by `value`.
7. **Write inventory.** Atomic write to `.vibe-prompt/state/inventory.json`. Validate against `plugins/vibe-prompt/schemas/inventory.schema.json` before write. **Branches on `workspaceKind`:**
   - **`single-workspace` or `unknown`** — emit ONE flat `inventory.json` (v0.6 back-compat shape; no `workspaces[]` array, no per-workspace files). v0.6 readers unchanged.
   - **`npm-workspaces` or `nested-projects`** — emit one per-workspace file at `.vibe-prompt/state/inventory-<workspace-name>.json` (one per detected workspace) PLUS the top-level `.vibe-prompt/state/inventory.json` as **aggregator**. Each per-workspace file's `inlinePrompts[]` / `registry.entries` / `personas[]` / `modelIdentifiers[]` are scoped to that workspace (per-workspace prompts only). The top-level aggregator carries the full union — every prompt entry in the aggregator's `inlinePrompts[]` gets an extra `workspaceIdentifier` field naming which workspace owns it; the aggregator's `workspaces[]` cross-references each per-workspace file via `workspaces[].inventoryFile`. Atomic write order: per-workspace files first, then aggregator last (so partial-failure leaves the previous aggregator intact).
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
