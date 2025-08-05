#!/bin/bash

# DocQuery API Production Startup Script
# This script starts the DocQuery API server with production settings

echo "🚀 Starting DocQuery API Server..."

# Set default values
PORT=${PORT:-8000}
HOST=${HOST:-0.0.0.0}
WORKERS=${WORKERS:-4}
LOG_LEVEL=${LOG_LEVEL:-info}

# Check if requirements are installed
echo "🔍 Checking dependencies..."
python -c "import fastapi, uvicorn, streamlit" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing required dependencies. Installing..."
    pip install -r requirements.txt
fi

# Check optional dependencies and warn if missing
echo "🔍 Checking optional dependencies..."
python -c "import sentence_transformers, faiss, docx" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Some optional dependencies missing. Install for full functionality:"
    echo "   pip install sentence-transformers faiss-cpu python-docx"
    echo "   Current setup will use fallback search methods."
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Function to start the server
start_server() {
    echo "🌟 Starting DocQuery API..."
    echo "   Host: $HOST"
    echo "   Port: $PORT"
    echo "   Workers: $WORKERS"
    echo "   Log Level: $LOG_LEVEL"
    echo ""
    echo "📚 API Documentation will be available at: http://$HOST:$PORT/docs"
    echo "💚 Health Check: http://$HOST:$PORT/health"
    echo "📊 Status: http://$HOST:$PORT/api/v1/status"
    echo ""
    
    # Start with uvicorn
    if [ "$WORKERS" -eq 1 ]; then
        # Single worker for development
        exec uvicorn api:app \
            --host "$HOST" \
            --port "$PORT" \
            --log-level "$LOG_LEVEL" \
            --access-log \
            --reload
    else
        # Multiple workers for production
        exec uvicorn api:app \
            --host "$HOST" \
            --port "$PORT" \
            --workers "$WORKERS" \
            --log-level "$LOG_LEVEL" \
            --access-log
    fi
}

# Function to run tests
run_tests() {
    echo "🧪 Running API tests..."
    
    # Start server in background for testing
    uvicorn api:app --host 127.0.0.1 --port 8001 &
    SERVER_PID=$!
    
    # Wait for server to start
    sleep 5
    
    # Run tests
    python -c "
import httpx
import asyncio

async def test():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get('http://127.0.0.1:8001/health')
            if response.status_code == 200:
                print('✅ Server is healthy')
                return True
            else:
                print('❌ Server health check failed')
                return False
    except Exception as e:
        print(f'❌ Connection failed: {e}')
        return False

result = asyncio.run(test())
exit(0 if result else 1)
"
    TEST_RESULT=$?
    
    # Stop test server
    kill $SERVER_PID 2>/dev/null
    
    if [ $TEST_RESULT -eq 0 ]; then
        echo "✅ Tests passed!"
        return 0
    else
        echo "❌ Tests failed!"
        return 1
    fi
}

# Function to show help
show_help() {
    echo "DocQuery API Startup Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start     Start the API server (default)"
    echo "  test      Run API tests"
    echo "  help      Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  PORT      Server port (default: 8000)"
    echo "  HOST      Server host (default: 0.0.0.0)" 
    echo "  WORKERS   Number of workers (default: 4)"
    echo "  LOG_LEVEL Log level (default: info)"
    echo ""
    echo "Examples:"
    echo "  $0                          # Start with defaults"
    echo "  PORT=8080 $0               # Start on port 8080"
    echo "  WORKERS=1 $0               # Start with 1 worker (dev mode)"
    echo "  $0 test                    # Run tests"
    echo ""
}

# Main script logic
case "${1:-start}" in
    start)
        start_server
        ;;
    test)
        run_tests
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac