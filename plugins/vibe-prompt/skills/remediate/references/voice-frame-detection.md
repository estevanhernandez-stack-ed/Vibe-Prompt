# Voice-frame detection — Category B sub-category extension

v0.6 extends Category B (contradiction removal) beyond direct banned-phrase
matching. The natal_interpretation round-trip on Celestia3 showed that v0.5's
regex catches "Fellow Pilgrim" but misses voice-frame phrasings — "quatrain-style
narrative", "shattering of the veil", "ancient dust", "mirrors of mercury",
"prophetic shadows" — that all echo the same prophet voice the global directive
bans. This reference catalogs the extraction rules + phrase patterns + the
confidence split between the two sub-categories.

The Category B distinction:

- **`banned-phrase-removal`** — v0.5 behavior. Direct match against an
  explicitly-banned phrase. Confidence 0.75. Routes per the v0.5 default.
- **`voice-frame-rewrite`** — v0.6 addition. Pattern match against archaic
  vocabulary, ritualistic framing, or capitalized abstract nouns that
  contradict the extracted voice rule. Confidence 0.65. ALWAYS stages by
  default; `--apply-voice-frame-fixes` flag is the opt-in for normal routing.

---

## Voice-rule extraction from global directive

Parse the global-directive layer (per `composer.json.layers[]` where
`type === "global-directive"`) for two rule shapes: explicit bans and positive
guidance that implies bans. Each extracted rule returns `{rule, confidence, source}`.

### Explicit-ban regex patterns

| Pattern | Match shape | Example | Confidence |
|---|---|---|---|
| `(?i)never (use\|say\|call\|address)` | direct "never X" command | `"never call them Fellow Pilgrim"` | 0.95 |
| `(?i)not (a\|the) (\w+)` | "not a 16th-century prophet" | `"You are not a 16th-century prophet."` | 0.85 |
| `(?i)avoid (\w+)` | softer ban | `"avoid archaic vocabulary"` | 0.80 |
| `(?i)no (\w+\s*){1,3}allowed` | structural ban | `"no archaic forms allowed"` | 0.85 |
| `(?i)don'?t (use\|say\|address)` | colloquial ban | `"don't use 'thou' or 'thee'"` | 0.85 |

### Persona-affirmation patterns (imply bans)

When the global directive AFFIRMS a positive voice, the contradicting voice is
implicitly banned. Each affirmation projects a ban set:

| Affirmation pattern | Implied ban | Confidence |
|---|---|---|
| `(?i)plain (modern\|simple) language` | archaic, formal-priest, prophet | 0.75 |
| `(?i)contractions` | formal-prose, archaic | 0.70 |
| `(?i)warm.{1,30}friend` | formal-priest, ritualistic, prophet | 0.75 |
| `(?i)second person` | third-person address (e.g. "the Pilgrim") | 0.80 |
| `(?i)conversational` | ritualistic, ceremonial, archaic | 0.70 |
| `(?i)direct` | indirect / oracular / circumlocutory | 0.65 |

### Extraction output shape

```json
{
  "bans": [
    {"rule": "Fellow Pilgrim", "confidence": 0.95, "source": "(?i)never (use|say|call|address)"},
    {"rule": "16th-century prophet", "confidence": 0.85, "source": "(?i)not (a|the) X"},
    {"rule": "archaic", "confidence": 0.75, "source": "implied:plain modern language"}
  ],
  "positiveGuidance": [
    {"rule": "plain modern language", "confidence": 0.95, "source": "literal-match"},
    {"rule": "contractions", "confidence": 0.95, "source": "literal-match"},
    {"rule": "warm friend tone", "confidence": 0.95, "source": "literal-match"}
  ],
  "globalConfidence": 0.80
}
```

`globalConfidence` is the mean of extracted-rule confidences. When global
confidence falls below 0.6, friction-log
`category-b-voice-frame-detection-confidence-low` (medium) and skip auto-rewrite
even with the flag set — too noisy to act on.

---

## Voice-frame phrase patterns

Once voice rules are extracted, scan task prompt content for phrases that
contradict the banned voice frame. Three pattern families, each emitting a
`{phrase, location, banSource}` triple per match.

### Archaic-vocabulary regex

| Pattern | Captures | Spec anchors |
|---|---|---|
| `(?i)\bthou\b\|\bthee\b\|\bthy\b\|\bthine\b` | second-person archaic pronouns | "thou" |
| `(?i)\bverily\b\|\bforsooth\b\|\bhark\b` | archaic interjections | "verily" |
| `(?i)\bancient\b.{0,30}(dust\|veil\|shadow\|wisdom)` | ritualistic ancient-X compounds | "ancient dust" |
| `(?i)\bveil\b.{0,30}(shatter\|pierce\|lift\|rend)` | veil-mysticism compound | "shattering of the veil" |
| `(?i)(mercur(ial\|y)\|prophet(ic\|s)?)\b.{0,40}(mirror\|shadow\|tongue)` | prophet-imagery compound | "mirrors of mercury", "prophetic shadows" |
| `(?i)\bquatrain(-style\|s)?\b` | poetic-form callouts | "quatrain-style narrative" |
| `(?i)\bFellow\s+[A-Z]\w+` | "Fellow X" address-form | "Fellow Pilgrim", "Fellow Seeker" |
| `(?i)\boracle('s)?\b\|\bsage('s)?\b` | seer-archetype nouns | "oracle's voice" |

### Ritualistic-framing regex

Phrases that frame the LLM's output as a sacred / ceremonial act. These
contradict any "warm friend" / "conversational" / "direct" voice affirmation.

