"""
FastAPI backend for DocQuery - wraps existing Python modules with HTTP endpoints.
Provides /upload, /search, and /analyze endpoints while keeping all core modules unchanged.
"""

import os
import sys
import tempfile
import time
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add parent directory to path to import existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import existing modules (unchanged)
from document_processor import DocumentProcessor
from query_parser import QueryParser
from output_formatter import OutputFormatter

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
        from simple_vector_search import SimpleVectorSearch as VectorSearch
        SEARCH_TYPE = "Simple text search"

# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str
    document_id: Optional[str] = None
    use_local_ai: bool = True

class SearchRequest(BaseModel):
    query: str
    document_id: str
    top_k: int = 3

class AnalysisResponse(BaseModel):
    success: bool
    analysis_id: str
    timestamp: str
    query: Dict[str, Any]
    analysis: Dict[str, Any]
    system: Dict[str, Any]

# FastAPI app setup
app = FastAPI(
    title="DocQuery API",
    description="AI-powered document analysis system",
    version="1.0.0"
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],  # Next.js dev server and production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for processed documents (in production, use Redis or database)
document_store: Dict[str, Dict] = {}
vector_search_instances: Dict[str, Any] = {}

# Initialize core components
document_processor = DocumentProcessor()
query_parser = QueryParser()
output_formatter = OutputFormatter()

