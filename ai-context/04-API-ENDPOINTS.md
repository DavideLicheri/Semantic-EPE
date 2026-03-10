# API Endpoints ECES

## Base URL

- **Development**: `http://localhost:8000`
- **Production (ISPRA)**: `http://10.158.251.79`

## Autenticazione

La maggior parte degli endpoint richiede autenticazione JWT.

**Header richiesto**:
```
Authorization: Bearer {jwt_token}
```

## Authentication Endpoints

### POST /api/auth/register
Registrazione nuovo utente (richiede approvazione admin).

**Request**:
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "full_name": "string"
}
```

**Response** (201):
```json
{
  "message": "User registered successfully. Waiting for admin approval.",
  "user": {
    "id": "uuid",
    "username": "string",
    "email": "string",
    "full_name": "string",
    "role": "user",
    "is_active": false
  }
}
```

### POST /api/auth/login
Login utente.

**Request**:
```json
{
  "username": "string",
  "password": "string"
}
```

**Response** (200):
```json
{
  "access_token": "jwt_token_string",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "username": "string",
    "email": "string",
    "full_name": "string",
    "role": "user|matrix_editor|super_admin",
    "is_active": true
  }
}
```

### GET /api/auth/me
Ottieni profilo utente corrente.

**Headers**: `Authorization: Bearer {token}`

**Response** (200):
```json
{
  "id": "uuid",
  "username": "string",
  "email": "string",
  "full_name": "string",
  "role": "string",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

### POST /api/auth/change-password
Cambio password utente.

**Headers**: `Authorization: Bearer {token}`

**Request**:
```json
{
  "current_password": "string",
  "new_password": "string"
}
```

**Response** (200):
```json
{
  "message": "Password changed successfully"
}
```

### GET /api/auth/users
Lista tutti gli utenti (solo super_admin).

**Headers**: `Authorization: Bearer {token}`

**Response** (200):
```json
{
  "users": [
    {
      "id": "uuid",
      "username": "string",
      "email": "string",
      "full_name": "string",
      "role": "string",
      "is_active": boolean,
      "created_at": "timestamp"
    }
  ]
}
```

### PUT /api/auth/users/{user_id}
Aggiorna utente (solo super_admin).

**Headers**: `Authorization: Bearer {token}`

**Request**:
```json
{
  "role": "user|matrix_editor|super_admin",
  "is_active": boolean
}
```

**Response** (200):
```json
{
  "message": "User updated successfully",
  "user": { ... }
}
```

## EURING Endpoints

### POST /api/euring/recognize
Riconosci versione EURING di una stringa.

**Headers**: `Authorization: Bearer {token}` (opzionale)

**Request**:
```json
{
  "euring_string": "string",
  "include_analysis": false
}
```

**Response** (200):
```json
{
  "success": true,
  "version": "euring_2000",
  "confidence": 0.95,
  "euring_string": "string",
  "length": 94,
  "discriminant_analysis": {
    "length_match": 1.0,
    "field_pattern_match": 0.9
  },
  "processing_time_ms": 15.5
}
```

### POST /api/euring/convert
Converti stringa EURING tra versioni.

**Headers**: `Authorization: Bearer {token}` (opzionale)

**Request**:
```json
{
  "euring_string": "string",
  "source_version": "2000",
  "target_version": "2020",
  "use_semantic": true
}
```

**Response** (200):
```json
{
  "success": true,
  "converted_string": "string",
  "source_version": "2000",
  "target_version": "2020",
  "conversion_method": "semantic",
  "conversion_notes": [
    "Field X mapped to Y",
    "Field Z added with default value"
  ],
  "semantic_data": {
    "domains_converted": 7,
    "fields_mapped": 32,
    "accuracy": 0.98
  },
  "processing_time_ms": 45.2
}
```

### POST /api/euring/parse
Parsa singola stringa EURING in campi.

**Headers**: `Authorization: Bearer {token}` (opzionale)

**Request**:
```json
{
  "euring_string": "string",
  "language": "it"
}
```

**Response** (200):
```json
{
  "success": true,
  "euring_string": "string",
  "detected_version": "euring_2000",
  "confidence": 0.95,
  "parsed_fields": {
    "Osservatorio": "TEST",
    "Specie riportata": "12345",
    "Sesso riportato": "M",
    "Età conclusa": "1",
    "Giorno": "15",
    "Mese": "05",
    "Anno": "2023",
    "Latitudine": "45.123",
    "Longitudine": "12.456"
  },
  "epe_compatible": true,
  "field_count": 36,
  "processing_time_ms": 25.3
}
```

### POST /api/euring/parse/batch
Parsa batch di stringhe EURING.

**Headers**: `Authorization: Bearer {token}` (opzionale)

**Request**:
```json
{
  "euring_strings": ["string1", "string2", "string3"],
  "language": "it"
}
```

**Response** (200):
```json
{
  "success": true,
  "total_strings": 3,
  "successful_parses": 3,
  "failed_parses": 0,
  "results": [
    {
      "index": 0,
      "success": true,
      "euring_string": "string1",
      "detected_version": "euring_2000",
      "confidence": 0.95,
      "parsed_fields": { ... },
      "epe_compatible": true,
      "field_count": 36
    }
  ],
  "version_distribution": {
    "euring_2000": 2,
    "euring_2020": 1
  },
  "processing_time_ms": 125.7
}
```

### GET /api/euring/versions/matrix
Ottieni matrice comparativa di tutte le versioni EURING.

**Headers**: `Authorization: Bearer {token}` (opzionale)

**Response** (200):
```json
{
  "success": true,
  "versions": [
    {
      "id": "euring_1966",
      "name": "EURING 1966",
      "year": 1966,
      "field_count": 20
    },
    {
      "id": "euring_2000",
      "name": "EURING 2000",
      "year": 2000,
      "field_count": 36
    }
  ],
  "field_matrix": [
    {
      "field_name": "scheme",
      "description": "Ringing scheme identifier",
      "semantic_meaning": "Ringing scheme identifier",
      "epe_order": 1,
      "versions": {
        "1966": {
          "position": 1,
          "name": "scheme",
          "data_type": "string",
          "length": 3,
          "description": "...",
          "semantic_domain": "identification_marking"
        },
        "2000": { ... }
      }
    }
  ],
  "processing_time_ms": 85.4
}
```

### GET /api/euring/domain/evolution/{domain}
Ottieni evoluzione di un dominio semantico.

**Headers**: `Authorization: Bearer {token}` (opzionale)

**Path Parameters**:
- `domain`: identification_marking | species | demographics | temporal | spatial | biometrics | methodology

**Response** (200):
```json
{
  "success": true,
  "domain": "biometrics",
  "evolution_data": {
    "domain_name": "Biometrics",
    "evolution_entries": [
      {
        "version": "euring_1966",
        "year": 1966,
        "fields_count": 3,
        "changes": [
          {
            "change_type": "added",
            "field_name": "wing_length",
            "semantic_impact": "Basic biometric measurement"
          }
        ]
      }
    ],
    "compatibility_matrix": {
      "1966->2000": "lossy",
      "2000->2020": "partial"
    }
  },
  "processing_time_ms": 42.1
}
```

### POST /api/euring/matrix/field/update
Aggiorna campo nella matrice (solo matrix_editor o super_admin).

**Headers**: `Authorization: Bearer {token}`

**Request**:
```json
{
  "field_name": "species_reported",
  "version": "2000",
  "property": "description",
  "value": "New description",
  "notes": "Updated for clarity"
}
```

**Response** (200):
```json
{
  "success": true,
  "field_name": "species_reported",
  "version": "2000",
  "property": "description",
  "old_value": "Old description",
  "new_value": "New description",
  "processing_time_ms": 18.3
}
```

### GET /api/euring/lookup/{version}/{field_name}
Ottieni lookup table per un campo.

**Headers**: `Authorization: Bearer {token}` (opzionale)

**Path Parameters**:
- `version`: 1966 | 1979 | 2000 | 2020
- `field_name`: nome del campo

**Response** (200):
```json
{
  "success": true,
  "field_name": "sex_reported",
  "version": "2000",
  "lookup_table": {
    "values": [
      {
        "code": "0",
        "description": "Sconosciuto",
        "description_en": "Unknown"
      },
      {
        "code": "1",
        "description": "Maschio",
        "description_en": "Male"
      }
    ]
  },
  "processing_time_ms": 8.2
}
```

## Analytics Endpoints (Solo Super Admin)

### GET /api/analytics/queries
Ottieni log delle query.

**Headers**: `Authorization: Bearer {token}`

**Query Parameters**:
- `user_id` (optional): Filtra per utente
- `start_date` (optional): Data inizio (ISO 8601)
- `end_date` (optional): Data fine (ISO 8601)
- `query_type` (optional): recognition | conversion | parse
- `limit` (optional): Numero risultati (default: 100)

**Response** (200):
```json
{
  "success": true,
  "queries": [
    {
      "id": 123,
      "user_id": "uuid",
      "username": "user1",
      "query_type": "recognition",
      "input_string": "...",
      "result": { ... },
      "processing_time": 25,
      "created_at": "2024-01-01T12:00:00"
    }
  ],
  "total_count": 1523,
  "processing_time_ms": 45.2
}
```

### GET /api/analytics/stats
Ottieni statistiche aggregate.

**Headers**: `Authorization: Bearer {token}`

**Query Parameters**:
- `start_date` (optional): Data inizio
- `end_date` (optional): Data fine

**Response** (200):
```json
{
  "success": true,
  "stats": {
    "total_queries": 5432,
    "queries_by_type": {
      "recognition": 2341,
      "conversion": 1876,
      "parse": 1215
    },
    "queries_by_user": {
      "user1": 234,
      "user2": 189
    },
    "avg_processing_time_ms": 32.5,
    "success_rate": 0.98
  },
  "processing_time_ms": 125.8
}
```

## Error Responses

Tutti gli endpoint possono restituire questi errori:

### 400 Bad Request
```json
{
  "detail": "Invalid input: ..."
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error: ..."
}
```

## Rate Limiting

- **Batch endpoints**: Max 1000 stringhe per richiesta
- **Concurrent requests**: Max 10 per batch processing
- **No rate limiting** per utenti autenticati su altri endpoint

## CORS

CORS è configurato per accettare richieste da:
- `http://localhost:5173` (development)
- `http://10.158.251.79` (production ISPRA)
