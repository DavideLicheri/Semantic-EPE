"""
Database service for ECES Analytics
PostgreSQL integration with connection pooling
"""
import asyncio
import asyncpg
import json
import hashlib
import logging
from typing import Optional, List, Dict, Any, Tuple
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

    async def upsert_euring_2020_canonical(
        self,
        canonical_string: str,
        parsed_fields: Dict[str, Any],
        field_count: int,
        field_positions: Dict[str, int],
        owner_username: Optional[str] = None,
    ) -> Optional[Tuple[int, bool]]:
        """
        Persiste una stringa EURING 2020 gia' parsata "pulita" (64/64 campi)
        nell'archivio canonico a faccette.

        Le righe EAV (euring_2020_field_values) vengono inserite SOLO alla
        prima comparsa di questa stringa esatta (string_hash nuovo): se la
        stringa e' gia' nota, si aggiornano solo last_seen/occurrence_count
        su euring_2020_canonical, i valori di campo non cambiano (la stessa
        stringa produce sempre lo stesso parsing).

        Al primo inserimento vengono anche risolti (HANDOFF.md, punti 6-11,
        migrazione 003):
          - alias_id: upsert su ring_alias per (ringing scheme, identification
            number) estratti da parsed_fields -- calcolato indipendentemente
            dalla visibilita' (punto 10).
          - owner_username / visibility (default 'private').
          - auto-condivisione (punto 7): se per lo stesso alias esistono gia'
            record con un owner_username DIVERSO, sia i record esistenti che
            quello nuovo passano a visibility='shared' e vengono collegati in
            euring_2020_shared_with, in entrambe le direzioni. Un record gia'
            'public' non viene MAI declassato a 'shared' da questa logica.

        Le occorrenze successive della stessa identica stringa NON toccano
        owner_username/visibility/alias_id (gia' fissati al primo inserimento).

        Args:
            canonical_string: stringa EURING 2020 completa (pipe-delimited)
            parsed_fields: {field_name: value} da Euring2020PositionParser
            field_count: numero di segmenti trovati (atteso: 64)
            field_positions: {field_name: position} per popolare l'EAV
            owner_username: chi ha sottomesso questa stringa (None se non
                disponibile -- il record risultera' senza proprietario finche'
                non viene backfillato)

        Returns:
            Tupla (id, is_new) -- is_new=True solo se questa e' la prima volta
            che questa esatta stringa viene archiviata (rilevante per non
            incrementare due volte i contatori aggregati di Lizzy, vedi
            archive_service.py). None se il logging su database e' disabilitato
            o in caso di errore (mai un'eccezione: l'archiviazione non deve mai
            far fallire la richiesta principale).
        """
        if not self.pool or not self.is_enabled:
            return None

        string_hash = hashlib.sha256(canonical_string.encode()).hexdigest()

        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    existing_id = await conn.fetchval(
                        "SELECT id FROM euring_2020_canonical WHERE string_hash = $1",
                        string_hash,
                    )

                    if existing_id is not None:
                        await conn.execute(
                            """
                            UPDATE euring_2020_canonical
                            SET last_seen = NOW(), occurrence_count = occurrence_count + 1
                            WHERE id = $1
                            """,
                            existing_id,
                        )
                        return existing_id, False

                    # --- Nuovo record: risolvi alias + ownership/visibilita' ---
                    alias_id: Optional[int] = None
                    visibility = "private"
                    other_owner_rows: List[Any] = []

                    ringing_scheme = parsed_fields.get("ringing scheme")
                    identification_number = parsed_fields.get("identification number")

                    if ringing_scheme and identification_number:
                        alias_id = await conn.fetchval(
                            """
                            INSERT INTO ring_alias (ringing_scheme, identification_number)
                            VALUES ($1, $2)
                            ON CONFLICT (ringing_scheme, identification_number)
                            DO UPDATE SET ringing_scheme = EXCLUDED.ringing_scheme
                            RETURNING alias_id
                            """,
                            ringing_scheme.strip(),
                            identification_number.strip(),
                        )

                        if owner_username:
                            other_owner_rows = await conn.fetch(
                                """
                                SELECT DISTINCT id, owner_username
                                FROM euring_2020_canonical
                                WHERE alias_id = $1
                                  AND owner_username IS NOT NULL
                                  AND owner_username != $2
                                """,
                                alias_id,
                                owner_username,
                            )
                            if other_owner_rows:
                                visibility = "shared"
                                for row in other_owner_rows:
                                    # Non declassare mai un record gia' pubblico.
                                    await conn.execute(
                                        """
                                        UPDATE euring_2020_canonical
                                        SET visibility = 'shared'
                                        WHERE id = $1 AND visibility != 'public'
                                        """,
                                        row["id"],
                                    )
                                    await conn.execute(
                                        """
                                        INSERT INTO euring_2020_shared_with
                                            (canonical_id, shared_with_username)
                                        VALUES ($1, $2)
                                        ON CONFLICT DO NOTHING
                                        """,
                                        row["id"],
                                        owner_username,
                                    )

                    canonical_id = await conn.fetchval(
                        """
                        INSERT INTO euring_2020_canonical
                            (canonical_string, string_hash, parsed_fields, field_count,
                             owner_username, visibility, alias_id)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        RETURNING id
                        """,
                        canonical_string,
                        string_hash,
                        json.dumps(parsed_fields, ensure_ascii=False),
                        field_count,
                        owner_username,
                        visibility,
                        alias_id,
                    )

                    # Condividi il nuovo record con gli altri proprietari trovati
                    # per lo stesso alias (direzione opposta rispetto a sopra).
                    for row in other_owner_rows:
                        await conn.execute(
                            """
                            INSERT INTO euring_2020_shared_with
                                (canonical_id, shared_with_username)
                            VALUES ($1, $2)
                            ON CONFLICT DO NOTHING
                            """,
                            canonical_id,
                            row["owner_username"],
                        )

                    field_rows = [
                        (canonical_id, field_positions[name], name, value)
                        for name, value in parsed_fields.items()
                        if name in field_positions
                    ]
                    if field_rows:
                        await conn.executemany(
                            """
                            INSERT INTO euring_2020_field_values
                                (canonical_id, field_position, field_name, field_value)
                            VALUES ($1, $2, $3, $4)
                            """,
                            field_rows,
                        )

                    return canonical_id, True

        except Exception as e:
            logger.error(f"Failed to upsert euring_2020_canonical: {e}")
            return None

    async def link_unique_string_to_canonical(self, input_string: str, canonical_id: int) -> None:
        """
        Collega una riga di unique_strings (dedup grezza, qualsiasi versione)
        al record canonico 2020 corrispondente.
        """
        if not self.pool or not self.is_enabled or canonical_id is None:
            return

        string_hash = hashlib.sha256(input_string.encode()).hexdigest()

        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    "UPDATE unique_strings SET canonical_id = $1 WHERE string_hash = $2",
                    canonical_id,
                    string_hash,
                )
        except Exception as e:
            logger.error(f"Failed to link unique_strings to canonical: {e}")

    async def search_canonical_2020(
        self, filters: Dict[str, str], page: int, page_size: int,
        requesting_username: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Ricerca a faccette sull'archivio canonico EURING 2020.

        filters: {field_name: field_value}, un solo valore per campo (AND tra
        campi diversi). Il pattern (field_name, field_value) IN (...) GROUP BY
        canonical_id HAVING COUNT(DISTINCT field_name) = N e' il modo standard
        per esprimere "un canonical_id deve avere una riga EAV corrispondente
        per OGNI filtro" senza self-join multipli.

        requesting_username: se fornito, i risultati sono limitati ai record
        pubblici, propri, o condivisi con questo utente. Se None (utente
        anonimo), SOLO i record pubblici. **Bug di privacy corretto
        30/07/2026**: prima di questa modifica il metodo ignorava del tutto
        owner_username/visibility e restituiva sempre l'intero archivio a
        chiunque, indipendentemente da chi chiamava /archive/search
        (HANDOFF.md, punti 6-11).
        """
        if not self.pool:
            return {"total": 0, "results": []}

        offset = max(0, (page - 1) * page_size)

        try:
            async with self.pool.acquire() as conn:
                pairs = list(filters.items()) if filters else []
                field_params: List[Any] = []
                for name, value in pairs:
                    field_params.extend([name, value])

                if requesting_username:
                    vis_idx = len(field_params) + 1
                    visibility_clause = f"""(
                        c.visibility = 'public'
                        OR c.owner_username = ${vis_idx}
                        OR EXISTS (
                            SELECT 1 FROM euring_2020_shared_with sw
                            WHERE sw.canonical_id = c.id AND sw.shared_with_username = ${vis_idx}
                        )
                    )"""
                    visibility_params = [requesting_username]
                else:
                    visibility_clause = "c.visibility = 'public'"
                    visibility_params = []

                if pairs:
                    placeholders = ", ".join(
                        f"(${i * 2 + 1}, ${i * 2 + 2})" for i in range(len(pairs))
                    )
                    id_subquery = f"""
                        SELECT canonical_id FROM euring_2020_field_values
                        WHERE (field_name, field_value) IN ({placeholders})
                        GROUP BY canonical_id
                        HAVING COUNT(DISTINCT field_name) = {len(pairs)}
                    """
                    where_clause = f"c.id IN ({id_subquery}) AND {visibility_clause}"
                else:
                    where_clause = visibility_clause

                all_params = field_params + visibility_params

                total = await conn.fetchval(
                    f"SELECT COUNT(*) FROM euring_2020_canonical c WHERE {where_clause}",
                    *all_params,
                )
                rows = await conn.fetch(
                    f"""
                    SELECT c.id, c.canonical_string, c.field_count,
                           c.first_seen, c.last_seen, c.occurrence_count,
                           c.visibility, c.alias_id
                    FROM euring_2020_canonical c
                    WHERE {where_clause}
                    ORDER BY c.first_seen DESC
                    LIMIT ${len(all_params) + 1} OFFSET ${len(all_params) + 2}
                    """,
                    *all_params,
                    page_size,
                    offset,
                )

                return {
                    "total": total or 0,
                    "results": [dict(r) for r in rows],
                }
        except Exception as e:
            logger.error(f"Failed to search euring_2020_canonical: {e}")
            return {"total": 0, "results": []}

    async def facet_counts_2020(
        self, field_names: List[str], filters: Dict[str, str],
        requesting_username: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Conteggi per faccetta su un elenco curato di campi (vedi
        ARCHIVE_FACET_FIELDS in euring_api.py). Prima versione: calcolati
        sull'intero archivio VISIBILE a requesting_username (non ricalcolati
        in base ai filtri gia' attivi -- semplificazione nota, una vera
        implementazione "drill down" escluderebbe il filtro sul campo stesso
        quando conta le sue faccette).

        requesting_username: stessa semantica di search_canonical_2020 --
        None = solo record pubblici (bug di privacy corretto 30/07/2026,
        prima i conteggi includevano anche i record privati/condivisi altrui).
        """
        if not self.pool:
            return {}

        if requesting_username:
            visibility_clause = """(
                c.visibility = 'public'
                OR c.owner_username = $2
                OR EXISTS (
                    SELECT 1 FROM euring_2020_shared_with sw
                    WHERE sw.canonical_id = c.id AND sw.shared_with_username = $2
                )
            )"""
        else:
            visibility_clause = "c.visibility = 'public'"

        try:
            async with self.pool.acquire() as conn:
                result: Dict[str, List[Dict[str, Any]]] = {}
                for field_name in field_names:
                    params: List[Any] = [field_name]
                    if requesting_username:
                        params.append(requesting_username)
                    rows = await conn.fetch(
                        f"""
                        SELECT fv.field_value, COUNT(*) as cnt
                        FROM euring_2020_field_values fv
                        JOIN euring_2020_canonical c ON c.id = fv.canonical_id
                        WHERE fv.field_name = $1
                          AND fv.field_value IS NOT NULL AND fv.field_value != ''
                          AND {visibility_clause}
                        GROUP BY fv.field_value
                        ORDER BY cnt DESC
                        LIMIT 20
                        """,
                        *params,
                    )
                    result[field_name] = [
                        {"value": r["field_value"], "count": r["cnt"]} for r in rows
                    ]
                return result
        except Exception as e:
            logger.error(f"Failed to compute facet counts: {e}")
            return {}

    async def increment_lizzy_stats(
        self, species_code: str, place_code: str, pentad: int, ringing_scheme: str
    ) -> None:
        """
        Incrementa (o crea) il contatore aggregato e anonimo per una
        combinazione specie+luogo+pentade+schema (HANDOFF.md, punto 14a,
        migrazione 004). Nessun riferimento a canonical_id/utente/stringa in
        questa tabella -- solo il codice applicativo chiamante (vedi
        archive_service._maybe_increment_lizzy_stats) e' responsabile di
        verificare il consenso PRIMA di chiamare questo metodo.
        """
        if not self.pool or not self.is_enabled:
            return

        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO lizzy_species_place_pentad_stats
                        (species_code, place_code, pentad, ringing_scheme, occurrence_count)
                    VALUES ($1, $2, $3, $4, 1)
                    ON CONFLICT (species_code, place_code, pentad, ringing_scheme)
                    DO UPDATE SET occurrence_count = lizzy_species_place_pentad_stats.occurrence_count + 1
                    """,
                    species_code,
                    place_code,
                    pentad,
                    ringing_scheme,
                )
        except Exception as e:
            logger.error(f"Failed to increment lizzy stats: {e}")

    async def get_lizzy_species_place_pentad_stats(
        self, species_code: str, place_code: str, pentad: int
    ) -> Dict[str, Any]:
        """
        Consultazione per Lizzy (punto 14a): conteggio totale per una
        combinazione specie+luogo+pentade, sommato su tutti gli schemi, PIU'
        il numero di schemi distinti dietro quel conteggio -- la
        "dichiarazione di provenienza" decisa il 30/07/2026 al posto di una
        soglia fissa di "sufficienza" (nessun giudizio di plausibilita' qui:
        solo i numeri grezzi, l'interpretazione resta a chi consuma questo
        dato).
        """
        if not self.pool:
            return {"total_occurrences": 0, "distinct_schemes": 0, "schemes": []}

        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT ringing_scheme, occurrence_count
                    FROM lizzy_species_place_pentad_stats
                    WHERE species_code = $1 AND place_code = $2 AND pentad = $3
                    ORDER BY occurrence_count DESC
                    """,
                    species_code,
                    place_code,
                    pentad,
                )
                total = sum(r["occurrence_count"] for r in rows)
                return {
                    "total_occurrences": total,
                    "distinct_schemes": len(rows),
                    "schemes": [
                        {"ringing_scheme": r["ringing_scheme"], "count": r["occurrence_count"]}
                        for r in rows
                    ],
                }
        except Exception as e:
            logger.error(f"Failed to get lizzy stats: {e}")
            return {"total_occurrences": 0, "distinct_schemes": 0, "schemes": []}

    async def get_visible_events_for_alias(
        self, alias_id: int, requesting_username: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Eventi per un dato alias_id (anello) visibili PER INTERO a
        requesting_username: pubblici, propri, o condivisi con lui.
        requesting_username=None (utente anonimo) -> solo pubblici.

        Coppia con count_all_events_for_alias: la differenza tra i due e' il
        numero da mostrare nel placeholder "N eventi non condivisi con te"
        (HANDOFF.md, punti 9-10).

        Non restituisce mai owner_username grezzo (potrebbe essere di un
        altro utente per i record pubblici/condivisi) -- solo un flag
        `is_own` calcolato, coerente con l'invariante del punto 6.
        """
        if not self.pool:
            return []

        try:
            async with self.pool.acquire() as conn:
                if requesting_username:
                    rows = await conn.fetch(
                        """
                        SELECT c.id, c.canonical_string, c.field_count,
                               (c.owner_username = $2) AS is_own,
                               c.visibility, c.first_seen, c.last_seen, c.occurrence_count
                        FROM euring_2020_canonical c
                        WHERE c.alias_id = $1
                          AND (
                            c.visibility = 'public'
                            OR c.owner_username = $2
                            OR EXISTS (
                                SELECT 1 FROM euring_2020_shared_with sw
                                WHERE sw.canonical_id = c.id
                                  AND sw.shared_with_username = $2
                            )
                          )
                        ORDER BY c.first_seen
                        """,
                        alias_id,
                        requesting_username,
                    )
                else:
                    rows = await conn.fetch(
                        """
                        SELECT c.id, c.canonical_string, c.field_count,
                               false AS is_own,
                               c.visibility, c.first_seen, c.last_seen, c.occurrence_count
                        FROM euring_2020_canonical c
                        WHERE c.alias_id = $1 AND c.visibility = 'public'
                        ORDER BY c.first_seen
                        """,
                        alias_id,
                    )
                return [dict(r) for r in rows]
        except Exception as e:
            logger.error(f"Failed to get visible events for alias {alias_id}: {e}")
            return []

    async def count_all_events_for_alias(self, alias_id: int) -> int:
        """
        Conteggio TOTALE di eventi per un dato alias_id, senza filtro di
        visibilita' e senza restituire alcun contenuto -- il numero grezzo
        da cui sottrarre len(get_visible_events_for_alias(...)) per ottenere
        il conteggio del placeholder "N eventi non condivisi con te".
        """
        if not self.pool:
            return 0

        try:
            async with self.pool.acquire() as conn:
                total = await conn.fetchval(
                    "SELECT COUNT(*) FROM euring_2020_canonical WHERE alias_id = $1",
                    alias_id,
                )
                return total or 0
        except Exception as e:
            logger.error(f"Failed to count events for alias {alias_id}: {e}")
            return 0

    async def get_alias_life_history(
        self, alias_id: int, requesting_username: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Storia di vita di un anello (alias_id) per la UI dell'archivio:
        eventi visibili per intero a requesting_username, alternati -- in
        ordine cronologico per data evento -- a segnaposto anonimizzati
        (anno, nazione, specie) per gli eventi non visibili. Deciso con
        Davide 03/08/2026, indipendente dal redesign del meccanismo di
        condivisione (si applica a "qualunque evento che non vedo per
        intero", a prescindere dal motivo).

        Per gli eventi nascosti si restituiscono SOLO tre informazioni,
        estratte da `parsed_fields` (gia' presente su ogni riga, nessun
        bisogno di toccare la tabella EAV): anno (prime 4 cifre del campo
        'date', formato DDMMYYYY), nazione (primi 2 caratteri del campo
        'place code', che per definizione EURING identificano sempre il
        paese), specie ('species concluded' o 'species mentioned' come
        fallback). Mai numero di anello, mai proprietario, mai altri campi.
        La specie e' inclusa anche nei segnaposto apposta: serve a
        intercettare errori di trascrizione (specie diversa tra eventi
        dello stesso alias fisico e' un segnale di anello letto/trascritto
        male da qualche parte).
        """
        if not self.pool:
            return []

        try:
            async with self.pool.acquire() as conn:
                if requesting_username:
                    rows = await conn.fetch(
                        """
                        SELECT c.id, c.canonical_string, c.field_count,
                               (c.owner_username = $2) AS is_own,
                               c.visibility, c.first_seen, c.last_seen, c.occurrence_count,
                               (
                                 c.visibility = 'public'
                                 OR c.owner_username = $2
                                 OR EXISTS (
                                     SELECT 1 FROM euring_2020_shared_with sw
                                     WHERE sw.canonical_id = c.id
                                       AND sw.shared_with_username = $2
                                 )
                               ) AS is_visible,
                               c.parsed_fields->>'date' AS event_date,
                               c.parsed_fields->>'place code' AS place_code,
                               COALESCE(
                                   c.parsed_fields->>'species concluded',
                                   c.parsed_fields->>'species mentioned'
                               ) AS species_code
                        FROM euring_2020_canonical c
                        WHERE c.alias_id = $1
                        """,
                        alias_id,
                        requesting_username,
                    )
                else:
                    rows = await conn.fetch(
                        """
                        SELECT c.id, c.canonical_string, c.field_count,
                               false AS is_own,
                               c.visibility, c.first_seen, c.last_seen, c.occurrence_count,
                               (c.visibility = 'public') AS is_visible,
                               c.parsed_fields->>'date' AS event_date,
                               c.parsed_fields->>'place code' AS place_code,
                               COALESCE(
                                   c.parsed_fields->>'species concluded',
                                   c.parsed_fields->>'species mentioned'
                               ) AS species_code
                        FROM euring_2020_canonical c
                        WHERE c.alias_id = $1
                        """,
                        alias_id,
                    )

                events = []
                for r in rows:
                    event_date = (r["event_date"] or "").strip()
                    sort_key = None
                    if len(event_date) == 8 and event_date.isdigit():
                        # DDMMYYYY -> YYYYMMDD, per ordinare cronologicamente
                        sort_key = event_date[4:8] + event_date[2:4] + event_date[0:2]

                    if r["is_visible"]:
                        events.append({
                            "kind": "full",
                            "id": r["id"],
                            "canonical_string": r["canonical_string"],
                            "field_count": r["field_count"],
                            "visibility": r["visibility"],
                            "is_own": r["is_own"],
                            "first_seen": r["first_seen"].isoformat() if r["first_seen"] else None,
                            "last_seen": r["last_seen"].isoformat() if r["last_seen"] else None,
                            "occurrence_count": r["occurrence_count"],
                            "sort_key": sort_key,
                        })
                    else:
                        place_code = (r["place_code"] or "").strip()
                        events.append({
                            "kind": "hidden",
                            "year": event_date[4:8] if sort_key else None,
                            "country": place_code[:2] if len(place_code) >= 2 else None,
                            "species_code": r["species_code"],
                            "sort_key": sort_key,
                        })

                events.sort(key=lambda e: (e["sort_key"] is None, e["sort_key"] or ""))
                for e in events:
                    e.pop("sort_key", None)
                return events
        except Exception as e:
            logger.error(f"Failed to get life history for alias {alias_id}: {e}")
            return []

    async def get_hidden_owners_for_alias(
        self, alias_id: int, requesting_username: str
    ) -> List[str]:
        """
        Proprietari DISTINTI dei record per questo alias_id che NON sono
        visibili a requesting_username -- serve solo per instradare
        internamente le richieste di contatto (contact_requests), MAI da
        restituire in una risposta API al richiedente (HANDOFF.md, punto 6:
        l'identita' del proprietario non va mai esposta a chi non e' gia'
        stato autorizzato dal proprietario stesso).
        """
        if not self.pool:
            return []

        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT DISTINCT owner_username
                    FROM euring_2020_canonical c
                    WHERE c.alias_id = $1
                      AND c.owner_username IS NOT NULL
                      AND c.owner_username != $2
                      AND NOT (
                        c.visibility = 'public'
                        OR EXISTS (
                            SELECT 1 FROM euring_2020_shared_with sw
                            WHERE sw.canonical_id = c.id
                              AND sw.shared_with_username = $2
                        )
                      )
                    """,
                    alias_id,
                    requesting_username,
                )
                return [r["owner_username"] for r in rows]
        except Exception as e:
            logger.error(f"Failed to get hidden owners for alias {alias_id}: {e}")
            return []

    async def create_contact_request(
        self, alias_id: int, requester_username: str, owner_username: str,
        message: Optional[str] = None
    ) -> Optional[int]:
        """
        Crea una richiesta di contatto verso owner_username per alias_id, se
        non ne esiste gia' una in stato 'pending' identica (evita spam da
        richieste ripetute). Ritorna l'id della richiesta creata, o None se
        gia' esisteva una pendente identica / errore / servizio disabilitato.
        """
        if not self.pool or not self.is_enabled:
            return None

        try:
            async with self.pool.acquire() as conn:
                existing = await conn.fetchval(
                    """
                    SELECT id FROM contact_requests
                    WHERE alias_id = $1 AND requester_username = $2
                      AND owner_username = $3 AND status = 'pending'
                    """,
                    alias_id, requester_username, owner_username,
                )
                if existing is not None:
                    return None

                return await conn.fetchval(
                    """
                    INSERT INTO contact_requests
                        (alias_id, requester_username, owner_username, message)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id
                    """,
                    alias_id, requester_username, owner_username, message,
                )
        except Exception as e:
            logger.error(f"Failed to create contact request: {e}")
            return None

    async def list_contact_requests_for_owner(self, owner_username: str) -> List[Dict[str, Any]]:
        """Richieste ricevute da owner_username, piu' recenti prima. Include requester_username (visibile all'owner, non e' l'informazione protetta)."""
        if not self.pool:
            return []
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT id, alias_id, requester_username, message, status,
                           shared, identity_revealed, created_at, responded_at
                    FROM contact_requests
                    WHERE owner_username = $1
                    ORDER BY created_at DESC
                    """,
                    owner_username,
                )
                return [dict(r) for r in rows]
        except Exception as e:
            logger.error(f"Failed to list contact requests for owner {owner_username}: {e}")
            return []

    async def list_contact_requests_for_requester(self, requester_username: str) -> List[Dict[str, Any]]:
        """
        Richieste inviate da requester_username. owner_username NON viene mai
        incluso qui (punto 6) -- solo esito (shared/identity_revealed) e stato.
        """
        if not self.pool:
            return []
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT id, alias_id, message, status, shared,
                           identity_revealed, created_at, responded_at
                    FROM contact_requests
                    WHERE requester_username = $1
                    ORDER BY created_at DESC
                    """,
                    requester_username,
                )
                return [dict(r) for r in rows]
        except Exception as e:
            logger.error(f"Failed to list contact requests for requester {requester_username}: {e}")
            return []

    async def respond_to_contact_request(
        self, request_id: int, owner_username: str, shared: bool, identity_revealed: bool
    ) -> Optional[Dict[str, Any]]:
        """
        Applica la risposta del proprietario a una richiesta di contatto.
        Se shared=true, il richiedente viene aggiunto a euring_2020_shared_with
        per TUTTI i record di questo alias_id di proprieta' di owner_username,
        e la loro visibilita' passa a 'shared' se era 'private' (mai declassata
        se gia' 'public'). Verifica che request_id appartenga davvero a
        owner_username prima di applicare qualunque modifica.
        """
        if not self.pool:
            return None

        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    row = await conn.fetchrow(
                        """
                        SELECT id, alias_id, requester_username, owner_username, status
                        FROM contact_requests
                        WHERE id = $1 AND owner_username = $2
                        """,
                        request_id, owner_username,
                    )
                    if row is None:
                        return None

                    await conn.execute(
                        """
                        UPDATE contact_requests
                        SET status = 'responded', shared = $2,
                            identity_revealed = $3, responded_at = NOW()
                        WHERE id = $1
                        """,
                        request_id, shared, identity_revealed,
                    )

                    if shared:
                        canonical_ids = await conn.fetch(
                            """
                            SELECT id FROM euring_2020_canonical
                            WHERE alias_id = $1 AND owner_username = $2
                            """,
                            row["alias_id"], owner_username,
                        )
                        for c in canonical_ids:
                            await conn.execute(
                                """
                                UPDATE euring_2020_canonical
                                SET visibility = 'shared'
                                WHERE id = $1 AND visibility != 'public'
                                """,
                                c["id"],
                            )
                            await conn.execute(
                                """
                                INSERT INTO euring_2020_shared_with
                                    (canonical_id, shared_with_username)
                                VALUES ($1, $2)
                                ON CONFLICT DO NOTHING
                                """,
                                c["id"], row["requester_username"],
                            )

                    return {"id": request_id, "shared": shared, "identity_revealed": identity_revealed}
        except Exception as e:
            logger.error(f"Failed to respond to contact request {request_id}: {e}")
            return None

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