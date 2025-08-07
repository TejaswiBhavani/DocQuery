#!/bin/bash

# Render deployment startup script for DocQuery Streamlit app

# Set default port if not provided by Render
PORT=${PORT:-8501}

# Set Streamlit configuration environment variables
export STREAMLIT_SERVER_PORT=$PORT
export STREAMLIT_SERVER_ADDRESS="0.0.0.0"
export STREAMLIT_SERVER_HEADLESS="true"
export STREAMLIT_BROWSER_GATHER_USAGE_STATS="false"
export STREAMLIT_SERVER_ENABLE_CORS="true"

# Start the Streamlit application
echo "Starting DocQuery Streamlit app on port $PORT..."
exec streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true