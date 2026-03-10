# Problemi Noti e Soluzioni ECES

## Problemi Attivi

### 1. Batch Parse con Stringhe Identiche
**Severità**: 🔴 Alta

**Descrizione**:
Quando si processano 3 o più stringhe EURING identiche in batch, il sistema restituisce errore Pydantic:
```
1 validation error for EuringBatchParseResponse
euring_string
  Field required [type=missing, input_value={'success': False, 'total...}
```

**Riproduzione**:
1. Vai a StringNavigator
2. Inserisci 3 stringhe identiche (es. stessa stringa EURING 2000)
3. Click "Analizza Batch"
4. Errore appare

**Causa Probabile**:
- Il modello `EuringBatchParseResponse` non ha campo `euring_string`
- Possibile confusione tra modelli response
- Potrebbe essere issue con validazione Pydantic quando result dict non contiene campo atteso

**Workaround**:
- Usare stringhe diverse
- Processare singolarmente

**Fix Proposto**:
1. Verificare modello `EuringBatchParseResponse` in `backend/app/models/euring_models.py`
2. Assicurarsi che `results` list contenga sempre `euring_string` per ogni item
3. Aggiungere test per edge case stringhe duplicate

**Priorità**: Alta (blocca funzionalità batch)

---

### 2. Cache Browser Dopo Deploy
**Severità**: 🟡 Media

**Descrizione**:
Dopo deployment di nuova versione frontend, utenti vedono versione vecchia fino a hard refresh.

**Riproduzione**:
1. Deploy nuova versione frontend
2. Utente apre browser (già usato prima)
3. Vede versione vecchia

**Causa**:
- Browser cache assets JS/CSS
- No cache busting implementato
- Service worker non configurato

**Workaround**:
- Hard refresh: Ctrl+Shift+R (Chrome/Firefox)
- Cmd+Shift+R (Safari)
- Clear browser cache

**Fix Proposto**:
1. Implementare cache busting con hash nei filename (Vite già lo fa)
2. Configurare headers Cache-Control appropriati in Nginx
3. Considerare service worker per controllo cache

**Priorità**: Media (workaround semplice)

---

### 3. Bundle Size Grande
**Severità**: 🟡 Media

**Descrizione**:
Bundle JavaScript frontend è ~700KB (minified), caricamento iniziale lento su connessioni lente.

**Impatto**:
- First load: 2-3 secondi su rete ISPRA
- Più lento su VPN remota

**Causa**:
- No code splitting
- Tutte dipendenze in bundle unico
- Chart libraries pesanti

**Workaround**:
- Nessuno (accettabile per rete interna)

**Fix Proposto**:
1. Implementare code splitting per route
2. Lazy load componenti pesanti (Analytics, DomainCharts)
3. Analizzare bundle con `vite-bundle-visualizer`
4. Considerare alternative più leggere per chart libraries

**Priorità**: Bassa (performance accettabile)

---

### 4. Sistema i18n Disabilitato
**Severità**: 🟢 Bassa (by design)

**Descrizione**:
Sistema internazionalizzazione presente nel codice ma non utilizzato. Tutto hardcoded in italiano.

**Storia**:
- Inizialmente implementato sistema i18n custom
- Race conditions e problemi sincronizzazione
- Decisione di semplificare: solo italiano

**Stato Attuale**:
- File i18n presenti ma non usati
- LanguageSelector rimosso
- Hook `useTranslation` non chiamato

**Fix Proposto**:
1. **Opzione A**: Rimuovere completamente codice i18n
2. **Opzione B**: Re-implementare con i18next (libreria matura)

**Priorità**: Bassa (funzionalità non richiesta)

---

### 5. Mobile Layout Non Ottimizzato
**Severità**: 🟡 Media

**Descrizione**:
Alcuni componenti non responsive su mobile/tablet:
- EuringMatrix: Scroll orizzontale difficile
- StringNavigator: Pulsanti troppo piccoli
- DomainCharts: Grafici non ridimensionati

**Impatto**:
- Usabilità ridotta su dispositivi mobili
- Non critico (utenti usano principalmente desktop)

**Workaround**:
- Usare desktop/laptop

**Fix Proposto**:
1. Aggiungere media queries per mobile
2. Ottimizzare layout tabelle per touch
3. Rendere grafici responsive

