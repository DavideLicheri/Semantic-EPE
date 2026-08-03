-- ECES Analytics Database Schema — Migration 004
-- Sostituisce lizzy_species_place_month_stats (migrazione 003, mai popolata,
-- ancora vuota in produzione) con una versione a PENTADI + ringing_scheme.
--
-- Contesto/decisioni (HANDOFF.md, 30/07/2026, dopo il deploy della 003):
--   - Granularita' temporale: pentadi (73/anno, 5 giorni ciascuna) invece di
--     mesi, su richiesta di Davide -- risoluzione fenologica molto piu' fine
--     per specie con calendari migratori/di svernamento differenti. Nessuna
--     fase fenologica codificata a priori (svernante/migrazione primaverile/
--     riproduzione/migrazione autunnale): il pattern per specie emerge dai
--     conteggi stessi, non da confini di fase decisi qui.
--   - Convenzione 29 febbraio: fuso nella stessa pentade del 28 febbraio
--     (calendario di riferimento non bisestile fisso), verificata con
--     esempi numerici concreti prima di procedere (vedi
--     backend/app/services/phenology_utils.py). Le pentadi NON sono
--     allineate ai confini dei mesi da fine febbraio in poi (28 non e'
--     divisibile per 5) -- normale per un sistema a pentadi.
--   - ringing_scheme aggiunto alla chiave: scoperto durante il deploy della
--     003 che l'archivio contiene gia' dati reali di piu' schemi (IAB, ESC).
--     Necessario per poter dichiarare la provenienza di ogni risposta di
--     Lizzy (decisione 30/07/2026 sul punto 14: "basato su dati di N schemi,
--     M osservazioni" invece di una soglia fissa di "sufficienza").
--   - place_code qui e' SEMPRE 'current place code' (luogo di QUESTO evento),
--     non 'place code' (luogo di inanellamento originale) -- stessa scelta
--     gia' motivata nella migrazione 003.

BEGIN;

DROP TABLE IF EXISTS lizzy_species_place_month_stats;

CREATE TABLE IF NOT EXISTS lizzy_species_place_pentad_stats (
    species_code TEXT NOT NULL,
    place_code TEXT NOT NULL,
    pentad SMALLINT NOT NULL,
    ringing_scheme TEXT NOT NULL,
    occurrence_count INTEGER NOT NULL DEFAULT 0,

    PRIMARY KEY (species_code, place_code, pentad, ringing_scheme),
    CONSTRAINT chk_lizzy_pentad_range CHECK (pentad BETWEEN 1 AND 73),
    CONSTRAINT positive_occurrence_count_lizzy_pentad CHECK (occurrence_count >= 0)
);

-- Indice di supporto per la query di consultazione tipica: totale + numero
-- di schemi distinti per una combinazione specie+luogo+pentade, a
-- prescindere dallo schema specifico.
CREATE INDEX IF NOT EXISTS idx_lizzy_pentad_species_place
    ON lizzy_species_place_pentad_stats(species_code, place_code, pentad);

COMMENT ON TABLE lizzy_species_place_pentad_stats IS
    'Contatore aggregato e anonimo (nessun riferimento a canonical_id, utente, o stringa) specie+luogo+pentade+schema, base statistica per i controlli di plausibilita'' di Lizzy (punto 14a). Incrementato dal codice applicativo SOLO per record il cui owner_username ha consents_to_aggregate_analysis=true in data/auth/users.json (verifica in Python, non via join SQL). La query di consultazione somma occurrence_count su tutti gli schemi per il totale, e conta ringing_scheme distinti per la dichiarazione di provenienza (decisione 30/07/2026: nessuna soglia fissa di "sufficienza", si dichiara sempre la provenienza invece).';
COMMENT ON COLUMN lizzy_species_place_pentad_stats.pentad IS
    'Pentade 1-73 (5 giorni ciascuna), calcolata da backend/app/services/phenology_utils.py. Convenzione: 29 febbraio fuso nella pentade del 28 febbraio, pentadi non allineate ai confini di mese da fine febbraio in poi -- verificato con esempi concreti il 30/07/2026.';
COMMENT ON COLUMN lizzy_species_place_pentad_stats.place_code IS
    'Deliberatamente "current place code" (luogo di QUESTO evento) e non "place code" (luogo di inanellamento originale) -- vedi stessa nota in migrazione 003.';

COMMIT;
