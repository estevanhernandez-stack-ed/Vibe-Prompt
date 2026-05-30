# Changelog

## [0.6.0] — 2026-05-29

Five additive capabilities organized around the "detection sharpness" theme. No breaking changes to v0.5 commands or surface area.

### Added

- **F12 API-parameter-aware detection.** F12's layer-order comparison now reads a new `apiParameter` field per composer layer and emits a deterministic verdict — F12 only fires critical when user-var and system-instruction layers share the same API parameter (e.g., both interpolated into `systemInstruction:`). When the API surface segregates them (user content in `contents[]` or `messages[]`, system instructions in `systemInstruction:`), F12 does NOT fire — composition order is structurally safe. When `apiParameter` is `null` (unknown), F12 confidence-degrades to severity `high` per v0.5 fallback. The audit finding records the analysis in a new `apiParameterContext` field describing the separation reasoning.

- **F13 — Implicit output format.** New static finding. Detection rule: prompt content contains at least one structural cue (`[BRACKETS]` blocks regex `\[[A-Z_]+\]`, 3+ `{{templated}}` vars in the same prompt, JSON-like data sections) AND the prompt content does NOT contain any output-format declaration (`[OUTPUT FORMAT:`, `[OUTPUT_SCHEMA]`, `Respond in JSON`, `prose only`, `narrative response`, etc.). Severity: medium. Score impact: `schema-tightness −2`, `instruction-clarity −1`. No LLM call. Suppressed by explicit `[OUTPUT FORMAT: flexible]` directive or by adding the prompt id to `audit.f13.outputFormatExceptions` config. Evidence includes `detectedCues[]` and `missingDeclarations[]` arrays.

- **Category B voice-frame depth.** `:remediate`'s Category B contradiction-removal now detects voice-frame phrase clusters in task prompts that contradict the global directive's voice rules — beyond direct banned-phrase matches. Voice-rule extraction parses the global directive for both explicit bans (`(?i)never (use|say|call|address)`, `(?i)not (a|the) X`, `(?i)avoid X`) and persona affirmations that imply bans (`plain modern language` → bans archaic; `contractions` → bans formal; `warm friend` → bans formal-priest). Voice-frame phrase patterns match archaic vocabulary, ritualistic framing, and capitalized abstract nouns. Emitted with `subCategory: "voice-frame-rewrite"`, confidence 0.65, ALWAYS staged by default. The audit finding records voice-frame contradictions in a new `voiceFrameContradictions[]` array.

- **`/vibe-prompt:remediate --auto-handoff-vibe-sec` flag.** Opt-in: when set AND F12 critical fires AND vibe-sec is installed, `:remediate` invokes `/vibe-sec:audit --scope user-input-boundary` and captures the result to `.vibe-prompt/remediate/state/handoff-vibe-sec-<timestamp>.json`. Falls back to v0.5 banner-only behavior with friction-log `auto-handoff-vibe-sec-unavailable` when vibe-sec isn't installed. Cross-plugin coordination without merging concerns — vibe-sec findings stay separate; vibe-prompt orchestrates only.

- **`/vibe-prompt:remediate --apply-voice-frame-fixes` flag.** Opt-in: when set, voice-frame Category B diffs follow normal routing (auto-write at ≥0.90, stage at 0.70-0.89). Without the flag, voice-frame diffs ALWAYS stage regardless of confidence — voice-drift risk requires human review by default.

- **composer.schema `global-directive` enum.** Layer type enum extends to include `global-directive`. `:first-run-setup` detection now emits `global-directive` for persona/master-directive layers (was `directive-field` in v0.5). `directive-field` remains a deprecated alias and continues to validate against the schema — old composer.json files don't break. Schema emits a warning when `directive-field` is used.

- **Router state branch: `review-vibe-sec-handoff-results`.** Bare `/vibe-prompt` router detects `.vibe-prompt/remediate/state/handoff-vibe-sec-*.json` files and routes to the new branch with a summary of vibe-sec findings + next-action menu.

