# Workspace detection

> Reference for `:scan`'s workspace-topology detection step. Added in v0.7 to close the monorepo scope-flattening gap surfaced on Project-626Labs-1 and Quiz Show during the cross-app probe.

The detector classifies every target app into one of four `workspaceKind` values, then branches per-workspace inventory emission accordingly. Detection runs once during pre-flight, before stack + provider detection.

## The four kinds

| `workspaceKind` | Trigger | Inventory shape |
|---|---|---|
| `single-workspace` | One `package.json` at the target root; no `workspaces` field; no nested `package.json` outside `node_modules/` | Flat `inventory.json` — v0.6 shape preserved |
| `npm-workspaces` | Top-level `package.json` declares a `workspaces` array (or workspaces object with `packages`) | Per-workspace `inventory-<name>.json` files + top-level aggregator |
| `nested-projects` | No top-level `workspaces` declaration BUT ≥2 nested `package.json` files outside `node_modules/` (e.g., `apps/<x>/package.json`, `packages/<y>/package.json`) | Per-workspace `inventory-<name>.json` files + top-level aggregator. **Requires user confirmation via friction trigger** on first detection |
| `unknown` | No `package.json` anywhere (or pure-Python target with no JS workspaces concept) | Flat `inventory.json` — back-compat shape |

## npm workspaces detection

The npm-workspaces path is deterministic:

1. Read top-level `package.json`.
2. Look for `workspaces` field — accepts array form (`["packages/*", "apps/*"]`) or object form (`{ "packages": [...] }`).
3. For each glob entry, expand against the filesystem:
   - `packages/*` → enumerate every immediate subdir under `packages/` that contains a `package.json`
   - `apps/*` → same shape under `apps/`
   - Literal paths (`tools/buildkite`) → resolve directly
4. Each resolved directory becomes one entry in `workspaces[]` with:
   - `name` — read from the workspace's own `package.json` `name` field; fallback to directory basename
   - `path` — relative path from target root
   - `packageJsonPath` — `<path>/package.json`
   - `inventoryFile` — `.vibe-prompt/state/inventory-<name>.json` (sanitize name: lowercase, replace `/` and `@` with `-`)
5. Set `workspaceKind: "npm-workspaces"`. Confidence: **high** (declaration is explicit).

## Nested package.json detection (no `workspaces` declaration)

Some monorepos (Project-626Labs-1) ship multiple sub-projects without an npm `workspaces` declaration — each sub-project's `package.json` lives independently, often coexisting with sibling `vibe-*/` plugin clones or `_ARCHIVE_*/` directories.

Detection rule:

1. After confirming the top-level `package.json` has NO `workspaces` field, walk the target root one level deep (and one more if `apps/` or `packages/` directories exist at root).
2. For every directory containing a `package.json` (and not matching exclude defaults), record it as a candidate workspace root.
3. If candidate count ≥2 → set `workspaceKind: "nested-projects"`.
4. **First-time detection in nested-projects mode triggers `workspace-detection-confidence-low` friction (medium)** — surfaces the detected roots for user confirmation. User can override via `scan.workspaceDetection: force-single` to flatten.
5. Confidence: **medium** by default (no explicit declaration to anchor on; some "nested" roots are tooling or fixtures, not real workspaces).

## Exclude defaults

The scan walker applies a default exclude set BEFORE workspace classification — directories matching these globs never count as candidate workspaces and never contribute to `inlinePrompts[]`. Effective excludes write to `inventory.json.scanExcludes[]`.

Default glob list (always applied unless user overrides via `scan.excludes: []`):

- `vibe-*/` — sibling plugin clones inside another vibe project
- `*-main/` — checked-out canary repos (e.g., `Vibe-Walk-main/`)
- `_ARCHIVE_*/` — archived sub-projects
- `node_modules/` — never scan deps
- `.git/` — never scan git internals
- `dist/` — build output
- `build/` — build output

Users append project-specific globs via `config.scan.excludes`. Auto-suggested candidates (any directory matching `vibe-*/`, `*-main/`, `_ARCHIVE_*/` at the target root) trigger `scan-excludes-recommended-but-not-applied` friction (low) when they aren't in the config — so the next scan can adopt them.

## Confidence calibration

Workspace detection emits a confidence value alongside `workspaceKind`. The scan reflects it in the banner (`workspace: npm-workspaces (high)`); the audit consumes it to weight per-workspace findings.

| Kind | Confidence | Reason |
|---|---|---|
| `single-workspace` | high | Single `package.json`, no ambiguity |
| `npm-workspaces` | high | Explicit declaration; glob expansion is mechanical |
| `nested-projects` | medium | Inferred from filesystem topology; some sibling dirs are not workspaces |
| `unknown` | low | No JS workspaces concept; pure-Python target or empty repo |

When user runs `:scan` with `scan.workspaceDetection: force-single` the detector skips classification, emits `workspaceKind: "single-workspace"` with confidence high (user assertion overrides inference). `force-monorepo` is the inverse — declares nested-projects mode even on a single-package.json target.

## Implementation note

Workspace detection is a `:scan` responsibility and does NOT depend on `:first-run-setup`. `:scan` emits the `workspaces[]` array; `:first-run-setup` consumes it (per Task 16 in the v0.7 plan) when deciding whether to emit per-workspace composers.
