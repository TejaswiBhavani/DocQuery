"""
Simplified FastAPI backend for DocQuery demo - works without heavy ML dependencies.
Provides /upload, /search, and /analyze endpoints with graceful fallbacks.
"""

import os
import sys
import tempfile
import time
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, Union

# Add parent directory to path to import existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import existing modules (unchanged) with fallbacks
try:
    from document_processor import DocumentProcessor
    DOCUMENT_PROCESSOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: DocumentProcessor not available: {e}")
    DOCUMENT_PROCESSOR_AVAILABLE = False

try:
    from query_parser import QueryParser
    QUERY_PARSER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: QueryParser not available: {e}")
    QUERY_PARSER_AVAILABLE = False

try:
    from output_formatter import OutputFormatter
    OUTPUT_FORMATTER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: OutputFormatter not available: {e}")
    OUTPUT_FORMATTER_AVAILABLE = False

# Try to import AI clients with fallbacks
try:
    from local_ai_client import LocalAIClient
    LOCAL_AI_AVAILABLE = True
except ImportError as e:
    print(f"Warning: LocalAIClient not available: {e}")
    LOCAL_AI_AVAILABLE = False

try:
    from openai_client import OpenAIClient
    OPENAI_AVAILABLE = True
except ImportError as e:
    print(f"Warning: OpenAIClient not available: {e}")
    OPENAI_AVAILABLE = False

# Try to import vector search with fallbacks
try:
    from vector_search import VectorSearch
    SEARCH_TYPE = "Advanced semantic search"
    VECTOR_SEARCH_AVAILABLE = True
except ImportError:
    try:
        from enhanced_vector_search import EnhancedVectorSearch as VectorSearch
        SEARCH_TYPE = "Enhanced TF-IDF search"
        VECTOR_SEARCH_AVAILABLE = True
    except ImportError:
        try:
            from simple_vector_search import SimpleVectorSearch as VectorSearch
            SEARCH_TYPE = "Simple text search"
            VECTOR_SEARCH_AVAILABLE = True
        except ImportError:
            print("Warning: No vector search available, using fallback")
            VECTOR_SEARCH_AVAILABLE = False
            SEARCH_TYPE = "Basic text matching"

