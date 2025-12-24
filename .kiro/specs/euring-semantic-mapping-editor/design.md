# Design Document - Semantic Mapping Editor

## Overview

Il Semantic Mapping Editor è un'interfaccia interattiva per correggere e migliorare i mapping semantici tra le versioni EURING. Si integra con l'architettura esistente del sistema EURING, utilizzando EPE come gold standard e i domini semantici già definiti.

## Architecture Integration

### Existing System Components

Il sistema attuale fornisce la base per l'editor:

1. **Frontend Components**:
   - `EuringMatrix.tsx`: Vista matrice comparativa (da estendere)
   - `StringNavigator.tsx`: Navigazione stringhe (per testing)
   - `DomainPanel.tsx`: Analisi domini (per contesto)

2. **Backend Services**:
   - `euring_api.py`: Endpoints per domini e compatibilità
   - `euring_2000_epe_compatible_parser.py`: Gold standard EPE
   - `domain_evolution_analyzer.py`: Analisi evoluzione domini
   - `semantic_field_grouper.py`: Raggruppamento campi semantici

3. **Data Models**:
   - 7 Domini Semantici definiti
   - Versioni EURING (1966, 1979, 2000, 2020)
   - Field definitions con posizioni e metadati

### New Components Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Semantic Mapping Editor                  │
├─────────────────────────────────────────────────────────────┤
│  Frontend (React/TypeScript)                               │
│  ┌─────────────────┐ ┌─────────────────┐ ┌───────────────┐ │
│  │ MappingEditor   │ │ ValidationPanel │ │ ExportPanel   │ │
│  │ Component       │ │ Component       │ │ Component     │ │
│  └─────────────────┘ └─────────────────┘ └───────────────┘ │
│  ┌─────────────────┐ ┌─────────────────┐ ┌───────────────┐ │
│  │ DragDropMatrix  │ │ MappingHistory  │ │ CollabPanel   │ │
│  │ Component       │ │ Component       │ │ Component     │ │
│  └─────────────────┘ └─────────────────┘ └───────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  Backend Services (Python/FastAPI)                         │
│  ┌─────────────────┐ ┌─────────────────┐ ┌───────────────┐ │
│  │ MappingManager  │ │ ValidationEngine│ │ ExportService │ │
│  │ Service         │ │ Service         │ │ Service       │ │
│  └─────────────────┘ └─────────────────┘ └───────────────┘ │
│  ┌─────────────────┐ ┌─────────────────┐ ┌───────────────┐ │
│  │ HistoryManager  │ │ CollabManager   │ │ EPEValidator  │ │
│  │ Service         │ │ Service         │ │ Service       │ │
│  └─────────────────┘ └─────────────────┘ └───────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                 │
│  ┌─────────────────┐ ┌─────────────────┐ ┌───────────────┐ │
│  │ Mapping         │ │ Validation      │ │ History       │ │
│  │ Repository      │ │ Repository      │ │ Repository    │ │
│  └─────────────────┘ └─────────────────┘ └───────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Component Design

### 1. Frontend Components

#### MappingEditor Component
```typescript
interface MappingEditorProps {
  versions: EuringVersion[];
  currentMappings: FieldMapping[];
  onMappingChange: (mapping: FieldMapping) => void;
  epeReference: EpeFieldDefinitions;
}

interface FieldMapping {
  id: string;
  sourceField: FieldDefinition;
  targetField: FieldDefinition;
  mappingType: 'automatic' | 'manual' | 'verified';
  confidence: number;
  semanticDomain: SemanticDomain;
  notes: string[];
  lastModified: Date;
  modifiedBy: string;
}
```

#### DragDropMatrix Component
```typescript
interface DragDropMatrixProps {
  sourceVersion: EuringVersion;
  targetVersion: EuringVersion;
  mappings: FieldMapping[];
  onDrop: (sourceField: string, targetField: string) => void;
  epeOrder: string[]; // EPE field order as reference
}
```

#### ValidationPanel Component
```typescript
interface ValidationPanelProps {
  mappings: FieldMapping[];
  testStrings: string[];
  epeValidator: EpeValidator;
  onValidationComplete: (results: ValidationResult[]) => void;
}

interface ValidationResult {
  mappingId: string;
  isValid: boolean;
  epeCompatible: boolean;
  errors: string[];
  warnings: string[];
  testResults: TestResult[];
}
```

### 2. Backend Services

#### MappingManager Service
```python
class MappingManager:
    def __init__(self, epe_parser: Euring2000EpeCompatibleParser):
        self.epe_parser = epe_parser
        self.mapping_repository = MappingRepository()
    
    async def get_current_mappings(self, domain: SemanticDomain) -> List[FieldMapping]:
        """Get current mappings for a domain"""
    
    async def update_mapping(self, mapping: FieldMapping) -> ValidationResult:
        """Update a field mapping with validation"""
    
    async def create_mapping_from_epe(self, field_name: str) -> FieldMapping:
        """Create mapping using EPE as gold standard"""
    
    async def validate_mapping_consistency(self, mappings: List[FieldMapping]) -> List[ValidationError]:
        """Validate mapping consistency across versions"""
```

