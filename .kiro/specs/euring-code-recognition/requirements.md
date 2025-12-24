# Requirements Document

## Introduction

Il sistema EURING Code Recognition è un'applicazione web per il riconoscimento automatico delle versioni del codice EURING utilizzate nelle stringhe di inanellamento e ricattura degli uccelli del Paleartico occidentale. L'applicazione deve essere in grado di identificare la versione del codice utilizzata in stringhe di formato sconosciuto e offrire la possibilità di convertirle tra diverse versioni storiche del codice EURING (dal 1963 ad oggi).

## Glossary

- **Sistema_EURING**: L'applicazione web per il riconoscimento e conversione dei codici EURING
- **Codice_EURING**: Standard europeo per la codifica dei dati di inanellamento degli uccelli
- **Stringa_EURING**: Sequenza di caratteri che rappresenta i dati di inanellamento secondo il formato EURING
- **Versione_Codice**: Specifica versione storica del codice EURING (dal 1963 ad oggi)
- **SKOS_Model**: Modello semantico che definisce le caratteristiche e relazioni tra le versioni del codice organizzato per domini semantici
- **Dominio_Semantico**: Ambito specifico del codice EURING (identificazione, specie, demografia, temporale, spaziale, biometria, metodologia)
- **Evoluzione_Dominio**: Tracciamento dei cambiamenti storici di un dominio semantico specifico attraverso le versioni
- **Utente_Autorizzato**: Utente che ha accesso al sistema tramite credenziali valide
- **Conversione_Formato**: Processo di traduzione di una stringa EURING da una versione ad un'altra

## Requirements

### Requirement 1

**User Story:** Come utente autorizzato, voglio accedere al sistema tramite password, così da poter utilizzare le funzionalità di riconoscimento e conversione in modo sicuro.

#### Acceptance Criteria

1. WHEN un utente inserisce credenziali valide, THEN il Sistema_EURING SHALL concedere l'accesso alle funzionalità principali
2. WHEN un utente inserisce credenziali non valide, THEN il Sistema_EURING SHALL negare l'accesso e mostrare un messaggio di errore
3. WHEN un utente non autenticato tenta di accedere alle funzionalità, THEN il Sistema_EURING SHALL reindirizzare alla pagina di login
4. WHEN una sessione utente scade, THEN il Sistema_EURING SHALL richiedere una nuova autenticazione

### Requirement 2

**User Story:** Come ricercatore ornitologico, voglio inserire stringhe EURING di formato sconosciuto, così da poter identificare quale versione del codice è stata utilizzata.

#### Acceptance Criteria

1. WHEN un utente inserisce una Stringa_EURING, THEN il Sistema_EURING SHALL accettare l'input e avviare il processo di riconoscimento
2. WHEN una Stringa_EURING viene analizzata, THEN il Sistema_EURING SHALL identificare la Versione_Codice utilizzata
3. WHEN il riconoscimento è completato, THEN il Sistema_EURING SHALL mostrare la versione identificata con il livello di confidenza
4. WHEN una stringa non è riconoscibile, THEN il Sistema_EURING SHALL informare l'utente e suggerire possibili cause
5. WHEN vengono inserite multiple stringhe in batch, THEN il Sistema_EURING SHALL permettere all'utente di specificare se sono della stessa versione o di versioni diverse
6. WHEN l'utente dichiara che le stringhe sono della stessa versione, THEN il Sistema_EURING SHALL ottimizzare il riconoscimento applicando la versione identificata a tutte le stringhe
7. WHEN l'utente indica versioni diverse, THEN il Sistema_EURING SHALL analizzare individualmente ciascuna stringa e presentare i risultati organizzati

### Requirement 3

**User Story:** Come curatore di database ornitologici, voglio convertire stringhe EURING tra diverse versioni del codice, così da standardizzare i dati storici.

#### Acceptance Criteria

1. WHEN una Versione_Codice è identificata, THEN il Sistema_EURING SHALL mostrare le versioni disponibili per la conversione
2. WHEN un utente seleziona una versione target, THEN il Sistema_EURING SHALL eseguire la Conversione_Formato
3. WHEN la conversione è completata, THEN il Sistema_EURING SHALL mostrare la stringa convertita nel nuovo formato
4. WHEN la conversione non è possibile, THEN il Sistema_EURING SHALL spiegare i motivi dell'incompatibilità
5. WHEN vengono convertite multiple stringhe, THEN il Sistema_EURING SHALL mantenere la corrispondenza tra originali e convertite

