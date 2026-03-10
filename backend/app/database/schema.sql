-- ECES Analytics Database Schema
-- PostgreSQL 14+ compatible

-- Database: eces_analytics
-- CREATE DATABASE eces_analytics;

-- Tabella principale query utenti
CREATE TABLE IF NOT EXISTS user_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(50) NOT NULL,
    username VARCHAR(100) NOT NULL,
    user_role VARCHAR(20) NOT NULL,
    query_type VARCHAR(20) NOT NULL, -- 'recognition', 'conversion', 'validation'
    input_string TEXT NOT NULL,
    input_length INTEGER,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    date_only DATE,
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(100),
    
    -- Risultati
    result_status VARCHAR(20) NOT NULL, -- 'success', 'error', 'partial'
    result_data JSONB,
    processing_time_ms INTEGER,
    euring_version_detected VARCHAR(10),
    confidence_score DECIMAL(5,4),
    
    -- Metadati
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_query_type CHECK (query_type IN ('recognition', 'conversion', 'validation')),
    CONSTRAINT valid_status CHECK (result_status IN ('success', 'error', 'partial')),
    CONSTRAINT valid_processing_time CHECK (processing_time_ms >= 0)
);

-- Tabella stringhe uniche (deduplicazione e statistiche)
CREATE TABLE IF NOT EXISTS unique_strings (
    id SERIAL PRIMARY KEY,
    string_hash VARCHAR(64) UNIQUE NOT NULL, -- SHA256 della stringa
    original_string TEXT NOT NULL,
    first_seen TIMESTAMPTZ DEFAULT NOW(),
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    total_queries INTEGER DEFAULT 1,
    successful_queries INTEGER DEFAULT 0,
    most_common_version VARCHAR(10),
    string_length INTEGER,
    
    CONSTRAINT positive_queries CHECK (total_queries >= 0),
    CONSTRAINT valid_success_count CHECK (successful_queries <= total_queries)
);

