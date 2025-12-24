# EURING Domain Evolution Matrices

This document provides detailed evolution matrices showing changes, additions, and removals for each semantic domain across all EURING versions (1966-2020).

## Overview

The EURING code system has evolved significantly over 54 years (1966-2020), with each version introducing new capabilities while maintaining backward compatibility where possible. The evolution is organized into 7 semantic domains:

1. **IDENTIFICATION_MARKING** - Ring numbers, schemes, metal rings, other marks, verification
2. **SPECIES** - Species codes, taxonomy, finder vs scheme identification  
3. **DEMOGRAPHICS** - Age, sex classification systems
4. **TEMPORAL** - Date/time formats and their evolution
5. **SPATIAL** - Coordinates, location accuracy, geographic encoding
6. **BIOMETRICS** - Wing, weight, bill, tarsus, fat, muscle, moult measurements
7. **METHODOLOGY** - Capture methods, conditions, manipulation, lures

## Evolution Summary by Version

| Version | Year | Total Fields | Major Innovation |
|---------|------|--------------|------------------|
| EURING 1966 | 1966 | 11 | First standardized format, space-separated |
| EURING 1979 | 1979 | 23 | Fixed-length format, encoded coordinates |
| EURING 2000 | 2000 | 24 | Complex alphanumeric encoding, enhanced accuracy |
| EURING 2020 | 2020 | 22 | Pipe-delimited, decimal coordinates, enhanced biometrics |
| EURING 2020 Official | 2020 | 15 | SKOS thesaurus integration, semantic precision |

## Domain Evolution Matrices

### 1. IDENTIFICATION_MARKING Domain Evolution

**Description**: Ring numbers, schemes, metal rings, other marks, and verification systems for unique bird identification throughout its life

| Field Name | 1966 | 1979 | 2000 | 2020 | 2020 Official | Evolution Type |
|------------|------|------|------|------|---------------|----------------|
| ring_number | ✓ (7 chars, 2L+5D) | ✓ (7 chars, 1L+6D) | ✓ (7 digits) | ✓ (8 chars, 3L+5D) | ❌ | **EVOLVED** |
| identification_number | ❌ | ❌ | ❌ | ❌ | ✓ (10 chars) | **NEW** |
| scheme_country | ❌ | ✓ (2 letters) | ❌ | ❌ | ❌ | **TRANSIENT** |
| scheme_code | ❌ | ❌ | ✓ (4 chars) | ❌ | ❌ | **TRANSIENT** |
| ringing_scheme | ❌ | ❌ | ❌ | ❌ | ✓ (3 letters) | **NEW** |
| ring_prefix | ❌ | ❌ | ✓ (3 chars) | ❌ | ❌ | **TRANSIENT** |
| ring_suffix | ❌ | ❌ | ✓ (2 letters) | ❌ | ❌ | **TRANSIENT** |
| metal_ring_info | ❌ | ❌ | ❌ | ✓ (1 digit) | ❌ | **TRANSIENT** |
| metal_ring_information | ❌ | ❌ | ❌ | ❌ | ✓ (1 digit, 0-7) | **NEW** |
| other_marks_info | ❌ | ❌ | ❌ | ✓ (5 digits) | ❌ | **TRANSIENT** |
| other_marks_information | ❌ | ❌ | ❌ | ❌ | ✓ (2 chars) | **NEW** |
| primary_identification_method | ❌ | ❌ | ❌ | ❌ | ✓ (2 chars) | **NEW** |
| verification_code | ❌ | ❌ | ❌ | ✓ (1 digit) | ❌ | **TRANSIENT** |
| verification_of_the_metal_ring | ❌ | ❌ | ❌ | ❌ | ✓ (1 digit) | **NEW** |

**Key Evolution Patterns**:
- **Ring Number Evolution**: Format changed from 2+5 → 1+6 → 7 digits → 3+5 → replaced by identification_number
- **Scheme Identification**: Evolved from country codes to complex scheme codes to official SKOS schemes
- **Verification Systems**: Introduced in 2020, refined in official SKOS version
- **Metal Ring Tracking**: Enhanced from simple presence to detailed status information

### 2. SPECIES Domain Evolution

**Description**: Species codes, taxonomy systems, and identification verification by both finders and ringing schemes

