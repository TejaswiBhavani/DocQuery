# DocQuery - Vercel Deployment Guide

DocQuery has been successfully refactored for Vercel deployment with a modern Next.js frontend and serverless Python API.

## 🏗️ Architecture

- **Frontend**: Next.js application with React components (`frontend/`)
- **API**: Individual Python serverless functions (`api/`)
- **Backend**: Python processing modules (`backend/`)

## 📁 Project Structure

```
DocQuery/
├── api/                     # Vercel serverless functions
│   ├── upload.py           # Document upload & processing
│   ├── search.py           # Document search
│   └── analyze.py          # AI-powered analysis
├── backend/                # Python processing modules
│   ├── document_processor.py
│   ├── query_parser.py
│   ├── local_ai_client.py
│   └── ... (all core modules)
├── frontend/               # Next.js application
│   ├── pages/index.js      # Main application
│   ├── components/         # React components
│   └── styles/            # CSS styles
├── vercel.json            # Vercel configuration
└── requirements.txt       # Python dependencies
```

## 🚀 Vercel Deployment

### 1. Connect Repository
- Connect your GitHub repository to Vercel
- Vercel will automatically detect Next.js and Python functions

### 2. Environment Variables
Configure these in Vercel Dashboard:
```bash
# Optional: For OpenAI integration
OPENAI_API_KEY=your_openai_api_key_here

# Optional: For advanced features
TRANSFORMERS_CACHE_DIR=/tmp/.transformers_cache
HUGGINGFACE_HUB_CACHE=/tmp/.huggingface_cache
```

### 3. Deploy
```bash
# Via Vercel CLI
vercel

# Or push to connected GitHub repo
git push origin main
```

## 💻 Local Development

### Backend Testing
```bash
# Install Python dependencies
pip install -r requirements.txt

# Test backend modules
cd backend && python -c "from document_processor import DocumentProcessor; print('✅ Backend working')"
```

### Frontend Development
```bash
# Install Node.js dependencies
cd frontend && npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## 🔧 API Endpoints

### Upload Document
```bash
POST /api/upload
Content-Type: application/json

{
  "file_content": "base64_encoded_file_content",
  "file_name": "document.pdf",
  "document_name": "My Document"
}
```

### Search Documents
```bash
POST /api/search
Content-Type: application/json

{
  "query": "search terms",
  "document_text": "document content to search",
  "top_k": 3
}
```

### Analyze Query
```bash
POST /api/analyze
Content-Type: application/json

{
  "query": "46-year-old male, knee surgery",
  "document_text": "policy content",
  "use_local_ai": true,
  "openai_api_key": "optional_if_using_openai"
}
```

## 🎯 Features

- **📄 Multi-format Support**: PDF, Word, Text, Email
- **🤖 AI Analysis**: Local AI or OpenAI integration
- **🔍 Smart Search**: Vector-based semantic search
- **📱 Responsive UI**: Modern React interface
- **⚡ Serverless**: Scales automatically
- **🚀 Fast Deploy**: Single command deployment

## 🔧 Customization

### Adding New API Endpoints
1. Create new `.py` file in `api/` directory
2. Follow the handler pattern from existing endpoints
3. Import modules from `backend/`

### Frontend Modifications
1. Edit components in `frontend/components/`
2. Modify pages in `frontend/pages/`
3. Update styles in `frontend/styles/`

## 📊 Performance

- **Cold Start**: ~2-3 seconds for Python functions
- **Warm Requests**: ~200-500ms
- **Frontend**: Static generation for optimal speed
- **Scaling**: Automatic based on demand

## 🐛 Troubleshooting

### API Issues
- Check Vercel function logs
- Verify Python dependencies in `requirements.txt`
- Ensure modules import correctly from `backend/`

### Frontend Issues  
- Check browser console for API call errors
- Verify CORS headers are set in API endpoints
- Test API endpoints independently

### Deployment Issues
- Verify `vercel.json` configuration
- Check build logs in Vercel dashboard
- Ensure Node.js and Python versions are compatible

---

## 🎉 Migration Complete!

The project has been successfully refactored from Streamlit to a modern serverless architecture:

- ✅ Streamlit removed
- ✅ Next.js frontend created
- ✅ Individual API endpoints built
- ✅ All existing Python logic preserved
- ✅ Ready for Vercel deployment