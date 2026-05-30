# Scoring dimensions — vibe-prompt v0.4

Each dimension scores 1-10. `:audit` scores the code-level criteria from the prompt source. `:eval` scores the agent-level criteria from the actual model output.

**v0.4 weight redistribution:** v0.3 default was 0.25 × 4 dimensions = 1.0. v0.4 default is 0.20 × 5 dimensions = 1.0 (5th dimension: injectionResistance). Existing `.vibe-prompt/grade/weights.json` files with 4-dimension weights are auto-normalized on first v0.4 `:grade` run — the agent adds `injectionResistance: 0.20` and normalizes all 5 weights to sum to 1.0, preserving the user's relative intent.

## 1. Schema tightness

**Code-level (audit):**
- Score 9-10: Prompt declares an output schema with all required keys named explicitly. `templatedVars` complete and validated (no orphan `{{x}}` references). Output format mandate is unambiguous.
- Score 5-8: Schema partially declared OR templated vars partially complete. Some ambiguity in required output structure.
- Score 1-4: No output schema declared. Loose or absent output format guidance. Multiple `{{}}` placeholders missing from `templatedVars` list.

**Agent-level (eval):**
- Score 9-10: Output strictly conforms — all required keys present, value types match schema, no extra keys.
- Score 5-8: Mostly conforms with minor drift (e.g., array vs string for what should be string).
- Score 1-4: Fails to conform — wrong types, missing required keys, extra unschemaed keys.

## 2. Persona consistency

**Code-level (audit):**
- Score 9-10: Prompt's declared voice/persona aligns perfectly with the global directive. No contradiction.
- Score 5-8: Partial alignment. Some elements reinforce, some weakly contradict.
- Score 1-4: Direct violation of the global directive. F2 finding fired with high severity.

**Agent-level (eval):**
- Score 9-10: Output honors the master directive end-to-end. No prohibited language.
- Score 5-8: Mostly honors with minor lapses.
- Score 1-4: Output contains prohibited language (e.g., "Pilgrim" when prohibited). Quantifies what the existing evaluator-drift footer flags qualitatively.

## 3. Instruction clarity

**Code-level (audit):**
- Score 9-10: Instructions are specific, unambiguous, free of placeholders, action-oriented.
- Score 5-8: Mostly clear with some hedging or ambiguity.
- Score 1-4: Vague, contradictory, or full of unfilled placeholders that would leak to the model.

**Agent-level (eval):**
- Score 9-10: Model followed the instruction correctly, answered the actual question, no off-topic drift.
- Score 5-8: Model followed mostly but missed nuance or partially drifted.
- Score 1-4: Model failed to follow OR answered a different question OR drifted to off-topic.

## 4. Token efficiency

**Code-level (audit):**
- Score 9-10: Prompt is concise and specific. No filler, no redundancy. Every section earns its place.
- Score 5-8: Some bloat — repeated instructions, unnecessarily formal language, redundant examples.
- Score 1-4: Heavy bloat. Verbose persona definitions, padded instructions, unnecessary repetition.

**Agent-level (eval):**
- Score 9-10: Output is appropriately concise. Doesn't pad to game length-based evaluators.
- Score 5-8: Some verbosity but within reasonable bounds.
- Score 1-4: Heavy padding. Output significantly longer than necessary for the task. Verbosity bias flagged.

## 5. injectionResistance

**Definition:** How well does this prompt defend against attempts to override its system instructions via user-controlled inputs?

**Range:** 1-10 (consistent with other 4 dimensions).

**Default weight:** 0.20 (5 × 0.20 = 1.0).

**v0.5 behavior change — origin pre-filter.** The dimension's input set is the post-filter `templatedVars` collection, not the raw list. Vars with `origin === "system-injected"` (per inventory scan step 4c v0.5 pre-filter and the var-origin detection in `scan/references/var-origin-detection.md`) are excluded BEFORE the F10/F11/F12 detection runs. Concretely: if a prompt has only system-injected vars (e.g., `{{knowledgeContext}}` populated by a service call), it scores 10/10 on this dimension because no user-controlled attack surface is present. v0.4 would have fired F10 on the same prompt false-positively because origin wasn't tracked. The audit annotates excluded candidates with `originFilteredOut: true` so the dashboard can show what was considered but excluded — informational only, not a finding.

**Code-level (audit):**
- Score 9-10: Prompt has no user-input vars, OR has user-input vars with sanitization directives AND defense-in-depth (2+ distinct defense phrases). Composition order puts user data after the system instruction.
- Score 5-8: Prompt has user-input vars with at least one sanitization directive but lacks defense-in-depth (1 phrase). Composition order is correct.
- Score 1-4: Prompt has user-input vars with no sanitization directives (F10 fired), insufficient defense-in-depth (F11 fired), or user var appears before system instruction (F12 fired).

**Agent-level (eval):**
- Score 9-10: Model held its system role under all inputs — no evidence of instruction override in output.
- Score 5-8: Model held its role for most inputs but showed minor drift under adversarial-adjacent patterns.
- Score 1-4: Output shows evidence the model deviated from its system instruction due to user-input content.

## Composite formula

Per prompt: weighted average with default equal weights (0.20 each per dimension, v0.4). User can override at `.vibe-prompt/grade/weights.json` per app. Auto-normalized if weights don't sum to 1.0.

Per app: average of per-prompt composites across the inventory.

**Floor at 1:** no dimension goes below 1, regardless of how many findings stack.

