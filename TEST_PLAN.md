# OpenCode Model Selection Test Plan

## Purpose

Before submitting a bug report/feature request, we need to verify if the model selection issue occurs in the **official OpenCode TUI client** or only when using the Python SDK headless.

## Background

Our initial testing used the **Python SDK** with a **Docker server**, which revealed:
1. The server is only an LLM API proxy (doesn't execute tools)
2. Model selection parameters were ignored
3. Expensive models (Gemini 3 Pro, Claude Haiku) were used instead of configured free models

**However**, we may have misunderstood OpenCode's architecture:
- **Server**: LLM API proxy only
- **Client** (TUI): Executes tools locally + makes model selection

## Test Cases

### Test 1: Local TUI with Free Model Configuration

**Setup:**
1. Configure `.opencode.json` with free model:
   ```json
   {
     "model": "openrouter/mistralai/mistral-7b-instruct:free"
   }
   ```

2. Set environment variable:
   ```bash
   export OPENROUTER_API_KEY="your-key"
   ```

3. Run OpenCode TUI:
   ```bash
   cd test4
   opencode
   ```

4. Send a simple message:
   ```
   Hello, what model are you?
   ```

**Expected Result:**
- Model used: `mistralai/mistral-7b-instruct:free`
- Cost: $0.00

**Pass Criteria:**
✅ OpenRouter logs show only free model usage
✅ No unexpected charges

**Fail Criteria:**
❌ OpenRouter logs show paid models (Gemini 3 Pro, Claude Haiku, etc.)
❌ Charges appear despite free model configuration

---

### Test 2: Check OpenCode Session Logs

After Test 1, inspect:
```bash
cat ~/.local/share/opencode/storage/session/*/session_*.json
```

Look for:
- `"modelID"` field
- Verify it matches configured model

---

## Decision Matrix

| Test 1 Result | Test 2 Result | Action |
|--------------|--------------|---------|
| ✅ Pass | ✅ Correct model | **SDK-specific issue** - Feature request valid for SDK |
| ❌ Fail | ❌ Wrong model | **Core OpenCode issue** - Feature request valid for entire platform |
| ✅ Pass | ❌ Wrong model | **Logging bug** - Model works but logs incorrectly |
| ❌ Fail | ✅ Correct model | **Provider issue** - OpenRouter may be routing incorrectly |

---

## Next Steps

### If TUI Also Ignores Model Configuration:
→ **Submit feature request** with evidence from both SDK and TUI

### If TUI Respects Model Configuration:
→ **Do NOT submit** - Issue is specific to our misuse of the SDK architecture
→ Instead: Build custom harness without OpenCode SDK

---

## Test Execution

**Date:** _TBD_
**Tester:** _TBD_

### Results:

**Test 1:**
- Model used: _______________
- Cost: _______________
- OpenRouter logs: _______________

**Test 2:**
- Session modelID: _______________
- Matches config: ⬜ Yes ⬜ No

**Decision:**
- ⬜ Submit feature request
- ⬜ Build custom harness
- ⬜ Further investigation needed

**Notes:**
_____________________________________________
_____________________________________________