**Priorità**: Bassa (utenti target usano desktop)

---

## Problemi Risolti

### ✅ Sistema i18n Race Conditions
**Risolto**: 6 Marzo 2026

**Problema**:
Sistema i18n aveva race conditions, traduzioni non caricate correttamente.

**Soluzione**:
Rimosso sistema i18n, mantenuto solo italiano.

**File Modificati**:
- `frontend/src/App.tsx` - Rimosso LanguageSelector
- `frontend/src/components/LanguageSelector.tsx` - Eliminato

---

### ✅ Nginx 404 su Refresh
**Risolto**: Gennaio 2026

**Problema**:
Refresh pagina su route React causava 404 Nginx.

**Soluzione**:
Aggiunto `try_files $uri $uri/ /index.html;` in Nginx config.

**File Modificati**:
- `/etc/nginx/sites-available/eces`

---

### ✅ Performance Caricamento Iniziale
**Risolto**: Gennaio 2026

**Problema**:
Caricamento JS lento (1.3s), Nginx non serviva static files correttamente.

**Soluzione**:
Configurato Nginx per servire direttamente da `/opt/eces/frontend/` invece di proxy.

**File Modificati**:
- `/etc/nginx/sites-available/eces`

---

### ✅ CORS Errors
**Risolto**: Dicembre 2025

**Problema**:
Browser bloccava richieste API per CORS.

**Soluzione**:
Configurato CORS in FastAPI con origini corrette.

**File Modificati**:
- `backend/main.py`
- `backend/.env.local`

---

### ✅ JWT Token Expiration Non Gestita
**Risolto**: Dicembre 2025

**Problema**:
Token scaduto causava errori, nessun redirect a login.

**Soluzione**:
Aggiunto check `isTokenExpired()` in `authService`, auto-logout se scaduto.

**File Modificati**:
- `frontend/src/services/auth.ts`
- `frontend/src/App.tsx`

---

### ✅ Database Service Corrotto
**Risolto**: 6 Marzo 2026

**Problema**:
File `backend/app/services/database_service.py` aveva struttura corrotta:
- `database_service = DatabaseService()` nel mezzo della classe
- File troncato, parentesi non chiusa

**Soluzione**:
Ristrutturato file, spostato istanza globale alla fine.

**File Modificati**:
- `backend/app/services/database_service.py`

---

### ✅ StringNavigator Layout Sliding Right
**Risolto**: 6 Marzo 2026

**Problema**:
Nel StringNavigator, la stringa EURING e i campi "scivolavano a destra" causando overflow orizzontale.

**Soluzione**:
- Aggiunto `overflow-x: hidden` ai container
- Migliorato `word-break` e `overflow-wrap`
- Rimossa vecchia visualizzazione stringa verticale
- Aggiunta nuova sezione "Stringa EURING Originale" orizzontale sopra tabella

**File Modificati**:
- `frontend/src/components/StringNavigator.tsx`
- `frontend/src/components/StringNavigator.css`

---

## Limitazioni Note

### 1. No Refresh Tokens
**Descrizione**: JWT token scade dopo 24h, richiede re-login.

**Impatto**: Utenti devono fare login ogni giorno.

**Motivazione**: Semplicità implementazione, uso interno.

**Mitigazione**: Token expiration lungo (24h).

---

### 2. No Rate Limiting
**Descrizione**: Nessun rate limiting su API.

**Impatto**: Possibile abuse (teorico).

**Motivazione**: Rete interna, utenti fidati.

**Mitigazione**: Autenticazione richiesta per operazioni critiche.

---

### 3. No Automated Tests
**Descrizione**: Solo testing manuale.

**Impatto**: Rischio regressioni.

**Motivazione**: Budget limitato, team piccolo.

**Mitigazione**: Testing manuale accurato prima deploy.

---

### 4. No Real-time Updates
**Descrizione**: No WebSocket, no polling automatico.

**Impatto**: Modifiche altri utenti non visibili in real-time.

**Motivazione**: Non necessario per use case.

**Mitigazione**: Refresh manuale pagina.

---

### 5. Single Server Deployment
**Descrizione**: No load balancing, no failover.

**Impatto**: Downtime se server offline.

**Motivazione**: Uso interno, disponibilità non critica.

**Mitigazione**: Backup regolari, restart automatico servizi.

---

## Troubleshooting Guide

