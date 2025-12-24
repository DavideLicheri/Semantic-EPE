# EURING Code Recognition System - API Documentation

## 🚀 Sistema Completato

Il backend EURING è ora completo con API REST funzionanti per riconoscimento e conversione dei codici EURING.

## 📋 Endpoints Disponibili

### 1. **Root Endpoint**
```
GET /
```
Restituisce informazioni sul sistema e lista degli endpoint disponibili.

**Response:**
```json
{
  "name": "EURING Code Recognition System",
  "version": "1.0.0",
  "description": "API for recognizing and converting EURING bird ringing codes",
  "endpoints": {
    "recognition": "/api/euring/recognize",
    "conversion": "/api/euring/convert",
    "batch_recognition": "/api/euring/batch/recognize",
    "batch_conversion": "/api/euring/batch/convert",
    "versions": "/api/euring/versions",
    "health": "/api/euring/health",
    "docs": "/docs"
  },
  "supported_versions": ["1966", "1979", "2000", "2020"]
}
```

### 2. **Riconoscimento Singolo**
```
POST /api/euring/recognize
```

**Request Body:**
```json
{
  "euring_string": "5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750",
  "include_analysis": true
}
```

**Response:**
```json
{
  "success": true,
  "version": "euring_1966",
  "confidence": 1.0,
  "euring_string": "5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750",
  "length": 55,
  "discriminant_analysis": {
    "has_pipes": false,
    "has_spaces": true,
    "has_dashes": false,
    "length": 55
  },
  "processing_time_ms": 15.3
}
```

### 3. **Conversione Singola**
```
POST /api/euring/convert
```

**Request Body:**
```json
{
  "euring_string": "5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750",
  "source_version": "1966",
  "target_version": "2020",
  "use_semantic": true
}
```

**Response:**
```json
{
  "success": true,
  "converted_string": "05320|TA12345|0|00000|3|9|20230211|1200|52.25|13.416666666666666|10|2|01|0|0|50.0|11.5|750.0|0|0|0|0",
  "source_version": "1966",
  "target_version": "2020",
  "conversion_method": "semantic",
  "conversion_notes": [
    "Sex code set to 9 (unknown) - not available in 1966",
    "Time set to 12:00 - not available in 1966"
  ],
  "processing_time_ms": 23.7
}
```

### 4. **Batch Recognition**
```
POST /api/euring/batch/recognize
```

**Request Body:**
```json
{
  "euring_strings": [
    "5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750",
    "05320|ISA12345|0|09920|3|2|20230521|1430|52.25412|-1.34521|1|10|01|0|0|135.5|19.5|4|2|0|0|2"
  ],
  "include_analysis": false,
  "max_concurrent": 10
}
```

**Response:**
```json
{
  "success": true,
  "total_processed": 2,
  "results": [
    {
      "success": true,
      "version": "euring_1966",
      "confidence": 1.0,
      "euring_string": "5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750",
      "length": 55
    },
    {
      "success": true,
      "version": "euring_2020",
      "confidence": 1.0,
      "euring_string": "05320|ISA12345|0|09920|3|2|20230521|1430|52.25412|-1.34521|1|10|01|0|0|135.5|19.5|4|2|0|0|2",
      "length": 91
    }
  ],
  "processing_time_ms": 45.2
}
```

### 5. **Batch Conversion**
```
POST /api/euring/batch/convert
```

**Request Body:**
```json
{
  "conversions": [
    {
      "euring_string": "5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750",
      "source_version": "1966",
      "target_version": "2020",
      "use_semantic": true
    }
  ],
  "max_concurrent": 10
}
```

### 6. **Versioni Supportate**
```
GET /api/euring/versions
```

