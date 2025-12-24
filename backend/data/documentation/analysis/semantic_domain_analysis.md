# EURING Semantic Domain Analysis

This document provides a comprehensive analysis of the 7 semantic domains across all EURING code versions (1966-2020).

## Executive Summary

- **Total Versions Analyzed**: 5
- **Total Fields Analyzed**: 67
- **Semantic Domains**: 7
- **Analysis Period**: 1966-2020 (54 years of evolution)

## Semantic Domains Overview

### Identification Marking
**Description**: Ring numbers, schemes, metal rings, other marks, and verification systems for unique bird identification throughout its life

**Total Fields**: 14

**Fields in this domain**:
- `identification_number` (present in: euring_2020_official)
- `metal_ring_info` (present in: euring_2020)
- `metal_ring_information` (present in: euring_2020_official)
- `other_marks_info` (present in: euring_2020)
- `other_marks_information` (present in: euring_2020_official)
- `primary_identification_method` (present in: euring_2020_official)
- `ring_number` (present in: euring_1966, euring_1979, euring_2000, euring_2020)
- `ring_prefix` (present in: euring_2000)
- `ring_suffix` (present in: euring_2000)
- `ringing_scheme` (present in: euring_2020_official)
- `scheme_code` (present in: euring_2000)
- `scheme_country` (present in: euring_1979)
- `verification_code` (present in: euring_2020)
- `verification_of_the_metal_ring` (present in: euring_2020_official)

### Species
**Description**: Species codes, taxonomy systems, and identification verification by both finders and ringing schemes

**Total Fields**: 5

**Fields in this domain**:
- `additional_code_1` (present in: euring_1979)
- `additional_codes` (present in: euring_2000)
- `species_as_mentioned_by_finder` (present in: euring_2020_official)
- `species_as_mentioned_by_scheme` (present in: euring_2020_official)
- `species_code` (present in: euring_1966, euring_1979, euring_2020)

### Demographics
**Description**: Age and sex classification systems based on plumage characteristics and morphological features

**Total Fields**: 5

**Fields in this domain**:
- `age_code` (present in: euring_1966, euring_1979, euring_2000, euring_2020)
- `age_mentioned_by_the_person` (present in: euring_2020_official)
- `sex_code` (present in: euring_1979, euring_2020)
- `sex_concluded_by_the_scheme` (present in: euring_2020_official)
- `sex_mentioned_by_the_person` (present in: euring_2020_official)

### Temporal
**Description**: Date and time formats for recording capture, observation, and handling events

**Total Fields**: 4

**Fields in this domain**:
- `date_code` (present in: euring_1966, euring_2020)
- `date_current` (present in: euring_1979, euring_2000)
- `date_first` (present in: euring_1979, euring_2000)
- `time_code` (present in: euring_2020)

### Spatial
**Description**: Geographic coordinates, location accuracy, and spatial encoding systems for recording bird locations

**Total Fields**: 13

**Fields in this domain**:
- `accuracy_code` (present in: euring_1979, euring_2000, euring_2020)
- `latitude` (present in: euring_1966)
- `latitude_decimal` (present in: euring_2020)
- `latitude_encoded` (present in: euring_1979)
- `latitude_sign` (present in: euring_2000)
- `latitude_value` (present in: euring_2000)
- `location_code` (present in: euring_2000)
- `longitude` (present in: euring_1966)
- `longitude_decimal` (present in: euring_2020)
- `longitude_encoded` (present in: euring_1979)
- `longitude_sign` (present in: euring_2000)
- `longitude_value` (present in: euring_2000)
- `region_code` (present in: euring_2000)

### Biometrics
**Description**: Physical measurements including wing length, weight, bill dimensions, tarsus, fat scores, muscle condition, and moult status

**Total Fields**: 12

**Fields in this domain**:
- `additional_code_2` (present in: euring_1979)
- `bill_length` (present in: euring_1966, euring_1979, euring_2020)
- `fat_score` (present in: euring_2020)
- `measurement_1` (present in: euring_2000)
- `measurement_2` (present in: euring_2000)
- `measurement_3` (present in: euring_2000)
- `measurement_4` (present in: euring_2000)
- `moult_code` (present in: euring_2020)
- `muscle_score` (present in: euring_2020)
- `tarsus_length` (present in: euring_1979, euring_2020)
- `weight` (present in: euring_1966, euring_1979, euring_2020)
- `wing_length` (present in: euring_1966, euring_1979, euring_2020)

