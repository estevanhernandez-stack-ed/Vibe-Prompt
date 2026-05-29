# Vibe-Prompt

Audit, organize, and classify the LLM prompts shipped in your app.

Vibe-Prompt is the prompt-audit and behavioral-testing layer for vibe-coded apps that ship LLM features. Point it at your repo and it inventories every prompt site (registry-tracked and inline), names the structural smells, recommends a reorg, and can run your prompts against the production model to surface semantic drift. Read-only static pass by default; real vendor calls only on `:eval` with explicit cost confirmation.

## Install

[Stable channel via the vibe-plugins marketplace]
[Canary channel: this repo directly]

## What it does

- `/vibe-prompt:scan` — inventory pass. Finds every prompt site in your app (registry + inline).
- `/vibe-prompt:audit` — structural pass. Flags 12 smell categories (F1–F12) with file:line evidence. Produces per-prompt scores across 5 dimensions (schema tightness, persona consistency, instruction clarity, token efficiency, injection resistance). F9 checks date-grounding; F10-F12 grade prompt-injection vulnerability.
- `/vibe-prompt:eval` — behavioral pass. Runs prompts against the prod model + an in-session Claude baseline. Surfaces semantic drift via mechanical comparator (including value-type-drift check) + LLM-judge with SWRS calibration, Long CoT reasoning, Swap-and-Discard position-bias mitigation, and verbosity penalty. Per-dimension scores on eval output. Cost-gated; always confirms before spending. Accepts `--inject-attacks` flag to run 6 canonical injection patterns against each prompt with a user-input var — judges whether the model honored the attack or held its role. Handoff to `/vibe-sec:audit` recommended when attacks succeed.
- `/vibe-prompt:grade` — synthesis pass. Reads audit + latest eval scores and computes per-prompt + app composite grades via weighted average. Tracks each prompt's best-ever score as the monotonic baseline — improvements advance it, regressions flag without resetting. Surfaces composite trends and flagged regressions in one dashboard.
- `/vibe-prompt:iterate` — discovery pass. Reads your inventory + audit findings + app domain (detected from CLAUDE.md → vibe-tool artifacts → package metadata → brief interview), dispatches one creative-divergent LLM call (~$0.02), and returns 3-5 prompts your app could add — each with a handoff hint to `/vibe-cartographer:scope` or `/vibe-iterate:feature-add`.
- `/vibe-prompt:radar` — model-news pass. Checks for new model releases, deprecations, and pricing changes from your vendors. Zero LLM cost; reads vendor changelogs and docs.
- `/vibe-prompt` (bare) — state-aware router; reads inventory + audit + eval + grade + iterate + radar state and recommends the next move.
- `/vibe-prompt:evolve-prompt` — L3 self-evolution. Reads session + friction logs across all six commands and proposes improvements to the plugin itself. Never auto-applies.

## What's new in v0.4

Three additive capabilities — no breaking changes to v0.3 surface area.

**F9 — Date-grounding static check.** Audit now detects date-handling prompts (by keyword regex + templated var names) that lack a temporal anchor in the composition stack. Fires `F9 (high)` with score impact `instruction-clarity −3, schema-tightness −1`. No LLM call required.

