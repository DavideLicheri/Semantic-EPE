# Design Document - EURING Code Recognition System

## Overview

Il sistema EURING Code Recognition è un'applicazione web che utilizza tecniche di pattern matching e machine learning per identificare automaticamente le versioni del codice EURING utilizzate nelle stringhe di inanellamento degli uccelli. Il sistema implementa un modello SKOS (Simple Knowledge Organization System) **modulare organizzato per domini semantici** per rappresentare formalmente le relazioni tra le diverse versioni storiche del codice dal 1963 ad oggi.

L'architettura è progettata per essere modulare, scalabile e facilmente estendibile per supportare nuove versioni del codice EURING che potrebbero essere introdotte in futuro. **La struttura SKOS modulare permette l'analisi indipendente di ogni dominio semantico e il tracciamento della loro evoluzione storica.**

### Domini Semantici SKOS

Il sistema organizza i campi EURING in 7 domini semantici principali:

1. **IDENTIFICATION_MARKING**: Ring numbers, schemes, metal rings, other marks, verification
2. **SPECIES**: Species codes, taxonomy, finder vs scheme identification  
3. **DEMOGRAPHICS**: Age, sex classification systems
4. **TEMPORAL**: Date/time formats and their evolution
5. **SPATIAL**: Coordinates, location accuracy, geographic encoding
6. **BIOMETRICS**: Wing, weight, bill, tarsus, fat, muscle, moult measurements
7. **METHODOLOGY**: Capture methods, conditions, manipulation, lures

## Architecture

Il sistema segue un'architettura a tre livelli:

### Presentation Layer
- **Web Interface**: Interfaccia utente responsive per l'inserimento e visualizzazione dei dati
- **Authentication Module**: Gestione dell'autenticazione e autorizzazione utenti
- **Results Visualization**: Componenti per la visualizzazione dei risultati di riconoscimento e conversione

### Business Logic Layer
- **Recognition Engine**: Motore principale per il riconoscimento delle versioni EURING
- **Conversion Service**: Servizio per la conversione tra diverse versioni del codice
- **SKOS Manager**: Gestione del modello semantico delle versioni EURING organizzato per domini
- **Domain Evolution Analyzer**: Analisi dell'evoluzione storica dei domini semantici
- **Semantic Domain Processor**: Elaborazione indipendente di ogni dominio semantico
- **Batch Processor**: Elaborazione ottimizzata di multiple stringhe
- **Billing Service**: Gestione del sistema di pricing e conteggio conversioni
- **Payment Processor**: Elaborazione dei pagamenti per conversioni a pagamento

### Data Layer
- **SKOS Repository**: Storage del modello semantico delle versioni EURING organizzato per domini
- **Domain Evolution Store**: Archivio dell'evoluzione storica dei domini semantici
- **Semantic Mapping Database**: Database delle mappature semantiche tra domini e versioni
- **User Data Store**: Memorizzazione dei dati utente e delle sessioni
- **Conversion History**: Archivio delle conversioni effettuate
- **Export Service**: Generazione di file di esportazione
- **Billing Database**: Storage dei dati di fatturazione e conteggi utente
- **Pricing Configuration**: Configurazione dei prezzi e limiti gratuiti

## Components and Interfaces

### Recognition Engine
```typescript
interface RecognitionEngine {
  recognizeVersion(euringString: string): RecognitionResult
  recognizeBatch(strings: string[], sameVersion?: boolean): BatchRecognitionResult
  getConfidenceLevel(result: RecognitionResult): number
}

interface RecognitionResult {
  detectedVersion: EuringVersion
  confidence: number
  alternativeVersions?: EuringVersion[]
  analysisDetails: AnalysisMetadata
}
```

