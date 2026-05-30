# Vibe-Prompt

Audit, organize, and classify the LLM prompts shipped in your app.

Vibe-Prompt is the prompt-audit and behavioral-testing layer for vibe-coded apps that ship LLM features. Point it at your repo and it inventories every prompt site (registry-tracked and inline), names the structural smells, recommends a reorg, and can run your prompts against the production model to surface semantic drift. Read-only static pass by default; real vendor calls only on `:eval` with explicit cost confirmation.

## Install

[Stable channel via the vibe-plugins marketplace]
[Canary channel: this repo directly]

## What it does

- `/vibe-prompt:scan` — inventory pass. Finds every prompt site in your app (registry + inline). Detects template-literal `${var}`, string-concat, and JSX-attr interpolations alongside `{{handlebars}}`. Classifies each templated var by origin (user-controlled vs system-injected) so injection grading targets the right vars.
- `/vibe-prompt:audit` — structural pass. Flags 13 smell categories (F1–F13) with file:line evidence. Produces per-prompt scores across 5 dimensions (schema tightness, persona consistency, instruction clarity, token efficiency, injection resistance). F9 checks date-grounding; F10-F12 grade prompt-injection vulnerability and filter out system-injected vars before firing; F12 detection is now API-parameter-aware (deterministic when composer.json layers have `apiParameter` populated); F13 flags prompts that use structural cues without declaring their output format.
- `/vibe-prompt:eval` — behavioral pass. Runs prompts against the prod model + an in-session Claude baseline. Surfaces semantic drift via mechanical comparator (including value-type-drift check) + LLM-judge with SWRS calibration, Long CoT reasoning, Swap-and-Discard position-bias mitigation, and verbosity penalty. Per-dimension scores on eval output. Cost-gated; always confirms before spending. Accepts `--inject-attacks` flag to run 6 canonical injection patterns against each prompt with a user-input var — judges whether the model honored the attack or held its role. Handoff to `/vibe-sec:audit` recommended when attacks succeed.
- `/vibe-prompt:grade` — synthesis pass. Reads audit + latest eval scores and computes per-prompt + app composite grades via weighted average. Tracks each prompt's best-ever score as the monotonic baseline — improvements advance it, regressions flag without resetting. Surfaces composite trends and flagged regressions in one dashboard.
- `/vibe-prompt:iterate` — discovery pass. Reads your inventory + audit findings + app domain (detected from CLAUDE.md → vibe-tool artifacts → package metadata → brief interview), dispatches one creative-divergent LLM call (~$0.02), and returns 3-5 prompts your app could add — each with a handoff hint to `/vibe-cartographer:scope` or `/vibe-iterate:feature-add`.
- `/vibe-prompt:remediate` — fix pass. Closes the audit → fix loop. Reads latest audit + composer.json, groups findings by fix category (A composer-level additions, B contradiction removal split into banned-phrase-removal + voice-frame-rewrite sub-categories, C defense addition), scores each proposed diff on a 5-dimension confidence rubric, and routes: auto-write (≥0.90 with backup), stage to `.vibe-prompt/remediate/pending/` (0.70-0.89), inline-only (<0.70). Voice-frame rewrites stage by default (voice-drift risk); `--apply-voice-frame-fixes` opts in to normal routing. F12 critical findings emit a cross-plugin handoff banner to `/vibe-sec:audit` rather than auto-proposing — composition-order is upstream of the prompt. Opt-in `--auto-handoff-vibe-sec` invokes `/vibe-sec:audit` automatically when F12 critical fires (falls back to banner if vibe-sec isn't installed).
- `/vibe-prompt:radar` — model-news pass. Checks for new model releases, deprecations, and pricing changes from your vendors. Zero LLM cost; reads vendor changelogs and docs.
- `/vibe-prompt` (bare) — state-aware router; reads inventory + audit + eval + grade + iterate + radar state plus pending remediation files and recommends the next move.
- `/vibe-prompt:evolve-prompt` — L3 self-evolution. Reads session + friction logs across all seven commands and proposes improvements to the plugin itself. Never auto-applies.

## What's new in v0.6

Five additive capabilities in the "detection sharpness" theme. No breaking changes to v0.5 surface area.

**F12 API-parameter-aware detection.** v0.5's F12 compared layer order from composer.json — useful, but blind to the difference between content passed in `systemInstruction:` vs `contents[]` (Gemini) or `messages[]` (OpenAI / Anthropic). When user content lives in `contents[]` and system instructions live in `systemInstruction:`, the API enforces structural separation regardless of composition order. v0.6 reads a new `apiParameter` field per composer layer and emits the correct deterministic verdict — F12 only fires critical when user-var and system-instruction layers share the same API parameter. When `apiParameter` is unknown, F12 confidence-degrades per v0.5 fallback. The Celestia3 `dreamText` case (passed in `contents[]`, not `systemInstruction:`) now correctly does NOT fire F12 critical.

**F13 — Implicit output format.** New static finding. Fires when a prompt uses structural cues (`[BRACKETS]` blocks, repeated `{{vars}}`, JSON-shaped data sections) but doesn't declare its output format. The model may emit JSON, code fences, or partial structure when prose was expected, or vice versa. Recommendation template offers two fixes: add `[OUTPUT FORMAT: prose, no JSON or code fences]` for prose output, or add `[OUTPUT_SCHEMA]` block for structured output. Suppressed by explicit `[OUTPUT FORMAT: flexible]` directive or via `audit.f13.outputFormatExceptions` config. Severity medium. Score impact: schema-tightness −2, instruction-clarity −1. Static analysis — no LLM cost.

**Category B voice-frame depth.** v0.5's Category B remediation caught direct banned-phrase matches (e.g., "Fellow Pilgrim") but missed voice-frame language patterns — "quatrain-style narrative", "shattering of the veil", "ancient dust" — that echo a banned persona without using the literal banned phrase. v0.6 extracts voice rules from the global directive (bans + positive guidance) and matches voice-frame phrase clusters (archaic vocabulary, ritualistic framing, capitalized abstract nouns) in task prompts. Emitted as Category B with `subCategory: "voice-frame-rewrite"`, confidence 0.65, ALWAYS staged by default. Opt in to normal confidence routing via `--apply-voice-frame-fixes` flag.

**`:remediate --auto-handoff-vibe-sec` flag.** v0.5 emitted a handoff banner on F12 critical recommending `/vibe-sec:audit` — advisory only. v0.6 adds opt-in auto-invocation: when the flag is set AND F12 critical fires AND vibe-sec is installed, `:remediate` invokes `/vibe-sec:audit --scope user-input-boundary` automatically and writes the result to `.vibe-prompt/remediate/state/handoff-vibe-sec-<timestamp>.json`. Falls back to v0.5 banner-only behavior with friction-log when vibe-sec isn't installed. Cross-plugin handoff orchestration without merging concerns — vibe-sec findings stay in vibe-sec; vibe-prompt just orchestrates.

**composer.schema `global-directive` enum.** Cosmetic fix. v0.5's first-run-setup emitted `directive-field` for layers that should be `global-directive`. v0.6 extends the layer-type enum to include `global-directive` and updates first-run-setup detection. `directive-field` remains a deprecated alias — old composer.json files continue to validate.

**7 new friction triggers** for the v0.6 detection gaps (apiParameter low confidence, auto-handoff outcomes, F13 false positives, voice-frame confidence and rejections).

## What's new in v0.5

Four additive capabilities. No breaking changes to v0.4 surface area.

**`/vibe-prompt:remediate` — the headline.** New sixth step-command. Closes the audit → fix loop. Reads the latest audit + composer.json, groups findings into three fix categories, scores each proposed diff on a 5-dimension confidence rubric (locate, diff-shape, voice-risk, schema-impact, version-bump), and routes them:

- **Category A — composer-level additions** (high confidence). One file, pure addition between named sections, no semantic edits. Maps F9 date-grounding to a master-directive injection. Default confidence 0.92.
- **Category B — contradiction removal** (medium confidence). One registry entry or inline prompt; locate-and-rephrase against a banned-phrase list pulled from F2 detection. Stages by default — voice drift risk requires re-eval. Default confidence 0.75.
- **Category C — defense addition** (high confidence on the additive parts). One prompt's content; adds a defense block before user-input vars plus a structural delimiter around the user var. Maps F10, F11, and F12 (when the fix is additive rather than restructuring). Default confidence 0.88 on the contract paragraph, 0.78 on delimiter placement.

Routing: ≥0.90 auto-writes (with backup at `.vibe-prompt/remediate/backup/<ISO-timestamp>/`); 0.70-0.89 stages to `.vibe-prompt/remediate/pending/<finding-id>.diff` with YAML front-matter; <0.70 inline-only. Flags: `--apply-pending`, `--reject-pending`, `--rollback`, `--interactive`, `--auto-apply`, `--skip-f12`, `--apply-contradictions`. F12 critical findings emit a handoff banner to `/vibe-sec:audit` instead of auto-proposing a fix — composition-order belongs upstream.

**Inventory scan completeness.** `:scan` now detects three more inline-prompt patterns beyond `{{handlebars}}`: template-literal `${var}` interpolations, string concatenation (`'... ' + userVar + ' ...'`), and JSX template attributes (`<Component prompt={`...${var}...`}>`). Each templated var carries `source` (handlebars | template-literal | concat | jsx-attr) and `declaredAt` line reference in `inventory.json`. Closes the gap that hid Oneirocriton's `dreamText` var from v0.4's F10 detection.

**System-injected var detection.** `:scan` now classifies each templated var by origin (`user-controlled` | `system-injected` | `unknown`) using a naming heuristic + call-graph proximity signal. `:audit` reads the origin field and filters F10/F11/F12 to user-controlled vars only. Findings record `originFilteredOut: true` when a candidate var was excluded. Closes the v0.4 false positive where arithmancy's `{{knowledgeContext}}` (a KnowledgeService injection) triggered F10. Config override at `.vibe-prompt/config/var-origins.json`.

**composer.json auto-generation in `:first-run-setup`.** v0.4 fired F12 confidence-degraded when composer.json was absent; `:remediate` Category A needs the layer map to locate composer files and named sections. `:first-run-setup` now detects composer files (filename heuristics + SDK imports), traces composition layers, classifies each layer (global-directive | format-directive | knowledge-context | task-instruction | user-data), and emits composer.json with per-layer confidence + globalConfidence. Floors confidence at 0.4 and prompts for verification when fewer than 2 layers resolve. Re-runnable via `:first-run-setup --regenerate-composer`.

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

## Iteration loop (v0.5)

The full v0.5 workflow is a seven-step loop, with an optional injection-attack probe after `:eval` and a fix pass after `:grade`:

1. `/vibe-prompt:scan` — inventory every prompt site (registry + inline patterns + var-origin classification).
2. `/vibe-prompt:audit` — static structural analysis (F1-F12) with 5-dimension per-prompt scores; F10-F12 filtered to user-controlled vars.
3. `/vibe-prompt:eval` — behavioral drift testing with SWRS-calibrated LLM-judge and per-dimension scores. Add `--inject-attacks` for active injection probing.
4. `/vibe-prompt:grade` — synthesize audit + eval scores into composite grades across 5 dimensions; compare vs monotonic baseline; surface regressions.
5. `/vibe-prompt:remediate` — close the audit → fix loop. Group findings by category, score confidence, route auto-write / stage / inline-only. Stage Category B by default; re-eval after applying.
6. `/vibe-prompt:iterate` — discover 3-5 new prompts the app could add, grounded in domain signals and audit gaps.
7. Build the new prompts (via `/vibe-cartographer:scope` or `/vibe-iterate:feature-add`) → loop back to step 1.

The bare `/vibe-prompt` router walks you through whichever step is next based on current state. Run it after any step to see where you stand. In v0.5 the router also detects when `.vibe-prompt/remediate/pending/` is non-empty and surfaces the review-pending-remediations menu (apply / reject / rollback per finding).

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

## Smell rubric (v0.6, F1–F13)

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
| F13 | Implicit output format (structural cues + no declaration) | medium | static | schema −2, clarity −1 |

F10-F12 also carry `handoffHint: "vibe-sec:audit"` for cross-plugin app-level review. F12 fires deterministically only when user-var and system-instruction layers share the same API parameter — when `apiParameter` is unknown, severity degrades to high per v0.5 fallback.

## Stack coverage (v0.5)

TS/JS (Gemini, Anthropic, OpenAI) + Python (anthropic, openai, google-generativeai). Inline-prompt patterns extended in v0.5: handlebars + template-literal + string-concat + JSX-attr. Stack vendors unchanged from v0.4.

## State

State lives in your target app under `.vibe-prompt/state/` (scan + audit), `.vibe-prompt/eval/state/` (eval + radar config), `.vibe-prompt/grade/state/` (grade results + monotonic baseline), `.vibe-prompt/iterate/` (domain cache + suggestions), and `.vibe-prompt/remediate/` (pending diffs + backup batches + runs ledger). Audit reports go to `docs/vibe-prompt/audit-YYYY-MM-DD.md`; eval dashboards go to `docs/vibe-prompt/eval-YYYY-MM-DD-HHMM.md`; grade dashboards go to `docs/vibe-prompt/grade-YYYY-MM-DD.md`. composer.json lives at `.vibe-prompt/composer.json` once generated. No telemetry.
