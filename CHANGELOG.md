# Changelog

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
