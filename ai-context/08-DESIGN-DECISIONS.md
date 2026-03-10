# Decisioni Tecniche e Design ECES

## Scelte Architetturali

### 1. Monorepo vs Separate Repos
**Decisione**: Monorepo (frontend + backend nello stesso repository)

**Motivazioni**:
- Progetto piccolo/medio
- Team singolo
- Deploy sincronizzato
- Condivisione tipi/modelli più facile

**Alternative considerate**:
- Separate repos: Overhead eccessivo per dimensione progetto

### 2. Backend Framework: FastAPI
**Decisione**: FastAPI invece di Flask/Django

**Motivazioni**:
- Performance eccellenti (async/await)
- Validazione automatica con Pydantic
- Documentazione API automatica (Swagger/OpenAPI)
- Type hints nativi Python
- Moderno e ben mantenuto

**Alternative considerate**:
- Flask: Troppo minimale, manca validazione
- Django: Troppo pesante, ORM non necessario
- Node.js/Express: Team preferisce Python

### 3. Frontend Framework: React
**Decisione**: React con TypeScript

**Motivazioni**:
- Ecosistema maturo
- TypeScript per type safety
- Component-based architecture
- Facile integrazione con Vite
- Team familiare con React

**Alternative considerate**:
- Vue.js: Meno diffuso nel team
- Angular: Troppo pesante
- Svelte: Troppo nuovo, ecosistema limitato

### 4. Build Tool: Vite
**Decisione**: Vite invece di Create React App

**Motivazioni**:
- Build velocissimo (HMR istantaneo)
- Configurazione minimale
- Tree-shaking ottimale
- ES modules nativi
- CRA deprecato

**Alternative considerate**:
- Create React App: Deprecato, lento
- Webpack: Configurazione complessa
- Parcel: Meno controllo

### 5. State Management: No Library
**Decisione**: useState + props, no Redux/MobX/Zustand

**Motivazioni**:
- Applicazione non complessa
- Pochi stati condivisi
- Auth state in App.tsx sufficiente
- Evita boilerplate

**Alternative considerate**:
- Redux: Overkill per dimensione app
- Zustand: Non necessario
- Context API: Props drilling gestibile

### 6. Styling: CSS Modules
**Decisione**: CSS puro con modules, no CSS-in-JS

**Motivazioni**:
- Semplicità
- Performance (no runtime)
- Scoping automatico
- Facile debug
- No dipendenze extra

**Alternative considerate**:
- Styled Components: Runtime overhead
- Tailwind: Troppo verboso in JSX
- SASS: Non necessario

### 7. Database: PostgreSQL + JSON
**Decisione**: PostgreSQL per analytics, JSON per auth/config

**Motivazioni**:
- PostgreSQL: Query complesse analytics, ACID
- JSON: Semplicità per pochi utenti, backup facile
- Hybrid approach: Best of both worlds

**Alternative considerate**:
- Solo PostgreSQL: Overhead per auth
- Solo JSON: Limitato per analytics
- MongoDB: Non necessario (dati strutturati)

### 8. Authentication: JWT
**Decisione**: JWT tokens invece di sessions

**Motivazioni**:
- Stateless (scalabile)
- Standard industry
- Facile integrazione frontend
- No session storage backend

**Alternative considerate**:
- Sessions: Stateful, complesso
- OAuth2: Overkill per uso interno
- Basic Auth: Insicuro

### 9. Deployment: Nginx + Systemd
**Decisione**: Nginx reverse proxy + Systemd services

**Motivazioni**:
- Standard Linux
- Affidabile
- Facile configurazione
- Logging integrato
- Auto-restart

**Alternative considerate**:
- Docker: Overhead non necessario
- Apache: Nginx più performante
- PM2: Specifico Node.js

## Scelte Dati EURING

### 1. Storage: JSON Files
**Decisione**: Definizioni EURING in JSON files

**Motivazioni**:
- Dati read-only (raramente modificati)
- Facile versioning (Git)
- Performance lettura veloce
- Backup semplice
- No query complesse necessarie