**Response:**
```json
{
  "supported_versions": [
    {
      "version": "1966",
      "name": "EURING Code 1966",
      "description": "First version - space-separated format with 11 fields",
      "format": "space_separated",
      "typical_length": 55,
      "example": "5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750"
    },
    {
      "version": "1979",
      "name": "EURING Code 1979",
      "description": "Fixed-length concatenated format with 78 characters",
      "format": "fixed_length",
      "typical_length": 78
    },
    {
      "version": "2000",
      "name": "EURING Code 2000",
      "description": "Complex fixed-length format with encoded fields",
      "format": "fixed_length_encoded",
      "typical_length": 96
    },
    {
      "version": "2020",
      "name": "EURING Code 2020",
      "description": "Modern pipe-delimited format with decimal coordinates",
      "format": "pipe_delimited",
      "typical_length": 91
    }
  ],
  "conversion_matrix": {
    "1966": ["1979", "2000", "2020"],
    "1979": ["1966", "2000", "2020"],
    "2000": ["1966", "1979", "2020"],
    "2020": ["1966", "1979", "2000"]
  }
}
```

### 7. **Health Check**
```
GET /api/euring/health
```

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "recognition_engine": "healthy",
    "conversion_service": "healthy",
    "semantic_converter": "healthy"
  },
  "timestamp": "2024-01-20T10:30:00"
}
```

## 🚀 Avvio del Server

### Metodo 1: Diretto
```bash
cd backend
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Metodo 2: Con script
```bash
cd backend
python3 main.py
```

Il server sarà disponibile su:
- **API**: http://localhost:8000
- **Documentazione Interattiva**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📊 Features Implementate

### ✅ Riconoscimento
- [x] Riconoscimento singolo con analisi discriminanti
- [x] Batch processing con concorrenza configurabile
- [x] Confidence scoring al 100% per stringhe valide
- [x] Analisi dettagliata opzionale
- [x] Metriche di performance (processing time)

### ✅ Conversione
- [x] Conversione semantica tra tutte le versioni
- [x] Batch conversion con concorrenza
- [x] Note dettagliate sulle conversioni
- [x] Gestione campi mancanti con valori di default
- [x] Preservazione integrità semantica

### ✅ Gestione Errori
- [x] Validazione input robusta
- [x] Error handling globale
- [x] Messaggi di errore descrittivi
- [x] Status codes HTTP appropriati

### ✅ Performance
- [x] Processing asincrono
- [x] Batch processing ottimizzato
- [x] Concorrenza configurabile
- [x] Metriche di performance

## 🔧 Configurazione CORS

Il server è configurato per accettare richieste da:
- `http://localhost:3000` (React)
- `http://localhost:5173` (Vite)

Per aggiungere altri origins, modificare `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📝 Esempi di Utilizzo

### Python
```python
import requests

# Riconoscimento
response = requests.post("http://localhost:8000/api/euring/recognize", json={
    "euring_string": "5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750",
    "include_analysis": True
})
print(response.json())

# Conversione
response = requests.post("http://localhost:8000/api/euring/convert", json={
    "euring_string": "5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750",
    "source_version": "1966",
    "target_version": "2020",
    "use_semantic": True
})
print(response.json())
```

### JavaScript/TypeScript
```typescript
// Riconoscimento
const recognizeResponse = await fetch('http://localhost:8000/api/euring/recognize', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    euring_string: '5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750',
    include_analysis: true
  })
});
const recognizeData = await recognizeResponse.json();

// Conversione
const convertResponse = await fetch('http://localhost:8000/api/euring/convert', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    euring_string: '5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750',
    source_version: '1966',
    target_version: '2020',
    use_semantic: true
  })
});
const convertData = await convertResponse.json();
```

### cURL
```bash
# Riconoscimento
curl -X POST http://localhost:8000/api/euring/recognize \
  -H "Content-Type: application/json" \
  -d '{"euring_string":"5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750","include_analysis":true}'

# Conversione
curl -X POST http://localhost:8000/api/euring/convert \
  -H "Content-Type: application/json" \
  -d '{"euring_string":"5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750","source_version":"1966","target_version":"2020","use_semantic":true}'
```

## 🎯 Prossimi Passi

1. **Frontend Integration**: Collegare il frontend React/Vite alle API
2. **Testing**: Eseguire test completi con stringhe reali
3. **Deployment**: Preparare per produzione
4. **Monitoring**: Aggiungere logging e monitoring
5. **Documentation**: Completare documentazione PDF integration

## 📚 Risorse

- **Documentazione Interattiva**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/euring/health
- **Versioni**: http://localhost:8000/api/euring/versions