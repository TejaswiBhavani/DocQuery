# DocQuery API - Production Deployment Guide

## 🚀 Quick Start

### Start the API Server
```bash
# Basic startup
uvicorn api:app --host 0.0.0.0 --port 8000

# Production startup with workers
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4

# Development with auto-reload
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### Environment Variables
```bash
export PORT=8000
export OPENAI_API_KEY=your_openai_key_here  # Optional
```

## 📋 API Specification

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
```
Authorization: Bearer b22f8e46c05cd2c3006ae987bbc9c24ca023045b4af9b189e5d3fe340b91514c
```

### Main Endpoint
```http
POST /api/v1/hackrx/run
Content-Type: application/json
Authorization: Bearer {token}

{
    "documents": "https://blob.url/document.pdf",
    "questions": [
        "What is the grace period for premium payment?",
        "What is the waiting period for pre-existing diseases?"
    ]
}
```

### Response Format
```json
{
    "answers": [
        "A grace period of thirty days is provided...",
        "There is a waiting period of thirty-six months..."
    ]
}
```

## 🔧 Features

### Document Processing
- ✅ PDF documents
- ✅ DOCX files  
- ✅ Text files
- ✅ Email files (.eml)
- ✅ Blob URL downloads
- ✅ Local file support (for testing)

### AI Analysis
- ✅ Local AI models (no API key required)
- ✅ OpenAI GPT integration (with API key)
- ✅ Enhanced vector search with FAISS
- ✅ TF-IDF fallback search
- ✅ Batch question processing

### API Features
- ✅ Bearer token authentication
- ✅ Comprehensive error handling
- ✅ Request validation
- ✅ Health checks
- ✅ Interactive documentation
- ✅ CORS enabled

## 📊 Performance

- **Response Time**: 0.05-5.0 seconds depending on document size
- **File Size Limit**: 100MB
- **Concurrent Questions**: Up to 10 per request
- **Search Methods**: Advanced → Enhanced → Simple (automatic fallback)

## 🧪 Testing

### Basic Health Check
```bash
curl http://localhost:8000/health
```

### API Status
```bash
curl http://localhost:8000/api/v1/status
```

### Test with Sample Request
```bash
curl -X POST "http://localhost:8000/api/v1/hackrx/run" \
  -H "Authorization: Bearer b22f8e46c05cd2c3006ae987bbc9c24ca023045b4af9b189e5d3fe340b91514c" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "file:///path/to/your/document.pdf",
    "questions": ["What is covered under this policy?"]
  }'
```

### Run Test Scripts
```bash
# Test all components
python test_full_api.py

# Test live server
python test_live_api.py

# Run demo
python demo_api.py
```

## 📚 Documentation

- **Interactive API Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health
- **Status**: http://localhost:8000/api/v1/status

## 🔒 Security

- Bearer token authentication required
- Input validation and sanitization
- File size limits enforced
- Temporary file cleanup
- No data persistence (stateless)

## 🛠️ Production Considerations

### Docker Deployment
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Optional: Install enhanced features
pip install sentence-transformers faiss-cpu python-docx

# Set environment variables
export PORT=8000
export WORKERS=4
```

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**: Install optional dependencies
   ```bash
   pip install sentence-transformers faiss-cpu python-docx
   ```

2. **Network Errors**: Check blob URL accessibility
   ```bash
   curl -I "https://your-blob-url.com/document.pdf"
   ```

3. **Large Files**: Increase timeout settings
   ```python
   httpx.AsyncClient(timeout=300.0)
   ```

4. **Memory Issues**: Reduce concurrent workers
   ```bash
   uvicorn api:app --workers 2
   ```

## 📈 Monitoring

### Health Endpoints
- `GET /health` - Basic health check
- `GET /api/v1/status` - Detailed system status

### Logging
- Application logs to stdout
- Error tracking available
- Request timing logged

## 🔄 API Versioning

Current version: **v1**
- Stable API contract
- Backward compatibility maintained
- Future versions will be additive

---

**Built for the DocQuery LLM-Powered Intelligent Query-Retrieval System**