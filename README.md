# Vibe-Prompt

Audit, organize, and classify the LLM prompts shipped in your app.

Vibe-Prompt is the prompt-audit and behavioral-testing layer for vibe-coded apps that ship LLM features. Point it at your repo and it inventories every prompt site (registry-tracked and inline), names the structural smells, recommends a reorg, and can run your prompts against the production model to surface semantic drift. Read-only static pass by default; real vendor calls only on `:eval` with explicit cost confirmation.

## Install

[Stable channel via the vibe-plugins marketplace]
[Canary channel: this repo directly]

## What it does

- `/vibe-prompt:scan` — inventory pass. Finds every prompt site in your app (registry + inline).
- `/vibe-prompt:audit` — structural pass. Flags 7 smell categories (F1–F7) with file:line evidence.
- `/vibe-prompt:eval` — behavioral pass. Runs prompts against the prod model + an in-session Claude baseline. Surfaces semantic drift mechanically + via LLM-judge (with evaluator-drift warnings). Cost-gated; always confirms before spending.
- `/vibe-prompt:radar` — model-news pass. Checks for new model releases, deprecations, and pricing changes from your vendors. Zero LLM cost; reads vendor changelogs and docs.
- `/vibe-prompt` (bare) — state-aware router; reads inventory + audit + eval + radar state and recommends the next move.
- `/vibe-prompt:evolve-prompt` — L3 self-evolution. Reads session + friction logs across all four commands and proposes improvements to the plugin itself. Never auto-applies.

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

## Stack coverage (v0.2)

TS/JS (Gemini, Anthropic, OpenAI) + Python (anthropic, openai, google-generativeai).

## State

State lives in your target app under `.vibe-prompt/state/` (scan + audit) and `.vibe-prompt/eval/state/` (eval + radar config). Audit reports go to `docs/vibe-prompt/audit-YYYY-MM-DD.md`; eval dashboards go to `docs/vibe-prompt/eval-YYYY-MM-DD-HHMM.md`. No telemetry.
