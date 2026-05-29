# Var origin detection — user-controlled vs system-injected

> v0.5 reference. Closes the v0.4 gap where arithmancy's `knowledgeContext` fired F10 false-positively because the scan couldn't tell user input from system service injection.

This file declares the two signals `:scan` uses to classify each captured templated var as `user-controlled`, `system-injected`, or `unknown`. The classification writes to `inventory.json` at `inlinePrompts[].templatedVars[].origin` plus `originConfidence` (0-1). Downstream consumers (F10/F11/F12 in `:audit`; Category C in `:remediate`) read these fields to filter their detection scope.

## Output

For each var detected by `inline-prompt-detection.md`:

```json
{
  "name": "dreamText",
  "source": "template-literal",
  "declaredAt": "src/Oneirocriton.tsx:L72",
  "origin": "user-controlled",
  "originConfidence": 0.92
}
```

Enum (locked by `inventory.schema.json`):

| origin | Meaning |
|---|---|
| `user-controlled` | Var content originates from user input (form field, URL param, chat message, prop drilling from user-bound state). F10/F11/F12 evaluate this var. `:remediate` Category C targets this var. |
| `system-injected` | Var content originates from a service call, cached lookup, or computed system value. F10/F11/F12 SKIP this var (writes `originFilteredOut: true`). `:remediate` does NOT target this var. |
| `unknown` | Detection couldn't resolve. Conservative default: classified as `user-controlled` for F10 purposes (audit may still fire) but with low confidence so user can override via `audit.varOriginOverrides` config. |

## Signal 1 — naming heuristic (high confidence)

Apply first. Match the var's bare identifier (the `name` field) against two regex lists.

### User-keyword regex

Case-insensitive match. Matches → `user-controlled`.

```
(?i)(user|input|message|query|text|content|bio|description|question|dream|note|comment|review|feedback|reply|chat)
```

Examples that match (→ `user-controlled`):
- `dreamText` (matches `dream`, `text`)
- `userMessage` (matches `user`, `message`)
- `userQuery` (matches `user`, `query`)
- `bioInput` (matches `bio`, `input`)
- `customerReview` (matches `review`)
- `feedbackBody` (matches `feedback`)
- `chatTranscript` (matches `chat`)

### System-keyword regex

Case-insensitive match. Matches → `system-injected`.

```
(?i)(knowledge|context|system|service|injected|cached|preloaded|fetched|loaded|enriched|computed)
```

Examples that match (→ `system-injected`):
- `knowledgeContext` (matches `knowledge`, `context`)
- `cachedLore` (matches `cached`)
- `systemMetadata` (matches `system`)
- `preloadedFacts` (matches `preloaded`)
- `enrichedProfile` (matches `enriched`)

### Confidence band

| Case | origin | originConfidence |
|---|---|---|
| Only user-keyword regex matches | `user-controlled` | 0.90 |
| Only system-keyword regex matches | `system-injected` | 0.90 |
| Neither regex matches | `unknown` (conservative → `user-controlled` for F10) | 0.40 |
| Both regexes match (conflict / ambiguous) | defer to Signal 2 | (computed by Signal 2) |

The 0.85 floor for clear naming-match is the design target; the actual value emitted depends on how many keyword hits the name has (e.g., `dreamText` has two user-keyword hits → 0.92).

### Conflict (ambiguous) cases

When both lists match, the naming signal is inconclusive. Fall through to Signal 2.

Examples that fall through:
- `userContext` (matches `user` AND `context`)
- `chatService` (matches `chat` AND `service`)
- `messageService` (matches `message` AND `service`)
- `inputCache` (matches `input` AND `cached`)

If Signal 2 also can't resolve, classify as `unknown` with `originConfidence: 0.40`.

## Signal 2 — call-graph proximity (medium confidence)

Apply when Signal 1 is inconclusive (conflict or no match). Trace where the var is assigned within its declaring scope; classify based on the assignment shape.

### Pattern 2a — service-call assignment → `system-injected`

If the var is bound from an awaited service call, classify as `system-injected`.

Regex (TS/JS):
```
(?:const|let|var)\s+<name>\s*=\s*await\s+([A-Z][A-Za-z0-9]*Service|[A-Z][A-Za-z0-9]*Cache|[A-Z][A-Za-z0-9]*Provider)\.
```

```ts
// Source
const knowledgeContext = await KnowledgeService.get(...);
// Classified
{name: "knowledgeContext", origin: "system-injected", originConfidence: 0.85}
```