### Methodology
**Description**: Capture methods, handling conditions, manipulation status, lures used, and procedural information

**Total Fields**: 14

**Fields in this domain**:
- `catching_lures` (present in: euring_2020_official)
- `catching_method` (present in: euring_2020_official)
- `condition_code` (present in: euring_1966, euring_1979, euring_2020)
- `empty_fields_1` (present in: euring_1979, euring_2000)
- `empty_fields_2` (present in: euring_1979, euring_2000)
- `empty_fields_3` (present in: euring_1979)
- `final_code` (present in: euring_2000)
- `manipulated` (present in: euring_2020_official)
- `method_code` (present in: euring_1966, euring_1979, euring_2020)
- `moved_before` (present in: euring_2020_official)
- `padding` (present in: euring_1979)
- `separator` (present in: euring_2000)
- `status_code` (present in: euring_1979, euring_2000)
- `status_info` (present in: euring_2020)

## Evolution Timeline

### EURING Code 1966 (1966)

**Description**: First version of the EURING code system established in 1966 - space-separated format with 11 fields

**Identification Marking Changes**:
- Added: ring_number

**Species Changes**:
- Added: species_code

**Demographics Changes**:
- Added: age_code

**Temporal Changes**:
- Added: date_code

**Spatial Changes**:
- Added: longitude, latitude

**Biometrics Changes**:
- Added: wing_length, weight, bill_length

**Methodology Changes**:
- Added: condition_code, method_code


### EURING Code 1979 (1979)

**Description**: EURING code version from 1979 - fixed-length concatenated format with 78 characters. CRITICAL: Field positions corrected based on real string analysis.

**Identification Marking Changes**:
- Added: scheme_country
- Modified: ring_number
- Improvements: Fixed-length format standardization, Encoded coordinate system, Additional measurement fields

**Species Changes**:
- Added: additional_code_1
- Modified: species_code
- Improvements: Fixed-length format standardization, Encoded coordinate system, Additional measurement fields

**Demographics Changes**:
- Added: sex_code
- Modified: age_code
- Improvements: Fixed-length format standardization, Encoded coordinate system, Additional measurement fields

**Temporal Changes**:
- Added: date_first, date_current
- Removed: date_code
- Improvements: Fixed-length format standardization, Encoded coordinate system, Additional measurement fields

**Spatial Changes**:
- Added: longitude_encoded, latitude_encoded, accuracy_code
- Removed: longitude, latitude
- Improvements: Fixed-length format standardization, Encoded coordinate system, Additional measurement fields

**Biometrics Changes**:
- Added: additional_code_2, tarsus_length
- Modified: wing_length, weight, bill_length
- Improvements: Fixed-length format standardization, Encoded coordinate system, Additional measurement fields

**Methodology Changes**:
- Added: empty_fields_1, empty_fields_3, status_code, empty_fields_2, padding
- Modified: condition_code, method_code
- Improvements: Fixed-length format standardization, Encoded coordinate system, Additional measurement fields


### EURING Code 2000 (2000)

**Description**: EURING code version from 2000 - complex fixed-length format with alphanumeric codes

**Identification Marking Changes**:
- Added: ring_prefix, ring_suffix, scheme_code
- Removed: scheme_country
- Modified: ring_number
- Improvements: Complex alphanumeric encoding, Enhanced location accuracy

**Species Changes**:
- Added: additional_codes
- Removed: additional_code_1, species_code
- Improvements: Complex alphanumeric encoding, Enhanced location accuracy

**Demographics Changes**:
- Removed: sex_code
- Improvements: Complex alphanumeric encoding, Enhanced location accuracy

**Temporal Changes**:
- Modified: date_first, date_current
- Improvements: Complex alphanumeric encoding, Enhanced location accuracy

**Spatial Changes**:
- Added: longitude_value, latitude_sign, latitude_value, location_code, longitude_sign, region_code
- Removed: longitude_encoded, latitude_encoded
- Modified: accuracy_code
- Improvements: Complex alphanumeric encoding, Enhanced location accuracy

