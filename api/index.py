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
        """Handle document analysis request with comprehensive processing"""
        import time
        from datetime import datetime
        
        start_time = time.time()
        
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
                processed_content = processor.extract_text(tmp_file_path)
                
                # Create text chunks for better search
                chunks = processor.chunk_text(processed_content)
                
                # Calculate processing statistics
                processing_time = time.time() - start_time
                avg_chunk_size = len(processed_content) // len(chunks) if chunks else 0
                
                # Preview content (first 1000 chars with ellipsis if longer)
                content_preview = processed_content[:1000] + '...' if len(processed_content) > 1000 else processed_content
                
                # Initialize vector search if available
                search_ready = False
                try:
                    if VectorSearch and len(chunks) > 0:
                        vector_search = VectorSearch()
                        vector_search.add_documents(chunks)
                        search_ready = True
                except Exception as search_error:
                    print(f"Vector search initialization failed: {search_error}")
                
                # Comprehensive response
                response = {
                    'success': True,
                    'timestamp': datetime.now().isoformat() + 'Z',
                    'document_analysis': {
                        'document_name': document_name,
                        'processed_content': content_preview,
                        'full_content_length': len(processed_content),
                        'character_count': len(document_text),
                        'chunk_count': len(chunks),
                        'average_chunk_size': avg_chunk_size
                    },
                    'processing_details': {
                        'processing_time': f'{processing_time:.3f}s',
                        'search_type': SEARCH_TYPE,
                        'chunks_created': len(chunks),
                        'search_ready': search_ready,
                        'vector_search_available': VectorSearch is not None
                    },
                    'document_stats': {
                        'total_characters': len(processed_content),
                        'total_words': len(processed_content.split()),
                        'estimated_reading_time': f'{len(processed_content.split()) // 200 + 1} min',
                        'chunk_distribution': {
                            'small_chunks': len([c for c in chunks if len(c) < 500]),
                            'medium_chunks': len([c for c in chunks if 500 <= len(c) < 1500]),
                            'large_chunks': len([c for c in chunks if len(c) >= 1500])
                        }
                    },
                    'capabilities': {
                        'ready_for_queries': True,
                        'semantic_search': search_ready,
                        'vector_analysis': VectorSearch is not None,
                        'advanced_ai': LocalAIClient is not None
                    },
                    'system': {
                        'processor_version': 'vercel_api_v1.0',
                        'search_type': SEARCH_TYPE
                    },
                    'status': 'processed'
                }
                
                return response
                
            finally:
                # Clean up temp file
                os.unlink(tmp_file_path)
                
        except Exception as e:
            processing_time = time.time() - start_time
            return {
                'error': f'Analysis failed: {str(e)}',
                'processing_time': f'{processing_time:.3f}s',
                'system': {
                    'processor_version': 'vercel_api_v1.0'
                },
                'status': 500
            }
    
    def handle_query(self, data):
        """Handle query processing request with enhanced analysis"""
        import time
        import uuid
        from datetime import datetime
        
        start_time = time.time()
        analysis_id = str(uuid.uuid4())[:8]
        
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
            
            # If document is provided, perform full analysis
            if document_text:
                # Process document into chunks for better analysis
                if DocumentProcessor:
                    processor = DocumentProcessor()
                    # Create temporary file for processing
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
                        tmp_file.write(document_text)
                        tmp_file_path = tmp_file.name
                    
                    try:
                        processed_content = processor.extract_text(tmp_file_path)
                        chunks = processor.chunk_text(processed_content)
                    finally:
                        os.unlink(tmp_file_path)
                else:
                    # Simple chunking fallback
                    chunks = [document_text[i:i+2000] for i in range(0, len(document_text), 2000)]
                
                # Perform vector search if available
                relevant_chunks = chunks[:3]  # Use first few chunks as fallback
                try:
                    if VectorSearch and len(chunks) > 0:
                        vector_search = VectorSearch()
                        vector_search.add_documents(chunks)
                        relevant_chunks = vector_search.search(query_text, top_k=3)
                except Exception as search_error:
                    print(f"Vector search failed: {search_error}")
                    # Fallback to first few chunks
                    pass
                
                # Enhanced AI analysis
                ai_client = LocalAIClient()
                
                # Get comprehensive analysis
                analysis = ai_client.analyze_query(parsed_query, relevant_chunks, query_text)
                
                # Extract analysis components with defaults
                decision_status = analysis.get('status', 'Pending Review')
                confidence_level = analysis.get('confidence', 'Medium')
                justification = analysis.get('justification', 'Analysis based on document content and query parameters.')
                
                # Calculate processing time
                processing_time = time.time() - start_time
                
                # Create comprehensive response matching Streamlit format
                response = {
                    'success': True,
                    'analysis_id': analysis_id,
                    'timestamp': datetime.now().isoformat() + 'Z',
                    'query': {
                        'original': query_text,
                        'parsed_components': {
                            key: value for key, value in parsed_query.items() 
                            if value and key in ['age', 'gender', 'procedure', 'location', 'policy_duration', 'query_type']
                        },
                        'domain': parsed_query.get('query_type', 'general')
                    },
                    'analysis': {
                        'decision': {
                            'status': decision_status,
                            'confidence': confidence_level,
                            'risk_level': analysis.get('risk_level', 'Low')
                        },
                        'justification': {
                            'summary': justification,
                            'detailed_factors': analysis.get('detailed_factors', [
                                'Query parameters evaluated against policy terms',
                                'Document content analysis completed',
                                'Risk assessment performed'
                            ]),
                            'clause_references': analysis.get('clause_references', [])
                        },
                        'recommendations': analysis.get('recommendations', [
                            'Review the analysis details for accuracy',
                            'Consider consulting with a policy expert if needed'
                        ]),
                        'next_steps': analysis.get('next_steps', [
                            'Proceed based on the decision status',
                            'Keep documentation for record-keeping'
                        ])
                    },
                    'document_analysis': {
                        'chunks_processed': len(chunks),
                        'relevant_sections': len(relevant_chunks),
                        'content_preview': relevant_chunks[0][:200] + '...' if relevant_chunks else None
                    },
                    'system': {
                        'analysis_method': 'Enhanced Local AI + Vector Search' if VectorSearch else 'Local AI Analysis',
                        'processing_time': f'{processing_time:.3f}s',
                        'model_version': 'vercel_api_v1.0',
                        'search_type': SEARCH_TYPE
                    },
                    'status': 'completed'
                }
                
                return response
            else:
                # Query parsing only
                processing_time = time.time() - start_time
                return {
                    'success': True,
                    'analysis_id': analysis_id,
                    'timestamp': datetime.now().isoformat() + 'Z',
                    'query': {
                        'original': query_text,
                        'parsed_components': {
                            key: value for key, value in parsed_query.items() 
                            if value and key in ['age', 'gender', 'procedure', 'location', 'policy_duration', 'query_type']
                        },
                        'domain': parsed_query.get('query_type', 'general')
                    },
                    'message': 'Query parsed successfully. Upload a document for complete analysis.',
                    'system': {
                        'processing_time': f'{processing_time:.3f}s',
                        'model_version': 'vercel_api_v1.0'
                    },
                    'status': 'parsed'
                }
                
        except Exception as e:
            processing_time = time.time() - start_time
            return {
                'error': f'Query processing failed: {str(e)}',
                'analysis_id': analysis_id,
                'system': {
                    'processing_time': f'{processing_time:.3f}s',
                    'model_version': 'vercel_api_v1.0'
                },
                'status': 500
            }