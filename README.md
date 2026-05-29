# Vibe-Prompt

Audit, organize, and classify the LLM prompts shipped in your app.

Vibe-Prompt is the prompt-audit and behavioral-testing layer for vibe-coded apps that ship LLM features. Point it at your repo and it inventories every prompt site (registry-tracked and inline), names the structural smells, recommends a reorg, and can run your prompts against the production model to surface semantic drift. Read-only static pass by default; real vendor calls only on `:eval` with explicit cost confirmation.

## Install

[Stable channel via the vibe-plugins marketplace]
[Canary channel: this repo directly]

## What it does

- `/vibe-prompt:scan` — inventory pass. Finds every prompt site in your app (registry + inline).
- `/vibe-prompt:audit` — structural pass. Flags 7 smell categories (F1–F7) with file:line evidence. Produces per-prompt scores across 4 dimensions (schema tightness, persona consistency, instruction clarity, token efficiency).
- `/vibe-prompt:eval` — behavioral pass. Runs prompts against the prod model + an in-session Claude baseline. Surfaces semantic drift via mechanical comparator + LLM-judge with SWRS calibration, Long CoT reasoning, Swap-and-Discard position-bias mitigation, and verbosity penalty. Per-dimension scores on eval output. Cost-gated; always confirms before spending.
- `/vibe-prompt:grade` — synthesis pass. Reads audit + latest eval scores and computes per-prompt + app composite grades via weighted average. Tracks each prompt's best-ever score as the monotonic baseline — improvements advance it, regressions flag without resetting. Surfaces composite trends and flagged regressions in one dashboard.
- `/vibe-prompt:iterate` — discovery pass. Reads your inventory + audit findings + app domain (detected from CLAUDE.md → vibe-tool artifacts → package metadata → brief interview), dispatches one creative-divergent LLM call (~$0.02), and returns 3-5 prompts your app could add — each with a handoff hint to `/vibe-cartographer:scope` or `/vibe-iterate:feature-add`.
- `/vibe-prompt:radar` — model-news pass. Checks for new model releases, deprecations, and pricing changes from your vendors. Zero LLM cost; reads vendor changelogs and docs.
- `/vibe-prompt` (bare) — state-aware router; reads inventory + audit + eval + grade + iterate + radar state and recommends the next move.
- `/vibe-prompt:evolve-prompt` — L3 self-evolution. Reads session + friction logs across all six commands and proposes improvements to the plugin itself. Never auto-applies.

## Iteration loop (v0.3)

The full v0.3 workflow is a six-step loop:

1. `/vibe-prompt:scan` — inventory every prompt site in the repo.
2. `/vibe-prompt:audit` — static structural analysis (F1-F7) with per-dimension scores.
3. `/vibe-prompt:eval` — behavioral drift testing with SWRS-calibrated LLM-judge and per-dimension scores.
4. `/vibe-prompt:grade` — synthesize audit + eval scores into composite grades; compare vs monotonic baseline; surface regressions.
5. `/vibe-prompt:iterate` — discover 3-5 new prompts the app could add, grounded in domain signals and audit gaps.
6. Build the new prompts (via `/vibe-cartographer:scope` or `/vibe-iterate:feature-add`) → loop back to step 1.

The bare `/vibe-prompt` router walks you through whichever step is next based on current state. Run it after any step to see where you stand.

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

## Stack coverage (v0.3)

TS/JS (Gemini, Anthropic, OpenAI) + Python (anthropic, openai, google-generativeai).

## State

State lives in your target app under `.vibe-prompt/state/` (scan + audit), `.vibe-prompt/eval/state/` (eval + radar config), `.vibe-prompt/grade/state/` (grade results + monotonic baseline), and `.vibe-prompt/iterate/` (domain cache + suggestions). Audit reports go to `docs/vibe-prompt/audit-YYYY-MM-DD.md`; eval dashboards go to `docs/vibe-prompt/eval-YYYY-MM-DD-HHMM.md`; grade dashboards go to `docs/vibe-prompt/grade-YYYY-MM-DD.md`. No telemetry.
