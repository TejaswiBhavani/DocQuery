#!/usr/bin/env python3
"""
Health check endpoint for Render deployment.
This provides a simple HTTP health check endpoint that Render can use
to monitor the health of the deployed Streamlit application.
"""

from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
import os
import sys
import psutil
import time
from datetime import datetime

app = FastAPI(
    title="DocQuery Health Check",
    description="Health monitoring endpoint for DocQuery Streamlit application",
    version="1.0.0"
)

# Track application start time
START_TIME = time.time()

@app.get("/healthz")
def health_check():
    """
    Basic health check endpoint that returns 200 OK.
    This is the endpoint Render will use to check if the service is healthy.
    """
    return Response(status_code=200, content="OK")

@app.get("/health")
def detailed_health():
    """
    Detailed health check with system information.
    Provides more comprehensive health status for debugging.
    """
    try:
        uptime = time.time() - START_TIME
        
        # Get system memory information
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available = memory.available / (1024**3)  # GB
        
        # Get system information
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat() + "Z",
            "uptime_seconds": round(uptime, 2),
            "system": {
                "memory_percent": memory_percent,
                "memory_available_gb": round(memory_available, 2),
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "platform": sys.platform
            },
            "environment": {
                "port": os.getenv("PORT", "8501"),
                "streamlit_port": os.getenv("STREAMLIT_SERVER_PORT", "not_set"),
                "render_service": os.getenv("RENDER_SERVICE_NAME", "not_set")
            },
            "service": {
                "name": "DocQuery",
                "version": "1.0.0",
                "description": "AI-powered document analysis system"
            }
        }
        
        # Check if we're running low on memory (warn if > 85% used)
        if memory_percent > 85:
            health_data["warnings"] = [
                f"High memory usage: {memory_percent:.1f}%"
            ]
        
        return JSONResponse(content=health_data, status_code=200)
        
    except Exception as e:
        return JSONResponse(
            content={
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat() + "Z",
                "error": str(e)
            },
            status_code=503
        )

@app.get("/")
def root():
    """
    Root endpoint that provides information about the service.
    """
    return {
        "service": "DocQuery Health Monitor",
        "status": "running",
        "endpoints": {
            "/healthz": "Basic health check (Render monitoring)",
            "/health": "Detailed health information",
            "/": "Service information"
        },
        "streamlit_app": {
            "description": "Main DocQuery Streamlit application",
            "port": os.getenv("PORT", "8501"),
            "note": "Access the main app at the root URL"
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable
    port = int(os.getenv("PORT", "8501"))
    
    print(f"Starting health check server on port {port}")
    
    # Run the health check server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )