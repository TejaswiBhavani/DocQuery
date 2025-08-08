#!/usr/bin/env python3
"""
Alternative FastAPI server for DocQuery deployment.
This provides a FastAPI wrapper around Streamlit as suggested in the problem statement.
Use this if the simple Streamlit approach doesn't work on Render.

To use this approach:
1. Update render.yaml startCommand to: uvicorn fastapi_server:app --host 0.0.0.0 --port $PORT
2. Update render.yaml healthCheckPath to: /healthz
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
import os
import subprocess
import threading
import time
import psutil

app = FastAPI(title="DocQuery FastAPI Wrapper", version="1.0.0")

# Global state
streamlit_process = None

def start_streamlit():
    """Start Streamlit server in background"""
    global streamlit_process
    
    port = int(os.getenv('PORT', 8501))
    streamlit_port = port + 1  # Use different port for Streamlit
    
    cmd = [
        'streamlit', 'run', 'app.py',
        '--server.port', str(streamlit_port),
        '--server.address', '0.0.0.0',
        '--server.headless', 'true'
    ]
    
    try:
        streamlit_process = subprocess.Popen(cmd)
        print(f"Started Streamlit on port {streamlit_port}")
        return streamlit_port
    except Exception as e:
        print(f"Failed to start Streamlit: {e}")
        return None

@app.on_event("startup")
async def startup_event():
    """Start Streamlit when FastAPI starts"""
    start_streamlit()
    # Give Streamlit time to start
    time.sleep(5)

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up Streamlit process on shutdown"""
    global streamlit_process
    if streamlit_process:
        streamlit_process.terminate()
        streamlit_process.wait()

@app.get("/", response_class=HTMLResponse)
async def root():
    """Proxy to Streamlit interface"""
    port = int(os.getenv('PORT', 8501)) + 1
    return f"""
    <html>
        <head>
            <title>DocQuery - AI Document Analysis</title>
            <meta http-equiv="refresh" content="0; url=http://localhost:{port}/" />
        </head>
        <body>
            <div style="text-align: center; padding: 2rem; font-family: Arial, sans-serif;">
                <h1>🤖 DocQuery</h1>
                <p>Redirecting to AI Document Analysis interface...</p>
                <p><a href="http://localhost:{port}/" style="color: #0066cc;">Click here if not redirected automatically</a></p>
            </div>
        </body>
    </html>
    """

@app.get("/healthz")
async def health_check():
    """Health check endpoint for Render"""
    return {"status": "ok", "message": "DocQuery FastAPI wrapper is running"}

@app.get("/health")
async def detailed_health():
    """Detailed health check with system information"""
    try:
        memory = psutil.virtual_memory()
        
        # Check if Streamlit process is running
        streamlit_status = "running" if streamlit_process and streamlit_process.poll() is None else "stopped"
        
        health_data = {
            "status": "healthy",
            "service": "DocQuery FastAPI Wrapper",
            "version": "1.0.0",
            "streamlit_process": streamlit_status,
            "memory_percent": memory.percent,
            "memory_available_gb": round(memory.available / (1024**3), 2),
            "port": os.getenv("PORT", "8501")
        }
        
        if memory.percent > 85:
            health_data["warnings"] = [f"High memory usage: {memory.percent:.1f}%"]
        
        return health_data
        
    except Exception as e:
        return JSONResponse(
            content={"status": "unhealthy", "error": str(e)},
            status_code=503
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8501))
    print(f"Starting FastAPI wrapper on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)