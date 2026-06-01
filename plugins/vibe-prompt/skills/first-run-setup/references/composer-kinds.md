# Composer kinds — multi-composer / multi-call-site / shared-package topology

> v0.7 reference. Closes the v0.6 gap where `composer.schema.json` modeled exactly ONE composer per app. The cross-app probe (Project-626Labs-1, WeSeeYouAtTheMovies, Quiz Show) surfaced three app shapes that the single-composer assumption can't represent. v0.7 introduces a four-value `kind` enum on each composer entry: `single-composer`, `multi-composer`, `multi-call-site`, `shared-package`.

This file catalogs each kind: how to detect it, what canonical evidence it produces, and how `:first-run-setup` should classify a given app. The kind determines downstream behavior — F12 runs per composer, remediate routes per call site, grade composites partition per workspace.

## Kind enum

| Kind | Composer files | Call-site topology | Canonical example |
|---|---|---|---|
| `single-composer` | exactly 1 | all SDK calls flow through that file | Celestia3 `src/lib/gemini.ts` |
| `multi-composer` | 2+ distinct files | each composer file has its own composition shape | 626Labs `galaxyCore.ts` + `ChatController.ts` |
| `multi-call-site` | 0 (no canonical composer file) | SDK calls scattered across N files, each composing inline | WeSeeYou (6 inline call sites) |
| `shared-package` | 1 in `packages/<name>/` | referenced from multiple workspaces | Quiz Show `packages/ai/src/gemini/GeminiService.ts` |

`compositionShape` (top-level) is `single` when `kind === "single-composer"`; `multi` otherwise.

## single-composer

**Detection heuristic.** Exactly one composer file matches the v0.6 detection heuristics (filename + SDK import). All SDK call sites in the repo route through that file (via direct import or re-export). No `packages/` directory contains a composer file.

**Canonical example — Celestia3 `src/lib/gemini.ts`.** Single composer with 6 traced layers (persona, master-directive, format, knowledge, task-instruction, chaos-protocol). All `technomancerModel.generateContent(...)` calls flow through `gemini.ts`. v0.7 emits `composers[0]` with `kind: "single-composer"`, `compositionShape: "single"`, and the top-level `layers[]` is preserved as a back-compat shim mirroring `composers[0].layers`.

**When in doubt.** If exactly one composer file resolves and `globalConfidence ≥ 0.7`, classify single-composer. The v0.6 emission shape is preserved.

## multi-composer

**Detection heuristic.** Two or more distinct files each (a) match composer-detection heuristics (filename or SDK import) AND (b) have their own SDK call site reachable from app code. Each composer's layer set is independent — the persona / master-directive / format / task-instruction layers differ between composers.

**Canonical example — 626Labs `galaxyCore.ts` + `ChatController.ts`.** `galaxyCore.ts` composes for the galaxy-rendering Gemini model with one persona; `ChatController.ts` composes for the conversational Gemini model with a different persona. Both import `@google/genai`. v0.7 emits `composers[]` of length 2, each with its own `layers[]`, `globalConfidence`, `apiParameterCompleteness`. Top-level `layers[]` is omitted (no single source of truth).

**Confidence note.** When two composers share substantial layer content (e.g., the same persona pulled from a config), still emit two composer entries — the call-site topology, not layer-content similarity, drives the kind.

## multi-call-site

**Detection heuristic.** Zero composer files resolve via filename heuristic, OR the resolved files don't contain a `generateContent` / `messages.create` / `chat.completions.create` call site. Instead, SDK calls appear inline across N source files (typically components, services, or callbacks), each composing its own prompt directly at the call site.

**Canonical example — WeSeeYouAtTheMovies.** No canonical composer file. SDK calls happen at 6 inline call sites: `MovieTrivia.tsx`, `BadgeIconGenerator.ts`, `ScoutReport.ts`, `AthleteCard.tsx`, `EventRecap.ts`, `ProfileBio.ts`. Each constructs its own `systemInstruction` literal inline. v0.7 emits `composers[]` grouped per the grouping heuristic below; each entry's `path` is an array of call-site paths rather than a single file.

### Multi-call-site grouping heuristic

When multiple inline call sites exist, group them into logical composers using:

1. **Same SDK + same persona → one group.** Call sites importing the same SDK (`@google/genai`) AND sharing a persona-like literal (matched via content signal — "You are a movie-trivia bot", "You are a badge generator", etc.) are treated as one logical composer.
2. **Differing personas → separate groups.** Call sites with distinct persona content emit separate composer entries even when they share the SDK.
3. **Mixed SDKs → always separate groups.** Anthropic call sites never group with Gemini call sites.

