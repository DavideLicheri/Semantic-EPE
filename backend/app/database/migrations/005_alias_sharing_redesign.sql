-- ECES Analytics Database Schema — Migration 005
-- Redesign del meccanismo di condivisione: sostituisce la condivisione
-- automatica introdotta in migrazione 003 con scelte esplicite, per
-- (proprietario, alias), prese dal singolo proprietario.
--
-- Prerequisito: migrazione 003 (ring_alias, euring_2020_canonical.owner_username/
-- visibility/alias_id, euring_2020_shared_with, contact_requests) già applicata.
--
-- Contesto/decisioni (vedi HANDOFF.md, sessioni 03/08/2026 e 07/08/2026 —
-- nessuna scelta qui non discussa con Davide):
--
--   - Trovato (03/08/2026, testando end-to-end la richiesta di contatto) che
--     la condivisione automatica di migrazione 003 scatta SEMPRE nell'istante
--     in cui un secondo proprietario tocca lo stesso alias, rendendo "richiedi
--     contatto" di fatto irraggiungibile in ogni scenario multi-proprietario
--     reale. Decisione: abbandonare la condivisione automatica.
--   - Ogni proprietario decide, per il PROPRIO dato su un anello (non per
--     singola stringa — un proprietario con più righe sullo stesso alias le
--     tratta come blocco unico), tra tre stati: privato (default, invariato),
--     condiviso in modo mirato con un altro proprietario specifico (reciproco
--     per costruzione: efficace solo quando ENTRAMBI scelgono "offered" verso
--     l'altro — nessuna perdita per chi condivide per primo), pubblico
--     (unilaterale, nessuna reciprocità richiesta, riguarda SOLO il proprio
--     dato — non si propaga agli altri proprietari dello stesso alias).
--   - Verificato con un esempio a 3 attori (07/08/2026): due proprietari sullo
--     stesso alias non si vedono a vicenda solo perché sono gli unici due —
--     serve la scelta attiva reciproca. Un terzo proprietario che sceglie
--     "pubblico" non coinvolge gli altri due. Non esiste una visibilità
--     "collettiva" della life history: è sempre calcolata al volo per singolo
--     evento, mai uno stato condiviso che qualcuno può alterare per gli altri.
--   - Comunicazione tra proprietari: un messaggio opzionale, singolo (NON un
--     thread) attaccato alla scelta di condivisione mirata — la maggior parte
--     delle ricatture sono banali (nessun messaggio), alcune (specie rare,
--     eventi anomali) possono valere uno scambio umano. Deciso di restare
--     semplici per ora: un solo messaggio, non una conversazione.
--   - Notifica generica automatica (non ancora implementata lato codice):
--     chi non condivide riceve comunque una notifica al momento
--     dell'inserimento di un evento collegato allo stesso alias — mai il
--     contenuto del dato altrui, solo il fatto che esiste. Trigger da
--     spostare nel codice applicativo (upsert_euring_2020_canonical), non in
--     questa migrazione.
--
-- QUESTA MIGRAZIONE È SOLO ADDITIVA: crea le nuove tabelle ma NON tocca né
-- rimuove euring_2020_canonical.visibility, euring_2020_shared_with, o
-- contact_requests — quelle restano finché il codice applicativo non viene
-- riscritto e testato per usare esclusivamente le nuove tabelle. Rimuoverle
-- prima causerebbe un'interruzione, dato che il codice attuale le legge
-- ancora. La migrazione dei DATI esistenti (righe già 'public'/'shared') va
-- fatta con uno script Python dedicato dopo il deploy di questa migrazione,
-- non qui — richiede decisioni di merge non esprimibili in puro SQL (es. un
-- proprietario con visibilità mista su più righe dello stesso alias deve
-- scegliere UN solo stato per l'intero alias, non è automatico).

BEGIN;

-- ============================================================================
-- 1. Condivisione mirata reciproca, per (alias, coppia di proprietari)
-- ============================================================================

CREATE TABLE IF NOT EXISTS alias_sharing_intent (
    alias_id BIGINT NOT NULL REFERENCES ring_alias(alias_id),
    from_username TEXT NOT NULL,
    to_username TEXT NOT NULL,
    state TEXT NOT NULL,
    message TEXT,
    decided_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (alias_id, from_username, to_username),
    CONSTRAINT chk_alias_sharing_intent_state CHECK (state IN ('offered', 'declined')),
    CONSTRAINT chk_alias_sharing_intent_not_self CHECK (from_username != to_username)
);

CREATE INDEX IF NOT EXISTS idx_alias_sharing_intent_to
    ON alias_sharing_intent(alias_id, to_username);

COMMENT ON TABLE alias_sharing_intent IS
    'Scelta esplicita e direzionale di un proprietario (from_username) di condividere il PROPRIO dato su un alias con un altro proprietario specifico (to_username). Visibilita'' effettiva = riga (A->B, offered) AND riga (B->A, offered) entrambe presenti (reciprocita''). Assenza di riga = non ancora deciso (diverso da state=declined, rifiuto attivo). Aggiornabile in qualunque momento (UPSERT), nessun lock permanente -- un proprietario puo'' sempre cambiare idea. Sostituisce la condivisione automatica di migrazione 003 (vedi commento di testa). Deciso 07/08/2026.';
COMMENT ON COLUMN alias_sharing_intent.message IS
    'Messaggio opzionale, singolo (non un thread/conversazione), visibile alla controparte insieme alla notifica. La maggior parte delle scelte di condivisione non lo useranno (ricatture banali); pensato per i casi che meritano davvero uno scambio (specie rare, eventi anomali). Deciso di restare semplici: un solo messaggio, non una conversazione a più turni.';
COMMENT ON COLUMN alias_sharing_intent.state IS
    'offered = questo proprietario condivide il proprio dato con to_username (efficace solo se reciproco). declined = rifiuto esplicito, distinto dal semplice "non ancora deciso" (nessuna riga).';

-- ============================================================================
-- 2. Visibilita' pubblica, per (alias, proprietario) -- unilaterale
-- ============================================================================

CREATE TABLE IF NOT EXISTS alias_owner_visibility (
    alias_id BIGINT NOT NULL REFERENCES ring_alias(alias_id),
    username TEXT NOT NULL,
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    decided_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (alias_id, username)
);

COMMENT ON TABLE alias_owner_visibility IS
    'Scelta unilaterale di un proprietario di rendere pubblico il PROPRIO dato su un alias -- nessuna reciprocita'' richiesta, non coinvolge gli altri proprietari dello stesso alias (verificato con un esempio a 3 attori il 07/08/2026: un terzo proprietario che sceglie pubblico non rende pubblici gli altri due). Granularita'' per (alias, proprietario), NON per singola stringa: un proprietario con piu'' righe sullo stesso alias le tratta come blocco unico -- non puo'' avere una riga pubblica e una privata sullo stesso alias. Deciso 07/08/2026.';

COMMIT;
