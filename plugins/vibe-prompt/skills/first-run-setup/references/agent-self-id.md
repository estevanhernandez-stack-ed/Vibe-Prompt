# Agent self-identification — first-run-setup

How vibe-prompt detects which agent is driving it, so the evaluator-drift framing adapts per-runtime.

## Detection signals (in order)

### Signal 1: Environment variables

Check for known agent runtime env vars:

| Env var pattern | Agent name | Likely model field source |
|---|---|---|
| `CLAUDE_CODE_*` | Claude Code | Detect from the session (see Model field below); ask if the session doesn't expose it |
| `CURSOR_*` | Cursor | Ask which model variant |
| `CLINE_*` | Cline | Ask which model variant |
| `GEMINI_CLI_*` | Gemini CLI | Detect from the session; ask if not exposed |
| `WINDSURF_*` | Windsurf | Ask which model variant |
| `GOOSE_*` | Goose | Ask which model variant |

If a match fires, fall through to user interview for the model field if unclear.

### Model field: detect from the session, or ask. Never default.

The `model` field is never filled from a hardcoded default. A default goes stale the day a new model ships (the pre-v0.8 `claude-opus-4-7` default did exactly that) and then every judge footer names the wrong evaluator, which is the one thing the evaluator-drift framing exists to get right.

1. **Session-exposed model id.** Some harnesses state the running model's exact id in the session context the agent already reads (Claude Code does). If present, use it verbatim, including any context suffix such as `[1m]`. `detectionMethod` stays whatever found the agent name.
2. **Ask.** If the session doesn't expose an id, ask the user which model is driving the session, and record `detectionMethod: "user-declared"` when the name also came from the interview.
3. **Unknown.** If the user doesn't know, record the `model` field as `"unknown"` and say so in the judge footer. An honest unknown beats a confident wrong id.

This is not Signal 4 self-introspection: reading an id the harness printed into the session is a fact lookup, not asking the model to describe itself.

### Signal 2: Marker files

If env detection fails, check home directory for known installation markers:

| Path | Agent name |
|---|---|
| `~/.claude/` | Claude Code |
| `~/.cursor/` | Cursor |
| `~/.cline/` | Cline |
| `~/.gemini/cli/` | Gemini CLI |
| `~/.windsurf/` | Windsurf |
| `~/.goose/` | Goose |

If a single marker exists, use that agent. If multiple markers exist, prefer the one that's been recently modified (sort by mtime) and confirm with user.

### Signal 3: User interview (fallback)

If signals 1 + 2 fail or are ambiguous, ask the user:

> I couldn't auto-detect which agent is running vibe-prompt. Please confirm:
> 1. Claude Code
> 2. Cursor
> 3. Cline
> 4. Gemini CLI
> 5. Other (specify)

After the agent name, also ask for the model (the user knows this; we can't reliably detect).

### Signal 4: Self-introspection (DO NOT use in v0.1)

We could ask the running agent to identify itself in a prompt. v0.1 does NOT do this because:
- Different agents respond inconsistently
- Self-reports may be wrong (e.g., a Claude variant claiming to be a different version)
- The friction of writing a robust parser exceeds the user-interview alternative

Friction-log `agent-detection-fallback-to-interview` (medium confidence) when we fall to signal 3.

## Cache shape

Write `.vibe-prompt/eval/agent.json` validated against `agent.schema.json`:

```json
{
  "version": "0.1",
  "name": "Claude Code",
  "model": "<id from the session, or as the user declared it>",
  "vendor": "anthropic",
  "detectedAt": "2026-05-28T...",
  "detectionMethod": "marker-file"
}
```

## Re-detection triggers

Re-run detection (don't trust the cache) when:

- The cache is older than 90 days
- The user runs `/vibe-prompt:eval` from a different agent than the cached one (e.g., env vars match Cursor but cache says Claude Code — friction-log + ask)

## How the LLM-judge prompt uses it

The judge prompt opens with:

> You are [agent.name + agent.model]. You are being asked to read two model outputs and identify drift between them. You may be biased toward outputs that match your own training style — name this risk explicitly in your findings.

And every judge finding ships with the footer:

> *Note: This finding came from [agent.name + agent.model] reading both outputs. The evaluator may be biased toward outputs that match its own style. Verify high-severity flags with a sample user, an A/B test, or by reading the outputs yourself before acting.*

This is the killer-feature wiring. Adapt the footer text per detected vendor:

- **Cross-vendor** (agent.vendor !== prod.vendor): emphasize cross-vendor bias risk
- **Intra-vendor** (agent.vendor === prod.vendor): emphasize version drift, not vendor bias
- **Unknown** (agent.vendor === null): emphasize "evaluator runtime unknown — interpret with full skepticism"
