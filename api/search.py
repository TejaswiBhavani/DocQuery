"""
Vercel serverless function for document search.
Endpoint: /api/search
"""
import os
import sys
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler
import json

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from document_processor import DocumentProcessor
    
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
            
    SEARCH_AVAILABLE = True
except ImportError as e:
    print(f"Import error in search.py: {e}")
    DocumentProcessor = None
    VectorSearch = None
    SEARCH_TYPE = "Search unavailable"
    SEARCH_AVAILABLE = False

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle document search requests"""
        # Set CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        try:
            if not SEARCH_AVAILABLE:
                self.send_response(503)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'error': 'Search functionality not available',
                    'message': 'Required dependencies missing',
                    'status': 503
                }
                self.wfile.write(json.dumps(response).encode())
                return
                
            # Read request data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Parse JSON data
            try:
                data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'error': 'Invalid JSON data', 'status': 400}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Process the search
            response = self.handle_search(data)
            
            self.send_response(200 if response.get('success') else 400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {
                'error': f'Search processing failed: {str(e)}',
                'status': 500
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def handle_search(self, data):
        """Perform search within document content"""
        start_time = time.time()
        
        try:
            # Extract search parameters
            query = data.get('query', '')
            document_text = data.get('document_text', '')
            top_k = data.get('top_k', 3)
            document_id = data.get('document_id', 'unknown')
            
            if not query:
                return {
                    'error': 'No search query provided',
                    'status': 400
                }
                
            if not document_text:
                return {
                    'error': 'No document content provided',
                    'status': 400
                }
            
            # Process document into chunks for search
            processor = DocumentProcessor()
            chunks = processor.chunk_text(document_text)
            
            if not chunks:
                return {
                    'error': 'No searchable content found in document',
                    'status': 400
                }
            
            # Perform search using available method
            relevant_chunks = []
            search_method = "simple_fallback"
            
            try:
                if VectorSearch:
                    # Initialize vector search
                    vector_search = VectorSearch()
                    
                    # Handle different vector search interfaces
                    if hasattr(vector_search, 'build_index'):
                        vector_search.build_index(chunks)
                        if hasattr(vector_search, 'search'):
                            relevant_chunks = vector_search.search(query, k=top_k)
                            search_method = "vector_search"
                    elif hasattr(vector_search, 'add_documents'):
                        vector_search.add_documents(chunks)
                        if hasattr(vector_search, 'search'):
                            relevant_chunks = vector_search.search(query, top_k=top_k)
                            search_method = "enhanced_search"
                    else:
                        # Simple search fallback
                        vector_search.documents = chunks
                        if hasattr(vector_search, 'search'):
                            relevant_chunks = vector_search.search(query, top_k=top_k)
                            search_method = "simple_search"
                            
            except Exception as search_error:
                print(f"Vector search failed: {search_error}")
                # Will fall back to simple search below
                pass
            
            # Fallback to simple keyword matching if vector search failed
            if not relevant_chunks:
                query_words = query.lower().split()
                scored_chunks = []
                
                for chunk in chunks:
                    chunk_lower = chunk.lower()
                    score = sum(1 for word in query_words if word in chunk_lower)
                    if score > 0:
                        scored_chunks.append((score, chunk))
                
                # Sort by relevance score and take top_k
                scored_chunks.sort(reverse=True, key=lambda x: x[0])
                relevant_chunks = [chunk for _, chunk in scored_chunks[:top_k]]
                search_method = "keyword_matching"
                
                # If still no results, take first few chunks
                if not relevant_chunks:
                    relevant_chunks = chunks[:top_k]
                    search_method = "fallback_first_chunks"
            
            # Calculate search statistics
            processing_time = time.time() - start_time
            
            # Format results
            response = {
                'success': True,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'search_results': {
                    'query': query,
                    'document_id': document_id,
                    'relevant_chunks': relevant_chunks,
                    'chunks_found': len(relevant_chunks),
                    'total_chunks_searched': len(chunks)
                },
                'search_metadata': {
                    'search_method': search_method,
                    'search_type': SEARCH_TYPE,
                    'processing_time': f'{processing_time:.3f}s',
                    'top_k_requested': top_k
                },
                'document_stats': {
                    'total_chunks': len(chunks),
                    'total_characters': len(document_text),
                    'average_chunk_size': len(document_text) // len(chunks) if chunks else 0
                },
                'preview': {
                    'first_result': relevant_chunks[0][:200] + '...' if relevant_chunks and len(relevant_chunks[0]) > 200 else relevant_chunks[0] if relevant_chunks else None
                }
            }
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            return {
                'error': f'Search processing failed: {str(e)}',
                'search_metadata': {
                    'processing_time': f'{processing_time:.3f}s',
                    'search_type': SEARCH_TYPE
                },
                'status': 500
            }