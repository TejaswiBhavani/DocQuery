import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Optional
from error_codes import SearchException, AIException

class VectorSearch:
    """Handles document embedding generation and FAISS-based semantic search."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the vector search system.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        try:
            self.model = SentenceTransformer(model_name)
            self.index = None
            self.document_chunks = []
            self.embeddings = None
        except Exception as e:
            raise AIException(
                "AI_MODEL_NOT_AVAILABLE",
                details={"model_name": model_name, "original_error": str(e)}
            )
    
    def build_index(self, document_chunks: List[str]) -> None:
        """
        Build FAISS index from document chunks.
        
        Args:
            document_chunks: List of text chunks to index
            
        Raises:
            SearchException: If indexing fails
        """
        if not document_chunks:
            raise SearchException(
                "SEARCH_INDEX_NOT_BUILT",
                details={"reason": "No document chunks provided"}
            )
        
        try:
            # Store chunks
            self.document_chunks = document_chunks
            
            # Generate embeddings
            self.embeddings = self.model.encode(
                document_chunks, 
                convert_to_numpy=True,
                show_progress_bar=False
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
            raise SearchException(
                "SEARCH_INDEX_NOT_BUILT",
                details={"original_error": str(e), "chunk_count": len(document_chunks)}
            )
    
    def search(self, query: str, k: int = 3) -> List[str]:
        """
        Search for most relevant document chunks based on query.
        
        Args:
            query: Search query string
            k: Number of top results to return
            
        Returns:
            List of most relevant document chunks
            
        Raises:
            SearchException: If search fails or index not built
        """
        if self.index is None:
            raise SearchException(
                "SEARCH_INDEX_NOT_BUILT",
                details={"reason": "Index not built, call build_index() first"}
            )
        
        if not query.strip():
            raise SearchException(
                "SEARCH_QUERY_EMPTY",
                details={"query": query}
            )
        
        try:
            # Generate query embedding
            query_embedding = self.model.encode(
                [query], 
                convert_to_numpy=True,
                show_progress_bar=False
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
            
            # Check if we found any results
            if not relevant_chunks:
                raise SearchException(
                    "SEARCH_NO_RESULTS",
                    details={"query": query, "searched_chunks": len(self.document_chunks)}
                )
            
            return relevant_chunks
            
        except SearchException:
            raise  # Re-raise search exceptions
        except Exception as e:
            raise SearchException(
                "SEARCH_INDEX_NOT_BUILT",
                details={"original_error": str(e), "query": query}
            )
    
    def get_similarity_scores(self, query: str, k: int = 3) -> List[tuple]:
        """
        Get similarity scores along with document chunks.
        
        Args:
            query: Search query string
            k: Number of top results to return
            
        Returns:
            List of tuples (chunk, similarity_score)
        """
        if self.index is None:
            raise Exception("Index not built. Call build_index() first.")
        
        try:
            # Generate query embedding
            query_embedding = self.model.encode(
                [query], 
                convert_to_numpy=True,
                show_progress_bar=False
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
