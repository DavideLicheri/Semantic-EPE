# Sistema di Autenticazione ECES

## Overview

ECES usa un sistema di autenticazione basato su JWT (JSON Web Tokens) con 3 livelli di autorizzazione.

## Architettura Auth

```
┌─────────────┐
│   Frontend  │
│   (React)   │
└──────┬──────┘
       │ 1. POST /api/auth/login
       │    {username, password}
       ▼
┌─────────────────────┐
│  Backend FastAPI    │
│  auth_api.py        │
└──────┬──────────────┘
       │ 2. Verifica credenziali
       ▼
┌─────────────────────┐
│  auth_service.py    │
│  - Hash password    │
│  - Genera JWT       │
└──────┬──────────────┘
       │ 3. JWT Token
       ▼
┌─────────────────────┐
│  Frontend           │
│  localStorage       │
│  - Salva token      │
└─────────────────────┘
       │ 4. Ogni richiesta
       │    Header: Authorization: Bearer {token}
       ▼
┌─────────────────────┐
│  dependencies.py    │
│  - Verifica token   │
│  - Estrae user      │
│  - Controlla perms  │
└─────────────────────┘
```

## Ruoli Utente

### 1. User (Utente Base)
**Permessi**:
- ✅ Riconoscimento versioni EURING
- ✅ Conversione codici
- ✅ Navigator stringhe batch
- ✅ Visualizzazione matrice EURING (read-only)
- ✅ Visualizzazione domini semantici
- ✅ Cambio propria password
- ❌ Editing matrice
- ❌ Gestione utenti
- ❌ Analytics

**Caso d'uso**: Ricercatori che usano il sistema per analisi dati

### 2. Matrix Editor
**Permessi**:
- ✅ Tutti i permessi di User
- ✅ Editing campi matrice EURING
  - Modifica description
  - Modifica semantic_domain
  - Modifica data_type
  - Modifica length
- ✅ Gestione lookup tables
- ❌ Gestione utenti
- ❌ Analytics

**Caso d'uso**: Esperti EURING che mantengono le definizioni dei campi

### 3. Super Admin
**Permessi**:
- ✅ Tutti i permessi di Matrix Editor
- ✅ Gestione utenti
  - Approvazione nuovi utenti
  - Cambio ruoli
  - Attivazione/disattivazione utenti
- ✅ Analytics dashboard
  - Visualizzazione log query
  - Statistiche utilizzo
  - Export dati

**Caso d'uso**: Amministratori sistema ISPRA

## Flusso Registrazione

```
1. Utente compila form registrazione
   ↓
2. POST /api/auth/register
   {username, email, password, full_name}
   ↓
3. Backend crea utente con:
   - role: "user"
   - is_active: false  ← IMPORTANTE
   - hashed_password
   ↓
4. Response: "In attesa approvazione admin"
   ↓
5. Super Admin vede utente in UserManagement
   ↓
6. Super Admin approva: is_active = true
   ↓
7. Utente può fare login
```

## Flusso Login

```
1. Utente inserisce username/password
   ↓
2. POST /api/auth/login
   ↓
3. Backend verifica:
   - Utente esiste?
   - Password corretta? (bcrypt.checkpw)
   - is_active = true?
   ↓
4. Se OK, genera JWT token:
   - Payload: {sub: user_id, role: role}
   - Expiration: 24 ore
   - Secret: da .env
   ↓
5. Response: {access_token, token_type, user}
   ↓
6. Frontend salva in localStorage:
   - key: "eces_token"
   - value: JWT string
   ↓
7. Frontend salva user in state
   ↓
8. Redirect a dashboard
```

## JWT Token Structure

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_uuid",
    "role": "user|matrix_editor|super_admin",
    "exp": 1234567890,
    "iat": 1234567890
  },
  "signature": "..."
}
```

## Verifica Token (Backend)

**File**: `backend/app/auth/dependencies.py`

### get_current_user
```python
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        # Decode JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        # Carica utente da database
        user = await auth_service.get_user_by_id(user_id)
        
        if user is None or not user.is_active:
            raise HTTPException(status_code=401)
            
        return user
    except JWTError:
        raise HTTPException(status_code=401)
```

### get_current_active_user
```python
async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
```

### require_matrix_edit_permission
```python
async def require_matrix_edit_permission(
    current_user: User = Depends(get_current_active_user)
) -> User:
    if current_user.role not in ["matrix_editor", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    return current_user
```

### require_super_admin
```python
async def require_super_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    if current_user.role != "super_admin":
        raise HTTPException(
            status_code=403,
            detail="Super admin access required"
        )
    return current_user
```

## Uso Dependencies negli Endpoint

### Endpoint Pubblico (no auth)
```python
@router.post("/api/euring/recognize")
async def recognize_euring(request: RecognitionRequest):
    # Nessuna autenticazione richiesta
    pass
```

### Endpoint con Auth Opzionale
```python
@router.post("/api/euring/recognize")
async def recognize_euring(
    request: RecognitionRequest,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    # Se autenticato, logga analytics
    if current_user:
        await usage_logger.log_query(current_user, ...)
    pass
```

### Endpoint Autenticato
```python
@router.get("/api/auth/me")
async def get_me(current_user: User = Depends(get_current_active_user)):
    return current_user
```

### Endpoint Matrix Editor
```python
@router.post("/api/euring/matrix/field/update")
async def update_field(
    request: FieldUpdateRequest,
    current_user: User = Depends(require_matrix_edit_permission)
):
    # Solo matrix_editor o super_admin
    pass
```

### Endpoint Super Admin
```python
@router.get("/api/analytics/queries")
async def get_queries(
    current_user: User = Depends(require_super_admin)
):
    # Solo super_admin
    pass
```

## Password Hashing

**Library**: `bcrypt`

### Hashing (Registrazione)
```python
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')
```

### Verifica (Login)
```python
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )
```

## Storage Utenti

### Database: JSON File

**File**: `backend/data/auth/users.json`

```json
{
  "users": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "admin",
      "email": "admin@ispra.it",
      "full_name": "Administrator",
      "hashed_password": "$2b$12$...",
      "role": "super_admin",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ]
}
```

### Perché JSON e non PostgreSQL?

- **Semplicità**: Pochi utenti (< 100)
- **Performance**: Lettura veloce, no query overhead
- **Backup**: File facilmente copiabile
- **No dipendenze**: Non serve PostgreSQL per auth

**Nota**: Analytics usa PostgreSQL, ma auth usa JSON per semplicità.

## Frontend Auth Service

**File**: `frontend/src/services/auth.ts`

```typescript
class AuthService {
  private readonly TOKEN_KEY = 'eces_token'
  private readonly API_URL = '/api/auth'

