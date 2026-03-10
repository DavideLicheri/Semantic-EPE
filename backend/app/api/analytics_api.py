"""
Analytics API endpoints for ECES
Fornisce statistiche d'uso e analytics per Super Admin
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import date, datetime, timedelta
from typing import Optional, List
import logging

from ..auth.dependencies import require_super_admin
from ..auth.models import User

# Import appropriate database service based on environment
import os
if os.getenv("DATABASE_URL", "").startswith("postgresql://"):
    from ..services.database_service import database_service
    from ..services.usage_logger import usage_logger
else:
    from ..services.database_service_local import database_service
    from ..services.usage_logger_local import usage_logger

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/usage/summary")
async def get_usage_summary(
    days: int = Query(30, ge=1, le=365, description="Giorni da analizzare"),
    current_user: User = Depends(require_super_admin)
):
    """
    Ottieni riassunto statistiche d'uso
    Solo per Super Admin
    """
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        stats = await database_service.get_usage_statistics(start_date, end_date)
        
        return {
            "success": True,
            "data": stats,
            "generated_at": datetime.now().isoformat(),
            "requested_by": current_user.username
        }
        
    except Exception as e:
        logger.error(f"Failed to get usage summary: {e}")
        raise HTTPException(status_code=500, detail="Errore nel recupero statistiche")

@router.get("/usage/detailed")
async def get_detailed_usage(
    start_date: date = Query(..., description="Data inizio (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Data fine (YYYY-MM-DD)"),
    current_user: User = Depends(require_super_admin)
):
    """
    Ottieni statistiche dettagliate per periodo specifico
    """
    try:
        # Validazione date
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="Data inizio deve essere <= data fine")
        
        if (end_date - start_date).days > 365:
            raise HTTPException(status_code=400, detail="Periodo massimo: 365 giorni")
        
        stats = await database_service.get_usage_statistics(start_date, end_date)
        
        return {
            "success": True,
            "data": stats,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": (end_date - start_date).days + 1
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get detailed usage: {e}")
        raise HTTPException(status_code=500, detail="Errore nel recupero statistiche dettagliate")

@router.get("/strings/popular")
async def get_popular_strings(
    limit: int = Query(20, ge=1, le=100, description="Numero stringhe da restituire"),
    min_queries: int = Query(2, ge=1, description="Minimo numero query per stringa"),
    current_user: User = Depends(require_super_admin)
):
    """
    Ottieni stringhe più testate
    """
    try:
        # Check if we're using PostgreSQL or SQLite
        if hasattr(database_service, 'pool') and database_service.pool:
            # PostgreSQL version
            async with database_service.pool.acquire() as conn:
                popular_strings = await conn.fetch("""
                    SELECT 
                        original_string,
                        total_queries,
                        successful_queries,
                        ROUND(successful_queries * 100.0 / total_queries, 2) as success_rate,
                        most_common_version,
                        string_length,
                        first_seen,
                        last_seen
                    FROM unique_strings
                    WHERE total_queries >= $1
                    ORDER BY total_queries DESC
                    LIMIT $2
                """, min_queries, limit)
                
                return {
                    "success": True,
                    "data": [dict(row) for row in popular_strings],
                    "filters": {
                        "limit": limit,
                        "min_queries": min_queries
                    },
                    "total_found": len(popular_strings)
                }
        else:
            # SQLite version
            conn = database_service.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    original_string,
                    total_queries,
                    successful_queries,
                    ROUND(CAST(successful_queries AS FLOAT) * 100.0 / total_queries, 2) as success_rate,
                    most_common_version,
                    string_length,
                    first_seen,
                    last_seen
                FROM unique_strings
                WHERE total_queries >= ?
                ORDER BY total_queries DESC
                LIMIT ?
            """, (min_queries, limit))
            
            popular_strings = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return {
                "success": True,
                "data": popular_strings,
                "filters": {
                    "limit": limit,
                    "min_queries": min_queries
                },
                "total_found": len(popular_strings)
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get popular strings: {e}")
        raise HTTPException(status_code=500, detail="Errore nel recupero stringhe popolari")

@router.get("/strings/{string_hash}/analytics")
async def get_string_analytics(
    string_hash: str,
    current_user: User = Depends(require_super_admin)
):
    """
    Ottieni analytics dettagliate per stringa specifica
    """
    try:
        analytics = await database_service.get_string_analytics(string_hash)
        
        if not analytics:
            raise HTTPException(status_code=404, detail="Stringa non trovata")
        
        return {
            "success": True,
            "data": analytics,
            "string_hash": string_hash
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get string analytics: {e}")
        raise HTTPException(status_code=500, detail="Errore nel recupero analytics stringa")

@router.get("/export/research")
async def export_research_dataset(
    start_date: Optional[date] = Query(None, description="Data inizio export"),
    end_date: Optional[date] = Query(None, description="Data fine export"),
    min_confidence: float = Query(0.0, ge=0.0, le=1.0, description="Confidenza minima"),
    format: str = Query("json", regex="^(json|csv)$", description="Formato export"),
    current_user: User = Depends(require_super_admin)
):
    """
    Esporta dataset anonimizzato per ricerca scientifica
    """
    try:
        # Default: ultimi 30 giorni
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        filters = {
            "start_date": start_date,
            "end_date": end_date,
            "min_confidence": min_confidence
        }
        
        dataset = await database_service.export_research_dataset(filters)
        
        if format == "csv":
            # Converti in CSV
            import csv
            import io
            
            output = io.StringIO()
            if dataset:
                writer = csv.DictWriter(output, fieldnames=dataset[0].keys())
                writer.writeheader()
                writer.writerows(dataset)
            
            csv_content = output.getvalue()
            
            from fastapi.responses import Response
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=eces_research_dataset_{start_date}_{end_date}.csv"}
            )
        
        return {
            "success": True,
            "data": dataset,
            "metadata": {
                "total_records": len(dataset),
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "filters": filters,
                "anonymized": True,
                "exported_at": datetime.now().isoformat(),
                "exported_by": current_user.username
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to export research dataset: {e}")
        raise HTTPException(status_code=500, detail="Errore nell'export dataset")

@router.get("/sessions/active")
async def get_active_sessions(
    current_user: User = Depends(require_super_admin)
):
    """
    Ottieni statistiche sessioni attive
    """
    try:
        # Get stats from usage logger (works for both PostgreSQL and SQLite)
        log_stats = usage_logger.get_log_stats()
        
        return {
            "success": True,
            "data": {
                "active_sessions": log_stats.get("active_sessions", 0),
                "pending_logs": log_stats.get("pending_logs", 0),
                "log_files": {
                    "main_log": log_stats.get("main_log", {}),
                    "error_log": log_stats.get("error_log", {})
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get active sessions: {e}")
        raise HTTPException(status_code=500, detail="Errore nel recupero sessioni attive")

@router.post("/maintenance/sync")
async def force_database_sync(
    current_user: User = Depends(require_super_admin)
):
    """
    Forza sincronizzazione logs con database
    """
    try:
        await usage_logger.force_sync()
        
        return {
            "success": True,
            "message": "Sincronizzazione locale completata",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to force sync: {e}")
        raise HTTPException(status_code=500, detail="Errore nella sincronizzazione")

@router.post("/maintenance/update-stats")
async def update_daily_statistics(
    target_date: Optional[date] = Query(None, description="Data per cui aggiornare statistiche"),
    current_user: User = Depends(require_super_admin)
):
    """
    Aggiorna statistiche giornaliere pre-calcolate
    """
    try:
        if not target_date:
            target_date = date.today()
        
        await database_service.update_daily_statistics(target_date)
        
        return {
            "success": True,
            "message": f"Statistiche aggiornate per {target_date}",
            "date": target_date.isoformat(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to update daily statistics: {e}")
        raise HTTPException(status_code=500, detail="Errore nell'aggiornamento statistiche")

@router.delete("/maintenance/cleanup")
async def cleanup_old_data(
    retention_days: int = Query(365, ge=30, le=3650, description="Giorni di retention"),
    current_user: User = Depends(require_super_admin)
):
    """
    Pulisce dati vecchi secondo retention policy
    """
    try:
        deleted_count = await database_service.cleanup_old_data(retention_days)
        
        return {
            "success": True,
            "message": f"Pulizia completata: {deleted_count} record eliminati",
            "deleted_records": deleted_count,
            "retention_days": retention_days,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to cleanup old data: {e}")
        raise HTTPException(status_code=500, detail="Errore nella pulizia dati")

@router.get("/health")
async def analytics_health():
    """
    Health check per sistema analytics
    """
    try:
        # Check database type
        if hasattr(database_service, 'pool'):
            # PostgreSQL version
            health_status = {
                "database": {
                    "connected": database_service.pool is not None,
                    "enabled": database_service.is_enabled,
                    "type": "PostgreSQL"
                },
                "logging": {
                    "active": True,
                    "stats": usage_logger.get_log_stats()
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # Test PostgreSQL connection
            if database_service.pool:
                try:
                    async with database_service.pool.acquire() as conn:
                        await conn.fetchval("SELECT 1")
                    health_status["database"]["test_query"] = "OK"
                except Exception as e:
                    health_status["database"]["test_query"] = f"FAILED: {str(e)}"
        else:
            # SQLite version
            health_status = {
                "database": {
                    "connected": True,
                    "enabled": database_service.is_enabled,
                    "type": "SQLite"
                },
                "logging": {
                    "active": True,
                    "stats": usage_logger.get_log_stats()
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # Test SQLite connection
            try:
                conn = database_service.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                conn.close()
                health_status["database"]["test_query"] = "OK"
            except Exception as e:
                health_status["database"]["test_query"] = f"FAILED: {str(e)}"
        
        return {
            "success": True,
            "status": "healthy",
            "data": health_status
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e)
        }