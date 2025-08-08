import os
# Add memory optimization and disable tokenizers parallelism for serverless
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import numpy as np
from typing import List, Optional

# Lazy loading for heavy dependencies
_sentence_transformer_model = None
_faiss_module = None

def get_sentence_transformer():
    """Lazy loading of SentenceTransformer model"""
    global _sentence_transformer_model
    if _sentence_transformer_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            # Use smaller model (80MB instead of 420MB)
            model_name = 'all-MiniLM-L6-v2'
            _sentence_transformer_model = SentenceTransformer(model_name)
        except ImportError:
            raise Exception("sentence-transformers not available")
    return _sentence_transformer_model

def get_faiss():
    """Lazy loading of FAISS module"""
    global _faiss_module
    if _faiss_module is None:
        try:
            import faiss
            _faiss_module = faiss
        except ImportError:
            raise Exception("faiss-cpu not available")
    return _faiss_module

class VectorSearch:
    """Memory-optimized vector search for serverless deployment."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the vector search system with lazy loading.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model_name = model_name
        self.model = None  # Lazy loaded
        self.index = None
        self.document_chunks = []
        self.embeddings = None
    
    def _ensure_model_loaded(self):
        """Ensure the model is loaded when needed"""
        if self.model is None:
            self.model = get_sentence_transformer()
    
    def build_index(self, document_chunks: List[str]) -> None:
        """
        Build FAISS index from document chunks with memory optimization.
        
        Args:
            document_chunks: List of text chunks to index
        """
        if not document_chunks:
            raise Exception("No document chunks provided for indexing")
        
        try:
            # Load model only when needed
            self._ensure_model_loaded()
            faiss = get_faiss()
            
            # Store chunks
            self.document_chunks = document_chunks
            
            # Generate embeddings with memory optimization
            self.embeddings = self.model.encode(
                document_chunks, 
                convert_to_numpy=True,
                show_progress_bar=False,
                batch_size=32  # Smaller batch size for memory efficiency
            )
            
            # Ensure embeddings are float32 for FAISS
            self.embeddings = self.embeddings.astype(np.float32)
            
            # Create FAISS index
            dimension = self.embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(self.embeddings)
            
            # Add embeddings to index
            self.index.add(self.embeddings)
            
        except Exception as e:
            raise Exception(f"Failed to build FAISS index: {str(e)}")
    
    def search(self, query: str, k: int = 3) -> List[str]:
        """
        Search for most relevant document chunks based on query with memory optimization.
        
        Args:
            query: Search query string
            k: Number of top results to return
            
        Returns:
            List of most relevant document chunks
        """
        if self.index is None:
            raise Exception("Index not built. Call build_index() first.")
        
        if not query.strip():
            raise Exception("Query cannot be empty")
        
        try:
            # Ensure model is loaded
            self._ensure_model_loaded()
            faiss = get_faiss()
            
            # Generate query embedding with smaller batch
            query_embedding = self.model.encode(
                [query], 
                convert_to_numpy=True,
                show_progress_bar=False,
                batch_size=1
            ).astype(np.float32)
            
            # Normalize query embedding
            faiss.normalize_L2(query_embedding)
            
            # Search index
            k = min(k, len(self.document_chunks))  # Don't search for more than available
            scores, indices = self.index.search(query_embedding, k)
            
            # Return relevant chunks
            relevant_chunks = []
            for i, idx in enumerate(indices[0]):
                if idx >= 0 and idx < len(self.document_chunks):
                    relevant_chunks.append(self.document_chunks[idx])
            
            return relevant_chunks
            
        except Exception as e:
            raise Exception(f"Search failed: {str(e)}")
    
    def get_similarity_scores(self, query: str, k: int = 3) -> List[tuple]:
        """
        Get similarity scores along with document chunks with memory optimization.
        
        Args:
            query: Search query string
            k: Number of top results to return
            
        Returns:
            List of tuples (chunk, similarity_score)
        """
        if self.index is None:
            raise Exception("Index not built. Call build_index() first.")
        
        try:
            # Ensure model is loaded
            self._ensure_model_loaded()
            faiss = get_faiss()
            
            # Generate query embedding
            query_embedding = self.model.encode(
                [query], 
                convert_to_numpy=True,
                show_progress_bar=False,
                batch_size=1
            ).astype(np.float32)
            
            # Normalize query embedding
            faiss.normalize_L2(query_embedding)
            
            # Search index
            k = min(k, len(self.document_chunks))
            scores, indices = self.index.search(query_embedding, k)
            
            # Return chunks with scores
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx >= 0 and idx < len(self.document_chunks):
                    results.append((self.document_chunks[idx], float(score)))
            
            return results
            
        except Exception as e:
            raise Exception(f"Failed to get similarity scores: {str(e)}")
    
    def get_index_stats(self) -> dict:
        """
        Get statistics about the current index.
        
        Returns:
            Dictionary with index statistics
        """
        if self.index is None:
            return {"status": "not_built"}
        
        return {
            "status": "built",
            "total_documents": len(self.document_chunks),
            "embedding_dimension": self.embeddings.shape[1] if self.embeddings is not None else None,
            "index_size": self.index.ntotal
        }