WeSeeYou worked example: 4 call sites share "movie-trivia-bot" persona + `@google/genai` → one composer entry with `path: ["MovieTrivia.tsx", "ScoutReport.ts", "AthleteCard.tsx", "EventRecap.ts"]`. The other 2 share "badge-generator" persona → second composer entry with `path: ["BadgeIconGenerator.ts", "ProfileBio.ts"]`. Total `composers[]` length 2 under `kind: "multi-call-site"`.

### Confidence calibration

| Grouping clarity | Confidence |
|---|---|
| All call sites cluster cleanly into 1-3 distinct personas | 0.85 |
| Personas partially overlap (same-SDK, similar-but-not-identical phrasing) | 0.70 |
| Call sites use computed persona vars (can't statically cluster) | 0.55 |
| No clustering possible (each call site is unique) | 0.40 (emits N composer entries, one per call site) |

## shared-package

**Detection heuristic.** A composer file matching the v0.6 detection heuristics lives inside a `packages/<name>/` (or workspace-detected equivalent) directory rather than the top-level `src/`. The composer is imported / re-exported across multiple workspaces in a monorepo. `inventory.workspaces[]` must show ≥2 workspaces consuming the composer's exports.

**Canonical example — Quiz Show `packages/ai/src/gemini/GeminiService.ts`.** Composer lives at `packages/ai/src/gemini/GeminiService.ts`, consumed by `apps/cinema/`, `apps/hotel/`, `apps/reel-battles/`, etc. v0.7 emits one `composers[]` entry with `kind: "shared-package"`, `path: "packages/ai/src/gemini/GeminiService.ts"`, and `globalConfidence` reflecting the package-level composition. Workspace-level audit findings reference this composer via `composerIdentifier` while still partitioning findings by `workspaceIdentifier`.

**Distinguishing from multi-composer.** Shared-package = ONE composer file referenced by many workspaces. Multi-composer = MULTIPLE composer files within the same workspace. If `packages/ai/` has the composer AND `apps/cinema/src/` has its own composer that doesn't go through `packages/ai/`, classify as multi-composer (or both kinds, surfaced as one `composers[]` entry per file).

## Classification workflow

1. Walk source tree, collect all composer-file candidates (v0.6 filename + SDK-import heuristics).
2. For each candidate, identify direct call sites (`generateContent` / `messages.create` / `chat.completions.create`).
3. Count distinct composer files containing call sites:
   - 0 → `multi-call-site` (proceed to grouping)
   - 1 → check file location: `packages/<name>/` → `shared-package`; otherwise `single-composer`
   - 2+ → `multi-composer` (or `shared-package` if any composer lives under `packages/<name>/` AND is referenced by ≥2 workspaces — `shared-package` wins)
4. Emit `composers[]` per the classification:
   - `single-composer` → length 1, top-level `layers[]` shim preserved
   - `multi-composer` → length N (one per file), no top-level `layers[]`
   - `multi-call-site` → length M (one per grouped persona/SDK cluster), each with `path` as string array
   - `shared-package` → length 1 with `path` pointing at the packages-rooted file

## Friction triggers

- `composer-multiplicity-detected` (positive) — multi-composer or shared-package kind correctly identified.
- `composer-kind-detection-ambiguous` (medium) — first-run-setup can't confidently pick a kind (e.g., one candidate matches single-composer heuristics but a second file has SDK call sites with no shared composition); user manual selection needed.

## What NOT to do

- Don't classify `multi-call-site` when at least one composer file resolves cleanly. Inline call sites that bypass an existing composer should still emit `kind: "single-composer"` (or multi-composer if there are 2+ composer files), with the inline sites surfaced as findings (F1) rather than a kind change.
- Don't classify `shared-package` when only one workspace consumes the package — that's just `single-composer` living in an unusual directory.
- Don't auto-confirm multi-call-site grouping when the persona clusters disagree with the SDK clusters; surface as `composer-kind-detection-ambiguous` and let the user choose.

## Cross-references

- Schema: `plugins/vibe-prompt/schemas/composer.schema.json` — `composers[]` + `kind` enum + `compositionShape`.
- Sibling reference: `composer-detection.md` — file discovery + layer tracing + apiParameter heuristics (per-composer, run once per entry in `composers[]`).
- Audit consumer: F12 / F10 / F11 iterate over `composers[]`, emitting `composerIdentifier` on findings.
- Remediate consumer: Category D-1 (inline-to-registry) generates one diff per call site under `multi-call-site` kind.
