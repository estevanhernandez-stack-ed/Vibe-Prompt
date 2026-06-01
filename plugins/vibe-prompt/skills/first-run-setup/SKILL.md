---
name: vibe-prompt:first-run-setup
description: Internal SKILL invoked on first invocation of `:eval` or `:radar` in a target app. Captures the composer pattern + agent self-ID + initial config. Writes `.vibe-prompt/eval/composer.json` + `.vibe-prompt/eval/agent.json` + `.vibe-prompt/eval/config.json`. Idempotent — re-runnable to refresh stale captures.
---

# First-run setup (internal)

Load `vibe-prompt:guide`. Then walk the user through three captures.

## Inputs

- Target app: CWD (or path arg)
- `.vibe-prompt/state/inventory.json` (required input — used to identify vendors)

## Workflow

1. **Pre-flight.** `session-logger` start. Verify inventory exists — if not, friction-log `inventory-not-found` and exit with: *"Run /vibe-prompt:scan first, or point at a manual inventory file."*

2. **Composer capture** — autonomous-first via `references/composer-detection.md` (v0.5), interactive fallback via `references/composer-interview.md`. Output: `.vibe-prompt/eval/composer.json`.
   - Stage 1: Detect composer file candidates by filename (`gemini.ts`, `openai.ts`, `anthropic.ts`, `llm.ts`, `ai.ts`, `chat.ts`) + SDK import (`@google/genai`, `@anthropic-ai/sdk`, `openai`). Multi-candidate output supported; user picks primary.
   - **Stage 1b (v0.7+): Composer-kind classification.** Before per-composer layer tracing, classify the app's composer topology into one of four kinds per `references/composer-kinds.md`:
     - `single-composer` — exactly one composer file holds all SDK call sites (Celestia3 shape; v0.6 back-compat default)
     - `multi-composer` — two or more distinct composer files, each with its own composition (626Labs `galaxyCore.ts` + `ChatController.ts`)
     - `multi-call-site` — zero canonical composer files; SDK calls scattered inline across N source files (WeSeeYou shape; group by SDK + persona per composer-kinds.md grouping heuristic)
     - `shared-package` — composer file lives under `packages/<name>/` and is referenced from 2+ workspaces (Quiz Show `packages/ai/src/gemini/GeminiService.ts`)
     Emit top-level `compositionShape: "single"` for single-composer; `"multi"` for the other three kinds. The classification determines whether `composers[]` is length 1 (single-composer back-compat shim, top-level `layers[]` also written) or length N (one entry per detected composer / persona-cluster).
   - Stage 2: Trace composition layers per composer (walk `+=` accumulation, template-literal segments, or array-join patterns). For each composer in `composers[]`, layer tracing + apiParameter detection + classification all run independently — Stage 2 / 2b / 3 iterate per composer.
   - Stage 2b (v0.6+): For each traced layer, detect the destination **`apiParameter`** (one of `systemInstruction` | `contents` | `messages` | `instructions` | `prompt` | `null`) per the apiParameter heuristics catalog in `references/composer-detection.md`. Write `apiParameter` + `apiParameterConfidence` on each layer. Used downstream by F12 API-parameter-aware detection.
   - Stage 3: Classify each layer (`global-directive`, `format-directive`, `knowledge-context`, `task-instruction`, `user-data`). Map to composer.schema.json type enum. Persona / master-directive layers (matched in Stage 3 by content + field-name heuristic) emit `type: "global-directive"` directly (v0.6+); the legacy `directive-field` enum value remains valid for backward compat but is no longer emitted by fresh detections.
   - Stage 4: Emit `composer.json` with `globalConfidence` (weighted average of per-layer confidence; weighted to include apiParameter confidence signal) and `regenerationSource` (`auto-detected` | `hybrid` | `manual`). When any layer's `apiParameter: null`, friction-log `f12-api-parameter-detection-low-confidence`.
     - v0.7+: emission writes `composers[]` array with one entry per classified composer. For `kind: "single-composer"`, ALSO write top-level `layers[]` as a back-compat shim (same array surfaced both places). For `kind: "multi-composer"` / `"multi-call-site"` / `"shared-package"`, omit top-level `layers[]` (no single source of truth). `apiParameterCompleteness` per composer reports the fraction of its layers with a non-null detected `apiParameter`.
   - Stage 5: When fewer than 2 layers resolve OR `globalConfidence < 0.40`, surface a warning banner + friction-log `composer-auto-generation-confidence-low`; ≥4 layers + globalConfidence ≥0.7 emits a clean banner with no friction.
   - Re-runnable via `:first-run-setup --regenerate-composer`.

3. **Agent self-ID** per `references/agent-self-id.md`. Output: `.vibe-prompt/eval/agent.json`.

4. **Config bootstrap.** Generate a default `.vibe-prompt/eval/config.json`:

   ```json
   {
     "version": "0.1",
     "vendors": {
       "gemini": {
         "defaultModel": "<from inventory.modelIdentifiers[0].value or ask user>",
         "fallbackModel": null
       }
     },
     "costCeiling": 2.00
   }
   ```

   Show the user the default + ask: *"Cost ceiling defaults to $2.00 per eval. Override?"*

5. **Sanity check.** Verify the user has at least one working Gemini auth method:
   - **Preferred:** `gcloud auth print-access-token` returns a non-empty value (means `gcloud auth login` has been run). No env var needed.
   - **Fallback:** `VIBE_PROMPT_GEMINI_API_KEY` is set (plugin-namespaced — NOT the generic `GEMINI_API_KEY`, to avoid Firebase deploy collisions).
   - If neither: warn the user and suggest running `gcloud auth login` before `:eval`. Do NOT abort — setup itself doesn't require auth; only `:eval` does.

6. **Post-flight.** `session-logger` terminal entry.

## Banner template

```
═══ Vibe-Prompt first-run setup ═══
Inventory:      14 prompts found at .vibe-prompt/state/inventory.json
Composer:       captured (6 layers, kind=stacked)
                source: src/lib/gemini.ts
Agent:          Claude Code (claude-opus-4-7), detected via marker-file
Config:         .vibe-prompt/eval/config.json written
                vendors: gemini (default: gemini-3.5-flash)
                ceiling: $2.00

Auth check:     gcloud auth: ✓ (token available)
                VIBE_PROMPT_GEMINI_API_KEY: not set (OAuth path preferred — OK)

Ready: /vibe-prompt:eval
```

## Never

- Read API keys from any file.
- Run vendor calls during setup.
- Auto-confirm composer or agent identity — always require user confirmation.
