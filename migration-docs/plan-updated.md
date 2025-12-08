# 🎉 AKTUALISIERTER Migration Plan: Claude Code SDK → OpenCode Python SDK

## 🚀 GROSSE NEWS: Offizielle OpenCode Python SDK!

OpenCode hat eine offizielle Python SDK: https://github.com/sst/opencode-sdk-python

**Das bedeutet: Keine Migration zu TypeScript nötig!** Wir können in Python bleiben!

## Projektübersicht

Dieses Repository enthält einen autonomen Coding-Agenten, der derzeit das Claude Code SDK (Python) verwendet. Ziel ist die Migration zu OpenCode **Python SDK**, während die bewährte Architektur mit Zwei-Agenten-Muster beibehalten wird.

## Aktuelle Architektur

### Technologien
- **Language**: Python 3.x
- **SDK**: `claude-code-sdk>=0.0.25`
- **Pattern**: Zwei-Agenten-System (Initializer + Coding Agent)
- **Security**: Bash allowlist + Sandbox
- **Persistence**: `feature_list.json` + Git commits

### Kernkomponenten
- `agent.py` - Agenten-Session-Logik
- `client.py` - Claude SDK Client-Konfiguration
- `security.py` - Bash-Befehls-Filterung
- `progress.py` - Fortschritts-Tracking
- `autonomous_agent_demo.py` - Main entry point
- `prompts/` - Agenten-Prompts (bleiben unverändert)

## Ziel-Architektur (OpenCode Python SDK)

### Technologien
- **Language**: Python 3.x (bleibt gleich!)
- **SDK**: `opencode-ai` (neu)
- **Pattern**: Zwei-Agenten-System (beibehalten)
- **Security**: OpenCode Permissions (angepasst)
- **Persistence**: Gleiche Mechanismen

### Angepasste Kernkomponenten
- `agent.py` - Agenten-Session-Logik (angepasst für OpenCode)
- `client.py` - OpenCode Client-Konfiguration (neu)
- `security.py` - Security Rules für OpenCode (angepasst)
- `progress.py` - Fortschritts-Tracking (minimal angepasst)
- `autonomous_agent_demo.py` - Main entry point (minimal angepasst)
- `prompts/` - Agenten-Prompts (bleiben unverändert)
- `requirements.txt` - Dependencies aktualisiert

## Vereinfachte Migrationsphasen

### Phase 1: SDK Austausch
1. **OpenCode Python SDK installieren**
   ```bash
   pip install --pre opencode-ai
   ```

2. **Requirements.txt aktualisieren**
   - `claude-code-sdk` entfernen
   - `opencode-ai` hinzufügen

3. **Client.py neu implementieren**
   - OpenCode Client anstelle von Claude SDK
   - API-Aufrufe umwandeln
   - Session-Management anpassen

### Phase 2: Core Components anpassen
1. **Security.py anpassen**
   - Bash allowlist → OpenCode Permissions
   - Sandbox-Konfiguration übernehmen

2. **Agent.py anpassen**
   - Session-Handling mit OpenCode API
   - Response-Handling anpassen
   - Error handling übernehmen

3. **Progress.py minimal anpassen**
   - OpenCode-spezifische Ausgaben

### Phase 3: Testing & Integration
1. **Funktionalität testen**
2. **Performance optimieren**
3. **Dokumentation anpassen**

## API Mapping: Claude SDK → OpenCode SDK

### Client Creation
**Claude SDK (alt):**
```python
from claude_code_sdk import ClaudeSDKClient
client = ClaudeSDKClient(options=ClaudeCodeOptions(...))
```

**OpenCode SDK (neu):**
```python
from opencode_ai import AsyncOpencode
client = AsyncOpencode()
```

### Session Management
**Claude SDK (alt):**
```python
await client.query(message)
async for msg in client.receive_response():
    # Handle response
```

**OpenCode SDK (neu):**
```python
session = await client.session.create({title: "My session"})
result = await client.session.prompt({
    path: {id: session.id},
    body: {model: {...}, parts: [{type: "text", text: message}]}
})
```

### Security Configuration
**Claude SDK (alt):**
```python
security_settings = {
    "sandbox": {"enabled": True},
    "permissions": {"allow": ["Read(./**)", "Bash(*)"]},
    "hooks": {"PreToolUse": [HookMatcher(matcher="Bash", hooks=[bash_security_hook])]}
}
```

**OpenCode SDK (neu):**
```python
# Über OpenCode Server-Konfiguration oder Permissions API
permissions = {"allow": ["Read(./**)", "Bash(*)"]}
```

## Was bleibt gleich? ✅

- **Python als Sprache** - Keine Lernkurve für neue Sprache!
- **Projektstruktur** - Alle Dateien bleiben an ihrem Platz
- **Zwei-Agenten-Muster** - Initializer + Coding Agent
- **Prompts** - Keine Änderungen nötig
- **Security-Konzept** - Bash allowlist → Permissions
- **Fortschritts-Tracking** - feature_list.json + Git
- **CLI Interface** - Gleiche Argumente und Optionen

## Was ändert sich? 🔄

- **SDK Importe** - `claude_code_sdk` → `opencode_ai`
- **Client-Erstellung** - Neue API für Client-Initialisierung
- **Session-Management** - OpenCode Session API statt direkter Queries
- **Response-Handling** - Strukturierte Antworten statt Streams
- **Error Handling** - OpenCode-spezifische Exceptions

## Zeitrahmen (aktualisiert)

- **Alt (TypeScript Migration)**: 15-21 Stunden
- **Neu (Python SDK Migration)**: 4-6 Stunden

**Ersparnis: ~70% Zeit!** 🎉

## Dependencies (Target)

```txt
opencode-ai>=0.1.0
asyncio (built-in)
pathlib (built-in)
json (built-in)
os (built-in)
argparse (built-in)
```

## Success Criteria (unverändert)

### Functional
- [ ] Autonomous agent builds complete applications
- [ ] Zwei-Agenten-Muster funktioniert korrekt
- [ ] Security model verhindert unberechtigten Zugriff
- [ ] Progress tracking und Resume-Funktionalität
- [ ] CLI Interface mit allen originalen Optionen

### Technical
- [ ] Python 3.8+ Kompatibilität
- [ ] Alle Tests erfolgreich
- [ ] Performance vergleichbar mit Original
- [ ] Proper error handling und logging
- [ ] Clean, maintainable code structure

## Risiken & Mitigations (minimal)

### Risk 1: OpenCode Python SDK Unterschiede
**Mitigation**: API-Dokumentation studieren, schrittweise Migration

### Risk 2: Session Management Änderungen
**Mitigation**: Prototypen bauen, gründlich testen

### Risk 3: Performance Unterschiede
**Mitigation**: Benchmarking, Optimierung wo nötig

## Timeline Estimate (neu)

- **Phase 1**: 1-2 Stunden (SDK Austausch)
- **Phase 2**: 2-3 Stunden (Components anpassen)
- **Phase 3**: 1 Stunde (Testing & Polish)

**Gesamt**: 4-6 Stunden für vollständige Migration

## Next Steps

1. OpenCode Python SDK installieren und testen
2. Client.py migrieren
3. Agent.py anpassen
4. Security.py übernehmen
5. Umfassende Tests durchführen
6. Dokumentation aktualisieren

---

**Status**: Migration Strategy aktualisiert ✨  
**Letzte Aktualisierung**: 2025-12-08 (Python SDK Entdeckung!)  
**Nächster Schritt**: OpenCode Python SDK installieren