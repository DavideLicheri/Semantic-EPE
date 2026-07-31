-- ECES Analytics Database Schema — Migration 003
-- Proprietà/visibilità dei record, alias del numero di anello, richieste di
-- contatto tra utenti, contatori aggregati per la conoscenza semantica di Lizzy.
--
-- Prerequisito: migrazione 002 (euring_2020_canonical, euring_2020_field_values)
-- già applicata.
--
-- Contesto/decisioni (vedi HANDOFF.md, "Discussione di dominio 25/07/2026" e
-- sessione di ripresa del 30/07/2026 — nessuna scelta qui non discussa con Davide):
--
--   - Ogni record dell'archivio a faccette ha un proprietario (chi l'ha
--     sottomesso) e una visibilità a 3 livelli: pubblico, privato, condiviso
--     con una lista specifica di utenti (punto 7).
--   - Il numero di anello reale non compare mai nella vista condivisa/pubblica:
--     si usa un alias stabile (schema+anello -> intero sequenziale), calcolato
--     per OGNI record indipendentemente dalla sua visibilità (punto 10) --
--     stesso pattern del NEXTVALID storico di EPE, e -- scoperto il 30/07/2026
--     analizzando il LOD RDF pubblico ISPRA (epe_organism_*.nt.gz) -- lo stesso
--     pattern esatto già in uso in produzione da ISPRA per la pubblicazione LOD
--     (organism/NNNNN_XXXXXX = "pseudonimo del numero di anello", isIssuedBy
--     organisation/001). Non è un caso: Davide aveva condiviso lui stesso
--     l'idea del NEXTVALID di EPE con i colleghi ISPRA che curano il LOD.
--   - Una ricattura che coinvolge 2+ utenti diversi rende quei record
--     automaticamente "condivisi" tra i soli utenti coinvolti (punto 7).
--   - I record non visibili ad un utente (di altri, non pubblici, non
--     condivisi con lui) restano contati ma non esposti nel dettaglio: serve
--     poter dire "esistono altri N eventi per questo anello, non condivisi con
--     te" (punto 9-10) e offrire una richiesta di contatto verso il/i
--     proprietari, risolta SEMPRE lato server -- l'identità del proprietario
--     non va mai esposta al richiedente (punto 6), a meno che il proprietario
--     stesso scelga di rivelarsi rispondendo alla richiesta.
--   - Le righe già esistenti in euring_2020_canonical (test del 24/07/2026,
--     precedenti a questa migrazione) non hanno un proprietario reale
--     tracciato: vengono attribuite all'account 'admin' (reale, garantito
--     esistere) con un flag dedicato che le mantiene isolabili come gruppo e
--     "disponibili a ricevere" un proprietario reale in futuro, se mai
--     identificato (decisione 30/07/2026).
--   - Il consenso all'uso aggregato/anonimo dei dati (punti 16-17, per i
--     contatori Lizzy sotto) vive nel modello User / data/auth/users.json
--     (file JSON, non Postgres) -- NON in questa migrazione. Il codice che
--     popola i contatori deve verificare quel consenso in Python prima di
--     incrementare, passando la lista di username consenzienti come parametro
--     alla query SQL (niente join diretto Postgres<->JSON).

BEGIN;

-- ============================================================================
-- 1. Alias del numero di anello (punto 11)
-- ============================================================================

CREATE TABLE IF NOT EXISTS ring_alias (
    alias_id BIGSERIAL PRIMARY KEY,
    ringing_scheme TEXT NOT NULL,
    identification_number TEXT NOT NULL,

    UNIQUE (ringing_scheme, identification_number)
);

COMMENT ON TABLE ring_alias IS
    'Alias stabile e non derivabile (BIGSERIAL, non hash/HMAC) per la coppia (ringing_scheme, identification_number), cioe'' per l''anello fisico. Calcolato per OGNI record archiviato indipendentemente dalla sua visibilita''. Stesso pattern del NEXTVALID storico di EPE, e dello stesso meccanismo gia'' in uso da ISPRA nel LOD pubblico (vedi epe_organism_*.nt.gz, verificato 30/07/2026).';

-- ============================================================================
-- 2. Proprieta'/visibilita' sui record dell'archivio canonico
-- ============================================================================

ALTER TABLE euring_2020_canonical
    ADD COLUMN IF NOT EXISTS owner_username TEXT,
    ADD COLUMN IF NOT EXISTS owner_is_placeholder BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS visibility TEXT NOT NULL DEFAULT 'private',
    ADD COLUMN IF NOT EXISTS alias_id BIGINT REFERENCES ring_alias(alias_id);

