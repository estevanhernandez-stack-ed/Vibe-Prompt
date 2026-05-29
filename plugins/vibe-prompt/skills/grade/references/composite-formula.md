# Composite formula — grade

## Per-prompt composite

Weighted average of the 4 dimension scores. Default equal weights (0.25 each).

User can override per-app via `.vibe-prompt/grade/weights.json`:

```json
{
  "version": "0.3",
  "weights": {
    "schemaTightness": 0.20,
    "personaConsistency": 0.40,
    "instructionClarity": 0.20,
    "tokenEfficiency": 0.20
  }
}
```

Weights must sum to 1.0 (or auto-normalized if not).

## App composite

Average of per-prompt composites across the inventory.

## Agent-suggested overrides

When the plugin detects a dimension is brand-load-bearing for the app, it proactively proposes an
override in the `:audit` workflow (not `:grade` — `:grade` is pure synthesis).

Heuristics (from `vibe-prompt:audit/references/scoring-dimensions.md`):
- 4+ prompts have F2 (persona contradiction) findings → suggest persona-consistency 2× weight
- 4+ prompts have F1/F1b/F4 (schema-related) findings → suggest schema-tightness 2× weight
- Average prompt token count > 4000 → suggest token-efficiency 2× weight

User confirms or declines via AskUserQuestion. Confirmed overrides write to
`.vibe-prompt/grade/weights.json` from `:audit` (not `:grade`).

## Auto-normalization

If weights don't sum to 1.0, `:grade` normalizes before computing:

```
normalizedWeight[d] = weight[d] / sum(all weights)
```

A normalization event logs a warning in the banner: "Weights didn't sum to 1.0 — normalized
automatically. Update `.vibe-prompt/grade/weights.json` to silence this."
