from fastapi import Request, Response, FastAPI
from fastapi.responses import JSONResponse
import logging
import time
import json
import asyncio
from typing import Callable

from ..services.usage_logger import usage_logger
from ..auth.dependencies import get_current_user_optional

logger = logging.getLogger(__name__)

# Endpoint da tracciare
TRACKED_ENDPOINTS = {
    "/api/euring/recognize": "recognition",
    "/api/euring/convert": "conversion", 
    "/api/euring/validate": "validation"
}

async def log_usage_middleware(request: Request, call_next):
    """
    Middleware FastAPI per logging automatico usage analytics
    """
    start_time = time.time()
    
    # Controlla se è un endpoint da tracciare
    path = request.url.path
    query_type = TRACKED_ENDPOINTS.get(path)
    
    if not query_type:
        # Non è un endpoint da tracciare, passa oltre
        response = await call_next(request)
        return response
    
    # Ottieni utente corrente (se autenticato)
    user = None
    try:
        # Estrai token dall'header Authorization
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # Qui dovremmo decodificare il token, ma per semplicità
            # saltiamo il logging se non riusciamo a ottenere l'utente
            pass
    except Exception:
        pass
    
    # Leggi il body della request per ottenere la stringa EURING
    input_string = None
    try:
        if request.method == "POST":
            # Leggi il body
            body = await request.body()
            if body:
                body_data = json.loads(body.decode())
                input_string = body_data.get("euring_string")
    except Exception as e:
        logger.debug(f"Could not extract input string: {e}")
    
    # Esegui la richiesta
    try:
        response = await call_next(request)
        processing_time = int((time.time() - start_time) * 1000)
        
        # Log solo se abbiamo i dati necessari
        if input_string and user:
            # Leggi la response
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            
            # Parse response
            try:
                result_data = json.loads(response_body.decode())
                result = {
                    "status": "success" if response.status_code == 200 else "error",
                    "data": result_data
                }
            except Exception:
                result = {"status": "error", "message": "Could not parse response"}
            
            # Log asincrono
            asyncio.create_task(usage_logger.log_query(
                user=user,
                query_type=query_type,
                input_string=input_string,
                result=result,
                processing_time=processing_time,
                request=request
            ))
            
            # Ricrea la response con il body
            return Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        
        return response
        
    except Exception as e:
        processing_time = int((time.time() - start_time) * 1000)
        logger.error(f"Request failed: {e}")
        
        # Log errore se abbiamo i dati
        if input_string and user:
            result = {"status": "error", "error": str(e)}
            asyncio.create_task(usage_logger.log_query(
                user=user,
                query_type=query_type,
                input_string=input_string,
                result=result,
                processing_time=processing_time,
                request=request
            ))
        
        raise

def add_usage_logging_middleware(app: FastAPI):
    """Aggiunge middleware di logging all'app FastAPI"""
    app.middleware("http")(log_usage_middleware)
    logger.info("Usage logging middleware added")
            logger.error(f"Failed to log error request: {e}")
    
    async def _get_user_from_request(self, request: Request):
        """Estrae utente dalla request (se autenticato)"""
        try:
            # Simula il processo di autenticazione
            authorization = request.headers.get("Authorization")
            if not authorization or not authorization.startswith("Bearer "):
                return None
            
            # Qui dovresti usare la tua logica di autenticazione
            # Per ora uso un placeholder
            from ..auth.auth_service import AuthService
            auth_service = AuthService()
            
            token = authorization.split(" ")[1]
            token_data = auth_service.verify_token(token)
            user = auth_service.get_user(token_data.username)
            
            return user
            
        except Exception as e:
            logger.debug(f"Could not extract user from request: {e}")
            return None
    
    async def _extract_input_string(self, request: Request) -> str:
        """Estrae stringa input dalla request body"""
        try:
            # Leggi body della request
            body = await request.body()
            if not body:
                return ""
            
            # Parse JSON
            data = json.loads(body.decode('utf-8'))
            
            # Estrai stringa secondo il tipo di endpoint
            if request.url.path == "/api/euring/recognize":
                return data.get("euring_string", "")
            elif request.url.path == "/api/euring/convert":
                return data.get("euring_string", "")
            elif request.url.path == "/api/euring/validate":
                return data.get("euring_string", "")
            
            return ""
            
        except Exception as e:
            logger.debug(f"Could not extract input string: {e}")
            return ""
    
    def _parse_response(self, response_body: bytes, status_code: int) -> dict:
        """Parse response per estrarre risultati"""
        try:
            if status_code >= 400:
                return {
                    "status": "error",
                    "http_status": status_code,
                    "message": "HTTP error response"
                }
            
            if not response_body:
                return {"status": "error", "message": "Empty response"}
            
            # Parse JSON response
            response_data = json.loads(response_body.decode('utf-8'))
            
            # Determina status dal contenuto
            if "error" in response_data:
                status = "error"
            elif response_data.get("success", True):
                status = "success"
            else:
                status = "partial"
            
            return {
                "status": status,
                "data": response_data,
                "detected_version": response_data.get("detected_version"),
                "confidence": response_data.get("confidence_score"),
                "field_count": len(response_data.get("fields", [])) if "fields" in response_data else None
            }
            
        except Exception as e:
            logger.debug(f"Could not parse response: {e}")
            return {
                "status": "error",
                "message": f"Failed to parse response: {str(e)}"
            }

def add_usage_logging_middleware(app):
    """Aggiunge middleware di logging all'app FastAPI"""
    middleware = UsageLoggingMiddleware(app)
    app.middleware("http")(middleware)
    logger.info("Usage logging middleware added")