### Requirement 4

**User Story:** Come amministratore di dati, voglio salvare ed esportare le stringhe convertite, così da poter utilizzare i dati standardizzati in altri sistemi.

#### Acceptance Criteria

1. WHEN una conversione è completata, THEN il Sistema_EURING SHALL offrire opzioni per salvare i risultati
2. WHEN l'utente richiede il salvataggio, THEN il Sistema_EURING SHALL memorizzare le stringhe originali e convertite
3. WHEN l'utente richiede l'esportazione, THEN il Sistema_EURING SHALL generare un file con i dati nel formato richiesto
4. WHEN vengono salvate multiple conversioni, THEN il Sistema_EURING SHALL organizzare i dati in modo strutturato
5. WHEN l'esportazione è richiesta, THEN il Sistema_EURING SHALL includere metadati sulla conversione effettuata

### Requirement 5

**User Story:** Come sviluppatore del sistema, voglio modellare le versioni del codice EURING in SKOS con domini semantici modulari, così da definire formalmente le caratteristiche e l'evoluzione di ogni ambito specifico.

#### Acceptance Criteria

1. WHEN il sistema viene inizializzato, THEN il Sistema_EURING SHALL caricare il SKOS_Model con tutte le versioni storiche organizzate per domini semantici
2. WHEN una nuova versione viene aggiunta, THEN il Sistema_EURING SHALL aggiornare il SKOS_Model mantenendo le relazioni per ogni dominio semantico
3. WHEN vengono definite le caratteristiche di una versione, THEN il Sistema_EURING SHALL memorizzare i campi, formati e regole specifiche organizzati per dominio semantico
4. WHEN vengono mappate le modifiche tra versioni, THEN il Sistema_EURING SHALL registrare le trasformazioni necessarie per ogni dominio semantico
5. WHEN il modello viene interrogato, THEN il Sistema_EURING SHALL fornire informazioni accurate sulle versioni e le loro relazioni per dominio specifico
6. WHEN viene richiesta l'evoluzione di un dominio, THEN il Sistema_EURING SHALL mostrare i cambiamenti storici per quel dominio specifico
7. WHEN vengono analizzati i domini indipendentemente, THEN il Sistema_EURING SHALL permettere l'analisi isolata di ogni ambito semantico

### Requirement 6

**User Story:** Come ricercatore, voglio che il sistema riconosca accuratamente le versioni del codice EURING dal 1963 ad oggi, così da poter lavorare con dati storici di qualsiasi periodo.

#### Acceptance Criteria

1. WHEN viene processata una stringa del 1963, THEN il Sistema_EURING SHALL riconoscere la prima versione del codice EURING
2. WHEN viene processata una stringa contemporanea, THEN il Sistema_EURING SHALL riconoscere l'ultima versione disponibile
3. WHEN vengono analizzate stringhe di periodi intermedi, THEN il Sistema_EURING SHALL identificare correttamente la versione specifica
4. WHEN esistono ambiguità tra versioni, THEN il Sistema_EURING SHALL utilizzare algoritmi di disambiguazione basati sul contesto
5. WHEN il riconoscimento è incerto, THEN il Sistema_EURING SHALL fornire multiple opzioni con livelli di probabilità

### Requirement 8

**User Story:** Come ricercatore ornitologico, voglio analizzare l'evoluzione storica di domini semantici specifici, così da comprendere come sono cambiati gli standard di codifica nel tempo.

#### Acceptance Criteria

1. WHEN viene richiesta l'analisi di un dominio semantico, THEN il Sistema_EURING SHALL mostrare l'evoluzione storica di quel dominio attraverso tutte le versioni
2. WHEN vengono confrontate versioni per un dominio, THEN il Sistema_EURING SHALL evidenziare le differenze specifiche per quel dominio
3. WHEN viene visualizzata l'evoluzione temporale, THEN il Sistema_EURING SHALL mostrare una timeline dei cambiamenti per dominio
4. WHEN vengono analizzati i campi di un dominio, THEN il Sistema_EURING SHALL raggruppare i campi correlati semanticamente
5. WHEN viene richiesta la compatibilità tra domini, THEN il Sistema_EURING SHALL valutare la compatibilità di conversione per dominio specifico
6. WHEN vengono esportati i dati di evoluzione, THEN il Sistema_EURING SHALL generare report strutturati per dominio semantico
7. WHEN viene interrogato un dominio specifico, THEN il Sistema_EURING SHALL fornire documentazione dettagliata sull'evoluzione di quel dominio