# Create a simple mock app that responds with demo data
class MockApp:
    def __init__(self):
        self.documents = {}
        
    def root(self):
        return {
            "message": "DocQuery FastAPI Backend (Demo Mode)",
            "version": "1.0.0",
            "status": "running",
            "capabilities": {
                "document_processor": DOCUMENT_PROCESSOR_AVAILABLE,
                "query_parser": QUERY_PARSER_AVAILABLE,
                "local_ai": LOCAL_AI_AVAILABLE,
                "openai": OPENAI_AVAILABLE,
                "vector_search": VECTOR_SEARCH_AVAILABLE,
                "search_type": SEARCH_TYPE
            },
            "endpoints": {
                "upload": "/upload - Upload and process documents",
                "search": "/search - Search within documents", 
                "analyze": "/analyze - AI-powered query analysis",
                "health": "/health - System health check"
            }
        }
    
    def upload(self, file_content: bytes, filename: str):
        """Mock document upload that creates a demo response."""
        document_id = str(uuid.uuid4())
        processing_time = 0.5 + (len(file_content) / 1000000) * 0.1  # Simulate processing time
        
        # Extract some basic text (fallback if no processor)
        if DOCUMENT_PROCESSOR_AVAILABLE:
            # Use real processor if available
            try:
                processor = DocumentProcessor()
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1] or '.txt') as tmp_file:
                    tmp_file.write(file_content)
                    tmp_file_path = tmp_file.name
                
                text_content = processor.extract_text(tmp_file_path)
                chunks = processor.chunk_text(text_content)
                os.unlink(tmp_file_path)
            except Exception as e:
                print(f"Processor error: {e}")
                # Fallback to basic text extraction
                text_content = file_content.decode('utf-8', errors='ignore')
                chunks = [text_content[i:i+1000] for i in range(0, len(text_content), 1000)]
        else:
            # Fallback text processing
            text_content = file_content.decode('utf-8', errors='ignore')
            chunks = [text_content[i:i+1000] for i in range(0, len(text_content), 1000)]
        
        # Store document data
        self.documents[document_id] = {
            "id": document_id,
            "name": filename,
            "text_content": text_content,
            "chunks": chunks,
            "upload_time": datetime.utcnow().isoformat() + "Z",
            "file_size": len(file_content)
        }
        
        return {
            "success": True,
            "document_id": document_id,
            "document_name": filename,
            "processing_time": f"{processing_time:.3f}s",
            "statistics": {
                "file_size": len(file_content),
                "character_count": len(text_content),
                "chunk_count": len(chunks),
                "average_chunk_size": len(text_content) // len(chunks) if chunks else 0
            },
            "capabilities": {
                "search_ready": True,
                "search_type": SEARCH_TYPE
            },
            "message": "Document processed successfully and ready for analysis"
        }
    
    def search(self, document_id: str, query: str, top_k: int = 3):
        """Mock search that returns relevant chunks."""
        if document_id not in self.documents:
            raise ValueError("Document not found")
            
        doc_data = self.documents[document_id]
        chunks = doc_data["chunks"]
        
        # Simple keyword matching fallback
        query_words = query.lower().split()
        scored_chunks = []
        
        for chunk in chunks:
            score = sum(1 for word in query_words if word in chunk.lower())
            if score > 0:
                scored_chunks.append((score, chunk))
        
        scored_chunks.sort(reverse=True)
        relevant_chunks = [chunk for _, chunk in scored_chunks[:top_k]]
        
        if not relevant_chunks and chunks:
            relevant_chunks = chunks[:top_k]  # Return first chunks if no matches
            
        return {
            "success": True,
            "document_id": document_id,
            "document_name": doc_data["name"],
            "query": query,
            "relevant_chunks": relevant_chunks,
            "total_chunks": len(chunks),
            "search_type": SEARCH_TYPE
        }
    
    def analyze(self, query: str, document_id: str = None, use_local_ai: bool = True):
        """Mock analysis that provides demo response."""
        analysis_id = str(uuid.uuid4())[:8]
        
        # Parse query if parser available
        parsed_query = {}
        if QUERY_PARSER_AVAILABLE:
            try:
                parser = QueryParser()
                parsed_query = parser.parse_query(query)
            except Exception as e:
                print(f"Parser error: {e}")
        
        # Get relevant chunks if document provided
        relevant_chunks = []
        document_data = None
        if document_id and document_id in self.documents:
            search_result = self.search(document_id, query, 3)
            relevant_chunks = search_result["relevant_chunks"]
            document_data = self.documents[document_id]
        
        # Create mock analysis result
        analysis_result = {
            "decision": "Approved" if "approve" in query.lower() else "Requires Review",
            "confidence": "Medium",
            "risk_level": "Low",
            "justification": f"Analysis based on query: '{query}'. " + 
                           ("Document content analyzed. " if document_data else "") +
                           "This is a demo response showing system capabilities.",
            "detailed_factors": [
                "Query parameters extracted and processed",
                "Document content analysis completed" if document_data else "No document provided",
                "Risk assessment performed using rule-based logic",
                "Confidence scoring based on available information"
            ],
            "recommendations": [
                "Review the analysis details for accuracy",
                "Consider additional documentation if needed",
                "Consult with domain expert for complex cases"
            ],
            "next_steps": [
                "Proceed based on the decision status",
                "Keep documentation for audit trail",
                "Follow up as necessary"
            ],
            "analysis_method": "demo_mode"
        }
        
        # Format comprehensive response
        response = {
            "success": True,
            "analysis_id": analysis_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "query": {
                "original": query,
                "parsed_components": {k: v for k, v in parsed_query.items() if v},
                "domain": parsed_query.get("query_type", "general")
            },
            "analysis": {
                "decision": {
                    "status": analysis_result["decision"],
                    "confidence": analysis_result["confidence"],
                    "risk_level": analysis_result["risk_level"]
                },
                "justification": {
                    "summary": analysis_result["justification"],
                    "detailed_factors": analysis_result["detailed_factors"],
                    "clause_references": []
                },
                "recommendations": analysis_result["recommendations"],
                "next_steps": analysis_result["next_steps"]
            },
            "document_analysis": {
                "document_id": document_id,
                "document_name": document_data["name"] if document_data else None,
                "chunks_analyzed": len(relevant_chunks),
                "relevant_content": relevant_chunks[:1] if relevant_chunks else []
            } if document_data else None,
            "system": {
                "analysis_method": "demo_mode_with_fallbacks",
                "processing_time": "0.125s",
                "model_version": "fastapi_demo_v1.0",
                "search_type": SEARCH_TYPE,
                "capabilities_used": {
                    "document_processor": DOCUMENT_PROCESSOR_AVAILABLE,
                    "query_parser": QUERY_PARSER_AVAILABLE and bool(parsed_query),
                    "vector_search": VECTOR_SEARCH_AVAILABLE,
                    "local_ai": False,  # Demo mode
                    "openai": False   # Demo mode
                }
            }
        }
        
        return response

