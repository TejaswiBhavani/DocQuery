from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import tempfile
import io

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from document_processor import DocumentProcessor
    from query_parser import QueryParser
    from local_ai_client import LocalAIClient
    from database_manager import DatabaseManager
    from dependency_checker import DependencyChecker
    
    # Try to import advanced vector search, fallback to simpler alternatives
    try:
        from vector_search import VectorSearch
        SEARCH_TYPE = "Advanced semantic search with sentence transformers"
    except ImportError:
        try:
            from enhanced_vector_search import EnhancedVectorSearch as VectorSearch
            SEARCH_TYPE = "Enhanced semantic search with TF-IDF"
        except ImportError:
            from simple_vector_search import SimpleVectorSearch as VectorSearch
            SEARCH_TYPE = "Simple text-based search"
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback to minimal functionality
    DocumentProcessor = None
    QueryParser = None
    LocalAIClient = None
    DatabaseManager = None
    DependencyChecker = None
    VectorSearch = None
    SEARCH_TYPE = "Limited functionality"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Handle status check
        if self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Check system status
            if DependencyChecker:
                dep_checker = DependencyChecker()
                capabilities = dep_checker.get_capabilities_summary()
            else:
                capabilities = {
                    'basic_functionality': False,
                    'word_processing': False,
                    'advanced_ai': False,
                    'semantic_search': False
                }
            
            response = {
                'status': 'online',
                'search_type': SEARCH_TYPE,
                'capabilities': capabilities,
                'message': 'DocQuery API is running on Vercel'
            }
            
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Default response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'message': 'DocQuery API',
            'endpoints': [
                '/api/status - Check system status',
                '/api/analyze - Analyze document (POST)',
                '/api/query - Query documents (POST)'
            ]
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        try:
            # Parse JSON data
            data = json.loads(post_data.decode('utf-8'))
            
            if self.path == '/api/analyze':
                response = self.handle_analyze(data)
            elif self.path == '/api/query':
                response = self.handle_query(data)
            else:
                response = {'error': 'Endpoint not found', 'status': 404}
                self.send_response(404)
            
            if response.get('status') != 404:
                self.send_response(200)
            
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {
                'error': f'Server error: {str(e)}',
                'status': 500
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def handle_analyze(self, data):
        """Handle document analysis request"""
        try:
            if not DocumentProcessor:
                return {
                    'error': 'Document processing not available',
                    'message': 'Core dependencies missing',
                    'status': 503
                }
            
            # Get document content from request
            document_text = data.get('document_text', '')
            document_name = data.get('document_name', 'uploaded_document.txt')
            
            if not document_text:
                return {
                    'error': 'No document text provided',
                    'status': 400
                }
            
            # Process the document
            processor = DocumentProcessor()
            
            # Create a temporary file for processing
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
                tmp_file.write(document_text)
                tmp_file_path = tmp_file.name
            
            try:
                processed_content = processor.process_document(tmp_file_path)
                
                return {
                    'success': True,
                    'document_name': document_name,
                    'processed_content': processed_content[:1000] + '...' if len(processed_content) > 1000 else processed_content,
                    'content_length': len(processed_content),
                    'status': 'processed'
                }
            finally:
                # Clean up temp file
                os.unlink(tmp_file_path)
                
        except Exception as e:
            return {
                'error': f'Analysis failed: {str(e)}',
                'status': 500
            }
    
    def handle_query(self, data):
        """Handle query processing request"""
        try:
            if not QueryParser or not LocalAIClient:
                return {
                    'error': 'Query processing not available',
                    'message': 'Core dependencies missing',
                    'status': 503
                }
            
            query_text = data.get('query', '')
            document_text = data.get('document_text', '')
            
            if not query_text:
                return {
                    'error': 'No query provided',
                    'status': 400
                }
            
            # Parse the query
            parser = QueryParser()
            parsed_query = parser.parse_query(query_text)
            
            # If document is provided, analyze it with the query
            if document_text:
                ai_client = LocalAIClient()
                analysis = ai_client.analyze_query(parsed_query, document_text[:5000])  # Limit text for API
                
                return {
                    'success': True,
                    'query': query_text,
                    'parsed_query': parsed_query,
                    'analysis': analysis,
                    'status': 'completed'
                }
            else:
                return {
                    'success': True,
                    'query': query_text,
                    'parsed_query': parsed_query,
                    'message': 'Query parsed successfully. Upload a document for analysis.',
                    'status': 'parsed'
                }
                
        except Exception as e:
            return {
                'error': f'Query processing failed: {str(e)}',
                'status': 500
            }