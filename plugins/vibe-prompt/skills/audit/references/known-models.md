# Known model identifiers (bundled list)

**Last-updated:** 2026-06-01

Bundled list of published model IDs the v0.7 F6-suspect-model sub-finding compares against. When a prompt references a model id NOT in this list (and not in the user's `audit.f6.modelIdExceptions` config array), F6-suspect-model fires at medium severity (or high if context7 is reachable and confirms the id is not in the vendor's published list).

This list goes stale. The v0.1 attempt at suspect-model was removed for this reason. v0.7 mitigates with:
- A last-updated stamp (this header) — auditors should sanity-check before trusting a low-severity miss.
- Confidence ladder — context7 lookup elevates from medium to high; bundled-list-only stays medium.
- Per-app config escape via `audit.f6.modelIdExceptions[]` — intentional pre-release / vendor-internal IDs can be added there to suppress the finding.

## Google (Gemini)

- `gemini-2.5-pro`
- `gemini-2.5-flash`
- `gemini-2.5-flash-lite`
- `gemini-2.0-flash`
- `gemini-2.0-flash-exp`
- `gemini-2.0-flash-thinking-exp`
- `gemini-1.5-pro`
- `gemini-1.5-pro-002`
- `gemini-1.5-flash`
- `gemini-1.5-flash-002`
- `gemini-1.5-flash-8b`
- `gemini-1.0-pro`
- `text-embedding-004`
- `embedding-001`

## Anthropic (Claude)

- `claude-opus-4-7`
- `claude-opus-4-6`
- `claude-opus-4-5`
- `claude-sonnet-4-7`
- `claude-sonnet-4-6`
- `claude-sonnet-4-5`
- `claude-haiku-4-6`
- `claude-haiku-4-5`
- `claude-3-7-sonnet`
- `claude-3-5-sonnet`
- `claude-3-5-haiku`
- `claude-3-opus`
- `claude-3-sonnet`
- `claude-3-haiku`

## OpenAI

- `gpt-4o`
- `gpt-4o-mini`
- `gpt-4-turbo`
- `gpt-4`
- `gpt-3.5-turbo`
- `o1`
- `o1-mini`
- `o1-preview`
- `text-embedding-3-large`
- `text-embedding-3-small`
- `text-embedding-ada-002`

## Detection rules

A match is **case-insensitive** on the model id. Suffix variants (e.g., date stamps like `-20250115`) are stripped before comparison — `gemini-2.5-flash-20250115` matches `gemini-2.5-flash`.

A `:lite`, `:nano`, `:pro`, or similar variant suffix introduced by a vendor in a new release that isn't on this list will fire the finding until the list is updated. Per-app escape: add to `audit.f6.modelIdExceptions[]`.

## Confidence ladder

- **High confidence** — context7 lookup succeeded AND vendor's published-models list does NOT contain the id. The audit can state "vendor-confirmed not-in-published-list" with grounding.
- **Medium confidence** — context7 unavailable; only the bundled list above was consulted. The audit recommends "verify against the vendor's current model list manually."

## Updating this list

When new models ship (vendor announcement, SDK release, context7 catches a new id), update the relevant section above and bump the last-updated stamp. Major-version bumps to a vendor's family (e.g., the next Gemini, Claude 5) get their own subsection.
