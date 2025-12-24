# Analisi Campo per Campo - Tutte le Versioni EURING

## Stringhe Reali di Riferimento

### EURING 1966 (55 caratteri, separati da spazi)
```
5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750
```

### EURING 1979 (78 caratteri, formato fisso)
```
05320ISA12345 099200501199505215215N01325E10321--0500115--075010--001090------
```

### EURING 2000 (96 caratteri, formato fisso complesso)
```
IABA0SA...7285004ZZ1187011870H0ZUMM55U-----0105200600600IA13+452409+009033908200400000---00086
```

### EURING 2020 (pipe-delimited, 22 campi)
```
05320|ISA12345|0|09920|3|2|20230521|1430|52.25412|-1.34521|1|10|01|0|0|135.5|19.5|4|2|0|0|2
```

## Analisi Campo per Campo

### Campo 1: SPECIES CODE (Codice Specie)

| Versione | Valore | Posizione | Lunghezza | Formato | Note |
|----------|--------|-----------|-----------|---------|------|
| 1966 | `5320` | 1 | 4 | Numerico | 4 cifre |
| 1979 | `05320` | 1-5 | 5 | Numerico | 5 cifre con zero iniziale |
| 2000 | `?` | ? | ? | ? | Da identificare nella stringa complessa |
| 2020 | `05320` | 1 | 5 | Numerico | 5 cifre con zero iniziale |

**Semantica**: Codice identificativo della specie secondo il sistema EURING
**Conversione**: 1966 (4 cifre) ↔ 1979/2020 (5 cifre con padding zero)

### Campo 2: RING NUMBER (Numero Anello)

| Versione | Valore | Posizione | Lunghezza | Formato | Note |
|----------|--------|-----------|-----------|---------|------|
| 1966 | `TA12345` | 2 | 7 | 2 lettere + 5 cifre | Formato semplice |
| 1979 | `ISA12345` | 6-12 | 7 | 3 lettere + 4 cifre? | Da verificare |
| 2000 | `SA...7285004` | ? | ? | Complesso con separatori | Da analizzare |
| 2020 | `ISA12345` | 2 | 8 | 3 lettere + 5 cifre | Formato moderno |

**Semantica**: Identificativo univoco dell'anello
**Conversione**: Formati diversi richiedono parsing e ricostruzione

### Campo 3: AGE CODE (Codice Età)

| Versione | Valore | Posizione | Lunghezza | Formato | Note |
|----------|--------|-----------|-----------|---------|------|
| 1966 | `3` | 3 | 1 | Numerico | Singola cifra |
| 1979 | `0` | ? | 1 | Numerico | Da localizzare |
| 2000 | `0` | ? | 1 | Numerico | Da localizzare |
| 2020 | `3` | 5 | 1 | Numerico | Singola cifra |

**Semantica**: Classificazione dell'età dell'uccello
**Conversione**: Diretta, stessi valori

### Campo 4: SEX CODE (Codice Sesso)

| Versione | Valore | Posizione | Lunghezza | Formato | Note |
|----------|--------|-----------|-----------|---------|------|
| 1966 | `?` | ? | ? | ? | Non presente o implicito |
| 1979 | `9` | ? | 1 | Numerico | Da localizzare |
| 2000 | `?` | ? | 1 | ? | Da localizzare |
| 2020 | `2` | 6 | 1 | Numerico | Singola cifra |

**Semantica**: Identificazione del sesso dell'uccello
**Conversione**: Potrebbe richiedere valori di default per versioni che non lo hanno

## Prossimi Passi

1. **Analisi Dettagliata**: Scomporre ogni stringa carattere per carattere
2. **Identificazione Campi**: Localizzare ogni campo in ogni versione
3. **Mappatura Semantica**: Definire il significato di ogni campo
4. **Regole di Conversione**: Stabilire come convertire tra formati
5. **Validazione**: Verificare la correttezza delle mappature

## Domande per la Documentazione

1. Quali sono i valori validi per ogni campo?
2. Ci sono campi opzionali o sempre presenti?
3. Come gestire i campi mancanti nelle conversioni?
4. Esistono regole di validazione incrociate tra campi?