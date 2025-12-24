# Species Domain Evolution

**Description**: Species codes, taxonomy systems, and identification verification by both finders and ringing schemes

## Field Evolution Details

### additional_code_1

**Versions Present**: euring_1979

**Format Evolution**:
- euring_1979: Length: 3, Type: numeric, Pattern: ^[0-9]{3}$

**Semantic Evolution**:
- euring_1979: Additional species or location code

### additional_codes

**Versions Present**: euring_2000

**Format Evolution**:
- euring_2000: Length: 12, Type: numeric, Pattern: ^[0-9]{12}$

**Semantic Evolution**:
- euring_2000: Additional species or measurement codes

### species_as_mentioned_by_finder

**Versions Present**: euring_2020_official

**Format Evolution**:
- euring_2020_official: Length: 5, Type: numeric, Pattern: ^[0-9]{5}$

**Semantic Evolution**:
- euring_2020_official: Species identification by person who found/handled bird

### species_as_mentioned_by_scheme

**Versions Present**: euring_2020_official

**Format Evolution**:
- euring_2020_official: Length: 5, Type: numeric, Pattern: ^[0-9]{5}$

**Semantic Evolution**:
- euring_2020_official: Verified species identification by scheme

### species_code

**Versions Present**: euring_1966, euring_1979, euring_2020

**Format Evolution**:
- euring_1966: Length: 4, Type: numeric
- euring_1979: Length: 5, Type: numeric, Pattern: ^[0-9]{5}$
- euring_2020: Length: 5, Type: numeric, Pattern: ^[0-9]{5}$

**Semantic Evolution**:
- euring_1966: EURING species code
- euring_1979: EURING species code
- euring_2020: EURING species code

## Compatibility Matrix

| From \ To | euring_1966 | euring_1979 | euring_2000 | euring_2020 | euring_2020_official | 
|-----------|----------|----------|----------|----------|----------|
| euring_1966 | SAME | LOSSY | INCOMPATIBLE | FULL | INCOMPATIBLE | 
| euring_1979 | LOSSY | SAME | INCOMPATIBLE | LOSSY | INCOMPATIBLE | 
| euring_2000 | INCOMPATIBLE | INCOMPATIBLE | SAME | INCOMPATIBLE | INCOMPATIBLE | 
| euring_2020 | FULL | LOSSY | INCOMPATIBLE | SAME | INCOMPATIBLE | 
| euring_2020_official | INCOMPATIBLE | INCOMPATIBLE | INCOMPATIBLE | INCOMPATIBLE | SAME | 