  async login(username: string, password: string): Promise<LoginResponse> {
    const response = await fetch(`${this.API_URL}/login`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({username, password})
    })
    
    if (!response.ok) throw new Error('Login failed')
    
    const data = await response.json()
    localStorage.setItem(this.TOKEN_KEY, data.access_token)
    return data
  }

  logout(): void {
    localStorage.removeItem(this.TOKEN_KEY)
  }

  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY)
  }

  isAuthenticated(): boolean {
    const token = this.getToken()
    if (!token) return false
    return !this.isTokenExpired()
  }

  isTokenExpired(): boolean {
    const token = this.getToken()
    if (!token) return true
    
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      return payload.exp * 1000 < Date.now()
    } catch {
      return true
    }
  }

  async getCurrentUser(): Promise<User> {
    const token = this.getToken()
    const response = await fetch(`${this.API_URL}/me`, {
      headers: {'Authorization': `Bearer ${token}`}
    })
    
    if (!response.ok) throw new Error('Failed to get user')
    return response.json()
  }
}

export const authService = new AuthService()
```

## Protected Routes (Frontend)

**File**: `frontend/src/App.tsx`

```typescript
function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [currentUser, setCurrentUser] = useState<User | null>(null)

  useEffect(() => {
    const checkAuth = async () => {
      if (authService.isAuthenticated() && !authService.isTokenExpired()) {
        try {
          const user = await authService.getCurrentUser()
          setCurrentUser(user)
          setIsAuthenticated(true)
        } catch {
          authService.logout()
        }
      }
    }
    checkAuth()
  }, [])

  if (!isAuthenticated) {
    return <Login onLoginSuccess={handleLoginSuccess} />
  }

  return (
    <div className="app">
      {/* Dashboard con tab */}
      {currentUser?.role === 'super_admin' && (
        <button onClick={() => setActiveTab('analytics')}>
          Analytics
        </button>
      )}
    </div>
  )
}
```

## Configurazione

### Backend (.env)

```bash
# JWT Configuration
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 ore

# Database
DATABASE_URL=postgresql://user:pass@localhost/eces

# CORS
CORS_ORIGINS=http://localhost:5173,http://10.158.251.79
```

### Generare SECRET_KEY

```python
import secrets
print(secrets.token_urlsafe(32))
```

## Security Best Practices

### ✅ Implementato

1. **Password Hashing**: bcrypt con salt
2. **JWT Expiration**: 24 ore
3. **HTTPS**: Non necessario (rete interna ISPRA)
4. **CORS**: Configurato per domini specifici
5. **SQL Injection**: Protetto (no SQL diretto)
6. **XSS**: React auto-escape
7. **Token in localStorage**: OK per rete interna

### ⚠️ Da Migliorare

1. **Refresh Tokens**: Non implementato (token scade dopo 24h, re-login necessario)
2. **Rate Limiting**: Non implementato
3. **2FA**: Non implementato
4. **Password Policy**: Minimo 8 caratteri (debole)
5. **Account Lockout**: Non implementato (brute force possibile)
6. **Audit Log**: Solo query log, non auth events

### ❌ Non Necessario (Rete Interna)

1. **HTTPS**: Rete interna ISPRA
2. **CSRF Protection**: JWT in header, non cookie
3. **Session Management**: Stateless JWT

## Credenziali Default

### Super Admin
- **Username**: `admin`
- **Password**: `admin`
- **Email**: `admin@ispra.it`
- **Role**: `super_admin`

**⚠️ IMPORTANTE**: Cambiare password dopo primo login in produzione!

## Troubleshooting Auth

### Token Expired
**Sintomo**: 401 Unauthorized dopo alcune ore
**Causa**: Token JWT scaduto (24h)
**Soluzione**: Re-login

### 403 Forbidden
**Sintomo**: Accesso negato a endpoint
**Causa**: Ruolo insufficiente
**Soluzione**: Verificare ruolo utente, contattare admin

### User Inactive
**Sintomo**: Login fallisce con "User not active"
**Causa**: `is_active = false`
**Soluzione**: Super admin deve approvare utente

### Token Invalid
**Sintomo**: 401 Unauthorized subito dopo login
**Causa**: SECRET_KEY cambiata o token corrotto
**Soluzione**: Logout + re-login, verificare SECRET_KEY

### CORS Error
**Sintomo**: Richieste bloccate da browser
**Causa**: Origine non in CORS_ORIGINS
**Soluzione**: Aggiungere origine in backend .env
