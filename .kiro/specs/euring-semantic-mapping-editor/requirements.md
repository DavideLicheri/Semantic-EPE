# Requirements Document

## Introduction

Il sistema attuale di riconoscimento EURING presenta definizioni semantiche deboli e incongruenze nei mapping tra versioni, come evidenziato nell'analisi della matrice EURING. È necessario un editor interattivo che permetta di definire manualmente e correggere i mapping semantici tra le diverse versioni EURING, migliorando l'accuratezza del riconoscimento e della conversione.

## Context

Il sistema attuale include:
- **Matrice EURING**: Vista comparativa che mostra l'evoluzione dei campi tra versioni (1966, 1979, 2000, 2020)
- **Parser EPE**: Gold standard per EURING 2000 con 36 campi definiti e posizioni esatte
- **Domini Semantici**: 7 domini (Identification, Species, Demographics, Temporal, Spatial, Biometrics, Methodology)
- **API Endpoints**: Sistema completo per analisi domini, compatibilità e export
- **Navigatore Stringhe**: Interfaccia per parsing e visualizzazione campo-valore

L'editor deve integrarsi con questa architettura esistente e utilizzare EPE come riferimento assoluto per EURING 2000.

## Glossary

- **Semantic_Mapping_Editor**: Interfaccia per editare i mapping semantici tra versioni EURING
- **Field_Correspondence**: Corrispondenza tra campi di versioni diverse basata su significato semantico
- **Manual_Override**: Possibilità di sovrascrivere i mapping automatici con definizioni manuali
- **Validation_Engine**: Sistema per validare i mapping usando stringhe EURING reali e parser EPE
- **Export_System**: Sistema per esportare le definizioni corrette in formato utilizzabile dal sistema
- **EPE_Gold_Standard**: Parser EURING 2000 che ha funzionato correttamente per 10 anni (riferimento assoluto)
- **Matrix_Integration**: Integrazione con la vista matrice EURING esistente per visualizzazione comparativa
- **Domain_Mapping**: Mapping semantico all'interno dei 7 domini semantici esistenti

## Requirements

### Requirement 1: Visualizzazione Mapping Attuali

**User Story:** Come esperto EURING, voglio visualizzare i mapping semantici attuali tra versioni, così da identificare incongruenze e problemi.

#### Acceptance Criteria

1. WHEN accedo all'editor di mapping THEN il sistema SHALL mostrare una matrice interattiva dei mapping attuali
2. WHEN visualizzo un mapping THEN il sistema SHALL evidenziare le incongruenze e i campi non mappati
3. WHEN seleziono un campo THEN il sistema SHALL mostrare tutti i dettagli (posizione, lunghezza, tipo, significato)
4. WHEN identifico un'incongruenza THEN il sistema SHALL permettere di contrassegnarla per correzione
5. WHEN visualizzo i mapping THEN il sistema SHALL mostrare il livello di confidenza per ogni corrispondenza

### Requirement 2: Editor Manuale dei Mapping

**User Story:** Come esperto EURING, voglio editare manualmente i mapping tra campi, così da correggere le incongruenze semantiche.

#### Acceptance Criteria

1. WHEN seleziono un campo di riferimento THEN il sistema SHALL permettere di scegliere il campo corrispondente in altre versioni
2. WHEN creo un mapping manuale THEN il sistema SHALL permettere di definire posizione, lunghezza, tipo di dato e significato semantico
3. WHEN salvo un mapping THEN il sistema SHALL validare la coerenza delle definizioni
4. WHEN modifico un mapping esistente THEN il sistema SHALL mantenere uno storico delle modifiche
5. WHEN definisco un mapping THEN il sistema SHALL permettere di aggiungere note esplicative

### Requirement 3: Validazione con Dati Reali

**User Story:** Come esperto EURING, voglio validare i mapping usando stringhe EURING reali, così da verificare la correttezza delle definizioni.

#### Acceptance Criteria

1. WHEN carico stringhe EURING di test THEN il sistema SHALL applicare i mapping e mostrare i risultati
2. WHEN un mapping fallisce THEN il sistema SHALL evidenziare l'errore e suggerire correzioni
3. WHEN valido un mapping THEN il sistema SHALL mostrare statistiche di successo per versione
4. WHEN testo una stringa THEN il sistema SHALL mostrare il parsing campo per campo con i mapping applicati
5. WHEN identifico errori THEN il sistema SHALL permettere di correggere i mapping direttamente dall'interfaccia di validazione

### Requirement 4: Gestione Versioni e Backup

**User Story:** Come amministratore del sistema, voglio gestire versioni dei mapping e backup, così da poter ripristinare configurazioni precedenti.

