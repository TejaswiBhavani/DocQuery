#!/bin/bash
# Vercel startup script for Streamlit

# Get port from environment variable (default 8501)
PORT=${PORT:-8501}

# Start Streamlit with proper configuration
streamlit run app.py \
  --server.port=$PORT \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --browser.gatherUsageStats=false \
  --server.enableCORS=false