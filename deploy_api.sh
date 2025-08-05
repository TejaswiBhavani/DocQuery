#!/bin/bash
# Deployment script for DocQuery - Start FastAPI REST API

set -e

echo "🚀 Starting DocQuery API Deployment"
echo "==================================="

# Set environment variables for deployment
export PORT=${PORT:-8000}
export HOST=${HOST:-0.0.0.0}
export WORKERS=${WORKERS:-1}

# Check if required dependencies are installed
echo "📦 Checking dependencies..."
python -c "import fastapi, uvicorn, PyPDF2, numpy, sklearn, openai, sqlalchemy, psycopg2" || {
    echo "❌ Missing dependencies. Installing..."
    pip install -r requirements.txt
}

echo "✅ Dependencies check complete"

# Check system status
echo "🔍 Checking system status..."
python dependency_checker.py

# Start the API server
echo "🌐 Starting FastAPI server on $HOST:$PORT with $WORKERS workers"
exec uvicorn api:app --host $HOST --port $PORT --workers $WORKERS