### SKOS Manager
```typescript
interface SKOSManager {
  loadVersionModel(): EuringVersionModel
  getVersionCharacteristics(version: string): VersionCharacteristics
  getConversionRules(fromVersion: string, toVersion: string): ConversionRules
  validateVersionCompatibility(from: string, to: string): boolean
  getDomainEvolution(domain: SemanticDomain): DomainEvolution
  analyzeDomainCompatibility(domain: SemanticDomain, fromVersion: string, toVersion: string): DomainCompatibility
  getSemanticDomains(): SemanticDomain[]
}

interface EuringVersionModel {
  versions: EuringVersion[]
  relationships: VersionRelationship[]
  conversionMappings: ConversionMapping[]
  semanticDomains: SemanticDomainDefinition[]
  domainEvolutions: DomainEvolution[]
}

interface SemanticDomainDefinition {
  id: string
  name: string
  description: string
  fields: string[]
  evolutionHistory: DomainEvolutionEntry[]
}

interface DomainEvolution {
  domain: SemanticDomain
  evolutionEntries: DomainEvolutionEntry[]
  compatibilityMatrix: DomainCompatibilityMatrix
}

interface DomainEvolutionEntry {
  version: string
  year: number
  changes: DomainChange[]
  fieldMappings: FieldMapping[]
  semanticNotes: string[]
}

enum SemanticDomain {
  IDENTIFICATION_MARKING = 'identification_marking',
  SPECIES = 'species',
  DEMOGRAPHICS = 'demographics', 
  TEMPORAL = 'temporal',
  SPATIAL = 'spatial',
  BIOMETRICS = 'biometrics',
  METHODOLOGY = 'methodology'
}
```
```

### Conversion Service
```typescript
interface ConversionService {
  convertString(input: string, fromVersion: string, toVersion: string): ConversionResult
  convertBatch(inputs: ConversionRequest[]): BatchConversionResult
  validateConversion(result: ConversionResult): ValidationResult
  checkConversionQuota(userId: string, requestedCount: number): QuotaCheckResult
}

interface ConversionResult {
  originalString: string
  convertedString: string
  fromVersion: string
  toVersion: string
  conversionMetadata: ConversionMetadata
  billingInfo?: BillingInfo
}
```

### Billing Service
```typescript
interface BillingService {
  checkUserQuota(userId: string): UserQuota
  calculateCost(userId: string, conversionCount: number): CostCalculation
  processPayment(userId: string, amount: number): PaymentResult
  updatePricing(newPricePerString: number): void
  getUserBillingHistory(userId: string): BillingHistory[]
}

interface UserQuota {
  userId: string
  freeConversionsUsed: number
  freeConversionsRemaining: number
  totalConversionsThisMonth: number
}

interface CostCalculation {
  freeConversions: number
  paidConversions: number
  pricePerString: number
  totalCost: number
  currency: string
}
```

## Data Models

### EuringVersion
```typescript
interface EuringVersion {
  id: string
  name: string
  year: number
  description: string
  fieldDefinitions: FieldDefinition[]
  validationRules: ValidationRule[]
  formatSpecification: FormatSpec
  semanticDomains: SemanticDomainMapping[]
}

interface FieldDefinition {
  position: number
  name: string
  dataType: string
  length: number
  validValues?: string[]
  description: string
  semanticDomain: SemanticDomain
  semanticMeaning: string
  evolutionNotes?: string[]
}

interface SemanticDomainMapping {
  domain: SemanticDomain
  fields: string[]
  domainSpecificRules: ValidationRule[]
  evolutionFromPrevious?: DomainEvolutionEntry
}
```

### ConversionMapping
```typescript
interface ConversionMapping {
  fromVersion: string
  toVersion: string
  fieldMappings: FieldMapping[]
  transformationRules: TransformationRule[]
  compatibilityLevel: CompatibilityLevel
  domainMappings: DomainConversionMapping[]
}

interface DomainConversionMapping {
  domain: SemanticDomain
  compatibility: DomainCompatibilityLevel
  fieldMappings: FieldMapping[]
  transformationRules: TransformationRule[]
  lossyConversion: boolean
  conversionNotes: string[]
}