#### Acceptance Criteria

1. WHEN salvo modifiche THEN il sistema SHALL creare automaticamente una versione dei mapping
2. WHEN voglio ripristinare THEN il sistema SHALL permettere di tornare a versioni precedenti
3. WHEN esporto mapping THEN il sistema SHALL creare un backup completo delle definizioni
4. WHEN importo mapping THEN il sistema SHALL validare la compatibilità con la versione attuale
5. WHEN gestisco versioni THEN il sistema SHALL mostrare un log delle modifiche con timestamp e autore

### Requirement 5: Interfaccia Drag & Drop

**User Story:** Come utente dell'editor, voglio un'interfaccia intuitiva drag & drop, così da creare mapping facilmente.

#### Acceptance Criteria

1. WHEN trascino un campo THEN il sistema SHALL mostrare le possibili destinazioni compatibili
2. WHEN rilascio un campo su una destinazione THEN il sistema SHALL creare automaticamente il mapping
3. WHEN creo un mapping drag & drop THEN il sistema SHALL pre-compilare i dettagli basandosi sui metadati
4. WHEN un mapping non è valido THEN il sistema SHALL impedire il drop e mostrare il motivo
5. WHEN uso drag & drop THEN il sistema SHALL fornire feedback visivo durante l'operazione

### Requirement 6: Export e Integrazione

**User Story:** Come sviluppatore del sistema, voglio esportare i mapping corretti, così da integrarli nel sistema di riconoscimento.

#### Acceptance Criteria

1. WHEN esporto mapping THEN il sistema SHALL generare file JSON compatibili con il sistema attuale
2. WHEN esporto definizioni THEN il sistema SHALL includere tutti i metadati necessari (posizione, tipo, lunghezza)
3. WHEN integro mapping THEN il sistema SHALL fornire API per aggiornare le definizioni in tempo reale
4. WHEN esporto configurazioni THEN il sistema SHALL permettere export parziale per versione specifica
5. WHEN genero export THEN il sistema SHALL validare la completezza e coerenza dei dati

### Requirement 7: Analisi e Statistiche

**User Story:** Come esperto EURING, voglio analizzare la qualità dei mapping, così da identificare aree che necessitano miglioramento.

#### Acceptance Criteria

1. WHEN accedo alle statistiche THEN il sistema SHALL mostrare metriche di qualità dei mapping per versione
2. WHEN analizzo i mapping THEN il sistema SHALL identificare campi con bassa confidenza o problematici
3. WHEN visualizzo report THEN il sistema SHALL mostrare percentuali di successo per tipo di campo
4. WHEN genero analisi THEN il sistema SHALL suggerire priorità per le correzioni manuali
5. WHEN esporto statistiche THEN il sistema SHALL fornire report dettagliati in formato CSV/PDF

### Requirement 8: Collaborazione Multi-Utente

**User Story:** Come team di esperti EURING, vogliamo collaborare sui mapping, così da sfruttare la conoscenza collettiva.

#### Acceptance Criteria

1. WHEN più utenti editano THEN il sistema SHALL gestire modifiche concorrenti senza conflitti
2. WHEN un utente modifica un mapping THEN il sistema SHALL notificare gli altri collaboratori
3. WHEN propongo una modifica THEN il sistema SHALL permettere review e approvazione da parte di altri esperti
4. WHEN c'è disaccordo THEN il sistema SHALL permettere discussioni e commenti sui mapping specifici
5. WHEN collaboro THEN il sistema SHALL mantenere traccia dei contributi di ogni utente

### Requirement 9: Integrazione Sistema Esistente

**User Story:** Come sviluppatore del sistema, voglio integrare l'editor con l'architettura esistente, così da mantenere coerenza e riutilizzare componenti.

#### Acceptance Criteria

1. WHEN accedo all'editor THEN il sistema SHALL integrarsi come nuova scheda nella UI esistente
2. WHEN modifico mapping THEN il sistema SHALL utilizzare gli endpoint API esistenti per domini e compatibilità
3. WHEN valido mapping THEN il sistema SHALL utilizzare il parser EPE come gold standard per EURING 2000
4. WHEN visualizzo mapping THEN il sistema SHALL riutilizzare i componenti della matrice EURING esistente
5. WHEN esporto mapping THEN il sistema SHALL integrarsi con il sistema di export domini esistente
6. WHEN navigo tra versioni THEN il sistema SHALL utilizzare i metadati delle versioni già caricate
7. WHEN analizzo domini THEN il sistema SHALL utilizzare i 7 domini semantici già definiti
8. WHEN testo mapping THEN il sistema SHALL integrarsi con il navigatore stringhe esistente