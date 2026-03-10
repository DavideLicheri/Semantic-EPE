"""
ECES Database Schema Module
Handles database initialization for both SQLite (local) and PostgreSQL (production)
"""

import sqlite3
import os
from pathlib import Path

def create_tables():
    """
    Create database tables for local SQLite development
    Adapted from PostgreSQL schema for SQLite compatibility
    """
    
    # Get database path
    db_path = Path(__file__).parent.parent.parent / "eces_local.db"
    
    # SQLite-compatible schema (adapted from PostgreSQL)
    sqlite_schema = """
    -- ECES Analytics Database Schema (SQLite version)
    
    -- Tabella principale query utenti
    CREATE TABLE IF NOT EXISTS user_queries (
        id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
        user_id TEXT NOT NULL,
        username TEXT NOT NULL,
        user_role TEXT NOT NULL,
        query_type TEXT NOT NULL CHECK (query_type IN ('recognition', 'conversion', 'validation')),
        input_string TEXT NOT NULL,
        input_length INTEGER,
        timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        date_only DATE,
        ip_address TEXT,
        user_agent TEXT,
        session_id TEXT,
        
        -- Risultati
        result_status TEXT NOT NULL CHECK (result_status IN ('success', 'error', 'partial')),
        result_data TEXT, -- JSON as TEXT in SQLite
        processing_time_ms INTEGER CHECK (processing_time_ms >= 0),
        euring_version_detected TEXT,
        confidence_score REAL,
        
        -- Metadati
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Tabella stringhe uniche (deduplicazione e statistiche)
    CREATE TABLE IF NOT EXISTS unique_strings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        string_hash TEXT UNIQUE NOT NULL,
        original_string TEXT NOT NULL,
        first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
        total_queries INTEGER DEFAULT 1 CHECK (total_queries >= 0),
        successful_queries INTEGER DEFAULT 0 CHECK (successful_queries <= total_queries),
        most_common_version TEXT,
        string_length INTEGER
    );
    
    -- Tabella statistiche giornaliere (pre-calcolate per performance)
    CREATE TABLE IF NOT EXISTS daily_statistics (
        date DATE PRIMARY KEY,
        total_queries INTEGER DEFAULT 0,
        unique_users INTEGER DEFAULT 0,
        unique_strings INTEGER DEFAULT 0,
        success_rate REAL DEFAULT 0,
        avg_processing_time REAL DEFAULT 0,
        most_active_user TEXT,
        most_tested_string TEXT,
        version_distribution TEXT, -- JSON as TEXT
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Tabella sessioni utente (per analytics avanzate)
    CREATE TABLE IF NOT EXISTS user_sessions (
        session_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        username TEXT NOT NULL,
        start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        end_time DATETIME,
        ip_address TEXT,
        user_agent TEXT,
        total_queries INTEGER DEFAULT 0,
        successful_queries INTEGER DEFAULT 0,
        is_active BOOLEAN DEFAULT 1
    );
    
    -- Indici per performance ottimale
    CREATE INDEX IF NOT EXISTS idx_user_queries_timestamp ON user_queries(timestamp);
    CREATE INDEX IF NOT EXISTS idx_user_queries_user_id ON user_queries(user_id);
    CREATE INDEX IF NOT EXISTS idx_user_queries_date ON user_queries(date_only);
    CREATE INDEX IF NOT EXISTS idx_user_queries_version ON user_queries(euring_version_detected);
    CREATE INDEX IF NOT EXISTS idx_user_queries_status ON user_queries(result_status);
    CREATE INDEX IF NOT EXISTS idx_user_queries_session ON user_queries(session_id);
    
    -- Indici per unique_strings
    CREATE INDEX IF NOT EXISTS idx_unique_strings_hash ON unique_strings(string_hash);
    CREATE INDEX IF NOT EXISTS idx_unique_strings_length ON unique_strings(string_length);
    CREATE INDEX IF NOT EXISTS idx_unique_strings_queries ON unique_strings(total_queries DESC);
    
    -- Indici per daily_statistics
    CREATE INDEX IF NOT EXISTS idx_daily_statistics_date ON daily_statistics(date DESC);
    
    -- Indici per user_sessions
    CREATE INDEX IF NOT EXISTS idx_user_sessions_user ON user_sessions(user_id);
    CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON user_sessions(is_active, start_time);
    """
    
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Execute schema
        cursor.executescript(sqlite_schema)
        
        # Create triggers for SQLite (simplified versions)
        trigger_sql = """
        -- Trigger per aggiornare campi derivati
        CREATE TRIGGER IF NOT EXISTS trigger_update_derived_fields
        AFTER INSERT ON user_queries
        BEGIN
            UPDATE user_queries 
            SET 
                input_length = length(NEW.input_string),
                date_only = date(NEW.timestamp)
            WHERE id = NEW.id;
            
            -- Aggiorna unique_strings
            INSERT OR REPLACE INTO unique_strings (
                string_hash, original_string, most_common_version, 
                string_length, total_queries, successful_queries,
                first_seen, last_seen
            )
            VALUES (
                lower(hex(NEW.input_string)),
                NEW.input_string,
                NEW.euring_version_detected,
                length(NEW.input_string),
                COALESCE((SELECT total_queries FROM unique_strings WHERE string_hash = lower(hex(NEW.input_string))), 0) + 1,
                COALESCE((SELECT successful_queries FROM unique_strings WHERE string_hash = lower(hex(NEW.input_string))), 0) + 
                    CASE WHEN NEW.result_status = 'success' THEN 1 ELSE 0 END,
                COALESCE((SELECT first_seen FROM unique_strings WHERE string_hash = lower(hex(NEW.input_string))), CURRENT_TIMESTAMP),
                CURRENT_TIMESTAMP
            );
        END;
        """
        
        cursor.executescript(trigger_sql)
        
        # Insert some sample data for testing
        sample_data = """
        -- Sample admin user session
        INSERT OR IGNORE INTO user_sessions (
            session_id, user_id, username, start_time, total_queries, is_active
        ) VALUES (
            'dev_session_001', 'admin', 'admin', CURRENT_TIMESTAMP, 0, 1
        );
        
        -- Sample query for testing
        INSERT OR IGNORE INTO user_queries (
            user_id, username, user_role, query_type, input_string,
            result_status, euring_version_detected, processing_time_ms,
            confidence_score, session_id
        ) VALUES (
            'admin', 'admin', 'super_admin', 'recognition', 
            'TEST EURING STRING FOR DEVELOPMENT',
            'success', '2000', 150, 0.95, 'dev_session_001'
        );
        """
        
        cursor.executescript(sample_data)
        
        conn.commit()
        conn.close()
        
        print(f"✅ SQLite database created successfully at: {db_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def reset_database():
    """Reset the local database by deleting and recreating it"""
    db_path = Path(__file__).parent.parent.parent / "eces_local.db"
    
    if db_path.exists():
        os.remove(db_path)
        print("🗑️ Existing database deleted")
    
    return create_tables()

if __name__ == "__main__":
    print("🗄️ Initializing ECES local database...")
    success = create_tables()
    if success:
        print("🎉 Database initialization complete!")
    else:
        print("❌ Database initialization failed!")