# Architettura Sistema ECES

## Architettura Generale

```
┌─────────────────────────────────────────────────────────┐
│                    NGINX (Port 80)                      │
│  - Reverse proxy per backend                            │
│  - Server statico per frontend                          │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┴─────────────────┐
        │                                   │
        ▼                                   ▼
┌──────────────────┐              ┌──────────────────┐
│  Frontend React  │              │  Backend FastAPI │
│  (Port 5173 dev) │              │  (Port 8000)     │
│  /opt/eces/      │              │  /opt/eces/      │
│  frontend/       │              │  backend/        │
└──────────────────┘              └──────────────────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    │                      │                      │
                    ▼                      ▼                      ▼
            ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
            │ PostgreSQL   │      │ JSON Files   │      │ File System  │
            │ (Analytics)  │      │ (EURING Data)│      │ (Users JSON) │
            └──────────────┘      └──────────────┘      └──────────────┘
```

## Backend Architecture

### Struttura Directory

```
backend/
├── app/
│   ├── api/                    # API endpoints
│   │   ├── euring_api.py      # EURING operations
│   │   ├── auth_api.py        # Authentication
│   │   └── analytics_api.py   # Analytics (Super Admin)
│   ├── auth/                   # Authentication system
│   │   ├── auth_service.py    # JWT token management
│   │   ├── dependencies.py    # Auth dependencies
│   │   └── models.py          # User models
│   ├── models/                 # Pydantic models
│   │   └── euring_models.py   # EURING data models
│   ├── services/               # Business logic
│   │   ├── recognition_engine.py
│   │   ├── conversion_service.py
│   │   ├── semantic_converter.py
│   │   ├── skos_manager.py
│   │   ├── field_translator.py
│   │   ├── lookup_table_service.py
│   │   ├── domain_*.py        # Domain analysis services
│   │   ├── database_service.py
│   │   ├── usage_logger.py
│   │   └── parsers/           # Version-specific parsers
│   ├── repositories/           # Data access
│   │   └── skos_repository.py
│   ├── middleware/             # Request/response middleware
│   │   └── logging_middleware.py
│   └── database/               # Database schemas
│       ├── schema.sql
│       └── schema.py
├── data/
│   ├── auth/
│   │   └── users.json         # User database (JSON)
│   └── euring_versions/       # EURING definitions
│       ├── versions/          # Version specs (JSON)
│       ├── domain_evolutions/ # Domain evolution data
│       └── conversion_mappings.json
├── tests/                      # Unit tests
└── main.py                     # FastAPI application entry
```

### Servizi Principali

#### 1. Recognition Engine
- **File**: `services/recognition_engine.py`
- **Funzione**: Identifica la versione EURING analizzando lunghezza e pattern
- **Algoritmo**: Discriminant analysis basato su field matching

#### 2. Conversion Service
- **File**: `services/conversion_service.py`
- **Funzione**: Converte stringhe tra versioni
- **Metodi**: 
  - Conversione diretta (field-to-field mapping)
  - Conversione semantica (preserva significato)

#### 3. SKOS Manager
- **File**: `services/skos_manager.py`
- **Funzione**: Gestisce definizioni versioni EURING
- **Dati**: Carica da JSON files in `data/euring_versions/`

#### 4. Semantic Domain Mapper
- **File**: `services/semantic_domain_mapper.py`
- **Funzione**: Assegna campi ai 7 domini semantici
- **Domini**: identification_marking, species, demographics, temporal, spatial, biometrics, methodology

#### 5. Field Translator
- **File**: `services/field_translator.py`
- **Funzione**: Traduce nomi campi e valori (IT/EN)
- **Nota**: Attualmente non usato (sistema solo italiano)

## Frontend Architecture

### Struttura Directory

```
frontend/
├── src/
│   ├── components/             # React components
│   │   ├── RecognitionPanel.tsx
│   │   ├── ConversionPanel.tsx
│   │   ├── StringNavigator.tsx
│   │   ├── EuringMatrix.tsx
│   │   ├── DomainPanel.tsx
│   │   ├── Analytics.tsx
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── UserManagement.tsx
│   │   └── UserProfile.tsx
│   ├── services/               # API clients
│   │   ├── api.ts             # EURING API calls
│   │   └── auth.ts            # Auth service
│   ├── types/                  # TypeScript types
│   │   └── euring-types.ts
│   ├── utils/                  # Utilities
│   │   └── semanticDomains.ts
│   ├── i18n/                   # Internationalization (non usato)
│   │   ├── index.ts
│   │   └── translations/
│   ├── hooks/                  # Custom React hooks
│   │   └── useTranslation.ts
│   ├── assets/                 # Static assets
│   │   └── images/
│   ├── App.tsx                 # Main app component
│   ├── App.css                 # Global styles
│   └── main.tsx                # Entry point
├── public/                     # Public assets
├── dist/                       # Build output
└── vite.config.ts             # Vite configuration
```

