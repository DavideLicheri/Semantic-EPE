"""
Simple logging middleware for ECES analytics
"""
import time
import json
import asyncio
from fastapi import Request, FastAPI
import logging

logger = logging.getLogger(__name__)

def add_simple_logging_middleware(app: FastAPI):
    """Add simple logging middleware to FastAPI app"""
    
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        
        # Check if this is a tracked endpoint
        path = request.url.path
        tracked_endpoints = {
            "/api/euring/recognize": "recognition",
            "/api/euring/convert": "conversion", 
            "/api/euring/validate": "validation"
        }
        
        query_type = tracked_endpoints.get(path)
        
        if query_type:
            logger.info(f"Tracking {query_type} request to {path}")
            
            # For now, just log to console - we'll enhance this later
            try:
                # Get user info from headers if available
                auth_header = request.headers.get("authorization", "")
                user_info = "authenticated" if auth_header.startswith("Bearer ") else "anonymous"
                
                logger.info(f"ECES Analytics: {query_type} request from {user_info} user")
                
            except Exception as e:
                logger.error(f"Error in logging middleware: {e}")
        
        # Process the request
        response = await call_next(request)
        
        if query_type:
            processing_time = int((time.time() - start_time) * 1000)
            logger.info(f"ECES Analytics: {query_type} completed in {processing_time}ms")
        
        return response
    
    logger.info("Simple logging middleware added to FastAPI app")