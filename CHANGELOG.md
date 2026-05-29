# Changelog

## v0.3.0 — 2026-05-29

Per-dimension scoring, composite grades, monotonic baseline regression tracking, and creative prompt discovery.

**New commands:**
- `/vibe-prompt:grade` — synthesizes audit + latest eval scores into per-prompt + app composite grades via weighted average across 4 dimensions. Tracks each prompt's best-ever score as the monotonic baseline: improvements advance it, regressions flag with ⚠ without resetting the bar. Accepts `--accept-regression` to advance baseline manually when a score drop is intentional.
- `/vibe-prompt:iterate` — creative discovery of new prompts your app could add. Reads inventory + audit findings + app domain (detected via CLAUDE.md → vibe-tool artifacts → package metadata → brief interview as last resort), dispatches one creative-divergent LLM call (~$0.02, Haiku at temperature 0.9), returns 3-5 suggestions with purpose, target persona, example output shape, and handoff hints to `/vibe-cartographer:scope` or `/vibe-iterate:feature-add`.

**Scoring extensions:**
- `:audit` and `:eval` now produce per-prompt scores on 4 dimensions: schema tightness, persona consistency, instruction clarity, token efficiency. Each 1-10.
- Composite per-prompt = weighted average of 4 dimension scores (default equal weights; user-overridable at `.vibe-prompt/grade/weights.json`).
- App composite = average of per-prompt composites across the full inventory.
- Agent proactively suggests weight overrides when a dimension is brand-load-bearing (e.g., 4+ F2 findings → suggest persona-consistency 2× weight).

