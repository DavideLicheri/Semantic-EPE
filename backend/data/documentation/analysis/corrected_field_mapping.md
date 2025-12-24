# Mappatura Corretta dei Campi EURING

## Analisi Basata sui Dati Reali

### Stringhe di Riferimento
- **1966**: `5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750` (55 caratteri)
- **1979**: `05320ISA12345 099200501199505215215N01325E10321--0500115--075010--001090------` (78 caratteri)
- **2000**: `IABA0SA...7285004ZZ1187011870H0ZUMM55U-----0105200600600IA13+452409+009033908200400000---00086` (94 caratteri)
- **2020**: `05320|ISA12345|0|09920|3|2|20230521|1430|52.25412|-1.34521|1|10|01|0|0|135.5|19.5|4|2|0|0|2` (91 caratteri)

## Mappatura Campo per Campo

### 1. SPECIES CODE (Codice Specie)
| Versione | Valore | Posizione | Formato | Note |
|----------|--------|-----------|---------|------|
| 1966 | `5320` | Campo 1 | 4 cifre | Senza zero iniziale |
| 1979 | `05320` | 0-5 | 5 cifre | Con zero iniziale |
| 2000 | `?` | Codificato | ? | Probabilmente in scheme_code |
| 2020 | `05320` | Campo 1 | 5 cifre | Con zero iniziale |

**Conversione**: 1966 ↔ 1979/2020 (aggiungere/rimuovere zero iniziale)

### 2. RING NUMBER (Numero Anello)
| Versione | Valore | Posizione | Formato | Note |
|----------|--------|-----------|---------|------|
| 1966 | `TA12345` | Campo 2 | 2 lettere + 5 cifre | Formato semplice |
| 1979 | `A12345 ` | 7-14 | 1 lettera + 5 cifre + spazio | Spazio finale |
| 2000 | `7285004` | 10-17 | 7 cifre | Solo numerico |
| 2020 | `ISA12345` | Campo 2 | 3 lettere + 5 cifre | Formato moderno |

**Problema**: I ring number sono completamente diversi tra le versioni!

### 3. SCHEME/COUNTRY CODE
| Versione | Valore | Posizione | Formato | Note |
|----------|--------|-----------|---------|------|
| 1966 | N/A | - | - | Non presente |
| 1979 | `IS` | 5-7 | 2 lettere | Codice paese |
| 2000 | `IABA` | 0-4 | 4 caratteri | Codice schema |
| 2020 | N/A | - | - | Non presente |

### 4. AGE CODE (Codice Età)
| Versione | Valore | Posizione | Formato | Note |
|----------|--------|-----------|---------|------|
| 1966 | `3` | Campo 3 | 1 cifra | Diretto |
| 1979 | `0` | 14-15 | 1 cifra | Diverso valore! |
| 2000 | `0` | 30-31 | 1 cifra | Stesso di 1979 |
| 2020 | `3` | Campo 5 | 1 cifra | Stesso di 1966 |

**Problema**: Valori diversi per lo stesso uccello!

### 5. SEX CODE (Codice Sesso)
| Versione | Valore | Posizione | Formato | Note |
|----------|--------|-----------|---------|------|
| 1966 | N/A | - | - | Non presente |
| 1979 | `9` | 15-16 | 1 cifra | Presente |
| 2000 | `?` | ? | 1 cifra | Da identificare |
| 2020 | `2` | Campo 6 | 1 cifra | Diverso valore! |

### 6. DATE (Data)
| Versione | Valore | Posizione | Formato | Note |
|----------|--------|-----------|---------|------|
| 1966 | `11022023` | Campo 4 | DDMMYYYY | 11/02/2023 |
| 1979 | `200501` + `199505` | 17-23, 23-29 | DDMMYY doppio | Due date diverse! |
| 2000 | `11870` + `11870` | 19-24, 24-29 | Codificato | Date codificate |
| 2020 | `20230521` | Campo 7 | YYYYMMDD | 21/05/2023 |

**Problema**: Date completamente diverse tra le versioni!

### 7. COORDINATES (Coordinate)
| Versione | Valore | Posizione | Formato | Note |
|----------|--------|-----------|---------|------|
| 1966 | `5215N 01325E` | Campo 5-6 | DDMMN DDDMME | 52°15'N 013°25'E |
| 1979 | `215215N01325` | 29-41 | Confuso | Parsing errato |
| 2000 | `+452409+009033` | 60-74 | Signed encoded | Coordinate codificate |
| 2020 | `52.25412 -1.34521` | Campo 9-10 | Decimali | Coordinate diverse! |

**Problema**: Coordinate completamente diverse!

## Conclusioni Importanti

### 🚨 **PROBLEMA CRITICO**: 
Le stringhe fornite **NON rappresentano lo stesso uccello**! Ogni versione ha:
- Ring number diversi
- Date diverse  
- Coordinate diverse
- Valori di età diversi

### Possibili Spiegazioni:
1. **Stringhe di esempio diverse**: Ogni stringa rappresenta un uccello diverso
2. **Conversioni già applicate**: Le stringhe potrebbero essere già state convertite
3. **Formati di test**: Potrebbero essere stringhe di test non correlate

### Raccomandazioni:
1. **Verificare con la documentazione PDF** se le stringhe rappresentano lo stesso uccello
2. **Ottenere stringhe correlate** dello stesso uccello in versioni diverse
3. **Definire regole di conversione** basate sulla documentazione ufficiale
4. **Creare mapping semantici** indipendenti dai valori specifici

### Prossimi Passi:
1. Analizzare la documentazione PDF per capire i formati
2. Definire regole di conversione teoriche
3. Implementare conversioni basate su logica semantica
4. Testare con dati correlati quando disponibili