| Pattern | Captures |
|---|---|
| `(?i)the cosmos` | grand cosmic framing |
| `(?i)the divine` | divine framing |
| `(?i)the source\b` | source-archetype framing |
| `(?i)the path` | journey-archetype framing |
| `(?i)sacred (text\|reading\|act)` | sacrament framing |
| `(?i)reveal(ed\|s)? (to\|unto)` | revelation framing |
| `(?i)blessed (be\|with)\b` | blessing framing |

### Capitalized-abstract-noun regex

Capitalized abstract nouns shift voice into ritual-speech regardless of phrase
content. They almost always contradict "plain modern language" affirmation.

| Pattern | Captures |
|---|---|
| `\bthe Pilgrim\b` | the Pilgrim — direct match |
| `\bthe Way\b` | the Way — capitalized abstract |
| `\bthe Source\b` | the Source — capitalized abstract |
| `\bthe Path\b` | the Path — capitalized abstract |
| `\bthe (Seeker\|Wanderer\|Initiate)\b` | seeker-archetype titles |
| `\bthe (Truth\|Light\|Voice)\b\s*(of\|within)` | abstract-title compounds |

Standalone capitalized nouns inside structural blocks (`[BRACKETS]`,
`{{templated_vars}}`, headings) are excluded — those are markup, not voice.

### Detection algorithm

1. Run each pattern family against the prompt content.
2. For each match, derive `banSource` by checking which extracted voice rule
   the phrase contradicts. Rule of thumb: archaic-vocab matches map to the
   highest-confidence archaic-ban (literal "thou" → explicit ban if present;
   else falls back to "plain modern language" implied ban).
3. Emit one `{phrase, location, banSource}` triple per match. Location is
   `{file, line, columnStart, columnEnd}` from inventory/registry locator.
4. Aggregate into `voiceFrameContradictions` array on the audit finding.

---

## Confidence calibration

The voice-frame sub-category's confidence sits at **0.65** instead of the
0.75 banned-phrase baseline. Three reasons:

1. **Semantic-edit risk.** Voice-frame rewrites change phrasing, not literal
   tokens. The model writes a substitute that "fits" the positive guidance —
   higher chance of drift than removing a literal phrase.
2. **Locator ambiguity.** Voice-frame patterns can match in multiple
   surrounding contexts; the "right" rewrite depends on which sentence the
   phrase lives in. Less certain than banned-phrase locators.
3. **Voice-drift after-eval.** Banned-phrase removal is verifiable with a
   single grep; voice-frame rewrites require a full re-eval to confirm the
   replacement preserves intent without re-introducing a different
   voice-frame.

### Sub-score adjustments

The 5-dimension rubric from `confidence-rubric.md` applies, with these
voice-frame-specific overrides:

| Dimension | Banned-phrase | Voice-frame |
|---|---|---|
| locate-confidence | 0.85 typical | 0.70 typical (multi-pattern matches) |
| diff-shape-confidence | 0.80 (find-and-rephrase) | 0.60 (semantic rewrite) |
| voice-risk (inverted) | 0.75 | 0.55 (higher drift risk) |
| schema-impact (inverted) | 1.0 (no schema) | 1.0 (no schema) |
| version-bump-required (inverted) | 0.5 (registry minor) | 0.5 (registry minor) |

Weighted average lands at ~0.65 vs ~0.75 for banned-phrase. The split confirms
why voice-frame ALWAYS stages even with the auto-write flag absent.

### Override gates

- Without `--apply-voice-frame-fixes`: voice-frame Category B diffs stage even
  when confidence ≥ 0.90 (because the conservative default treats voice-drift
  risk as load-bearing).
- With `--apply-voice-frame-fixes`: voice-frame diffs follow normal routing
  (auto-write at ≥ 0.90, stage at 0.70-0.89, inline-only below 0.70).
- Banned-phrase Category B continues using v0.5's `--apply-contradictions`
  flag. The two flags are independent — opting into one does NOT opt into the
  other.

### Rewrite-rationale annotation

Every voice-frame diff emits a `voiceFrameRewriteRationale` field on the
pending-fix front-matter (per `pending-fix.schema.json` v0.6 extension). The
rationale explicitly names:

1. Which voice-frame phrase was detected.
2. Which voice rule it contradicted (and the rule's source — explicit ban or
   implied ban).
3. How the proposed rewrite aligns with the positive-guidance affirmation.

Example rationale:

> Detected `"quatrain-style narrative"` (archaic-vocabulary pattern). Contradicts
> `"plain modern language"` positive-guidance affirmation in the global
> directive. Proposed rewrite uses "structured opening paragraph" — preserves
> the structural intent (formal opening section) while dropping the archaic
> poetic-form label.

The rationale is what makes the staged diff reviewable without re-running the
voice-rule extraction. The user sees the contradiction + the alignment without
having to reconstruct the chain.

---

## Edge cases

- **Empty global directive.** When the global-directive layer is absent or
  empty, voice-rule extraction returns zero rules. The voice-frame extension
  silently skips — no findings, no friction log. Banned-phrase Category B
  continues unaffected (it doesn't depend on extraction).
- **Conflicting voice rules.** When extraction returns both a positive
  affirmation (`"plain modern language"`) AND an explicit ban that contradicts
  it (theoretical edge case), prefer the explicit ban. Confidence drops 0.10
  for any voice-frame finding sourced from the affirmation side.
- **High-recall pattern hits.** Patterns like `(?i)the path` will match in
  prompts that legitimately use "the path" as a domain term (e.g., file-system
  prompts). Voice-frame findings are suppressed when the phrase appears inside
  a code fence, `[BRACKETS]` block, or a templated var. The locator step
  consults inventory.json to identify these structural zones.
