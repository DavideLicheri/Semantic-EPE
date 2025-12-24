"""
EURING Code Recognition System - Main FastAPI Application
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from app.api.euring_api import router as euring_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 EURING Recognition System starting up...")
    print("📊 Loading EURING version data...")
    print("🔍 Initializing recognition engine...")
    print("🔄 Initializing conversion services...")
    print("✅ System ready!")
    
    yield
    
    # Shutdown
    print("🛑 EURING Recognition System shutting down...")


app = FastAPI(
    title="EURING Code Recognition System",
    description="API for recognizing and converting EURING bird ringing codes between different versions",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],  # React + Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(euring_router)


@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "name": "EURING Code Recognition System",
        "version": "1.0.0",
        "description": "API for recognizing and converting EURING bird ringing codes",
        "endpoints": {
            "recognition": "/api/euring/recognize",
            "conversion": "/api/euring/convert",
            "batch_recognition": "/api/euring/batch/recognize",
            "batch_conversion": "/api/euring/batch/convert",
            "versions": "/api/euring/versions",
            "health": "/api/euring/health",
            "domain_evolution": "/api/euring/domains/{domain}/evolution",
            "domain_comparison": "/api/euring/domains/{domain}/compare/{version1}/{version2}",
            "domain_timeline": "/api/euring/domains/timeline",
            "domain_fields": "/api/euring/domains/{domain}/fields",
            "domain_compatibility": "/api/euring/domains/{domain}/compatibility/{fromVersion}/{toVersion}",
            "domain_export": "/api/euring/domains/export/{domain}",
            "docs": "/docs"
        },
        "supported_versions": ["1966", "1979", "2000", "2020"],
        "semantic_domains": [
            "identification_marking",
            "species", 
            "demographics",
            "temporal",
            "spatial",
            "biometrics",
            "methodology"
        ]
    }


@app.get("/health")
async def health_check():
    """Legacy health check endpoint"""
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "path": str(request.url)
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )