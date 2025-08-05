#!/bin/bash
# Deployment script for DocQuery - Start Streamlit Web Application

set -e

echo "🚀 Starting DocQuery Web Application Deployment"
echo "================================================"

# Set environment variables for deployment
export PORT=${PORT:-8080}
export STREAMLIT_SERVER_PORT=$PORT
export STREAMLIT_SERVER_ADDRESS=${HOST:-0.0.0.0}
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Check if required dependencies are installed
echo "📦 Checking dependencies..."
python -c "import streamlit, PyPDF2, numpy, sklearn, openai, sqlalchemy, psycopg2" || {
    echo "❌ Missing dependencies. Installing..."
    pip install -r requirements.txt
}

echo "✅ Dependencies check complete"

# Check system status
echo "🔍 Checking system status..."
python dependency_checker.py

# Start the application
echo "🌐 Starting Streamlit application on $STREAMLIT_SERVER_ADDRESS:$PORT"
exec streamlit run app.py --server.port $PORT --server.address $STREAMLIT_SERVER_ADDRESS