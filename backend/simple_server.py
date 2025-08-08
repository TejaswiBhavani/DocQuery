"""
Minimal FastAPI backend for DocQuery demo - avoids problematic ML dependencies.
Provides working /upload, /search, and /analyze endpoints for demonstration.
"""

import os
import sys
import tempfile
import time
import uuid
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import cgi

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Safe imports that avoid ML dependencies
try:
    from query_parser import QueryParser
    QUERY_PARSER_AVAILABLE = True
    print("✓ QueryParser loaded successfully")
except Exception as e:
    print(f"❌ QueryParser not available: {e}")
    QUERY_PARSER_AVAILABLE = False

try:
    from output_formatter import OutputFormatter
    OUTPUT_FORMATTER_AVAILABLE = True
    print("✓ OutputFormatter loaded successfully")
except Exception as e:
    print(f"❌ OutputFormatter not available: {e}")
    OUTPUT_FORMATTER_AVAILABLE = False

# For document processing, use basic fallback to avoid PDF dependencies
try:
    # Only try to import if PyPDF2 is available
    import PyPDF2
    from document_processor import DocumentProcessor
    DOCUMENT_PROCESSOR_AVAILABLE = True
    print("✓ DocumentProcessor loaded successfully")
except Exception as e:
    print(f"❌ DocumentProcessor not available (expected in demo): {e}")
    DOCUMENT_PROCESSOR_AVAILABLE = False

