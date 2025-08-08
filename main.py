#!/usr/bin/env python3
"""
Main FastAPI application for DocQuery - replaces Streamlit with web-based interface.
Serves HTML frontend and provides REST API endpoints for document analysis.
"""

import os
import sys
import tempfile
import time
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# Add current directory to path to import existing modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import existing modules (unchanged)
try:
    from document_processor import DocumentProcessor
    DOCUMENT_PROCESSOR_AVAILABLE = True
except ImportError:
    DOCUMENT_PROCESSOR_AVAILABLE = False
    print("Warning: DocumentProcessor not available")

try:
    from query_parser import QueryParser  
    QUERY_PARSER_AVAILABLE = True
except ImportError:
    QUERY_PARSER_AVAILABLE = False
    print("Warning: QueryParser not available")

try:
    from output_formatter import OutputFormatter
    OUTPUT_FORMATTER_AVAILABLE = True
except ImportError:
    OUTPUT_FORMATTER_AVAILABLE = False
    print("Warning: OutputFormatter not available")

# Try to import AI clients with fallbacks
try:
    from local_ai_client import LocalAIClient
    LOCAL_AI_AVAILABLE = True
except ImportError:
    LOCAL_AI_AVAILABLE = False
    print("Warning: LocalAIClient not available")

try:
    from openai_client import OpenAIClient  
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAIClient not available")

# Try to import vector search with fallbacks
try:
    from vector_search import VectorSearch
    SEARCH_TYPE = "Advanced semantic search"
except ImportError:
    try:
        from enhanced_vector_search import EnhancedVectorSearch as VectorSearch
        SEARCH_TYPE = "Enhanced TF-IDF search"
    except ImportError:
        try:
            from simple_vector_search import SimpleVectorSearch as VectorSearch
            SEARCH_TYPE = "Simple text search"
        except ImportError:
            VectorSearch = None
            SEARCH_TYPE = "Basic keyword search"

# Pydantic models for request/response
class AnalyzeDocumentRequest(BaseModel):
    document_text: str
    document_name: Optional[str] = "uploaded_document.txt"

class QueryRequest(BaseModel):
    query: str
    document_text: Optional[str] = None

# FastAPI app setup
app = FastAPI(
    title="DocQuery - AI Document Analysis",
    description="AI-powered document analysis system without Streamlit",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files if static directory exists
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Global state for processed documents (in production, use Redis or database)
document_store: Dict[str, Dict] = {}
vector_search_instances: Dict[str, Any] = {}

# Initialize core components that are available
if DOCUMENT_PROCESSOR_AVAILABLE:
    document_processor = DocumentProcessor()
if QUERY_PARSER_AVAILABLE:
    query_parser = QueryParser()
if OUTPUT_FORMATTER_AVAILABLE:
    output_formatter = OutputFormatter()

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the main HTML frontend instead of Streamlit."""
    # Look for index.html in the current directory
    current_dir = Path(__file__).parent
    index_path = current_dir / "index.html"
    
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(f.read())
    else:
        return HTMLResponse("""
        <!DOCTYPE html>
        <html><head><title>DocQuery</title></head>
        <body>
            <h1>DocQuery API</h1>
            <p>Frontend not found. API endpoints available:</p>
            <ul>
                <li>POST /api/analyze - Analyze document text</li>
                <li>POST /api/query - Process queries</li>
                <li>GET /health - Health check</li>
            </ul>
        </body></html>
        """)

@app.get("/style.css")
async def serve_css():
    """Serve the CSS file if it exists."""
    current_dir = Path(__file__).parent
    css_path = current_dir / "style.css"
    if css_path.exists():
        return FileResponse(css_path, media_type="text/css")
    else:
        return ""

@app.get("/health")
async def health_check():
    """Health check endpoint for deployment platforms."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "DocQuery FastAPI (No Streamlit)",
        "capabilities": {
            "document_processor": DOCUMENT_PROCESSOR_AVAILABLE,
            "query_parser": QUERY_PARSER_AVAILABLE,
            "local_ai": LOCAL_AI_AVAILABLE,
            "openai": OPENAI_AVAILABLE,
            "search_type": SEARCH_TYPE
        },
        "documents_loaded": len(document_store)
    }

@app.get("/api/status")
async def api_status():
    """API status endpoint for the frontend."""
    return {
        "status": "online",
        "search_type": SEARCH_TYPE,
        "capabilities": {
            "basic_functionality": DOCUMENT_PROCESSOR_AVAILABLE and QUERY_PARSER_AVAILABLE,
            "word_processing": DOCUMENT_PROCESSOR_AVAILABLE,
            "advanced_ai": LOCAL_AI_AVAILABLE or OPENAI_AVAILABLE,
            "semantic_search": VectorSearch is not None
        },
        "message": "DocQuery API running without Streamlit"
    }

