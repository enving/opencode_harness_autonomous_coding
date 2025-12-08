# Migration Plan: Claude Code SDK → OpenCode

## Projektübersicht

Dieses Repository enthält einen autonomen Coding-Agenten, der derzeit das Claude Code SDK (Python) verwendet. Ziel ist die Migration zu OpenCode (JavaScript/TypeScript), während die bewährte Architektur mit Zwei-Agenten-Muster beibehalten wird.

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

## Ziel-Architektur (OpenCode)

### Technologien
- **Language**: TypeScript/Node.js
- **SDK**: `@opencode-ai/sdk`
- **Pattern**: Zwei-Agenten-System (beibehalten)
- **Security**: OpenCode Permissions (angepasst)
- **Persistence**: Gleiche Mechanismen

### Neue Kernkomponenten
- `src/agent.ts` - Agenten-Session-Logik (TypeScript)
- `src/client.ts` - OpenCode Client-Konfiguration
- `src/security.ts` - Security Rules für OpenCode
- `src/progress.ts` - Fortschritts-Tracking (angepasst)
- `src/index.ts` - Main entry point
- `package.json` - Dependencies & Scripts
- `tsconfig.json` - TypeScript-Konfiguration

## Migrationsphasen

### Phase 1: Grundlagen schaffen
1. **Git Repository initialisieren** ✅
2. **Package.json erstellen** mit allen Dependencies
3. **TypeScript Setup** (tsconfig.json, build pipeline)
4. **Projektstruktur anlegen** (src/ Verzeichnis)
5. **OpenCode SDK installieren** und konfigurieren

### Phase 2: Core Components migrieren
1. **Client.ts erstellen** - OpenCode Client statt Claude SDK
2. **Security.ts anpassen** - Bash allowlist → OpenCode Permissions
3. **Agent.ts neu implementieren** - Session-Management mit OpenCode
4. **Progress.ts übernehmen** - Fortschritts-Tracking anpassen
5. **Index.ts erstellen** - Main entry point

### Phase 3: Agenten-Logik implementieren
1. **Session Management** - OpenCode Session API nutzen
2. **Zwei-Agenten-Muster** - Initializer + Coding Agent
3. **Prompt Integration** - Bestehende Prompts wiederverwenden
4. **Autonome Loop** - Session-basierte Iterationen
5. **Error Handling** - Robuste Fehlerbehandlung

### Phase 4: Features & Polish
1. **Security Testing** - Permissions verifizieren
2. **Performance Optimierung** - Session-Handling optimieren
3. **Logging & Monitoring** - Detailliertes Feedback
4. **CLI Interface** - Kommandozeilen-Argumente
5. **Documentation** - README und Code-Docs

## Technische Herausforderungen

### 1. API-Unterschiede
**Claude SDK**: `await client.query(message)` + Stream handling
**OpenCode**: `await client.session.prompt({ path, body })`

### 2. Security Model
**Claude**: Bash hooks + allowlist
**OpenCode**: Permissions system + tool restrictions

### 3. Session Management
**Claude**: Fresh client per session
**OpenCode**: Persistent sessions mit IDs

### 4. Error Handling
**Claude**: Exception-based
**OpenCode**: Response-based mit status codes

## Beibehaltene Konzepte

### ✅ Zwei-Agenten-Muster
- Initializer: Feature list generation + project setup
- Coding Agent: Feature implementation + testing

### ✅ Prompt System
- `prompts/app_spec.txt` - Projekt-Spezifikation
- `prompts/initializer_prompt.md` - Initializer-Prompt
- `prompts/coding_prompt.md` - Coding-Prompt

### ✅ Fortschritts-Tracking
- `feature_list.json` - Test cases als Source of Truth
- Git commits für Persistenz
- Session resume capability

### ✅ Security-First-Ansatz
- Bash command restrictions
- Filesystem sandboxing
- Tool access control

## Dependencies (Target)

```json
{
  "dependencies": {
    "@opencode-ai/sdk": "^1.0.0",
    "typescript": "^5.0.0",
    "tsx": "^4.0.0",
    "commander": "^11.0.0",
    "chalk": "^5.0.0",
    "ora": "^7.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "eslint": "^8.0.0",
    "prettier": "^3.0.0"
  }
}
```

## File Mapping (Python → TypeScript)

| Python File | TypeScript File | Anmerkungen |
|-------------|------------------|-------------|
| `agent.py` | `src/agent.ts` | Core agent logic |
| `client.py` | `src/client.ts` | OpenCode client |
| `security.py` | `src/security.ts` | Security rules |
| `progress.py` | `src/progress.ts` | Progress tracking |
| `prompts.py` | `src/prompts.ts` | Prompt utilities |
| `autonomous_agent_demo.py` | `src/index.ts` | Main entry |
| `requirements.txt` | `package.json` | Dependencies |
| `test_security.py` | `tests/security.test.ts` | Tests |

## Success Criteria

### Functional
- [ ] Autonomous agent builds complete applications
- [ ] Two-agent pattern works correctly
- [ ] Security model prevents unauthorized access
- [ ] Progress tracking and resume functionality
- [ ] CLI interface with all original options

### Technical
- [ ] TypeScript compilation without errors
- [ ] All tests passing
- [ ] Performance comparable to Python version
- [ ] Proper error handling and logging
- [ ] Clean, maintainable code structure

### User Experience
- [ ] Simple installation and setup
- [ ] Clear documentation and examples
- [ ] Intuitive command-line interface
- [ ] Helpful error messages
- [ ] Progress visibility during long runs

## Risks & Mitigations

### Risk 1: OpenCode API Changes
**Mitigation**: Version pinning + compatibility layer

### Risk 2: Security Model Differences
**Mitigation**: Comprehensive testing + fallback mechanisms

### Risk 3: Performance Regression
**Mitigation**: Benchmarking + optimization iterations

### Risk 4: TypeScript Learning Curve
**Mitigation**: Incremental migration + extensive documentation

## Timeline Estimate

- **Phase 1**: 2-3 Stunden (Setup)
- **Phase 2**: 4-6 Stunden (Core Components)
- **Phase 3**: 6-8 Stunden (Agent Logic)
- **Phase 4**: 3-4 Stunden (Polish)

**Gesamt**: 15-21 Stunden für vollständige Migration

## Next Steps

1. Beginne mit Phase 1: Grundlagen schaffen
2. Erstelle `progress.md` für detailliertes Tracking
3. Implementiere schrittweise jede Phase
4. Teste kontinuierlich während der Migration
5. Dokumentiere alle Entscheidungen und Herausforderungen