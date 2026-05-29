# Scoring dimensions — vibe-prompt v0.3

Each dimension scores 1-10. `:audit` scores the code-level criteria from the prompt source. `:eval` scores the agent-level criteria from the actual model output.

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

## Composite formula

Per prompt: weighted average with default equal weights (0.25 each per dimension). User can override at `.vibe-prompt/grade/weights.json` per app.

Per app: average of per-prompt composites across the inventory.

**Floor at 1:** no dimension goes below 1, regardless of how many findings stack.

## F-finding score impacts (audit)

Each fired finding applies deductions per the list below. Deductions stack: if two findings both penalize instruction-clarity, apply both. Floor at 1 after all deductions.

| Finding | Severity | instruction-clarity | schema-tightness | persona-consistency | token-efficiency |
|---------|----------|---------------------|------------------|---------------------|-----------------|
| F1      | high     | −1                  | —                | —                   | −2              |
| F1b     | advisory | —                   | −2               | —                   | —               |
| F2      | high     | —                   | —                | −4                  | —               |
| F3      | medium   | −2                  | —                | —                   | —               |
| F4      | high     | −2                  | −3               | —                   | —               |
| F5      | low      | —                   | —                | −2                  | −1              |
| F6      | high     | −1                  | —                | —                   | —               |
| F7      | medium   | —                   | —                | —                   | −1              |
| **F9**  | **high** | **−3**              | **−1**           | —                   | —               |

**F9 rationale:** a prompt handling dates without temporal grounding gives the model instructions that are ambiguous relative to real-world time. The model's training cutoff becomes an invisible and wrong "current date." instruction-clarity penalty is −3 (high) because the ambiguity is structural. schema-tightness penalty is −1 because the missing temporal anchor implies the output schema can't be reliably satisfied when dates matter.

F10, F11, F12 impacts are Phase 4 (injectionResistance dimension — not yet active in v0.4 Phase 2).

## Agent-suggested weight overrides

When the plugin detects a dimension is brand-load-bearing for the app, it proactively suggests an override. Heuristics:
- If 4+ prompts in the inventory have F2 (persona contradiction) findings → suggest weighting persona consistency 2× (signal: voice is brand-load-bearing)
- If 4+ prompts have schema-related findings → suggest weighting schema tightness 2× (signal: structured-output is load-bearing)
- If average prompt token count > 4000 → suggest weighting token efficiency 2× (signal: cost optimization matters)

User confirms or declines. Confirmed overrides write to `.vibe-prompt/grade/weights.json`.