**LLM-judge calibration patterns (all applied together on `:eval`'s judge layer):**
- SWRS structure: judge emits Strengths, Weaknesses, Reasoning before Score — reduces middling-score bias.
- Long CoT: judge walks analysis step-by-step per dimension before committing to scores — reduces self-preference bias.
- Swap-and-Discard: each prod-vs-baseline comparison runs twice (swapped order); position-bias ties are discarded. Tie rate > 30% friction-logged as `swap-and-discard-tie-rate-over-30pct`.
- Verbosity penalty: judge explicitly instructed to penalize unnecessary elaboration — "quality is not length."

**Monotonic baseline discipline:**
- `:grade` tracks "best score so far" per prompt — never the most recent run.
- Improvements advance the baseline; regressions flag without advancing backward.
- Designed to surface drift without letting it become normal. The bar only moves up.

**Cross-plugin architecture note:**
- `:iterate`'s "creative discovery from inventory + domain signals" pattern is reusable architecture. The domain-detection cascade (CLAUDE.md → vibe-tool artifacts → package metadata → interview) and the creative-divergent dispatch pattern are documented in `skills/iterate/references/` for vibe-iterate v.NEXT to lift as `:feature-add-ai` (working name). Cross-plugin reuse is the intent, not a fork concern.

**6 new friction triggers:**
- Grade: `weight-override-suggested-and-rejected` (low), `regression-flagged` (high), `regression-flagged-and-accepted-as-baseline` (medium), `composite-score-flat-after-fix` (medium), `swap-and-discard-tie-rate-over-30pct` (medium).
- Iterate: `iterate-suggestion-implemented` (high), `iterate-suggestion-dismissed-as-off-domain` (medium).

**Validation (Celestia3 round-trip — design-time):**
- Round-tripped on Celestia3 `natal_interpretation` namespace. Persona-consistency on `natal_interpretation` expected to drag app composite into the 60-75 range due to the Pilgrim contradiction (the F2 finding from v0.1 now scores numerically — validates that scoring catches what the rubric flags qualitatively).
- `:iterate` expected to propose 3+ from ground-truth list: horary, progressed chart, solar return, composite chart, tarot spreads, remediation rituals.

**v0.4+ candidates queued:**
- Prompt-injection vulnerability grading: vibe-sec audits app-level injection surface; vibe-prompt should cover prompt-content-level security (new family composition gap, not yet addressed by either plugin).
- Auto-handoff from `:iterate` suggestions directly into `/vibe-cartographer:scope` (currently requires manual copy-paste).
- App-callable eval endpoint pattern: expose `:eval` as a callable from CI rather than a pure conversational command.
- Value-type-drift mechanical check: catch when a prompt's output schema declares `string` but the actual output is consistently returning `array` (static type-drift, detectable without LLM-judge).

---

## v0.2.0 — 2026-05-29

Behavioral testing and model-news radar, re-homed from the brief standalone Vibe-Eval design into vibe-prompt step-commands.

**New commands:**
- `/vibe-prompt:eval` — runs prompts against the prod model + in-session Claude baseline (drift mode) or a candidate model (upgrade-test mode). Surfaces semantic drift via mechanical comparator + LLM-judge. Every judge finding ships with an evaluator-drift footer. Cost-gated with pre-run estimate + confirm.
- `/vibe-prompt:radar` — checks vendor changelogs and model release pages for new models, deprecations, and pricing changes relevant to your stack. Zero LLM cost.

**Behind the scenes:**
- `first-run-setup` SKILL: one-time onboarding for eval — captures composer pattern, detects agent identity, sets cost ceiling, writes `.vibe-prompt/eval/{config,composer,agent}.json`.
- Vendor-clients abstraction: `GeminiClient` via curl + AI Studio API key or OAuth Bearer. `REFERER` header set for AI Studio free-tier compatibility.
- Bare router extended to 5 state branches: scan → audit → eval → radar-refresh → full posture. Each branch hands off to the appropriate command with a cost/impact summary.
- `evolve-prompt` loop extended: reads eval-side and radar-side friction (cost-ceiling hits, evaluator-drift dismissals, stale-radar events) alongside scan/audit friction. Single evolution loop for all four commands.

**Env var naming:**
- `VIBE_PROMPT_GEMINI_API_KEY` — NOT the generic `GEMINI_API_KEY`. Namespaced to prevent pickup by Firebase tooling or other Gemini-stack apps in the same shell.

**Validation (Celestia3 round-trip):**
- Round-tripped on Celestia3 `natal_interpretation` prompt. Real cross-vendor drift detected: Pilgrim character reference leaked in Gemini-2.5-flash output; in-session Claude baseline honored the prohibition. 5 LLM-judge findings produced with cross-vendor evaluator-drift footer. Cost $0.000198. Run aborted cleanly within $2.00 ceiling.

**Architectural note:**
Behavioral capabilities were briefly designed as a standalone plugin (Vibe-Eval solo repo, `C:/Users/estev/Projects/Vibe-Eval`) before being re-homed into vibe-prompt step-commands. The solo repo served as the design surface; the migration (Phases 1–8) moved all content into vibe-prompt with substitutions applied. Vibe-Eval solo repo is now archived.

---

## v0.1.0 — 2026-05-28

Initial release. Static prompt audit for vibe-coded apps.

**Commands:**
- `/vibe-prompt:scan` — inventory every prompt site (registry + inline)
- `/vibe-prompt:audit` — flag the 7 structural smells (F1-F7)
- `/vibe-prompt` — state-aware bare router
- `/vibe-prompt:evolve-prompt` — L3 self-evolution

**Stack coverage:** TypeScript/JavaScript and Python.

**Validation:** round-tripped against Celestia3 (Next.js + Firebase + Gemini). Scan found 14 prompt sites (6 registry-tracked + 8 inline) across 8 distinct personas. Audit fired 6 of 7 smells (F1-F6); F7 correctly did NOT fire because ChatService.ts uses registry-fetched prompts. The plugin caught three findings the manual cowpath audit missed: corrected F6 occurrence count, surfaced a TarotSpread.tsx voice contradiction, and detected a synastry templating mismatch.

**Known v0.1 limitations (queued for v0.2):**
- No dead-code / orphaned-prompt smell.
- F4 doesn't flag call-site `.replace()` vars that drift from the registry entry's `templatedVars`.
- No detection of conditional persona overrides (runtime branches that inject voice changes).
- F2 trace depth is one hop (global directive → task prompt).