- **7 new friction triggers:** `f12-api-parameter-detection-low-confidence` (medium), `auto-handoff-vibe-sec-completed` (positive), `auto-handoff-vibe-sec-unavailable` (medium), `f13-fired-but-prompt-intentionally-flexible-output` (low), `f13-recommended-fix-applied-and-eval-confirms-output-stability` (positive), `category-b-voice-frame-detection-confidence-low` (medium), `category-b-voice-frame-rewrite-rejected` (low). Each maps to a concrete handler template in `evolve-prompt/SKILL.md`.

### Changed

- `:audit` F12 detection checks `apiParameter` first; falls through to v0.5 layer-order check only when `apiParameter` is shared or unknown.
- `:audit` produces F1-F13 (was F1-F12 in v0.5).
- `:remediate` Category B splits into two sub-categories: `banned-phrase-removal` (confidence 0.75, normal routing) and `voice-frame-rewrite` (confidence 0.65, always staged unless `--apply-voice-frame-fixes`).
- `:first-run-setup` composer detection traces each layer's destination API parameter and emits `apiParameter` + `apiParameterConfidence` per layer.
- `:first-run-setup` emits `global-directive` for persona/master-directive layers instead of `directive-field`.
- `audit/references/smell-rubric-f1-f12.md` renamed to `smell-rubric-f1-f13.md` with F13 section added.
- Guide SKILL adds "Detection sharpness (v0.6)" section.
- Audit report template renders F13 findings, `apiParameterContext` on F12 findings, and `voiceFrameContradictions[]` on voice-frame Category B findings.

### Schema changes

- **NEW: `handoff-vibe-sec.schema.json`** — records `runId`, `timestamp`, `triggeringFinding`, `vibeSecVersion`, `vibeSecFindings[]`, `exitCode`, `scope`.
- `composer.schema.json` — `layers[].apiParameter` enum (`systemInstruction` | `contents` | `messages` | `instructions` | `prompt` | `null`), `layers[].apiParameterConfidence` number 0-1, layer `type` enum extended with `global-directive` (`directive-field` deprecated but still validates).
- `audit.schema.json` — `findings[].id` enum extended to F13; `findings[].apiParameterContext` optional object (`{userVarApiParameter, systemInstructionApiParameter, separationVerified}`); `findings[].voiceFrameContradictions[]` optional array (`{phrase, location, banSource}`).
- `remediate-result.schema.json` — `appliedDiffs[].subCategory` optional string; `f12HandoffsEmitted[].autoHandoffInvoked` optional boolean; `f12HandoffsEmitted[].vibeSecResultPath` optional string.
- `pending-fix.schema.json` — `findingCategory` enum gains documented sub-category notation (`B-voice-frame` valid alongside A/B/C); `voiceFrameRewriteRationale` optional string.
- `config.schema.json` — `remediate.autoHandoffVibeSec` boolean (default false); `remediate.applyVoiceFrameFixes` boolean (default false); `audit.f13.outputFormatExceptions` string array.

### Migration notes

- **No breaking changes.** All v0.5 commands, schemas, and state files remain valid.
- **v0.5 composer.json continues to validate** against the v0.6 schema. `apiParameter` is optional; layers without it are treated as `null` (unknown), which makes F12 detection confidence-degrade per v0.5 fallback. Re-run `:first-run-setup --regenerate-composer` to populate `apiParameter` and unlock deterministic F12 verdicts.
- **`directive-field` layer type is deprecated but still validates.** Existing composer.json files using `directive-field` continue to work; the schema emits a warning. New emissions use `global-directive`.
- **v0.5 audit.json continues to validate.** Findings without `apiParameterContext` or `voiceFrameContradictions` are treated as v0.5-era — no migration required.
- **`--auto-handoff-vibe-sec` and `--apply-voice-frame-fixes` are opt-in.** Default `:remediate` behavior is identical to v0.5 (banner-only handoff on F12 critical; voice-frame fixes always staged).
- **F13 detection is automatic** on next `:audit` run. To suppress per-prompt: add prompt id to `audit.f13.outputFormatExceptions` in config, or add explicit `[OUTPUT FORMAT: flexible]` directive to the prompt content.

---

## [0.5.0] — 2026-05-29

Four additive capabilities, organized around closing the audit → fix loop. No breaking changes to v0.4 commands or surface area.

### Added