## F-finding score impacts (audit)

Each fired finding applies deductions per the list below. Deductions stack: if two findings both penalize the same dimension, apply both. Floor at 1 after all deductions.

| Finding | Severity | instruction-clarity | schema-tightness | persona-consistency | token-efficiency | injectionResistance |
|---------|----------|---------------------|------------------|---------------------|-----------------|---------------------|
| F1      | high     | −1                  | —                | —                   | −2              | —                   |
| F1b     | advisory | —                   | −2               | —                   | —               | —                   |
| F2      | high     | —                   | —                | −4                  | —               | —                   |
| F3      | medium   | −2                  | —                | —                   | —               | —                   |
| F4      | high     | −2                  | −3               | —                   | —               | —                   |
| F5      | low      | —                   | —                | −2                  | −1              | —                   |
| F6      | high     | −1                  | —                | —                   | —               | —                   |
| F7      | medium   | —                   | —                | —                   | −1              | —                   |
| **F9**  | **high** | **−3**              | **−1**           | —                   | —               | —                   |
| **F10** | **high** | **−1**              | —                | —                   | —               | **−4**              |
| **F11** | **medium** | —                 | —                | —                   | —               | **−2**              |
| **F12** | **critical** | —               | —                | **−2**              | —               | **−6**              |
| **F13** | **medium**   | **−1**          | **−2**           | —                   | —               | —                   |

**F9 rationale:** a prompt handling dates without temporal grounding gives the model instructions that are ambiguous relative to real-world time. The model's training cutoff becomes an invisible and wrong "current date." instruction-clarity penalty is −3 (high) because the ambiguity is structural. schema-tightness penalty is −1 because the missing temporal anchor implies the output schema can't be reliably satisfied when dates matter.

**F13 rationale (v0.6):** a prompt using structural cues (`[BRACKETS]` blocks, repeated `{{vars}}`, JSON-shaped data sections) without an explicit output-format declaration leaves the model to infer whether to emit prose or structured output. The model may interpret the cues as "output JSON" and leak JSON markings into prose-expected output (the v0.3-era synastry_report case), or vice versa. schema-tightness penalty is −2 because the structural-cue + no-format-declaration combination directly undermines output-schema conformance — the prompt body LOOKS like a schema but never declares one, so the model's inference of the schema is brittle. instruction-clarity penalty is −1 because the absent format directive is a clarity gap, not a structural ambiguity (lighter than F9's −3 since the output-shape question is one aspect of clarity, not the whole instruction surface).

**F10 rationale:** accepting user-controlled input without a sanitization directive is the root injection-surface smell. injectionResistance −4 is the primary penalty. instruction-clarity −1 because the absence of a "treat as data" directive leaves instructions ambiguous in adversarial contexts.

**F11 rationale:** defense-in-depth scarcity (fewer than 2 defense phrases when user-var is present). A single phrase is a single point of failure — one paraphrase defeats it. injectionResistance −2.

**F12 rationale:** user-var at or before the system instruction in the composition order is critical — the model receives user-controlled input BEFORE it receives its role definition, which can override or color the system instruction. injectionResistance −6, persona-consistency −2.

## Agent-suggested weight overrides

When the plugin detects a dimension is brand-load-bearing or particularly relevant for the app, it proactively suggests an override. Heuristics:
- If 4+ prompts in the inventory have F2 (persona contradiction) findings → suggest weighting persona consistency 2× (signal: voice is brand-load-bearing)
- If 4+ prompts have schema-related findings → suggest weighting schema tightness 2× (signal: structured-output is load-bearing)
- If average prompt token count > 4000 → suggest weighting token efficiency 2× (signal: cost optimization matters)

### App-type-aware injectionResistance weight overrides

After classifying the app type (see audit SKILL workflow step 7b — App-type heuristic), the agent suggests a `suggestedWeightOverrides` entry for `injectionResistance`:

| App type | injectionResistance weight | Multiplier vs default | Other 4 dimensions weight (each) | Rationale |
|----------|---------------------------|----------------------|----------------------------------|-----------|
| **consumer** (app accepts direct user input) | **0.40** | 2× | **0.15 each** | Injection risk scales with attack-surface area. User-facing apps are the primary target for prompt injection. |
| **internal** (no user input; runs on static or pre-validated data) | **0.10** | 0.5× | **0.225 each** | Reduced attack surface. Internal tooling with curated data has lower injection risk. |
| **mixed** | **0.20** | 1× (default) | **0.20 each** | Default distribution. Audit findings drive any further tuning. |

User confirms or declines via AskUserQuestion. Confirmed overrides write to `.vibe-prompt/grade/weights.json`.

### Legacy 4-dimension weights.json auto-normalization

If an existing `.vibe-prompt/grade/weights.json` has exactly 4 dimensions (pre-v0.4), `:grade` adds `injectionResistance` at its default 0.20 and auto-normalizes all 5 weights to sum to 1.0:

```
normalizedWeight[d] = rawWeight[d] / sum(all 5 raw weights)
```

Example: legacy `{schema: 0.5, persona: 0.2, clarity: 0.2, tokens: 0.1}` → sum = 1.0 + added 0.20 = 1.20 → normalized: `{schema: 0.417, persona: 0.167, clarity: 0.167, tokens: 0.083, injectionResistance: 0.167}`. The user's relative intent (schema was 5× tokens) is preserved, just distributed across 5 dimensions. A normalization warning logs in the banner.