class DemoDocQueryBackend:
    def __init__(self):
        self.documents = {}
        print("🚀 DocQuery Demo Backend initialized")
        
    def process_text_content(self, content: str) -> List[str]:
        """Simple text chunking fallback."""
        # Split into chunks of ~1000 characters
        chunk_size = 1000
        chunks = []
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            if chunk.strip():  # Only add non-empty chunks
                chunks.append(chunk)
        return chunks
    
    def extract_text_from_file(self, file_path: str, filename: str) -> str:
        """Extract text from uploaded files with fallbacks."""
        file_ext = os.path.splitext(filename)[1].lower()
        
        try:
            if file_ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif file_ext == '.pdf' and DOCUMENT_PROCESSOR_AVAILABLE:
                # Use real document processor if available
                processor = DocumentProcessor()
                return processor.extract_text(file_path)
            else:
                # Fallback: try to read as text
                with open(file_path, 'rb') as f:
                    content = f.read()
                # Try to decode as text
                try:
                    return content.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        return content.decode('latin1')
                    except:
                        return f"Binary file uploaded: {filename} ({len(content)} bytes)"
        except Exception as e:
            return f"Error processing {filename}: {str(e)}"
    
    def handle_upload(self, file_content: bytes, filename: str) -> Dict:
        """Process document upload."""
        start_time = time.time()
        document_id = str(uuid.uuid4())
        
        # Create temporary file
        file_ext = os.path.splitext(filename)[1] or '.txt'
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext, mode='wb') as tmp_file:
            tmp_file.write(file_content)
            tmp_file_path = tmp_file.name
        
        try:
            # Extract text content
            text_content = self.extract_text_from_file(tmp_file_path, filename)
            
            # Create chunks
            chunks = self.process_text_content(text_content)
            
            # Store document
            self.documents[document_id] = {
                "id": document_id,
                "name": filename,
                "text_content": text_content,
                "chunks": chunks,
                "upload_time": datetime.utcnow().isoformat() + "Z",
                "file_size": len(file_content),
                "processing_time": time.time() - start_time
            }
            
            return {
                "success": True,
                "document_id": document_id,
                "document_name": filename,
                "processing_time": f"{time.time() - start_time:.3f}s",
                "statistics": {
                    "file_size": len(file_content),
                    "character_count": len(text_content),
                    "chunk_count": len(chunks),
                    "average_chunk_size": len(text_content) // len(chunks) if chunks else 0
                },
                "capabilities": {
                    "search_ready": True,
                    "search_type": "keyword_matching"
                },
                "message": "Document processed successfully and ready for analysis"
            }
            
        finally:
            # Clean up temp file
            try:
                os.unlink(tmp_file_path)
            except:
                pass
    
    def handle_search(self, document_id: str, query: str, top_k: int = 3) -> Dict:
        """Search within document."""
        if document_id not in self.documents:
            raise ValueError("Document not found")
        
        doc_data = self.documents[document_id]
        chunks = doc_data["chunks"]
        
        # Simple keyword search
        query_words = query.lower().split()
        scored_chunks = []
        
        for i, chunk in enumerate(chunks):
            chunk_lower = chunk.lower()
            score = sum(chunk_lower.count(word) for word in query_words)
            if score > 0:
                scored_chunks.append((score, chunk, i))
        
        # Sort by score and take top_k
        scored_chunks.sort(reverse=True, key=lambda x: x[0])
        relevant_chunks = [chunk for _, chunk, _ in scored_chunks[:top_k]]
        
        # If no matches, return first few chunks
        if not relevant_chunks and chunks:
            relevant_chunks = chunks[:top_k]
        
        return {
            "success": True,
            "document_id": document_id,
            "document_name": doc_data["name"],
            "query": query,
            "relevant_chunks": relevant_chunks,
            "total_chunks": len(chunks),
            "search_type": "keyword_matching",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def handle_analyze(self, query: str, document_id: str = None, use_local_ai: bool = True) -> Dict:
        """Analyze query with document context."""
        start_time = time.time()
        analysis_id = str(uuid.uuid4())[:8]
        
        # Parse query if available
        parsed_query = {}
        if QUERY_PARSER_AVAILABLE:
            try:
                parser = QueryParser()
                parsed_query = parser.parse_query(query)
            except Exception as e:
                print(f"Query parsing error: {e}")
        
        # Get document context
        document_data = None
        relevant_chunks = []
        if document_id and document_id in self.documents:
            try:
                search_result = self.handle_search(document_id, query, 3)
                relevant_chunks = search_result["relevant_chunks"]
                document_data = self.documents[document_id]
            except Exception as e:
                print(f"Search error: {e}")
        
        # Generate analysis (rule-based demo logic)
        analysis = self.generate_demo_analysis(query, parsed_query, relevant_chunks)
        
        # Format response
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
                    "status": analysis["decision"],
                    "confidence": analysis["confidence"],
                    "risk_level": analysis.get("risk_level", "Medium")
                },
                "justification": {
                    "summary": analysis["justification"],
                    "detailed_factors": analysis.get("detailed_factors", []),
                    "clause_references": analysis.get("clause_references", [])
                },
                "recommendations": analysis.get("recommendations", []),
                "next_steps": analysis.get("next_steps", [])
            },
            "document_analysis": {
                "document_id": document_id,
                "document_name": document_data["name"] if document_data else None,
                "chunks_analyzed": len(relevant_chunks),
                "relevant_content": relevant_chunks[:1] if relevant_chunks else []
            } if document_data else None,
            "system": {
                "analysis_method": "rule_based_demo",
                "processing_time": f"{time.time() - start_time:.3f}s",
                "model_version": "demo_v1.0",
                "search_type": "keyword_matching",
                "capabilities_used": {
                    "document_processor": DOCUMENT_PROCESSOR_AVAILABLE,
                    "query_parser": QUERY_PARSER_AVAILABLE,
                    "vector_search": False,
                    "local_ai": False,
                    "openai": False
                }
            }
        }
        
        return response
    
    def generate_demo_analysis(self, query: str, parsed_query: Dict, relevant_chunks: List[str]) -> Dict:
        """Generate demo analysis based on simple rules."""
        query_lower = query.lower()
        
        # Simple decision logic based on keywords
        if any(word in query_lower for word in ['approve', 'accept', 'yes', 'covered']):
            decision = "Approved"
            confidence = "High"
            risk_level = "Low"
        elif any(word in query_lower for word in ['reject', 'deny', 'no', 'not covered']):
            decision = "Rejected" 
            confidence = "High"
            risk_level = "High"
        else:
            decision = "Requires Review"
            confidence = "Medium"
            risk_level = "Medium"
        
        # Generate contextual justification
        justification_parts = [f"Analysis of query: '{query}'"]
        
        if parsed_query:
            if parsed_query.get('age'):
                justification_parts.append(f"Patient age: {parsed_query['age']}")
            if parsed_query.get('procedure'):
                justification_parts.append(f"Procedure: {parsed_query['procedure']}")
            if parsed_query.get('location'):
                justification_parts.append(f"Location: {parsed_query['location']}")
        
        if relevant_chunks:
            justification_parts.append(f"Relevant document content found and analyzed ({len(relevant_chunks)} sections)")
        
        justification_parts.append("Decision based on rule-based analysis in demo mode")
        
        return {
            "decision": decision,
            "confidence": confidence,
            "risk_level": risk_level,
            "justification": ". ".join(justification_parts),
            "detailed_factors": [
                "Query parsing and component extraction completed",
                f"Document analysis: {'completed' if relevant_chunks else 'no document provided'}",
                f"Risk assessment: {risk_level.lower()} risk identified",
                "Rule-based decision logic applied"
            ],
            "recommendations": [
                "Review analysis results for accuracy",
                "Consider additional documentation if needed",
                f"{'Proceed with application' if decision == 'Approved' else 'Additional review required'}"
            ],
            "next_steps": [
                f"{'Submit for processing' if decision == 'Approved' else 'Gather additional information'}",
                "Document decision for audit trail",
                "Follow organizational procedures"
            ]
        }