| Field Name | 1966 | 1979 | 2000 | 2020 | 2020 Official | Evolution Type |
|------------|------|------|------|------|---------------|----------------|
| species_code | ✓ (4 digits) | ✓ (5 digits) | ❌ | ✓ (5 digits) | ❌ | **EVOLVED** |
| species_as_mentioned_by_finder | ❌ | ❌ | ❌ | ❌ | ✓ (5 digits) | **NEW** |
| species_as_mentioned_by_scheme | ❌ | ❌ | ❌ | ❌ | ✓ (5 digits) | **NEW** |
| additional_code_1 | ❌ | ✓ (3 digits) | ❌ | ❌ | ❌ | **TRANSIENT** |
| additional_codes | ❌ | ❌ | ✓ (12 digits) | ❌ | ❌ | **TRANSIENT** |

**Key Evolution Patterns**:
- **Species Code Length**: Expanded from 4 to 5 digits in 1979, maintained through 2020
- **Dual Identification**: Official SKOS version introduces separate finder vs scheme identification
- **Additional Codes**: Various additional coding systems tried and abandoned
- **Taxonomy Integration**: Official version aligns with IOC taxonomy standards

### 3. DEMOGRAPHICS Domain Evolution

**Description**: Age and sex classification systems based on plumage characteristics and morphological features

| Field Name | 1966 | 1979 | 2000 | 2020 | 2020 Official | Evolution Type |
|------------|------|------|------|------|---------------|----------------|
| age_code | ✓ (1 digit, 1-9) | ✓ (1 digit, 0-9) | ✓ (1 digit) | ✓ (1 digit, 1-9) | ❌ | **EVOLVED** |
| age_mentioned_by_the_person | ❌ | ❌ | ❌ | ❌ | ✓ (1 char, 0-9,A-H) | **NEW** |
| sex_code | ❌ | ✓ (1 digit) | ❌ | ✓ (1 digit, 1-9) | ❌ | **EVOLVED** |
| sex_mentioned_by_the_person | ❌ | ❌ | ❌ | ❌ | ✓ (1 char, M/F/U) | **NEW** |
| sex_concluded_by_the_scheme | ❌ | ❌ | ❌ | ❌ | ✓ (1 char, M/F/U) | **NEW** |

**Key Evolution Patterns**:
- **Age Classification**: Evolved from 1-9 to 0-9 to enhanced alphanumeric system
- **Sex Determination**: Introduced in 1979, refined with dual finder/scheme approach
- **Validation Enhancement**: Official version provides clear M/F/U categories
- **Plumage-Based System**: Official version emphasizes plumage state over actual age

### 4. TEMPORAL Domain Evolution

**Description**: Date and time formats for recording capture, observation, and handling events

| Field Name | 1966 | 1979 | 2000 | 2020 | 2020 Official | Evolution Type |
|------------|------|------|------|------|---------------|----------------|
| date_code | ✓ (DDMMYYYY) | ❌ | ❌ | ✓ (YYYYMMDD) | ❌ | **EVOLVED** |
| date_first | ❌ | ✓ (DDMMYY) | ✓ (5 digits) | ❌ | ❌ | **TRANSIENT** |
| date_current | ❌ | ✓ (DDMMYY) | ✓ (5 digits) | ❌ | ❌ | **TRANSIENT** |
| time_code | ❌ | ❌ | ❌ | ✓ (HHMM) | ❌ | **TRANSIENT** |

**Key Evolution Patterns**:
- **Date Format Evolution**: DDMMYYYY → DDMMYY → encoded → YYYYMMDD → removed
- **Dual Dating**: 1979-2000 tracked both first and current encounter dates
- **Time Addition**: 2020 introduced time recording, removed in official version
- **Encoding Complexity**: 2000 version used complex 5-digit encoding
- **Simplification**: Official SKOS version removes temporal fields entirely

### 5. SPATIAL Domain Evolution

**Description**: Geographic coordinates, location accuracy, and spatial encoding systems for recording bird locations

