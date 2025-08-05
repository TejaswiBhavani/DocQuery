"""
Batch Processor - Handles processing multiple questions efficiently
"""
import asyncio
import time
import logging
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor

# Import existing components
from query_parser import QueryParser
from local_ai_client import LocalAIClient
from openai_client import OpenAIClient

logger = logging.getLogger(__name__)

class BatchProcessor:
    """Handles batch processing of multiple questions against a document."""
    
    def __init__(self, use_openai: bool = False, api_key: Optional[str] = None, max_workers: int = 3):
        """
        Initialize batch processor.
        
        Args:
            use_openai: Whether to use OpenAI or local AI
            api_key: OpenAI API key if using OpenAI
            max_workers: Maximum number of concurrent workers
        """
        self.use_openai = use_openai
        self.max_workers = max_workers
        
        # Initialize AI clients
        if use_openai and api_key:
            self.ai_client = OpenAIClient()
            # Set API key in environment
            import os
            os.environ["OPENAI_API_KEY"] = api_key
        else:
            self.ai_client = LocalAIClient()
        
        # Initialize query parser
        self.query_parser = QueryParser()
        
        logger.info(f"Batch processor initialized with {'OpenAI' if use_openai else 'Local AI'}")
    
    async def process_questions(self, questions: List[str], vector_search, document_chunks: List[str]) -> List[str]:
        """
        Process multiple questions asynchronously.
        
        Args:
            questions: List of questions to process
            vector_search: Vector search instance
            document_chunks: List of document chunks
            
        Returns:
            List of answers corresponding to the questions
        """
        start_time = time.time()
        
        try:
            # Process questions concurrently but with controlled concurrency
            semaphore = asyncio.Semaphore(self.max_workers)
            
            async def process_single_question(question: str) -> str:
                async with semaphore:
                    return await self._process_single_question(question, vector_search, document_chunks)
            
            # Create tasks for all questions
            tasks = [process_single_question(q) for q in questions]
            
            # Execute all tasks concurrently
            answers = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions
            processed_answers = []
            for i, answer in enumerate(answers):
                if isinstance(answer, Exception):
                    logger.error(f"Error processing question {i+1}: {str(answer)}")
                    processed_answers.append(f"Error processing question: {str(answer)}")
                else:
                    processed_answers.append(answer)
            
            processing_time = time.time() - start_time
            logger.info(f"Batch processed {len(questions)} questions in {processing_time:.2f}s")
            
            return processed_answers
            
        except Exception as e:
            logger.error(f"Batch processing failed: {str(e)}")
            # Return error messages for all questions
            return [f"Batch processing error: {str(e)}"] * len(questions)
    
    async def _process_single_question(self, question: str, vector_search, document_chunks: List[str]) -> str:
        """
        Process a single question asynchronously.
        
        Args:
            question: Question to process
            vector_search: Vector search instance
            document_chunks: List of document chunks
            
        Returns:
            Answer string
        """
        try:
            # Parse the question
            parsed_query = self.query_parser.parse_query(question)
            
            # Search for relevant chunks
            relevant_chunks = vector_search.search(question, k=3)
            
            # Get AI analysis
            if asyncio.iscoroutinefunction(self.ai_client.analyze_query):
                analysis_result = await self.ai_client.analyze_query(
                    parsed_query, 
                    relevant_chunks, 
                    question
                )
            else:
                # Run synchronous AI client in thread pool
                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor() as executor:
                    analysis_result = await loop.run_in_executor(
                        executor,
                        self.ai_client.analyze_query,
                        parsed_query,
                        relevant_chunks,
                        question
                    )
            
            # Extract answer from analysis result
            answer = self._extract_answer(analysis_result, question, relevant_chunks)
            
            return answer
            
        except Exception as e:
            logger.error(f"Error processing question '{question}': {str(e)}")
            return f"Error analyzing question: {str(e)}"
    
    def _extract_answer(self, analysis_result: Dict[str, Any], question: str, relevant_chunks: List[str]) -> str:
        """
        Extract a concise answer from the analysis result.
        
        Args:
            analysis_result: Analysis result from AI client
            question: Original question
            relevant_chunks: Relevant document chunks
            
        Returns:
            Formatted answer string
        """
        try:
            if not analysis_result or not isinstance(analysis_result, dict):
                return "Unable to analyze the question due to invalid analysis result."
            
            # Get justification as the main answer
            justification = analysis_result.get('justification', '')
            
            if justification and justification.strip():
                # Clean up the justification
                answer = justification.strip()
                
                # Add specific details if available
                decision = analysis_result.get('decision', '')
                if decision and decision not in answer:
                    if decision.lower() in ['approved', 'covered', 'yes']:
                        answer = f"Yes, {answer.lower()}" if not answer.lower().startswith(('yes', 'no')) else answer
                    elif decision.lower() in ['rejected', 'denied', 'not covered', 'no']:
                        answer = f"No, {answer.lower()}" if not answer.lower().startswith(('yes', 'no')) else answer
                
                # Add amount if relevant
                amount = analysis_result.get('amount')
                if amount and str(amount) not in answer:
                    answer += f" The amount is {amount}."
                
                # Add confidence if low
                confidence = analysis_result.get('confidence', '').lower()
                if confidence == 'low':
                    answer += " (Note: This analysis has low confidence due to limited information)"
                
                return answer
            
            # Fallback: try to construct answer from other fields
            decision = analysis_result.get('decision', '')
            clause_reference = analysis_result.get('clause_reference', '')
            
            if decision:
                answer = f"Based on the policy analysis, the decision is: {decision}."
                if clause_reference:
                    answer += f" This is based on: {clause_reference}"
                return answer
            
            # Last resort: provide generic response based on relevant chunks
            if relevant_chunks:
                return "Based on the document analysis, please refer to the relevant policy sections for detailed information."
            
            return "Unable to find relevant information in the document to answer this question."
            
        except Exception as e:
            logger.error(f"Error extracting answer: {str(e)}")
            return "Error occurred while processing the analysis result."
    
    def process_questions_sync(self, questions: List[str], vector_search, document_chunks: List[str]) -> List[str]:
        """
        Synchronous wrapper for batch processing.
        
        Args:
            questions: List of questions to process
            vector_search: Vector search instance
            document_chunks: List of document chunks
            
        Returns:
            List of answers
        """
        try:
            # Run async function in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.process_questions(questions, vector_search, document_chunks))
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Synchronous batch processing failed: {str(e)}")
            return [f"Processing error: {str(e)}"] * len(questions)


class OptimizedBatchProcessor(BatchProcessor):
    """Optimized version with caching and smarter chunking."""
    
    def __init__(self, use_openai: bool = False, api_key: Optional[str] = None, max_workers: int = 3):
        super().__init__(use_openai, api_key, max_workers)
        self._question_cache = {}
        self._chunk_cache = {}
    
    async def _process_single_question(self, question: str, vector_search, document_chunks: List[str]) -> str:
        """
        Optimized processing with caching.
        """
        # Check cache first
        cache_key = hash(question)
        if cache_key in self._question_cache:
            logger.debug(f"Cache hit for question: {question[:50]}...")
            return self._question_cache[cache_key]
        
        # Process normally
        answer = await super()._process_single_question(question, vector_search, document_chunks)
        
        # Cache result
        self._question_cache[cache_key] = answer
        
        return answer
    
    def clear_cache(self):
        """Clear processing cache."""
        self._question_cache.clear()
        self._chunk_cache.clear()
        logger.info("Processing cache cleared")