#### ValidationEngine Service
```python
class ValidationEngine:
    def __init__(self, epe_parser: Euring2000EpeCompatibleParser):
        self.epe_parser = epe_parser
        self.string_navigator = StringNavigator()
    
    async def validate_mapping_with_epe(self, mapping: FieldMapping, test_strings: List[str]) -> ValidationResult:
        """Validate mapping against EPE gold standard"""
    
    async def test_mapping_with_real_strings(self, mapping: FieldMapping, strings: List[str]) -> List[TestResult]:
        """Test mapping with real EURING strings"""
    
    async def generate_validation_report(self, mappings: List[FieldMapping]) -> ValidationReport:
        """Generate comprehensive validation report"""
```

### 3. Data Models

#### FieldMapping Model
```python
@dataclass
class FieldMapping:
    id: str
    source_version: str
    target_version: str
    source_field: FieldDefinition
    target_field: FieldDefinition
    mapping_type: MappingType
    confidence: float
    semantic_domain: SemanticDomain
    epe_compatible: bool
    validation_status: ValidationStatus
    notes: List[str]
    created_at: datetime
    modified_at: datetime
    created_by: str
    modified_by: str
    
class MappingType(Enum):
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    EPE_VERIFIED = "epe_verified"
    EXPERT_REVIEWED = "expert_reviewed"

class ValidationStatus(Enum):
    PENDING = "pending"
    VALID = "valid"
    INVALID = "invalid"
    NEEDS_REVIEW = "needs_review"
```

## Integration Points

### 1. Matrix Integration
- Extend `EuringMatrix.tsx` with editing capabilities
- Add mapping visualization overlay
- Integrate drag & drop functionality
- Show confidence levels and validation status

### 2. API Integration
- Extend existing `/api/euring/domains/` endpoints
- Add new `/api/euring/mappings/` endpoints
- Integrate with domain compatibility assessments
- Use existing export functionality

### 3. EPE Integration
- Use `euring_2000_epe_compatible_parser.py` as validation reference
- Validate all EURING 2000 mappings against EPE
- Use EPE field order as canonical reference
- Ensure zero tolerance for EPE discrepancies

### 4. String Navigator Integration
- Use existing string parsing for validation
- Integrate test string functionality
- Show mapping results in field-value format
- Provide real-time validation feedback

## User Experience Flow

### 1. Access Editor
```
Main App → "🔧 Editor Mapping" tab → MappingEditor Component
```

### 2. View Current Mappings
```
Select Domain → Load Current Mappings → Display Matrix with Confidence Levels
```

### 3. Edit Mapping
```
Drag Field → Drop on Target → Validate with EPE → Save with Confidence Score
```

### 4. Validate Changes
```
Select Test Strings → Run Validation → Show Results → Fix Issues → Re-validate
```

### 5. Export Corrected Mappings
```
Select Export Format → Generate Export → Integrate with System → Deploy Changes
```

## Implementation Phases

### Phase 1: Core Editor (Requirements 1-2)
- Basic mapping visualization
- Manual editing interface
- EPE integration for EURING 2000
- Simple validation

### Phase 2: Advanced Features (Requirements 3-4)
- Real string validation
- Version management
- History tracking
- Backup/restore

### Phase 3: User Experience (Requirements 5-6)
- Drag & drop interface
- Export functionality
- API integration
- Performance optimization

### Phase 4: Analytics & Collaboration (Requirements 7-9)
- Statistics and reporting
- Multi-user collaboration
- Full system integration
- Production deployment

## Technical Considerations

### Performance
- Lazy loading of large mapping datasets
- Efficient drag & drop with virtual scrolling
- Caching of validation results
- Background processing for bulk operations

### Data Consistency
- Use EPE as single source of truth for EURING 2000
- Maintain referential integrity across versions
- Atomic updates for mapping changes
- Conflict resolution for concurrent edits

### Validation Strategy
- Real-time validation during editing
- Batch validation for bulk changes
- EPE compatibility checks for EURING 2000
- Statistical validation using real data

### Integration Safety
- Non-destructive editing (versioned changes)
- Rollback capabilities
- Staging environment for testing
- Gradual deployment of corrected mappings

## Success Metrics

1. **Accuracy Improvement**: Increase mapping confidence scores by 30%
2. **EPE Compatibility**: 100% compatibility for EURING 2000 mappings
3. **User Adoption**: 80% of domain experts use the editor regularly
4. **Validation Success**: 95% of mappings pass real string validation
5. **System Integration**: Zero breaking changes to existing functionality

## Risk Mitigation

1. **EPE Compatibility Risk**: Continuous validation against EPE gold standard
2. **Performance Risk**: Progressive loading and caching strategies
3. **Data Loss Risk**: Comprehensive backup and version control
4. **User Adoption Risk**: Intuitive UI and comprehensive documentation
5. **Integration Risk**: Extensive testing with existing system components