"""
Database service for ECES Analytics
PostgreSQL integration with connection pooling
"""
import asyncio
import asyncpg
import json
import hashlib
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from pathlib import Path
import os

from ..auth.models import User

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service per gestione database PostgreSQL analytics"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.db_url = self._get_database_url()
        self.is_enabled = os.getenv("ENABLE_DATABASE_LOGGING", "false").lower() == "true"
        
    def _get_database_url(self) -> str:
        """Costruisce URL database da variabili ambiente"""
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        database = os.getenv("DB_NAME", "eces_analytics")
        user = os.getenv("DB_USER", "eces_user")
        password = os.getenv("DB_PASSWORD", "eces_password")
        ssl_mode = os.getenv("PGSSLMODE", "prefer")
        
        # Costruisci URL con parametri SSL
        url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        if ssl_mode == "disable":
            url += "?sslmode=disable"
        
        return url
    
    async def initialize(self):
        """Inizializza connection pool PostgreSQL"""
        if not self.is_enabled:
            logger.info("Database logging disabled")
            return
            
        try:
            self.pool = await asyncpg.create_pool(
                self.db_url,
                min_size=2,
                max_size=10,
                command_timeout=60,
                server_settings={
                    'application_name': 'eces_analytics',
                    'timezone': 'UTC'
                }
            )
            logger.info("Database connection pool initialized")
            
            # Test connessione
            async with self.pool.acquire() as conn:
                version = await conn.fetchval("SELECT version()")
                logger.info(f"Connected to PostgreSQL: {version}")
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            self.pool = None
    
    async def close(self):
        """Chiude connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    async def log_user_query(self, user: User, query_data: Dict[str, Any]) -> bool:
        """
        Registra query utente nel database
        
        Args:
            user: Utente che ha fatto la query
            query_data: Dati della query (tipo, stringa, risultato, etc.)
            
        Returns:
            bool: True se salvato con successo
        """
        if not self.pool or not self.is_enabled:
            return False
            
        try:
            async with self.pool.acquire() as conn:
                # Inserisci nella tabella user_queries
                await conn.execute("""
                    INSERT INTO user_queries (
                        user_id, username, user_role, query_type, input_string,
                        ip_address, user_agent, session_id, result_status,
                        result_data, processing_time_ms, euring_version_detected,
                        confidence_score
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                """, 
                    user.id,
                    user.username,
                    user.role.value,
                    query_data['query_type'],
                    query_data['input_string'],
                    query_data.get('ip_address'),
                    query_data.get('user_agent'),
                    query_data.get('session_id'),
                    query_data['result_status'],
                    json.dumps(query_data['result_data']) if query_data.get('result_data') else None,
                    query_data.get('processing_time_ms', 0),
                    query_data.get('euring_version_detected'),
                    query_data.get('confidence_score')
                )
                
                # Aggiorna o inserisci nella tabella unique_strings
                await self._update_unique_strings(conn, query_data)
                
                logger.debug(f"Logged query for user {user.username}: {query_data['query_type']}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to log user query: {e}")
            return False
    
    async def get_usage_statistics(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Genera statistiche d'uso per periodo specificato
        
        Args:
            start_date: Data inizio periodo
            end_date: Data fine periodo
            
        Returns:
            Dict con statistiche complete
        """
        if not self.pool:
            return {}
            
        try:
            async with self.pool.acquire() as conn:
                # Statistiche generali
                stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_queries,
                        COUNT(DISTINCT user_id) as unique_users,
                        COUNT(DISTINCT input_string) as unique_strings,
                        ROUND(AVG(processing_time_ms), 2) as avg_processing_time,
                        ROUND(
                            COUNT(*) FILTER (WHERE result_status = 'success') * 100.0 / COUNT(*), 
                            2
                        ) as success_rate,
                        MIN(timestamp) as first_query,
                        MAX(timestamp) as last_query
                    FROM user_queries 
                    WHERE date_only BETWEEN $1 AND $2
                """, start_date, end_date)
                
                # Top stringhe più testate
                top_strings = await conn.fetch("""
                    SELECT 
                        us.original_string,
                        us.total_queries,
                        us.successful_queries,
                        ROUND(us.successful_queries * 100.0 / us.total_queries, 2) as success_rate,
                        us.most_common_version,
                        us.string_length
                    FROM unique_strings us
                    WHERE us.string_hash IN (
                        SELECT DISTINCT encode(sha256(input_string::bytea), 'hex')
                        FROM user_queries 
                        WHERE date_only BETWEEN $1 AND $2
                    )
                    ORDER BY us.total_queries DESC 
                    LIMIT 10
                """, start_date, end_date)
                
                # Distribuzione versioni EURING
                version_dist = await conn.fetch("""
                    SELECT 
                        COALESCE(euring_version_detected, 'Unknown') as version,
                        COUNT(*) as count,
                        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
                    FROM user_queries 
                    WHERE date_only BETWEEN $1 AND $2
                    GROUP BY euring_version_detected
                    ORDER BY count DESC
                """, start_date, end_date)
                
                # Utenti più attivi
                top_users = await conn.fetch("""
                    SELECT 
                        username,
                        COUNT(*) as query_count,
                        COUNT(DISTINCT input_string) as unique_strings_tested,
                        ROUND(AVG(processing_time_ms), 2) as avg_processing_time,
                        MAX(timestamp) as last_activity
                    FROM user_queries 
                    WHERE date_only BETWEEN $1 AND $2
                    GROUP BY user_id, username
                    ORDER BY query_count DESC
                    LIMIT 10
                """, start_date, end_date)
                
                # Trend giornaliero
                daily_trend = await conn.fetch("""
                    SELECT 
                        date_only,
                        COUNT(*) as queries,
                        COUNT(DISTINCT user_id) as active_users,
                        ROUND(AVG(processing_time_ms), 2) as avg_time
                    FROM user_queries 
                    WHERE date_only BETWEEN $1 AND $2
                    GROUP BY date_only
                    ORDER BY date_only
                """, start_date, end_date)
                
                return {
                    "period": {
                        "start": start_date.isoformat(),
                        "end": end_date.isoformat(),
                        "days": (end_date - start_date).days + 1
                    },
                    "summary": dict(stats) if stats else {},
                    "top_strings": [dict(row) for row in top_strings],
                    "version_distribution": [dict(row) for row in version_dist],
                    "top_users": [dict(row) for row in top_users],
                    "daily_trend": [dict(row) for row in daily_trend]
                }
                
        except Exception as e:
            logger.error(f"Failed to get usage statistics: {e}")
            return {}
    
    async def export_research_dataset(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Esporta dataset anonimizzato per ricerca scientifica
        
        Args:
            filters: Filtri per export (date, versioni, etc.)
            
        Returns:
            Lista di record anonimizzati
        """
        if not self.pool:
            return []
            
        try:
            start_date = filters.get('start_date', date.today() - timedelta(days=30))
            end_date = filters.get('end_date', date.today())
            min_confidence = filters.get('min_confidence', 0.0)
            
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        input_string,
                        euring_version_detected,
                        confidence_score,
                        result_status,
                        processing_time_ms,
                        date_only,
                        EXTRACT(HOUR FROM timestamp) as hour_of_day,
                        input_length,
                        (result_data->>'field_count')::integer as field_count
                    FROM user_queries
                    WHERE date_only BETWEEN $1 AND $2
                        AND result_status = 'success'
                        AND (confidence_score IS NULL OR confidence_score >= $3)
                    ORDER BY timestamp
                """, start_date, end_date, min_confidence)
                
                # Anonimizza e restituisce
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to export research dataset: {e}")
            return []
    
    async def get_string_analytics(self, string_hash: str) -> Dict[str, Any]:
        """
        Ottieni analytics dettagliate per una stringa specifica
        
        Args:
            string_hash: Hash SHA256 della stringa
            
        Returns:
            Dict con analytics della stringa
        """
        if not self.pool:
            return {}
            
        try:
            async with self.pool.acquire() as conn:
                # Info stringa
                string_info = await conn.fetchrow("""
                    SELECT * FROM unique_strings WHERE string_hash = $1
                """, string_hash)
                
                if not string_info:
                    return {}
                
                # Cronologia test
                test_history = await conn.fetch("""
                    SELECT 
                        timestamp,
                        username,
                        result_status,
                        euring_version_detected,
                        confidence_score,
                        processing_time_ms
                    FROM user_queries 
                    WHERE encode(sha256(input_string::bytea), 'hex') = $1
                    ORDER BY timestamp DESC
                    LIMIT 50
                """, string_hash)
                
                return {
                    "string_info": dict(string_info),
                    "test_history": [dict(row) for row in test_history]
                }
                
        except Exception as e:
            logger.error(f"Failed to get string analytics: {e}")
            return {}
    
    async def update_daily_statistics(self, target_date: Optional[date] = None):
        """
        Aggiorna statistiche giornaliere pre-calcolate
        
        Args:
            target_date: Data per cui calcolare statistiche (default: oggi)
        """
        if not self.pool:
            return
            
        if target_date is None:
            target_date = date.today()
            
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("SELECT update_daily_statistics($1)", target_date)
                logger.info(f"Updated daily statistics for {target_date}")
                
        except Exception as e:
            logger.error(f"Failed to update daily statistics: {e}")
    
    async def cleanup_old_data(self, retention_days: int = 365) -> int:
        """
        Pulisce dati vecchi secondo retention policy
        
        Args:
            retention_days: Giorni di retention (default: 365)
            
        Returns:
            Numero di record eliminati
        """
        if not self.pool:
            return 0
            
        try:
            async with self.pool.acquire() as conn:
                deleted_count = await conn.fetchval(
                    "SELECT cleanup_old_data($1)", retention_days
                )
                logger.info(f"Cleaned up {deleted_count} old records")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return 0

    async def _update_unique_strings(self, conn, query_data: Dict[str, Any]):
        """
        Aggiorna la tabella unique_strings per tracciare stringhe duplicate
        
        Args:
            conn: Connessione database attiva
            query_data: Dati della query
        """
        input_string = query_data['input_string']
        string_hash = hashlib.sha256(input_string.encode()).hexdigest()
        is_successful = query_data['result_status'] == 'success'
        euring_version = query_data.get('euring_version_detected')
        
        # Usa UPSERT (INSERT ... ON CONFLICT) per gestire duplicati
        await conn.execute("""
            INSERT INTO unique_strings (
                string_hash, original_string, string_length, 
                total_queries, successful_queries, most_common_version,
                first_seen, last_seen
            ) VALUES (
                $1, $2, $3, 1, $4, $5, NOW(), NOW()
            )
            ON CONFLICT (string_hash) DO UPDATE SET
                total_queries = unique_strings.total_queries + 1,
                successful_queries = unique_strings.successful_queries + $4,
                last_seen = NOW(),
                most_common_version = CASE 
                    WHEN $5 IS NOT NULL THEN $5 
                    ELSE unique_strings.most_common_version 
                END
        """, 
            string_hash,
            input_string,
            len(input_string),
            1 if is_successful else 0,
            euring_version
        )

# Istanza globale del servizio
database_service = DatabaseService()