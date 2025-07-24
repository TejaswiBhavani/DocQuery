import os
import json
from typing import Dict, List, Optional
from openai import OpenAI

class OpenAIClient:
    """Handles OpenAI API interactions for document analysis and decision making."""
    
    def __init__(self):
        """Initialize OpenAI client with API key from environment."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("OpenAI API key not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
    
    def analyze_query(self, parsed_query: Dict, relevant_chunks: List[str], original_query: str) -> Dict:
        """
        Analyze query against relevant document chunks using OpenAI.
        
        Args:
            parsed_query: Structured query data extracted from user input
            relevant_chunks: Most relevant document sections from vector search
            original_query: Original user query string
            
        Returns:
            Dictionary containing decision, justification, and other analysis results
        """
        try:
            # Prepare context from relevant chunks
            context = "\n\n".join([f"DOCUMENT SECTION {i+1}:\n{chunk}" for i, chunk in enumerate(relevant_chunks)])
            
            # Create the analysis prompt
            prompt = self._create_analysis_prompt(parsed_query, context, original_query)
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Using gpt-3.5-turbo as specified in requirements
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert policy analyst that reviews insurance policies, contracts, and legal documents. You must provide accurate decisions based on the provided document sections and respond in valid JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1,  # Low temperature for consistent, factual responses
                max_tokens=1000
            )
            
            # Parse and validate response
            response_content = response.choices[0].message.content
            if response_content is None:
                raise Exception("Empty response from OpenAI API")
            result = json.loads(response_content)
            
            # Ensure required fields are present
            validated_result = self._validate_response(result)
            
            return validated_result
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse OpenAI response as JSON: {str(e)}")
        except Exception as e:
            raise Exception(f"OpenAI API call failed: {str(e)}")
    
    def _create_analysis_prompt(self, parsed_query: Dict, context: str, original_query: str) -> str:
        """
        Create a detailed prompt for policy analysis.
        
        Args:
            parsed_query: Structured query information
            context: Relevant document sections
            original_query: Original user query
            
        Returns:
            Formatted prompt string
        """
        # Format parsed query information
        query_details = []
        if parsed_query.get('age'):
            query_details.append(f"Age: {parsed_query['age']}")
        if parsed_query.get('gender'):
            query_details.append(f"Gender: {parsed_query['gender']}")
        if parsed_query.get('procedure'):
            query_details.append(f"Procedure: {parsed_query['procedure']}")
        if parsed_query.get('location'):
            query_details.append(f"Location: {parsed_query['location']}")
        if parsed_query.get('policy_duration'):
            query_details.append(f"Policy Duration: {parsed_query['policy_duration']}")
        
        query_summary = "\n".join(query_details) if query_details else "Limited structured information available"
        
        prompt = f"""
ORIGINAL QUERY: "{original_query}"

EXTRACTED QUERY DETAILS:
{query_summary}

RELEVANT DOCUMENT SECTIONS:
{context}

TASK:
Analyze the query against the provided document sections and determine if the request should be approved or rejected based on the policy terms, conditions, and clauses found in the documents.

ANALYSIS REQUIREMENTS:
1. Carefully review all document sections for relevant terms and conditions
2. Consider factors like coverage periods, excluded procedures, geographic limitations, waiting periods, and eligibility criteria
3. Look for specific clauses that support or contradict the approval of this request
4. If coverage amounts or benefits are mentioned in the documents, include relevant monetary information
5. Base your decision strictly on what is written in the provided document sections

RESPONSE FORMAT:
Respond with a valid JSON object containing exactly these fields:
{{
    "decision": "Approved" or "Rejected",
    "justification": "Detailed explanation of the decision based on policy clauses and terms",
    "clause_reference": "Specific clause numbers, sections, or text from the document that supports the decision",
    "amount": "Monetary amount if applicable (e.g., coverage limit, deductible, payout amount) or null if not applicable",
    "confidence": "High, Medium, or Low - based on clarity of policy terms and relevance of document sections"
}}

Ensure your response is valid JSON and base your analysis strictly on the provided document content.
"""
        
        return prompt
    
    def _validate_response(self, response: Dict) -> Dict:
        """
        Validate and standardize the OpenAI response.
        
        Args:
            response: Raw response from OpenAI
            
        Returns:
            Validated and standardized response
        """
        # Ensure required fields exist
        validated = {
            'decision': response.get('decision', 'Unknown'),
            'justification': response.get('justification', 'No justification provided'),
            'clause_reference': response.get('clause_reference', 'No specific clause referenced'),
            'amount': response.get('amount'),
            'confidence': response.get('confidence', 'Medium')
        }
        
        # Validate decision field
        if validated['decision'] not in ['Approved', 'Rejected', 'Unknown']:
            validated['decision'] = 'Unknown'
        
        # Validate confidence field
        if validated['confidence'] not in ['High', 'Medium', 'Low']:
            validated['confidence'] = 'Medium'
        
        # Ensure strings are not empty
        if not validated['justification'].strip():
            validated['justification'] = 'Decision made based on policy analysis'
        
        if not validated['clause_reference'].strip():
            validated['clause_reference'] = 'General policy terms and conditions'
        
        return validated
    
    def get_api_status(self) -> Dict:
        """
        Check if OpenAI API is accessible and working.
        
        Returns:
            Dictionary with API status information
        """
        try:
            # Make a simple test call
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            return {
                "status": "active",
                "model": "gpt-3.5-turbo",
                "message": "API is functioning normally"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"API error: {str(e)}"
            }
