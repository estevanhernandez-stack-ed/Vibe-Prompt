---
name: vibe-prompt:radar
description: This skill should be used when the user says "/vibe-prompt:radar", "what's new in models", "any new gemini models", "model news digest". Read-only digest of model-space updates for vendors the app uses. Reads inventory to find vendors; queries vendor news sources via context7 + web fetch; caches weekly. Zero LLM calls at run time.
---

# /vibe-prompt:radar

Load `vibe-prompt:guide`. Then load `references/vendor-news-sources.md`.

## Inputs

- `.vibe-prompt/state/inventory.json` (read to identify vendors)
- `.vibe-prompt/eval/cache/radar.json` (read for last fetch timestamp)

## Workflow

1. **Pre-flight.** `session-logger` start. Read inventory; collect unique vendors from `aiProviders`.

2. **Cache check.** Read `.vibe-prompt/eval/cache/radar.json`. If `fetchedAt < 7 days ago`, render banner from cache and exit.

3. **Refresh fetch.** For each vendor, query the sources in `references/vendor-news-sources.md`. Extract new models, deprecations, pricing changes.

4. **Update cache.** Write `.vibe-prompt/eval/cache/radar.json` atomic.

5. **Render banner.**

```
═══ Vibe-Prompt radar ═══
Fetched:        2026-05-28 14:30 UTC
Vendors:        gemini

Since your last check (2026-05-15):
  NEW   gemini-3.0-flash — announced 2026-05-22, faster + cheaper than 3.5-flash
  DEPR  gemini-2.0-pro — sunset 2026-08-01

Next: /vibe-prompt:eval --mode upgrade-test --candidate gemini-3.0-flash
      to verify parity before swapping.
```

6. **Post-flight.** session-logger terminal.

## Never

- Make any model API call.
- Persist API keys.
- Auto-trigger an upgrade-test eval (only suggest).
