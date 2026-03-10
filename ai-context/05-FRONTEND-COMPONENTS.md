# Frontend Components ECES

## Struttura Componenti React

### App.tsx - Componente Principale

**Responsabilità**:
- Gestione routing tra tab
- Gestione stato autenticazione
- Layout principale con header e navigation

**Stati principali**:
```typescript
const [activeTab, setActiveTab] = useState<'recognize' | 'convert' | 'domains' | 'navigator' | 'matrix' | 'users' | 'analytics'>('recognize')
const [isAuthenticated, setIsAuthenticated] = useState(false)
const [currentUser, setCurrentUser] = useState<User | null>(null)
```

**Tab disponibili**:
- `recognize`: RecognitionPanel
- `convert`: ConversionPanel
- `navigator`: StringNavigator
- `matrix`: EuringMatrix
- `domains`: DomainPanel
- `users`: UserManagement (solo super_admin)
- `analytics`: Analytics (solo super_admin)

### RecognitionPanel.tsx

**Scopo**: Riconoscimento versione EURING

**Funzionalità**:
- Input singola stringa EURING
- Chiamata API `/api/euring/recognize`
- Visualizzazione versione riconosciuta con confidenza
- Analisi discriminante (opzionale)

**Stati**:
```typescript
const [euringString, setEuringString] = useState('')
const [result, setResult] = useState<RecognitionResult | null>(null)
const [loading, setLoading] = useState(false)
const [error, setError] = useState<string | null>(null)
```

**UI Elements**:
- Textarea per input stringa
- Pulsante "Riconosci Versione"
- Card risultato con:
  - Badge versione riconosciuta
  - Barra confidenza
  - Dettagli analisi

### ConversionPanel.tsx

**Scopo**: Conversione codici tra versioni

**Funzionalità**:
- Input stringa EURING
- Selezione versione source (dropdown)
- Selezione versione target (dropdown)
- Checkbox "Usa conversione semantica"
- Chiamata API `/api/euring/convert`
- Visualizzazione stringa convertita
- Note di conversione

**Stati**:
```typescript
const [inputString, setInputString] = useState('')
const [sourceVersion, setSourceVersion] = useState('2000')
const [targetVersion, setTargetVersion] = useState('2020')
const [useSemantic, setUseSemantic] = useState(true)
const [result, setResult] = useState<ConversionResult | null>(null)
```

**UI Elements**:
- Textarea input
- 2 Select per versioni
- Checkbox conversione semantica
- Pulsante "Converti"
- Card risultato con:
  - Stringa convertita (copiabile)
  - Note conversione
  - Dati semantici (se disponibili)

### StringNavigator.tsx

**Scopo**: Navigazione batch stringhe EURING

**Funzionalità**:
- Input multiplo: textarea o file upload (.txt, .csv)
- Parsing batch con API `/api/euring/parse/batch`
- Navigazione tra stringhe con pulsanti
- Visualizzazione campo-valore per stringa corrente
- Paginazione (50 stringhe per pagina)
- Domini semantici colorati

**Stati principali**:
```typescript
const [strings, setStrings] = useState<ParsedString[]>([])
const [currentIndex, setCurrentIndex] = useState(0)
const [currentPage, setCurrentPage] = useState(0)
const [inputText, setInputText] = useState('')
const [loading, setLoading] = useState(false)
```

**Layout**:
1. **Input Section**: Textarea + pulsanti "Analizza Singola"/"Analizza Batch" + upload file
2. **Stringa EURING corrente**: Box orizzontale con stringa in evidenza
3. **Navigazione grafica**: Pulsanti Precedente/Successiva con indicatore posizione
4. **Tabella campi**: 3 colonne (Icona Dominio | Campo | Valore)
5. **Navigazione stringhe**: Pulsanti per ogni stringa con info (osservatorio, anello, specie, data, coordinate)
6. **Paginazione**: Pulsanti "50 Precedenti"/"50 Successivi"

**Domini semantici**:
- Ogni campo ha icona e colore del dominio
- 7 domini: identification_marking (🔖), species (🦅), demographics (👤), temporal (📅), spatial (🌍), biometrics (📏), methodology (🔬)

**Filtri campi**:
- Nasconde campi tecnici (version, note, epe_error, parser_type, ecc.)
- Mostra solo campi EURING rilevanti con valori non vuoti

### EuringMatrix.tsx

**Scopo**: Matrice comparativa versioni EURING

**Funzionalità**:
- Visualizzazione tabella con tutte le versioni (colonne) e campi (righe)
- Ordinamento per ordine EPE
- Filtri per dominio semantico
- Editing campi (solo matrix_editor/super_admin)
- Lookup tables per valori validi
- Export dati (futuro)

