"""
Local Database service for ECES Analytics
SQLite integration for local development
"""
import sqlite3
import json
import hashlib
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from pathlib import Path
import os

from ..auth.models import User

logger = logging.getLogger(__name__)

class LocalDatabaseService:
    """Service per gestione database SQLite locale"""
    
    def __init__(self):
        self.db_path = Path(__file__).parent.parent.parent / "eces_local.db"
        self.is_enabled = True  # Always enabled for local development
        
    def get_connection(self):
        """Get SQLite connection"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    
    async def initialize(self):
        """Initialize SQLite database (no-op for local)"""
        logger.info("Local SQLite database ready")
        return True
    
    async def close(self):
        """Close database (no-op for SQLite)"""
        logger.info("Local database service closed")
    
    async def log_user_query(self, user: User, query_data: Dict[str, Any]) -> bool:
        """
        Log user query to SQLite database
        
        Args:
            user: User who made the query
            query_data: Query data (type, string, result, etc.)
            
        Returns:
            bool: True if saved successfully
        """
        if not self.is_enabled:
            return False
            
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Insert into user_queries table
            cursor.execute("""
                INSERT INTO user_queries (
                    user_id, username, user_role, query_type, input_string,
                    ip_address, user_agent, session_id, result_status,
                    result_data, processing_time_ms, euring_version_detected,
                    confidence_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
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
            ))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Logged query for user {user.username}: {query_data['query_type']}")
            return True
                
        except Exception as e:
            logger.error(f"Failed to log user query: {e}")
            return False
    
    async def get_usage_statistics(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Generate usage statistics for specified period
        
        Args:
            start_date: Period start date
            end_date: Period end date
            
        Returns:
            Dict with complete statistics
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # General statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_queries,
                    COUNT(DISTINCT user_id) as unique_users,
                    COUNT(DISTINCT input_string) as unique_strings,
                    ROUND(AVG(processing_time_ms), 2) as avg_processing_time,
                    ROUND(
                        CAST(SUM(CASE WHEN result_status = 'success' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(*), 
                        2
                    ) as success_rate,
                    MIN(timestamp) as first_query,
                    MAX(timestamp) as last_query
                FROM user_queries 
                WHERE date(timestamp) BETWEEN ? AND ?
            """, (start_date.isoformat(), end_date.isoformat()))
            
            stats_row = cursor.fetchone()
            stats = dict(stats_row) if stats_row else {}
            
            # Top tested strings
            cursor.execute("""
                SELECT 
                    us.original_string,
                    us.total_queries,
                    us.successful_queries,
                    ROUND(CAST(us.successful_queries AS FLOAT) * 100.0 / us.total_queries, 2) as success_rate,
                    us.most_common_version,
                    us.string_length
                FROM unique_strings us
                WHERE us.string_hash IN (
                    SELECT DISTINCT lower(hex(input_string))
                    FROM user_queries 
                    WHERE date(timestamp) BETWEEN ? AND ?
                )
                ORDER BY us.total_queries DESC 
                LIMIT 10
            """, (start_date.isoformat(), end_date.isoformat()))
            
            top_strings = [dict(row) for row in cursor.fetchall()]
            
            # EURING version distribution
            cursor.execute("""
                SELECT 
                    COALESCE(euring_version_detected, 'Unknown') as version,
                    COUNT(*) as count,
                    ROUND(CAST(COUNT(*) AS FLOAT) * 100.0 / (SELECT COUNT(*) FROM user_queries WHERE date(timestamp) BETWEEN ? AND ?), 2) as percentage
                FROM user_queries 
                WHERE date(timestamp) BETWEEN ? AND ?
                GROUP BY euring_version_detected
                ORDER BY count DESC
            """, (start_date.isoformat(), end_date.isoformat(), start_date.isoformat(), end_date.isoformat()))
            
            version_dist = [dict(row) for row in cursor.fetchall()]
            
            # Most active users
            cursor.execute("""
                SELECT 
                    username,
                    COUNT(*) as query_count,
                    COUNT(DISTINCT input_string) as unique_strings_tested,
                    ROUND(AVG(processing_time_ms), 2) as avg_processing_time,
                    MAX(timestamp) as last_activity
                FROM user_queries 
                WHERE date(timestamp) BETWEEN ? AND ?
                GROUP BY user_id, username
                ORDER BY query_count DESC
                LIMIT 10
            """, (start_date.isoformat(), end_date.isoformat()))
            
            top_users = [dict(row) for row in cursor.fetchall()]
            
            # Daily trend
            cursor.execute("""
                SELECT 
                    date(timestamp) as date_only,
                    COUNT(*) as queries,
                    COUNT(DISTINCT user_id) as active_users,
                    ROUND(AVG(processing_time_ms), 2) as avg_time
                FROM user_queries 
                WHERE date(timestamp) BETWEEN ? AND ?
                GROUP BY date(timestamp)
                ORDER BY date(timestamp)
            """, (start_date.isoformat(), end_date.isoformat()))
            
            daily_trend = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            return {
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "days": (end_date - start_date).days + 1
                },
                "summary": stats,
                "top_strings": top_strings,
                "version_distribution": version_dist,
                "top_users": top_users,
                "daily_trend": daily_trend
            }
                
        except Exception as e:
            logger.error(f"Failed to get usage statistics: {e}")
            return {}
    
    async def export_research_dataset(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Export anonymized dataset for scientific research
        
        Args:
            filters: Export filters (dates, versions, etc.)
            
        Returns:
            List of anonymized records
        """
        try:
            start_date = filters.get('start_date', date.today() - timedelta(days=30))
            end_date = filters.get('end_date', date.today())
            min_confidence = filters.get('min_confidence', 0.0)
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    input_string,
                    euring_version_detected,
                    confidence_score,
                    result_status,
                    processing_time_ms,
                    date(timestamp) as date_only,
                    CAST(strftime('%H', timestamp) AS INTEGER) as hour_of_day,
                    input_length
                FROM user_queries
                WHERE date(timestamp) BETWEEN ? AND ?
                    AND result_status = 'success'
                    AND (confidence_score IS NULL OR confidence_score >= ?)
                ORDER BY timestamp
            """, (start_date.isoformat(), end_date.isoformat(), min_confidence))
            
            rows = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return rows
                
        except Exception as e:
            logger.error(f"Failed to export research dataset: {e}")
            return []
    
    async def get_string_analytics(self, string_hash: str) -> Dict[str, Any]:
        """
        Get detailed analytics for a specific string
        
        Args:
            string_hash: SHA256 hash of the string
            
        Returns:
            Dict with string analytics
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # String info
            cursor.execute("SELECT * FROM unique_strings WHERE string_hash = ?", (string_hash,))
            string_info_row = cursor.fetchone()
            
            if not string_info_row:
                conn.close()
                return {}
            
            string_info = dict(string_info_row)
            
            # Test history
            cursor.execute("""
                SELECT 
                    timestamp,
                    username,
                    result_status,
                    euring_version_detected,
                    confidence_score,
                    processing_time_ms
                FROM user_queries 
                WHERE lower(hex(input_string)) = ?
                ORDER BY timestamp DESC
                LIMIT 50
            """, (string_hash,))
            
            test_history = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return {
                "string_info": string_info,
                "test_history": test_history
            }
                
        except Exception as e:
            logger.error(f"Failed to get string analytics: {e}")
            return {}
    
    async def update_daily_statistics(self, target_date: Optional[date] = None):
        """
        Update pre-calculated daily statistics
        
        Args:
            target_date: Date to calculate statistics for (default: today)
        """
        if target_date is None:
            target_date = date.today()
            
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Calculate daily statistics
            cursor.execute("""
                INSERT OR REPLACE INTO daily_statistics (
                    date, total_queries, unique_users, unique_strings, 
                    success_rate, avg_processing_time, most_active_user, most_tested_string
                )
                SELECT 
                    ? as date,
                    COUNT(*) as total_queries,
                    COUNT(DISTINCT user_id) as unique_users,
                    COUNT(DISTINCT input_string) as unique_strings,
                    ROUND(
                        CAST(SUM(CASE WHEN result_status = 'success' THEN 1 ELSE 0 END) AS FLOAT) * 100.0 / COUNT(*), 
                        2
                    ) as success_rate,
                    ROUND(AVG(processing_time_ms), 2) as avg_processing_time,
                    (SELECT user_id FROM user_queries 
                     WHERE date(timestamp) = ? 
                     GROUP BY user_id 
                     ORDER BY COUNT(*) DESC 
                     LIMIT 1) as most_active_user,
                    (SELECT input_string FROM user_queries 
                     WHERE date(timestamp) = ? 
                     GROUP BY input_string 
                     ORDER BY COUNT(*) DESC 
                     LIMIT 1) as most_tested_string
                FROM user_queries 
                WHERE date(timestamp) = ?
            """, (target_date.isoformat(), target_date.isoformat(), target_date.isoformat(), target_date.isoformat()))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Updated daily statistics for {target_date}")
                
        except Exception as e:
            logger.error(f"Failed to update daily statistics: {e}")
    
    async def cleanup_old_data(self, retention_days: int = 365) -> int:
        """
        Clean up old data according to retention policy
        
        Args:
            retention_days: Retention days (default: 365)
            
        Returns:
            Number of deleted records
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cutoff_date = (date.today() - timedelta(days=retention_days)).isoformat()
            
            cursor.execute("DELETE FROM user_queries WHERE date(timestamp) < ?", (cutoff_date,))
            deleted_count = cursor.rowcount
            
            # Clean up orphaned unique_strings
            cursor.execute("""
                DELETE FROM unique_strings 
                WHERE string_hash NOT IN (
                    SELECT DISTINCT lower(hex(input_string)) 
                    FROM user_queries
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up {deleted_count} old records")
            return deleted_count
                
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return 0

# Create instance based on environment
def get_database_service():
    """Get appropriate database service based on environment"""
    if os.getenv("ENVIRONMENT", "development") == "development":
        return LocalDatabaseService()
    else:
        from .database_service import DatabaseService
        return DatabaseService()

# Global instance
database_service = get_database_service()