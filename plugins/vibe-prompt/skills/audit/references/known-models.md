# Known model identifiers (bundled list)

**Last-updated:** 2026-10-01

Bundled list of published model IDs the v0.7 F6-suspect-model sub-finding compares against. When a prompt references a model id NOT in this list (and not in the user's `audit.f6.modelIdExceptions` config array), F6-suspect-model fires at medium severity (or high if context7 is reachable and confirms the id is not in the vendor's published list).

The **Retirement dates** section at the bottom feeds the v0.8 F6-retiring-model sub-finding. A model can be both known (real, published) and retiring: retired ids stay in the known lists below so F6-suspect-model does not double-fire on them; F6-retiring-model owns them.

This list goes stale. The v0.1 attempt at suspect-model was removed for this reason. v0.7 mitigates with:
- A last-updated stamp (this header) — auditors should sanity-check before trusting a low-severity miss.
- Confidence ladder — context7 lookup elevates from medium to high; bundled-list-only stays medium.
- Per-app config escape via `audit.f6.modelIdExceptions[]` — intentional pre-release / vendor-internal IDs can be added there to suppress the finding.

**Sources:**
- Anthropic models overview (fetched 2026-09-30): https://platform.claude.com/docs/en/models/overview
- Anthropic model deprecations (fetched 2026-09-30): https://platform.claude.com/docs/en/about-claude/model-deprecations
- Anthropic Opus 5.5 availability (Bedrock ID, fetched 2026-09-22): https://platform.claude.com/docs/en/models/opus-5-5/whats-new-opus-5-5
- Anthropic Sonnet 5.5 availability (Bedrock ID, fetched 2026-09-30): https://platform.claude.com/docs/en/models/sonnet-5-5/whats-new-sonnet-5-5
- Google Gemini models (fetched 2026-09-22): https://ai.google.dev/gemini-api/docs/models
- Google Gemini deprecations (fetched 2026-09-22): https://ai.google.dev/gemini-api/docs/deprecations

## Google (Gemini)

- `gemini-3.8-flash`
- `gemini-3.7-flash`
- `gemini-3.6-flash`
- `gemini-3.5-flash`
- `gemini-3.5-flash-lite`
- `gemini-3.1-flash-lite`
- `gemini-3.1-flash-image`
- `gemini-3-pro-image`
- `gemini-3.1-pro-preview`
- `gemini-3-flash-preview`
- `gemini-3-pro-preview` (served live as of 2026-10-01, version `3-pro-preview-11-2025`; a retired row for it was removed in 0.8.2)
- `gemini-2.5-pro`
- `gemini-2.5-flash`
- `gemini-2.5-flash-lite`
- `gemini-2.5-flash-image` (shutdown 2026-10-02; see Retirement dates)
- `gemini-2.0-flash` (shut down 2026-06-01; see Retirement dates)
- `gemini-2.0-flash-001` (shut down 2026-06-01)
- `gemini-2.0-flash-lite` (shut down 2026-06-01)
- `gemini-2.0-flash-exp`
- `gemini-2.0-flash-thinking-exp`
- `gemini-1.5-pro`
- `gemini-1.5-pro-002`
- `gemini-1.5-flash`
- `gemini-1.5-flash-002`
- `gemini-1.5-flash-8b`
- `gemini-1.0-pro`
- `gemini-embedding-2`
- `gemini-embedding-001`
- `text-embedding-004` (shut down 2026-01-14)
- `embedding-001` (shut down 2025-10-30)

<!-- Unconfirmed 2026-09-22: gemini-2.0-flash-exp, gemini-2.0-flash-thinking-exp, and every gemini-1.x id are pre-existing entries that no longer appear on Google's models or deprecations pages; their shutdown dates could not be confirmed, so they carry no Retirement row. -->

## Anthropic (Claude)

Current (models overview, 2026-09-30):

- `claude-fable-5-1`
- `claude-opus-5-5`
- `claude-sonnet-5-5`
- `claude-haiku-4-5` (dated form `claude-haiku-4-5-20251001`; still the current Haiku, no Haiku 5.x is published)

Legacy, still available:

