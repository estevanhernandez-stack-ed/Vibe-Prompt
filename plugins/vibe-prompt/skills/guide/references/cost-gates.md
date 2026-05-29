# Cost gates — vibe-prompt

## Pre-run estimate

Before any vendor API call, present a cost estimate to the user:

```
═══ Vibe-Prompt eval estimate ═══
Mode:           drift
Prompts:        14
Fixtures:       1 per prompt (synthesized)
Models:
  Prod:         gemini-3.5-flash (14 calls)
  Baseline:     in-session agent (14 calls, no API cost)
LLM-judge:      ENABLED (14 calls, in-session, no API cost)

Estimated tokens: 28,400 prompt + 8,400 completion
Estimated cost:   $0.18 (Gemini only; in-session calls bill against your Claude Code session)
Cost ceiling:    $2.00

Proceed? [y/N]
```

Wait for explicit user confirm before issuing any vendor call.

## Cost calculation

For each model call, estimate cost using a known per-token rate:

| Model | Input $/1M tok | Output $/1M tok |
|---|---|---|
| gemini-3.5-flash | $0.075 | $0.30 |
| gemini-2.5-flash | $0.075 | $0.30 |
| gemini-2.5-pro | $1.25 | $5.00 |

If the model isn't in the table, fall back to a conservative estimate (input: $1, output: $4 per 1M) and friction-log `model-cost-rate-unknown`.

In-session agent calls (Claude baseline + LLM-judge) are accounted as $0 toward the API cost ceiling. They DO bill against the user's Claude Code session but vibe-prompt doesn't track those (out of scope for v0.1).

## Hard ceiling

User configures `costCeiling` in `.vibe-prompt/eval/config.json` (default: $2.00). Plugin tracks running cost after each vendor call. If running cost + next-call estimate would exceed ceiling:

1. Stop dispatching new vendor calls
2. Set `summary.abortedByCostCeiling = true` in the run-result
3. Render the partial dashboard with a warning banner: *"Run aborted at $X of $Y ceiling. N of M prompts completed. Re-run with higher ceiling to finish."*
4. Friction-log `cost-ceiling-exceeded` with confidence high

## Per-call retries

On rate-limit errors (HTTP 429), wait 30 seconds and retry once. Each retry counts toward the cost budget. On second 429, give up on that prompt and record `error: rate-limit-exhausted` in its `outputs.prod` entry.

On other errors (timeouts, 5xx), retry once with 5-second backoff. Same accounting.
