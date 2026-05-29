# Domain detection cascade — iterate

Detection order (stop at first confident match):

## 1. CLAUDE.md at app root

Highest signal. If `<target-app>/CLAUDE.md` exists:
- Read it
- Extract: app's stated purpose, persona, domain area, brand voice
- Verify with user via one-line confirm: "I read your CLAUDE.md — your app is [summary]. Look right? (Y/n)"
- If confirmed, cache to `.vibe-prompt/iterate/domain.json` and proceed
- If user pushes back, fall through to step 2

## 2. Vibe-tool artifacts

Sources to check (in priority order):
- `docs/architecture/` — Cart-generated architecture docs
- `docs/scope.md` — Cart's scope document
- `docs/walk/` — Walk's tour configs (signal: user-facing flows + AI features)
- `.vibe-iterate/atlas.jsonl` — Iterate's feature log
- `.vibe-sec/state/` — Sec's audit (signal: security concerns + stack)

Aggregate signals into a domain summary. Verify with user before proceeding.

## 3. Package metadata + prompts

- `package.json` description + name + dependencies (vendor signals like `@google/genai` → AI-app;
  `firebase` → Firebase stack)
- `README.md` if present
- The prompts themselves — subject matter is often the strongest signal

## 4. Last resort: short interview

If steps 1-3 didn't yield a confident domain summary, ask:

> "Couldn't pin down your app's domain confidently. Tell me in 2-3 sentences what it does."

Cache the user's response.

## Cache

Captured domain at `.vibe-prompt/iterate/domain.json`:

```json
{
  "summary": "Frontier AI meets technomancy: astrology (natal/synastry/horary), Hermeticism (Picatrix, Agrippa), numerology, tarot, dream interpretation. Voice: warm modern oracle, not 16th-century prophet.",
  "source": "claude-md",
  "capturedAt": "2026-05-29T...",
  "verifiedByUser": true
}
```

User can refresh with `:iterate --refresh-domain` flag.

## Confidence signals

A domain summary is "confident" when it names:
- The app's primary value proposition (what it does for the user)
- The domain or subject matter (astrology, legal research, recipe generation, etc.)
- The target user archetype (developer, end user, professional, etc.)

If the domain summary is too generic ("it's an app that uses AI"), push back and try the next
cascade level before going to user interview.
