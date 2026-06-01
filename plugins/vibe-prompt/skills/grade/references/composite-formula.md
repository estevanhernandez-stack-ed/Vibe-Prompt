# Composite formula — grade (v0.4)

## Per-prompt composite

Weighted average of the 5 dimension scores. Default equal weights (0.20 each, v0.4).

**v0.4 dimensions:** `schemaTightness`, `personaConsistency`, `instructionClarity`, `tokenEfficiency`, `injectionResistance`.

Per dimension: when both audit and eval results are present, the dimension score = average(audit dimension score, eval dimension score). When eval is absent, use the audit dimension score directly.

User can override per-app via `.vibe-prompt/grade/weights.json`:

```json
{
  "version": "0.4",
  "weights": {
    "schemaTightness": 0.20,
    "personaConsistency": 0.20,
    "instructionClarity": 0.20,
    "tokenEfficiency": 0.20,
    "injectionResistance": 0.20
  }
}
```

Weights must sum to 1.0 (or auto-normalized if not).

## App composite

Average of per-prompt composites across the inventory.

## App composite — per-workspace (v0.7+)

When the audit emits findings tagged with `workspaceIdentifier` (multi-workspace mode),
`:grade` partitions findings by workspace and computes one composite per workspace:

```
perWorkspace[name] = mean(per-prompt composites whose prompts produced findings under workspaceIdentifier=name)
aggregate          = mean(all non-null perWorkspace values)
```

`appComposite.perWorkspace[<name>]` exposes the per-workspace number; `appComposite.aggregate`
exposes the cross-workspace mean (replaces the v0.6 single number for multi-workspace apps).
Workspaces with zero findings are emitted as `perWorkspace[<name>] = null` AND surfaced
under `appComposite.workspacesWithNoFindings[]` so downstream tools can flag empty workspaces
explicitly.

### Back-compat: single-workspace apps preserve v0.6 flat-number shape

For single-workspace audits (no `workspaceIdentifier` on findings, or all values null), the
v0.7 `:grade` emits `appComposite` as a flat number — exactly the v0.6 shape. The schema's
`oneOf` branch keeps both shapes valid; downstream consumers reading v0.6 grade-result.json
files continue to work without changes.

| Audit shape | `appComposite` emission |
|---|---|
| Single-workspace (v0.6 or v0.7 single-workspace mode) | Flat integer 1-10 — back-compat path |
| Multi-workspace (v0.7+) | Object: `{ perWorkspace, aggregate, workspacesWithNoFindings }` |

## Agent-suggested overrides

When the plugin detects a dimension is brand-load-bearing for the app, it proactively proposes an
override in the `:audit` workflow (not `:grade` — `:grade` is pure synthesis).

Heuristics (from `vibe-prompt:audit/references/scoring-dimensions.md`):
- 4+ prompts have F2 (persona contradiction) findings → suggest persona-consistency 2× weight
- 4+ prompts have F1/F1b/F4 (schema-related) findings → suggest schema-tightness 2× weight
- Average prompt token count > 4000 → suggest token-efficiency 2× weight
- App-type heuristic: consumer → injectionResistance 0.40; internal → 0.10; mixed → 0.20

User confirms or declines via AskUserQuestion. Confirmed overrides write to
`.vibe-prompt/grade/weights.json` from `:audit` (not `:grade`).

## Auto-normalization

If weights don't sum to 1.0, `:grade` normalizes before computing:

```
normalizedWeight[d] = weight[d] / sum(all weights)
```

A normalization event logs a warning in the banner: "Weights didn't sum to 1.0 — normalized
automatically. Update `.vibe-prompt/grade/weights.json` to silence this."

## Legacy 4-dimension weights.json migration (v0.3 → v0.4)

If `.vibe-prompt/grade/weights.json` has exactly 4 dimensions (pre-v0.4 format), `:grade` adds `injectionResistance: 0.20` and auto-normalizes all 5 weights:

```
normalizedWeight[d] = rawWeight[d] / sum(rawWeights + 0.20)
```

Example: legacy `{schemaTightness: 0.5, personaConsistency: 0.2, instructionClarity: 0.2, tokenEfficiency: 0.1}` → raw sum = 1.0 + 0.20 added = 1.20 → normalized: `{schemaTightness: 0.417, personaConsistency: 0.167, instructionClarity: 0.167, tokenEfficiency: 0.083, injectionResistance: 0.167}`. The user's relative intent (schema was 5× tokens) is preserved. Normalization warning logs in the banner.
