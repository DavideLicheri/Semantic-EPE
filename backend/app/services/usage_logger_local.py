"""
Local Usage Logger Service for ECES
Simplified logging for local development
"""
import json
import time
import uuid
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from fastapi import Request

from ..auth.models import User

logger = logging.getLogger(__name__)

class LocalUsageLogger:
    """
    Simplified logging system for local development:
    1. File logging only (no database sync)
    2. In-memory session stats
    """
    
    def __init__(self):
        self.log_dir = Path("data/usage")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Log files
        self.main_log = self.log_dir / "user_queries.jsonl"
        self.error_log = self.log_dir / "errors.jsonl"
        
        # In-memory session stats
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
        Log user query (simplified for local development)
        
        Args:
            user: User who made the query
            query_type: Query type ('recognition', 'conversion', 'validation')
            input_string: EURING string tested
            result: Processing result
            processing_time: Processing time in ms
            request: HTTP request for metadata
            
        Returns:
            Unique log ID
        """
        log_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        # Extract metadata from request
        request_info = self._extract_request_info(request) if request else {}
        
        # Build log entry
        log_entry = {
            "id": log_id,
            "timestamp": timestamp.isoformat(),
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role.value,
                "department": getattr(user, 'department', 'local')
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
        
        # Write to file immediately
        self._write_to_file(log_entry)
        
        # Update session stats
        self._update_session_stats(user, request_info, result)
        
        logger.debug(f"Logged query {log_id} for user {user.username}")
        return log_id
    
    def _extract_request_info(self, request: Request) -> Dict[str, Any]:
        """Extract information from HTTP request"""
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
        """Write log to JSONL file"""
        try:
            with open(self.main_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False, default=str) + '\n')
        except Exception as e:
            logger.error(f"Failed to write log to file: {e}")
            # Fallback to error log
            self._write_error_log({"error": str(e), "log_entry": log_entry})
    
    def _write_error_log(self, error_data: Dict[str, Any]):
        """Write errors to separate file"""
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
        """Update session statistics in memory"""
        session_id = request_info.get("session_id", "local_session")
        
        if session_id not in self.session_stats:
            self.session_stats[session_id] = {
                "user_id": user.id,
                "username": user.username,
                "start_time": datetime.now(),
                "total_queries": 0,
                "successful_queries": 0,
                "unique_strings": set(),
                "ip_address": request_info.get("client_ip", "127.0.0.1")
            }
        
        stats = self.session_stats[session_id]
        stats["total_queries"] += 1
        stats["last_activity"] = datetime.now()
        
        if result.get("status") == "success":
            stats["successful_queries"] += 1
        
        # Track unique strings per session
        string_hash = hashlib.sha256(result.get("input_string", "").encode()).hexdigest()
        stats["unique_strings"].add(string_hash)
    
    async def get_session_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current session statistics"""
        stats = self.session_stats.get(session_id)
        if not stats:
            return None
            
        # Convert set to list for JSON
        stats_copy = stats.copy()
        stats_copy["unique_strings_count"] = len(stats["unique_strings"])
        del stats_copy["unique_strings"]
        
        return stats_copy
    
    async def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Clean up old sessions from memory"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        expired_sessions = [
            session_id for session_id, stats in self.session_stats.items()
            if stats.get("last_activity", stats["start_time"]) < cutoff_time
        ]
        
        for session_id in expired_sessions:
            del self.session_stats[session_id]
        
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    async def force_sync(self):
        """No-op for local development (no database sync needed)"""
        logger.info("Force sync completed (local development - no database sync)")
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Get log file statistics"""
        try:
            main_log_size = self.main_log.stat().st_size if self.main_log.exists() else 0
            error_log_size = self.error_log.stat().st_size if self.error_log.exists() else 0
            
            # Count lines in files
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
                "pending_logs": 0,  # No pending logs in local development
                "active_sessions": len(self.session_stats)
            }
        except Exception as e:
            logger.error(f"Failed to get log stats: {e}")
            return {}

# Create instance based on environment
def get_usage_logger():
    """Get appropriate usage logger based on environment"""
    import os
    if os.getenv("ENVIRONMENT", "development") == "development":
        return LocalUsageLogger()
    else:
        from .usage_logger import UsageLogger
        return UsageLogger()

# Global instance
usage_logger = get_usage_logger()