- **`/vibe-prompt:remediate` — new sixth step-command (headline).** Closes the audit → fix loop. Reads latest `audit.json` + composer.json + inventory, groups findings into three fix categories, scores each proposed diff on a 5-dimension confidence rubric, and routes by threshold. Backups + atomic rollback supported. F12 critical findings emit a cross-plugin handoff banner to `/vibe-sec:audit` rather than auto-proposing — composition-order belongs upstream of the prompt.
  - **Category A — composer-level additions** (default 0.92 confidence). One file, pure addition between named sections, no semantic edits. Maps F9 date-grounding to a master-directive injection. Floors at 0.80 if composer.json absent or layer confidence < 0.6.
  - **Category B — contradiction removal** (default 0.75 confidence). One registry entry or inline prompt; locate-and-rephrase against a banned-phrase list pulled from F2 detection. Stages by default (voice drift risk); auto-bumps registry minor version. Floors at 0.50 when the banned phrase appears > 3 times.
  - **Category C — defense addition** (default 0.88 on contract paragraph, 0.78 on delimiter placement). Adds a defense block before user-input vars + a structural delimiter around the user var. Maps F10, F11, and F12 (when the fix is additive rather than restructuring). Delimiter name derived from var name (`dreamText` → `DREAM`, etc.).
  - **Confidence rubric:** locate (0.30) + diff-shape (0.25) + voice-risk (0.20) + schema-impact (0.15) + version-bump (0.10). Routing: ≥0.90 auto-write, 0.70-0.89 stage, <0.70 inline-only. User overrides at `.vibe-prompt/config/remediate-thresholds.json`.
  - **State layout:** `.vibe-prompt/remediate/pending/<finding-id>.diff` (staged fixes with YAML front-matter + unified-diff body), `.vibe-prompt/remediate/backup/<ISO-timestamp>/` (pre-apply file backups), `.vibe-prompt/remediate/state/runs.jsonl` (append-only ledger).
  - **Flags:** `--apply-pending <findingId>`, `--reject-pending <findingId>`, `--rollback <ISO-timestamp>`, `--interactive`, `--auto-apply`, `--skip-f12`, `--apply-contradictions`.

- **Inventory scan completeness — three new inline-prompt detection patterns.** `:scan` now detects template-literal `${var}` interpolations, string concatenation with user-controlled variables, and JSX template attributes alongside existing `{{handlebars}}` detection. Each templated var carries `source` (handlebars | template-literal | concat | jsx-attr) and `declaredAt` line reference. Closes the v0.4 gap that hid Oneirocriton's `dreamText` var from F10 detection.

- **System-injected var detection.** `:scan` now classifies each templated var by origin (`user-controlled` | `system-injected` | `unknown`) using two signals: a naming heuristic (high confidence) and call-graph proximity (medium confidence, with conservative fallback to user-controlled when unknown). `:audit` reads the origin field and filters F10/F11/F12 to user-controlled vars only. Findings record `originFilteredOut: true` when a candidate var was excluded due to system-injected detection. Closes the v0.4 false positive on arithmancy's `{{knowledgeContext}}`. Config override at `.vibe-prompt/config/var-origins.json`.

- **composer.json auto-generation in `:first-run-setup`.** First-run setup now detects composer files (filename heuristics: `gemini.ts`, `openai.ts`, `anthropic.ts`, `llm.ts`, `ai.ts`, `chat.ts`; plus SDK import detection for `@google/genai`, `@anthropic-ai/sdk`, `openai`), traces composition layers, classifies each layer (global-directive | format-directive | knowledge-context | task-instruction | user-data), and emits composer.json with per-layer `confidence` + `globalConfidence` + `regenerationSource` enum (manual | auto-detected | hybrid). Confidence floor: emit `confidence: 0.4` and prompt user to verify manually when fewer than 2 layers resolve. Re-runnable via `:first-run-setup --regenerate-composer`. Enables full-confidence Category A fixes and full critical severity on F12.

- **4 new friction triggers:** `staged-fix-applied-and-eval-confirms-improvement` (positive), `staged-fix-rejected` (medium), `auto-write-rolled-back` (high), `composer-auto-generation-confidence-low` (medium). Each maps to a concrete handler template in `evolve-prompt/SKILL.md`.