**value-type-drift mechanical check.** Eval's mechanical comparator now catches when a key's value type in prod output differs from the OUTPUT_SCHEMA declaration — even when the key is present (schema-shape check passes but value shape doesn't). Catches cases like Gemini emitting `array<object>` when the schema declares `string`.

**Prompt-injection vulnerability grading (5th scoring dimension + 3 findings + active probe).** `:audit` now scores each prompt on a 5th dimension: `injectionResistance` (1-10, default weight 0.20). Three new findings:
- F10 (high) — user-input var with no sanitization directive
- F11 (medium) — defense-in-depth scarcity (< 2 defense phrases)
- F12 (critical) — user-var at or before system instruction in composition order

All three carry `handoffHint: "vibe-sec:audit"` for cross-plugin app-level review.

`:eval --inject-attacks` adds an active probe: 6 canonical injection patterns (direct-override, role-assertion, role-flip, instruction-deflection, trust-manipulation, encoded-payload) substituted into each user-input var, judged by a binary LLM-judge. Results in `run-result.injectAttackResults` + `injectAttackSummary`. Typical cost: $0.006 for 1 prompt × 1 var × 6 fixtures.

App-type heuristic: audit detects consumer-facing apps (3+ user-input vars or CLAUDE.md signals) and suggests `injectionResistance` weight 2× (0.40). Internal apps get 0.5× (0.10). Always advisory; you confirm before the weight writes.

Weight redistribution: v0.3's 0.25 × 4 reshuffles to 0.20 × 5. Existing `weights.json` files auto-normalize.

## Iteration loop (v0.4)

The full v0.4 workflow is a six-step loop, with an optional injection-attack probe after `:eval`:

1. `/vibe-prompt:scan` — inventory every prompt site in the repo.
2. `/vibe-prompt:audit` — static structural analysis (F1-F12) with 5-dimension per-prompt scores.
3. `/vibe-prompt:eval` — behavioral drift testing with SWRS-calibrated LLM-judge and per-dimension scores. Add `--inject-attacks` for active injection probing.
4. `/vibe-prompt:grade` — synthesize audit + eval scores into composite grades across 5 dimensions; compare vs monotonic baseline; surface regressions.
5. `/vibe-prompt:iterate` — discover 3-5 new prompts the app could add, grounded in domain signals and audit gaps.
6. Build the new prompts (via `/vibe-cartographer:scope` or `/vibe-iterate:feature-add`) → loop back to step 1.

The bare `/vibe-prompt` router walks you through whichever step is next based on current state. Run it after any step to see where you stand. In v0.4 the router also detects when inject-attack results are present and surfaces the attack summary + next-action menu.

## What it does NOT do

- Auto-mutation. Audit recommendations are plans, not patches.
- Token-cost benchmarking against production logs.
- Telemetry. Nothing leaves the target app or `~/.claude/plugins/data/vibe-prompt/`.

## Required setup for :eval

`:eval` makes real API calls to your app's vendor (e.g., Gemini). Before running, set:

```bash
export VIBE_PROMPT_GEMINI_API_KEY=your-key-here
```

The namespaced variable (`VIBE_PROMPT_GEMINI_API_KEY`, not the generic `GEMINI_API_KEY`) prevents the key from being picked up by Firebase tooling or other Gemini-stack apps in the same shell.

Get a free API key at [Google AI Studio](https://aistudio.google.com/app/apikey) — the simplest source. Alternatively, if `gcloud auth print-access-token` works in your shell, Vibe-Prompt uses that Bearer token automatically (no key needed).

Keys are read from the environment only and never written to disk.

## Smell rubric (v0.4, F1–F12)

| ID | Name | Severity | Static / Eval | Score impact |
|---|---|---|---|---|
| F1 | Inline-prompt registry bypass | high | static | schema −2 |
| F1b | Registry-schema mismatch | medium | static | schema −3 |
| F2 | Voice contradiction | high | static | persona −3 |
| F3 | Implicit model assumption | medium | static | clarity −2 |
| F4 | Var drift | high | static | schema −2 |
| F5 | Persona sprawl | low | static | persona −1 |
| F6 | Hardcoded or unknown model | high | static | clarity −2 |
| F7 | Dead prompt code | medium | static | token −2 |
| F9 | Date-handling prompt without temporal grounding | high | static | clarity −3, schema −1 |
| F10 | User-input var without sanitization marker | high | static | injectionRes −4, clarity −1 |
| F11 | Defense-in-depth scarcity | medium | static | injectionRes −2 |
| F12 | User-var at or before system instruction | critical | static | injectionRes −6, persona −2 |

F10-F12 also carry `handoffHint: "vibe-sec:audit"` for cross-plugin app-level review.

## Stack coverage (v0.4)

TS/JS (Gemini, Anthropic, OpenAI) + Python (anthropic, openai, google-generativeai). Stack coverage unchanged from v0.3.

## State

State lives in your target app under `.vibe-prompt/state/` (scan + audit), `.vibe-prompt/eval/state/` (eval + radar config), `.vibe-prompt/grade/state/` (grade results + monotonic baseline), and `.vibe-prompt/iterate/` (domain cache + suggestions). Audit reports go to `docs/vibe-prompt/audit-YYYY-MM-DD.md`; eval dashboards go to `docs/vibe-prompt/eval-YYYY-MM-DD-HHMM.md`; grade dashboards go to `docs/vibe-prompt/grade-YYYY-MM-DD.md`. No telemetry.
