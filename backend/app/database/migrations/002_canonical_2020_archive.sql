-- ECES Analytics Database Schema — Migration 002
-- Canonical EURING 2020 archive + faceted search
--
-- Prerequisito: schema.sql (tabelle user_queries, unique_strings, daily_statistics,
-- user_sessions) già applicato — questa migrazione lo estende, non lo sostituisce.
--
-- Contesto/decisioni (vedi design_archivio_faccette.md nel repo, sessione 23/07/2026):
--   - Ogni stringa EURING gestita da ECES (recognize/convert/parse) viene, se possibile,
--     normalizzata in EURING 2020 (formato pipe-delimited, 64 campi, confermato con
--     stringhe reali il 23/07/2026) e archiviata qui in modo deduplicato.
--   - Se la normalizzazione a 2020 non è pulita (segment count != 64), la stringa NON
--     entra in questo archivio — resta comunque nel log classico user_queries come oggi.
--   - Per /convert si archiviano sia la stringa sorgente sia quella convertita, ciascuna
--     come proprio record se si normalizza correttamente.
--   - Non si partiziona per ora (volumi iniziali modesti); i nomi/indici sono scelti per
--     rendere un futuro partizionamento per range temporale un'aggiunta, non una riscrittura.

BEGIN;

-- Tabella principale: una riga per ogni stringa EURING 2020 distinta (deduplicata)
CREATE TABLE IF NOT EXISTS euring_2020_canonical (
    id SERIAL PRIMARY KEY,
    canonical_string TEXT UNIQUE NOT NULL,     -- la stringa EURING 2020 completa, pipe-delimited
    string_hash VARCHAR(64) UNIQUE NOT NULL,   -- SHA256 di canonical_string, per lookup rapido
    parsed_fields JSONB NOT NULL,              -- tutti i 64 campi scomposti, {field_name: value}
    field_count INTEGER NOT NULL,              -- numero di segmenti trovati (atteso: 64)
    first_seen TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    occurrence_count INTEGER NOT NULL DEFAULT 1,  -- quante volte questa stringa 2020 è stata vista/prodotta

    CONSTRAINT positive_field_count CHECK (field_count > 0),
    CONSTRAINT positive_occurrence_count CHECK (occurrence_count > 0)
);

CREATE INDEX IF NOT EXISTS idx_euring_2020_canonical_hash ON euring_2020_canonical(string_hash);
CREATE INDEX IF NOT EXISTS idx_euring_2020_canonical_first_seen ON euring_2020_canonical(first_seen);
CREATE INDEX IF NOT EXISTS idx_euring_2020_canonical_parsed_fields
    ON euring_2020_canonical USING gin(parsed_fields);

-- Tabella EAV: un valore per campo per stringa, per la ricerca a faccette
CREATE TABLE IF NOT EXISTS euring_2020_field_values (
    canonical_id INTEGER NOT NULL REFERENCES euring_2020_canonical(id) ON DELETE CASCADE,
    field_position SMALLINT NOT NULL,   -- position da euring_2020.json (1-64), stabile
    field_name TEXT NOT NULL,           -- name da euring_2020.json, per leggibilità nelle query
    field_value TEXT,                   -- valore del campo per questa stringa (può essere vuoto/NULL)

    PRIMARY KEY (canonical_id, field_position)
);

-- Indice principale per le faccette: conteggi/filtri per campo+valore
CREATE INDEX IF NOT EXISTS idx_euring_2020_field_values_facet
    ON euring_2020_field_values(field_position, field_value);

-- Indice di supporto per risalire da una stringa a tutti i suoi campi (join inverso)
CREATE INDEX IF NOT EXISTS idx_euring_2020_field_values_canonical
    ON euring_2020_field_values(canonical_id);

-- Collegamento da unique_strings (dedup "grezzo", qualsiasi versione/formato as-received)
-- al record canonico 2020 corrispondente. NULL se quella stringa grezza non si normalizza
-- in modo pulito a EURING 2020.
ALTER TABLE unique_strings
    ADD COLUMN IF NOT EXISTS canonical_id INTEGER REFERENCES euring_2020_canonical(id);

CREATE INDEX IF NOT EXISTS idx_unique_strings_canonical_id ON unique_strings(canonical_id);

-- Nota: niente funzione plpgsql di upsert qui. La logica di "inserisci il
-- canonico + le righe EAV SOLO alla prima comparsa di questa stringa,
-- altrimenti limitati ad aggiornare occurrence_count/last_seen" richiede di
-- coordinare due tabelle in modo che l'applicazione può esprimere in modo più
-- chiaro con una transazione esplicita (vedi database_service.py,
-- upsert_euring_2020_canonical) che con un singolo statement SQL.

COMMENT ON TABLE euring_2020_canonical IS
    'Archivio deduplicato di stringhe EURING normalizzate in formato 2020 (pipe-delimited, 64 campi). Popolato solo per parsing "puliti" (field_count = 64).';
COMMENT ON TABLE euring_2020_field_values IS
    'Scomposizione EAV (entity-attribute-value) dei campi di ogni stringa in euring_2020_canonical, per ricerca a faccette.';
COMMENT ON COLUMN euring_2020_canonical.parsed_fields IS
    'Copia integrale di tutti i campi scomposti in JSONB, ridondante con euring_2020_field_values per query flessibili/debug senza join.';
COMMENT ON COLUMN unique_strings.canonical_id IS
    'Riferimento al record EURING 2020 canonico corrispondente, se la stringa grezza si normalizza correttamente. NULL altrimenti.';

COMMIT;