### Changed

- `:audit` F10/F11/F12 detection filters by var origin — only `user-controlled` and `unknown` vars trigger findings. `system-injected` vars are excluded with `originFilteredOut: true` recorded.
- `:scan` inventory output now includes `source` + `declaredAt` + `origin` + `originConfidence` per templated var.
- `:first-run-setup` runs composer auto-generation when `.vibe-prompt/composer.json` is absent on first command.
- Router (bare `/vibe-prompt`) extended with `review-pending-remediations` state branch — fires when `.vibe-prompt/remediate/pending/` is non-empty.
- Guide SKILL updated with v0.5 remediate overview.
- Audit scoring-dimensions reference notes that `injectionResistance` is filtered after origin detection.

### Schema changes

- **NEW: `remediate-result.schema.json`** — runId, timestamp, auditRunId, totalFindings, diffsByCategory (A/B/C counts), appliedDiffs[], stagedDiffs[], inlineOnlyDiffs[], f12HandoffsEmitted[], backupBatchPath.
- **NEW: `pending-fix.schema.json`** — YAML front-matter validation for staged `.diff` files (findingId, findingCategory, confidence, targetFile, targetRange, backupPath, recommendationSource, postApplyRecommendation, versionBumpRequired, suggestedVersion).
- `inventory.schema.json` — `inlinePrompts[].templatedVars[]` extended with `source` enum, `declaredAt` line ref, `origin` enum, `originConfidence` 0-1 number.
- `composer.schema.json` — `layers[].confidence` per-layer, `globalConfidence`, `regenerationSource` enum.
- `audit.schema.json` — `findings[].originFilteredOut` boolean, `findings[].varOriginUsed` reference to origin classification used.
- `config.schema.json` — `remediate.autoApplyThreshold` (default 0.90), `remediate.stageThreshold` (default 0.70), `remediate.backupRetentionDays` (default 30), `audit.varOriginOverrides` (object).

### Migration notes

- **No breaking changes.** All v0.4 commands, schemas, and state files remain valid.
- **v0.4 inventory.json continues to validate.** `{{handlebars}}` vars stay as string-only entries with no `source` / `origin` fields. v0.5 scan re-run normalizes existing entries to include the new fields.
- **v0.4 audit.json continues to validate.** Findings without `originFilteredOut` are treated as unfiltered (no `system-injected` detection was applied). v0.5 audit re-run writes the new fields.
- **composer.json from v0.4 is read as `regenerationSource: "manual"`** if the field is missing. Per-layer confidence defaults to 1.0 when absent (treats existing entries as authored).
- **`:remediate` is opt-in.** Existing v0.4 workflows that stop at `:grade` are unchanged.
- **Auto-write is gated.** Default `:remediate` behavior stages all fixes. Auto-write only triggers with `--auto-apply` flag.

---

## [0.4.0] — 2026-05-29

Three additive capabilities. No breaking changes to v0.3 commands or surface area.

### Added

- **F9 — Date-grounding static check.** Fires on prompts that handle date-related inputs (birth dates, transit windows, current time references) but lack a temporal anchor in the composition stack. Detection is keyword regex + templated var names; no LLM call. Severity: high. Score impact: instruction-clarity −3, schema-tightness −1.

- **value-type-drift mechanical check.** New check in the eval mechanical comparator (between schema-shape and length-delta). Catches when a key's value type in prod or baseline output differs from the OUTPUT_SCHEMA declaration, even when the key is present. Covers the case that keyword-set checks pass but value shape doesn't (e.g., Gemini emitting `array<object>` when schema declares `string`). Fires `value-type-drift` or `value-type-drift-both` (both outputs differ from declared type).

