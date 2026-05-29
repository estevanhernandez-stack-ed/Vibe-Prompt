# Vendor clients — eval

How vibe-prompt calls each vendor's API. v0.1 supports Gemini + in-session agent.

## GeminiClient

### Authentication & Setup

**Important context on the two Google AI service paths.** Google exposes Gemini through two distinct endpoints with incompatible auth models:

| Endpoint | URL | Accepts API key? | Accepts OAuth Bearer? |
|---|---|---|---|
| AI Studio / Generative Language API | `generativelanguage.googleapis.com` | ✅ Yes | ❌ Not for personal Gmail accounts (returns `403 ACCESS_TOKEN_SCOPE_INSUFFICIENT` even with `cloud-platform` scope) |
| Vertex AI | `aiplatform.googleapis.com` | ❌ Not supported | ✅ Yes (OAuth + cloud-platform scope) |

**v0.1 uses the AI Studio endpoint with an API key.** OAuth Bearer via gcloud was attempted during the v0.1 cowpath round-trip and confirmed not to work — `gcloud auth login` from personal Gmail accounts can't access the Generative Language API regardless of scopes. (Antigravity's initial suggestion of `--scopes=...generative-language` was rejected because that scope doesn't exist; switching to default scopes hit the underlying account-level restriction.) **v0.2 will add a Vertex AI client** for the OAuth path.

**The v0.1 API key path:**

