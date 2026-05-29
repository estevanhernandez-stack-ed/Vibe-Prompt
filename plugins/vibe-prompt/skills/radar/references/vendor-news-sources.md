# Vendor news sources — radar

Where vibe-prompt looks for model-space updates per vendor.

## Sources by vendor

### Gemini (Google)

- Google AI blog: https://blog.google/technology/ai/
- Gemini API docs changelog: https://ai.google.dev/gemini-api/docs/changelog
- AI Studio model registry: https://aistudio.google.com/models (model list when reachable)
- Search context7 for "google gemini model release" with date filter ≥ last 90 days

### Anthropic

- Anthropic news: https://www.anthropic.com/news
- Claude docs changelog: https://docs.claude.com/en/docs/changelog
- Search context7 for "anthropic claude model release" with date filter ≥ last 90 days

### OpenAI

- OpenAI blog: https://openai.com/blog
- Platform docs models page: https://platform.openai.com/docs/models
- Search context7 for "openai gpt model release" with date filter ≥ last 90 days

## Fetch order

1. Try context7 first (cached + structured).
2. Fall back to WebFetch on the direct URLs.
3. If both fail for a vendor, friction-log `vendor-news-source-unreachable` and skip that vendor for this run (don't fail the whole radar).

## What to extract

For each source, look for:

- **New model announcements** — model name, release date, summary line
- **Deprecation notices** — model name, sunset date
- **Pricing changes** — affected models, new $/1M tok rates (these update the rate table in `cost-gates.md`)

## Cache

Write `.vibe-prompt/eval/cache/radar.json`:

```json
{
  "version": "0.1",
  "fetchedAt": "<ISO 8601>",
  "vendors": {
    "gemini": {
      "newModels": [
        { "name": "gemini-3.0-flash", "announcedAt": "2026-05-15", "summary": "..." }
      ],
      "deprecations": [
        { "name": "gemini-2.0-pro", "sunsetAt": "2026-08-01" }
      ]
    },
    "anthropic": { ... },
    "openai": { ... }
  }
}
```

Cache TTL: 7 days. Bare command refreshes if older.

## Never

- Make vendor API calls during radar (radar is read-only on docs, not models).
- Persist any vendor pricing data without dated source URL (provenance matters).
