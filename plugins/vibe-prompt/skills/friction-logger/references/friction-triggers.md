# Friction triggers — vibe-prompt

Single source of truth for which command logs which friction at which confidence. Agents do NOT tune per call.

## scan triggers

| Trigger code | Confidence | When |
|---|---|---|
| `no-recognized-stack` | high | No `package.json` AND no `pyproject.toml`/`requirements.txt` |
| `registry-detected-but-empty-entries` | high | Registry found, but extraction yielded zero entries |
| `model-identifier-unrecognized` | high | Model string matches no published-model regex (per F6 list) |
| `low-confidence-detections-over-40pct` | medium | More than 40% of inline detections are low-confidence (per persona-extraction.md §confidence) |
| `inline-prompt-without-fallback-aggregate` | low | At least 3 inline sites with no fallback (logged once per scan) |

## audit triggers

| Trigger code | Confidence | When |
|---|---|---|
| `f6-suspect-model-detected` | high | F6 fires with the suspect-model variant |
| `f2-contradiction-cross-file-attempted` | medium | F2 detection surfaced a likely contradiction but the 1-hop trace couldn't fully resolve it |
| `rubric-default-recommendation-felt-generic` | medium | Agent's self-read of the just-rendered recommendation says it lacks app-specific detail |
| `inventory-schema-violation` | high | inventory.json failed schema validation on read |

## first-run-setup triggers

| Trigger code | Confidence | When |
|---|---|---|
| `composer-mimic-confirmation-required` | medium | User had to manually correct the captured composer pattern |
| `agent-detection-fallback-to-interview` | medium | Self-id failed all detection signals and had to ask user |
| `inventory-not-found` | high | `.vibe-prompt/state/inventory.json` missing and user couldn't provide a manual one |

## eval triggers

| Trigger code | Confidence | When |
|---|---|---|
| `key-pattern-in-state-file` | high | Pre-run guardrail caught a state file with a key pattern |
| `cost-ceiling-exceeded` | high | Run aborted partway through |
| `vendor-sdk-not-installed` | high | Plugin needed a vendor SDK that isn't bundled (e.g., OpenAI in v0.1) |
| `model-cost-rate-unknown` | medium | Estimated cost using conservative fallback (model not in rate table) |
| `vendor-api-error` | medium | Vendor returned 5xx after retry |
| `vendor-rate-limit-exhausted` | medium | Vendor returned 429 twice |
| `llm-judge-finding-dismissed-as-bias` | low | User flagged a judge finding as bias-only, not real drift |
| `fixture-synthesis-low-confidence` | low | Agent's confidence in a synthesized fixture is low |

## radar triggers

| Trigger code | Confidence | When |
|---|---|---|
| `radar-cache-older-than-7-days` | low | Posture detected stale cache |
| `vendor-news-source-unreachable` | medium | Web fetch failed for a vendor blog/news source |

## router triggers

| Trigger code | Confidence | When |
|---|---|---|
| `audit-older-than-14-days` | low | Posture branch detects stale audit |
| `eval-older-than-30-days` | low | Posture detected stale last eval run |

## evolve-prompt triggers

| Trigger code | Confidence | When |
|---|---|---|
| `no-sessions-in-30-days` | low | Insufficient data to make any proposal |

## grade triggers

| Trigger code | Confidence | When |
|---|---|---|
| `weight-override-suggested-and-rejected` | low | Plugin suggested a dimension weight override; user declined. |
| `regression-flagged` | high | A prompt's composite regressed vs baseline. |
| `regression-flagged-and-accepted-as-baseline` | medium | User accepted a regression as the new baseline via `--accept-regression`. Signal that monotonic discipline may be wrong here, OR scoring has calibration issue. |
| `composite-score-flat-after-fix` | medium | User claims to have fixed a prompt finding but composite didn't move. Signal that dimension formula isn't sensitive enough OR fix didn't land. |
| `swap-and-discard-tie-rate-over-30pct` | medium | More than 30% of judge calls discarded as position-bias ties. Tighten judge prompt or change judge model. |

## iterate triggers

| Trigger code | Confidence | When |
|---|---|---|
| `iterate-suggestion-implemented` | high | User actually built a `:iterate` suggestion (verifiable by next `:scan` finding the new prompt). Positive signal — suggestion engine is valuable. |
| `iterate-suggestion-dismissed-as-off-domain` | medium | User flagged a suggestion as wrong for the app. Signal to tighten domain detection. |
