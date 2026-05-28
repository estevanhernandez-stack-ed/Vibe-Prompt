# Detection heuristics — scan

Read these before any inventory pass. Heuristics are best-effort; the SKILL must flag low-confidence detections.

## Step 1: Stack detection

| Signal | Stack class |
|---|---|
| `package.json` + `"typescript"` dep or `tsconfig.json` | typescript |
| `package.json` without `typescript` | javascript |
| `pyproject.toml` or `requirements.txt` or `setup.py` | python |
| Mixed (both `package.json` and `pyproject.toml`) | multi (scan both, report under one inventory) |

## Step 2: AI provider detection

Look for these imports in source files (exclude `node_modules/`, `.venv/`, `venv/`, `dist/`, `build/`):

| Import / require pattern | Provider |
|---|---|
| `@google/generative-ai`, `@google/genai`, `google.generativeai` | gemini |
| `@anthropic-ai/sdk`, `from anthropic` | anthropic |
| `openai` (TS/JS), `from openai` | openai |
| Other vendor SDKs | "other" |

Multiple providers in one app is normal; record all.

## Step 3: Registry detection

A "registry" is a central data structure mapping prompt IDs → content. Detection patterns:

- **Default-export-record (TS/JS):** const object literal with entries shaped `{ id, content, category, version }` or similar. Common in `*ConfigService.ts`, `*PromptService.ts`, `lib/prompts/*.ts`.
- **Class-static method (TS/JS):** `class ... { static async getPrompt(id) { ... } }` with a Firestore/DB-backed fetch.
- **Module-level dict (Python):** `PROMPTS = { "id": "..." }` in a `prompts.py` / `templates.py` / `system_prompts.py`.
- **YAML/JSON tables:** `prompts.yaml`, `prompts.json` files at any level.

Mark `registry.detected = true` if any match. Record `location` (file path) and `format` (one of: `default-export-record`, `class-static-fetcher`, `module-dict`, `yaml-table`, `json-table`).

## Step 4: Inline prompt detection

For each detected AI provider, search for these patterns:

**TypeScript/JavaScript:**
- Calls to `generateContent(...)`, `messages.create(...)`, `chat.completions.create(...)`, `client.complete(...)` with a `systemInstruction` / `system` / `system_message` field that is a string literal (not a registry-fetched value).
- Template strings (` ``...`` `) assigned to `const systemPrompt`, `const prompt`, etc., followed by use in an AI call within the same scope.
- Triple-quoted-equivalents in JSX strings starting with `You are`, `You must`, `Your role`, `Respond as`, `Act as`.

**Python:**
- `client.messages.create(...)`, `client.chat.completions.create(...)`, `model.generate_content(...)`, `model.invoke(...)` where the system field is a string literal.
- Triple-quoted strings `"""You are..."""` assigned to a name that's then used in an AI call.

For each hit, capture: file path, start line, end line of the literal, persona label (extracted), output shape, templated vars, voice-bearing flag, fallback presence, estimated token count.

## Step 5: Confidence flags

Tag every detection with confidence:

- **high:** matched a known SDK call site pattern directly.
- **medium:** matched a string-literal-assigned-to-named-const pattern but didn't confirm AI-call usage in the same file.
- **low:** matched persona-language regex (`You are the ...`) but no SDK call nearby. Likely a false positive; include but flag.

Aggregate confidence per inventory; if >40% of inline detections are low-confidence, note it in the scan output banner.

## What NOT to scan

- `node_modules/`, `.venv/`, `venv/`, `dist/`, `build/`, `coverage/`, `.next/`, `out/`, generated `*.lib.*` and `*.d.ts` files.
- Anything in `.git/`.
- Files larger than 500 KB (likely generated or non-source).
- Test files (`__tests__/`, `*.test.*`, `*.spec.*`) — include them in inventory but tag `testFile: true` so audit can de-prioritize.