interface FieldMapping {
  sourceField: string
  targetField: string
  transformationType: TransformationType
  transformationFunction?: string
  semanticDomain: SemanticDomain
  conversionAccuracy: number
}

enum DomainCompatibilityLevel {
  FULL = 'full',
  PARTIAL = 'partial', 
  LOSSY = 'lossy',
  INCOMPATIBLE = 'incompatible'
}

interface DomainChange {
  changeType: 'added' | 'removed' | 'modified' | 'renamed'
  fieldName: string
  previousValue?: any
  newValue?: any
  semanticImpact: string
  compatibilityImpact: DomainCompatibilityLevel
}
```

### UserSession
```typescript
interface UserSession {
  userId: string
  sessionId: string
  createdAt: Date
  lastActivity: Date
  conversionHistory: ConversionHistoryEntry[]
  currentQuota: UserQuota
}

interface ConversionHistoryEntry {
  timestamp: Date
  originalStrings: string[]
  results: ConversionResult[]
  exportedFiles?: ExportedFile[]
  billingInfo?: BillingInfo
}
```

### Billing Models
```typescript
interface BillingInfo {
  conversionCount: number
  freeConversionsUsed: number
  paidConversions: number
  totalCost: number
  currency: string
  paymentRequired: boolean
}

interface PricingConfiguration {
  freeConversionLimit: number
  pricePerStringCents: number
  currency: string
  lastUpdated: Date
  updatedBy: string
}

interface BillingHistory {
  id: string
  userId: string
  timestamp: Date
  conversionCount: number
  amountCharged: number
  currency: string
  paymentStatus: PaymentStatus
  transactionId?: string
}

