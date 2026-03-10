# Modello Dati ECES

## Struttura Codici EURING

### Formato Generale

Un codice EURING è una stringa di caratteri a lunghezza fissa che codifica informazioni sull'inanellamento di un uccello. Ogni versione ha una lunghezza specifica e una struttura di campi definita.

### Versioni EURING

#### EURING 1966
- **Lunghezza**: 80 caratteri
- **Campi**: ~20 campi
- **Caratteristiche**: Primo formato standardizzato, campi posizionali fissi

#### EURING 1979
- **Lunghezza**: 117 caratteri
- **Campi**: ~25 campi
- **Caratteristiche**: Aggiunta campi biometrici

#### EURING 2000
- **Lunghezza**: 94 caratteri (standard) o variabile (EPE-compatible)
- **Campi**: 36 campi
- **Caratteristiche**: Standard moderno, compatibile con EPE (EURING Data Bank)
- **Ordine campi**: Segue ordine EPE per compatibilità

#### EURING 2020
- **Lunghezza**: Variabile
- **Campi**: 40+ campi
- **Caratteristiche**: Versione più recente con campi aggiuntivi per biometria avanzata

## Domini Semantici

I campi EURING sono organizzati in 7 domini semantici che rappresentano categorie logiche di informazioni:

### 1. Identification & Marking
**Scopo**: Identificazione dell'uccello e del sistema di marcaggio

**Campi tipici**:
- Ringing scheme (centro inanellamento)
- Primary identification method
- Ring number (numero anello)
- Metal ring verification
- Metal ring information
- Other marks information

**Evoluzione**: Da semplice numero anello (1966) a sistema complesso di identificazione multipla (2020)

### 2. Species
**Scopo**: Identificazione tassonomica

**Campi tipici**:
- Species reported (specie riportata)
- Species concluded (specie conclusa)

**Evoluzione**: Codici specie standardizzati EURING, da 4 a 5 caratteri

### 3. Demographics
**Scopo**: Caratteristiche demografiche dell'individuo

**Campi tipici**:
- Sex reported / concluded (sesso)
- Age reported / concluded (età)
- Status (status vitale)
- Brood size (dimensione covata)
- Pullus age (età pulcino)

**Evoluzione**: Da codici semplici (M/F, 1/2/3) a sistemi complessi con distinzione reported/concluded

### 4. Temporal
**Scopo**: Informazioni temporali dell'evento

**Campi tipici**:
- Day (giorno)
- Month (mese)
- Year (anno)
- Date accuracy (accuratezza data)
- Time (ora)

**Evoluzione**: Da data semplice (1966) a timestamp completo con accuratezza (2020)

### 5. Spatial
**Scopo**: Localizzazione geografica

**Campi tipici**:
- Area code (codice area EDB)
- Latitude (latitudine)
- Longitude (longitudine)
- Coordinate accuracy (accuratezza coordinate)
- Place code (codice luogo)

**Evoluzione**: Da codici area semplici a coordinate GPS precise con accuratezza

### 6. Biometrics
**Scopo**: Misure fisiche dell'uccello

**Campi tipici**:
- Wing length (lunghezza ala)
- Weight/Mass (peso)
- Bill length (lunghezza becco)
- Tarsus length (lunghezza tarso)
- Tail length (lunghezza coda)
- Fat score (punteggio grasso)
- Muscle score (punteggio muscolo)
- Primary moult (muta primarie)
- Plumage code (codice piumaggio)

**Evoluzione**: Espansione massiva da pochi campi (1966) a 20+ misure dettagliate (2020)

### 7. Methodology
**Scopo**: Metodi e condizioni di cattura/osservazione

**Campi tipici**:
- Manipulation (manipolazione)
- Moved before capture (spostato prima cattura)
- Catching method (metodo cattura)
- Lures used (esche usate)
- Condition code (codice condizione)
- Circumstances code (codice circostanze)
- Circumstances presumed (circostanze presunte)

