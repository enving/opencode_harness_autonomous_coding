# Feature Request: Client-Side Model Selection Control for SDK

## Summary

The OpenCode SDK currently ignores client-side model configuration, making it impossible to enforce cost controls for autonomous long-running agents. This creates unexpected costs and prevents use of free-tier models.

## Problem Description

When using the OpenCode Python SDK for autonomous coding agents, the server-side model selection logic overrides all client-side configuration, including:

1. `.opencode.json` configuration file
2. SDK method parameters (`model_id`, `provider_id`)
3. Docker environment variables (`DEFAULT_MODEL`)

### Expected Behavior

When configured with:

```json
{
  "model": "openrouter/meta-llama/llama-3.1-8b-instruct:free",
  "max_tokens": 200
}
```

And calling the SDK with **required parameters** as defined in the official API:

```python
# Official SDK signature from opencode-ai v0.1.0a36:
# async chat(id, *, model_id: str, provider_id: str, parts, extra_body, ...)

result = await client.session.chat(
    session_id,
    model_id="mistralai/mistral-7b-instruct:free",  # REQUIRED parameter
    provider_id="openrouter",                        # REQUIRED parameter
    parts=[{"type": "text", "text": message}],
    extra_body={"max_tokens": 200}
)
```

**Note:** According to the SDK's Python signature, `model_id` and `provider_id` are **required parameters**, not optional. We used the API correctly.

**Expected:** Server uses `mistralai/mistral-7b-instruct:free` (free tier, $0.00 cost)

### Actual Behavior

The OpenCode server ignores configuration and selects different models:

- `google/gemini-3-pro-preview` (paid, $0.15/request)
- `claude-haiku-4.5` via Amazon Bedrock (paid, $0.01-0.02/request)

**Evidence from Docker container inspection:**

```bash
# Environment variable explicitly set:
$ docker exec opencode-server env | grep MODEL
DEFAULT_MODEL=openrouter/meta-llama/llama-3.1-8b-instruct:free

# But session data shows different model was used:
$ docker exec opencode-server cat /root/.local/share/opencode/storage/message/.../msg_*.json
{
  "modelID": "google/gemini-3-pro-preview",
  "providerID": "openrouter",
  "cost": 0.014294
}
```

**Result:** Unexpected costs accumulate rapidly in long-running autonomous sessions.

### Evidence

OpenRouter usage logs from a 10-minute test session:

```
Dec 10, 08:56 PM - Gemini 3 Pro Preview - 19,849 tokens - $0.152
Dec 10, 08:56 PM - Claude Haiku 4.5 - 12,290 tokens - $0.0125
Dec 10, 08:54 PM - Gemini 3 Pro Preview - 12,617 tokens - $0.0136
Dec 10, 08:54 PM - Claude Haiku 4.5 - 1,862 tokens - $0.00192
(21+ similar requests)
```

**Total cost:** ~$0.30-0.50 for 10 minutes instead of $0.00 (free tier)

## Use Case

Building autonomous coding agents that:
- Run for hours/days implementing features
- Need predictable, controllable costs
- Should use free-tier models for development/testing
- Follow the [Anthropic Long-Running Agents Guide](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

## Proposed Solution

Add client-side control over model selection with one of these approaches:

### Option 1: Honor SDK Parameters (Preferred)

When `model_id` and `provider_id` are explicitly passed to `client.session.chat()`, use them without modification:

```python
# This should guarantee the exact model is used
result = await client.session.chat(
    session_id,
    model_id="mistralai/mistral-7b-instruct:free",
    provider_id="openrouter",
    enforce_model=True,  # New parameter to enforce exact model
    ...
)
```

### Option 2: Strict Mode Configuration

Add a configuration option to disable server-side model selection:

```json
{
  "model": "openrouter/meta-llama/llama-3.1-8b-instruct:free",
  "enforce_model": true,  // Disable server-side model switching
  "fallback_behavior": "error"  // Fail if model unavailable instead of switching
}
```

### Option 3: Model Allowlist

Allow users to specify which models are allowed:

```json
{
  "allowed_models": [
    "openrouter/mistralai/mistral-7b-instruct:free",
    "openrouter/meta-llama/llama-3.1-8b-instruct:free"
  ],
  "block_paid_models": true
}
```

## Impact

Without this feature:

❌ OpenCode SDK is unsuitable for cost-sensitive autonomous agents  
❌ Developers cannot control costs in long-running sessions  
❌ Free-tier development/testing is impossible  
❌ SDK behavior is unpredictable and undocumented  

With this feature:

✅ Developers have full cost control  
✅ Free-tier models can be guaranteed  
✅ Autonomous agents can run safely for hours/days  
✅ SDK behavior is predictable and documented  

## Workarounds Attempted

All failed to prevent server-side model switching:

1. ✅ Configured `.opencode.json` with explicit model
2. ✅ Passed model parameters via SDK methods
3. ✅ Set Docker environment variables
4. ✅ Used `extra_body` to limit `max_tokens`
5. ❌ **None prevented the server from selecting paid models**

## Environment

- **OpenCode Server:** Docker `ghcr.io/sst/opencode` (latest)
- **OpenCode Python SDK:** `opencode-ai` v0.1.0a36
- **Provider:** OpenRouter
- **Models Configured:** Free tier (`mistralai/mistral-7b-instruct:free`, `meta-llama/llama-3.1-8b-instruct:free`)
- **Models Actually Used:** Paid tier (Gemini 3 Pro, Claude Haiku)

### SDK Method Signature (verified):

```python
async def chat(
    self, id: str, *,
    model_id: str,              # REQUIRED - but ignored by server
    provider_id: str,           # REQUIRED - but ignored by server  
    parts: Iterable[...],
    extra_body: Body | None,    # Used for max_tokens - but ignored by server
    ...
) -> AssistantMessage
```

The parameters `model_id` and `provider_id` are **required** by the SDK API, yet the server overrides them.

## Additional Context

This issue affects autonomous coding workflows described in:
- [Anthropic's Long-Running Agents Guide](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- OpenCode SDK documentation for multi-session workflows

The lack of client-side model control makes OpenCode SDK incompatible with cost-controlled autonomous development, forcing developers to either:
1. Accept unpredictable costs
2. Implement custom harnesses with direct API calls (bypassing OpenCode entirely)

## References

- **Project Repository:** https://github.com/[user]/opencode_harness_autonomous_coding
- **Anthropic Guide:** https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- **OpenCode Docs:** https://opencode.ai/docs

---

**Is this a bug or a feature request?**

Both. It's a **bug** that configuration is ignored, and a **feature request** to add explicit client-side model control.

**Priority:** High - Affects SDK usability for autonomous agents and cost control.