-- Tabella statistiche giornaliere (pre-calcolate per performance)
CREATE TABLE IF NOT EXISTS daily_statistics (
    date DATE PRIMARY KEY,
    total_queries INTEGER DEFAULT 0,
    unique_users INTEGER DEFAULT 0,
    unique_strings INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0,
    avg_processing_time DECIMAL(8,2) DEFAULT 0,
    most_active_user VARCHAR(100),
    most_tested_string TEXT,
    version_distribution JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabella sessioni utente (per analytics avanzate)
CREATE TABLE IF NOT EXISTS user_sessions (
    session_id VARCHAR(100) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    username VARCHAR(100) NOT NULL,
    start_time TIMESTAMPTZ DEFAULT NOW(),
    end_time TIMESTAMPTZ,
    ip_address INET,
    user_agent TEXT,
    total_queries INTEGER DEFAULT 0,
    successful_queries INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

-- Indici per performance ottimale
CREATE INDEX IF NOT EXISTS idx_user_queries_timestamp ON user_queries(timestamp);
CREATE INDEX IF NOT EXISTS idx_user_queries_user_id ON user_queries(user_id);
CREATE INDEX IF NOT EXISTS idx_user_queries_date ON user_queries(date_only);
CREATE INDEX IF NOT EXISTS idx_user_queries_string_hash ON user_queries(md5(input_string));
CREATE INDEX IF NOT EXISTS idx_user_queries_version ON user_queries(euring_version_detected);
CREATE INDEX IF NOT EXISTS idx_user_queries_status ON user_queries(result_status);
CREATE INDEX IF NOT EXISTS idx_user_queries_session ON user_queries(session_id);

-- Indice GIN per ricerca full-text nelle stringhe
CREATE INDEX IF NOT EXISTS idx_user_queries_string_search 
ON user_queries USING gin(to_tsvector('english', input_string));

-- Indice GIN per query JSON sui risultati
CREATE INDEX IF NOT EXISTS idx_user_queries_result_data 
ON user_queries USING gin(result_data);

-- Indici per unique_strings
CREATE INDEX IF NOT EXISTS idx_unique_strings_hash ON unique_strings(string_hash);
CREATE INDEX IF NOT EXISTS idx_unique_strings_length ON unique_strings(string_length);
CREATE INDEX IF NOT EXISTS idx_unique_strings_queries ON unique_strings(total_queries DESC);

-- Indici per daily_statistics
CREATE INDEX IF NOT EXISTS idx_daily_statistics_date ON daily_statistics(date DESC);

-- Indici per user_sessions
CREATE INDEX IF NOT EXISTS idx_user_sessions_user ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON user_sessions(is_active, start_time);

-- Funzione per aggiornare statistiche giornaliere
CREATE OR REPLACE FUNCTION update_daily_statistics(target_date DATE DEFAULT CURRENT_DATE)
RETURNS VOID AS $$
BEGIN
    INSERT INTO daily_statistics (
        date, total_queries, unique_users, unique_strings, 
        success_rate, avg_processing_time, most_active_user, most_tested_string
    )
    SELECT 
        target_date,
        COUNT(*) as total_queries,
        COUNT(DISTINCT user_id) as unique_users,
        COUNT(DISTINCT input_string) as unique_strings,
        ROUND(
            COUNT(*) FILTER (WHERE result_status = 'success') * 100.0 / COUNT(*), 
            2
        ) as success_rate,
        ROUND(AVG(processing_time_ms), 2) as avg_processing_time,
        (SELECT user_id FROM user_queries 
         WHERE date_only = target_date 
         GROUP BY user_id 
         ORDER BY COUNT(*) DESC 
         LIMIT 1) as most_active_user,
        (SELECT input_string FROM user_queries 
         WHERE date_only = target_date 
         GROUP BY input_string 
         ORDER BY COUNT(*) DESC 
         LIMIT 1) as most_tested_string
    FROM user_queries 
    WHERE date_only = target_date
    ON CONFLICT (date) DO UPDATE SET
        total_queries = EXCLUDED.total_queries,
        unique_users = EXCLUDED.unique_users,
        unique_strings = EXCLUDED.unique_strings,
        success_rate = EXCLUDED.success_rate,
        avg_processing_time = EXCLUDED.avg_processing_time,
        most_active_user = EXCLUDED.most_active_user,
        most_tested_string = EXCLUDED.most_tested_string,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- Trigger per aggiornare unique_strings automaticamente
CREATE OR REPLACE FUNCTION update_unique_strings_trigger()
RETURNS TRIGGER AS $$
BEGIN
    -- Calcola valori derivati
    NEW.input_length := length(NEW.input_string);
    NEW.date_only := NEW.timestamp::date;
    
    INSERT INTO unique_strings (string_hash, original_string, most_common_version, string_length)
    VALUES (
        encode(sha256(NEW.input_string::bytea), 'hex'),
        NEW.input_string,
        NEW.euring_version_detected,
        length(NEW.input_string)
    )
    ON CONFLICT (string_hash) DO UPDATE SET
        last_seen = NOW(),
        total_queries = unique_strings.total_queries + 1,
        successful_queries = CASE 
            WHEN NEW.result_status = 'success' 
            THEN unique_strings.successful_queries + 1
            ELSE unique_strings.successful_queries
        END,
        most_common_version = COALESCE(NEW.euring_version_detected, unique_strings.most_common_version);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger per calcolare string_length in unique_strings
CREATE OR REPLACE FUNCTION calculate_string_length_trigger()
RETURNS TRIGGER AS $$
BEGIN
    NEW.string_length := length(NEW.original_string);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_calculate_string_length ON unique_strings;
CREATE TRIGGER trigger_calculate_string_length
    BEFORE INSERT OR UPDATE ON unique_strings
    FOR EACH ROW
    EXECUTE FUNCTION calculate_string_length_trigger();

-- Applica trigger
DROP TRIGGER IF EXISTS trigger_update_unique_strings ON user_queries;
CREATE TRIGGER trigger_update_unique_strings
    AFTER INSERT ON user_queries
    FOR EACH ROW
    EXECUTE FUNCTION update_unique_strings_trigger();

-- Funzione per pulizia automatica (retention policy)
CREATE OR REPLACE FUNCTION cleanup_old_data(retention_days INTEGER DEFAULT 365)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM user_queries 
    WHERE timestamp < NOW() - INTERVAL '1 day' * retention_days;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Pulisci anche unique_strings orfane
    DELETE FROM unique_strings 
    WHERE string_hash NOT IN (
        SELECT DISTINCT encode(sha256(input_string::bytea), 'hex') 
        FROM user_queries
    );
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Commenti per documentazione
COMMENT ON TABLE user_queries IS 'Log completo di tutte le query utenti ECES';
COMMENT ON TABLE unique_strings IS 'Statistiche deduplicate per stringa unica';
COMMENT ON TABLE daily_statistics IS 'Statistiche giornaliere pre-calcolate';
COMMENT ON TABLE user_sessions IS 'Sessioni utente per analytics comportamentali';

COMMENT ON COLUMN user_queries.input_string IS 'Stringa EURING testata dall''utente';
COMMENT ON COLUMN user_queries.result_data IS 'Risultato completo in formato JSON';
COMMENT ON COLUMN user_queries.processing_time_ms IS 'Tempo elaborazione in millisecondi';
COMMENT ON COLUMN user_queries.confidence_score IS 'Punteggio confidenza riconoscimento (0-1)';