- **Prompt-injection vulnerability grading.** Fifth scoring dimension (`injectionResistance`, 1-10, default weight 0.20) + three new audit findings + active inject-attack eval mode:
  - **F10 (high)** — user-input var without sanitization directive. Score impact: injectionResistance −4, instruction-clarity −1.
  - **F11 (medium)** — defense-in-depth scarcity (< 2 defense phrases when user-input var detected). Score impact: injectionResistance −2.
  - **F12 (critical)** — user-var injection layer at or before system-instruction layer in composer order. Score impact: injectionResistance −6, persona-consistency −2. Severity degrades to `high` when composer-mimic confidence < 0.6.
  - **F10, F11, F12** all carry `handoffHint: "vibe-sec:audit"` for cross-plugin app-level review.
  - **`--inject-attacks` eval flag** — after the standard prod + baseline + judge pipeline, substitutes 6 canonical injection patterns (direct-override, role-assertion, role-flip, instruction-deflection, trust-manipulation, encoded-payload) into each user-input var. Binary LLM-judge determines honor-vs-resist per fixture. Results in `injectAttackResults` + `injectAttackSummary`. Cost-gated; estimated cost shown before running ($0.001/fixture pair, typically <$0.01 for cowpath scope).
  - **App-type weight heuristic** — audit detects consumer-facing apps and suggests `injectionResistance` weight 2× (consumer) or 0.5× (internal). Advisory; confirmed before write.
  - **Router v0.4 branch** — bare `/vibe-prompt` router detects non-empty `injectAttackResults` in latest eval state and surfaces attack summary + next-action menu (review fixtures, dispatch evolve-prompt, run vibe-sec handoff).

- **4 new friction triggers:** `injection-attack-succeeded` (high), `f9-fired-but-prompt-already-has-date-grounding` (low), `value-type-drift-fired-but-types-are-compatible` (low), `injection-resistance-dimension-flat-across-prompts` (medium). Each maps to a concrete handler template in `evolve-prompt/SKILL.md`.

### Changed

- `:audit` now applies F1-F12 (was F1-F7 in v0.3, F1-F9 partially in interim builds).
- Per-prompt scoring extended from 4 dimensions to 5 (adds `injectionResistance`). Audit report template adds `InjectionRes` column.
- `:eval` mechanical comparator adds value-type-drift check between schema-shape and length-delta sections.
- Guide SKILL adds "Prompt-injection vulnerability grading (v0.4)" section covering the full F10-F12 family, eval mode, handoff, and weight heuristic.
- Audit report template updated: 5-column per-prompt scores table, F9-F12 render templates, cross-plugin handoff note in recommended-sequence section.
- Router extended with branch 3b (review-injection-attack-results).
- smell-rubric renamed `smell-rubric-f1-f7.md` → `smell-rubric-f1-f12.md` (done in earlier phases).

### Schema changes

- `audit.schema.json` — `findings[].id` enum extended to F9-F12; `findings[].handoffHint` optional string; `auditGrade.perPrompt.dimensions.injectionResistance` added; `auditGrade.suggestedWeightOverrides[]` extended with `rationale` and `appTypeSignal`.
- `run-result.schema.json` — `injectAttackResults` (optional array) + `injectAttackSummary` (optional object) added; `evalGrade.dimensions.injectionResistance` added; mechanical-finding `category` enum extended with `value-type-drift` + `value-type-drift-both`.
- `grade-result.schema.json` — `perPrompt.composite.dimensions` + `perPrompt.composite.weights` + `appComposite.dimensions` extended with `injectionResistance`.
- `baseline.schema.json` — `perPrompt.bestScores.injectionResistance` added.
- `config.schema.json` — `eval.injectAttack.*` section added (enabled, fixtures, costCeiling); `audit.injectionResistance.userInputVars` extension point added.
- `inject-attack-fixture.schema.json` — NEW schema (6-field fixture definition).

### Migration notes

- **No breaking changes.** All v0.3 commands, schemas, and state files remain valid.
- **4-dimension `weights.json` files auto-normalize to 5 dimensions.** Existing `.vibe-prompt/grade/weights.json` with 4 dimension entries (summing to 1.0) are automatically extended: the agent distributes the 5th dimension weight (0.20) by proportionally reducing the other four. No manual update needed. The first `:grade` run after upgrade writes the normalized 5-dim weights.
- **`injectionResistance` column is omitted for pre-v0.4 state files.** If `audit.json` has no `injectionResistance` in `auditGrade.perPrompt.dimensions`, the audit report renders `—` in that column. No error.
- **`--inject-attacks` is opt-in.** Existing `:eval` invocations without the flag are unchanged.

---

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