- `claude-fable-5`
- `claude-opus-5`
- `claude-opus-4-8`
- `claude-opus-4-7`
- `claude-opus-4-6`
- `claude-opus-4-5` (dated form `claude-opus-4-5-20251101`)
- `claude-sonnet-5` (moved off the current list 2026-09-30)
- `claude-sonnet-4-6`
- `claude-sonnet-4-5` (dated form `claude-sonnet-4-5-20250929`; deprecated 2026-09-30, retires 2026-11-30, replacement `claude-sonnet-5-5`; see Retirement dates)
- `claude-mythos-5-1`
- `claude-mythos-5`
- `claude-mythos-preview` (deprecated 2026-06-09, retirement to be announced)

Retired (kept so F6-suspect-model stays quiet; F6-retiring-model fires on these):

- `claude-opus-4-1`
- `claude-opus-4`
- `claude-sonnet-4`
- `claude-3-7-sonnet`
- `claude-3-5-sonnet`
- `claude-3-5-haiku`
- `claude-3-opus`
- `claude-3-sonnet`
- `claude-3-haiku`
- `claude-2.1`
- `claude-2.0`

Platform-prefixed forms (confirmed on the models overview and the Opus 5.5 / Sonnet 5.5 availability lists):

- `anthropic.claude-fable-5-1`
- `anthropic.claude-opus-5-5`
- `anthropic.claude-sonnet-5-5`
- `anthropic.claude-sonnet-5`
- `anthropic.claude-haiku-4-5`

<!-- Removed 2026-09-22: claude-sonnet-4-7 and claude-haiku-4-6. Neither appears on the models overview or the deprecations page; they were never published ids. -->
<!-- Unconfirmed 2026-09-22: Bedrock ids for models older than those five, and regional/global Bedrock inference-profile prefixes (e.g. `us.`, `global.`). The overview mentions regional and global endpoints but does not print the prefixed strings. Add via `audit.f6.modelIdExceptions[]` per app until confirmed. -->

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

A match is **case-insensitive** on the model id. Suffix variants are stripped before comparison:

- Date stamps like `-20250115` — `gemini-2.5-flash-20250115` matches `gemini-2.5-flash`; `claude-3-5-sonnet-20241022` matches `claude-3-5-sonnet`.
- Google Cloud `@YYYYMMDD` snapshots — `claude-haiku-4-5@20251001` matches `claude-haiku-4-5`.
- A `[1m]`-style context suffix a harness appends (e.g. `claude-opus-5-5[1m]`) is stripped before comparison.

A `:lite`, `:nano`, `:pro`, or similar variant suffix introduced by a vendor in a new release that isn't on this list will fire the finding until the list is updated. Per-app escape: add to `audit.f6.modelIdExceptions[]`.

## Confidence ladder

- **High confidence** — context7 lookup succeeded AND vendor's published-models list does NOT contain the id. The audit can state "vendor-confirmed not-in-published-list" with grounding.
- **Medium confidence** — context7 unavailable; only the bundled list above was consulted. The audit recommends "verify against the vendor's current model list manually."

## Retirement dates

Feeds F6-retiring-model (v0.8). Key is the suffix-stripped id per the Detection rules above. `Kind` is:

- `retired` — the vendor lists the model as retired / shut down on that date. Requests fail.
- `scheduled` — the vendor has announced a retirement or shutdown date.
- `floor` — the vendor commits only to "not sooner than" this date. The model may live longer; the date is the earliest it can go.

Anthropic dates apply to Anthropic-operated platforms (Claude API, Claude Platform on AWS, Microsoft Foundry); Amazon Bedrock and Google Cloud set their own schedules. Source: https://platform.claude.com/docs/en/about-claude/model-deprecations (fetched 2026-09-30).