Also catches:
- `await fetchContext(...)` → `system-injected` (function name suggests system fetch)
- `await LoreCache.read(...)` → `system-injected`
- `await client.getCache(...)` → `system-injected`

Confidence ≥0.80 for clear service-call pattern.

### Pattern 2b — form-input assignment → `user-controlled`

If the var traces to a form input field, URL param, or component prop that traces to a form field, classify as `user-controlled`.

Regex (TS/JS/TSX):
```
useState\(''\)|useState\(""\)|e\.target\.value|router\.query|searchParams\.|request\.body\.|req\.body\.
```

```tsx
// Source
const [dreamText, setDreamText] = useState('');
// ...
<textarea onChange={e => setDreamText(e.target.value)} />
// Classified
{name: "dreamText", origin: "user-controlled", originConfidence: 0.85}
```

Also catches:
- `const userMessage = req.body.message;` → `user-controlled` (Express handler)
- `const query = router.query.q;` → `user-controlled` (Next.js param)
- `const text = formData.get('text');` → `user-controlled` (FormData)
- Prop drilling: prop traces back to a `useState` form-field setter → `user-controlled`

Confidence ≥0.80 for clear form-input pattern.

### Pattern 2c — no traceable assignment → `unknown` (conservative)

If Signal 2 can't find the var's assignment within the declaring scope (e.g., imported from elsewhere with no resolvable origin), classify conservatively:
- `origin: "unknown"`
- `originConfidence: 0.40`

Per spec §3 Signal 2: F10 still fires on `unknown` (conservative — user can suppress via `audit.varOriginOverrides` config). This ensures we don't miss real user-input risks while still letting users dial down noise.

### Confidence band

| Case | origin | originConfidence |
|---|---|---|
| Pattern 2a fires (service-call) | `system-injected` | 0.80 |
| Pattern 2b fires (form-input) | `user-controlled` | 0.80 |
| Both 2a and 2b fire (very rare) | `unknown` | 0.40 |
| Neither fires (no traceable assignment) | `unknown` (treat as user-controlled for F10) | 0.40 |

## Override mechanism

Users can override detection via `.vibe-prompt/config/var-origins.json` (or the equivalent `audit.varOriginOverrides` field in the unified config — see `config.schema.json`):

```json
{
  "knowledgeContext": "system-injected",
  "dreamText": "user-controlled"
}
```

When an override exists for a var name:
- The override wins regardless of Signal 1 / Signal 2 output.
- `originConfidence` is set to 1.0.
- A note is emitted in the scan banner: *"Overrode 2 vars via varOriginOverrides config."*

## Combining the signals

For each captured var:

1. Check override config. If present → use it, confidence 1.0.
2. Apply Signal 1.
   - If only one keyword regex matches → done.
   - If neither matches → flag as `unknown`, confidence 0.40; still apply Signal 2 as enrichment.
   - If both match → conflict, defer to Signal 2.
3. Apply Signal 2 (when Signal 1 is inconclusive).
   - If Pattern 2a fires alone → `system-injected`, confidence 0.80.
   - If Pattern 2b fires alone → `user-controlled`, confidence 0.80.
   - If neither fires → `unknown`, confidence 0.40.

## Examples

| Var name | Signal 1 | Signal 2 | Final origin | Confidence |
|---|---|---|---|---|
| `dreamText` | user-keyword (two hits: dream, text) | n/a | user-controlled | 0.92 |
| `knowledgeContext` | system-keyword (two hits: knowledge, context) | n/a | system-injected | 0.92 |
| `prompt` | no match | no resolvable assignment | unknown | 0.40 |
| `userContext` | conflict (user + context) | `await KnowledgeService.get(...)` | system-injected | 0.80 |
| `chatService` | conflict (chat + service) | `const chatService = new ChatService();` | unknown | 0.40 |
| `userMessage` | user-keyword (user, message) | n/a | user-controlled | 0.92 |
| `cachedLore` | system-keyword (cached) | n/a | system-injected | 0.90 |

## Downstream consumers

- `:audit` F10/F11/F12 detection reads `origin`. Skips vars with `origin: "system-injected"`. Emits `originFilteredOut: true` on the audit finding when a candidate was filtered.
- `:audit` F10/F11/F12 still fires on `origin: "unknown"` (conservative default per spec §3 Signal 2).
- `:remediate` Category C targets only `origin: "user-controlled"` vars when building defense-block diffs.

## Conservative fallback (spec §3 Signal 2 invariant)

When unable to determine: classify as `user-controlled` for F10 evaluation purposes. The audit can over-fire (false positive) but never under-fire (false negative) on user-input vars. This biases toward safety; users can suppress via config when they know better.