# Create simple HTTP server for demo
if __name__ == "__main__":
    import json
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from urllib.parse import urlparse, parse_qs
    import cgi

    app = MockApp()
    
    class RequestHandler(BaseHTTPRequestHandler):
        def _set_cors_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        def do_OPTIONS(self):
            self.send_response(200)
            self._set_cors_headers()
            self.end_headers()
        
        def do_GET(self):
            parsed_path = urlparse(self.path)
            
            if parsed_path.path == '/' or parsed_path.path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                
                response = app.root()
                self.wfile.write(json.dumps(response, indent=2).encode())
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Not found"}).encode())
        
        def do_POST(self):
            try:
                parsed_path = urlparse(self.path)
                
                if parsed_path.path == '/upload':
                    # Handle file upload
                    content_type = self.headers['content-type']
                    if not content_type.startswith('multipart/form-data'):
                        raise ValueError("Expected multipart/form-data")
                    
                    form_data = cgi.FieldStorage(
                        fp=self.rfile,
                        headers=self.headers,
                        environ={'REQUEST_METHOD': 'POST'}
                    )
                    
                    if 'file' not in form_data:
                        raise ValueError("No file provided")
                    
                    file_item = form_data['file']
                    filename = file_item.filename or 'uploaded_file.txt'
                    file_content = file_item.file.read()
                    
                    response = app.upload(file_content, filename)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self._set_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode())
                
                elif parsed_path.path in ['/analyze', '/search']:
                    # Handle JSON requests
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    data = json.loads(post_data.decode('utf-8'))
                    
                    if parsed_path.path == '/analyze':
                        response = app.analyze(
                            query=data.get('query', ''),
                            document_id=data.get('document_id'),
                            use_local_ai=data.get('use_local_ai', True)
                        )
                    else:  # /search
                        response = app.search(
                            document_id=data['document_id'],
                            query=data['query'],
                            top_k=data.get('top_k', 3)
                        )
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self._set_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode())
                
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self._set_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())
            
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Server error: {str(e)}"}).encode())
        
        def log_message(self, format, *args):
            print(f"{self.address_string()} - {format % args}")

    port = int(os.getenv("PORT", 8000))
    server = HTTPServer(('0.0.0.0', port), RequestHandler)
    print(f"🚀 DocQuery FastAPI Backend (Demo Mode) starting on port {port}")
    print(f"📝 Core modules available:")
    print(f"   - DocumentProcessor: {'✓' if DOCUMENT_PROCESSOR_AVAILABLE else '❌'}")
    print(f"   - QueryParser: {'✓' if QUERY_PARSER_AVAILABLE else '❌'}")
    print(f"   - VectorSearch: {'✓' if VECTOR_SEARCH_AVAILABLE else '❌'}")
    print(f"   - LocalAI: {'✓' if LOCAL_AI_AVAILABLE else '❌'}")
    print(f"🌐 Access at: http://localhost:{port}")
    print(f"📚 Endpoints: /upload, /analyze, /search, /health")
    print()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server shutting down...")
        server.shutdown()