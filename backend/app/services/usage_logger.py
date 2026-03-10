"""
Usage Logger Service for ECES
Hybrid logging: immediate file logging + batch database sync
"""
import json
import time
import uuid
import hashlib
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from fastapi import Request

from ..auth.models import User
from .database_service import database_service

logger = logging.getLogger(__name__)

class UsageLogger:
    """
    Sistema di logging ibrido per ECES:
    1. Log immediato su file JSONL (zero latenza)
    2. Sync asincrono su PostgreSQL (analytics)
    """
    
    def __init__(self):
        self.log_dir = Path("data/usage")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # File di log
        self.main_log = self.log_dir / "user_queries.jsonl"
        self.error_log = self.log_dir / "errors.jsonl"
        
        # Queue per batch processing
        self.pending_logs = []
        self.batch_size = 10
        self.batch_interval = 300  # 5 minuti
        
        # Statistiche in memoria
        self.session_stats = {}
        
    async def log_query(
        self, 
        user: User, 
        query_type: str, 
        input_string: str, 
        result: Dict[str, Any], 
        processing_time: int,
        request: Optional[Request] = None
    ) -> str:
        """
        Log completo di una query utente
        
        Args:
            user: Utente che ha fatto la query
            query_type: Tipo query ('recognition', 'conversion', 'validation')
            input_string: Stringa EURING testata
            result: Risultato dell'elaborazione
            processing_time: Tempo elaborazione in ms
            request: Request HTTP per metadata
            
        Returns:
            ID univoco del log
        """
        log_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        # Estrai metadata dalla request
        request_info = self._extract_request_info(request) if request else {}
        
        # Costruisci entry di log
        log_entry = {
            "id": log_id,
            "timestamp": timestamp.isoformat(),
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role.value,
                "department": user.department
            },
            "query": {
                "type": query_type,
                "input_string": input_string,
                "input_length": len(input_string),
                "string_hash": hashlib.sha256(input_string.encode()).hexdigest()
            },
            "result": {
                "status": result.get("status", "unknown"),
                "data": result,
                "processing_time_ms": processing_time,
                "euring_version_detected": result.get("detected_version"),
                "confidence_score": result.get("confidence")
            },
            "request": request_info,
            "session": {
                "id": request_info.get("session_id"),
                "ip": request_info.get("client_ip"),
                "user_agent": request_info.get("user_agent")
            }
        }
        
        # 1. Log immediato su file (sincrono, veloce)
        self._write_to_file(log_entry)
        
        # 2. Aggiungi alla queue per database (asincrono)
        self.pending_logs.append(log_entry)
        
        # 3. Aggiorna statistiche sessione
        self._update_session_stats(user, request_info, result)
        
        # 4. Batch sync se necessario
        if len(self.pending_logs) >= self.batch_size:
            asyncio.create_task(self._sync_to_database())
        
        logger.debug(f"Logged query {log_id} for user {user.username}")
        return log_id
    
    def _extract_request_info(self, request: Request) -> Dict[str, Any]:
        """Estrae informazioni dalla request HTTP"""
        if not request:
            return {}
            
        return {
            "client_ip": getattr(request.client, 'host', None) if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "session_id": request.headers.get("x-session-id") or request.cookies.get("session_id"),
            "referer": request.headers.get("referer"),
            "method": request.method,
            "url": str(request.url),
            "timestamp": datetime.now().isoformat()
        }
    
    def _write_to_file(self, log_entry: Dict[str, Any]):
        """Scrive log su file JSONL (sincrono, veloce)"""
        try:
            with open(self.main_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False, default=str) + '\n')
        except Exception as e:
            logger.error(f"Failed to write log to file: {e}")
            # Fallback su error log
            self._write_error_log({"error": str(e), "log_entry": log_entry})
    
    def _write_error_log(self, error_data: Dict[str, Any]):
        """Scrive errori su file separato"""
        try:
            error_entry = {
                "timestamp": datetime.now().isoformat(),
                "error_data": error_data
            }
            with open(self.error_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(error_entry, ensure_ascii=False, default=str) + '\n')
        except Exception as e:
            logger.critical(f"Failed to write error log: {e}")
    
    def _update_session_stats(self, user: User, request_info: Dict[str, Any], result: Dict[str, Any]):
        """Aggiorna statistiche di sessione in memoria"""
        session_id = request_info.get("session_id")
        if not session_id:
            return
            
        if session_id not in self.session_stats:
            self.session_stats[session_id] = {
                "user_id": user.id,
                "username": user.username,
                "start_time": datetime.now(),
                "total_queries": 0,
                "successful_queries": 0,
                "unique_strings": set(),
                "ip_address": request_info.get("client_ip")
            }
        
        stats = self.session_stats[session_id]
        stats["total_queries"] += 1
        stats["last_activity"] = datetime.now()
        
        if result.get("status") == "success":
            stats["successful_queries"] += 1
        
        # Traccia stringhe uniche per sessione
        string_hash = hashlib.sha256(result.get("input_string", "").encode()).hexdigest()
        stats["unique_strings"].add(string_hash)
    
    async def _sync_to_database(self):
        """Sincronizza logs pendenti con PostgreSQL"""
        if not self.pending_logs:
            return
            
        logs_to_sync = self.pending_logs.copy()
        self.pending_logs.clear()
        
        for log_entry in logs_to_sync:
            try:
                # Converti formato per database
                db_data = self._convert_to_db_format(log_entry)
                
                # Crea oggetto User temporaneo
                user = type('User', (), {
                    'id': log_entry['user']['id'],
                    'username': log_entry['user']['username'],
                    'role': type('Role', (), {'value': log_entry['user']['role']})()
                })()
                
                # Salva nel database
                await database_service.log_user_query(user, db_data)
                
            except Exception as e:
                logger.error(f"Failed to sync log to database: {e}")
                # Rimetti in coda per retry
                self.pending_logs.append(log_entry)
    
    def _convert_to_db_format(self, log_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Converte formato log per database"""
        return {
            "query_type": log_entry["query"]["type"],
            "input_string": log_entry["query"]["input_string"],
            "result_status": log_entry["result"]["status"],
            "result_data": log_entry["result"]["data"],
            "processing_time_ms": log_entry["result"]["processing_time_ms"],
            "euring_version_detected": log_entry["result"]["euring_version_detected"],
            "confidence_score": log_entry["result"]["confidence_score"],
            "ip_address": log_entry["session"]["ip"],
            "user_agent": log_entry["session"]["user_agent"],
            "session_id": log_entry["session"]["id"]
        }
    
    async def get_session_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Ottieni statistiche di sessione corrente"""
        stats = self.session_stats.get(session_id)
        if not stats:
            return None
            
        # Converti set in lista per JSON
        stats_copy = stats.copy()
        stats_copy["unique_strings_count"] = len(stats["unique_strings"])
        del stats_copy["unique_strings"]
        
        return stats_copy
    
    async def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Pulisce sessioni vecchie dalla memoria"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        expired_sessions = [
            session_id for session_id, stats in self.session_stats.items()
            if stats.get("last_activity", stats["start_time"]) < cutoff_time
        ]
        
        for session_id in expired_sessions:
            del self.session_stats[session_id]
        
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    async def force_sync(self):
        """Forza sincronizzazione di tutti i logs pendenti"""
        if self.pending_logs:
            await self._sync_to_database()
            logger.info("Forced sync of pending logs completed")
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Ottieni statistiche sui log files"""
        try:
            main_log_size = self.main_log.stat().st_size if self.main_log.exists() else 0
            error_log_size = self.error_log.stat().st_size if self.error_log.exists() else 0
            
            # Conta righe nei file
            main_log_lines = 0
            if self.main_log.exists():
                with open(self.main_log, 'r') as f:
                    main_log_lines = sum(1 for _ in f)
            
            return {
                "main_log": {
                    "file": str(self.main_log),
                    "size_bytes": main_log_size,
                    "lines": main_log_lines
                },
                "error_log": {
                    "file": str(self.error_log),
                    "size_bytes": error_log_size
                },
                "pending_logs": len(self.pending_logs),
                "active_sessions": len(self.session_stats)
            }
        except Exception as e:
            logger.error(f"Failed to get log stats: {e}")
            return {}

# Istanza globale del logger
usage_logger = UsageLogger()