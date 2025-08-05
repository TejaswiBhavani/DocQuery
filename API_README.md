# DocQuery API - LLM-Powered Intelligent Query-Retrieval System

A production-ready FastAPI backend that processes documents and answers questions using advanced AI analysis. Built for insurance, legal, HR, and compliance domains.

## 🎯 Quick Start

### Start the API Server
```bash
# Quick start
uvicorn api:app --host 0.0.0.0 --port 8000

# Or use the startup script
./start_api.sh
```

### Make a Request
```bash
curl -X POST "http://localhost:8000/api/v1/hackrx/run" \
  -H "Authorization: Bearer b22f8e46c05cd2c3006ae987bbc9c24ca023045b4af9b189e5d3fe340b91514c" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://your-blob-url.com/policy.pdf",
    "questions": [
      "What is the grace period for premium payment?",
      "What is the waiting period for pre-existing diseases?"
    ]
  }'
```

## 📋 API Specification

### Authentication
```
Authorization: Bearer b22f8e46c05cd2c3006ae987bbc9c24ca023045b4af9b189e5d3fe340b91514c
```

### Main Endpoint
**POST** `/api/v1/hackrx/run`

**Request Body:**
```json
{
  "documents": "https://blob.url/document.pdf",
  "questions": [
    "Question 1?",
    "Question 2?"
  ]
}
```

**Response:**
```json
{
  "answers": [
    "Answer to question 1...",
    "Answer to question 2..."
  ]
}
```

### Additional Endpoints
- `GET /health` - Health check
- `GET /api/v1/status` - System status and capabilities
- `GET /docs` - Interactive API documentation
- `POST /api/v1/hackrx/run-with-openai` - Enhanced processing with OpenAI

## 🚀 Features

### Document Processing
- ✅ **PDF Documents** - Extract text and analyze content
- ✅ **Word Documents** - Process .docx files
- ✅ **Text Files** - Handle plain text documents
- ✅ **Email Files** - Parse .eml email files
- ✅ **Blob URLs** - Download from Azure/AWS blob storage
- ✅ **Local Files** - Support file:// URLs for testing

### AI Analysis
- ✅ **Local AI Models** - No API key required, runs offline
- ✅ **OpenAI Integration** - Enhanced analysis with GPT models
- ✅ **Semantic Search** - FAISS-based vector search
- ✅ **TF-IDF Fallback** - Robust search with automatic fallback
- ✅ **Batch Processing** - Handle multiple questions efficiently
- ✅ **Domain-Specific** - Optimized for insurance, legal, HR, compliance

### API Features
- ✅ **Bearer Authentication** - Secure API access
- ✅ **Input Validation** - Comprehensive request validation
- ✅ **Error Handling** - Detailed error messages and status codes
- ✅ **CORS Enabled** - Cross-origin resource sharing
- ✅ **Health Checks** - Built-in monitoring endpoints
- ✅ **Auto Documentation** - OpenAPI/Swagger docs

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| Response Time | 0.05-5.0 seconds |
| Max File Size | 100MB |
| Concurrent Questions | Up to 10 per request |
| Supported Formats | PDF, DOCX, TXT, EML |
| Search Methods | 3-tier fallback system |
| Authentication | Bearer token |

## 🧪 Testing

### Run All Tests
```bash
# Test components
python test_full_api.py

# Test live server
python test_live_api.py

# Run demo
python demo_api.py
```

### Test Specific Features
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test status endpoint
curl http://localhost:8000/api/v1/status

# View API documentation
open http://localhost:8000/docs
```

## 🐳 Docker Deployment

### Build and Run
```bash
# Build image
docker build -t docquery-api .

# Run container
docker run -p 8000:8000 docquery-api

# Run with environment variables
docker run -p 8000:8000 -e PORT=8000 -e WORKERS=4 docquery-api
```

### Docker Compose
```yaml
version: '3.8'
services:
  docquery-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PORT=8000
      - WORKERS=4
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 🔧 Configuration

### Environment Variables
```bash
PORT=8000                    # Server port
HOST=0.0.0.0                # Server host
WORKERS=4                   # Number of workers
OPENAI_API_KEY=sk-...       # Optional: OpenAI API key
LOG_LEVEL=info              # Logging level
```

### Production Settings
```bash
# Production startup
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4

# With custom settings
WORKERS=8 PORT=8080 ./start_api.sh
```

## 📚 Documentation

- **Interactive API Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json
- **Deployment Guide**: [API_DEPLOYMENT_GUIDE.md](API_DEPLOYMENT_GUIDE.md)
- **Original Streamlit App**: [app.py](app.py)

## 🔒 Security

- **Authentication**: Bearer token required for all endpoints
- **Input Validation**: Comprehensive request validation
- **File Size Limits**: 100MB maximum file size
- **Temporary Files**: Automatic cleanup after processing
- **No Data Persistence**: Stateless operation for security

## 🛠️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Client App    │───▶│   FastAPI API    │───▶│  Document       │
│                 │    │                  │    │  Processor      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  Batch           │    │  Vector Search  │
                       │  Processor       │    │  (FAISS/TF-IDF) │
                       └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  Local AI        │    │  Output         │
                       │  Analysis        │    │  Formatter      │
                       └──────────────────┘    └─────────────────┘
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python test_full_api.py`
5. Submit a pull request

## 📝 License

This project is part of the DocQuery system for document analysis and query processing.

## 🆘 Support

### Common Issues

1. **Import Errors**: Install optional dependencies
   ```bash
   pip install sentence-transformers faiss-cpu python-docx
   ```

2. **Network Timeouts**: Increase timeout for large files
3. **Memory Issues**: Reduce worker count or file size
4. **Authentication Errors**: Verify bearer token

### Getting Help

- Check the [Deployment Guide](API_DEPLOYMENT_GUIDE.md)
- View logs for detailed error information
- Test with sample documents first
- Use the `/docs` endpoint for API exploration

---

**🤖 Built for intelligent document analysis and query processing**