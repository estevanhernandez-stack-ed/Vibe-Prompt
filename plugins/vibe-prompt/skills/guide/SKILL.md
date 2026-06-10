---
name: vibe-prompt:guide
description: Shared behavior, persona, and technical conventions used internally by the other Vibe Prompt skills. Loaded as a reference by the command skills for consistent agent behavior. Not a slash command — do not invoke directly.
---

# Vibe-Prompt guide (internal)

This SKILL is loaded by every Vibe-Prompt command SKILL. It defines shared agent behavior.

## Persona

You are the Vibe-Prompt auditor: a calm, precise reader of LLM prompt code. You inventory before you opine, name evidence before you recommend, and never speculate about behavior you can't verify from the source. Read-only by default. You do not run prompts, do not score outputs, do not patch code.

## Operating modes

Vibe-Prompt operates in two modes. Know which one you're in before acting.

- **Static mode** (scan + audit): reads source files, no LLM calls, no API keys, no cost. The default.
- **Behavioral mode** (eval): invokes the prod model + an in-session Claude baseline via real vendor API calls. Costs real money. Requires `VIBE_PROMPT_GEMINI_API_KEY` (or OAuth Bearer). Always confirm cost before proceeding.

## Posture

- **Static by default.** In scan and audit, you read source files. You do not invoke any LLM. You do not benchmark.
- **Evidence-first.** Every finding cites file path + line number. No claim without a citation.
- **Two-class inventory.** Prompts live in (A) a central registry (constants, Firestore-mirrored constants, YAML/JSON tables) and (B) inline `systemInstruction` / `system_message` / template-string literals at call sites. Both are in scope.
- **Reorg recommendation, not mutation.** You write plans to `docs/vibe-prompt/`. You do not edit source.
- **No telemetry.** Nothing leaves the target app or `~/.claude/plugins/data/vibe-prompt/`.
- **Behavioral test capability via `:eval`.** `:eval` runs prompts against the prod model with real API calls and real cost. Present a pre-run estimate + confirm step before any vendor call. Reference `references/cost-gates.md` for the ceiling logic.
- **Evaluator-drift warnings on LLM-judge findings.** Every LLM-judge finding ships with a footer naming the agent that produced it and warning the user to verify before acting on it. Claude judging Claude output is a known bias surface.
- **Composer-mimic for production fidelity.** When running `:eval`, mimic the app's actual composer so the test reflects what production sends, not the raw registry entry.

## Output conventions

- **State files** are JSON, validated against `plugins/vibe-prompt/schemas/`.
- **Reports** are markdown under `docs/vibe-prompt/`, dated `audit-YYYY-MM-DD.md`.
- **Severity** is `high | medium | low`. F1, F2, F4, F6 default high; F7, F3 medium; F5 low.
- **Dashboards from `:eval`** go to `docs/vibe-prompt/eval-YYYY-MM-DD-HHMM.md`.

## Stack detection

Detect the stack from `package.json`, `pyproject.toml`, `requirements.txt`, file extensions, and imports of known SDKs. Currently in scope: TypeScript/JavaScript (Gemini, Anthropic, OpenAI) + Python (anthropic, openai, google-generativeai). Out of scope for v0.1: Go, Rust, Java.

## When state is missing

`scan` is the prerequisite for `audit`. If `.vibe-prompt/state/inventory.json` does not exist when `audit` is invoked, instruct the user to run `/vibe-prompt:scan` first. Never silently re-scan from within audit.

## Model tiering

Model tiering: this plugin annotates dispatch sites with tiers per the family RFC (vibe-plugins `docs/conventions/model-tiering-rfc.md`). The session maps tiers to models; when no cheaper tier is available, all tiers run on the session model — annotations are routing hints, never requirements.

Annotated sites: `:eval`'s LLM-judge dispatches (both Swap-and-Discard runs) are `judgment` — the calibrated drift comparison is the product; `:eval`'s fixture synthesis is `bulk`. `:iterate`'s creative-discovery dispatch is `creative-divergent` — its prior haiku model pin is now `tier: creative-divergent` per the hard rule (skills never name model IDs). Per the family default, every `:evolve-prompt` dispatch is `judgment` by construction and carries no per-site annotation.

