# AGENTS.md - OpenCode Harness Autonomous Coding

## 🚨 AKTUELLE PROBLEME & LÖSUNGEN

### Problem 1: Bezahltes Claude-Modell wird trotz OpenRouter/Mistral verwendet ✅
**Status:** BEHOBEN - client.py nutzt jetzt FREE Mistral

**Lösung:**
- [x] In `client.py` Zeile 182-196: OpenRouter FREE Mistral als Fallback verwenden
- [x] Sicherstellen dass NIEMALS anthropic direkt aufgerufen wird wenn OpenRouter Key vorhanden
- [x] Alle `anthropic/claude` References durch `mistralai/mistral-7b-instruct:free` ersetzen

### Problem 2: Nach feature_list.json Erstellung geht es nicht weiter ✅
**Status:** BEHOBEN - Auto-Switch zu Coding-Prompt implementiert

**Lösung:**
- [x] Log-Ausgabe bei Session-Wechsel implementiert
- [x] `is_first_run` Flag Logik überprüft (agent.py Zeile 112-136)
- [x] feature_list.json Validation nach Erstellung
- [x] Automatischer Prompt-Wechsel nach erster Session

### Problem 3: Max Tokens Konfiguration ✅
**Status:** BEHOBEN - Alle auf 200 reduziert

**Locations:**
- client.py:93 - Config: 200 tokens ✅
- client.py:187 - OpenRouter free: 200 tokens ✅
- client.py:195 - Anthropic: 200 tokens ✅
- client.py:204 - OpenCode: 200 tokens ✅
- client.py:223 - Custom: 200 tokens ✅
- client.py:225 - Free models: 200 tokens ✅
- client.py:241 - Fallback: 200 tokens ✅

**Lösung:**
- [x] Überall auf 200 tokens limitiert
- [x] Config max_tokens auf 200 reduziert

### Problem 4: API Keys werden nicht erkannt ❌
**Status:** NEU ENTDECKT - Environment Variables werden nicht gelesen

**Fehler:**
```
Debug: ANTHROPIC_API_KEY = NOT SET
Debug: OPENROUTER_API_KEY = NOT SET
Debug: OPENCODE_API_KEY = NOT SET
```

**Ursache:**
- OpenCode Docker Server hat den Key, aber er wird nicht an Python weitergegeben
- Environment Variables werden im PowerShell nicht korrekt gesetzt

**Lösung:**
```powershell
# Option 1: Direkt aus Docker .opencode.json lesen
# Docker Workspace: /workspace/.opencode.json
# Lokal: C:\Users\t.wilms\Documents\opencode_harness_autonomous_coding\my-app\.opencode.json

# Option 2: API Key aus /tmp/api-key lesen (wie in app_spec.txt erwähnt)
# Python-Skript soll /tmp/api-key lesen wenn keine ENV vars gesetzt

# Option 3: Key manuell in PowerShell setzen
$env:OPENROUTER_API_KEY = "sk-or-v1-..."
python autonomous_agent_demo.py ...
```

### Problem 5: OpenRouter Key Limit erreicht ❌
**Status:** NEU - Rate Limit überschritten

**Fehler:**
```
Key limit exceeded (total limit). Manage it using https://openrouter.ai/settings/keys
```