enum PaymentStatus {
  FREE = 'free',
  PENDING = 'pending',
  COMPLETED = 'completed',
  FAILED = 'failed'
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Authentication Properties

**Property 1: Valid credentials grant access**
*For any* user with valid credentials, authentication should succeed and grant access to system functionalities
**Validates: Requirements 1.1**

**Property 2: Invalid credentials deny access**
*For any* user with invalid credentials, authentication should fail and display an appropriate error message
**Validates: Requirements 1.2**

**Property 3: Unauthenticated access redirects**
*For any* attempt to access protected functionality without authentication, the system should redirect to the login page
**Validates: Requirements 1.3**

### Recognition Properties

**Property 4: Valid EURING strings are accepted**
*For any* valid EURING string from a known version, the system should accept the input and initiate recognition processing
**Validates: Requirements 2.1**

**Property 5: Version recognition accuracy**
*For any* EURING string from a known version, the system should correctly identify that specific version
**Validates: Requirements 2.2**

**Property 6: Recognition results completeness**
*For any* completed recognition process, the result should include both the identified version and confidence level
**Validates: Requirements 2.3**

**Property 7: Invalid string handling**
*For any* unrecognizable or corrupted EURING string, the system should provide informative error messages and suggestions
**Validates: Requirements 2.4**

**Property 8: Batch optimization consistency**
*For any* batch of EURING strings declared as same version, applying the identified version to all strings should produce consistent results
**Validates: Requirements 2.6**

**Property 9: Individual batch analysis**
*For any* batch of EURING strings with mixed versions, each string should be analyzed individually and results should be organized by string
**Validates: Requirements 2.7**

### Conversion Properties

**Property 10: Conversion options availability**
*For any* identified EURING version, the system should display all compatible target versions for conversion
**Validates: Requirements 3.1**

**Property 11: Conversion execution**
*For any* compatible version pair, selecting a target version should successfully execute the format conversion
**Validates: Requirements 3.2**

**Property 12: Conversion output format**
*For any* completed conversion, the output should be a valid EURING string in the target version format
**Validates: Requirements 3.3**

**Property 13: Incompatibility explanation**
*For any* incompatible version conversion attempt, the system should provide clear explanations of why the conversion cannot be performed
**Validates: Requirements 3.4**

**Property 14: Batch conversion correspondence**
*For any* batch conversion operation, the correspondence between original and converted strings should be preserved in order
**Validates: Requirements 3.5**

### Data Management Properties

**Property 15: Save options availability**
*For any* completed conversion, save options should be available to the user
**Validates: Requirements 4.1**

**Property 16: Data persistence round trip**
*For any* conversion data saved to the system, retrieving the data should return both original and converted strings accurately
**Validates: Requirements 4.2**

**Property 17: Export format compliance**
*For any* export request, the generated file should conform to the requested format and contain all conversion data
**Validates: Requirements 4.3**

**Property 18: Multi-conversion organization**
*For any* set of saved conversions, the data should be organized in a consistent, structured manner
**Validates: Requirements 4.4**

**Property 19: Export metadata inclusion**
*For any* exported file, conversion metadata should be included and accurately reflect the operations performed
**Validates: Requirements 4.5**

### SKOS Model Properties

**Property 20: Version addition integrity**
*For any* new EURING version added to the SKOS model, existing version relationships should remain intact
**Validates: Requirements 5.2**

**Property 21: Version characteristics round trip**
*For any* EURING version, storing and retrieving version characteristics should preserve all fields, formats, and rules
**Validates: Requirements 5.3**

**Property 22: Transformation mapping round trip**
*For any* version transformation mapping, storing and retrieving the mapping should preserve all transformation rules
**Validates: Requirements 5.4**

**Property 23: Model query accuracy**
*For any* query to the SKOS model, the returned information about versions and relationships should be accurate and complete
**Validates: Requirements 5.5**

**Property 24: Semantic domain organization**
*For any* EURING version, all fields should be correctly assigned to their appropriate semantic domains
**Validates: Requirements 5.6**

**Property 25: Domain evolution tracking**
*For any* semantic domain, the evolution history should accurately reflect changes across all versions
**Validates: Requirements 5.7**

### Domain Evolution Properties

**Property 26: Domain evolution accuracy**
*For any* semantic domain evolution request, the system should accurately show historical changes for that domain
**Validates: Requirements 8.1**

**Property 27: Domain comparison consistency**
*For any* two versions compared within a domain, the differences should be accurately identified and categorized
**Validates: Requirements 8.2**

**Property 28: Evolution timeline accuracy**
*For any* domain evolution timeline, the chronological order and change descriptions should be accurate
**Validates: Requirements 8.3**

**Property 29: Semantic field grouping**
*For any* domain analysis, fields should be correctly grouped by semantic relationships
**Validates: Requirements 8.4**

**Property 30: Domain compatibility assessment**
*For any* domain-specific conversion compatibility check, the assessment should accurately reflect conversion feasibility
**Validates: Requirements 8.5**

**Property 31: Domain evolution export completeness**
*For any* domain evolution export, all relevant historical data and metadata should be included
**Validates: Requirements 8.6**

**Property 32: Domain documentation accuracy**
*For any* domain-specific documentation request, the returned information should be complete and accurate
**Validates: Requirements 8.7**

### Historical Coverage Properties

**Property 33: Intermediate version recognition**
*For any* EURING string from any historical period (1963-present), the system should correctly identify the specific version used
**Validates: Requirements 6.3**

**Property 34: Ambiguity resolution**
*For any* ambiguous EURING string that could match multiple versions, the system should apply context-based disambiguation algorithms
**Validates: Requirements 6.4**

**Property 35: Uncertainty handling**
*For any* recognition result with low confidence, the system should provide multiple version options with probability scores
**Validates: Requirements 6.5**

### Billing Properties

**Property 36: Free conversion limit**
*For any* user performing up to 19 conversions, the system should provide the service without charge
**Validates: Requirements 7.1**

**Property 37: Paid conversion billing**
*For any* user exceeding 19 conversions, the system should calculate and require payment for additional strings
**Validates: Requirements 7.2**

**Property 38: Dynamic pricing calculation**
*For any* conversion request, the cost calculation should use the current configurable price per string
**Validates: Requirements 7.3**

**Property 39: Pricing update propagation**
*For any* price modification by administrator, subsequent conversions should use the new pricing immediately
**Validates: Requirements 7.4**

**Property 40: Cost transparency**
*For any* user session, the system should clearly display remaining free conversions and costs for additional conversions
**Validates: Requirements 7.5**

## Error Handling

Il sistema implementa una strategia di error handling a più livelli:

### Input Validation
- **Syntax Validation**: Verifica della sintassi delle stringhe EURING prima del processing
- **Version Compatibility**: Controllo della compatibilità tra versioni prima della conversione
- **Authentication Validation**: Verifica delle credenziali e dello stato della sessione

### Processing Errors
- **Recognition Failures**: Gestione di stringhe non riconoscibili con suggerimenti per la risoluzione
- **Conversion Errors**: Handling di conversioni impossibili con spiegazioni dettagliate
- **SKOS Model Errors**: Gestione di errori nel modello semantico con fallback appropriati

### System Errors
- **Database Connectivity**: Retry automatico e fallback per problemi di connessione
- **Export Failures**: Gestione di errori durante la generazione di file di esportazione
- **Session Management**: Handling di sessioni scadute e problemi di autenticazione

### Error Recovery
- **Graceful Degradation**: Il sistema continua a funzionare anche con funzionalità limitate
- **User Feedback**: Messaggi di errore informativi con azioni suggerite
- **Logging and Monitoring**: Registrazione completa degli errori per debugging e monitoraggio

## Testing Strategy

Il sistema utilizza un approccio di testing duale che combina unit testing e property-based testing per garantire correttezza e robustezza.

### Unit Testing
Gli unit test verificano:
- Esempi specifici di riconoscimento per versioni note del codice EURING
- Casi edge come la prima versione (1963) e l'ultima versione disponibile
- Scenari di errore specifici (credenziali invalide, stringhe corrotte)
- Integrazione tra componenti del sistema
- Funzionalità di esportazione con formati specifici

### Property-Based Testing
Il sistema utilizza **Hypothesis** (per Python) come libreria per property-based testing. Ogni test property-based è configurato per eseguire un minimo di 100 iterazioni per garantire copertura adeguata dello spazio degli input.

I property-based test verificano:
- **Proprietà di riconoscimento**: Per qualsiasi stringa EURING valida, il riconoscimento deve produrre risultati consistenti
- **Proprietà di conversione**: Le conversioni tra versioni compatibili devono preservare l'informazione semantica
- **Proprietà di round-trip**: Salvare e recuperare dati deve preservare l'integrità
- **Proprietà di batch processing**: L'elaborazione in batch deve mantenere corrispondenze e ordine
- **Proprietà del modello SKOS**: Le operazioni sul modello devono preservare l'integrità delle relazioni

### Test Data Generation
- **Generatori di stringhe EURING**: Creazione automatica di stringhe valide per tutte le versioni storiche
- **Generatori di credenziali**: Creazione di credenziali valide e invalide per test di autenticazione
- **Generatori di batch**: Creazione di set di stringhe con versioni omogenee o miste
- **Generatori di versioni**: Creazione di nuove versioni del codice per test del modello SKOS

### Test Requirements
- Ogni property-based test deve essere taggato con il formato: **Feature: euring-code-recognition, Property {number}: {property_text}**
- Ogni correctness property deve essere implementata da un singolo property-based test
- I test devono essere eseguiti con almeno 100 iterazioni per garantire copertura statistica
- I test unit e property-based sono complementari e entrambi devono essere inclusi nella suite di test