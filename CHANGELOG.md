# Changelog

## v0.1.0 — 2026-05-28

Initial release. Static prompt audit for vibe-coded apps.

**Commands:**
- `/vibe-prompt:scan` — inventory every prompt site (registry + inline)
- `/vibe-prompt:audit` — flag the 7 structural smells (F1-F7)
- `/vibe-prompt` — state-aware bare router
- `/vibe-prompt:evolve-prompt` — L3 self-evolution

**Stack coverage:** TypeScript/JavaScript and Python.

**Validation:** round-tripped against Celestia3 (Next.js + Firebase + Gemini). Scan found 14 prompt sites (6 registry-tracked + 8 inline) across 8 distinct personas. Audit fired 6 of 7 smells (F1-F6); F7 correctly did NOT fire because ChatService.ts uses registry-fetched prompts. The plugin caught three findings the manual cowpath audit missed: corrected F6 occurrence count, surfaced a TarotSpread.tsx voice contradiction, and detected a synastry templating mismatch.

**Known v0.1 limitations (queued for v0.2):**
- No dead-code / orphaned-prompt smell.
- F4 doesn't flag call-site `.replace()` vars that drift from the registry entry's `templatedVars`.
- No detection of conditional persona overrides (runtime branches that inject voice changes).
- F2 trace depth is one hop (global directive → task prompt).
