# Confidence rubric — remediate

Every generated diff scores on five dimensions, weighted-averaged to a single 0-1
confidence. The confidence determines routing per `SKILL.md` step 4.

## The 5 dimensions

| Dimension | Weight | What it measures |
|---|---|---|
| **locate-confidence** | 0.30 | How sure we are about which file/line to edit |
| **diff-shape-confidence** | 0.25 | How well the diff matches the template |
| **voice-risk** (inverted) | 0.20 | 1.0 = no risk (additive); lower = more risk |
| **schema-impact** (inverted) | 0.15 | 1.0 = no schema touched; lower = direct schema edit |
| **version-bump-required** (inverted) | 0.10 | 1.0 = code-only change; lower = registry version decision |

Weights sum to **1.0**. Final confidence = weighted average of the 5 sub-scores.

---

## locate-confidence (weight 0.30)

How sure we are about which file/line to edit. Highest-weighted dimension because
landing the diff on the wrong line is the most expensive failure mode (worse than
proposing the wrong template — the user can spot template wrongness in review).

| Signal | Sub-score |
|---|---|
| `composer.json` present + finding is F9 | 1.0 |
| Inline prompt with unique anchor text (template-literal containing distinctive var name) | 0.95 |
| Registry entry with file:line reference and unique content match | 0.90 |
| Registry entry with ambiguous content match (banned phrase appears in 2+ entries) | 0.70 |
| Inline prompt with no anchor text or ambiguous location | 0.55 |
| Cannot locate target file/line confidently | 0.30 |

---

## diff-shape-confidence (weight 0.25)

How well the diff matches the category template. Pure-addition diffs score highest
because there's nothing to "merge wrong"; find-and-rephrase diffs lose confidence
as the number of occurrences grows.

| Diff shape | Sub-score |
|---|---|
| Pure addition (Category A or Category C contract paragraph) | 1.0 |
| Pure addition with structural wrap (Category C delimiter placement) | 0.85 |
| Find-and-rephrase with ≤ 2 occurrences (Category B) | 0.80 |
| Find-and-rephrase with 3 occurrences (Category B) | 0.70 |
| Find-and-rephrase with > 3 occurrences (Category B) | 0.55 |
| Multi-file diff (out of scope for v0.5; flag and skip) | 0.20 |

---

## voice-risk (weight 0.20, inverted)

How much voice-drift risk the diff carries. Sub-score is **inverted** — higher means
less risk. Used because voice drift is the hardest to verify mechanically and the
most expensive to ship wrong.

| Risk profile | Sub-score |
|---|---|
| No voice risk (additive composer-level — Category A) | 1.0 |
| Token cost only (Category C — additive defense + delimiter) | 0.95 |
| Semantic edit on per-prompt content (Category B — find-and-rephrase) | 0.55 |
| Persona-level rewrite (out of scope for v0.5) | 0.30 |

---

## schema-impact (weight 0.15, inverted)

Whether the diff touches `OUTPUT_SCHEMA` or any structured output contract. Sub-score
is inverted — higher means less schema impact.

| Schema touch | Sub-score |
|---|---|
| Diff does not touch OUTPUT_SCHEMA | 1.0 |
| Tangential mention (e.g., example text references schema fields) | 0.75 |
| Direct schema edit (changing field types or required fields) | 0.50 |

For v0.5, Category A + B + C diffs all score 1.0 here in the common case — none of
them edit `OUTPUT_SCHEMA` directly. The dimension is retained for future categories
that might restructure schema.

---

## version-bump-required (weight 0.10, inverted)

Whether the diff requires a registry version bump and whether the bump is automatic.

| Bump shape | Sub-score |
|---|---|
| Pure code/template change (no registry touched) | 1.0 |
| Registry content change with automatic minor bump (Category B normal case) | 0.85 |
| Registry content change requiring user version decision (no semver in current version) | 0.65 |

---

## Routing thresholds

After weighted-averaging, route the diff per its confidence:

| Confidence | Route |
|---|---|
| **≥ 0.90** | **auto-write** to source file with backup batch |
| **0.70 – 0.89** | **stage** to `.vibe-prompt/remediate/pending/<finding-id>.diff` |
| **< 0.70** | **inline-only** — emit recommendation text only, no file action |