**Stati**:
```typescript
const [matrixData, setMatrixData] = useState<MatrixData | null>(null)
const [selectedDomain, setSelectedDomain] = useState<string>('all')
const [editingField, setEditingField] = useState<EditingField | null>(null)
const [lookupTables, setLookupTables] = useState<Record<string, any>>({})
```

**Permessi**:
- **User**: Solo visualizzazione
- **Matrix Editor**: Editing campi (description, semantic_domain, data_type, length)
- **Super Admin**: Editing completo + gestione lookup tables

**UI Elements**:
- Filtro domini (dropdown)
- Tabella scrollabile orizzontale
- Celle editabili (doppio click)
- Modal per editing lookup tables
- Pulsanti salva/annulla

### DomainPanel.tsx

**Scopo**: Analisi evoluzione domini semantici

**Funzionalità**:
- Selezione dominio (7 domini disponibili)
- Timeline evoluzione attraverso versioni
- Grafici comparativi
- Analisi compatibilità tra versioni
- Visualizzazione campi per dominio

**Sub-componenti**:
- **DomainEvolutionTimeline**: Timeline verticale con milestone per versione
- **DomainEvolutionCharts**: Grafici a barre/linee per evoluzione campi
- **DomainComparison**: Confronto side-by-side tra 2 versioni

**Stati**:
```typescript
const [selectedDomain, setSelectedDomain] = useState<SemanticDomain>('identification_marking')
const [evolutionData, setEvolutionData] = useState<DomainEvolution | null>(null)
const [selectedVersions, setSelectedVersions] = useState<[string, string]>(['2000', '2020'])
```

**Visualizzazioni**:
1. **Timeline**: Evoluzione cronologica del dominio
2. **Charts**: Numero campi per versione, compatibilità
3. **Comparison**: Diff tra 2 versioni selezionate

### Login.tsx

**Scopo**: Autenticazione utente

**Funzionalità**:
- Form login (username, password)
- Chiamata API `/api/auth/login`
- Salvataggio JWT token in localStorage
- Redirect a dashboard dopo login
- Link a registrazione

**Stati**:
```typescript
const [username, setUsername] = useState('')
const [password, setPassword] = useState('')
const [error, setError] = useState<string | null>(null)
const [loading, setLoading] = useState(false)
```

**UI**:
- Logo EPE centrato
- Form con 2 input + pulsante
- Link "Registrati" per nuovi utenti
- Messaggi errore

### Register.tsx

**Scopo**: Registrazione nuovo utente

**Funzionalità**:
- Form registrazione (username, email, password, full_name)
- Validazione campi
- Chiamata API `/api/auth/register`
- Messaggio "In attesa approvazione admin"
- Link ritorno a login

**Validazioni**:
- Username: min 3 caratteri, alfanumerico
- Email: formato valido
- Password: min 8 caratteri
- Full name: min 3 caratteri

### UserManagement.tsx

**Scopo**: Gestione utenti (solo super_admin)

**Funzionalità**:
- Lista tutti gli utenti
- Filtri per ruolo/stato
- Approvazione nuovi utenti (is_active)
- Cambio ruolo utente
- Disattivazione utenti

**Stati**:
```typescript
const [users, setUsers] = useState<User[]>([])
const [filter, setFilter] = useState<'all' | 'pending' | 'active'>('all')
const [editingUser, setEditingUser] = useState<User | null>(null)
```

**Azioni**:
- Approva utente: `is_active = true`
- Cambia ruolo: `role = 'user' | 'matrix_editor' | 'super_admin'`
- Disattiva: `is_active = false`

### UserProfile.tsx

**Scopo**: Profilo utente corrente

**Funzionalità**:
- Visualizzazione dati utente
- Cambio password
- Statistiche utilizzo (se disponibili)

**Form cambio password**:
- Current password
- New password
- Confirm new password
- Validazione match

### Analytics.tsx

**Scopo**: Dashboard analytics (solo super_admin)

**Funzionalità**:
- Statistiche aggregate sistema
- Grafici utilizzo per utente
- Log query con filtri
- Export dati (futuro)

**Filtri**:
- Periodo (start_date, end_date)
- Utente
- Tipo query (recognition, conversion, parse)

**Visualizzazioni**:
- Totale query
- Query per tipo (pie chart)
- Query per utente (bar chart)
- Tempo medio processing
- Success rate
- Tabella log query

## Styling

### Approccio CSS

- **CSS Modules**: Ogni componente ha il suo `.css` file
- **Naming convention**: BEM-like (`.component-element--modifier`)
- **Colori domini**: Definiti in `semanticDomains.ts`
- **Responsive**: Media queries per mobile (<768px)

