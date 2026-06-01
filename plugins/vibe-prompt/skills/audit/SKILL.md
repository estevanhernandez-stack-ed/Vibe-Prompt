---
name: vibe-prompt:audit
description: This skill should be used when the user says "/vibe-prompt:audit", "audit my prompts", "what's wrong with my prompts", "find prompt smells", "structural prompt review", or wants a structural audit of LLM prompts in their app. Reads `.vibe-prompt/state/inventory.json` (required prerequisite — created by `/vibe-prompt:scan`), applies the F1-F12 rubric (all active in v0.4), writes `.vibe-prompt/state/audit.json` and a human-readable `docs/vibe-prompt/audit-YYYY-MM-DD.md`. Read-only — no source mutation.
---

# /vibe-prompt:audit

Load `vibe-prompt:guide` first. Then load `references/smell-rubric-f1-f13.md`, `references/audit-report-template.md`, `references/scoring-dimensions.md`, and `vibe-prompt:guide/references/calibration-patterns.md`.

Apply the F1-F12 rubric (F1-F9 active in v0.4; F10-F12 are Phase 4) to the cached inventory. Emit machine-readable findings + human-readable dated report.

## Inputs

- `.vibe-prompt/state/inventory.json` in the target app — REQUIRED.
- No flags in v0.1.

## Workflow

1. **Pre-flight.** Invoke `session-logger` start. Read `.vibe-prompt/state/inventory.json`. If missing, instruct the user to run `/vibe-prompt:scan` first and exit. Validate inventory against `plugins/vibe-prompt/schemas/inventory.schema.json` — if invalid, friction-log `inventory-schema-violation` and abort.
1b. **Per-composer iteration setup (v0.7).** Read `.vibe-prompt/eval/composer.json` if present. Build the composer-iteration set:
   - If composer.json has `composers[]` (v0.7 shape) with one or more entries → iterate composer-aware findings (F12 and any other findings that consult composition order or `apiParameter`) ONCE PER composer in `composers[]`. For each iteration, set the active composer's `layers[]`, `globalConfidence`, and the composer's `path` (or first path for multi-call-site groups whose `path` is an array of call-site paths).
   - If composer.json has no `composers[]` (v0.6 back-compat shape — only top-level `layers[]`) → run composer-aware findings ONCE as a single-composer iteration. Set `composerIdentifier: null` on emitted findings (back-compat signal for downstream consumers).
   - If composer.json is absent → composer-aware findings (F12) follow the existing absent-composer.json fallback (severity-degrade to high). `composerIdentifier: null` on emitted findings.
   - Findings emitted from a per-composer iteration carry `composerIdentifier` matching the active composer's path (or first path for multi-call-site groups). Non-composer-aware findings (F1, F1b, F3, F5, F6, F7, F9, F13) run once globally and emit `composerIdentifier: null` regardless.