### Componenti Principali

#### 1. RecognitionPanel
- Riconoscimento versione EURING
- Input singola stringa
- Visualizzazione risultati con confidenza

#### 2. ConversionPanel
- Conversione tra versioni
- Selezione versione source/target
- Visualizzazione stringa convertita

#### 3. StringNavigator
- Caricamento batch (textarea o file)
- Navigazione tra stringhe
- Parsing e visualizzazione campo-valore
- Paginazione (50 stringhe per pagina)

#### 4. EuringMatrix
- Matrice comparativa versioni
- Editing campi (Matrix Editor/Super Admin)
- Lookup tables per valori validi

#### 5. DomainPanel
- Visualizzazione domini semantici
- Timeline evoluzione
- Grafici comparativi
- Analisi compatibilità

#### 6. Analytics
- Dashboard statistiche (Solo Super Admin)
- Query per utente/periodo
- Grafici utilizzo sistema

## Database

### PostgreSQL (Analytics)

```sql
-- Tabella utenti
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella query log
CREATE TABLE query_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    query_type VARCHAR(50),
    input_string TEXT,
    result JSONB,
    processing_time INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### JSON Files (Users)

```json
{
  "users": [
    {
      "id": "uuid",
      "username": "admin",
      "email": "admin@example.com",
      "full_name": "Administrator",
      "hashed_password": "bcrypt_hash",
      "role": "super_admin",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00"
    }
  ]
}
```

## API Architecture

### REST Endpoints

```
/api/euring/
  POST /recognize              # Riconosci versione
  POST /convert                # Converti stringa
  POST /parse                  # Parsa stringa singola
  POST /parse/batch            # Parsa batch stringhe
  GET  /versions/matrix        # Matrice versioni
  GET  /domain/evolution/{domain}
  POST /matrix/field/update    # Aggiorna campo (auth)
  GET  /lookup/{version}/{field}

/api/auth/
  POST /register               # Registrazione
  POST /login                  # Login (JWT)
  GET  /me                     # Profilo utente
  POST /change-password        # Cambio password
  GET  /users                  # Lista utenti (admin)
  PUT  /users/{id}            # Aggiorna utente (admin)

/api/analytics/
  GET  /queries                # Log query (super_admin)
  GET  /stats                  # Statistiche (super_admin)
```

## Autenticazione

### JWT Token Flow

```
1. User → POST /api/auth/login {username, password}
2. Backend → Verifica credenziali
3. Backend → Genera JWT token (exp: 24h)
4. Backend → Response {access_token, token_type, user}
5. Frontend → Salva token in localStorage
6. Frontend → Ogni richiesta: Header "Authorization: Bearer {token}"
7. Backend → Verifica token con dependencies.py
```

### Ruoli e Permessi

- **user**: Accesso base (recognition, conversion, navigator, domains)
- **matrix_editor**: + Editing matrice EURING
- **super_admin**: + Gestione utenti + Analytics

## Deployment Architecture

### Server ISPRA

```
/opt/eces/
├── frontend/              # Frontend build (Nginx serve da qui)
│   ├── index.html
│   └── assets/
├── backend/               # Backend Python
│   ├── app/
│   ├── data/
│   ├── venv/
│   └── main.py
└── logs/                  # Application logs
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name 10.158.251.79;
    
    # Frontend
    location / {
        root /opt/eces/frontend;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Systemd Services

```ini
# /etc/systemd/system/eces-backend.service
[Unit]
Description=ECES Backend Service
After=network.target postgresql.service

[Service]
Type=simple
User=amministratore
WorkingDirectory=/opt/eces/backend
ExecStart=/opt/eces/backend/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## Performance Considerations

1. **Frontend Build**: ~700KB JS bundle (considerare code splitting)
2. **API Response Time**: <100ms per recognition, <200ms per conversion
3. **Batch Processing**: Max 1000 stringhe per batch
4. **Concurrent Requests**: Max 10 concurrent per batch
5. **Database**: PostgreSQL per analytics, JSON per configurazioni (più veloce)

## Security

1. **JWT Tokens**: Expire dopo 24h
2. **Password Hashing**: bcrypt con salt
3. **CORS**: Configurato per dominio ISPRA
4. **SQL Injection**: Protetto da SQLAlchemy ORM
5. **XSS**: React auto-escape
6. **HTTPS**: Non configurato (rete interna)