vibe-prompt reads `VIBE_PROMPT_GEMINI_API_KEY` (plugin-namespaced; see `security-hard-rules.md` for why we don't reuse the generic `GEMINI_API_KEY` name — it collides with Firebase deploy tooling).

**Three options to create the key — pick AI Studio or Service-Account-Bound for vibe-prompt's use case:**

| Source | URL / Method | Best for | Trade-off / Setup |
|---|---|---|---|
| **AI Studio (easiest)** | https://aistudio.google.com/app/apikey | Dev / eval / local testing | Simpler — no service-account binding required. Generates a key that works directly with `x-goog-api-key`. |
| **Service-Account-Bound API Key (recommended)** | `gcloud services api-keys` | Programmatic local dev setup | Extremely clean. Created via CLI, bound to a zero-privilege service account. Leaves no on-disk JSON keys. |
| Google Cloud Console | Cloud Console → APIs & Services → Credentials | Production / IAM-controlled use cases | As of 2026-05, Gemini-capable Cloud Console API keys must be bound to a service account first. Adds IAM setup ceremony that vibe-prompt doesn't need. |

Both create keys in the same GCP project and bill against the same line. For dev-local eval purposes, either AI Studio or a service-account-bound API key works.

**Option A: Service-Account-Bound API Key Setup (gcloud CLI)**

To set up a secure, zero-privilege service-account-bound API key via `gcloud` (bypassing the web UI entirely):

1. Create a dedicated zero-privilege service account (requires no IAM roles):
   ```bash
   gcloud iam service-accounts create vibe-prompt-key-bound \
     --description="Service account for vibe-prompt key binding" \
     --display-name="Vibe-Prompt Bound Key Service Account" \
     --project=celestia3
   ```
2. Create the API key bound to this service account (keep it unrestricted so the API gateway routes it correctly):
   ```bash
   gcloud services api-keys create \
     --display-name="Vibe-Prompt Bound Key" \
     --service-account="vibe-prompt-key-bound@celestia3.iam.gserviceaccount.com" \
     --project=celestia3
   ```
3. Copy the `keyString` (starts with `AQ.`) from the output and set it:
   - PowerShell: `[Environment]::SetEnvironmentVariable('VIBE_PROMPT_GEMINI_API_KEY', '<pasted key>', 'User')`
   - Bash: `export VIBE_PROMPT_GEMINI_API_KEY=<pasted key>`

**Option B: AI Studio Key Setup**

1. Go to https://aistudio.google.com/app/apikey
2. Click **Create API key**, pick your target GCP project from the dropdown.
3. Set the environment variable `VIBE_PROMPT_GEMINI_API_KEY` to the generated key.

If your key has zero restrictions, you do NOT need to set `VIBE_PROMPT_GEMINI_REFERER`. The Referer header path below is only for keys with HTTP referrer allowlists.

**Key configuration (when you want restrictions):**

- **API restrictions: Restrict key → Generative Language API only.** Belt-and-suspenders scope limit on what the key can do if it leaks. This is the load-bearing security control.
- **Application restrictions: three options, pick one:**
  - **None.** Simplest. Relies on the namespaced env var + API restriction for blast radius.
  - **IP addresses.** Real security against off-network use. Drawback: any network change (coffee shop, VPN, ISP-assigned IP shift) breaks vibe-prompt and the error is opaque (`API_KEY_HTTP_REFERRER_BLOCKED` even though it's IP).
  - **HTTP referrers.** Reusable with existing dev-host allowlists (`http://localhost:3000/*`, `https://*.dev/*`, etc.). vibe-prompt's curl can be told to spoof a referrer matching your allowlist via the optional `VIBE_PROMPT_GEMINI_REFERER` env var (see API call shape below). Note: referrer restrictions are spoofable by any client, so this is friction-against-accidents rather than security-against-actors — but if you already have a referrer allowlist for production and don't want to touch it, it's a clean reuse.
- Set the key value at Windows User scope (PowerShell `[Environment]::SetEnvironmentVariable('VIBE_PROMPT_GEMINI_API_KEY', '...', 'User')`) or in your shell profile (`export VIBE_PROMPT_GEMINI_API_KEY=...`). NEVER commit.
- (Optional) Set the referrer value at User scope too: `[Environment]::SetEnvironmentVariable('VIBE_PROMPT_GEMINI_REFERER', 'http://localhost:3000', 'User')` (or whatever matches your allowlist).

### API call shape

```bash
if [ -z "${VIBE_PROMPT_GEMINI_API_KEY:-}" ]; then
  echo "ERROR: VIBE_PROMPT_GEMINI_API_KEY not set. See vendor-clients.md for setup." >&2
  exit 1
fi

# Optional referrer header — only included if VIBE_PROMPT_GEMINI_REFERER is set.
# Use case: your API key has an HTTP referrer allowlist (e.g., localhost:3000 or a .dev domain)
# and you want vibe-prompt to match it rather than create a new less-restricted key.
REFERER_HEADER=()
if [ -n "${VIBE_PROMPT_GEMINI_REFERER:-}" ]; then
  REFERER_HEADER=(--header "Referer: $VIBE_PROMPT_GEMINI_REFERER")
fi

curl --silent --show-error \
  --request POST \
  --header "x-goog-api-key: $VIBE_PROMPT_GEMINI_API_KEY" \
  --header "Content-Type: application/json" \
  "${REFERER_HEADER[@]}" \
  --data @body.json \
  "https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent"
```

Notes:
- The key is read from the namespaced env var inline at the moment of the call. Do NOT copy it into intermediate variables, files, or log lines.
- `VIBE_PROMPT_GEMINI_REFERER` is optional. Only set it if your API key has an HTTP referrer allowlist. The value must match your allowlist exactly (e.g., `http://localhost:3000` or `https://yourapp.dev`).
- `${MODEL}` should be a published Gemini model name (e.g., `gemini-2.5-flash` or `gemini-3.5-flash`). The v1beta endpoint supports `gemini-3.5-flash` and `gemini-2.5-flash` directly. Note that `gemini-2.0-flash` is deprecated/unavailable for new users on the v1beta endpoint and will return 404.

Where `body.json` is:

```json
{
  "systemInstruction": {
    "parts": [{ "text": "<composed system prompt>" }]
  },
  "contents": [
    {
      "role": "user",
      "parts": [{ "text": "<user prompt with fixture vars filled>" }]
    }
  ],
  "generationConfig": {
    "temperature": 0.7,
    "topP": 0.9,
    "maxOutputTokens": 4096
  }
}
```

### Response parsing

Capture `response.candidates[0].content.parts[0].text` as the output text. Capture `usageMetadata.promptTokenCount` + `usageMetadata.candidatesTokenCount` as input/output tokens.

### Cost accounting

```
cost = (inputTokens * inputRate + outputTokens * outputRate) / 1_000_000
```

Use the rates in `cost-gates.md`. Add to running total.

### Error handling

| HTTP code | Treatment |
|---|---|
| 200 | Success |
| 401, 403 | Fatal — key invalid. Abort entire eval, friction-log `vendor-api-error` high |
| 429 | Retry once after 30s. On second 429, record `vendor-rate-limit-exhausted` for this prompt |
| 4xx (other) | Single retry. On second failure, record error for this prompt + friction-log |
| 5xx | Single retry after 5s. On second failure, record error |
| Network error | Single retry after 5s. On second failure, record error |

## InSessionAgentClient

### Call shape

Dispatch a subagent via the Agent tool with:

- `subagent_type: "general-purpose"`
- `model: "haiku"` (cheap; the baseline doesn't need top-tier reasoning)
- Prompt: the composed system prompt as system context + the fixture-filled user prompt as the task
- Instruction in prompt: "Produce ONLY the model output, no commentary. Do not preface or post-amble."

### Response parsing

The subagent's final text response IS the output. Strip any obvious framing (preamble like "Sure, here's the output:" if it sneaks in).

### Cost accounting

In-session agent calls are accounted as $0 toward the API cost ceiling (they bill against the user's session, which vibe-prompt doesn't track in v0.1). Token counts can still be captured from the subagent's usage metadata for the eval-result.

### Error handling

If the subagent fails (returns null or errors), treat as `error: "in-session-agent-failed"` for that prompt. Continue with the eval.

## OpenAIClient (v0.1 stub)

Stub implementation. Returns:

```
Error: OpenAI vendor not implemented in v0.1. Configure prod model as gemini or run vibe-prompt against a Gemini-stack app.
```

Friction-log `vendor-sdk-not-installed` high.

## Multi-vendor dispatch

For each prompt + each role (prod, baseline):

1. Look up the vendor: prod = `config.vendors.<vendor>` ; baseline = `agent.vendor` (defaults to "anthropic" via in-session Claude)
2. Dispatch the matching client
3. Capture output, tokens, cost
4. Append to eval-result `prompts[*].outputs.<role>`
