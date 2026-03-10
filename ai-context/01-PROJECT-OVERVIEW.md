# ECES - EURING Code Exchange System

## Panoramica Progetto

ECES (EURING Code Exchange System) è un sistema web per il riconoscimento, conversione e analisi di codici EURING utilizzati per l'inanellamento degli uccelli in Europa.

## Contesto

Il sistema EURING (European Union for Bird Ringing) ha evoluto nel tempo diversi formati di codifica per i dati di inanellamento:
- **EURING 1966** - Primo formato standardizzato
- **EURING 1979** - Evoluzione con più campi
- **EURING 2000** - Standard moderno con 36 campi
- **EURING 2020** - Versione più recente con campi aggiuntivi

## Obiettivi del Sistema

1. **Riconoscimento Automatico**: Identificare la versione EURING di una stringa di codice
2. **Conversione Semantica**: Convertire codici tra diverse versioni mantenendo l'integrità semantica
3. **Analisi Domini**: Visualizzare l'evoluzione dei domini semantici (specie, biometria, coordinate, ecc.)
4. **Navigazione Batch**: Analizzare e navigare grandi quantità di stringhe EURING
5. **Editing Matrice**: Permettere agli utenti autorizzati di modificare le definizioni dei campi

## Utenti Target

- **Ricercatori ornitologici**: Analisi dati storici di inanellamento
- **Centri di inanellamento**: Conversione dati tra formati
- **ISPRA**: Ente italiano che gestisce i dati di inanellamento
- **Amministratori sistema**: Gestione utenti e configurazioni

## Deployment Attuale

- **Server**: ISPRA Ubuntu Server (10.158.251.79)
- **Accesso**: Rete interna ISPRA (richiede VPN FortiClient)
- **URL**: http://10.158.251.79/
- **Credenziali default**: admin/admin (Super Admin)

## Stack Tecnologico

### Backend
- **Python 3.11** con FastAPI
- **PostgreSQL** per analytics e gestione utenti
- **JSON files** per dati EURING e configurazioni
- **Pydantic** per validazione dati

### Frontend
- **React 18** con TypeScript
- **Vite** come build tool
- **CSS modules** per styling

### Deployment
- **Nginx** come reverse proxy e server statico
- **Systemd** per gestione servizi
- **SSH** per deployment remoto

## Funzionalità Principali

### 1. Riconoscimento Versione
Analizza una stringa EURING e determina automaticamente la versione (1966, 1979, 2000, 2020) con livello di confidenza.

### 2. Conversione Codici
Converte stringhe EURING da una versione all'altra usando mappature semantiche che preservano il significato dei dati.

### 3. Navigator Stringhe
Interfaccia per caricare e navigare batch di stringhe EURING (file .txt o .csv), con parsing automatico e visualizzazione campo-valore.

### 4. Matrice EURING
Visualizzazione comparativa di tutti i campi attraverso le versioni, con possibilità di editing per utenti autorizzati.

### 5. Domini Semantici
Analisi dell'evoluzione dei 7 domini semantici:
- Identification & Marking (anelli, schemi)
- Species (codici specie)
- Demographics (età, sesso)
- Temporal (data, ora)
- Spatial (coordinate, luoghi)
- Biometrics (misure fisiche)
- Methodology (metodi cattura, condizioni)

### 6. Sistema Autenticazione
- Registrazione utenti con approvazione admin
- 3 ruoli: User, Matrix Editor, Super Admin
- Gestione profili e cambio password
- Analytics per Super Admin

## Lingua

Il sistema è **solo in italiano**. Era stato implementato un sistema i18n (italiano/inglese) ma è stato rimosso perché non funzionava correttamente. Tutti i testi dell'interfaccia sono hardcoded in italiano.

## Stato Attuale

Sistema completamente funzionante e deployato su server ISPRA. Tutte le funzionalità core sono operative:
- ✅ Riconoscimento versioni
- ✅ Conversione codici
- ✅ Navigator batch stringhe
- ✅ Matrice editing
- ✅ Domini semantici
- ✅ Autenticazione e autorizzazione
- ✅ Analytics per Super Admin
- ✅ Gestione utenti

## Problemi Noti

1. **Batch Parse con stringhe identiche**: Errore Pydantic quando si processano 3+ stringhe identiche (da investigare)
2. **Performance**: Caricamento iniziale può essere lento su rete ISPRA
3. **Cache browser**: A volte necessario hard refresh (Ctrl+Shift+R) dopo deployment

## Prossimi Sviluppi

- Fix batch parse error
- Ottimizzazione performance caricamento
- Export risultati in formati standard (CSV, Excel)
- Documentazione utente finale