2. **Apply rubric.** Walk `references/smell-rubric-f1-f13.md` in order F1 → F1b → F2 → F3 → F4 → F5 → F6 → F7 → F9 → F10 → F11 → F12 → F13. For each smell, run the detection rule against `inventory.json`. If it fires, build a finding object: `{ id, smell, severity, evidence[], recommendation, composerIdentifier }`. Use the recommendation template, filling in concrete values from inventory (file paths, IDs, counts). F11 and F12 are only evaluated when F10 has already fired on the same prompt (F10 is prerequisite). F13 is independent (static analysis on prompt content) and runs after F12. F10, F11, and F12 loop once per composer entry in step 1b's iteration set; each emitted finding's `composerIdentifier` matches the active composer's path.
2b. **F1 registry-kind gate (v0.7).** Before applying F1, inspect `inventory.registry.kind` (added in v0.7):
   - If `registry.kind === "prompt-content"` → F1 fires per its existing detection rule (registry detected AND inline prompts exist). Existing v0.6 behavior.
   - If `registry.kind === "hybrid"` → F1 fires (hybrid registries contain prompt-content; bypassing them is still the F1 smell).
   - If `registry.kind === "model-routing"` → F1 does NOT fire on this registry (model-routing is task-id → model-id mapping, not a prompt store; inline systemInstructions are NOT bypassing it). F1b fires instead (no prompt-content registry detected), treating the inline sites the same as an app with no registry at all. This closes the 626Labs false-positive surfaced in the v0.6 cross-app probe.
   - If `registry.kind === "task-mapping"` → F1 does NOT fire (task-mapping registries describe tasks but don't store prompt content). F1b fires if inline sites are abundant.
   - If `registry.kind` is undefined / null (v0.6 inventories before kind classification) → fall back to v0.6 behavior (F1 fires when `registry.detected === true` and inline prompts exist). Back-compat preserved.
3. **F2 semantic pass.** Voice-contradiction detection cannot run from inventory alone — it needs prompt content. Re-read each voice-bearing prompt's content from the target source. Compare global directive (if present in registry as a `*directive` / `*persona` entry) against each task prompt. Surface contradictions with specific file:line citations on BOTH the rule and the violation.
4. **F6 known-model lookup + suspect-model sub-finding (v0.7).** Compare each `modelIdentifiers[*].value` against the bundled list in `references/known-models.md`. Two paths:
   - **F6 (consolidation):** existing v0.6 behavior — fires when `occurrences.length >= 2` (consolidate duplicates).
   - **F6-suspect-model (v0.7 revival):** fires when a model id is NOT in `references/known-models.md` AND NOT in `config.audit.f6.modelIdExceptions[]`. Build finding `{ id: "F6-suspect-model", severity: "medium", evidence: { modelValue, occurrences[], lookupResult, listLastUpdated }, recommendation: "<verify against vendor's current published model list>" }`.
   - **Confidence ladder for F6-suspect-model:**
     - **High** — context7 lookup succeeded AND vendor's published-models list does NOT contain the id (vendor-confirmed not-in-published-list).
     - **Medium** — context7 unavailable; only the bundled list was consulted. Add "verify manually" to recommendation.
   - **Escape hatch:** entries listed in `config.audit.f6.modelIdExceptions[]` are NEVER flagged by F6-suspect-model, even if missing from the bundled list (intentional pre-release / vendor-internal ids).
4b. **F9 date-grounding check.** For each prompt in inventory (registry entries + inline prompts):
   - **Step A — Date-intent match:** scan the prompt's content + any `templatedVars` entries. Check for:
     - Keyword regex: `\b(?:birth ?date|birthday|birth ?day|transit|natal|nativity|current|today|now|year|month|age|when)\b` (case-insensitive)
     - Templated date vars: matches `{{[^}]*[Dd]ate[^}]*}}`, `{{[^}]*[Dd]ob[^}]*}}`, or `{{[^}]*[Bb]irth[^}]*}}`
     - If step A produces no match, skip this prompt for F9.
   - **Step B — Composition-stack temporal anchor:** inspect the composition stack (global directive from composer.json or inventory + this prompt's content + any wrapping layers). Check for:
     - Literal markers: `[CURRENT DATE]`, `[TODAY]`, `[NOW]`, `[CURRENT_TIMESTAMP]`
     - Phrase markers (case-insensitive): `today is`, `current date`, `as of`
     - Injected templated date vars at the global layer (composer-mimic already identifies these layers)
   - **Fire when:** step A matched AND step B found nothing. Build finding `{ id: "F9", severity: "high", evidence: { promptId, promptLocation, dateKeywords[], compositionStackLocation }, recommendation: <template from rubric> }`.
   - **Confidence degrade:** if composer-mimic confidence is < 0.6 for this app (check `.vibe-prompt/eval/composer.json` `confidence` field if available), set severity to `"medium"` instead of `"high"` and add `"composition stack detection low-confidence; verify manually"` to evidence.
   - **False-positive escape:** if `--ignore-finding F9 --on-prompt <id>` was passed in the CLI flags, skip F9 for that specific prompt id.
4c. **F10 user-input-var detection.** For each prompt in inventory:
   - **v0.5 origin pre-filter (additional pre-step, does not replace v0.4 detection).** Before applying the user-origin heuristic regex, filter `templatedVars[]` to only those with `origin === "user-controlled"` (or `origin === "unknown"` — the conservative default per spec §3). Skip any var whose `origin === "system-injected"`. For each skipped candidate, annotate the audit's `findings[]` (or the per-prompt skip log) with `originFilteredOut: true` and `varOriginUsed: "system-injected"` so the dashboard can show which vars were considered but excluded. Honor the user's `.vibe-prompt/config/var-origins.json` overrides (per spec §3) before applying the heuristic. Note: a finding with `originFilteredOut: true` indicates a candidate var was excluded — it does NOT mean a real F10 fired. The annotation is informational.
   - **User-var detection (v0.4 behavior, preserved):** scan the post-filter `templatedVars` set for names matching user-origin heuristics:
     - Exact: `userInput`, `userMessage`, `userQuery`, `userText`, `userContent`, `userPrompt`, `userData`, `userBio`, `userDescription`, `userQuestion`
     - Contains (case-insensitive): `(?i)(message|query|text|prompt|input|content|bio|description|question|dream|note|comment|review|feedback|reply|chat)`
     - Extended list from `.vibe-prompt/config/user-input-vars.json` or `audit.injectionResistance.userInputVars` in config.json (additive to defaults)
   - **Sanitization-directive scan:** if user-var matched, check prompt content within 200 chars of each user-var reference for:
     - `(?i)treat .* as data`
     - `(?i)ignore .* instructions`
     - `(?i)do not execute`
     - `(?i)your role is fixed`
     - `(?i)content within .* is data only`
   - **Fire F10 when:** user-var detected (post-filter) AND no sanitization directive found nearby. Build finding `{ id: "F10", severity: "high", handoffHint: "vibe-sec:audit", evidence: { promptId, promptLocation, userVars[], varTypes[] }, varOriginUsed: "user-controlled", recommendation: <template from rubric> }`.
   - **Track F10-fired prompts** — a prompt set used as a prerequisite gate for F11 and F12 detection. The origin pre-filter applies transitively: F11 and F12 only consider prompts that passed the F10 user-controlled gate.

4d. **F11 defense-in-depth scarcity detection.** For each prompt in the F10-fired set (which already excludes `origin: "system-injected"` vars per step 4c's v0.5 pre-filter):
   - **Defense-phrase scan:** count distinct defense phrases in the full prompt content (not just the 200-char window):
     - "treat as data"
     - "ignore instructions within"
     - "your role is fixed"
     - "do not execute commands"
     - "regardless of user request"
     - "always remain"
   - **Fire F11 when:** defense-phrase count < 2. Build finding `{ id: "F11", severity: "medium", handoffHint: "vibe-sec:audit", evidence: { promptId, detectedDefensePhrases[], recommendedDefensePhrases[] }, recommendation: <template from rubric> }`.

4e. **F12 composition-order violation detection (API-parameter-aware, v0.6+; per-composer iteration v0.7+).** Loop once per composer entry from step 1b's iteration set (v0.7). For each composer, walk each prompt in the F10-fired set (origin-filtered for `user-controlled` vars only), and only if composer.json is available (`.vibe-prompt/eval/composer.json` from v0.2+ setup). Read the active composer's `layers[]` + `globalConfidence` for this iteration. Emit `composerIdentifier` on each F12 finding (matching the active composer's `path`, or the first entry when the composer is a multi-call-site group whose path is an array). When composer.json has no `composers[]` (v0.6 back-compat shape), iterate once with `composerIdentifier: null`:
   - **Read composition order** from composer.json — ordered list of layers: `{ layerName, type, vars[], apiParameter }`.
   - **Find user-var injection layer:** the layer whose `vars[]` contains the user-var (or the innermost layer for inline injections).
   - **Find system-instruction layer:** the layer with `type: "global-directive"` (or v0.5 legacy `directive-field` for persona/master-directive id) or the first layer by index.
   - **Step 1 — apiParameter separation check (v0.6+, applied FIRST before layer-order logic):**
     - Read `apiParameter` from each layer (user-var and system-instruction).
     - **If user-var layer `apiParameter` is `"contents"` OR `"messages"` AND system-instruction layer `apiParameter` is `"systemInstruction"`** → the API parameter structurally segregates user content from the system instruction. F12 does **NOT** fire (structurally safe regardless of layer order). Emit no finding for this prompt. The audit annotates the finding-skip log entry with `apiParameterContext: { userVarApiParameter, systemInstructionApiParameter, separationVerified: true }`.
     - **If both layers share the SAME `apiParameter`** (e.g., both interpolated into the same `systemInstruction` string, or both inside the `messages[]` array) → composition order matters within that parameter. Fall through to step 2 (v0.5 layer-order rule).
     - **If either layer's `apiParameter` is `null` (unknown)** → API-parameter check is inconclusive. Fall through to step 2 but mark severity for confidence-degrade per step 3 below.
   - **Step 2 — Fire F12 when:** user-var layer index ≤ system-instruction layer index AND step 1 did not declare structural safety. Build finding `{ id: "F12", severity: "critical", handoffHint: "vibe-sec:audit", evidence: { promptId, userVar, userVarLayer, systemInstructionLayer, compositionOrder[] }, apiParameterContext: { userVarApiParameter, systemInstructionApiParameter, separationVerified: false }, recommendation: <template from rubric> }`.
   - **Step 3 — Confidence degrade (v0.7 decoupled from composer multiplicity).** Severity degrades from `critical` to `high` ONLY on **detection ambiguity** — composer-multiplicity by itself is NOT a severity input. Severity stays critical when apiParameter is unambiguous on all relevant layers, even when the app is multi-composer / multi-call-site. Severity degrades to `high` when ANY of:
     - **Per-layer apiParameter confidence < 0.6** on the user-var layer OR the system-instruction layer (`apiParameterConfidence` field on the active composer's layer)
     - **Either layer's `apiParameter` is `null`** (unknown destination — v0.6 fallback path preserved)
     - **composer.json is absent**
     - Active composer's `globalConfidence` < 0.6 — but only when that confidence reflects detection uncertainty on the layers being inspected, not multiplicity-induced confidence dilution.
   - **Multiplicity flag (v0.7, context only):** when the active composer is part of a multi-composer / multi-call-site / shared-package shape, emit `metadata.composerMultiplicityFlag: true` on the finding for downstream consumers. This is informational — multiplicity is **not** a severity input.

4f. **F13 implicit output format detection (v0.6, static — no LLM).** For each prompt in inventory (registry entries + inline prompts):
   - **Read F13 exception list:** load `audit.f13.outputFormatExceptions` (string array) from config. If the prompt's id appears in this array, **skip F13 for that prompt** (user has acknowledged intentional flexible output).
   - **Step A — Structural-cue match.** Scan prompt content for at least ONE of:
     - `[BRACKETS]` blocks — regex `\[[A-Z_]+\]` (one or more uppercase + underscore tokens inside square brackets). Match → cue label `"BRACKETS-blocks"`.
     - `{{var}}` templated sections — count occurrences of `{{...}}` in the prompt content; match when count > 2 (more than 2 occurrences in the same prompt). Match → cue label `"templated-vars-3x"`.
     - JSON-like data sections — regex matching JSON-shape: either `^\s*\{[^}]*\}\s*$` (a `{...}` block on its own line) OR `: "[^"]+"` repeated 3+ times in the prompt content. Match → cue label `"json-shaped-data"`.
   - **Step B — Output-format declaration absence.** Scan prompt content for ANY of (case-insensitive where noted):
     - `[OUTPUT FORMAT:` (case-insensitive)
     - `[OUTPUT_SCHEMA]` block marker
     - `Respond in JSON` / `Return JSON` / `JSON output` (explicit structured-output declarations)
     - `prose only` / `no JSON` / `narrative response` (explicit prose declarations)
     - `[OUTPUT FORMAT: flexible]` (explicit flexible-output suppression)
   - **Fire F13 when:** Step A matched AND Step B found NONE of the declarations (i.e., absence is total). Build finding `{ id: "F13", severity: "medium", evidence: { promptId, promptLocation, detectedCues: [<cue labels>], missingDeclarations: [<list of declarations looked for but not found>] }, recommendation: <template from rubric §F13> }`.
   - **F13 is independent of F10/F11/F12** — runs on every prompt regardless of user-var presence. Its concern is output-shape ambiguity, not injection surface.

5. **Compose summary.** Count findings by severity → `summary.byCategory`. Total → `summary.totalFindings`.
6. **Compute per-prompt scores.** Per `references/scoring-dimensions.md` and the Score impact sections in `references/smell-rubric-f1-f13.md`:
   - For each prompt in inventory, start each dimension (schemaTightness, personaConsistency, instructionClarity, tokenEfficiency, injectionResistance) at 10.
   - For each fired finding that targets this prompt, apply its Score impact deductions to the affected dimensions.
   - Floor each dimension at 1 (no dimension goes below 1).
   - Compute per-prompt composite: weighted average of the 5 dimension scores. Default equal weights (0.20 each, v0.4). Check `.vibe-prompt/grade/weights.json` for user overrides; apply if present. Auto-normalize if weights don't sum to 1.0.
   - Write all per-prompt dimension scores + composite to `audit.json`'s `auditGrade.perPrompt` map.
   - Compute `auditGrade.appComposite` as the average of all per-prompt composites.
7. **Check for agent-suggested weight overrides.** Heuristics per `references/scoring-dimensions.md` Agent-suggested weight overrides section:
   - If 4+ prompts in the inventory have F2 (voice contradiction) findings → suggest weighting persona-consistency at 2× the base weight.
   - If 4+ prompts have schema-related findings (F1b or F4) → suggest weighting schema-tightness at 2×.
   - If average prompt token count across the inventory exceeds 4000 tokens → suggest weighting token-efficiency at 2×.

7b. **App-type heuristic for injectionResistance weight override.** Classify the app type to determine whether injectionResistance deserves adjusted weight. Detection sources (all optional; use what's present):
   - Read `.vibe-prompt/iterate/domain.json` if present (v0.3 artifact — check `appType` or `userInteraction` fields)
   - Read the app's `CLAUDE.md` (if present) — look for signals like "user input", "user message", "accepts", "chat", "prompt from user"
   - Count user-input vars found across the full inventory (F10 detection results): 3+ user-input vars across prompts is a consumer signal
   - Classify as:
     - **consumer**: domain.json says consumer/user-facing, OR CLAUDE.md mentions user-input patterns, OR 3+ user-input vars found
     - **internal**: domain.json says internal/curated/no-user-input, AND no user-input vars found
     - **mixed**: signals conflict or unclear
   - Append a `suggestedWeightOverrides` entry per the heuristics in `references/scoring-dimensions.md` (consumer → 0.40 / 0.15×4; internal → 0.10 / 0.225×4; mixed → default 0.20 / 0.20×4). Include `appTypeSignal` and `rationale` fields.
   - Combine all triggered suggestions (steps 7 + 7b) into a single AskUserQuestion. If accepted, write the confirmed weights to `.vibe-prompt/grade/weights.json` and recompute all per-prompt composites and appComposite with the new weights before writing audit.json.
8. **Write audit.json.** Atomic write to `.vibe-prompt/state/audit.json`. Validate against schema before write.
9. **Render report.** Apply `references/audit-report-template.md` to write `docs/vibe-prompt/audit-{YYYY-MM-DD}.md` in the target app. Date is today's date in the target's local time zone — but use UTC YYYY-MM-DD for the filename to keep ordering stable.
10. **Render banner.** ≤ 25 lines. Includes finding count by severity, the highest-severity finding's one-liner, the report path, the next recommended step.
11. **Post-flight.** `session-logger` terminal entry.

## Banner template

```
═══ Vibe-Prompt audit ═══
Findings:   7 total
  High:     4 (F1, F2, F4, F6)
  Medium:   2 (F3, F7)
  Low:      1 (F5)

Headline:   Registry exists but 10 inline sites bypass it (F1, high)
Report:     docs/vibe-prompt/audit-2026-05-28.md
State:      .vibe-prompt/state/audit.json

Suggested first move: F6 verify-model (cheapest, highest signal).
```

## Friction triggers

See `friction-triggers.md`. Highlights:
- `f6-suspect-model-detected` — high confidence
- `f2-contradiction-cross-file-attempted` (when v0.1 1-hop trace surfaced what looks like a deeper conflict but couldn't resolve it) — medium
- `rubric-default-recommendation-felt-generic` (heuristic — the agent's own read of whether the recommendation it just emitted is specific enough)

## Never

- Run any prompt.
- Re-scan from within audit. Audit reads cached inventory; scan owns inventory.
- Modify source.
