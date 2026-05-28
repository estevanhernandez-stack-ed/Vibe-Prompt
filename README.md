# Vibe-Prompt

Audit, organize, and classify the LLM prompts shipped in your app.

Vibe-Prompt is the static prompt-audit layer for vibe-coded apps that ship LLM features. Point it at your repo and it inventories every prompt site (registry-tracked and inline), names the structural smells, and recommends a reorg. Read-only by default; no behavioral testing, no auto-mutation.

## Install

[Stable channel via the vibe-plugins marketplace]
[Canary channel: this repo directly]

## What it does

- `/vibe-prompt:scan` — inventory pass. Finds every prompt site in your app.
- `/vibe-prompt:audit` — structural pass. Flags 7 smell categories with file:line evidence.
- `/vibe-prompt` (bare) — state-aware router; recommends the next move.

## What it does NOT do

- Behavioral eval (run prompts, score outputs). That's a future `vibe-eval`.
- Auto-mutation. Audit recommendations are plans, not patches.
- Token-cost benchmarking against production logs.

## Stack coverage (v0.1)

TS/JS (Gemini, Anthropic, OpenAI) + Python (anthropic, openai, google-generativeai).

## State

State lives in your target app under `.vibe-prompt/state/`. Audit reports go to `docs/vibe-prompt/`. No telemetry.
