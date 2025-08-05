import os
import json
from datetime import datetime
from typing import Dict, List, Optional

class LightweightDatabaseManager:
    """Lightweight in-memory database manager for Vercel deployment."""
    
    def __init__(self):
        """Initialize in-memory storage."""
        self.documents = {}
        self.queries = {}
        self.analysis_results = {}
        self.search_results = {}
        self._doc_counter = 1
        self._query_counter = 1
        self._analysis_counter = 1
        self._search_counter = 1
    
    def save_document(self, filename: str, file_size: int, chunk_count: int, 
                     processing_time: float, search_type: str) -> int:
        """Save document information."""
        doc_id = self._doc_counter
        self._doc_counter += 1
        
        self.documents[doc_id] = {
            'id': doc_id,
            'filename': filename,
            'upload_time': datetime.utcnow().isoformat(),
            'file_size': file_size,
            'chunk_count': chunk_count,
            'processing_time': processing_time,
            'search_type': search_type
        }
        
        return doc_id
    
    def save_query(self, document_id: int, original_query: str, 
                  parsed_query: Dict, processing_time: float) -> int:
        """Save user query information."""
        query_id = self._query_counter
        self._query_counter += 1
        
        self.queries[query_id] = {
            'id': query_id,
            'document_id': document_id,
            'original_query': original_query,
            'parsed_query': parsed_query,
            'processing_time': processing_time,
            'query_time': datetime.utcnow().isoformat()
        }
        
        return query_id
    
    def save_analysis(self, query_id: int, decision: str, amount: str, 
                     justification: str, clause_reference: str, confidence: str,
                     relevant_chunks: List[str], ai_model_used: str, 
                     processing_time: float) -> int:
        """Save AI analysis results."""
        analysis_id = self._analysis_counter
        self._analysis_counter += 1
        
        self.analysis_results[analysis_id] = {
            'id': analysis_id,
            'query_id': query_id,
            'decision': decision,
            'amount': amount,
            'justification': justification,
            'clause_reference': clause_reference,
            'confidence': confidence,
            'relevant_chunks': relevant_chunks,
            'ai_model_used': ai_model_used,
            'analysis_time': datetime.utcnow().isoformat(),
            'processing_time': processing_time
        }
        
        return analysis_id
    
    def save_search_results(self, query_id: int, results: List[Dict]) -> List[int]:
        """Save search results."""
        result_ids = []
        
        for result in results:
            result_id = self._search_counter
            self._search_counter += 1
            
            self.search_results[result_id] = {
                'id': result_id,
                'query_id': query_id,
                'document_chunk': result.get('text', ''),
                'similarity_score': result.get('score', 0.0),
                'chunk_index': result.get('index', 0),
                'result_time': datetime.utcnow().isoformat()
            }
            
            result_ids.append(result_id)
        
        return result_ids
    
    def get_document_stats(self) -> Dict:
        """Get document processing statistics."""
        if not self.documents:
            return {
                'total_documents': 0,
                'total_size': 0,
                'avg_processing_time': 0,
                'search_types': {}
            }
        
        total_size = sum(doc['file_size'] for doc in self.documents.values())
        avg_processing = sum(doc['processing_time'] for doc in self.documents.values()) / len(self.documents)
        search_types = {}
        
        for doc in self.documents.values():
            search_type = doc['search_type']
            search_types[search_type] = search_types.get(search_type, 0) + 1
        
        return {
            'total_documents': len(self.documents),
            'total_size': total_size,
            'avg_processing_time': avg_processing,
            'search_types': search_types
        }
    
    def get_query_history(self, limit: int = 10) -> List[Dict]:
        """Get recent query history."""
        sorted_queries = sorted(
            self.queries.values(),
            key=lambda x: x['query_time'],
            reverse=True
        )
        return sorted_queries[:limit]
    
    def close(self):
        """Close database connection (no-op for in-memory storage)."""
        pass

# Try to use full database manager, fallback to lightweight version
try:
    from sqlalchemy import create_engine
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

# For Vercel deployment, always use lightweight manager to avoid size issues
FORCE_LIGHTWEIGHT = os.getenv('VERCEL') == '1' or os.getenv('FORCE_LIGHTWEIGHT_DB') == '1'

if SQLALCHEMY_AVAILABLE and not FORCE_LIGHTWEIGHT:
    # Import the full database manager for local development
    from database_manager_full import DatabaseManager
else:
    # Use lightweight manager for Vercel deployment
    DatabaseManager = LightweightDatabaseManager