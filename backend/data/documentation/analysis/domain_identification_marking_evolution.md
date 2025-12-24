# Identification Marking Domain Evolution

**Description**: Ring numbers, schemes, metal rings, other marks, and verification systems for unique bird identification throughout its life

## Field Evolution Details

### identification_number

**Versions Present**: euring_2020_official

**Format Evolution**:
- euring_2020_official: Length: 10, Type: alphanumeric, Pattern: ^[A-Z0-9\.\-]{10}$

**Semantic Evolution**:
- euring_2020_official: Unique ring identifier for the bird throughout its life

### metal_ring_info

**Versions Present**: euring_2020

**Format Evolution**:
- euring_2020: Length: 1, Type: numeric, Pattern: ^[0-9]$

**Semantic Evolution**:
- euring_2020: Metal ring status or type

### metal_ring_information

**Versions Present**: euring_2020_official

**Format Evolution**:
- euring_2020_official: Length: 1, Type: numeric, Pattern: ^[0-7]$

**Semantic Evolution**:
- euring_2020_official: Status of metal ring on the bird

### other_marks_info

**Versions Present**: euring_2020

**Format Evolution**:
- euring_2020: Length: 5, Type: numeric, Pattern: ^[0-9]{5}$

**Semantic Evolution**:
- euring_2020: Additional marking information

### other_marks_information

**Versions Present**: euring_2020_official

**Format Evolution**:
- euring_2020_official: Length: 2, Type: alphanumeric, Pattern: ^[A-Z\-]{2}$

**Semantic Evolution**:
- euring_2020_official: Additional marking information

### primary_identification_method

**Versions Present**: euring_2020_official

**Format Evolution**:
- euring_2020_official: Length: 2, Type: alphanumeric, Pattern: ^[A-Z][0-9]$

**Semantic Evolution**:
- euring_2020_official: Primary identification marker type

### ring_number

**Versions Present**: euring_1966, euring_1979, euring_2000, euring_2020

**Format Evolution**:
- euring_1966: Length: 7, Type: alphanumeric, Pattern: ^[A-Z]{2}[0-9]{5}$
- euring_1979: Length: 7, Type: alphanumeric, Pattern: ^[A-Z][0-9]{6}$
- euring_2000: Length: 7, Type: numeric, Pattern: ^[0-9]{7}$
- euring_2020: Length: 8, Type: alphanumeric, Pattern: ^[A-Z]{3}[0-9]{5}$

**Semantic Evolution**:
- euring_1966: Unique ring identifier
- euring_1979: Unique ring identifier
- euring_2000: Unique ring identifier
- euring_2020: Unique ring identifier

### ring_prefix

**Versions Present**: euring_2000

**Format Evolution**:
- euring_2000: Length: 3, Type: alphanumeric, Pattern: ^[A-Z0-9]{3}$

**Semantic Evolution**:
- euring_2000: Ring series identifier

### ring_suffix

**Versions Present**: euring_2000

**Format Evolution**:
- euring_2000: Length: 2, Type: alphanumeric, Pattern: ^[A-Z]{2}$

**Semantic Evolution**:
- euring_2000: Ring series suffix

### ringing_scheme

**Versions Present**: euring_2020_official

**Format Evolution**:
- euring_2020_official: Length: 3, Type: alphanumeric, Pattern: ^[A-Z]{3}$

**Semantic Evolution**:
- euring_2020_official: Identification of ringing scheme or country

### scheme_code

**Versions Present**: euring_2000

**Format Evolution**:
- euring_2000: Length: 4, Type: alphanumeric, Pattern: ^[A-Z0-9]{4}$

**Semantic Evolution**:
- euring_2000: Ringing scheme identifier

### scheme_country

**Versions Present**: euring_1979

**Format Evolution**:
- euring_1979: Length: 2, Type: alphanumeric, Pattern: ^[A-Z]{2}$

**Semantic Evolution**:
- euring_1979: Country code for ringing scheme

### verification_code

**Versions Present**: euring_2020

**Format Evolution**:
- euring_2020: Length: 1, Type: numeric, Pattern: ^[0-9]$

**Semantic Evolution**:
- euring_2020: Data verification status

### verification_of_the_metal_ring

**Versions Present**: euring_2020_official

**Format Evolution**:
- euring_2020_official: Length: 1, Type: numeric, Pattern: ^[0-9]$

**Semantic Evolution**:
- euring_2020_official: Whether ring was verified by scheme

## Compatibility Matrix

| From \ To | euring_1966 | euring_1979 | euring_2000 | euring_2020 | euring_2020_official | 
|-----------|----------|----------|----------|----------|----------|
| euring_1966 | SAME | LOSSY | INCOMPATIBLE | INCOMPATIBLE | INCOMPATIBLE | 
| euring_1979 | LOSSY | SAME | INCOMPATIBLE | INCOMPATIBLE | INCOMPATIBLE | 
| euring_2000 | INCOMPATIBLE | INCOMPATIBLE | SAME | INCOMPATIBLE | INCOMPATIBLE | 
| euring_2020 | INCOMPATIBLE | INCOMPATIBLE | INCOMPATIBLE | SAME | INCOMPATIBLE | 
| euring_2020_official | INCOMPATIBLE | INCOMPATIBLE | INCOMPATIBLE | INCOMPATIBLE | SAME | 

