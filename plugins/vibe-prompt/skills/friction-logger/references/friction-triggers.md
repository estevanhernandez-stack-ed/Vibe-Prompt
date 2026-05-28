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

## router triggers

| Trigger code | Confidence | When |
|---|---|---|
| `audit-older-than-14-days` | low | Posture branch detects stale audit |

## evolve-prompt triggers

| Trigger code | Confidence | When |
|---|---|---|
| `no-sessions-in-30-days` | low | Insufficient data to make any proposal |