| Model (stripped) | Dated / full id on the vendor page | Retirement date | Kind |
|---|---|---|---|
| `claude-haiku-4-5` | `claude-haiku-4-5-20251001` | 2026-10-15 | floor |
| `claude-opus-4-5` | `claude-opus-4-5-20251101` | 2026-11-24 | floor |
| `claude-sonnet-4-5` | `claude-sonnet-4-5-20250929` | 2026-11-30 | scheduled |
| `claude-opus-4-6` | `claude-opus-4-6` | 2027-02-05 | floor |
| `claude-sonnet-4-6` | `claude-sonnet-4-6` | 2027-02-17 | floor |
| `claude-opus-4-7` | `claude-opus-4-7` | 2027-04-16 | floor |
| `claude-opus-4-8` | `claude-opus-4-8` | 2027-05-28 | floor |
| `claude-fable-5` | `claude-fable-5` | 2027-06-09 | floor |
| `claude-mythos-5` | `claude-mythos-5` | 2027-06-09 | floor |
| `claude-sonnet-5` | `claude-sonnet-5` | 2027-06-30 | floor |
| `claude-opus-5` | `claude-opus-5` | 2027-07-24 | floor |
| `claude-fable-5-1` | `claude-fable-5-1` | 2027-09-01 | floor |
| `claude-mythos-5-1` | `claude-mythos-5-1` | 2027-09-01 | floor |
| `claude-opus-5-5` | `claude-opus-5-5` | 2027-09-22 | floor |
| `claude-sonnet-5-5` | `claude-sonnet-5-5` | 2027-09-28 | floor |
| `claude-opus-4-1` | `claude-opus-4-1-20250805` | 2026-08-05 | retired |
| `claude-opus-4` | `claude-opus-4-20250514` | 2026-06-15 | retired |
| `claude-sonnet-4` | `claude-sonnet-4-20250514` | 2026-06-15 | retired |
| `claude-3-haiku` | `claude-3-haiku-20240307` | 2026-04-20 | retired |
| `claude-3-7-sonnet` | `claude-3-7-sonnet-20250219` | 2026-02-19 | retired |
| `claude-3-5-haiku` | `claude-3-5-haiku-20241022` | 2026-02-19 | retired |
| `claude-3-opus` | `claude-3-opus-20240229` | 2026-01-05 | retired |
| `claude-3-5-sonnet` | `claude-3-5-sonnet-20240620`, `claude-3-5-sonnet-20241022` | 2025-10-28 | retired |
| `claude-3-sonnet` | `claude-3-sonnet-20240229` | 2025-07-21 | retired |
| `claude-2.1` | `claude-2.1` | 2025-07-21 | retired |
| `claude-2.0` | `claude-2.0` | 2025-07-21 | retired |

Google Gemini API shutdown dates. Source: https://ai.google.dev/gemini-api/docs/deprecations (fetched 2026-09-22). Correction 2026-10-01: `gemini-3-pro-preview` carried a "retired 2026-03-09" row here through 0.8.1; a live `GET /v1beta/models/gemini-3-pro-preview` on 2026-10-01 returned the model (version `3-pro-preview-11-2025`, generateContent supported), so the row was wrong and is removed. Prefer the live models endpoint over a page read when a row would fire F6-retiring-model on a model an app is serving today.

| Model (stripped) | Full id on the vendor page | Retirement date | Kind |
|---|---|---|---|
| `gemini-2.5-flash-image` | `gemini-2.5-flash-image` | 2026-10-02 | scheduled |
| `gemini-3.1-flash-lite` | `gemini-3.1-flash-lite` | 2027-05-07 | scheduled |
| `gemini-embedding-001` | `gemini-embedding-001` | 2028-05-14 | scheduled |
| `gemini-2.0-flash` | `gemini-2.0-flash`, `gemini-2.0-flash-001` | 2026-06-01 | retired |
| `gemini-2.0-flash-lite` | `gemini-2.0-flash-lite`, `gemini-2.0-flash-lite-001` | 2026-06-01 | retired |
| `text-embedding-004` | `text-embedding-004` | 2026-01-14 | retired |
| `embedding-001` | `embedding-001` | 2025-10-30 | retired |

<!-- 2026-09-30: claude-sonnet-4-5-20250929 moved from floor (2026-09-29) to scheduled (2026-11-30) when Anthropic announced its deprecation; recommended replacement claude-sonnet-5-5. -->
<!-- Not listed: claude-mythos-preview (deprecated 2026-06-09, retirement "to be announced"; no date to compute against). claude-1.x / claude-instant-1.x (retired 2024-11-06) are omitted from both lists as too old to appear in a live codebase; add them if an audit ever meets one. -->

## Updating this list

When new models ship (vendor announcement, SDK release, context7 catches a new id), update the relevant section above and bump the last-updated stamp. When a vendor's deprecations page changes, update the Retirement dates tables in the same edit. Major-version bumps to a vendor's family (e.g., the next Gemini, Claude 6) get their own subsection. Never add an id that a vendor page does not print; unconfirmed ids go in a comment line.
