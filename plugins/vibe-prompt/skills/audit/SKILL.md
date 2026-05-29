---
name: vibe-prompt:audit
description: This skill should be used when the user says "/vibe-prompt:audit", "audit my prompts", "what's wrong with my prompts", "find prompt smells", "structural prompt review", or wants a structural audit of LLM prompts in their app. Reads `.vibe-prompt/state/inventory.json` (required prerequisite — created by `/vibe-prompt:scan`), applies the F1-F12 rubric (all active in v0.4), writes `.vibe-prompt/state/audit.json` and a human-readable `docs/vibe-prompt/audit-YYYY-MM-DD.md`. Read-only — no source mutation.
---

# /vibe-prompt:audit

Load `vibe-prompt:guide` first. Then load `references/smell-rubric-f1-f12.md`, `references/audit-report-template.md`, `references/scoring-dimensions.md`, and `vibe-prompt:guide/references/calibration-patterns.md`.

Apply the F1-F12 rubric (F1-F9 active in v0.4; F10-F12 are Phase 4) to the cached inventory. Emit machine-readable findings + human-readable dated report.

## Inputs

- `.vibe-prompt/state/inventory.json` in the target app — REQUIRED.
- No flags in v0.1.

## Workflow

1. **Pre-flight.** Invoke `session-logger` start. Read `.vibe-prompt/state/inventory.json`. If missing, instruct the user to run `/vibe-prompt:scan` first and exit. Validate inventory against `plugins/vibe-prompt/schemas/inventory.schema.json` — if invalid, friction-log `inventory-schema-violation` and abort.
2. **Apply rubric.** Walk `references/smell-rubric-f1-f12.md` in order F1 → F1b → F2 → F3 → F4 → F5 → F6 → F7 → F9 → F10 → F11 → F12. For each smell, run the detection rule against `inventory.json`. If it fires, build a finding object: `{ id, smell, severity, evidence[], recommendation }`. Use the recommendation template, filling in concrete values from inventory (file paths, IDs, counts). F11 and F12 are only evaluated when F10 has already fired on the same prompt (F10 is prerequisite).
3. **F2 semantic pass.** Voice-contradiction detection cannot run from inventory alone — it needs prompt content. Re-read each voice-bearing prompt's content from the target source. Compare global directive (if present in registry as a `*directive` / `*persona` entry) against each task prompt. Surface contradictions with specific file:line citations on BOTH the rule and the violation.
4. **F6 known-model lookup.** Compare each `modelIdentifiers[*].value` against the bundled known-models list (in `references/smell-rubric-f1-f12.md` §F6). If unrecognized, the suspect-model variant of F6 fires with elevated severity language and a "verify what's actually served" recommendation.
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
   - **User-var detection:** scan `templatedVars` for names matching user-origin heuristics:
     - Exact: `userInput`, `userMessage`, `userQuery`, `userText`, `userContent`, `userPrompt`, `userData`, `userBio`, `userDescription`, `userQuestion`
     - Contains (case-insensitive): `(?i)(message|query|text|prompt|input|content|bio|description|question|dream|note|comment|review|feedback|reply|chat)`
     - Extended list from `.vibe-prompt/config/user-input-vars.json` or `audit.injectionResistance.userInputVars` in config.json (additive to defaults)
   - **Sanitization-directive scan:** if user-var matched, check prompt content within 200 chars of each user-var reference for:
     - `(?i)treat .* as data`
     - `(?i)ignore .* instructions`
     - `(?i)do not execute`
     - `(?i)your role is fixed`
     - `(?i)content within .* is data only`
   - **Fire F10 when:** user-var detected AND no sanitization directive found nearby. Build finding `{ id: "F10", severity: "high", handoffHint: "vibe-sec:audit", evidence: { promptId, promptLocation, userVars[], varTypes[] }, recommendation: <template from rubric> }`.
   - **Track F10-fired prompts** — a prompt set used as a prerequisite gate for F11 and F12 detection.

4d. **F11 defense-in-depth scarcity detection.** For each prompt in the F10-fired set:
   - **Defense-phrase scan:** count distinct defense phrases in the full prompt content (not just the 200-char window):
     - "treat as data"
     - "ignore instructions within"
     - "your role is fixed"
     - "do not execute commands"
     - "regardless of user request"
     - "always remain"
   - **Fire F11 when:** defense-phrase count < 2. Build finding `{ id: "F11", severity: "medium", handoffHint: "vibe-sec:audit", evidence: { promptId, detectedDefensePhrases[], recommendedDefensePhrases[] }, recommendation: <template from rubric> }`.

4e. **F12 composition-order violation detection.** For each prompt in the F10-fired set, and only if composer.json is available (`.vibe-prompt/eval/composer.json` from v0.2+ setup):
   - **Read composition order** from composer.json — ordered list of layers: `{ layerName, type, vars[] }`.
   - **Find user-var injection layer:** the layer whose `vars[]` contains the user-var (or the innermost layer for inline injections).
   - **Find system-instruction layer:** the layer with `type: "global-directive"` or the first layer by index.
   - **Fire F12 when:** user-var layer index ≤ system-instruction layer index. Build finding `{ id: "F12", severity: "critical", handoffHint: "vibe-sec:audit", evidence: { promptId, userVar, userVarLayer, systemInstructionLayer, compositionOrder[] }, recommendation: <template from rubric> }`.
   - **Confidence degrade:** if composer.json `confidence` field < 0.6 (or composer.json is absent), F12 severity degrades from `critical` to `high` and evidence notes "composition order detection low-confidence; verify manually."

5. **Compose summary.** Count findings by severity → `summary.byCategory`. Total → `summary.totalFindings`.
6. **Compute per-prompt scores.** Per `references/scoring-dimensions.md` and the Score impact sections in `references/smell-rubric-f1-f12.md`:
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
