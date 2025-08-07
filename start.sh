#!/bin/bash

# Render deployment startup script for DocQuery Streamlit app

# Set default port if not provided by Render
PORT=${PORT:-8501}

# Set Streamlit configuration environment variables
export STREAMLIT_SERVER_PORT=$PORT
export STREAMLIT_SERVER_ADDRESS="0.0.0.0"
export STREAMLIT_SERVER_HEADLESS="true"
export STREAMLIT_BROWSER_GATHER_USAGE_STATS="false"
export STREAMLIT_SERVER_ENABLE_CORS="false"
export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION="false"

# Set Python optimization flags for production
export PYTHONUNBUFFERED=1
export PYTHONOPTIMIZE=1

# Start the Streamlit application with additional flags for Render
echo "Starting DocQuery Streamlit app on port $PORT..."
exec streamlit run app.py \
  --server.port $PORT \
  --server.address 0.0.0.0 \
  --server.headless true \
  --server.enableCORS false \
  --server.enableXsrfProtection false \
  --logger.level error