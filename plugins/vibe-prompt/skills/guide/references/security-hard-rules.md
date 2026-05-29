# Security hard rules — vibe-prompt

These rules are non-negotiable. The guide SKILL loads this reference; every command SKILL inherits these defaults.

## Auth handling

1. **Prefer OAuth Bearer over API keys for Gemini.** When `gcloud auth print-access-token` returns a value, use it via `Authorization: Bearer <token>` header. No persistent secret on disk, no env var to leak, automatic refresh. This is the default path documented in `vendor-clients.md`.

2. **API keys from env vars only — and namespaced.** When the OAuth path isn't available, fall back to:
   - `VIBE_PROMPT_GEMINI_API_KEY` (NOT the generic `GEMINI_API_KEY`)
   - `VIBE_PROMPT_ANTHROPIC_API_KEY` (when Anthropic vendor lands; v0.2)
   - `VIBE_PROMPT_OPENAI_API_KEY` (when OpenAI vendor lands; v0.2)

   The `VIBE_PROMPT_*` namespace prevents the env var from being picked up by Firebase deploy tooling, other Gemini-stack apps in the same shell, or any tooling that reads the generic name. **NEVER read keys from any file** in `.vibe-prompt/` or anywhere else inside the target app.

3. **Never persist.** Keys, tokens, and any vendor credentials are never written to state files, log files, cache files, or anywhere on disk.

4. **Never echo.** When logging or reporting, NEVER print a key value, a Bearer token, or any header containing one. If you must reference a credential existed at all (e.g., "VIBE_PROMPT_GEMINI_API_KEY was set: true"), reveal at most the last 4 chars surrounded by asterisks: `****abc1`. Bearer tokens are NEVER previewed at all (too long, too sensitive — boolean presence only).

## Pre-run guardrail

Before reading ANY state file (config, composer, agent, run-result), grep-scan the file for these patterns:

- Google AI: `AIza[0-9A-Za-z_-]{35}`
- Anthropic: `sk-ant-(api|admin)[0-9A-Za-z_-]+`
- OpenAI: `sk-[a-zA-Z0-9]{48}|sk-proj-[a-zA-Z0-9_-]+`

If any match fires, REFUSE to start. Output:

> Refusing to start: state file `<path>` contains a pattern matching a vendor API key. This is a security risk — keys should live in env vars only. Please:
> 1. Remove the suspect content from the file
> 2. Rotate the leaked key with the vendor
> 3. Re-run vibe-prompt

Friction-log `key-pattern-in-state-file` with confidence high.

## Compose with vibe-sec when available

If the target app has `vibe-sec` installed (check for `plugins/vibe-sec/` symlink in `~/.claude/plugins/` OR `.vibe-sec/` state directory in the target app), defer all key-pattern regex to vibe-sec's scan. Otherwise use the inline patterns above.

## Vendor SDK call wrapping

When making vendor API calls via curl:
- Pass the key via header (`x-goog-api-key`, `x-api-key`, `Authorization: Bearer`), NEVER in the URL or body
- Set `--silent --show-error` so curl doesn't accidentally echo headers to stdout
- Capture stdout to a temp file or variable; never pipe directly to a log

## Cost-side guardrail

Even if a key check passes, refuse to start a run if the configured `costCeiling` is 0 or negative. Suggest a sensible default ($2.00) and ask the user to confirm.