@app.get("/")
async def root():
    """API health check and information."""
    return {
        "message": "DocQuery FastAPI Backend",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/upload - Upload and process documents",
            "search": "/search - Search within documents",
            "analyze": "/analyze - AI-powered query analysis"
        },
        "capabilities": {
            "local_ai": LOCAL_AI_AVAILABLE,
            "openai": OPENAI_AVAILABLE,
            "search_type": SEARCH_TYPE
        }
    }

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_name: Optional[str] = Form(None)
):
    """
    Upload and process a document for analysis.
    Creates text chunks and builds searchable index.
    """
    try:
        start_time = time.time()
        document_id = str(uuid.uuid4())
        
        # Use provided name or file name
        doc_name = document_name or file.filename or f"document_{document_id[:8]}"
        
        # Read file content
        file_content = await file.read()
        
        # Create temporary file with proper extension
        file_extension = os.path.splitext(file.filename or "")[1] or ".txt"
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            tmp_file.write(file_content)
            tmp_file_path = tmp_file.name
        
        try:
            # Process document using existing module
            text_content = document_processor.extract_text(tmp_file_path)
            chunks = document_processor.chunk_text(text_content)
            
            # Initialize vector search for this document
            vector_search = VectorSearch()
            
            # Handle different vector search interfaces
            try:
                if hasattr(vector_search, 'build_index'):
                    vector_search.build_index(chunks)
                elif hasattr(vector_search, 'add_documents'):
                    vector_search.add_documents(chunks)
                else:
                    # Fallback for simple search
                    vector_search.documents = chunks
            except Exception as search_error:
                print(f"Vector search setup warning: {search_error}")
                # Continue without vector search
                vector_search = None
            
            # Store document and search instance
            processing_time = time.time() - start_time
            
            document_data = {
                "id": document_id,
                "name": doc_name,
                "text_content": text_content,
                "chunks": chunks,
                "upload_time": datetime.utcnow().isoformat() + "Z",
                "processing_time": processing_time,
                "file_size": len(file_content),
                "chunk_count": len(chunks)
            }
            
            document_store[document_id] = document_data
            if vector_search:
                vector_search_instances[document_id] = vector_search
            
            return {
                "success": True,
                "document_id": document_id,
                "document_name": doc_name,
                "processing_time": f"{processing_time:.3f}s",
                "statistics": {
                    "file_size": len(file_content),
                    "character_count": len(text_content),
                    "chunk_count": len(chunks),
                    "average_chunk_size": len(text_content) // len(chunks) if chunks else 0
                },
                "capabilities": {
                    "search_ready": vector_search is not None,
                    "search_type": SEARCH_TYPE
                },
                "message": "Document processed successfully and ready for analysis"
            }
            
        finally:
            # Clean up temp file
            os.unlink(tmp_file_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

@app.post("/search")
async def search_documents(request: SearchRequest):
    """
    Search for relevant content within a processed document.
    """
    try:
        if request.document_id not in document_store:
            raise HTTPException(status_code=404, detail="Document not found")
        
        document_data = document_store[request.document_id]
        chunks = document_data["chunks"]
        
        # Perform vector search if available
        if request.document_id in vector_search_instances:
            vector_search = vector_search_instances[request.document_id]
            try:
                if hasattr(vector_search, 'search'):
                    relevant_chunks = vector_search.search(request.query, k=request.top_k)
                else:
                    # Fallback to simple matching
                    query_lower = request.query.lower()
                    scored_chunks = []
                    for chunk in chunks:
                        score = sum(1 for word in query_lower.split() if word in chunk.lower())
                        if score > 0:
                            scored_chunks.append((score, chunk))
                    scored_chunks.sort(reverse=True)
                    relevant_chunks = [chunk for _, chunk in scored_chunks[:request.top_k]]
            except Exception as search_error:
                print(f"Search error: {search_error}")
                # Fallback to first few chunks
                relevant_chunks = chunks[:request.top_k]
        else:
            # Simple fallback search
            query_lower = request.query.lower()
            relevant_chunks = []
            for chunk in chunks:
                if any(word in chunk.lower() for word in query_lower.split()):
                    relevant_chunks.append(chunk)
                if len(relevant_chunks) >= request.top_k:
                    break
            
            if not relevant_chunks:
                relevant_chunks = chunks[:request.top_k]
        
        return {
            "success": True,
            "document_id": request.document_id,
            "document_name": document_data["name"],
            "query": request.query,
            "relevant_chunks": relevant_chunks,
            "total_chunks": len(chunks),
            "search_type": SEARCH_TYPE,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/analyze")
async def analyze_query(request: QueryRequest):
    """
    Perform AI-powered analysis of a query against a document.
    This is the main endpoint that combines parsing, search, and AI analysis.
    """
    try:
        start_time = time.time()
        analysis_id = str(uuid.uuid4())[:8]
        
        # Parse query using existing module
        parsed_query = query_parser.parse_query(request.query)
        
        relevant_chunks = []
        document_data = None
        
        # If document provided, get relevant chunks
        if request.document_id:
            if request.document_id not in document_store:
                raise HTTPException(status_code=404, detail="Document not found")
            
            document_data = document_store[request.document_id]
            chunks = document_data["chunks"]
            
            # Get relevant chunks via search
            if request.document_id in vector_search_instances:
                vector_search = vector_search_instances[request.document_id]
                try:
                    if hasattr(vector_search, 'search'):
                        relevant_chunks = vector_search.search(request.query, k=3)
                    else:
                        relevant_chunks = chunks[:3]  # Fallback
                except Exception:
                    relevant_chunks = chunks[:3]  # Fallback
            else:
                # Simple search fallback
                query_words = request.query.lower().split()
                scored_chunks = []
                for chunk in chunks:
                    score = sum(1 for word in query_words if word in chunk.lower())
                    if score > 0:
                        scored_chunks.append((score, chunk))
                scored_chunks.sort(reverse=True)
                relevant_chunks = [chunk for _, chunk in scored_chunks[:3]]
                if not relevant_chunks:
                    relevant_chunks = chunks[:3]
        
        # Perform AI analysis
        analysis_result = None
        ai_method = "rule_based_fallback"
        
        if request.use_local_ai and LOCAL_AI_AVAILABLE:
            try:
                local_ai = LocalAIClient()
                analysis_result = local_ai.analyze_query(parsed_query, relevant_chunks, request.query)
                ai_method = "local_ai"
            except Exception as e:
                print(f"Local AI analysis failed: {e}")
        
        elif not request.use_local_ai and OPENAI_AVAILABLE:
            try:
                openai_client = OpenAIClient()
                analysis_result = openai_client.analyze_query(parsed_query, relevant_chunks, request.query)
                ai_method = "openai_gpt"
            except Exception as e:
                print(f"OpenAI analysis failed: {e}")
        
        # Fallback analysis if AI fails
        if not analysis_result:
            analysis_result = {
                "decision": "Requires Review",
                "confidence": "Medium",
                "justification": "Basic rule-based analysis completed. Advanced AI analysis unavailable.",
                "recommendations": [
                    "Review the query and document content manually",
                    "Consider enabling AI analysis for more detailed insights"
                ],
                "analysis_method": "rule_based_fallback"
            }
            ai_method = "rule_based_fallback"
        
        # Format response using existing output formatter
        processing_time = time.time() - start_time
        
        # Create comprehensive response
        response_data = {
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
                    "status": analysis_result.get("decision", "Pending"),
                    "confidence": analysis_result.get("confidence", "Medium"),
                    "risk_level": analysis_result.get("risk_level", "Medium")
                },
                "justification": {
                    "summary": analysis_result.get("justification", "Analysis completed"),
                    "detailed_factors": analysis_result.get("detailed_factors", []),
                    "clause_references": analysis_result.get("clause_references", [])
                },
                "recommendations": analysis_result.get("recommendations", []),
                "next_steps": analysis_result.get("next_steps", [])
            },
            "document_analysis": {
                "document_id": request.document_id,
                "document_name": document_data["name"] if document_data else None,
                "chunks_analyzed": len(relevant_chunks),
                "relevant_content": relevant_chunks[:1] if relevant_chunks else []  # Preview only
            } if document_data else None,
            "system": {
                "analysis_method": ai_method,
                "processing_time": f"{processing_time:.3f}s",
                "model_version": "fastapi_v1.0",
                "search_type": SEARCH_TYPE,
                "capabilities_used": {
                    "local_ai": LOCAL_AI_AVAILABLE and request.use_local_ai,
                    "openai": OPENAI_AVAILABLE and not request.use_local_ai,
                    "vector_search": request.document_id in vector_search_instances if request.document_id else False
                }
            }
        }
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/documents")
async def list_documents():
    """List all uploaded documents."""
    return {
        "success": True,
        "documents": [
            {
                "id": doc_id,
                "name": data["name"],
                "upload_time": data["upload_time"],
                "chunk_count": data["chunk_count"],
                "file_size": data["file_size"]
            }
            for doc_id, data in document_store.items()
        ],
        "total": len(document_store)
    }

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a processed document."""
    if document_id not in document_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Remove from stores
    del document_store[document_id]
    if document_id in vector_search_instances:
        del vector_search_instances[document_id]
    
    return {
        "success": True,
        "message": f"Document {document_id} deleted successfully"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "capabilities": {
            "local_ai": LOCAL_AI_AVAILABLE,
            "openai": OPENAI_AVAILABLE,
            "search_type": SEARCH_TYPE
        },
        "documents_loaded": len(document_store)
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0", 
        port=port,
        reload=True
    )