### Problema: Login Non Funziona

**Sintomi**:
- Errore "Invalid credentials"
- 401 Unauthorized

**Possibili Cause**:
1. Password errata
2. Utente non attivo (`is_active = false`)
3. Backend offline

**Debug Steps**:
```bash
# Check backend status
ssh amministratore@10.158.251.79 "systemctl status eces-backend"

# Check logs
ssh amministratore@10.158.251.79 "sudo journalctl -u eces-backend -n 50"

# Test API
curl http://10.158.251.79/api/auth/login -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

**Soluzioni**:
- Verificare credenziali
- Super admin deve approvare utente
- Restart backend se offline

---

### Problema: Matrice Non Carica

**Sintomi**:
- Spinner infinito
- Errore "Failed to load matrix"

**Possibili Cause**:
1. Backend offline
2. File JSON corrotti
3. Timeout rete

**Debug Steps**:
```bash
# Test API
curl http://10.158.251.79/api/euring/versions/matrix

# Check JSON files
ssh amministratore@10.158.251.79 "ls -la /opt/eces/backend/data/euring_versions/versions/"
```

**Soluzioni**:
- Restart backend
- Restore JSON da backup
- Aumentare timeout Nginx

---

### Problema: Conversione Fallisce

**Sintomi**:
- Errore "Conversion failed"
- Stringa convertita vuota

**Possibili Cause**:
1. Versione source errata
2. Stringa malformata
3. Mapping non disponibile

**Debug Steps**:
```bash
# Test riconoscimento prima
curl http://10.158.251.79/api/euring/recognize -X POST \
  -H "Content-Type: application/json" \
  -d '{"euring_string":"YOUR_STRING"}'

# Test conversione
curl http://10.158.251.79/api/euring/convert -X POST \
  -H "Content-Type: application/json" \
  -d '{"euring_string":"YOUR_STRING","source_version":"2000","target_version":"2020"}'
```

**Soluzioni**:
- Verificare versione source corretta
- Controllare formato stringa
- Verificare mapping esiste in `conversion_mappings.json`

---

### Problema: Analytics Non Mostra Dati

**Sintomi**:
- Dashboard vuota
- Errore "Failed to load analytics"

**Possibili Cause**:
1. PostgreSQL offline
2. Nessun dato loggato
3. Permessi insufficienti

**Debug Steps**:
```bash
# Check PostgreSQL
ssh amministratore@10.158.251.79 "systemctl status postgresql"

# Check database
ssh amministratore@10.158.251.79 "psql -U eces_user -d eces -c 'SELECT COUNT(*) FROM query_log;'"

# Check user role
# Deve essere super_admin
```

**Soluzioni**:
- Restart PostgreSQL
- Verificare ruolo utente
- Popolare database con query test

---

## Reporting Issues

### Come Segnalare un Bug

1. **Descrizione chiara**: Cosa succede vs cosa dovrebbe succedere
2. **Passi riproduzione**: Step-by-step per riprodurre
3. **Screenshot**: Se problema UI
4. **Logs**: Backend logs se disponibili
5. **Ambiente**: Browser, OS, rete (VPN?)

### Template Issue

```markdown
## Descrizione
[Descrizione chiara del problema]

## Riproduzione
1. Vai a...
2. Click su...
3. Vedi errore...

## Comportamento Atteso
[Cosa dovrebbe succedere]

## Comportamento Attuale
[Cosa succede invece]

## Screenshot
[Se applicabile]

## Logs
[Backend logs se disponibili]

## Ambiente
- Browser: Chrome 120
- OS: Windows 11
- Rete: VPN FortiClient
- User Role: matrix_editor
```

---

## Contatti

Per supporto tecnico:
- **Email**: [admin@ispra.it]
- **Server**: 10.158.251.79
- **Documentazione**: `/opt/eces/docs/`

---

## Changelog Problemi

### 2026-03-06
- ✅ Risolto: Sistema i18n race conditions
- ✅ Risolto: Database service corrotto
- ✅ Risolto: StringNavigator layout sliding
- 🔴 Nuovo: Batch parse stringhe identiche

### 2026-01-15
- ✅ Risolto: Nginx 404 su refresh
- ✅ Risolto: Performance caricamento

### 2025-12-20
- ✅ Risolto: CORS errors
- ✅ Risolto: JWT expiration handling