-- ADD CONSTRAINT non supporta IF NOT EXISTS in PostgreSQL (a differenza di
-- ADD COLUMN/DROP CONSTRAINT) -- pattern idiomatico per renderlo idempotente:
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'chk_euring_2020_canonical_visibility'
    ) THEN
        ALTER TABLE euring_2020_canonical
            ADD CONSTRAINT chk_euring_2020_canonical_visibility
            CHECK (visibility IN ('public', 'private', 'shared'));
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_euring_2020_canonical_owner
    ON euring_2020_canonical(owner_username);
CREATE INDEX IF NOT EXISTS idx_euring_2020_canonical_alias
    ON euring_2020_canonical(alias_id);

-- Backfill: righe pre-esistenti alla feature (es. id=1 del test del 24/07/2026)
-- non hanno un proprietario reale tracciato. Attribuite ad 'admin' (account
-- reale, garantito esistere, mai eliminabile in quanto unico super_admin di
-- bootstrap -- vedi auth_service.py) con flag owner_is_placeholder=true, cosi'
-- da restare un gruppo isolabile e riattribuibile in futuro senza toccare
-- eventuali sottomissioni reali dell'account admin stesso.
UPDATE euring_2020_canonical
SET owner_username = 'admin',
    owner_is_placeholder = true,
    visibility = 'private'
WHERE owner_username IS NULL;

-- NOTA: questo backfill NON popola alias_id per le righe pre-esistenti.
-- Richiede di estrarre 'ringing scheme'/'identification number' da
-- euring_2020_field_values (o da parsed_fields) e fare upsert su ring_alias
-- per ciascuna riga -- logica non banale da esprimere in puro SQL, va fatta
-- con un piccolo script Python una tantum dopo il deploy di questa
-- migrazione. Finche' non viene eseguito, alias_id resta NULL sulle righe
-- gia' archiviate prima di oggi (impatto noto: quelle righe non parteciperanno
-- al conteggio "eventi totali per alias" finche' non vengono backfillate).

COMMENT ON COLUMN euring_2020_canonical.owner_username IS
    'Username di chi ha sottomesso il record (da current_user al momento dell''archiviazione). NULL solo transitoriamente prima del backfill.';
COMMENT ON COLUMN euring_2020_canonical.owner_is_placeholder IS
    'true per le righe attribuite retroattivamente a un proprietario fittizio (admin) perche'' precedenti a questa feature -- NON per sottomissioni reali dell''account admin. Permette di isolare il gruppo e di riattribuirlo in futuro se il vero proprietario viene identificato.';
COMMENT ON COLUMN euring_2020_canonical.visibility IS
    'Livello di visibilita'' del record: public (tutti), private (solo owner_username), shared (solo utenti in euring_2020_shared_with). Default private.';
COMMENT ON COLUMN euring_2020_canonical.alias_id IS
    'Alias dell''anello (ring_alias), popolato al primo inserimento per (ringing_scheme, identification_number) di questo record, indipendentemente dalla visibilita''.';

-- ============================================================================
-- 3. Condivisione esplicita (lista di utenti) -- punto 7
-- ============================================================================

CREATE TABLE IF NOT EXISTS euring_2020_shared_with (
    canonical_id INTEGER NOT NULL REFERENCES euring_2020_canonical(id) ON DELETE CASCADE,
    shared_with_username TEXT NOT NULL,

    PRIMARY KEY (canonical_id, shared_with_username)
);

COMMENT ON TABLE euring_2020_shared_with IS
    'Lista esplicita di utenti con cui un record a visibility=shared e'' condiviso. Popolata sia manualmente (l''owner condivide) sia automaticamente quando una ricattura coinvolge 2+ utenti diversi sullo stesso alias_id (punto 7).';

-- ============================================================================
-- 4. Richieste di contatto verso il proprietario di un record nascosto
--    (punto 9-10, esteso il 30/07/2026 su richiesta di Davide)
-- ============================================================================

CREATE TABLE IF NOT EXISTS contact_requests (
    id SERIAL PRIMARY KEY,
    alias_id BIGINT NOT NULL REFERENCES ring_alias(alias_id),
    requester_username TEXT NOT NULL,
    owner_username TEXT NOT NULL,
    message TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    shared BOOLEAN,
    identity_revealed BOOLEAN,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    responded_at TIMESTAMPTZ,

    CONSTRAINT chk_contact_requests_status CHECK (status IN ('pending', 'responded'))
);