@app.post("/api/analyze")
async def analyze_document(request: AnalyzeDocumentRequest):
    """
    Analyze document text and create searchable chunks.
    This replaces Streamlit document processing.
    """
    try:
        start_time = time.time()
        
        if not DOCUMENT_PROCESSOR_AVAILABLE:
            # Fallback processing
            text_content = request.document_text
            # Simple chunking
            chunk_size = 1000
            chunks = [text_content[i:i+chunk_size] for i in range(0, len(text_content), chunk_size)]
        else:
            # Use full document processor
            # Create temporary file for processing
            file_extension = ".txt"
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension, mode='w', encoding='utf-8') as tmp_file:
                tmp_file.write(request.document_text)
                tmp_file_path = tmp_file.name
            
            try:
                text_content = document_processor.extract_text(tmp_file_path)
                chunks = document_processor.chunk_text(text_content)
            finally:
                os.unlink(tmp_file_path)
        
        # Initialize vector search if available
        vector_search = None
        search_ready = False
        if VectorSearch and len(chunks) > 0:
            try:
                vector_search = VectorSearch()
                if hasattr(vector_search, 'build_index'):
                    vector_search.build_index(chunks)
                elif hasattr(vector_search, 'add_documents'):
                    vector_search.add_documents(chunks)
                search_ready = True
            except Exception as e:
                print(f"Vector search initialization failed: {e}")
                vector_search = None
        
        processing_time = time.time() - start_time
        
        # Store document for future queries
        document_id = str(uuid.uuid4())
        document_store[document_id] = {
            "text_content": text_content,
            "chunks": chunks,
            "name": request.document_name,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        
        if vector_search:
            vector_search_instances[document_id] = vector_search
        
        # Response matching frontend expectations
        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "document_analysis": {
                "document_name": request.document_name,
                "processed_content": text_content[:1000] + ("..." if len(text_content) > 1000 else ""),
                "full_content_length": len(text_content),
                "character_count": len(request.document_text),
                "chunk_count": len(chunks),
                "average_chunk_size": len(text_content) // len(chunks) if chunks else 0
            },
            "processing_details": {
                "processing_time": f"{processing_time:.3f}s",
                "search_type": SEARCH_TYPE,
                "chunks_created": len(chunks),
                "search_ready": search_ready,
                "vector_search_available": VectorSearch is not None
            },
            "document_stats": {
                "total_characters": len(text_content),
                "total_words": len(text_content.split()),
                "estimated_reading_time": f"{len(text_content.split()) // 200 + 1} min",
                "chunk_distribution": {
                    "small_chunks": len([c for c in chunks if len(c) < 500]),
                    "medium_chunks": len([c for c in chunks if 500 <= len(c) < 1500]),
                    "large_chunks": len([c for c in chunks if len(c) >= 1500])
                }
            },
            "capabilities": {
                "ready_for_queries": True,
                "semantic_search": search_ready,
                "vector_analysis": VectorSearch is not None,
                "advanced_ai": LOCAL_AI_AVAILABLE
            },
            "system": {
                "processor_version": "fastapi_v1.0",
                "search_type": SEARCH_TYPE
            },
            "status": "processed",
            "_internal_document_id": document_id  # For internal use
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document analysis failed: {str(e)}")

@app.post("/api/query") 
async def process_query(request: QueryRequest):
    """
    Process query against document content.
    This replaces Streamlit query processing.
    """
    try:
        start_time = time.time()
        analysis_id = str(uuid.uuid4())[:8]
        
        # Parse query if parser available
        parsed_query = {}
        if QUERY_PARSER_AVAILABLE:
            try:
                parsed_query = query_parser.parse_query(request.query)
            except Exception as e:
                print(f"Query parsing failed: {e}")
        
        # Get relevant chunks from document
        relevant_chunks = []
        if request.document_text:
            # Process document inline for query
            if DOCUMENT_PROCESSOR_AVAILABLE:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tmp_file:
                    tmp_file.write(request.document_text)
                    tmp_file_path = tmp_file.name
                
                try:
                    processed_content = document_processor.extract_text(tmp_file_path)
                    chunks = document_processor.chunk_text(processed_content)
                finally:
                    os.unlink(tmp_file_path)
            else:
                # Simple fallback chunking
                chunk_size = 1000
                chunks = [request.document_text[i:i+chunk_size] for i in range(0, len(request.document_text), chunk_size)]
            
            # Simple search for relevant chunks
            query_lower = request.query.lower()
            scored_chunks = []
            for chunk in chunks:
                score = sum(1 for word in query_lower.split() if word.lower() in chunk.lower())
                if score > 0:
                    scored_chunks.append((score, chunk))
            
            scored_chunks.sort(reverse=True)
            relevant_chunks = [chunk for _, chunk in scored_chunks[:3]]
            if not relevant_chunks:
                relevant_chunks = chunks[:3]
        
        # Perform AI analysis
        analysis_result = None
        ai_method = "rule_based_fallback"
        
        if LOCAL_AI_AVAILABLE:
            try:
                local_ai = LocalAIClient()
                analysis_result = local_ai.analyze_query(parsed_query, relevant_chunks, request.query)
                ai_method = "local_ai"
            except Exception as e:
                print(f"Local AI analysis failed: {e}")
        
        # Fallback analysis
        if not analysis_result:
            analysis_result = generate_fallback_analysis(request.query, parsed_query, relevant_chunks)
        
        processing_time = time.time() - start_time
        
        # Create response matching frontend expectations
        return {
            "success": True,
            "analysis_id": analysis_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "query": {
                "original": request.query,
                "parsed_components": {k: v for k, v in parsed_query.items() if v},
                "domain": parsed_query.get("query_type", "general")
            },
            "analysis": {
                "decision": {
                    "status": analysis_result.get("decision", "Requires Review"),
                    "confidence": analysis_result.get("confidence", "Medium"),
                    "risk_level": analysis_result.get("risk_level", "Medium")
                },
                "justification": {
                    "summary": analysis_result.get("justification", "Analysis completed based on available data"),
                    "detailed_factors": analysis_result.get("detailed_factors", []),
                    "clause_references": analysis_result.get("clause_references", [])
                },
                "recommendations": analysis_result.get("recommendations", [
                    "Review analysis results for accuracy",
                    "Consider additional documentation if needed"
                ]),
                "next_steps": analysis_result.get("next_steps", [
                    "Proceed based on analysis results",
                    "Document decision for records"
                ])
            },
            "document_analysis": {
                "chunks_processed": len(relevant_chunks) if relevant_chunks else 0,
                "relevant_sections": len(relevant_chunks),
                "content_preview": relevant_chunks[0][:200] + "..." if relevant_chunks else None
            } if request.document_text else None,
            "system": {
                "analysis_method": ai_method,
                "processing_time": f"{processing_time:.3f}s",
                "model_version": "fastapi_no_streamlit_v1.0",
                "search_type": SEARCH_TYPE
            },
            "status": "completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

def generate_fallback_analysis(query: str, parsed_query: Dict, relevant_chunks: List[str]) -> Dict:
    """Generate fallback analysis when AI is not available."""
    query_lower = query.lower()
    
    # Simple decision logic
    if any(word in query_lower for word in ['approved', 'accept', 'yes', 'covered']):
        decision = "Approved"
        confidence = "Medium"
        risk_level = "Low"
    elif any(word in query_lower for word in ['rejected', 'deny', 'no', 'not covered']):
        decision = "Rejected" 
        confidence = "Medium"
        risk_level = "High"
    else:
        decision = "Requires Review"
        confidence = "Medium"
        risk_level = "Medium"
    
    justification_parts = [f"Rule-based analysis of query: '{query}'"]
    if parsed_query.get('age'):
        justification_parts.append(f"Patient age: {parsed_query['age']}")
    if parsed_query.get('procedure'):
        justification_parts.append(f"Procedure: {parsed_query['procedure']}")
    if relevant_chunks:
        justification_parts.append(f"Analyzed {len(relevant_chunks)} relevant document sections")
    
    return {
        "decision": decision,
        "confidence": confidence,
        "risk_level": risk_level,
        "justification": ". ".join(justification_parts),
        "detailed_factors": [
            "Query parsing completed",
            "Document content analyzed" if relevant_chunks else "No document provided",
            "Rule-based decision applied",
            f"Risk level: {risk_level}"
        ],
        "recommendations": [
            "Review the analysis for accuracy",
            "Consider expert consultation if needed",
            f"{'Proceed with approval process' if decision == 'Approved' else 'Additional review recommended'}"
        ],
        "next_steps": [
            f"{'Submit application' if decision == 'Approved' else 'Gather more information'}",
            "Document the decision",
            "Follow organizational procedures"
        ]
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting DocQuery FastAPI server (no Streamlit) on port {port}")
    print(f"📍 Frontend available at: http://localhost:{port}")
    print(f"📊 API endpoints at: http://localhost:{port}/api/*")
    print(f"❤️ Health check: http://localhost:{port}/health")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0", 
        port=port,
        reload=False
    )