| Field Name | 1966 | 1979 | 2000 | 2020 | 2020 Official | Evolution Type |
|------------|------|------|------|------|---------------|----------------|
| latitude | ✓ (DDMMN/S) | ❌ | ❌ | ❌ | ❌ | **REPLACED** |
| longitude | ✓ (DDDMME/W) | ❌ | ❌ | ❌ | ❌ | **REPLACED** |
| latitude_encoded | ❌ | ✓ (6 digits) | ❌ | ❌ | ❌ | **TRANSIENT** |
| longitude_encoded | ❌ | ✓ (6 chars) | ❌ | ❌ | ❌ | **TRANSIENT** |
| latitude_sign | ❌ | ❌ | ✓ (+/-) | ❌ | ❌ | **TRANSIENT** |
| latitude_value | ❌ | ❌ | ✓ (6 digits) | ❌ | ❌ | **TRANSIENT** |
| longitude_sign | ❌ | ❌ | ✓ (+/-) | ❌ | ❌ | **TRANSIENT** |
| longitude_value | ❌ | ❌ | ✓ (6 digits) | ❌ | ❌ | **TRANSIENT** |
| latitude_decimal | ❌ | ❌ | ❌ | ✓ (decimal) | ❌ | **TRANSIENT** |
| longitude_decimal | ❌ | ❌ | ❌ | ✓ (decimal) | ❌ | **TRANSIENT** |
| location_code | ❌ | ❌ | ✓ (5 chars) | ❌ | ❌ | **TRANSIENT** |
| region_code | ❌ | ❌ | ✓ (4 chars) | ❌ | ❌ | **TRANSIENT** |
| accuracy_code | ❌ | ✓ (2 digits) | ✓ (2 chars) | ✓ (2 digits) | ❌ | **EVOLVED** |

**Key Evolution Patterns**:
- **Coordinate Evolution**: Degrees/minutes → encoded → signed decimal → decimal degrees → removed
- **Accuracy Tracking**: Introduced in 1979, maintained through 2020
- **Location Coding**: 2000 introduced complex location and region codes
- **Simplification**: 2020 used clean decimal degrees
- **Complete Removal**: Official SKOS version removes all spatial information

### 6. BIOMETRICS Domain Evolution

**Description**: Physical measurements including wing length, weight, bill dimensions, tarsus, fat scores, muscle condition, and moult status

| Field Name | 1966 | 1979 | 2000 | 2020 | 2020 Official | Evolution Type |
|------------|------|------|------|------|---------------|----------------|
| wing_length | ✓ (3 digits, mm) | ✓ (3 digits, mm) | ❌ | ✓ (decimal, mm) | ❌ | **EVOLVED** |
| weight | ✓ (4 digits, 0.1g) | ✓ (4 digits, 0.1g) | ❌ | ✓ (decimal, g) | ❌ | **EVOLVED** |
| bill_length | ✓ (4 digits, 0.1mm) | ✓ (4 digits, 0.1mm) | ❌ | ✓ (1 digit, code) | ❌ | **EVOLVED** |
| tarsus_length | ❌ | ✓ (2 digits, mm) | ❌ | ✓ (1 digit, code) | ❌ | **EVOLVED** |
| fat_score | ❌ | ❌ | ❌ | ✓ (1 digit, 0-9) | ❌ | **NEW** |
| muscle_score | ❌ | ❌ | ❌ | ✓ (1 digit, 0-9) | ❌ | **NEW** |
| moult_code | ❌ | ❌ | ❌ | ✓ (1 digit, 0-9) | ❌ | **NEW** |
| measurement_1 | ❌ | ❌ | ✓ (4 digits) | ❌ | ❌ | **TRANSIENT** |
| measurement_2 | ❌ | ❌ | ✓ (3 digits) | ❌ | ❌ | **TRANSIENT** |
| measurement_3 | ❌ | ❌ | ✓ (3 digits) | ❌ | ❌ | **TRANSIENT** |
| measurement_4 | ❌ | ❌ | ✓ (3 digits) | ❌ | ❌ | **TRANSIENT** |
| additional_code_2 | ❌ | ✓ (3 digits) | ❌ | ❌ | ❌ | **TRANSIENT** |

**Key Evolution Patterns**:
- **Core Measurements**: Wing, weight, bill maintained across most versions
- **Precision Evolution**: Integer measurements → decimal measurements → coded measurements
- **Condition Assessment**: 2020 introduced fat, muscle, and moult scoring
- **Generic Measurements**: 2000 used generic measurement fields
- **Complete Removal**: Official SKOS version removes all biometric data

### 7. METHODOLOGY Domain Evolution

**Description**: Capture methods, handling conditions, manipulation status, lures used, and procedural information

