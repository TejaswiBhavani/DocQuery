"""
Vercel serverless function for document upload and processing.
Endpoint: /api/upload
"""
import os
import sys
import tempfile
import time
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler
import json
import io
import base64

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from document_processor import DocumentProcessor
    from dependency_checker import DependencyChecker
    
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
            
    PROCESSING_AVAILABLE = True
except ImportError as e:
    print(f"Import error in upload.py: {e}")
    DocumentProcessor = None
    DependencyChecker = None
    VectorSearch = None
    SEARCH_TYPE = "Processing unavailable"
    PROCESSING_AVAILABLE = False

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle document upload and processing"""
        # Set CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        try:
            if not PROCESSING_AVAILABLE:
                self.send_response(503)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'error': 'Document processing not available',
                    'message': 'Required dependencies missing',
                    'status': 503
                }
                self.wfile.write(json.dumps(response).encode())
                return
                
            # Read request data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Parse JSON or form data
            try:
                data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json') 
                self.end_headers()
                response = {'error': 'Invalid JSON data', 'status': 400}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Process the upload
            response = self.handle_upload(data)
            
            self.send_response(200 if response.get('success') else 500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {
                'error': f'Upload processing failed: {str(e)}',
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
    
    def handle_upload(self, data):
        """Process document upload with comprehensive analysis"""
        start_time = time.time()
        document_id = str(uuid.uuid4())
        
        try:
            # Extract file data from request
            file_content = data.get('file_content', '')  # Base64 encoded file
            file_name = data.get('file_name', 'uploaded_document.txt')
            document_name = data.get('document_name') or file_name
            
            if not file_content:
                return {
                    'error': 'No file content provided',
                    'status': 400
                }
            
            # Decode base64 file content if provided
            try:
                if file_content.startswith('data:'):
                    # Remove data URL prefix
                    file_content = file_content.split(',')[1]
                
                file_bytes = base64.b64decode(file_content)
                file_size = len(file_bytes)
                
            except Exception as decode_error:
                # Fallback: treat as plain text
                file_bytes = file_content.encode('utf-8')
                file_size = len(file_bytes)
            
            # Create temporary file with proper extension
            file_extension = os.path.splitext(file_name)[1] or '.txt'
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                tmp_file.write(file_bytes)
                tmp_file_path = tmp_file.name
            
            try:
                # Process document using existing module
                processor = DocumentProcessor()
                text_content = processor.extract_text(tmp_file_path)
                chunks = processor.chunk_text(text_content)
                
                # Initialize vector search for document
                search_ready = False
                try:
                    if VectorSearch and len(chunks) > 0:
                        vector_search = VectorSearch()
                        # Handle different vector search interfaces
                        if hasattr(vector_search, 'build_index'):
                            vector_search.build_index(chunks)
                        elif hasattr(vector_search, 'add_documents'):
                            vector_search.add_documents(chunks)
                        else:
                            # Simple search fallback
                            vector_search.documents = chunks
                        search_ready = True
                except Exception as search_error:
                    print(f"Vector search setup warning: {search_error}")
                    search_ready = False
                
                # Calculate processing statistics
                processing_time = time.time() - start_time
                avg_chunk_size = len(text_content) // len(chunks) if chunks else 0
                
                # Content preview for response
                content_preview = text_content[:500] + '...' if len(text_content) > 500 else text_content
                
                # Success response
                response = {
                    'success': True,
                    'document_id': document_id,
                    'document_name': document_name,
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'processing_time': f'{processing_time:.3f}s',
                    'document_analysis': {
                        'content_preview': content_preview,
                        'character_count': len(text_content),
                        'chunk_count': len(chunks),
                        'average_chunk_size': avg_chunk_size,
                        'file_size': file_size
                    },
                    'capabilities': {
                        'search_ready': search_ready,
                        'search_type': SEARCH_TYPE,
                        'vector_search_available': VectorSearch is not None
                    },
                    'statistics': {
                        'total_words': len(text_content.split()),
                        'estimated_reading_time': f'{len(text_content.split()) // 200 + 1} min',
                        'chunk_distribution': {
                            'small_chunks': len([c for c in chunks if len(c) < 500]),
                            'medium_chunks': len([c for c in chunks if 500 <= len(c) < 1500]),
                            'large_chunks': len([c for c in chunks if len(c) >= 1500])
                        }
                    },
                    'message': 'Document uploaded and processed successfully'
                }
                
                return response
                
            finally:
                # Clean up temporary file
                os.unlink(tmp_file_path)
                
        except Exception as e:
            processing_time = time.time() - start_time
            return {
                'error': f'Document processing failed: {str(e)}',
                'document_id': document_id,
                'processing_time': f'{processing_time:.3f}s',
                'status': 500
            }