# Domain-Specific Conversion Rules Implementation

## Overview

This document summarizes the implementation of Task C.3: "Implement domain-specific conversion rules" for the EURING Code Recognition System. The implementation provides domain-specific conversion mappings, transformation rules, and compatibility assessment for each semantic domain.

## Requirements Addressed

- **Requirement 5.4**: Domain-specific transformation rules and compatibility checking
- **Requirement 8.5**: Domain compatibility level assessment and lossy conversion detection

## Components Implemented

### 1. DomainConversionService (`app/services/domain_conversion_service.py`)

**Purpose**: Core service for creating and managing domain-specific conversion rules.

**Key Features**:
- Creates `DomainConversionMapping` for each semantic domain
- Implements domain-specific transformation rules
- Assesses domain compatibility levels
- Handles field mappings and transformation functions
- Provides basic compatibility assessment when domain evolution data is unavailable

**Key Methods**:
- `create_domain_conversion_mapping()`: Creates domain-specific conversion mapping
- `assess_domain_compatibility_level()`: Assesses compatibility between versions for a domain
- `apply_domain_transformation()`: Applies domain-specific transformations to field data
- `get_domain_transformation_rules()`: Retrieves transformation rules for a domain

### 2. Enhanced Conversion Service (`app/services/conversion_service.py`)

**Purpose**: Extended the existing conversion service to use domain-specific rules.

**New Features**:
- `convert_with_domain_rules()`: Converts EURING strings using domain-specific rules
- `load_versions_for_domain_conversion()`: Loads version data for domain conversion
- `_extract_domain_fields()`: Extracts fields belonging to specific domains

**Integration**: The conversion service now processes each semantic domain independently, applying domain-specific transformations and collecting domain-specific results.

### 3. Enhanced SKOS Manager (`app/services/skos_manager.py`)

**Purpose**: Extended SKOS manager to integrate domain-specific conversion capabilities.

**New Methods**:
- `create_domain_conversion_mapping()`: Creates domain conversion mappings via SKOS manager
- `get_domain_conversion_rules()`: Retrieves domain-specific conversion rules
- `assess_all_domain_compatibility_levels()`: Assesses compatibility for all domains
- `update_conversion_mapping_with_domain_rules()`: Updates existing mappings with domain rules

## Semantic Domains Supported

The implementation supports all 7 semantic domains defined in the system:

1. **IDENTIFICATION_MARKING**: Ring numbers, schemes, metal rings, other marks, verification
2. **SPECIES**: Species codes, taxonomy, finder vs scheme identification
3. **DEMOGRAPHICS**: Age, sex classification systems
4. **TEMPORAL**: Date/time formats and their evolution
5. **SPATIAL**: Coordinates, location accuracy, geographic encoding
6. **BIOMETRICS**: Wing, weight, bill, tarsus, fat, muscle, moult measurements
7. **METHODOLOGY**: Capture methods, conditions, manipulation, lures

## Domain-Specific Features

### Field Mapping
- Automatic field correspondence detection across versions
- Semantic meaning-based field matching
- Position-based fallback matching
- Conversion accuracy calculation

### Transformation Rules
- Domain-specific transformation functions
- Default value rules for new fields
- Conditional transformations based on field types
- Version-specific transformation expressions

### Compatibility Assessment
- Four compatibility levels: FULL, PARTIAL, LOSSY, INCOMPATIBLE
- Lossy conversion detection and reporting
- Field-level compatibility analysis
- Domain-specific conversion warnings and notes

## Transformation Functions

The implementation includes domain-specific transformation functions:

### IDENTIFICATION_MARKING Domain
- Ring number format expansion/truncation
- Metal ring information defaults
- Scheme code transformations

### TEMPORAL Domain
- Date format conversions (DDMMYYYY ↔ YYYYMMDD)
- Default time values for older versions
- Time precision handling

### SPATIAL Domain
- Coordinate format conversions (degrees/minutes ↔ decimal)
- Accuracy code defaults
- Geographic precision handling

### BIOMETRICS Domain
- Measurement unit conversions
- Default values for missing measurements
- Data type conversions (integer ↔ float)

### METHODOLOGY Domain
- Method code format adjustments
- Status information defaults
- Condition code transformations

## Testing

### Unit Tests (`test_domain_conversion_service.py`)
- Tests all core domain conversion service functionality
- Validates field mapping and transformation rule creation
- Tests compatibility assessment algorithms
- Verifies domain field extraction and correspondence detection

### Integration Tests (`test_domain_conversion_integration.py`)
- Tests integration with conversion service and SKOS manager
- Validates end-to-end domain-specific conversion workflows
- Tests domain field extraction from parsed data
- Verifies SKOS manager domain conversion capabilities

**Test Results**: All tests pass successfully, validating the implementation.

## Usage Examples

### Creating Domain Conversion Mapping
```python
domain_service = DomainConversionService()
domain_service.load_versions(versions)

mapping = await domain_service.create_domain_conversion_mapping(
    SemanticDomain.IDENTIFICATION_MARKING, "1966", "2020"
)
```

### Converting with Domain Rules
```python
conversion_service = EuringConversionService()
result = await conversion_service.convert_with_domain_rules(
    euring_string, "1966", "2020"
)
```

### Assessing Domain Compatibility
```python
skos_manager = SKOSManagerImpl()
assessments = await skos_manager.assess_all_domain_compatibility_levels(
    "1966", "2020"
)
```

## Benefits

1. **Granular Control**: Domain-specific rules allow fine-tuned conversion logic for each semantic area
2. **Improved Accuracy**: Domain-aware transformations provide more accurate conversions
3. **Better Error Handling**: Domain-specific warnings and compatibility assessments
4. **Extensibility**: Easy to add new domains or modify existing domain rules
5. **Maintainability**: Clear separation of concerns by semantic domain

## Future Enhancements

1. **Advanced Transformation Functions**: More sophisticated transformation logic for complex field conversions
2. **Machine Learning Integration**: Use ML models for better field correspondence detection
3. **User-Defined Rules**: Allow users to define custom transformation rules for specific use cases
4. **Performance Optimization**: Caching and optimization for large-scale batch conversions
5. **Validation Framework**: Enhanced validation of transformation results

## Conclusion

The domain-specific conversion rules implementation successfully addresses the requirements by providing:
- Comprehensive domain-specific conversion mappings
- Flexible transformation rule framework
- Accurate compatibility assessment
- Robust error handling and fallback mechanisms
- Extensive test coverage

The implementation is production-ready and provides a solid foundation for domain-aware EURING code conversions.