### Colori Domini Semantici

```css
.domain-identification_marking { color: #FF6B6B; }
.domain-species { color: #4ECDC4; }
.domain-demographics { color: #45B7D1; }
.domain-temporal { color: #FFA07A; }
.domain-spatial { color: #98D8C8; }
.domain-biometrics { color: #F7DC6F; }
.domain-methodology { color: #81C784; }
```

### Layout Responsive

```css
@media (max-width: 768px) {
  .navigation-buttons { flex-direction: column; }
  .matrix-table { overflow-x: auto; }
  .domain-charts { grid-template-columns: 1fr; }
}
```

## Gestione Stato

### Local State (useState)

Usato per:
- Form inputs
- Loading states
- Error messages
- UI toggles

### Props Drilling

- `currentUser` passato da App.tsx ai componenti che necessitano permessi
- Callback functions per azioni (onLoginSuccess, onLogout, ecc.)

### No State Management Library

- Progetto non usa Redux/MobX/Zustand
- Stato gestito con useState e props
- Auth state in App.tsx
- API calls dirette nei componenti

## API Integration

### Service Layer

**File**: `frontend/src/services/api.ts`

Classe `EuringAPI` con metodi statici:
```typescript
class EuringAPI {
  static async recognizeVersion(euringString: string): Promise<RecognitionResult>
  static async convertString(request: ConversionRequest): Promise<ConversionResult>
  static async parseEuringString(euringString: string, language: string): Promise<ParseResult>
  static async parseEuringStringsBatch(strings: string[], language: string): Promise<BatchParseResult>
  static async getVersionsMatrix(): Promise<MatrixData>
  static async getDomainEvolution(domain: string): Promise<DomainEvolution>
  static async updateMatrixField(update: FieldUpdate): Promise<UpdateResult>
  static async getLookupTable(version: string, field: string): Promise<LookupTable>
}
```

**Auth Service**: `frontend/src/services/auth.ts`

```typescript
class AuthService {
  login(username: string, password: string): Promise<LoginResponse>
  register(userData: RegisterData): Promise<RegisterResponse>
  logout(): void
  getCurrentUser(): Promise<User>
  isAuthenticated(): boolean
  isTokenExpired(): boolean
  getToken(): string | null
  changePassword(currentPassword: string, newPassword: string): Promise<void>
}
```

### Error Handling

```typescript
try {
  const result = await EuringAPI.recognizeVersion(string)
  setResult(result)
} catch (error: any) {
  setError(error.message || 'Errore durante il riconoscimento')
} finally {
  setLoading(false)
}
```

## Internazionalizzazione (Non Attiva)

Sistema i18n presente ma non utilizzato:
- `frontend/src/i18n/` contiene traduzioni IT/EN
- Hook `useTranslation()` disponibile ma non usato
- Tutti i testi sono hardcoded in italiano
- Selettore lingua rimosso dall'interfaccia

**Motivo**: Sistema i18n aveva problemi di sincronizzazione e race conditions. Decisione di mantenere solo italiano per semplicità.

## Performance Optimization

### Lazy Loading

Non implementato (bundle unico ~700KB)

### Memoization

Non usato (componenti semplici, re-render non problematici)

### Virtualization

Non necessaria (max 1000 stringhe batch, paginazione a 50)

### Code Splitting

Da implementare per ridurre bundle size

## Testing

### Unit Tests

Non presenti (da implementare)

### E2E Tests

Non presenti (da implementare)

### Manual Testing

Testing manuale su:
- Chrome/Brave (principale)
- Firefox
- Safari (limitato)

## Build & Deploy

### Development

```bash
cd frontend
npm install
npm run dev  # Vite dev server su port 5173
```

### Production Build

```bash
npm run build  # Output in frontend/dist/
```

### Deploy

```bash
# Crea tar da dist/
tar -czf frontend-build.tar.gz -C dist .

# Upload a server ISPRA
sshpass -p 'password' scp frontend-build.tar.gz user@10.158.251.79:/tmp/

# Estrai su server
ssh user@10.158.251.79 "sudo rm -rf /opt/eces/frontend/* && sudo tar -xzf /tmp/frontend-build.tar.gz -C /opt/eces/frontend/"

# Restart Nginx
ssh user@10.158.251.79 "sudo systemctl restart nginx"
```

## Known Issues Frontend

1. **Cache browser**: Dopo deploy necessario hard refresh (Ctrl+Shift+R)
2. **Bundle size**: 700KB JS, considerare code splitting
3. **Mobile layout**: Alcuni componenti non ottimizzati per mobile
4. **Accessibility**: Non testato con screen readers
5. **i18n system**: Presente ma disabilitato, da rimuovere completamente o fixare
