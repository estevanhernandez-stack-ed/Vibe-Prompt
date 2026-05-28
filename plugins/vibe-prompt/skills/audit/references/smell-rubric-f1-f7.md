# F1-F7 smell rubric — audit

Each finding has: ID, Smell, Severity default, Detection rule (reads from inventory.json), Recommendation template. The audit SKILL applies these in order.

---

## F1 — Registry exists, isn't enforced

**Severity (default):** high
**Detection:** `inventory.registry.detected === true` AND `inventory.inlinePrompts.length > 0`.
**Evidence:** every entry of `inlinePrompts`.
**Recommendation template:**
> Move each inline `systemInstruction` literal into the registry at `{registry.location}` with a stable id (e.g., `<feature>_<role>`). Call sites switch to the registry's fetch method ({inferred method name}). The hybrid sites (see F7) are the highest priority.

## F1b — No central registry detected

**Severity (default):** advisory
**Detection:** `inventory.registry.detected === false` AND `inventory.inlinePrompts.length >= 3`.
**Evidence:** the top 5 inline sites (by token count).
**Recommendation template:**
> No central registry detected. With {N} inline prompts, consider introducing one — a const map of `id → content` in `src/lib/prompts.ts` or equivalent. Registry + admin UI unlocks production tuning without code deploys.

## F2 — Voice contradicts itself across the composition stack

**Severity (default):** high
**Detection:** for each voice-bearing prompt (registry or inline), extract directives that look like bans or persona rules (regex on phrases like "never", "do not", "always", "you are not"). Compare across the composition stack (global persona + each task prompt). A finding fires when:
- A global directive declares a ban (e.g., "never call the user X") AND
- A task prompt that gets stacked on top instructs the model to do the banned thing (e.g., addresses the user as X).

The detection is best-effort and may require the agent to read the actual content semantically rather than purely lexically. v0.1 trace depth: 1 hop (global directive → task prompt). Deeper graph analysis is v0.2.

**Evidence:** file + line of the global directive rule AND file + line of the violating task prompt.
**Recommendation template:**
> Hold persona at the global directive only. Strip per-prompt persona overrides from `{violating prompt id}` so the composer doesn't stack contradictions. Per-prompt content becomes task-only.

## F3 — Version drift inside the registry

**Severity (default):** medium
**Detection:** `inventory.registry.entries[*].version` values where the major numbers diverge by ≥ 2, OR where one entry's content version label (e.g., "v3.5.0") doesn't match the voice rules implied by another entry at the same major (manual reading required — agent makes a best-effort call).
**Evidence:** the diverging version values.
**Recommendation template:**
> Coordinate registry version bumps. When the global directive changes major, every voice-bearing prompt either re-confirms voice at the new version or gets re-touched and bumped. Highest-priority correction: any entry whose version label doesn't match its content (silent staleness).

## F4 — Naive templating without unfilled-var validation

**Severity (default):** high
**Detection:** `inventory.registry.entries[*].templatedVars.length > 0` OR `inventory.inlinePrompts[*].templatedVars.length > 0`, AND no `requiredVars` field exists in the registry entry interface (i.e., no validator path detected).
**Evidence:** call sites that pass user data through `.replace()` or string substitution without validation. Detect by grepping target source for `.replace(/\\{\\{[^}]+\\}\\}/g` patterns.
**Recommendation template:**
> Add a typed renderer: each prompt declares its required vars; the renderer throws if any are missing. ~30 LOC. Catches unfilled-placeholder leakage at the boundary.

## F5 — Persona fragmentation

**Severity (default):** low
**Detection:** `inventory.personas.length > 3`.
**Evidence:** full `inventory.personas` array.
**Recommendation template:**
> {N} distinct persona labels detected for what may be one brand voice. Decide consciously: collapse to 1-3 personas, or document the intentional per-feature split. If unsure, the registry version of each persona is the authoritative source.

## F6 — Hard-coded model identifier

**Severity (default):** high
**Detection:** for each `inventory.modelIdentifiers[*]`, if `occurrences.length >= 2`, fire a hardcoding finding.

**Why no typo detection in v0.1.** An earlier draft of this rubric included a "suspect model" sub-finding that fired when the identifier didn't match a bundled known-models pattern list. This was removed after a cowpath calibration on Celestia3: model names ship faster than rubric updates, the bundled list went stale within a release cycle, and false positives erode audit trust. The cowpath audit incorrectly flagged `gemini-3.5-flash` as a typo when it is in fact a real Google model (declared in `@google/genai/dist/genai.d.ts` `Model_2` type union). Model-registry lookup belongs in v0.2 when the plugin can plumb a fresh source (context7, the `claude-api` skill, or a vendor's published-model API). Until then, F6 is a pure consolidation finding.

**Evidence:** every occurrence (file + line) of the hardcoded identifier.
**Recommendation template:**
> Consolidate model identifier `{value}` to one config source. It appears in {N} places ({file:line list}); when the model bumps, all sites have to move in lockstep and the type system can't catch a missed one. Create a single config module (e.g., `src/config/ai.ts`) exporting `DEFAULT_MODEL`; have client, server, and any service-layer defaults import from it.

## F7 — Hybrid call sites

**Severity (default):** medium
**Detection:** any single source file that contains BOTH a `getPrompt(...)` (or equivalent registry fetch) call AND an inline `systemInstruction` literal.
**Evidence:** file + line of registry calls AND file + line of inline calls within that file.
**Recommendation template:**
> Pick one pattern per service. `{file}` mixes registry-fetched and inline prompts; route the inline call sites through the registry once they exist there (depends on F1 fix). Improves reader-comprehension for future contributors.
