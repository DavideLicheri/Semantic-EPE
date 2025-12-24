# Temporal Domain Evolution

**Description**: Date and time formats for recording capture, observation, and handling events

## Field Evolution Details

### date_code

**Versions Present**: euring_1966, euring_2020

**Format Evolution**:
- euring_1966: Length: 8, Type: numeric, Pattern: ^[0-3][0-9][0-1][0-9][0-9]{4}$
- euring_2020: Length: 8, Type: numeric, Pattern: ^[0-9]{8}$

**Semantic Evolution**:
- euring_1966: Capture date
- euring_2020: Capture/observation date

### date_current

**Versions Present**: euring_1979, euring_2000

**Format Evolution**:
- euring_1979: Length: 6, Type: numeric, Pattern: ^[0-9]{6}$
- euring_2000: Length: 5, Type: numeric, Pattern: ^[0-9]{5}$

**Semantic Evolution**:
- euring_1979: Date of current capture/observation
- euring_2000: Date of current capture/observation

### date_first

**Versions Present**: euring_1979, euring_2000

**Format Evolution**:
- euring_1979: Length: 6, Type: numeric, Pattern: ^[0-9]{6}$
- euring_2000: Length: 5, Type: numeric, Pattern: ^[0-9]{5}$

**Semantic Evolution**:
- euring_1979: Date of first capture/observation
- euring_2000: Date of first capture/observation

### time_code

**Versions Present**: euring_2020

**Format Evolution**:
- euring_2020: Length: 4, Type: numeric, Pattern: ^[0-9]{4}$

**Semantic Evolution**:
- euring_2020: Capture/observation time

## Compatibility Matrix

| From \ To | euring_1966 | euring_1979 | euring_2000 | euring_2020 | euring_2020_official | 
|-----------|----------|----------|----------|----------|----------|
| euring_1966 | SAME | INCOMPATIBLE | INCOMPATIBLE | LOSSY | INCOMPATIBLE | 
| euring_1979 | INCOMPATIBLE | SAME | FULL | INCOMPATIBLE | INCOMPATIBLE | 
| euring_2000 | INCOMPATIBLE | FULL | SAME | INCOMPATIBLE | INCOMPATIBLE | 
| euring_2020 | LOSSY | INCOMPATIBLE | INCOMPATIBLE | SAME | INCOMPATIBLE | 
| euring_2020_official | INCOMPATIBLE | INCOMPATIBLE | INCOMPATIBLE | INCOMPATIBLE | SAME | 

