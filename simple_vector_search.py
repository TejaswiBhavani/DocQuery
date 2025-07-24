import re
from typing import List, Tuple
from collections import Counter

class SimpleVectorSearch:
    """Simple text-based search as fallback when ML dependencies are not available."""
    
    def __init__(self):
        """Initialize the simple search system."""
        self.document_chunks = []
        self.processed_chunks = []
    
    def build_index(self, document_chunks: List[str]) -> None:
        """
        Build simple search index from document chunks.
        
        Args:
            document_chunks: List of text chunks to index
        """
        if not document_chunks:
            raise Exception("No document chunks provided for indexing")
        
        self.document_chunks = document_chunks
        
        # Preprocess chunks for better text matching
        self.processed_chunks = []
        for chunk in document_chunks:
            processed = self._preprocess_text(chunk)
            self.processed_chunks.append(processed)
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for better matching.
        
        Args:
            text: Input text
            
        Returns:
            Processed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep alphanumeric and spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        return text.strip()
    
    def search(self, query: str, k: int = 3) -> List[str]:
        """
        Search for most relevant document chunks based on query.
        
        Args:
            query: Search query string
            k: Number of top results to return
            
        Returns:
            List of most relevant document chunks
        """
        if not self.document_chunks:
            raise Exception("Index not built. Call build_index() first.")
        
        if not query.strip():
            raise Exception("Query cannot be empty")
        
        # Preprocess query
        processed_query = self._preprocess_text(query)
        query_words = set(processed_query.split())
        
        # Score each chunk
        scores = []
        for i, processed_chunk in enumerate(self.processed_chunks):
            chunk_words = set(processed_chunk.split())
            
            # Calculate similarity score
            intersection = query_words.intersection(chunk_words)
            union = query_words.union(chunk_words)
            
            if len(union) == 0:
                jaccard_score = 0
            else:
                jaccard_score = len(intersection) / len(union)
            
            # Add bonus for exact phrase matches
            phrase_bonus = 0
            if len(processed_query) > 3:  # Only for meaningful queries
                if processed_query in processed_chunk:
                    phrase_bonus = 0.5
            
            # Add bonus for medical/insurance keywords
            medical_keywords = [
                'surgery', 'procedure', 'treatment', 'medical', 'hospital', 
                'insurance', 'policy', 'coverage', 'claim', 'benefit',
                'knee', 'hip', 'heart', 'brain', 'liver', 'kidney'
            ]
            
            keyword_bonus = 0
            for keyword in medical_keywords:
                if keyword in query_words and keyword in chunk_words:
                    keyword_bonus += 0.1
            
            total_score = jaccard_score + phrase_bonus + min(keyword_bonus, 0.3)
            scores.append((total_score, i))
        
        # Sort by score and return top k
        scores.sort(reverse=True, key=lambda x: x[0])
        k = min(k, len(self.document_chunks))
        
        relevant_chunks = []
        for score, idx in scores[:k]:
            if score > 0:  # Only return chunks with some relevance
                relevant_chunks.append(self.document_chunks[idx])
        
        # If no relevant chunks found, return first few chunks
        if not relevant_chunks and self.document_chunks:
            relevant_chunks = self.document_chunks[:k]
        
        return relevant_chunks
    
    def get_similarity_scores(self, query: str, k: int = 3) -> List[Tuple[str, float]]:
        """
        Get similarity scores along with document chunks.
        
        Args:
            query: Search query string
            k: Number of top results to return
            
        Returns:
            List of tuples (chunk, similarity_score)
        """
        relevant_chunks = self.search(query, k)
        
        # For simplicity, assign decreasing scores
        results = []
        for i, chunk in enumerate(relevant_chunks):
            score = max(0.1, 1.0 - (i * 0.2))  # Scores from 1.0 to 0.1
            results.append((chunk, score))
        
        return results
    
    def get_index_stats(self) -> dict:
        """
        Get statistics about the current index.
        
        Returns:
            Dictionary with index statistics
        """
        if not self.document_chunks:
            return {"status": "not_built"}
        
        return {
            "status": "built",
            "total_documents": len(self.document_chunks),
            "search_type": "simple_text_based",
            "index_size": len(self.document_chunks)
        }