# Wie überwache ich den OpenCode Agent?

## 🚀 Agent starten

**Option 1: Mit Batch-Datei (Empfohlen für Windows)**
```bash
START_TESTX.bat
```

**Option 2: Direkt mit Python**
```bash
python autonomous_agent_demo.py --project-dir testx --model opencode/big-pickle
```

## 📊 Progress überwachen

### Methode 1: Progress-Checker (Empfohlen)

In einem **separaten Terminal/PowerShell Fenster**:

```bash
python check_progress.py testx
```

Das zeigt dir:
- ✅ Ob `feature_list.json` existiert (bedeutet: Initializer fertig!)
- 📈 Wieviele Features fertig vs. noch offen sind
- 🔄 Welche Session gerade aktiv ist
- 📁 Welche Dateien im Projekt erstellt wurden

**Tipp:** Führe das alle paar Minuten aus, um den Fortschritt zu sehen!

### Methode 2: Direkt im Agent-Fenster

Im Terminal wo der Agent läuft, siehst du:

```
[Tool: bash] - Agent führt einen Bash-Befehl aus
[Tool: write] - Agent schreibt eine Datei
[Tool: read] - Agent liest eine Datei
[Tool: edit] - Agent bearbeitet eine Datei
```

**Was bedeuten die Tools?**
- `bash` = Agent testet oder führt Commands aus
- `write` = Neue Datei wird erstellt
- `edit` = Existierende Datei wird geändert
- `read` = Agent liest Code
- `todowrite` = Agent plant nächste Schritte

### Methode 3: OpenCode Server Logs

Der OpenCode Server zeigt auch Aktivität. Wenn du den Server manuell gestartet hast:

```bash
# Im Terminal wo "opencode serve" läuft
# Du siehst API calls wie:
POST /session/:id/message
```

### Methode 4: Dateisystem beobachten

```bash
# Schaue dir die Dateien im testx Ordner an
dir testx

# Warte auf feature_list.json - das bedeutet Phase 1 ist fertig!
dir testx\feature_list.json
```

## 🕒 Zeitplan & Erwartungen

### Phase 1: Initializer (10-20+ Minuten)
- **Was passiert:** Agent erstellt `feature_list.json` mit ~200 Test Cases
- **Wie erkenne ich es:** 
  - Viel `[Tool: read]` und `[Tool: write]` Activity
  - `feature_list.json` wird erstellt
- **Progress checken:** `python check_progress.py testx`
- **Wichtig:** Diese Phase scheint manchmal zu "hängen" - ist aber normal! Der Agent arbeitet im Hintergrund.

### Phase 2: Coding Agent (mehrere Stunden)
- **Was passiert:** Agent implementiert Feature für Feature
- **Wie erkenne ich es:**
  - Ständige `[Tool: bash]`, `[Tool: write]`, `[Tool: edit]` Activity
  - Features in `feature_list.json` bekommen `"passes": true`
- **Progress checken:** `python check_progress.py testx` zeigt % Complete

## 🔍 Troubleshooting

### "Nichts passiert seit 10 Minuten"

**1. Check ob der Agent läuft:**
```bash
python check_progress.py testx
```
Schaut nach "ACTIVE" sessions.

**2. Check Server:**
```bash
curl http://localhost:4096/session
```
Sollte JSON mit sessions zurückgeben.

**3. Check Agent Logs:**
Schau ins Terminal wo du `START_TESTX.bat` gestartet hast.

### "feature_list.json existiert nicht nach 30+ Minuten"

Der Initializer hat Probleme. Mögliche Ursachen:
1. **Zu kurzes Token-Limit:** Check `testx/.opencode.json` - sollte keine `max_tokens` Limit haben
2. **Falsches Model:** Sollte `opencode/big-pickle` sein
3. **Server Problem:** Restart OpenCode server

**Fix:**
```bash
# Stop den Agent (Ctrl+C)
# Lösche testx
rmdir /S testx
# Starte neu
START_TESTX.bat
```

### "Agent stoppt mit Error"

Check die Error-Message. Häufige Probleme:
- **Unicode Error:** Schon gefixt in neuem Code
- **API Error 500:** Server Problem - restart `opencode serve`
- **Connection refused:** Server nicht gestartet - starte `opencode serve`

## 📈 Live-Monitoring Setup

**Terminal 1: Agent**
```bash
START_TESTX.bat
```

**Terminal 2: Progress Monitor (alle 2 Min)**
```bash
# PowerShell script für Auto-Refresh
while ($true) {
    Clear-Host
    python check_progress.py testx
    Start-Sleep -Seconds 120
}
```

**Terminal 3: Server (falls du ihn manuell startest)**
```bash
opencode serve
```

## 🎯 Was du sehen solltest

### Normaler Ablauf:

**Minute 0-1:**
```
Created new OpenCode session: ses_...
Sending prompt to OpenCode agent...
[Tool: read] - Reading app_spec.txt
```

**Minute 1-15:**
```
[Tool: read] - Lots of reading
[Tool: write] - Writing feature_list.json
[Tool: todowrite] - Planning
```

**Minute 15-20:**
```
✓ feature_list.json exists! (check_progress.py)
Total features: 200
Completed: 0 (0.0%)
```

**Danach (Stunden):**
```
[Tool: write] - Creating components
[Tool: bash] - npm install
[Tool: edit] - Fixing issues
[Tool: bash] - npm run build

✓ feature_list.json exists!
Total features: 200
Completed: 15 (7.5%)  <- steigt kontinuierlich
```

## 💡 Tipps

1. **Geduld!** Die erste Phase dauert wirklich 10-20+ Minuten
2. **Nicht panicken** wenn keine Output kommt - der Agent arbeitet!
3. **check_progress.py** ist dein Freund - nutze es!
4. **FREE Model** = langsamer aber kostenlos
5. **Session Logs** kannst du auch im OpenCode UI sehen (http://localhost:4096)

## 🆘 Hilfe

Wenn gar nichts klappt:

```bash
# Vollständiger Reset
# 1. Stop Agent (Ctrl+C)
# 2. Stop Server
# 3. Clean up
rmdir /S testx
# 4. Restart Server
opencode serve
# 5. Restart Agent (neues Terminal)
START_TESTX.bat
# 6. Monitor (noch ein Terminal)
python check_progress.py testx
```

---

**Happy Coding! 🚀**
