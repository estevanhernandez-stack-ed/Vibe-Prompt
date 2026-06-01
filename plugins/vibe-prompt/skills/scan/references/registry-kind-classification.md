# Registry-kind classification

> Reference for `:scan`'s registry-kind classifier. Added in v0.7 to close the gap surfaced on Project-626Labs-1 where `config/modelRegistry.ts` triggered an F1 false-positive (it's a model-routing table, not a prompt-content registry).

Every registry detected by `:scan` is classified into one of four kinds. The classification writes to `inventory.registry.kind` and gates downstream audit logic — F1 fires only on `prompt-content` and `hybrid` registries.

## The four kinds

| `registry.kind` | Content shape | F1 fires? |
|---|---|---|
| `prompt-content` | String prompts keyed by id (`{ id: "you are a..." }`) | yes |
| `model-routing` | Model identifiers keyed by task/agent (`{ chat: "gemini-2.5-pro" }`) | no |
| `task-mapping` | Task descriptors / IO schemas keyed by id | no |
| `hybrid` | Mixes prompt content with model IDs (or task descriptors with embedded prompts) | yes |

## Classifier signal order

The classifier inspects each registry's value shape and runs three signals in order. First confident hit wins; absent confident hits → `hybrid` as the safe fallback.

### Signal 1 — Value type

For the exported registry's first 10 values (or all if fewer):

- **All values are plain strings** → strong vote for `prompt-content`
- **All values match `/^(gemini|claude|gpt|o)[\d.-]+/` model-id regex** → strong vote for `model-routing`
- **All values are objects with descriptive keys (`description`, `inputs`, `outputs`, `schema`)** → strong vote for `task-mapping`
- **Mixed (strings + objects, or strings that contain both prompt text AND model IDs)** → `hybrid`

### Signal 2 — Key naming

- Keys describing tasks/agents (`generateBio`, `summarizeThread`, `triviaQuestion`) — neutral
- Keys describing model roles (`mainChat`, `embed`, `fastFallback`) — vote for `model-routing`
- File or export name contains `model`/`Models`/`modelRegistry` — strong vote for `model-routing`
- File or export name contains `prompt`/`Prompts`/`promptRegistry` — strong vote for `prompt-content`
- File or export name contains `task`/`Tasks`/`taskRegistry` — strong vote for `task-mapping`

### Signal 3 — Inline content heuristic

For string values:
- Length >50 chars AND contains "You are" / "Act as" / second-person directive → `prompt-content`
- Length <30 chars AND matches a known model regex → `model-routing`

## prompt-content registry

**Detection heuristic:** values are mostly strings; strings are long-form (often >50 chars) and contain persona / directive language ("You are", "Act as"). The export or filename frequently includes `prompt` / `Prompt`.

**Canonical example** — Celestia3 `src/lib/ConfigService.ts`:

```typescript
export const PROMPTS = {
  natalReading: "You are Pilgrim. Compose a natal reading for {{birth}}...",
  synastryReport: "You are Pilgrim. Two charts: {{chartA}} and {{chartB}}...",
};
```

**Audit behavior:** F1 fires when prompt content bypasses this registry (inline `systemInstruction` at a call site that could have referenced `PROMPTS.<id>`).

## model-routing registry

**Detection heuristic:** values are short strings matching a model-id regex (`gemini-*`, `claude-*`, `gpt-*`, `o*-mini`). Filename or export name contains `model` / `Models` / `modelRegistry`. Keys describe task or agent roles (task-id → model-id mapping).

**Canonical example** — 626Labs `config/modelRegistry.ts` (the file that triggered the v0.6 false-positive):

```typescript
export const MODELS = {
  mainChat: "gemini-2.5-pro",
  embed: "text-embedding-004",
  fastFallback: "gemini-2.5-flash",
  vision: "gemini-2.5-pro",
};
```

**Audit behavior:** F1 does NOT fire on a model-routing registry — inline systemInstruction at a call site is not "bypassing" a model-routing table because the table doesn't carry prompts. F1b (no prompt-content registry detected) fires instead when the inventory has no prompt-content registry at all. F6 model-id consolidation (Category D-3) reads model-routing registries to confirm the canonical model-id source already exists.

## task-mapping registry

**Detection heuristic:** values are objects with descriptive metadata fields — `description`, `inputs`, `outputs`, `schema`, `requiredVars`. The export often shapes one entry per agent task. Some entries embed a prompt string; many don't.

**Canonical example** — typical Anthropic / multi-agent setup:

```typescript
export const TASKS = {
  generate: {
    description: "Produce a Wikipedia-style summary",
    inputs: ["topic", "tone"],
    outputs: "markdown",
    schema: SummarySchema,
  },
  critique: {
    description: "Score a draft against rubric",
    inputs: ["draft"],
    outputs: "json-object",
  },
};
```

**Audit behavior:** F1 does NOT fire — task descriptors aren't prompt content. If task entries embed prompt strings inline they get classified `hybrid` instead.

## hybrid registry

**Detection heuristic:** mixed value shapes — strings AND objects in the same registry, or strings that contain both prompt text AND model IDs in the same entry. Also the safe fallback when signals 1-3 produce no clear winner.

**Canonical example** — fused config that lists prompts + model IDs per agent:

```typescript
export const AGENTS = {
  pilgrim: {
    prompt: "You are Pilgrim. Compose...",
    model: "gemini-2.5-pro",
  },
  technomancer: {
    prompt: "You are Technomancer. Diagnose...",
    model: "gemini-2.5-flash",
  },
};
```

**Audit behavior:** F1 fires — hybrid contains prompt-content, so inline systemInstruction at call sites is bypassing the registry's prompt-bearing entries. F6 model-id consolidation also applies. The audit annotates findings with `registryKind: "hybrid"` for transparency.

## Output contract

The classifier writes to `inventory.registry.kind` (one of the four enum values). Confidence is not surfaced as a separate field — the classifier either picks confidently or falls back to `hybrid` as the safe option. Downstream audit logic (F1 in particular) reads `registry.kind` and branches accordingly.
