# Spatial Domain Evolution

**Description**: Geographic coordinates, location accuracy, and spatial encoding systems for recording bird locations

## Field Evolution Details

### accuracy_code

**Versions Present**: euring_1979, euring_2000, euring_2020

**Format Evolution**:
- euring_1979: Length: 2, Type: numeric, Pattern: ^[0-9]{2}$
- euring_2000: Length: 2, Type: alphanumeric, Pattern: ^[A-Z0-9]{2}$
- euring_2020: Length: 2, Type: numeric, Pattern: ^[0-9]{2}$

**Semantic Evolution**:
- euring_1979: Accuracy of location coordinates
- euring_2000: Accuracy of location coordinates
- euring_2020: Accuracy of location coordinates

### latitude

**Versions Present**: euring_1966

**Format Evolution**:
- euring_1966: Length: 5, Type: coordinate, Pattern: ^[0-9]{4}[NS]$

**Semantic Evolution**:
- euring_1966: Geographic latitude

### latitude_decimal

**Versions Present**: euring_2020

**Format Evolution**:
- euring_2020: Length: 8, Type: decimal, Pattern: ^[+-]?[0-9]+\.[0-9]+$

**Semantic Evolution**:
- euring_2020: Geographic latitude coordinate

### latitude_encoded

**Versions Present**: euring_1979

**Format Evolution**:
- euring_1979: Length: 6, Type: encoded, Pattern: ^[0-9]{6}$

**Semantic Evolution**:
- euring_1979: Geographic latitude

### latitude_sign

**Versions Present**: euring_2000

**Format Evolution**:
- euring_2000: Length: 1, Type: string, Pattern: ^[+-]$

**Semantic Evolution**:
- euring_2000: Latitude hemisphere indicator

### latitude_value

**Versions Present**: euring_2000

**Format Evolution**:
- euring_2000: Length: 6, Type: numeric, Pattern: ^[0-9]{6}$

**Semantic Evolution**:
- euring_2000: Geographic latitude coordinate

### location_code

**Versions Present**: euring_2000

**Format Evolution**:
- euring_2000: Length: 5, Type: alphanumeric, Pattern: ^[A-Z0-9]{5}$

**Semantic Evolution**:
- euring_2000: Geographic location identifier

### longitude

**Versions Present**: euring_1966

**Format Evolution**:
- euring_1966: Length: 6, Type: coordinate, Pattern: ^[0-9]{5}[EW]$

**Semantic Evolution**:
- euring_1966: Geographic longitude

### longitude_decimal

**Versions Present**: euring_2020

**Format Evolution**:
- euring_2020: Length: 9, Type: decimal, Pattern: ^[+-]?[0-9]+\.[0-9]+$

**Semantic Evolution**:
- euring_2020: Geographic longitude coordinate

### longitude_encoded

**Versions Present**: euring_1979

**Format Evolution**:
- euring_1979: Length: 6, Type: encoded, Pattern: ^[A-Z0-9]{6}$

**Semantic Evolution**:
- euring_1979: Geographic longitude

### longitude_sign

**Versions Present**: euring_2000

**Format Evolution**:
- euring_2000: Length: 1, Type: string, Pattern: ^[+-]$

**Semantic Evolution**:
- euring_2000: Longitude hemisphere indicator

### longitude_value

**Versions Present**: euring_2000

**Format Evolution**:
- euring_2000: Length: 6, Type: numeric, Pattern: ^[0-9]{6}$

**Semantic Evolution**:
- euring_2000: Geographic longitude coordinate

### region_code

**Versions Present**: euring_2000

**Format Evolution**:
- euring_2000: Length: 4, Type: alphanumeric, Pattern: ^[A-Z0-9]{4}$

**Semantic Evolution**:
- euring_2000: Geographic region identifier

## Compatibility Matrix

| From \ To | euring_1966 | euring_1979 | euring_2000 | euring_2020 | euring_2020_official | 
|-----------|----------|----------|----------|----------|----------|
| euring_1966 | SAME | INCOMPATIBLE | INCOMPATIBLE | INCOMPATIBLE | INCOMPATIBLE | 
| euring_1979 | INCOMPATIBLE | SAME | INCOMPATIBLE | INCOMPATIBLE | INCOMPATIBLE | 
| euring_2000 | INCOMPATIBLE | INCOMPATIBLE | SAME | INCOMPATIBLE | INCOMPATIBLE | 
| euring_2020 | INCOMPATIBLE | INCOMPATIBLE | INCOMPATIBLE | SAME | INCOMPATIBLE | 
| euring_2020_official | INCOMPATIBLE | INCOMPATIBLE | INCOMPATIBLE | INCOMPATIBLE | SAME | 