**Alternative considerate**:
- Database: Overhead per dati statici
- YAML: Meno standard per API
- XML: Verboso

### 2. Semantic Domains: 7 Domini
**Decisione**: Organizzare campi in 7 domini semantici

**Motivazioni**:
- Logica chiara
- Facilita comprensione evoluzione
- Mapping conversioni più preciso
- Visualizzazione migliore

**Domini scelti**:
1. Identification & Marking
2. Species
3. Demographics
4. Temporal
5. Spatial
6. Biometrics
7. Methodology

**Alternative considerate**:
- Più domini: Troppo granulare
- Meno domini: Troppo generico
- No domini: Difficile navigazione

### 3. Conversion Strategy: Semantic
**Decisione**: Conversione semantica invece di posizionale

**Motivazioni**:
- Preserva significato dati
- Gestisce campi aggiunti/rimossi
- Più robusto a cambiamenti formato
- Migliore per conversioni lossy

**Alternative considerate**:
- Posizionale: Fragile, non gestisce evoluzione
- Hybrid: Complessità eccessiva

### 4. Version Recognition: Discriminant Analysis
**Decisione**: Algoritmo basato su lunghezza + pattern matching

**Motivazioni**:
- Veloce
- Accurato (>95% confidence)
- Semplice da implementare
- No ML necessario

**Alternative considerate**:
- Machine Learning: Overkill
- Solo lunghezza: Insufficiente
- Regex complessi: Fragili

## Scelte UI/UX

### 1. Single Page Application
**Decisione**: SPA con tab navigation

**Motivazioni**:
- Esperienza fluida
- No page reload
- State persistente
- Veloce

**Alternative considerate**:
- Multi-page: Più lento
- Server-side rendering: Non necessario

### 2. Batch Navigation: Paginazione
**Decisione**: 50 stringhe per pagina

**Motivazioni**:
- Performance (no virtualization needed)
- UX semplice
- Caricamento veloce

**Alternative considerate**:
- Infinite scroll: Confuso per utenti
- Virtualization: Complessità non necessaria
- Tutte insieme: Lento con 1000+ stringhe

### 3. Matrix View: Horizontal Scroll
**Decisione**: Tabella scrollabile orizzontalmente

**Motivazioni**:
- Mostra tutte versioni insieme
- Comparazione facile
- Standard per matrici

**Alternative considerate**:
- Vertical: Difficile comparare
- Accordion: Nasconde informazioni
- Separate views: Scomodo

### 4. Domain Colors: Fixed Palette
**Decisione**: 7 colori fissi per domini

**Motivazioni**:
- Riconoscimento visivo immediato
- Consistenza UI
- Accessibilità (contrasto)

