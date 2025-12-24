# Biometrics Domain Evolution

**Description**: Physical measurements including wing length, weight, bill dimensions, tarsus, fat scores, muscle condition, and moult status

## Field Evolution Details

### additional_code_2

**Versions Present**: euring_1979

**Format Evolution**:
- euring_1979: Length: 3, Type: numeric, Pattern: ^[0-9]{3}$

**Semantic Evolution**:
- euring_1979: Additional measurement or status code

### bill_length

**Versions Present**: euring_1966, euring_1979, euring_2020

**Format Evolution**:
- euring_1966: Length: 4, Type: numeric
- euring_1979: Length: 4, Type: numeric, Pattern: ^[0-9]{4}$
- euring_2020: Length: 1, Type: numeric, Pattern: ^[0-9]$

**Semantic Evolution**:
- euring_1966: Biometric measurement - bill length
- euring_1979: Biometric measurement - bill length
- euring_2020: Biometric measurement - bill length

### fat_score

**Versions Present**: euring_2020

**Format Evolution**:
- euring_2020: Length: 1, Type: numeric, Pattern: ^[0-9]$

**Semantic Evolution**:
- euring_2020: Body fat condition score

### measurement_1

**Versions Present**: euring_2000

**Format Evolution**:
- euring_2000: Length: 4, Type: numeric, Pattern: ^[0-9]{4}$

**Semantic Evolution**:
- euring_2000: Biometric measurement 1

### measurement_2

**Versions Present**: euring_2000

**Format Evolution**:
- euring_2000: Length: 3, Type: numeric, Pattern: ^[0-9]{3}$

**Semantic Evolution**:
- euring_2000: Biometric measurement 2

### measurement_3

**Versions Present**: euring_2000

**Format Evolution**:
- euring_2000: Length: 3, Type: numeric, Pattern: ^[0-9]{3}$

**Semantic Evolution**:
- euring_2000: Biometric measurement 3

### measurement_4

**Versions Present**: euring_2000

**Format Evolution**:
- euring_2000: Length: 3, Type: numeric, Pattern: ^[0-9]{3}$

**Semantic Evolution**:
- euring_2000: Biometric measurement 4

### moult_code

**Versions Present**: euring_2020

**Format Evolution**:
- euring_2020: Length: 1, Type: numeric, Pattern: ^[0-9]$

**Semantic Evolution**:
- euring_2020: Feather moult condition

### muscle_score

**Versions Present**: euring_2020

**Format Evolution**:
- euring_2020: Length: 1, Type: numeric, Pattern: ^[0-9]$

**Semantic Evolution**:
- euring_2020: Body muscle condition score

### tarsus_length

**Versions Present**: euring_1979, euring_2020

**Format Evolution**:
- euring_1979: Length: 2, Type: numeric, Pattern: ^[0-9]{2}$
- euring_2020: Length: 1, Type: numeric, Pattern: ^[0-9]$

**Semantic Evolution**:
- euring_1979: Biometric measurement - tarsus length
- euring_2020: Biometric measurement - tarsus length

### weight

**Versions Present**: euring_1966, euring_1979, euring_2020

**Format Evolution**:
- euring_1966: Length: 4, Type: numeric
- euring_1979: Length: 4, Type: numeric, Pattern: ^[0-9]{4}$
- euring_2020: Length: 4, Type: decimal, Pattern: ^[0-9]+\.[0-9]$

**Semantic Evolution**:
- euring_1966: Biometric measurement - body weight
- euring_1979: Biometric measurement - body weight
- euring_2020: Biometric measurement - body weight

### wing_length

**Versions Present**: euring_1966, euring_1979, euring_2020

**Format Evolution**:
- euring_1966: Length: 3, Type: numeric
- euring_1979: Length: 3, Type: numeric, Pattern: ^[0-9]{3}$
- euring_2020: Length: 5, Type: decimal, Pattern: ^[0-9]+\.[0-9]$

**Semantic Evolution**:
- euring_1966: Biometric measurement - wing length
- euring_1979: Biometric measurement - wing length
- euring_2020: Biometric measurement - wing length

## Compatibility Matrix

| From \ To | euring_1966 | euring_1979 | euring_2000 | euring_2020 | euring_2020_official | 
|-----------|----------|----------|----------|----------|----------|
| euring_1966 | SAME | LOSSY | INCOMPATIBLE | INCOMPATIBLE | INCOMPATIBLE | 
| euring_1979 | LOSSY | SAME | INCOMPATIBLE | LOSSY | INCOMPATIBLE | 
| euring_2000 | INCOMPATIBLE | INCOMPATIBLE | SAME | INCOMPATIBLE | INCOMPATIBLE | 
| euring_2020 | INCOMPATIBLE | LOSSY | INCOMPATIBLE | SAME | INCOMPATIBLE | 
| euring_2020_official | INCOMPATIBLE | INCOMPATIBLE | INCOMPATIBLE | INCOMPATIBLE | SAME | 