**Lösung:**
- [ ] Neuen OpenRouter API Key erstellen (https://openrouter.ai/settings/keys)
- [ ] Oder: Alternative free models nutzen (z.B. OpenCode eigene Models)
- [ ] Oder: Anthropic Key nutzen (aber PAID!)

---

## 📋 IMPLEMENTIERUNGSPLAN

### Phase 1: Kostenproblem beheben (PRIORITÄT 1) 🔥
**Ziel:** Sicherstellen dass KEINE bezahlten API-Calls gemacht werden

#### Task 1.1: client.py - Model Selection Fix
```python
# client.py Zeile 179-206 ersetzen:
if model == "auto":
    if openrouter_key:
        # IMMER FREE MISTRAL verwenden wenn OpenRouter Key vorhanden
        result = await client.session.chat(
            session_id,
            model_id="mistralai/mistral-7b-instruct:free",
            provider_id="openrouter",
            parts=[{"type": "text", "text": message}],
            extra_body={"max_tokens": 200}
        )
    elif anthropic_key:
        # WARNUNG: Dies ist PAID tier! Nur verwenden wenn explizit gewünscht
        print("⚠️  WARNING: Using PAID Claude model - costs apply!")
        result = await client.session.chat(
            session_id,
            model_id="claude-3-5-sonnet-20241022",
            provider_id="anthropic",
            parts=[{"type": "text", "text": message}],
            extra_body={"max_tokens": 200}  # Reduziert!
        )
    else:
        # OpenCode free fallback
        result = await client.session.chat(...)
```

#### Task 1.2: Config max_tokens reduzieren
```python
# client.py Zeile 93:
"max_tokens": 200,  # War: 1000
```

#### Task 1.3: Alle Fallback max_tokens auf 200 setzen
- Zeile 241: 2000 → 200
- Zeile 195: 1000 → 200

### Phase 2: Session-Fortsetzung debuggen (PRIORITÄT 2)
**Ziel:** Nach feature_list.json geht es automatisch weiter

#### Task 2.1: Logging verbessern
```python
# agent.py nach Zeile 113 einfügen:
print(f"🔍 DEBUG: is_first_run={is_first_run}")
print(f"🔍 DEBUG: feature_list.json exists={tests_file.exists()}")
print(f"🔍 DEBUG: Will use {'INITIALIZER' if is_first_run else 'CODING'} prompt")
```

#### Task 2.2: Feature-Liste Check
```python
# Nach feature_list.json Erstellung:
if tests_file.exists():
    print(f"✅ feature_list.json created with {len(json.loads(tests_file.read_text()))} features")
else:
    print("❌ ERROR: feature_list.json not found after creation!")
```

#### Task 2.3: Git Commit nach Feature-Liste
```python
# Nach feature_list.json Erstellung automatisch committen:
if is_first_run and tests_file.exists():
    subprocess.run(["git", "add", "feature_list.json"], cwd=project_dir)
    subprocess.run(["git", "commit", "-m", "Add feature_list.json"], cwd=project_dir)
    print("✅ feature_list.json committed")
```

### Phase 3: Auto-Continue Mechanismus (PRIORITÄT 3)
**Ziel:** Agent arbeitet kontinuierlich bis alle Features fertig sind

#### Task 3.1: Session-Loop Logik prüfen
- agent.py Zeile 144-173: While-Loop sollte weiterlaufen
- Status "continue" sollte Loop nicht beenden
- Nur bei "error" oder max_iterations stoppen

#### Task 3.2: Prompt-Switching
```python
# Nach jeder Session prüfen:
if iteration == 1 and is_first_run:
    prompt = get_coding_prompt()  # Wechsel zu Coding-Prompt
    is_first_run = False
else:
    prompt = get_coding_prompt()  # Weiter mit Coding
```

---

## 🔧 TESTING COMMANDS

### Test 1: Free Model Test
```bash
# Setze NUR OpenRouter Key
$env:OPENROUTER_API_KEY="sk-or-v1-..."
$env:ANTHROPIC_API_KEY=""

# Teste mit explizit free model
python autonomous_agent_demo.py --project-dir ./test_free --model openrouter/mistralai/mistral-7b-instruct:free --max-iterations 2
```

### Test 2: Session Continuation Test
```bash
# Erste Session - Feature-Liste erstellen
python autonomous_agent_demo.py --project-dir ./test_continue --max-iterations 1

# Prüfe ob feature_list.json existiert
ls ./test_continue/feature_list.json

# Zweite Session - sollte automatisch weitermachen
python autonomous_agent_demo.py --project-dir ./test_continue --max-iterations 1
```

### Test 3: Kosten-Monitor
```bash
# Checke OpenRouter Dashboard vor/nach Test
# https://openrouter.ai/activity

# Sollte $0.00 costs zeigen für free models
```

---

## 📝 CODE STYLE GUIDELINES

**Python:**
- Follow PEP 8 conventions
- Type hints required for function signatures
- Use async/await for OpenCode SDK calls
- Import organization: stdlib → third-party → local

**Error Handling:**
- Python: Use try/except with specific exception types
- Always handle OpencodeError/AsyncOpencode errors
- Log alle API errors mit vollem traceback

**Testing:**
- Pytest for Python
- Test files: test_*.py
- Commands: `python -m pytest -v`

---

## 🎯 SUCCESS CRITERIA

### Phase 1 Complete ✅
- [ ] Keine bezahlten API calls mehr
- [ ] OpenRouter free Mistral wird verwendet
- [ ] max_tokens überall ≤ 200
- [ ] Test zeigt $0.00 costs auf OpenRouter Dashboard

### Phase 2 Complete ✅
- [ ] feature_list.json wird erstellt
- [ ] Automatisch wird in Coding-Session gewechselt
- [ ] feature_list.json wird gefunden und gelesen
- [ ] Coding prompt wird geladen

### Phase 3 Complete ✅
- [ ] Agent läuft kontinuierlich (5-10 iterations)
- [ ] Features werden implementiert
- [ ] "passes": false → "passes": true Updates
- [ ] Git commits nach jedem Feature

---

## 🚀 NEXT ACTIONS

1. **SOFORT:** Fix client.py Model Selection (Task 1.1-1.3)
2. **DANN:** Test mit free model (Test 1)
3. **DANACH:** Debug Session Continuation (Task 2.1-2.3)
4. **ZULETZT:** Implement Auto-Continue (Task 3.1-3.2)

---

## 📚 RESOURCES

- OpenRouter Free Models: https://openrouter.ai/models?pricing=free
- OpenCode Python SDK: https://github.com/opencode-ai/opencode-python
- Anthropic API Pricing: https://www.anthropic.com/pricing#anthropic-api