Thresholds are user-configurable via `.vibe-prompt/config/remediate-thresholds.json`
(schema fields `remediate.autoApplyThreshold` and `remediate.stageThreshold`).

---

## Worked example — Category A, F9 with composer.json present

Scenario: Celestia3, F9 fires on `arithmancy_natal_integration`. composer.json
present with globalConfidence 0.85. The composer file is `src/lib/gemini.ts`,
masterDirective layer at line 80.

| Dimension | Sub-score | Reasoning |
|---|---|---|
| locate-confidence | 1.0 | composer.json present + F9 finding |
| diff-shape-confidence | 1.0 | Pure addition (Category A) |
| voice-risk (inverted) | 1.0 | No voice risk — composer-level additive |
| schema-impact (inverted) | 1.0 | Does not touch OUTPUT_SCHEMA |
| version-bump-required (inverted) | 1.0 | Pure code change |

**Weighted confidence:** `1.0 × 0.30 + 1.0 × 0.25 + 1.0 × 0.20 + 1.0 × 0.15 + 1.0 × 0.10 = 1.00`

Route: auto-write. Realistic landed confidence (after the spec's 0.92 default
floor) is reported as 0.92 in `remediate-result.json` — the rubric ceiling tops
out at the per-category default to leave headroom for future edge cases.

---

## Worked example — Category B, F2 with 3 occurrences

Scenario: Celestia3, F2 fires on `natal_interpretation` (the "Fellow Pilgrim" leak).
Three occurrences of the banned phrase in `ConfigService.ts:67-102`.

| Dimension | Sub-score | Reasoning |
|---|---|---|
| locate-confidence | 0.90 | Registry entry with unique content match |
| diff-shape-confidence | 0.70 | Find-and-rephrase with 3 occurrences |
| voice-risk (inverted) | 0.55 | Semantic edit on per-prompt content |
| schema-impact (inverted) | 1.0 | Does not touch OUTPUT_SCHEMA |
| version-bump-required (inverted) | 0.85 | Registry change with auto minor bump |

**Weighted confidence:** `0.90 × 0.30 + 0.70 × 0.25 + 0.55 × 0.20 + 1.0 × 0.15 + 0.85 × 0.10 = 0.74`

Realistic landed confidence rounds to ~0.75 per the Category B default. Route:
stage (Category B always stages by default; auto-write only with `--apply-contradictions`).

---

## Worked example — Category C, F10 on Oneirocriton

Scenario: Celestia3, F10 fires on Oneirocriton inline prompt. `dreamText` user-var
detected via template-literal interpolation. composer.json absent for the inline
prompt scope.

Split: contract paragraph + delimiter placement scored separately.

### Contract paragraph
| Dimension | Sub-score |
|---|---|
| locate-confidence | 0.95 |
| diff-shape-confidence | 1.0 (pure addition) |
| voice-risk (inverted) | 0.95 |
| schema-impact (inverted) | 1.0 |
| version-bump-required (inverted) | 1.0 |

**Confidence:** ~0.97 — but capped at Category C contract default 0.88 in the
spec to leave headroom for inline-prompt edge cases.

### Delimiter placement
| Dimension | Sub-score |
|---|---|
| locate-confidence | 0.90 |
| diff-shape-confidence | 0.85 |
| voice-risk (inverted) | 0.95 |
| schema-impact (inverted) | 1.0 |
| version-bump-required (inverted) | 1.0 |

**Confidence:** ~0.91 — capped at Category C delimiter default 0.78 because the
delimiter name choice carries detection uncertainty not captured in this rubric.

### Combined diff confidence

Weighted average of contract (0.88) and delimiter (0.78) → ~0.83. Below 0.90
auto-write threshold → routes to stage.

---

## Why the spec's per-category defaults cap the rubric output

The per-category defaults in `fix-categories.md` (Category A = 0.92, Category B =
0.75, Category C contract = 0.88, Category C delimiter = 0.78) represent the ceiling
the spec is comfortable with at v0.5 — there are unseen edge cases (composer files
with unusual structure, prompts with custom delimiters already, etc.) that the
rubric doesn't currently penalize. The cap leaves room for friction signals to
tune the rubric upward over time as we observe real round-trips.

If the rubric output exceeds the per-category default, `:remediate` reports the
per-category default as the landed confidence. Override via
`.vibe-prompt/config/remediate-thresholds.json` if you want the raw rubric output
to flow through.
