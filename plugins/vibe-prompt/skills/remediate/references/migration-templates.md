# Migration templates — Category D (v0.7)

Category D covers **mechanical refactors** that the audit→fix loop has historically
left as inline-only because they touch architecture, not prompt content. v0.7 ships
three migration templates that bridge the audit→fix gap for F1, F4, and F6 findings.

The category is determined by the audit finding ID:

| Finding | Category | Migration kind |
|---|---|---|
| F1 (inline systemInstruction bypasses registry) | D-1 | `D-1-inline-to-registry` |
| F4 (registry without typed renderer) | D-2 | `D-2-typed-renderer` |
| F6 (hardcoded model ID across multiple sites) | D-3 | `D-3-model-consolidation` |

All three default to **stage** routing — even at high confidence — because the
diffs touch architecture surfaces (registry shape, helper function signatures,
shared config files). Three opt-in flags unlock auto-write at the ≥0.90 threshold:

- `--apply-inline-to-registry` (D-1)
- `--apply-typed-renderer` (D-2)
- `--apply-model-consolidation` (D-3)

Without the flag, Category D diffs stage by default. With the flag, normal
confidence routing applies (auto-write at ≥0.90, stage at 0.70-0.89).

---

## D-1 inline-to-registry

**Detection trigger:** F1 finding on an inline `systemInstruction` literal at a
call site. The audit identifies the inline literal, its host file/range, and the
registry file the app already has (or the inferred path if absent).

**Confidence:** 0.85 default. Drops to 0.70 floor when the registry file isn't
detected (the diff has to invent the registry path, raising risk).

**Routing default:** **stage** by default. `--apply-inline-to-registry` opt-in
enables auto-write at confidence ≥0.90. Per-call-site — multiple inline sites can
be migrated independently in the same `:remediate` run.

**Touches:** TWO files per finding —
1. The registry file (new entry appended)
2. The call-site file (literal replaced with `getPrompt(id)` invocation + import injected if absent)

**Voice-risk:** 0.95 (mechanical refactor; prompt text preserved verbatim).

### Diff template

```diff
// File 1: src/lib/prompts/registry.ts (or app-conventional path)
   export const PROMPTS = {
     existingPrompt: { id: "existing-prompt", content: "..." },
+    <auto-derived-id>: {
+      id: "<auto-derived-id>",
+      content: "<extracted-inline-literal>",
+      version: "1.0.0"
+    },
   };

// File 2: <call-site-file> — replace inline literal with registry lookup
+  import { getPrompt } from "<registry-path>";
   ...
-  systemInstruction: "<inline-literal>",
+  systemInstruction: getPrompt("<auto-derived-id>"),
```

**Auto-derived id rules:**
- Strip filename + nearest function/method name; kebab-case the result.
- Example: `src/services/MovieTriviaService.ts` `generateBadge()` → `movie-trivia-badge`.
- Deduplicate against existing registry entries; append `-N` suffix on collision.

**Import-injection rules:**
- If `getPrompt` already imported from the registry path → no-op.
- If a different import from the registry path exists → extend the named-import list.
- If no import from registry path → add new import line at the top of the existing
  import block.

---

## D-2 typed-renderer

**Detection trigger:** F4 finding on a registry that uses raw `{{var}}` string
interpolation without a typed renderer. The audit identifies the registry file,
the prompt entries with templated vars, and the call sites that interpolate manually.

**Confidence:** 0.75 default. The diff touches the registry interface (adds
`requiredVars`) AND multiple call sites; higher complexity than D-1.

**Routing default:** **stage** by default. `--apply-typed-renderer` opt-in
enables auto-write at confidence ≥0.90.

**Touches:** THREE+ files per finding —
1. The registry file (extends each entry with `requiredVars: string[]`)
2. A new or existing helper file (adds `renderPrompt(id, vars)` helper that throws on missing var)
3. Every call site that interpolates the prompt (replaces raw template + var-passing with `renderPrompt(id, vars)`)

**Voice-risk:** 0.90 (template content preserved; only the interpolation surface changes).

### Diff template

