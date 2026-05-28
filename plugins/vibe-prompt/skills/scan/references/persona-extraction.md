# Persona extraction — scan

After detecting a prompt site, extract the persona label.

## Extraction order

1. **From declared persona field** (registry only): if the registry entry has a `name` field or `persona` field, use that.
2. **From "You are" anchor:** regex `/You are (the |an? )?([A-Z][A-Za-z0-9 ,.'-]+?)(\.|,|;|\n|$)/` on the prompt text. Capture group 2 is the persona label. Strip trailing punctuation.
3. **Fallback:** if no "You are" anchor, look for `Act as ...`, `Respond as ...`, `You will play ...`. Same capture rule.
4. **Last resort:** persona label = null. Flag the site as `personaLabel: null` with `confidence: low`.

## Normalization

- Strip extra whitespace, collapse internal spaces.
- Preserve case (the label is brand-identifying).
- Keep parenthetical qualifiers ("Athanor (the Resurrected Seer)" → "Athanor, the Resurrected Seer" — replace inner parens with comma+space, but only when the qualifier reads as appositive).

## De-duplication for the `personas` top-level array

- Case-sensitive exact match → dedupe.
- Case-insensitive near-match WITHOUT exact match → do NOT dedupe (this is signal for F5 persona fragmentation — surface both).
- Maintain insertion order in the array.

## Examples (from Celestia3)

- "You are the **Athanor** — a modern oracle" → `Athanor`
- "You are the Oneirocriton Dream Oracle, an ancient Hermetic dream interpreter" → `Oneirocriton Dream Oracle`
- "You are the **Athanor**, the Resurrected Seer" → `Athanor, the Resurrected Seer`
- "You are the **Athanor AI** performing a multimodal energy scan" → `Athanor AI`
- "You are the Chronos Scryer" → `Chronos Scryer`