CREATE INDEX IF NOT EXISTS idx_contact_requests_owner ON contact_requests(owner_username, status);
CREATE INDEX IF NOT EXISTS idx_contact_requests_requester ON contact_requests(requester_username);
CREATE INDEX IF NOT EXISTS idx_contact_requests_alias ON contact_requests(alias_id);

COMMENT ON TABLE contact_requests IS
    'Richieste di contatto verso il proprietario di eventi non visibili per un dato alias (placeholder "N eventi non condivisi con te"). owner_username e'' risolto e usato SOLO lato server (notifica email via email_service) -- non va mai restituito al richiedente in nessuna risposta API.';
COMMENT ON COLUMN contact_requests.shared IS
    'Decisione indipendente 1: il proprietario ha scelto di condividere il record col richiedente (aggiungendolo a euring_2020_shared_with)? NULL finche'' status=pending.';
COMMENT ON COLUMN contact_requests.identity_revealed IS
    'Decisione indipendente 2: il proprietario ha scelto di rivelare la propria identita'' al richiedente? Indipendente da "shared" -- si puo'' condividere il dato restando anonimi, o viceversa.';

-- ============================================================================
-- 5. Contatori aggregati e anonimi per la conoscenza semantica di Lizzy
--    (punto 14-15) -- ambito deciso il 30/07/2026: SOLO le due analisi
--    confermate fattibili con gli attributi presenti nel LOD RDF ISPRA
--    (verificato 30/07/2026 su epe_observation_2001.nt/epe_organism_2001.nt):
--      (a) plausibilita' specie+luogo+mese -- FATTIBILE, tabella sotto.
--      (b) coerenza eta'/anno tra eventi dello stesso anello -- ESCLUSA: il
--          campo eta' non e' pubblicato nel LOD RDF ISPRA (verificato, nessun
--          predicato equivalente in epe_observation/epe_organism). Nessuna
--          tabella creata per questa analisi.
--      (c) coerenza geografica/temporale tra eventi consecutivi dello stesso
--          anello -- FATTIBILE, ma NESSUNA nuova tabella: si calcola on-demand
--          da euring_2020_canonical + euring_2020_field_values (campi 'date',
--          'latitude', 'longitude'), raggruppando per alias_id e ordinando
--          cronologicamente. Scelta deliberata: e'' un confronto tra eventi
--          del singolo individuo (via alias), non una statistica di
--          popolazione -- non ha senso pre-aggregarlo in una tabella a parte.
--          Il filtro di consenso (vedi sotto) si applica comunque a livello
--          di query, non di schema.
-- ============================================================================

CREATE TABLE IF NOT EXISTS lizzy_species_place_month_stats (
    species_code TEXT NOT NULL,        -- da 'species concluded' (fallback 'species mentioned' se assente)
    place_code TEXT NOT NULL,          -- da 'current place code' (luogo DELL'EVENTO, non del solo inanellamento originale)
    month SMALLINT NOT NULL,
    occurrence_count INTEGER NOT NULL DEFAULT 0,

    PRIMARY KEY (species_code, place_code, month),
    CONSTRAINT chk_lizzy_species_place_month_stats_month CHECK (month BETWEEN 1 AND 12),
    CONSTRAINT positive_occurrence_count_lizzy CHECK (occurrence_count >= 0)
);

COMMENT ON TABLE lizzy_species_place_month_stats IS
    'Contatore aggregato e anonimo (nessun riferimento a canonical_id, utente, o stringa) specie+luogo+mese, base statistica per i controlli di plausibilita'' di Lizzy (punto 14a). Incrementato dal codice applicativo SOLO per record il cui owner_username ha consents_to_aggregate_analysis=true in data/auth/users.json (verifica fatta in Python, non via join SQL -- il consenso non vive in Postgres). Nessuna soglia di "sufficienza dati" codificata qui: la trasparenza sulla provenienza (quanti schemi/quante osservazioni) va calcolata e dichiarata a runtime da chi consuma questa tabella (decisione 30/07/2026, vedi HANDOFF.md).';
COMMENT ON COLUMN lizzy_species_place_month_stats.place_code IS
    'Deliberatamente "current place code" (luogo di QUESTO evento specifico) e non "place code" (luogo di inanellamento originale) -- per una ricattura le due cose differiscono, e la domanda di Lizzy ("questa specie e'' mai stata segnalata in questo luogo in questo periodo?") riguarda il luogo dell''evento corrente.';

COMMIT;