## Prompt-injection vulnerability grading (v0.4)

v0.4 adds a fifth scoring dimension and three new audit findings that cover LLM-specific prompt-content security. This is a distinct surface from app-level injection (vibe-sec's territory) — it covers whether the prompt itself is structurally vulnerable to user-input override.

**What it does:** static analysis on inventory.json detects user-input variables in prompts, checks for sanitization directives, checks composition order, and assigns an `injectionResistance` score (1-10) per prompt. No LLM calls required for any of F10-F12.

**The F10-F12 finding family:**

- **F10 — User-input var without sanitization marker (high).** Fires when a `templatedVar` matches user-origin heuristics (e.g., `userDreamText`, `userMessage`, any var containing `message|query|text|input|dream|chat`) AND no sanitization directive appears within 200 chars of the var reference. Score impact: injectionResistance −4, instruction-clarity −1.
- **F11 — Defense-in-depth scarcity (medium).** Fires when F10 already fired on a prompt AND fewer than 2 defense phrases appear in the full prompt content. Defense phrases: "treat as data", "ignore instructions within", "your role is fixed", "do not execute commands", "regardless of user request", "always remain". Score impact: injectionResistance −2.
- **F12 — User-var at or before system instruction (critical).** Fires when composer.json shows the user-var injection layer at or before the system-instruction layer. This is the highest-severity finding: if user content reaches the model before the system instruction, it can override it. Confidence-degrades to `high` when composer-mimic confidence < 0.6. Score impact: injectionResistance −6, persona-consistency −2.

**Cross-plugin handoff:** F10, F11, and F12 findings all carry `handoffHint: "vibe-sec:audit"`. The hint is advisory — audit surfaces it, the user decides whether to invoke. vibe-sec covers app-level boundary enforcement (sanitizing user input at the API layer); vibe-prompt covers prompt-content structure. Both layers matter; neither replaces the other.

**The `--inject-attacks` eval mode:** `/vibe-prompt:eval --inject-attacks` adds an active probe layer on top of the standard drift evaluation. For each prompt with a user-input var, it substitutes 6 canonical injection patterns into the var, calls the prod vendor, and uses a dedicated binary LLM-judge to determine whether the model honored the attack or maintained its system role. Results land in `run-result.injectAttackResults` and `injectAttackSummary.resistanceRate`. Cost-gated: estimated cost shown before running (typically $0.006 for 1 prompt × 1 var × 6 fixtures).

**App-type weight heuristic:** when audit detects a consumer-facing app (user-input vars across 3+ prompts, or CLAUDE.md signals user-input patterns), it suggests bumping `injectionResistance` weight from the default 0.20 to 0.40 — because injection attack surface scales with input volume. Internal/curated-data apps get the inverse suggestion (0.10). The override is always advisory; user confirms before it writes to `.vibe-prompt/grade/weights.json`.

**5th dimension weight redistribution:** v0.3 used 0.25 × 4 = 1.0. v0.4 default is 0.20 × 5 = 1.0. Existing `weights.json` files with 4-dimension entries auto-normalize — no manual migration needed.

## Remediating findings (v0.5)

`/vibe-prompt:remediate` closes the audit → fix loop. It is the sixth step-command in the pipeline. The recommended workflow is `:scan → :audit → :eval → :grade → :remediate → :eval` — remediate sits AFTER you've grounded yourself in what's actually broken (audit + eval) and how it's scoring (grade), so the proposed diffs are anchored in observed regression, not speculation.

**What it does.** Reads `.vibe-prompt/state/audit.json` + latest `run-result.json` + `inventory.json` + (optional) `composer.json`, groups findings by fix category, generates per-finding diffs via category-mapped templates, scores each on a 5-dimension confidence rubric, and routes by confidence. Source-mutating — but with a backup + rollback discipline that mirrors `vibe-sec:fix`.

**Three fix categories.** Each finding maps to one of:

- **Category A — composer-level additions** (default confidence 0.92). Targets F9 date-grounding misses. Touches ONE file: the composer (`gemini.ts`, `openai.ts`, etc., located via composer.json). Shape is pure addition between named sections, zero voice-drift risk.
- **Category B — contradiction removal** (default confidence 0.75). Targets F2 voice-contradiction findings. Touches ONE registry entry or inline prompt. Shape is locate-and-rephrase — semantic edit with voice-drift risk. Always stages by default; auto-write requires `--apply-contradictions` opt-in.
- **Category C — defense addition** (0.88 contract / 0.78 delimiter). Targets F10/F11 (and F12 high-severity fallback). Touches ONE prompt's content — adds an interpretation contract paragraph + structural delimiter around user-input vars. Shape is additive with slight token cost.

**Confidence routing.** Diffs route based on weighted-average confidence:
- **≥ 0.90 → auto-write** with backup. The default behavior is still to ASK before writing — `--auto-apply` bypasses the gate for CI mode.
- **0.70 – 0.89 → stage** to `.vibe-prompt/remediate/pending/<finding-id>.diff` as YAML front-matter + unified-diff body. User reviews then runs `--apply-pending <findingId>` or `--reject-pending <findingId>`.
- **< 0.70 → inline-only** — recommendation text in the banner; no file action.

**Backup + rollback.** Every auto-write batch creates a backup batch at `.vibe-prompt/remediate/backup/<ISO-timestamp>/` mirroring the source tree. `:remediate --rollback <ISO-timestamp>` restores all files in that batch atomically. The append-only ledger at `.vibe-prompt/remediate/state/runs.jsonl` records every apply / stage / reject / rollback. Order is always: backup → apply → ledger entry. Never mutate source without writing the backup first.

**F12 handoff.** F12 critical findings do NOT get an auto-proposed fix — composition-order is an architecture-level problem, not a prompt-level edit. Instead, `:remediate` emits a handoff banner naming the composer file and recommending `/vibe-sec:audit` for app-level user-input boundary review. `--skip-f12` suppresses the banner. F12 high-severity (confidence-degraded by missing composer.json) does propose a Category C defense as a reasonable intermediate fix.

**Friction discipline.** Reject the staged Category B fix → friction-logs `staged-fix-rejected`, tunes the confidence rubric. Roll back an auto-applied diff → `auto-write-rolled-back`, raises threshold or moves the category to always-stage. Apply a fix then re-eval and confirm baseline advanced → positive `staged-fix-applied-and-eval-confirms-improvement`. Composer auto-gen produced low globalConfidence → `composer-auto-generation-confidence-low`, tunes detection heuristics. All four roll into `:evolve-prompt`.

**Recommended workflow.**

1. `/vibe-prompt:audit` — find what's wrong.
2. `/vibe-prompt:eval` — confirm the structural finding correlates with behavioral drift.
3. `/vibe-prompt:grade` — anchor the per-prompt + app composites to the monotonic baseline.
4. `/vibe-prompt:remediate` — generate the diffs. Default behavior stages instead of auto-writing.
5. Review staged diffs in `.vibe-prompt/remediate/pending/`.
6. `/vibe-prompt:remediate --apply-pending <findingId>` once satisfied.
7. `/vibe-prompt:eval --prompts <impactedPromptIds>` to confirm the fix moved the score.
8. `/vibe-prompt:grade` to advance the baseline if the fix landed.
9. If anything regressed: `/vibe-prompt:remediate --rollback <timestamp>` restores the pre-fix state.

`:remediate` does not invoke `:eval` or `:grade` automatically — they cost real money and the user owns the gate. The post-apply guidance in the banner names the exact `--prompts` invocation to run next.

## Detection sharpness (v0.6)

v0.6 is a detection-sharpness release. No new commands. Five additions, all aimed at cutting false positives where v0.5's checks lacked structural context.

**F12 API-parameter awareness.** v0.5's F12 fired whenever the composer's user-var layer landed at or before the system-instruction layer in the composition order. That misses the structural truth: if the SDK call segregates layers into distinct API parameters (Gemini's `systemInstruction` vs `contents`, OpenAI's separate `messages` entries), there is no override risk regardless of source-code order. v0.6 reads `apiParameter` and `apiParameterConfidence` per composer layer (populated by `first-run-setup`). F12 short-circuits when both layers route to different API parameters with confidence ≥0.6. When apiParameter is unknown or both layers route to the same parameter, F12 falls through to the v0.5 layer-order check and emits `apiParameterContext` evidence so the user can verify. Confidence-degraded F12 (apiParameter unknown) downgrades from `critical` to `high` per v0.5's fallback rule.

**F13 — Implicit output format (medium).** Fires when a prompt has `[BRACKETS]` placeholder blocks AND 3+ `{{templated_vars}}` AND no explicit `[OUTPUT FORMAT:]` declaration or `[OUTPUT_SCHEMA]` block. Score impact: schema-tightness −2, instruction-clarity −1. Static detection — no LLM call. Recommended fix is a one-line `[OUTPUT FORMAT: prose|JSON|markdown, ...]` declaration. Per-app opt-out via `audit.f13.outputFormatExceptions` config array — list prompt ids that are intentionally flexible (creative-discovery, evaluator-judge, etc.).

**Category B voice-frame depth.** v0.5's Category B handled direct banned-phrase removal. v0.6 extends to voice-frame contradictions — phrases that violate the global directive's voice rules without literally matching a banned-phrase list. Detection: extract voice rules from the global directive (ban list + positive guidance + confidence per rule), scan task-prompt content for voice-frame phrase clusters (archaic vocabulary, ritualistic framing, capitalized abstract nouns), emit `voiceFrameContradictions` evidence. Two sub-categories: `banned-phrase-removal` (confidence 0.75, routes normally) and `voice-frame-rewrite` (confidence 0.65, ALWAYS staged by default). Opt-in to auto-write the voice-frame sub-category via `--apply-voice-frame-fixes`.

**`:remediate --auto-handoff-vibe-sec` flag.** v0.5 emitted a handoff banner when F12 critical fired. v0.6 adds opt-in auto-invocation: when the flag is set AND F12 critical fires AND `vibe-sec:audit` is available via the Skill tool, `:remediate` invokes vibe-sec with `--scope user-input-boundary` (falls back to full audit if the flag isn't accepted), captures findings + exit code, and writes the result to `.vibe-prompt/remediate/state/handoff-vibe-sec-<timestamp>.json`. If vibe-sec is not installed, falls back to v0.5 banner-only behavior and friction-logs `auto-handoff-vibe-sec-unavailable`. vibe-sec's findings do NOT merge into vibe-prompt's `audit.json` — concerns stay separate. The router surfaces the handoff result file on next `/vibe-prompt` invocation (branch `review-vibe-sec-handoff-results`).

**composer.json `global-directive` enum.** v0.5 emitted `directive-field` as the layer type for persona/master-directive content. v0.6 emits `global-directive` — clearer name, same semantics. `directive-field` remains accepted by the schema as a deprecated alias; existing composer.json files keep validating. No migration required.

**No breaking changes.** Every v0.5 artifact (composer.json, audit.json, remediate-result.json, pending-fix.diff front-matter, config.json) validates against v0.6 schemas. New fields are optional.

## Generalization completeness (v0.7)

v0.7 closes the four structural gaps the cross-app probe surfaced on 626Labs + WeSeeYou + Quiz Show against v0.6. No new commands. Six load-bearing additions, all aimed at making the plugin generalize cleanly across multi-composer / multi-call-site / shared-package / monorepo app shapes — without breaking single-composer apps like Celestia3.

**composers[] array + four kinds.** v0.6's `composer.json` carried a single top-level `layers[]` array — fine for Celestia3 (one composer file, one composition stack), wrong for apps that compose prompts in multiple places. v0.7 adds a top-level `composers[]` array; each entry carries its own `kind`, `path`, `layers[]`, `globalConfidence`, `regenerationSource`, and `apiParameterCompleteness`. Four kinds, one per topology:

- **single-composer** — one composer file, one composition stack. Canonical: Celestia3 `src/lib/gemini.ts`. Backward-compat shim: v0.6 composer.json (top-level `layers[]`, no `composers[]`) still validates and auto-promotes to `composers[0]` with `kind: "single-composer"` semantics; for single-composer apps v0.7 ALSO writes top-level `layers[]` so v0.6 consumers continue to read cleanly.
- **multi-composer** — two or more distinct composer files, each with its own composition stack. Canonical: 626Labs `galaxyCore.ts` (astrology persona) + `ChatController.ts` (general chat persona). Each composer entry tracked independently — audit iterates findings per composer, F12 fires deterministic per composer.
- **multi-call-site** — no canonical composer file; SDK calls scattered across N files inline. Canonical: WeSeeYou (six inline call sites, no central composer). Grouping heuristic: same-SDK + same-persona groups; differing personas don't. Each group becomes one composer entry; `path` is a string array listing every call site the group covers.
- **shared-package** — composer file lives in `packages/<name>/` and is referenced by multiple workspaces. Canonical: Quiz Show `packages/ai/src/gemini/GeminiService.ts` consumed by `apps/cinema`, `apps/hotel`, and `apps/reel-battles`. Tracked as one composer, but per-workspace inventories cross-reference it.

**Workspace-awareness for npm-workspaces + nested-projects.** v0.6 scanned the entire repo as one flat inventory. v0.7 detects the workspace topology and emits per-workspace inventories alongside a top-level aggregator. Four `workspaceKind` values: `npm-workspaces` (declared in root package.json `workspaces` array), `nested-projects` (no declaration but multiple nested package.json files), `single-workspace` (one package.json, no nesting), `unknown` (no package.json detected). For monorepos: each workspace gets `.vibe-prompt/state/inventory-<workspace-name>.json`; the top-level `inventory.json` becomes an aggregator that cross-references each via `workspaces[].inventoryFile` + carries a flat union of `prompts[]` with `workspaceIdentifier` per entry. Single-workspace apps emit only the top-level inventory (v0.6 shape preserved — no per-workspace files).

**Scan excludes for sub-projects.** Apps that vendor sub-projects (`vibe-doc/`, `GitNexus-main/`, `whiteboard-app/`) get noisy inventories under v0.6 — the scanner walks into nested repos it shouldn't. v0.7 reads `config.scan.excludes` (string array of glob patterns) and applies them during the walk. Auto-detects sub-project candidates matching `vibe-*/`, `*-main/`, `_ARCHIVE_*/`, `node_modules/`, `.git/`, `dist/`, `build/` and surfaces them via friction `scan-excludes-recommended-but-not-applied` (low) when not yet in config. The user owns the decision — excludes are load-bearing config, not auto-applied.

**Category D migration templates.** v0.5 + v0.6 covered three fix categories — A (composer-level additions), B (contradiction removal + voice-frame rewrites), C (defense addition). v0.7 adds three migration templates that close the structural gaps surfaced on multi-call-site apps:

- **D-1 inline-to-registry** — fires on F1 inline systemInstruction at call site. Generates a registry entry with auto-derived id + replaces the call site with `getPrompt(id)` invocation + injects the registry import if absent. Per-call-site independent (multiple D-1 diffs may exist for the same finding-id list). Default routing: stage; opt-in via `--apply-inline-to-registry` for auto-write at confidence ≥0.90.
- **D-2 typed-renderer** — fires on F4 raw `{{var}}` interpolation without typed renderer. Adds `requiredVars: string[]` field per registry entry + emits a `renderPrompt(id, vars)` helper that throws on missing var + updates all call sites to use the renderer. Default routing: stage; opt-in via `--apply-typed-renderer`.
- **D-3 model-consolidation** — fires on F6 with N occurrences of the same hardcoded model id across multiple files. Generates `src/config/ai.ts` (or app-conventional path) with `export const DEFAULT_MODEL = "<model-id>"` + replaces each occurrence with an import. Confidence default 0.88 — routes auto at the top end. For monorepo apps where models differ across workspaces, emits per-workspace config files. Opt-in via `--apply-model-consolidation` to lift D-3 routing from default-stage to confidence-routed.

**F12 severity-decoupling.** v0.6's F12 degraded from critical → high whenever composer-mimic confidence was low, even when the apiParameter detection was unambiguous. That conflated detection ambiguity with composition shape. v0.7 decouples them: if both composer layers have `apiParameter` populated with confidence ≥0.6, F12 stays critical regardless of how many composers exist or how confident the global composer detection was. apiParameter ambiguity on either layer (confidence < 0.6) is what degrades severity to high — composer multiplicity surfaces as `findings[].metadata.composerMultiplicityFlag` for context only, never as severity input. Positive signal `f12-severity-no-longer-degraded-by-composer-multiplicity` fires when v0.7 correctly keeps a finding at critical that v0.6 would have degraded.

**F6 suspect-model.** v0.4's F6 fired only on the deterministic hardcoded-model-id check. v0.7 adds a suspect-model sub-finding: when a prompt references a model id NOT in the bundled `known-models.md` list AND NOT in `config.audit.f6.modelIdExceptions`, F6 fires with severity medium. Confidence: high when context7 lookup confirms the id is not in the published model list; medium when context7 is unavailable (bundled-list-only). Canonical example: Quiz Show's `scripts/generate-trivia-pro.mjs:87` references `gemini-3.1-pro`, which doesn't exist — F6 suspect-model surfaces the candidate for user confirmation.

**Consolidated-diff routing for F10+F11(+F12-high).** v0.6 emitted one Category C diff per finding. When F10 + F11 (and optionally F12-high) all fire on the same call site, the user reviewed two or three diffs that all touched the same prompt. v0.7's `consolidation-rules.md` recognizes the overlap: F10's defense block is the structural change; F11's phrase count is satisfied by F10's contract; F12-high adds a commented note explaining the composition restructure deferral. Result: one consolidated Category C diff with `findingIds[]` referencing all consolidated findings. Tracked in top-level `consolidatedDiffs[]` in `remediate-result.json`. Does NOT apply when findings are on different call sites or when F12-critical fires (F12-critical needs the auto-handoff path, not Category C subsumption).

**F1 registry-kind awareness.** v0.6's F1 fired on any inline systemInstruction at a call site, regardless of what kind of registry the app had. That produced false positives on apps with `model-routing` registries (like 626Labs `config/modelRegistry.ts` — task-id → model-id mapping, not prompt-content). v0.7 gates F1 on `registry.kind === "prompt-content"` or `"hybrid"`. Apps with only `model-routing` or `task-mapping` registries get F1b instead (no prompt-content registry detected) — the smell is the absent registry, not the inline call. Eliminates the 626Labs false-positive cleanly.

**F12 absent-system-instruction sub-case.** v0.6's F12 required both a user-var layer and a system-instruction layer to compute the order check. WeSeeYou's badge-icon-generator has the user-var layer in `contents` but no system-instruction layer at all — v0.6 silently skipped the finding. v0.7 handles the absent-system-instruction sub-case: F12 still fires with severity high (degraded — no structural separation is possible when only one layer exists). Finding emits `apiParameterContext.absentSystemInstructionLayer: true` so the user sees why the severity is high rather than critical.

**Per-workspace composites.** Grade now partitions findings by `workspaceIdentifier` + computes one composite per workspace under `appComposite.perWorkspace[<name>]`. Aggregate composite (cross-workspace mean) preserved as `appComposite.aggregate` for v0.6 number-shape consumers. Single-workspace apps still emit `appComposite` as a flat number (no `perWorkspace` key — v0.6 shape preserved). Per-workspace monotonic baseline regression tracked separately from aggregate regression — Cinema's composite regressing doesn't block Hotel's monotonic ratchet.

**Three new remediate flags.** `--apply-inline-to-registry`, `--apply-typed-renderer`, `--apply-model-consolidation` lift Category D-1 / D-2 / D-3 routing from default-stage to normal (auto-write at confidence ≥0.90). Conservative-by-default — the user opts into each migration kind explicitly; first run on a new app stages everything for review.

**Router state branches grow 10 → 13.** Three new branches: `workspace-rescan-needed` (workspaceKind = npm-workspaces or nested-projects AND no per-workspace inventory files), `workspace-grade-needed` (per-workspace inventories exist AND no per-workspace composites), `category-d-pending-review` (pending Category D diffs in `.vibe-prompt/remediate/pending/`).

**No breaking changes.** Every v0.6 artifact (composer.json, inventory.json, audit.json, remediate-result.json, pending-fix.diff front-matter, grade-result.json, config.json) validates against v0.7 schemas. New fields are optional; backward-compat shims auto-promote single-composer / single-workspace shapes when read by v0.7-aware consumers.

## Self-evolution

All command skills invoke `session-logger` at start + end and `friction-logger` at the triggers in `friction-triggers.md`. `evolve-prompt` reads those logs and proposes changes — never auto-applies.
