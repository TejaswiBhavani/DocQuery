"""
Vercel serverless function for document search with FastAPI integration.
Endpoint: /api/search
"""
import os
import sys
import json
from http.server import BaseHTTPRequestHandler

# Memory optimization
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Import with fallback handling
try:
    from document_processor import DocumentProcessor
    from query_parser import QueryParser
    
    # Try to import optimized vector search
    try:
        from vector_search import VectorSearch
        SEARCH_TYPE = "Optimized semantic search with all-MiniLM-L6-v2"
    except ImportError:
        try:
            from enhanced_vector_search import EnhancedVectorSearch as VectorSearch
            SEARCH_TYPE = "Enhanced TF-IDF search"
        except ImportError:
            from simple_vector_search import SimpleVectorSearch as VectorSearch
            SEARCH_TYPE = "Simple text search"
            
    PROCESSING_AVAILABLE = True
except ImportError as e:
    print(f"Import error in search.py: {e}")
    DocumentProcessor = None
    QueryParser = None
    VectorSearch = None
    SEARCH_TYPE = "Search unavailable"
    PROCESSING_AVAILABLE = False

def semantic_search(query: str, document_chunks: list = None) -> dict:
    """
    Perform semantic search with memory optimization.
    
    Args:
        query: Search query string
        document_chunks: List of document chunks to search in
        
    Returns:
        Dictionary with search results
    """
    if not PROCESSING_AVAILABLE:
        return {
            "error": "Search dependencies not available",
            "results": []
        }
    
    if not document_chunks:
        return {
            "error": "No document content provided",
            "results": []
        }
    
    try:
        # Use optimized vector search with lazy loading
        vector_search = VectorSearch()
        
        # Build index with memory optimization
        vector_search.build_index(document_chunks)
        
        # Perform search
        results = vector_search.search(query, k=3)
        
        return {
            "query": query,
            "results": results,
            "search_method": SEARCH_TYPE,
            "total_chunks_searched": len(document_chunks)
        }
        
    except Exception as e:
        # Fallback to simple text search
        query_words = query.lower().split()
        scored_chunks = []
        
        for chunk in document_chunks:
            chunk_lower = chunk.lower()
            score = sum(1 for word in query_words if word in chunk_lower)
            if score > 0:
                scored_chunks.append((score, chunk))
        
        # Sort by relevance score and take top 3
        scored_chunks.sort(reverse=True, key=lambda x: x[0])
        results = [chunk for _, chunk in scored_chunks[:3]]
        
        return {
            "query": query,
            "results": results,
            "search_method": "Fallback keyword matching",
            "total_chunks_searched": len(document_chunks),
            "fallback_reason": str(e)
        }

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle document search requests"""
        # Set CORS headers
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        try:
            # Read request data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Parse JSON data
            data = json.loads(post_data.decode('utf-8'))
            query = data.get('query', '')
            document_text = data.get('document_text', '')
            
            if not query:
                response = {
                    'error': 'No search query provided',
                    'status': 400
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            if not document_text:
                response = {
                    'error': 'No document content provided',
                    'status': 400
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Process document into chunks for search
            if PROCESSING_AVAILABLE:
                processor = DocumentProcessor()
                chunks = processor.chunk_text(document_text)
            else:
                # Simple fallback chunking
                chunks = [document_text[i:i+1000] for i in range(0, len(document_text), 1000)]
            
            # Parse query if parser is available
            parsed_query = None
            if PROCESSING_AVAILABLE and QueryParser:
                try:
                    parser = QueryParser()
                    parsed_query = parser.parse_query(query)
                except:
                    parsed_query = {"original": query}
            
            # Perform search
            search_results = semantic_search(query, chunks)
            
            # Format response according to problem statement
            response = {
                "query": query,
                "parsed_components": parsed_query,
                "results": search_results["results"],
                "search_metadata": {
                    "search_method": search_results["search_method"],
                    "total_chunks_searched": search_results["total_chunks_searched"],
                    "chunks_found": len(search_results["results"])
                },
                "success": True
            }
            
            if "fallback_reason" in search_results:
                response["search_metadata"]["fallback_reason"] = search_results["fallback_reason"]
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
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