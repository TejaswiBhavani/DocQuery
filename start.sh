#!/bin/bash

# Render deployment startup script for DocQuery with health check
# This script starts both the health check endpoint and the Streamlit application

# Set default port if not provided by Render
PORT=${PORT:-8501}

# Set Streamlit configuration environment variables
export STREAMLIT_SERVER_PORT=$PORT
export STREAMLIT_SERVER_ADDRESS="0.0.0.0"
export STREAMLIT_SERVER_HEADLESS="true"
export STREAMLIT_BROWSER_GATHER_USAGE_STATS="false"
export STREAMLIT_SERVER_ENABLE_CORS="true"
export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION="false"

# Health check endpoint (for Render monitoring)
echo "Starting DocQuery health check endpoint on port $PORT..."
uvicorn healthz:app --host 0.0.0.0 --port $PORT &
HEALTH_PID=$!

# Give health endpoint time to start
sleep 5

# Start the Streamlit application 
echo "Starting DocQuery Streamlit app on port $PORT..."
exec streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true

# Note: The health endpoint runs in background while Streamlit runs in foreground
# This allows Render to monitor health via /healthz endpoint while serving the main app