# Demographics Domain Evolution

**Description**: Age and sex classification systems based on plumage characteristics and morphological features

## Field Evolution Details

### age_code

**Versions Present**: euring_1966, euring_1979, euring_2000, euring_2020

**Format Evolution**:
- euring_1966: Length: 1, Type: numeric
- euring_1979: Length: 1, Type: numeric, Pattern: ^[0-9]$
- euring_2000: Length: 1, Type: numeric, Pattern: ^[0-9]$
- euring_2020: Length: 1, Type: numeric, Pattern: ^[1-9]$

**Semantic Evolution**:
- euring_1966: Bird age category
- euring_1979: Bird age category
- euring_2000: Bird age category
- euring_2020: Bird age category

### age_mentioned_by_the_person

**Versions Present**: euring_2020_official

**Format Evolution**:
- euring_2020_official: Length: 1, Type: alphanumeric, Pattern: ^[0-9A-H]$

**Semantic Evolution**:
- euring_2020_official: Age classification based on plumage state

### sex_code

**Versions Present**: euring_1979, euring_2020

**Format Evolution**:
- euring_1979: Length: 1, Type: numeric, Pattern: ^[0-9]$
- euring_2020: Length: 1, Type: numeric, Pattern: ^[1-9]$

**Semantic Evolution**:
- euring_1979: Bird sex category
- euring_2020: Bird sex category

### sex_concluded_by_the_scheme

**Versions Present**: euring_2020_official

**Format Evolution**:
- euring_2020_official: Length: 1, Type: alphanumeric, Pattern: ^[MFU]$

**Semantic Evolution**:
- euring_2020_official: Verified sex identification by scheme

### sex_mentioned_by_the_person

**Versions Present**: euring_2020_official

**Format Evolution**:
- euring_2020_official: Length: 1, Type: alphanumeric, Pattern: ^[MFU]$

**Semantic Evolution**:
- euring_2020_official: Sex identification by handler

## Compatibility Matrix

| From \ To | euring_1966 | euring_1979 | euring_2000 | euring_2020 | euring_2020_official | 
|-----------|----------|----------|----------|----------|----------|
| euring_1966 | SAME | LOSSY | FULL | LOSSY | INCOMPATIBLE | 
| euring_1979 | LOSSY | SAME | LOSSY | FULL | INCOMPATIBLE | 
| euring_2000 | FULL | LOSSY | SAME | LOSSY | INCOMPATIBLE | 
| euring_2020 | LOSSY | FULL | LOSSY | SAME | INCOMPATIBLE | 
| euring_2020_official | INCOMPATIBLE | INCOMPATIBLE | INCOMPATIBLE | INCOMPATIBLE | SAME | 