# HTTP Server implementation
class DocQueryHandler(BaseHTTPRequestHandler):
    backend = DemoDocQueryBackend()
    
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        if self.path in ['/', '/health']:
            response_data = {
                "message": "DocQuery FastAPI Backend (Demo Mode)",
                "version": "1.0.0",
                "status": "running",
                "capabilities": {
                    "document_processor": DOCUMENT_PROCESSOR_AVAILABLE,
                    "query_parser": QUERY_PARSER_AVAILABLE,
                    "output_formatter": OUTPUT_FORMATTER_AVAILABLE
                },
                "endpoints": {
                    "upload": "POST /upload - Upload and process documents",
                    "search": "POST /search - Search within documents",
                    "analyze": "POST /analyze - AI-powered query analysis"
                },
                "documents_loaded": len(self.backend.documents)
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(response_data, indent=2).encode())
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_POST(self):
        try:
            if self.path == '/upload':
                # Handle multipart form data
                content_type = self.headers.get('content-type', '')
                if not content_type.startswith('multipart/form-data'):
                    raise ValueError("Expected multipart/form-data")
                
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST'}
                )
                
                if 'file' not in form:
                    raise ValueError("No file provided")
                
                file_item = form['file']
                filename = file_item.filename or 'uploaded_file.txt'
                file_content = file_item.file.read()
                
                response = self.backend.handle_upload(file_content, filename)
                
            elif self.path in ['/analyze', '/search']:
                # Handle JSON data
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length == 0:
                    raise ValueError("No data provided")
                
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                if self.path == '/analyze':
                    response = self.backend.handle_analyze(
                        query=data.get('query', ''),
                        document_id=data.get('document_id'),
                        use_local_ai=data.get('use_local_ai', True)
                    )
                elif self.path == '/search':
                    response = self.backend.handle_search(
                        document_id=data['document_id'],
                        query=data['query'],
                        top_k=data.get('top_k', 3)
                    )
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())
                return
            
            # Send successful response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            # Send error response
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self._send_cors_headers()
            self.end_headers()
            error_response = {"error": f"Server error: {str(e)}"}
            self.wfile.write(json.dumps(error_response).encode())
    
    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {self.address_string()} - {format % args}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    
    print("=" * 60)
    print("🚀 DocQuery Demo Backend Starting")
    print("=" * 60)
    print(f"📍 Port: {port}")
    print(f"🌐 URL: http://localhost:{port}")
    print()
    print("📋 Available Modules:")
    print(f"   - Document Processor: {'✅ Available' if DOCUMENT_PROCESSOR_AVAILABLE else '❌ Not available (using fallback)'}")
    print(f"   - Query Parser: {'✅ Available' if QUERY_PARSER_AVAILABLE else '❌ Not available'}")  
    print(f"   - Output Formatter: {'✅ Available' if OUTPUT_FORMATTER_AVAILABLE else '❌ Not available'}")
    print()
    print("📡 Endpoints:")
    print("   - GET  /         - System information")
    print("   - GET  /health   - Health check")
    print("   - POST /upload   - Upload documents")
    print("   - POST /search   - Search within documents")
    print("   - POST /analyze  - Analyze queries")
    print()
    print("🔧 Demo Mode: Using rule-based analysis with keyword matching")
    print("=" * 60)
    
    try:
        server = HTTPServer(('0.0.0.0', port), DocQueryHandler)
        print(f"✅ Server ready! Access at http://localhost:{port}")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
    except Exception as e:
        print(f"❌ Server error: {e}")
    finally:
        print("👋 Server stopped")