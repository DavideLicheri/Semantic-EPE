# Mappatura Semantica dei Campi EURING

## Approccio Semantico

Dato che le stringhe di esempio rappresentano uccelli diversi, creiamo una mappatura basata sul **significato semantico** dei campi piuttosto che sui valori specifici.

## Campi Semantici Identificati

### 1. IDENTIFICAZIONE SPECIE
**Semantica**: Codice che identifica la specie dell'uccello secondo il sistema EURING

| Versione | Campo | Posizione | Formato | Esempio |
|----------|-------|-----------|---------|---------|
| 1966 | species_code | Campo 1 | 4 cifre | `5320` |
| 1979 | species_code | 0-5 | 5 cifre | `05320` |
| 2000 | ? | Codificato | ? | Da identificare |
| 2020 | species_code | Campo 1 | 5 cifre | `05320` |

**Regole di Conversione**:
- 1966 → 1979/2020: Aggiungere zero iniziale
- 1979/2020 → 1966: Rimuovere zero iniziale

### 2. IDENTIFICAZIONE ANELLO
**Semantica**: Numero univoco dell'anello applicato all'uccello

| Versione | Campo | Posizione | Formato | Esempio |
|----------|-------|-----------|---------|---------|
| 1966 | ring_number | Campo 2 | 2 lettere + 5 cifre | `TA12345` |
| 1979 | ring_number | 7-14 | 1 lettera + 6 cifre | `A12345 ` |
| 2000 | ring_number | 10-17 | 7 cifre | `7285004` |
| 2020 | ring_number | Campo 2 | 3 lettere + 5 cifre | `ISA12345` |

**Regole di Conversione**:
- Mantenere la parte numerica quando possibile
- Adattare il formato delle lettere secondo la versione target
- Gestire perdita di informazioni nelle conversioni

### 3. SCHEMA/PAESE
**Semantica**: Identificazione dello schema di inanellamento o paese

| Versione | Campo | Posizione | Formato | Esempio |
|----------|-------|-----------|---------|---------|
| 1966 | N/A | - | - | Non presente |
| 1979 | scheme_country | 5-7 | 2 lettere | `IS` |
| 2000 | scheme_code | 0-4 | 4 caratteri | `IABA` |
| 2020 | N/A | - | - | Non presente |

**Regole di Conversione**:
- Usare mapping tra codici paese e schemi
- Valori di default quando non disponibili

### 4. CLASSIFICAZIONE ETÀ
**Semantica**: Categoria di età dell'uccello al momento della cattura

| Versione | Campo | Posizione | Formato | Esempio |
|----------|-------|-----------|---------|---------|
| 1966 | age_code | Campo 3 | 1 cifra | `3` |
| 1979 | age_code | 14-15 | 1 cifra | `0` |
| 2000 | age_code | 30-31 | 1 cifra | `0` |
| 2020 | age_code | Campo 5 | 1 cifra | `3` |

**Regole di Conversione**:
- Conversione diretta quando i sistemi di codifica sono compatibili
- Mapping tra sistemi di codifica diversi se necessario

### 5. CLASSIFICAZIONE SESSO
**Semantica**: Identificazione del sesso dell'uccello

| Versione | Campo | Posizione | Formato | Esempio |
|----------|-------|-----------|---------|---------|
| 1966 | N/A | - | - | Non presente |
| 1979 | sex_code | 15-16 | 1 cifra | `9` |
| 2000 | ? | ? | 1 cifra | Da identificare |
| 2020 | sex_code | Campo 6 | 1 cifra | `2` |

**Regole di Conversione**:
- Valore di default (sconosciuto) quando non disponibile
- Conversione diretta quando disponibile

### 6. INFORMAZIONI TEMPORALI
**Semantica**: Data e ora della cattura/osservazione

| Versione | Campo | Posizione | Formato | Esempio |
|----------|-------|-----------|---------|---------|
| 1966 | date_code | Campo 4 | DDMMYYYY | `11022023` |
| 1979 | date_first, date_current | 17-29 | DDMMYY × 2 | `200501`, `199505` |
| 2000 | date_first, date_current | 19-29 | Codificato × 2 | `11870`, `11870` |
| 2020 | date_code, time_code | Campo 7-8 | YYYYMMDD, HHMM | `20230521`, `1430` |

**Regole di Conversione**:
- Conversione tra formati di data
- Gestione di date multiple (prima cattura vs. cattura corrente)
- Tempo di default quando non disponibile

### 7. POSIZIONE GEOGRAFICA
**Semantica**: Coordinate geografiche del luogo di cattura

| Versione | Campo | Posizione | Formato | Esempio |
|----------|-------|-----------|---------|---------|
| 1966 | latitude, longitude | Campo 5-6 | DDMMN, DDDMME | `5215N`, `01325E` |
| 1979 | latitude, longitude | 29-41 | Formato fisso | Da rianalizzare |
| 2000 | coordinates | 60-74 | Signed encoded | `+452409+009033` |
| 2020 | lat_decimal, lon_decimal | Campo 9-10 | Decimali | `52.25412`, `-1.34521` |

**Regole di Conversione**:
- Conversione tra gradi/minuti e decimali
- Gestione di coordinate codificate
- Mantenimento della precisione quando possibile

### 8. MISURAZIONI BIOMETRICHE
**Semantica**: Misurazioni fisiche dell'uccello

| Versione | Campo | Posizione | Formato | Esempio |
|----------|-------|-----------|---------|---------|
| 1966 | wing_length, weight, bill_length | Campo 9-11 | Interi | `050`, `0115`, `0750` |
| 1979 | wing_length, weight, bill_length | 48-61 | Interi | Da rianalizzare |
| 2000 | measurements | 43-56 | Codificato | `0105200600600` |
| 2020 | wing_length, weight, bill_length, etc. | Campo 16+ | Decimali | `135.5`, `19.5`, `4` |

**Regole di Conversione**:
- Conversione tra unità di misura
- Gestione di precisione diversa (interi vs decimali)
- Mapping di misurazioni codificate

### 9. CONDIZIONI E METODI
**Semantica**: Informazioni sulle condizioni di cattura e metodi utilizzati

| Versione | Campo | Posizione | Formato | Esempio |
|----------|-------|-----------|---------|---------|
| 1966 | condition_code, method_code | Campo 7-8 | 2 cifre, 1 cifra | `10`, `2` |
| 1979 | condition_code, method_code | 41-44 | Vari | Da rianalizzare |
| 2000 | ? | ? | ? | Da identificare |
| 2020 | condition_code, method_code | Campo 11-12 | 1 cifra, 2 cifre | `1`, `10` |

## Strategia di Implementazione

### 1. Parser Semantici
Creare parser che identificano i campi per significato semantico, non per posizione fissa.

### 2. Convertitori Semantici
Implementare convertitori che trasformano il significato, non i valori letterali.

### 3. Validatori Semantici
Validare la coerenza semantica piuttosto che la correttezza sintattica.

### 4. Mappature Configurabili
Permettere configurazione delle mappature basata sulla documentazione ufficiale.

## Prossimi Passi

1. **Implementare parser semantici** per ogni versione
2. **Creare convertitori semantici** tra versioni
3. **Definire regole di validazione** semantica
4. **Testare con dati reali** quando disponibili
5. **Integrare con documentazione PDF** per validazione