**Biometrics Changes**:
- Added: measurement_2, measurement_4, measurement_1, measurement_3
- Removed: bill_length, wing_length, weight, additional_code_2, tarsus_length
- Improvements: Complex alphanumeric encoding, Enhanced location accuracy

**Methodology Changes**:
- Added: separator, final_code
- Removed: padding, empty_fields_3, condition_code, method_code
- Modified: empty_fields_1, empty_fields_2, status_code
- Improvements: Complex alphanumeric encoding, Enhanced location accuracy


### EURING Code 2020 (2020)

**Description**: Current EURING code version with pipe-delimited format and decimal coordinates

**Identification Marking Changes**:
- Added: metal_ring_info, verification_code, other_marks_info
- Removed: ring_prefix, ring_suffix, scheme_code
- Modified: ring_number
- Improvements: Decimal coordinate format, Pipe-delimited structure, Enhanced biometric measurements

**Species Changes**:
- Added: species_code
- Removed: additional_codes
- Improvements: Decimal coordinate format, Pipe-delimited structure, Enhanced biometric measurements

**Demographics Changes**:
- Added: sex_code
- Modified: age_code
- Improvements: Decimal coordinate format, Pipe-delimited structure, Enhanced biometric measurements

**Temporal Changes**:
- Added: time_code, date_code
- Removed: date_first, date_current
- Improvements: Decimal coordinate format, Pipe-delimited structure, Enhanced biometric measurements

**Spatial Changes**:
- Added: longitude_decimal, latitude_decimal
- Removed: longitude_value, latitude_sign, latitude_value, location_code, longitude_sign, region_code
- Modified: accuracy_code
- Improvements: Decimal coordinate format, Pipe-delimited structure, Enhanced biometric measurements

**Biometrics Changes**:
- Added: bill_length, wing_length, muscle_score, fat_score, moult_code, weight, tarsus_length
- Removed: measurement_2, measurement_4, measurement_1, measurement_3
- Improvements: Decimal coordinate format, Pipe-delimited structure, Enhanced biometric measurements

**Methodology Changes**:
- Added: condition_code, status_info, method_code
- Removed: empty_fields_1, status_code, separator, final_code, empty_fields_2
- Improvements: Decimal coordinate format, Pipe-delimited structure, Enhanced biometric measurements


### EURING Code 2020 (Official SKOS) (2020)

**Description**: Official EURING 2020 code based on SKOS thesaurus with precise field definitions

**Identification Marking Changes**:
- Added: other_marks_information, identification_number, verification_of_the_metal_ring, metal_ring_information, primary_identification_method, ringing_scheme
- Removed: metal_ring_info, verification_code, ring_number, other_marks_info
- Improvements: Official SKOS thesaurus integration, Precise field definitions with editorial notes, Priority-based manipulation codes

**Species Changes**:
- Added: species_as_mentioned_by_finder, species_as_mentioned_by_scheme
- Removed: species_code
- Improvements: Official SKOS thesaurus integration, Precise field definitions with editorial notes, Priority-based manipulation codes

**Demographics Changes**:
- Added: sex_mentioned_by_the_person, age_mentioned_by_the_person, sex_concluded_by_the_scheme
- Removed: age_code, sex_code
- Improvements: Official SKOS thesaurus integration, Precise field definitions with editorial notes, Priority-based manipulation codes

**Temporal Changes**:
- Removed: time_code, date_code
- Improvements: Official SKOS thesaurus integration, Precise field definitions with editorial notes, Priority-based manipulation codes

**Spatial Changes**:
- Removed: longitude_decimal, latitude_decimal, accuracy_code
- Improvements: Official SKOS thesaurus integration, Precise field definitions with editorial notes, Priority-based manipulation codes

**Biometrics Changes**:
- Removed: fat_score, moult_code, muscle_score, bill_length, weight, wing_length, tarsus_length
- Improvements: Official SKOS thesaurus integration, Precise field definitions with editorial notes, Priority-based manipulation codes

**Methodology Changes**:
- Added: moved_before, catching_lures, manipulated, catching_method
- Removed: condition_code, status_info, method_code
- Improvements: Official SKOS thesaurus integration, Precise field definitions with editorial notes, Priority-based manipulation codes