```diff
// File 1: src/lib/prompts/registry.ts — extend each entry with requiredVars
   export const PROMPTS = {
-    movieReview: { id: "movie-review", content: "Review {{title}} as a {{genre}} critic." },
+    movieReview: {
+      id: "movie-review",
+      content: "Review {{title}} as a {{genre}} critic.",
+      requiredVars: ["title", "genre"]
+    },
   };

// File 2: src/lib/prompts/render.ts (NEW) — typed renderer helper
+  import { PROMPTS } from "./registry";
+
+  export function renderPrompt(id: string, vars: Record<string, string>): string {
+    const entry = PROMPTS[id];
+    if (!entry) throw new Error(`Unknown prompt id: ${id}`);
+    for (const required of entry.requiredVars ?? []) {
+      if (!(required in vars)) {
+        throw new Error(`renderPrompt(${id}): missing var '${required}'`);
+      }
+    }
+    return entry.content.replace(/{{(\w+)}}/g, (_, key) => vars[key] ?? "");
+  }

// File 3+: each call site — replace manual interpolation with renderPrompt
-  const prompt = PROMPTS.movieReview.content
-    .replace("{{title}}", title)
-    .replace("{{genre}}", genre);
+  const prompt = renderPrompt("movie-review", { title, genre });
```

**Renderer-helper conventions:**
- File name: `src/lib/prompts/render.ts` by default; falls back to app-conventional
  path detected from the existing registry file's neighbors.
- Throws on missing required vars (caught early at call site; replaces silent
  empty-string interpolation).
- Empty `requiredVars: []` is allowed (no enforcement; renderer still works).

---

## D-3 model-consolidation

**Detection trigger:** F6 finding with N occurrences of the same hardcoded model
ID across multiple files (threshold: N ≥ 3 to fire D-3; below threshold stays
inline-only). The audit identifies every occurrence with its file/range.

**Confidence:** 0.88 default. The diff is mechanical (string substitution) but
touches a new shared file + N call sites. Voice-risk = 1.0 (model ID has no
semantic content; replacement is safe).

**Routing default:** **auto-write** at the top end — confidence 0.88 falls just
under the 0.90 threshold, but with `--apply-model-consolidation` the route flips
to auto-write at ≥0.88 (D-3's confidence default IS the floor for this flag).

**Touches:** N+1 files per finding —
1. `src/config/ai.ts` (NEW; or app-conventional path) — exports `DEFAULT_MODEL`
2. Every occurrence file — replaces hardcoded string with import

**Voice-risk:** 1.0 (model IDs are pure config; no prompt-content surface).

### Diff template

```diff
// File 1: src/config/ai.ts (NEW) — default model export
+  export const DEFAULT_MODEL = "gemini-2.5-flash";

// File 2: src/services/MovieTriviaService.ts — replace hardcoded ID with import
+  import { DEFAULT_MODEL } from "@/config/ai";
   ...
-  model: "gemini-2.5-flash",
+  model: DEFAULT_MODEL,

// File 3: scripts/generate-badges.mjs — same pattern at every occurrence
+  import { DEFAULT_MODEL } from "../src/config/ai";
   ...
-  const model = "gemini-2.5-flash";
+  const model = DEFAULT_MODEL;
```

**Conventional-path detection:**
- Default: `src/config/ai.ts`.
- Fallback to `config/ai.ts` if `src/` doesn't exist.
- For Next.js apps: `lib/config/ai.ts`.
- For monorepos (workspaceKind `npm-workspaces` or `nested-projects`): one config
  file per workspace under `<workspace>/src/config/ai.ts`. If models differ across
  workspaces, emit one D-3 diff per workspace; if all workspaces share the same
  model, emit a single shared config at `packages/config/ai.ts` and have each
  workspace import from it.

**Import-path conventions:**
- Path-alias preferred when `tsconfig.json` declares one (`@/config/ai`).
- Relative path fallback when no alias detected.

**When NOT to fire D-3:**
- Single occurrence of a model ID → stays inline-only (consolidation has no return).
- Mixed model IDs across the codebase → emit per-distinct-id D-3 (`DEFAULT_MODEL`,
  `EMBED_MODEL`, etc.) rather than collapsing into one.

---

## Cross-cutting notes

**`migrationKind` field.** Every Category D pending diff or applied diff carries a
`migrationKind` enum value (`D-1-inline-to-registry` | `D-2-typed-renderer` |
`D-3-model-consolidation`). The field is required when `findingCategory ∈ {D-1,
D-2, D-3}` per `pending-fix.schema.json` v0.7 extension.

**Per-finding independence.** Category D diffs don't consolidate — each finding
gets its own diff even if multiple findings target the same file. (Contrast with
the F10+F11(+F12-high) consolidation in `consolidation-rules.md`.)

**Friction triggers.**
- `category-d-migration-applied-and-eval-confirms-no-regression` (positive)
- `category-d-migration-rejected` (low)

**Backward compat.** v0.6 remediate-result.json validates against v0.7 schemas —
the new `migrationKind` and `consolidatedDiffs` fields are optional, and the
v0.6 surface continues to work without modification.
