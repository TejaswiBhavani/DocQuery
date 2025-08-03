import numpy as np
import re
from typing import List, Tuple, Dict
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from error_codes import SearchException

class EnhancedVectorSearch:
    """Enhanced vector search using TF-IDF and cosine similarity for semantic understanding."""
    
    def __init__(self):
        """Initialize the enhanced search system."""
        self.document_chunks = []
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.processed_chunks = []
    
    def build_index(self, document_chunks: List[str]) -> None:
        """
        Build enhanced search index from document chunks using TF-IDF.
        
        Args:
            document_chunks: List of text chunks to index
        """
        if not document_chunks:
            raise SearchException(
                "SEARCH_INDEX_NOT_BUILT",
                details={"reason": "No document chunks provided"}
            )
        
        self.document_chunks = document_chunks
        
        # Preprocess chunks
        self.processed_chunks = [self._preprocess_text(chunk) for chunk in document_chunks]
        
        # Create TF-IDF vectorizer with enhanced features
        # Adjust parameters based on document collection size
        num_docs = len(self.processed_chunks)
        max_df = min(0.95, max(0.1, num_docs - 1)) if num_docs > 1 else 1.0
        min_df = 1 if num_docs > 1 else 1
        
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=min(10000, num_docs * 100),
            stop_words='english',
            ngram_range=(1, 2) if num_docs < 10 else (1, 3),
            min_df=min_df,
            max_df=max_df,
            lowercase=True,
            sublinear_tf=True
        )
        
        # Fit and transform documents with error handling
        try:
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.processed_chunks)
        except ValueError as e:
            # Fallback for very small document collections
            if "max_df corresponds to" in str(e):
                self.tfidf_vectorizer = TfidfVectorizer(
                    max_features=min(1000, num_docs * 50),
                    stop_words=None,  # Don't use stop words for small collections
                    ngram_range=(1, 1),  # Only unigrams for very small collections
                    min_df=1,
                    max_df=1.0,
                    lowercase=True
                )
                self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.processed_chunks)
            else:
                raise e
    
    def _preprocess_text(self, text: str) -> str:
        """
        Advanced text preprocessing for better semantic understanding.
        
        Args:
            text: Input text
            
        Returns:
            Processed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Expand common medical abbreviations
        medical_expansions = {
            'pts': 'patients', 'pt': 'patient', 'dx': 'diagnosis', 'tx': 'treatment',
            'hx': 'history', 'sx': 'surgery', 'rx': 'prescription', 'yr': 'year',
            'mo': 'month', 'wk': 'week', 'm': 'male', 'f': 'female',
            'hosp': 'hospital', 'clinic': 'clinic', 'med': 'medical'
        }
        
        for abbrev, expansion in medical_expansions.items():
            text = re.sub(rf'\b{abbrev}\b', expansion, text)
        
        # Normalize medical terms
        medical_normalizations = {
            'knee surgery': 'knee_surgery orthopedic_procedure',
            'hip surgery': 'hip_surgery orthopedic_procedure',
            'heart surgery': 'heart_surgery cardiac_procedure',
            'brain surgery': 'brain_surgery neurological_procedure',
            'insurance policy': 'insurance_policy coverage',
            'claim': 'insurance_claim coverage_request'
        }
        
        for term, normalized in medical_normalizations.items():
            text = re.sub(rf'\b{term}\b', normalized, text)
        
        # Remove extra whitespace and special characters
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def search(self, query: str, k: int = 3) -> List[str]:
        """
        Search for most relevant document chunks using semantic similarity.
        
        Args:
            query: Search query string
            k: Number of top results to return
            
        Returns:
            List of most relevant document chunks
        """
        if self.tfidf_matrix is None:
            raise Exception("Index not built. Call build_index() first.")
        
        if not query.strip():
            raise Exception("Query cannot be empty")
        
        # Preprocess and expand query
        processed_query = self._preprocess_text(query)
        expanded_query = self._expand_query_semantically(processed_query)
        
        # Transform query using the fitted vectorizer
        query_vector = self.tfidf_vectorizer.transform([expanded_query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # Get top k most similar documents
        top_indices = similarities.argsort()[-k:][::-1]
        
        # Filter out very low similarity scores
        relevant_chunks = []
        for idx in top_indices:
            if similarities[idx] > 0.05:  # Minimum similarity threshold
                relevant_chunks.append(self.document_chunks[idx])
        
        # If no relevant chunks found with high similarity, use simple keyword matching
        if not relevant_chunks:
            relevant_chunks = self._fallback_keyword_search(query, k)
        
        return relevant_chunks[:k]
    
    def _expand_query_semantically(self, query: str) -> str:
        """
        Expand query with semantically related terms for better matching.
        
        Args:
            query: Processed query
            
        Returns:
            Expanded query with related terms
        """
        # Medical domain expansions
        expansions = {
            'knee_surgery': 'knee surgery orthopedic procedure joint replacement arthroscopy',
            'hip_surgery': 'hip surgery orthopedic procedure joint replacement arthroplasty',
            'heart_surgery': 'heart surgery cardiac procedure cardiovascular operation bypass',
            'brain_surgery': 'brain surgery neurological procedure neurosurgery craniotomy',
            'male': 'male man gentleman',
            'female': 'female woman lady',
            'pune': 'pune maharashtra india location city',
            'mumbai': 'mumbai maharashtra india location city',
            'delhi': 'delhi india location city capital',
            'bangalore': 'bangalore bengaluru karnataka india location city',
            'insurance_policy': 'insurance policy coverage plan benefits',
            'month': 'month months duration period time',
            'year': 'year years duration period time'
        }
        
        expanded_terms = [query]
        query_words = query.split()
        
        for word in query_words:
            if word in expansions:
                expanded_terms.append(expansions[word])
        
        return ' '.join(expanded_terms)
    
    def _fallback_keyword_search(self, query: str, k: int) -> List[str]:
        """
        Fallback keyword-based search when semantic search yields no results.
        
        Args:
            query: Original query
            k: Number of results to return
            
        Returns:
            List of relevant chunks based on keyword matching
        """
        query_words = set(self._preprocess_text(query).split())
        scores = []
        
        for i, chunk in enumerate(self.processed_chunks):
            chunk_words = set(chunk.split())
            intersection = query_words.intersection(chunk_words)
            
            # Calculate keyword overlap score
            if len(query_words) > 0:
                score = len(intersection) / len(query_words)
                scores.append((score, i))
        
        # Sort by score and return top k
        scores.sort(reverse=True, key=lambda x: x[0])
        
        relevant_chunks = []
        for score, idx in scores[:k]:
            if score > 0:
                relevant_chunks.append(self.document_chunks[idx])
        
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
        if self.tfidf_matrix is None:
            raise Exception("Index not built. Call build_index() first.")
        
        processed_query = self._preprocess_text(query)
        expanded_query = self._expand_query_semantically(processed_query)
        
        query_vector = self.tfidf_vectorizer.transform([expanded_query])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        top_indices = similarities.argsort()[-k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.05:
                results.append((self.document_chunks[idx], float(similarities[idx])))
        
        return results
    
    def get_index_stats(self) -> Dict:
        """
        Get statistics about the current index.
        
        Returns:
            Dictionary with index statistics
        """
        if self.tfidf_matrix is None:
            return {"status": "not_built"}
        
        return {
            "status": "built",
            "total_documents": len(self.document_chunks),
            "search_type": "enhanced_tfidf_semantic",
            "vocabulary_size": len(self.tfidf_vectorizer.vocabulary_) if self.tfidf_vectorizer else 0,
            "feature_matrix_shape": self.tfidf_matrix.shape
        }