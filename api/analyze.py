"""
Vercel serverless function for AI-powered query analysis.
Endpoint: /api/analyze
"""
import os
import sys
import time
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler
import json

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from document_processor import DocumentProcessor
    from query_parser import QueryParser
    from local_ai_client import LocalAIClient
    from openai_client import OpenAIClient
    
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
            
    ANALYSIS_AVAILABLE = True
    LOCAL_AI_AVAILABLE = LocalAIClient is not None
    OPENAI_AVAILABLE = OpenAIClient is not None
    
except ImportError as e:
    print(f"Import error in analyze.py: {e}")
    DocumentProcessor = None
    QueryParser = None
    LocalAIClient = None
    OpenAIClient = None
    VectorSearch = None
    SEARCH_TYPE = "Analysis unavailable"
    ANALYSIS_AVAILABLE = False
    LOCAL_AI_AVAILABLE = False
    OPENAI_AVAILABLE = False

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle AI analysis requests"""
        # Set CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        try:
            if not ANALYSIS_AVAILABLE:
                self.send_response(503)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'error': 'Analysis functionality not available',
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
            
            # Process the analysis
            response = self.handle_analysis(data)
            
            self.send_response(200 if response.get('success') else 400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {
                'error': f'Analysis processing failed: {str(e)}',
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
    
    def handle_analysis(self, data):
        """Perform comprehensive AI analysis of query against document"""
        start_time = time.time()
        analysis_id = str(uuid.uuid4())[:8]
        
        try:
            # Extract analysis parameters
            query = data.get('query', '')
            document_text = data.get('document_text', '')
            use_local_ai = data.get('use_local_ai', True)
            document_id = data.get('document_id', 'unknown')
            openai_api_key = data.get('openai_api_key', '')
            
            if not query:
                return {
                    'error': 'No query provided for analysis',
                    'status': 400
                }
            
            # Parse the query using existing module
            parser = QueryParser()
            parsed_query = parser.parse_query(query)
            
            # Process document and find relevant chunks if provided
            relevant_chunks = []
            document_stats = {}
            
            if document_text:
                processor = DocumentProcessor()
                chunks = processor.chunk_text(document_text)
                document_stats = {
                    'total_chunks': len(chunks),
                    'total_characters': len(document_text),
                    'average_chunk_size': len(document_text) // len(chunks) if chunks else 0
                }
                
                # Find relevant chunks using search
                try:
                    if VectorSearch and len(chunks) > 0:
                        vector_search = VectorSearch()
                        
                        # Handle different vector search interfaces
                        if hasattr(vector_search, 'build_index'):
                            vector_search.build_index(chunks)
                            if hasattr(vector_search, 'search'):
                                relevant_chunks = vector_search.search(query, k=3)
                        elif hasattr(vector_search, 'add_documents'):
                            vector_search.add_documents(chunks)
                            if hasattr(vector_search, 'search'):
                                relevant_chunks = vector_search.search(query, top_k=3)
                        else:
                            # Simple search fallback
                            vector_search.documents = chunks
                            if hasattr(vector_search, 'search'):
                                relevant_chunks = vector_search.search(query, top_k=3)
                                
                except Exception as search_error:
                    print(f"Vector search failed in analysis: {search_error}")
                    # Fallback to keyword matching
                    pass
                
                # Fallback to simple search if vector search failed
                if not relevant_chunks:
                    query_words = query.lower().split()
                    scored_chunks = []
                    for chunk in chunks:
                        score = sum(1 for word in query_words if word in chunk.lower())
                        if score > 0:
                            scored_chunks.append((score, chunk))
                    scored_chunks.sort(reverse=True)
                    relevant_chunks = [chunk for _, chunk in scored_chunks[:3]]
                    
                    # If still no results, use first few chunks
                    if not relevant_chunks:
                        relevant_chunks = chunks[:3]
            
            # Perform AI analysis
            analysis_result = None
            ai_method = "rule_based_fallback"
            
            # Try Local AI first if requested
            if use_local_ai and LOCAL_AI_AVAILABLE:
                try:
                    local_ai = LocalAIClient()
                    analysis_result = local_ai.analyze_query(parsed_query, relevant_chunks, query)
                    ai_method = "local_ai"
                except Exception as e:
                    print(f"Local AI analysis failed: {e}")
            
            # Try OpenAI if local AI failed or not requested
            elif not use_local_ai and OPENAI_AVAILABLE and openai_api_key:
                try:
                    # Set API key temporarily
                    original_key = os.environ.get('OPENAI_API_KEY')
                    os.environ['OPENAI_API_KEY'] = openai_api_key
                    
                    openai_client = OpenAIClient()
                    analysis_result = openai_client.analyze_query(parsed_query, relevant_chunks, query)
                    ai_method = "openai_gpt"
                    
                    # Restore original API key
                    if original_key:
                        os.environ['OPENAI_API_KEY'] = original_key
                    elif 'OPENAI_API_KEY' in os.environ:
                        del os.environ['OPENAI_API_KEY']
                        
                except Exception as e:
                    print(f"OpenAI analysis failed: {e}")
            
            # Fallback analysis if AI methods failed
            if not analysis_result:
                analysis_result = {
                    "decision": "Requires Manual Review",
                    "confidence": "Medium",
                    "justification": f"Basic analysis completed for query: '{query}'. " + 
                                   ("Document content analyzed. " if document_text else "No document provided. ") +
                                   "Advanced AI analysis unavailable - please review manually.",
                    "recommendations": [
                        "Review the query parameters and document content",
                        "Consider using AI analysis for more detailed insights",
                        "Consult with domain experts if needed"
                    ],
                    "risk_level": "Medium",
                    "next_steps": [
                        "Manual review recommended",
                        "Gather additional information if needed"
                    ]
                }
                ai_method = "rule_based_fallback"
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Create comprehensive response
            response = {
                'success': True,
                'analysis_id': analysis_id,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'query': {
                    'original': query,
                    'parsed_components': {
                        key: value for key, value in parsed_query.items() 
                        if value and key in ['age', 'gender', 'procedure', 'location', 'policy_duration', 'query_type']
                    },
                    'domain': parsed_query.get('query_type', 'general')
                },
                'analysis': {
                    'decision': {
                        'status': analysis_result.get('decision', 'Pending'),
                        'confidence': analysis_result.get('confidence', 'Medium'),
                        'risk_level': analysis_result.get('risk_level', 'Medium')
                    },
                    'justification': {
                        'summary': analysis_result.get('justification', 'Analysis completed'),
                        'detailed_factors': analysis_result.get('detailed_factors', []),
                        'clause_references': analysis_result.get('clause_references', [])
                    },
                    'recommendations': analysis_result.get('recommendations', []),
                    'next_steps': analysis_result.get('next_steps', [])
                },
                'document_analysis': {
                    'document_id': document_id,
                    'chunks_analyzed': len(relevant_chunks),
                    'relevant_content_preview': relevant_chunks[0][:200] + '...' if relevant_chunks else None,
                    'document_stats': document_stats
                } if document_text else None,
                'system': {
                    'analysis_method': ai_method,
                    'processing_time': f'{processing_time:.3f}s',
                    'model_version': 'vercel_api_v1.0',
                    'search_type': SEARCH_TYPE,
                    'capabilities_used': {
                        'local_ai': LOCAL_AI_AVAILABLE and use_local_ai,
                        'openai': OPENAI_AVAILABLE and not use_local_ai and bool(openai_api_key),
                        'vector_search': len(relevant_chunks) > 0,
                        'query_parsing': True
                    }
                }
            }
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            return {
                'error': f'Analysis processing failed: {str(e)}',
                'analysis_id': analysis_id,
                'system': {
                    'processing_time': f'{processing_time:.3f}s',
                    'model_version': 'vercel_api_v1.0'
                },
                'status': 500
            }