**Colori scelti**:
- Identification: Rosso (#FF6B6B)
- Species: Turchese (#4ECDC4)
- Demographics: Blu (#45B7D1)
- Temporal: Arancione (#FFA07A)
- Spatial: Verde acqua (#98D8C8)
- Biometrics: Giallo (#F7DC6F)
- Methodology: Verde (#81C784)

## Scelte Internazionalizzazione

### 1. Solo Italiano (Attuale)
**Decisione**: Rimuovere sistema i18n, mantenere solo italiano

**Motivazioni**:
- Sistema i18n aveva bug (race conditions)
- Utenti primari italiani (ISPRA)
- Semplicità manutenzione
- Performance migliori

**Storia**:
- Inizialmente implementato i18n IT/EN
- Problemi sincronizzazione traduzioni
- Decisione di semplificare

**Futuro**:
- Se necessario inglese, re-implementare con sistema più robusto
- Considerare i18next invece di custom solution

## Scelte Performance

### 1. No Code Splitting
**Decisione**: Bundle unico (attualmente ~700KB)

**Motivazioni**:
- Applicazione non enorme
- Rete interna veloce
- Semplicità deployment

**Futuro**:
- Implementare se bundle > 1MB
- Split per route principali

### 2. No Caching Strategy
**Decisione**: Cache browser standard, no service worker

**Motivazioni**:
- Applicazione interna
- Aggiornamenti frequenti
- Complessità non giustificata

**Futuro**:
- Considerare se utenti remoti

### 3. Batch Processing: Sequential
**Decisione**: Processare stringhe sequenzialmente nel batch

**Motivazioni**:
- Semplicità codice
- Sufficiente per 1000 stringhe
- No race conditions

**Alternative considerate**:
- Parallel: Complessità, possibili race conditions
- Worker threads: Overkill

## Scelte Security

### 1. JWT in localStorage
**Decisione**: Salvare JWT in localStorage invece di cookie

**Motivazioni**:
- Rete interna (XSS risk basso)
- Semplicità implementazione
- No CSRF concerns

**Alternative considerate**:
- HttpOnly cookie: Più sicuro ma complesso
- SessionStorage: Perso al refresh tab

### 2. No HTTPS
**Decisione**: HTTP solo (no SSL/TLS)

**Motivazioni**:
- Rete interna ISPRA
- No dati sensibili trasmessi
- Complessità certificati non giustificata

**Futuro**:
- Implementare se esposto a internet

### 3. Password Policy: Minimal
**Decisione**: Solo min 8 caratteri

**Motivazioni**:
- Utenti interni fidati
- Approvazione admin richiesta
- Bilanciamento usabilità/sicurezza

**Futuro**:
- Aggiungere complessità se richiesto

## Scelte Testing

### 1. No Automated Tests (Attualmente)
**Decisione**: Solo testing manuale

**Motivazioni**:
- Progetto piccolo
- Team singolo
- Sviluppo rapido
- Budget limitato

**Futuro**:
- Aggiungere unit tests per logica critica
- E2E tests per flussi principali

### 2. Manual Testing Focus
**Decisione**: Testing manuale su browser reali

**Motivazioni**:
- Catch UI issues
- Verifica UX
- Più veloce per iterazioni rapide

**Browser testati**:
- Chrome/Brave (principale)
- Firefox (secondario)
- Safari (limitato)

## Lessons Learned

### 1. i18n Complexity
**Problema**: Sistema i18n custom aveva race conditions
**Soluzione**: Rimosso, mantenuto solo italiano
**Lezione**: Usare librerie mature (i18next) o evitare se non necessario

### 2. Cache Browser
**Problema**: Utenti vedevano versione vecchia dopo deploy
**Soluzione**: Hard refresh (Ctrl+Shift+R)
**Lezione**: Implementare cache busting o service worker

### 3. Batch Parse Identical Strings
**Problema**: Errore Pydantic con stringhe identiche
**Soluzione**: Da investigare
**Lezione**: Testare edge cases

### 4. JSON vs Database
**Problema**: Inizialmente tutto in database, lento
**Soluzione**: Hybrid approach (JSON per config, DB per analytics)
**Lezione**: Scegliere storage appropriato per tipo dato

### 5. Matrix Editing Permissions
**Problema**: Inizialmente tutti potevano editare
**Soluzione**: Ruoli matrix_editor e super_admin
**Lezione**: Pensare permessi da subito

## Future Improvements

### Short Term
1. Fix batch parse identical strings error
2. Implementare cache busting
3. Aggiungere unit tests critici
4. Ottimizzare bundle size (code splitting)

### Medium Term
1. Export risultati (CSV, Excel)
2. Grafici analytics più avanzati
3. Audit log completo
4. Email notifications

### Long Term
1. Mobile app (React Native?)
2. API pubblica per centri inanellamento
3. Machine learning per recognition
4. Real-time collaboration editing matrice

## Non-Goals

Cose deliberatamente NON implementate:

1. **Multi-tenancy**: Sistema single-tenant per ISPRA
2. **Real-time updates**: No WebSocket, polling sufficiente
3. **Offline mode**: Richiede connessione
4. **Mobile-first**: Desktop-first per utenti ricercatori
5. **Microservices**: Monolite sufficiente per scala
6. **GraphQL**: REST API sufficiente
7. **Server-side rendering**: SPA sufficiente
8. **Progressive Web App**: Non necessario
9. **Blockchain**: Assolutamente no 😄
10. **AI/ML**: Algoritmi deterministici sufficienti
