# Composer interview — first-run-setup

How vibe-prompt captures the app's composer pattern at first-run, with concrete examples from Celestia3.

## Goal

Produce `.vibe-prompt/eval/composer.json` (validated against the composer schema) that describes what layers the target app stacks onto every model call, in what order, with what triggers.

## Interview flow

1. **Detect inventory.** If `.vibe-prompt/state/inventory.json` exists, read it. If not, ask the user to point at one or to run `/vibe-prompt:scan` first.

2. **Find the composer file.** Scan inventory for any `composer` hint OR search the target app for files that:
   - Define a function/method named like `generateContent`, `complete`, `invoke`, `send`
   - That function constructs the model request body
   - Common locations: `src/lib/<vendor>.ts`, `src/services/ai*.ts`, `lib/llm.py`

3. **Ask the user to confirm or correct.**

   > I think your composer lives at `src/lib/gemini.ts`. Does that look right? (Y / point me elsewhere)

4. **Read the file. Identify layers.** Parse for these patterns (in order they appear in code):

   | Pattern | Layer type |
   |---|---|
   | Direct string concatenation with a config field | `directive-field` (capture the field name) |
   | If/then injection based on a boolean flag | `conditional` (capture the condition expression) |
   | Call to a knowledge service or static content | `knowledge-injection` |
   | The call's own systemInstruction passed in | `task-instruction` |

5. **For each layer, capture the static text.** For `directive-field` and `knowledge-injection`, read the underlying constant/function and capture the resulting text verbatim. For `conditional`, capture both branches if both have static text.

6. **Render a preview.** Show the user:

   > Based on your composer, a call with `systemInstruction = "Analyze this dream"` and `contents = [user text]` would produce this composed system prompt for the model:
   >
   > <preview text>
   >
   > Confirm? (Y / let me correct)

7. **Write `composer.json`** in the target app at `.vibe-prompt/eval/composer.json`. Validate against schema.

## Concrete example: Celestia3

`src/lib/gemini.ts:54-153` (the `technomancerModel.generateContent` function) stacks these layers:

| Order | Layer ID | Type | Source |
|---|---|---|---|
| 1 | `directive-persona` | `directive-field` | `DEFAULT_DIRECTIVE.persona` in `ConfigService.ts:33` |
| 2 | `directive-master` | `directive-field` | `DEFAULT_DIRECTIVE.masterDirective` in `ConfigService.ts:34` |
| 3 | `format-default` OR `format-json` | `conditional` | If `systemInstruction` or any `contents.text` contains "json" → format-json; else → format-default |
| 4 | `knowledge-smart` OR `knowledge-primer` | `conditional` | If `directive.isKnowledgeSyncEnabled` → smart lore; else → hermetic primer |
| 5 | `task-instruction` | `task-instruction` | The call's own `systemInstructionContent` |
| 6 | `chaos-protocol` | `conditional` | If `allowEntropy === true` → chaos protocol literal |

For each `directive-field` and `conditional` literal layer, capture the actual text verbatim. For `task-instruction`, the text is the per-call argument (no static capture).

## Apps without a composer

If the app's call sites pass `system` / `systemInstruction` / `system_message` straight to the SDK with no pre-processing, `kind = "identity"` and `layers = []`. The composer-mimic step at eval time is a no-op.

## When the heuristic fails

If you can't find the composer or the user can't confirm the rendered preview, friction-log `composer-mimic-confirmation-required` (medium confidence) and ask the user to:

1. Paste the rendered composed prompt as it appears in production logs, OR
2. Edit the auto-detected layers in `.vibe-prompt/eval/composer.json` directly

Either way, only proceed when the user explicitly confirms the captured pattern.