| Field Name | 1966 | 1979 | 2000 | 2020 | 2020 Official | Evolution Type |
|------------|------|------|------|------|---------------|----------------|
| condition_code | ✓ (2 digits) | ✓ (2 digits) | ❌ | ✓ (1 digit) | ❌ | **EVOLVED** |
| method_code | ✓ (1 digit) | ✓ (1 digit) | ❌ | ✓ (2 digits) | ❌ | **EVOLVED** |
| status_code | ❌ | ✓ (1 digit) | ✓ (1 char) | ❌ | ❌ | **TRANSIENT** |
| status_info | ❌ | ❌ | ❌ | ✓ (1 digit) | ❌ | **TRANSIENT** |
| manipulated | ❌ | ❌ | ❌ | ❌ | ✓ (1 char, priority) | **NEW** |
| moved_before | ❌ | ❌ | ❌ | ❌ | ✓ (1 digit) | **NEW** |
| catching_method | ❌ | ❌ | ❌ | ❌ | ✓ (1 char) | **NEW** |
| catching_lures | ❌ | ❌ | ❌ | ❌ | ✓ (1 char) | **NEW** |
| empty_fields_1 | ❌ | ✓ (--) | ✓ (-----) | ❌ | ❌ | **STRUCTURAL** |
| empty_fields_2 | ❌ | ✓ (--) | ✓ (---) | ❌ | ❌ | **STRUCTURAL** |
| empty_fields_3 | ❌ | ✓ (--) | ❌ | ❌ | ❌ | **STRUCTURAL** |
| separator | ❌ | ❌ | ✓ (...) | ❌ | ❌ | **STRUCTURAL** |
| padding | ❌ | ✓ (------) | ❌ | ❌ | ❌ | **STRUCTURAL** |
| final_code | ❌ | ❌ | ✓ (5 digits) | ❌ | ❌ | **STRUCTURAL** |

**Key Evolution Patterns**:
- **Core Methods**: Condition and method codes maintained across versions
- **Enhanced Methodology**: Official SKOS introduces detailed capture methodology
- **Priority Systems**: Manipulation codes use priority-based selection
- **Structural Elements**: Various versions included format-specific structural fields
- **Semantic Precision**: Official version provides precise methodological categories

## Cross-Domain Compatibility Analysis

### Version-to-Version Compatibility Summary

| From Version | To Version | Overall Compatibility | Critical Issues |
|--------------|------------|----------------------|-----------------|
| 1966 → 1979 | PARTIAL | Format change (space → fixed), coordinate encoding |
| 1979 → 2000 | LOSSY | Complex encoding, many field changes |
| 2000 → 2020 | PARTIAL | Format change (fixed → pipe), coordinate simplification |
| 2020 → 2020 Official | INCOMPATIBLE | Complete field restructure, SKOS semantics |
| Any → 2020 Official | INCOMPATIBLE | Fundamental semantic reorganization |

### Domain Stability Analysis

| Domain | Stability Score | Most Stable Fields | Most Volatile Fields |
|--------|----------------|-------------------|---------------------|
| IDENTIFICATION_MARKING | 3/10 | ring_number (until 2020) | scheme identification |
| SPECIES | 7/10 | species_code | additional codes |
| DEMOGRAPHICS | 6/10 | age_code | sex determination |
| TEMPORAL | 2/10 | none | all date formats |
| SPATIAL | 1/10 | accuracy_code | coordinate formats |
| BIOMETRICS | 4/10 | wing_length, weight | measurement encoding |
| METHODOLOGY | 5/10 | condition_code | status systems |

## Recommendations for Future Evolution

### 1. Maintain Core Stability
- Preserve essential identification fields (ring numbers, species codes)
- Maintain backward compatibility for critical demographic data
- Standardize measurement units and precision

### 2. Enhance Semantic Precision
- Continue SKOS thesaurus development
- Provide clear field definitions and editorial notes
- Implement controlled vocabularies for coded fields

### 3. Improve Conversion Support
- Develop robust conversion algorithms between versions
- Maintain conversion metadata and accuracy indicators
- Provide lossy conversion warnings and alternatives

### 4. Standardize Format Evolution
- Establish clear versioning and migration paths
- Maintain format documentation and examples
- Provide validation tools for each version

This analysis demonstrates the complex evolution of the EURING code system and provides the foundation for implementing domain-aware conversion and analysis systems.