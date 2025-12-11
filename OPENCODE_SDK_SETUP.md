# OpenCode SDK Setup & Configuration

## Status: ✅ WORKING

Der OpenCode Python SDK ist jetzt korrekt konfiguriert und funktioniert mit eurem lokalen Server auf `http://localhost:4096`.

## Wichtige Erkenntnisse

### 1. Server & SDK Verbindung
- ✅ Server läuft auf `http://localhost:4096`
- ✅ SDK nutzt `AsyncOpencode(base_url="http://localhost:4096")`
- ✅ Sessions können erstellt und genutzt werden

### 2. Verfügbare Provider

Der Server unterstützt **3 Provider**:

| Provider ID | Name | Models | Kosten |
|------------|------|--------|--------|
| `opencode` | OpenCode Zen | 3 (big-pickle, grok-code, gpt-5-nano) | **FREE** ✅ |
| `mistral` | Mistral | 23 (ministral-3b, pixtral-large, etc.) | $0.04-$6/M tokens |
| `anthropic` | Anthropic | 21 (Claude Sonnet, Opus, etc.) | **PAID** ⚠️ |

### 3. Model Auswahl

**WICHTIG:** Die Model-Auswahl funktioniert über **zwei Wege**:

#### A) API Call Parameter
```python
await client.session.chat(
    session_id,
    model_id="big-pickle",      # Model ID
    provider_id="opencode",     # Provider ID
    parts=[{"type": "text", "text": "..."}]
)
```

#### B) `.opencode.json` Konfiguration
Die `.opencode.json` im Project-Directory setzt das **Default-Model**:

```json
{
  "provider": "opencode",
  "model": "big-pickle"
}
```

**⚠️ WICHTIG:** Der Server scheint die Config-Datei zu bevorzugen! Die API-Parameter werden möglicherweise überschrieben.

### 4. Empfohlene Konfiguration

**Für KOSTENLOSE Nutzung:**

```python
# client.py - send_prompt() Funktion
await client.session.chat(
    session_id,
    model_id="big-pickle",      # FREE OpenCode model
    provider_id="opencode",
    parts=[{"type": "text", "text": message}],
    extra_body={"max_tokens": 8000}
)
```

```json
// .opencode.json im Project-Directory
{
  "provider": "opencode",
  "model": "big-pickle"
}
```

**Alternative günstige Models:**
- `mistral/ministral-3b-latest` - $0.04/M tokens (sehr günstig)
- `mistral/ministral-8b-latest` - $0.10/M tokens

### 5. Angepasste Dateien

#### `client.py`
- ✅ `create_client()` nutzt jetzt `opencode/big-pickle` als Default
- ✅ `send_prompt()` validiert Provider (nur `mistral`, `anthropic`, `opencode`)
- ✅ Warnt bei PAID models (Anthropic)
- ✅ `.opencode.json` wird korrekt erstellt mit `provider` und `model` Feldern

#### `autonomous_agent_demo.py`
- Keine Änderungen nötig (nutzt bereits die richtige Struktur)

## Testen

```bash
# Test 1: SDK Verbindung testen
python test_opencode_connection.py

# Test 2: Agent mit FREE model starten
python autonomous_agent_demo.py --project-dir ./test_project --model auto
# Nutzt automatisch: opencode/big-pickle

# Test 3: Spezifisches Modell nutzen
python autonomous_agent_demo.py --project-dir ./test_project --model mistral/ministral-3b-latest

# Test 4: Anthropic (WARNUNG: COSTS!)
python autonomous_agent_demo.py --project-dir ./test_project --model anthropic/claude-3-5-sonnet-20241022
```

## Kosten-Kontrolle

### ✅ Sichere FREE Models:
- `opencode/big-pickle` - 100% kostenlos
- `opencode/grok-code` - 100% kostenlos
- `opencode/gpt-5-nano` - 100% kostenlos

### ⚠️ Günstige Models:
- `mistral/ministral-3b-latest` - $0.04/M tokens
- `mistral/ministral-8b-latest` - $0.10/M tokens

### ❌ TEURE Models (VERMEIDEN!):
- Alle `anthropic/*` Models - Kosten Geld!
- `mistral/pixtral-large-latest` - $2-6/M tokens

## Nächste Schritte

1. ✅ **Verifiziert:** SDK funktioniert mit lokalem Server
2. ✅ **Konfiguriert:** FREE OpenCode Models als Default
3. ⏳ **TODO:** Autonomous Agent mit FREE model testen
4. ⏳ **TODO:** Sicherstellen, dass `.opencode.json` im project_dir korrekt erstellt wird

## Troubleshooting

### Problem: "Using PAID Claude model"
**Lösung:** Prüfe `.opencode.json` im Project-Directory:
```bash
cat ./test_project/.opencode.json
# Sollte zeigen: "provider": "opencode", "model": "big-pickle"
```

### Problem: "Provider 'openrouter' not found"
**Lösung:** Der Server kennt keinen `openrouter` Provider! Nutze `opencode`, `mistral` oder `anthropic`.

### Problem: "Cost: $0.027 for response"
**Lösung:** Du nutzt ein PAID model! Prüfe:
1. `.opencode.json` - sollte `opencode/big-pickle` sein
2. API Call - sollte `provider_id="opencode"` nutzen

## OpenCode SDK Referenz

### Session erstellen
```python
session = await client.session.create(extra_body={})
session_id = session.id
```

### Message senden
```python
result = await client.session.chat(
    session_id,
    model_id="big-pickle",
    provider_id="opencode",
    parts=[{"type": "text", "text": "Hello!"}]
)
```

### Response verarbeiten
```python
# result ist ein AssistantMessage (Pydantic model)
if hasattr(result, 'parts'):
    for part in result.parts:
        if hasattr(part, 'text'):
            print(part.text)
```

### Providers abrufen
```python
providers_response = await client.app.providers()
# providers_response.providers ist eine Liste von Provider objekten
for p in providers_response.providers:
    print(f"{p.name}: {len(p.models)} models")
```
