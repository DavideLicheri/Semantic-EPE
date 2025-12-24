# Methodology Domain Evolution

**Description**: Capture methods, handling conditions, manipulation status, lures used, and procedural information

## Field Evolution Details

### catching_lures

**Versions Present**: euring_2020_official

**Format Evolution**:
- euring_2020_official: Length: 1, Type: alphanumeric, Pattern: ^[A-Z\-]$

**Semantic Evolution**:
- euring_2020_official: Type of lure used in capture

### catching_method

**Versions Present**: euring_2020_official

**Format Evolution**:
- euring_2020_official: Length: 1, Type: alphanumeric, Pattern: ^[A-Z\-]$

**Semantic Evolution**:
- euring_2020_official: Capture method employed

### condition_code

**Versions Present**: euring_1966, euring_1979, euring_2020

**Format Evolution**:
- euring_1966: Length: 2, Type: numeric
- euring_1979: Length: 2, Type: numeric, Pattern: ^[0-9]{2}$
- euring_2020: Length: 1, Type: numeric, Pattern: ^[0-9]$

**Semantic Evolution**:
- euring_1966: Bird condition at capture
- euring_1979: Bird condition at capture
- euring_2020: Bird condition at capture

### empty_fields_1

**Versions Present**: euring_1979, euring_2000

**Format Evolution**:
- euring_1979: Length: 2, Type: string, Pattern: ^--$
- euring_2000: Length: 5, Type: string, Pattern: ^-----$

**Semantic Evolution**:
- euring_1979: Placeholder for unused fields
- euring_2000: Placeholder for unused fields

### empty_fields_2

**Versions Present**: euring_1979, euring_2000

**Format Evolution**:
- euring_1979: Length: 2, Type: string, Pattern: ^--$
- euring_2000: Length: 3, Type: string, Pattern: ^---$

**Semantic Evolution**:
- euring_1979: Placeholder for unused fields
- euring_2000: Placeholder for unused fields

### empty_fields_3

**Versions Present**: euring_1979

**Format Evolution**:
- euring_1979: Length: 2, Type: string, Pattern: ^--$

**Semantic Evolution**:
- euring_1979: Placeholder for unused fields

### final_code

**Versions Present**: euring_2000

**Format Evolution**:
- euring_2000: Length: 5, Type: numeric, Pattern: ^[0-9]{5}$

**Semantic Evolution**:
- euring_2000: Record validation or checksum code

### manipulated

**Versions Present**: euring_2020_official

**Format Evolution**:
- euring_2020_official: Length: 1, Type: alphanumeric, Pattern: ^[A-Z]$

**Semantic Evolution**:
- euring_2020_official: Type of manipulation performed on bird

### method_code

**Versions Present**: euring_1966, euring_1979, euring_2020

**Format Evolution**:
- euring_1966: Length: 1, Type: numeric
- euring_1979: Length: 1, Type: numeric, Pattern: ^[0-9]$
- euring_2020: Length: 2, Type: numeric, Pattern: ^[0-9]{2}$

**Semantic Evolution**:
- euring_1966: Method used for capture/observation
- euring_1979: Method used for capture/observation
- euring_2020: Method used for capture/observation

### moved_before

**Versions Present**: euring_2020_official

**Format Evolution**:
- euring_2020_official: Length: 1, Type: numeric, Pattern: ^[0-9]$

**Semantic Evolution**:
- euring_2020_official: Movement status before capture/recovery

### padding

**Versions Present**: euring_1979

**Format Evolution**:
- euring_1979: Length: 6, Type: string, Pattern: ^------$

**Semantic Evolution**:
- euring_1979: End-of-record padding

### separator

**Versions Present**: euring_2000

**Format Evolution**:
- euring_2000: Length: 3, Type: string, Pattern: ^\.\.\.$

**Semantic Evolution**:
- euring_2000: Field delimiter

### status_code

**Versions Present**: euring_1979, euring_2000

**Format Evolution**:
- euring_1979: Length: 1, Type: numeric, Pattern: ^[0-9]$
- euring_2000: Length: 1, Type: alphanumeric, Pattern: ^[A-Z0-9]$

**Semantic Evolution**:
- euring_1979: Bird status or condition
- euring_2000: Bird status or condition

### status_info

**Versions Present**: euring_2020

**Format Evolution**:
- euring_2020: Length: 1, Type: numeric, Pattern: ^[0-9]$

**Semantic Evolution**:
- euring_2020: Additional status information

## Compatibility Matrix

| From \ To | euring_1966 | euring_1979 | euring_2000 | euring_2020 | euring_2020_official | 
|-----------|----------|----------|----------|----------|----------|
| euring_1966 | SAME | INCOMPATIBLE | INCOMPATIBLE | LOSSY | INCOMPATIBLE | 
| euring_1979 | INCOMPATIBLE | SAME | INCOMPATIBLE | INCOMPATIBLE | INCOMPATIBLE | 
| euring_2000 | INCOMPATIBLE | INCOMPATIBLE | SAME | INCOMPATIBLE | INCOMPATIBLE | 
| euring_2020 | LOSSY | INCOMPATIBLE | INCOMPATIBLE | SAME | INCOMPATIBLE | 
| euring_2020_official | INCOMPATIBLE | INCOMPATIBLE | INCOMPATIBLE | INCOMPATIBLE | SAME | 