**Evoluzione**: Da codici semplici a sistema dettagliato di documentazione metodologica

## Modelli Pydantic

### FieldDefinition

```python
class FieldDefinition(BaseModel):
    position: int                              # Posizione nella stringa
    name: str                                  # Nome campo
    data_type: str                             # Tipo dato (string, int, float)
    length: int                                # Lunghezza campo
    valid_values: Optional[List[str]]          # Valori validi (lookup)
    valid_values_descriptions: Optional[Dict[str, str]]  # Descrizioni valori
    description: str                           # Descrizione campo
    semantic_domain: Optional[SemanticDomain]  # Dominio semantico
    semantic_meaning: Optional[str]            # Significato semantico
    evolution_notes: Optional[List[str]]       # Note evoluzione
```

### EuringVersion

```python
class EuringVersion(BaseModel):
    id: str                                    # es. "euring_2000"
    name: str                                  # es. "EURING 2000"
    year: int                                  # Anno versione
    description: str                           # Descrizione
    field_definitions: List[FieldDefinition]   # Definizioni campi
    validation_rules: List[ValidationRule]     # Regole validazione
    format_specification: FormatSpec           # Specifiche formato
    semantic_domains: Optional[List[SemanticDomainMapping]]
```

### ConversionMapping

```python
class ConversionMapping(BaseModel):
    from_version: str                          # Versione source
    to_version: str                            # Versione target
    field_mappings: List[FieldMapping]         # Mappature campi
    transformation_rules: List[TransformationRule]
    compatibility_level: CompatibilityLevel    # full/partial/limited/none
    domain_mappings: Optional[List[DomainConversionMapping]]
```

### FieldMapping

```python
class FieldMapping(BaseModel):
    source_field: str                          # Campo source
    target_field: str                          # Campo target
    transformation_type: TransformationType    # direct/calculated/conditional/split/merge
    transformation_function: Optional[str]     # Funzione trasformazione
    semantic_domain: Optional[SemanticDomain]  # Dominio semantico
    conversion_accuracy: Optional[float]       # Accuratezza conversione (0-1)
```

## Compatibilità tra Versioni

### Matrice Compatibilità Domini

```
Domain: IDENTIFICATION_MARKING
  1966 → 1979: FULL
  1979 → 2000: FULL
  2000 → 2020: FULL
  1966 → 2020: PARTIAL (perdita informazioni)

Domain: SPECIES
  Tutte le conversioni: FULL (codici standardizzati)

Domain: DEMOGRAPHICS
  1966 → 2000: PARTIAL (età/sesso semplificati)
  2000 → 2020: FULL

Domain: TEMPORAL
  1966 → 2000: PARTIAL (no ora)
  2000 → 2020: FULL

Domain: SPATIAL
  1966 → 2000: LOSSY (codici area → coordinate)
  2000 → 2020: FULL

Domain: BIOMETRICS
  1966 → 2000: LOSSY (pochi campi)
  2000 → 2020: PARTIAL (nuovi campi non mappabili indietro)

Domain: METHODOLOGY
  1966 → 2000: PARTIAL
  2000 → 2020: FULL
```

### Livelli Compatibilità

- **FULL**: Conversione completa senza perdita informazioni
- **PARTIAL**: Conversione possibile con alcune limitazioni
- **LOSSY**: Conversione con perdita significativa di informazioni
- **INCOMPATIBLE**: Conversione non possibile

## Lookup Tables

Alcuni campi hanno valori codificati con lookup tables:

### Esempi Lookup Tables

#### Sex (Sesso)
```json
{
  "0": "Sconosciuto",
  "1": "Maschio",
  "2": "Femmina",
  "3": "Sesso non determinato"
}
```

#### Age (Età)
```json
{
  "0": "Età sconosciuta",
  "1": "Pullus (nidiaceo)",
  "2": "Giovane (volantone)",
  "3": "1° anno calendario",
  "4": "Dopo 1° anno calendario",
  