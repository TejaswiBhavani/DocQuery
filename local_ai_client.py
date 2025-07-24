"""
Local AI client for document analysis without requiring external API keys.
Uses open-source models that can run locally.
"""
import json
import re
from typing import Dict, List, Any, Optional
import logging

# Try to import transformers for local AI models
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Try to import spacy for enhanced NLP
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

class LocalAIClient:
    """Local AI client that works without external API keys."""
    
    def __init__(self):
        self.sentiment_analyzer = None
        self.summarizer = None
        self.nlp = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize available local models."""
        try:
            if TRANSFORMERS_AVAILABLE:
                # Initialize sentiment analysis model (lightweight)
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    return_all_scores=True
                )
                
                # Initialize summarization model (lightweight)
                self.summarizer = pipeline(
                    "summarization",
                    model="facebook/bart-large-cnn",
                    max_length=150,
                    min_length=50
                )
                
            if SPACY_AVAILABLE:
                try:
                    # Try to load English model
                    self.nlp = spacy.load("en_core_web_sm")
                except OSError:
                    # Model not installed, use basic processing
                    self.nlp = None
                    
        except Exception as e:
            logging.warning(f"Could not initialize some local AI models: {e}")
    
    def analyze_query(self, parsed_query: Dict, relevant_chunks: List[str], original_query: str) -> Dict[str, Any]:
        """
        Analyze query using local AI models and rule-based logic.
        
        Args:
            parsed_query: Parsed query components
            relevant_chunks: Relevant document sections
            original_query: Original user query
            
        Returns:
            Analysis result with decision, justification, etc.
        """
        try:
            # Combine relevant chunks for analysis
            combined_text = " ".join(relevant_chunks[:3])  # Use top 3 chunks
            
            # Extract key information
            decision_info = self._analyze_decision_context(combined_text, parsed_query, original_query)
            
            # Generate structured response
            result = {
                "decision": decision_info["decision"],
                "justification": decision_info["justification"],
                "confidence": decision_info["confidence"],
                "amount": decision_info.get("amount"),
                "clause_reference": decision_info.get("clause_reference"),
                "analysis_method": "Local AI + Rule-based"
            }
            
            return result
            
        except Exception as e:
            # Fallback to basic rule-based analysis
            return self._fallback_analysis(parsed_query, relevant_chunks, original_query)
    
    def _analyze_decision_context(self, text: str, parsed_query: Dict, original_query: str) -> Dict[str, Any]:
        """Analyze decision context using available models and rules."""
        
        # Rule-based analysis for insurance/policy decisions
        decision_keywords = {
            "approve": ["covered", "eligible", "approved", "included", "valid", "within policy"],
            "reject": ["excluded", "not covered", "denied", "invalid", "outside policy", "pre-existing"]
        }
        
        text_lower = text.lower()
        query_lower = original_query.lower()
        
        # Count positive and negative indicators
        approve_score = sum(text_lower.count(keyword) for keyword in decision_keywords["approve"])
        reject_score = sum(text_lower.count(keyword) for keyword in decision_keywords["reject"])
        
        # Analyze specific conditions
        age_factor = self._analyze_age_factor(parsed_query.get("age"), text)
        procedure_factor = self._analyze_procedure_factor(parsed_query.get("procedure"), text)
        location_factor = self._analyze_location_factor(parsed_query.get("location"), text)
        policy_factor = self._analyze_policy_duration(parsed_query.get("policy_duration"), text)
        
        # Calculate overall score
        total_score = approve_score - reject_score + age_factor + procedure_factor + location_factor + policy_factor
        
        # Use sentiment analysis if available
        sentiment_boost = 0
        if self.sentiment_analyzer and TRANSFORMERS_AVAILABLE:
            try:
                sentiment_result = self.sentiment_analyzer(text[:512])  # Limit text length
                if sentiment_result and len(sentiment_result[0]) > 0:
                    # Find positive sentiment score
                    for score_dict in sentiment_result[0]:
                        if score_dict['label'] in ['POSITIVE', 'LABEL_2']:
                            sentiment_boost = score_dict['score'] * 2 - 1  # Convert to -1 to 1 range
                            break
            except Exception as e:
                logging.warning(f"Sentiment analysis failed: {e}")
        
        total_score += sentiment_boost
        
        # Make decision
        if total_score > 0.5:
            decision = "Approved"
            confidence = "High" if total_score > 2 else "Medium"
        elif total_score < -0.5:
            decision = "Rejected" 
            confidence = "High" if total_score < -2 else "Medium"
        else:
            decision = "Under Review"
            confidence = "Low"
        
        # Generate justification
        justification = self._generate_justification(decision, parsed_query, text, {
            "approve_score": approve_score,
            "reject_score": reject_score,
            "age_factor": age_factor,
            "procedure_factor": procedure_factor,
            "location_factor": location_factor,
            "policy_factor": policy_factor
        })
        
        # Extract amount if mentioned
        amount = self._extract_amount(text)
        
        # Find clause reference
        clause_reference = self._find_clause_reference(text)
        
        return {
            "decision": decision,
            "justification": justification,
            "confidence": confidence,
            "amount": amount,
            "clause_reference": clause_reference
        }
    
    def _analyze_age_factor(self, age: Optional[str], text: str) -> float:
        """Analyze age-related factors."""
        if not age:
            return 0
        
        try:
            age_num = int(re.search(r'\d+', age).group()) if re.search(r'\d+', age) else 0
            
            # Look for age-related terms in text
            age_terms = ["age limit", "minimum age", "maximum age", "age restriction"]
            text_lower = text.lower()
            
            for term in age_terms:
                if term in text_lower:
                    # Extract numbers near age terms
                    pattern = f"{term}[^0-9]*(\d+)"
                    match = re.search(pattern, text_lower)
                    if match:
                        limit_age = int(match.group(1))
                        if "minimum" in term and age_num >= limit_age:
                            return 1
                        elif "maximum" in term and age_num <= limit_age:
                            return 1
                        else:
                            return -1
            
            # General age factor (middle age typically better coverage)
            if 25 <= age_num <= 65:
                return 0.2
            else:
                return -0.1
                
        except (ValueError, AttributeError):
            return 0
    
    def _analyze_procedure_factor(self, procedure: Optional[str], text: str) -> float:
        """Analyze procedure-related factors."""
        if not procedure:
            return 0
        
        procedure_lower = procedure.lower()
        text_lower = text.lower()
        
        # Check if procedure is mentioned in text
        if procedure_lower in text_lower:
            # Look for coverage indicators near the procedure
            context_window = 200
            proc_index = text_lower.find(procedure_lower)
            if proc_index != -1:
                context = text_lower[max(0, proc_index-context_window):proc_index+context_window]
                
                positive_terms = ["covered", "included", "eligible", "approved"]
                negative_terms = ["excluded", "not covered", "denied", "restricted"]
                
                pos_count = sum(term in context for term in positive_terms)
                neg_count = sum(term in context for term in negative_terms)
                
                return pos_count - neg_count
        
        return 0
    
    def _analyze_location_factor(self, location: Optional[str], text: str) -> float:
        """Analyze location-related factors."""
        if not location:
            return 0
        
        location_lower = location.lower()
        text_lower = text.lower()
        
        # Check if location is mentioned
        if location_lower in text_lower:
            # Look for network/coverage terms
            network_terms = ["network", "covered area", "service area", "available"]
            
            for term in network_terms:
                if term in text_lower:
                    return 0.5
            
            return 0.2  # Location mentioned but no specific coverage info
        
        return 0
    
    def _analyze_policy_duration(self, duration: Optional[str], text: str) -> float:
        """Analyze policy duration factors."""
        if not duration:
            return 0
        
        try:
            # Extract number of months/years
            duration_match = re.search(r'(\d+)\s*(month|year)', duration.lower())
            if duration_match:
                num = int(duration_match.group(1))
                unit = duration_match.group(2)
                
                months = num if unit == "month" else num * 12
                
                # Look for waiting period or eligibility terms
                text_lower = text.lower()
                waiting_terms = ["waiting period", "eligibility period", "coverage begins"]
                
                for term in waiting_terms:
                    if term in text_lower:
                        # Extract waiting period
                        pattern = f"{term}[^0-9]*(\d+)\s*(month|day)"
                        match = re.search(pattern, text_lower)
                        if match:
                            wait_num = int(match.group(1))
                            wait_unit = match.group(2)
                            wait_months = wait_num if wait_unit == "month" else wait_num / 30
                            
                            if months >= wait_months:
                                return 1  # Past waiting period
                            else:
                                return -1  # Still in waiting period
                
                # General duration factor (longer policies usually better)
                if months >= 12:
                    return 0.3
                elif months >= 6:
                    return 0.1
                else:
                    return -0.2
                    
        except (ValueError, AttributeError):
            pass
        
        return 0
    
    def _generate_justification(self, decision: str, parsed_query: Dict, text: str, factors: Dict) -> str:
        """Generate human-readable justification."""
        
        justification_parts = []
        
        # Decision-specific opening
        if decision == "Approved":
            justification_parts.append("Based on the policy analysis, the claim appears to be eligible for coverage.")
        elif decision == "Rejected":
            justification_parts.append("Based on the policy analysis, the claim does not meet coverage requirements.")
        else:
            justification_parts.append("The claim requires additional review based on the available information.")
        
        # Add specific factors
        if factors["age_factor"] > 0:
            justification_parts.append("Age requirements are satisfied.")
        elif factors["age_factor"] < 0:
            justification_parts.append("Age-related restrictions may apply.")
        
        if factors["procedure_factor"] > 0:
            justification_parts.append("The requested procedure appears to be covered under the policy.")
        elif factors["procedure_factor"] < 0:
            justification_parts.append("The requested procedure may be excluded or restricted.")
        
        if factors["location_factor"] > 0:
            justification_parts.append("The treatment location is within the covered network.")
        
        if factors["policy_factor"] > 0:
            justification_parts.append("Policy duration requirements are met.")
        elif factors["policy_factor"] < 0:
            justification_parts.append("Policy may still be within a waiting period.")
        
        # Add summary
        if len(justification_parts) == 1:
            justification_parts.append("Please review the complete policy terms for detailed coverage information.")
        
        return " ".join(justification_parts)
    
    def _extract_amount(self, text: str) -> Optional[str]:
        """Extract monetary amounts from text."""
        # Pattern for currency amounts
        amount_pattern = r'[\$₹€£]\s*[\d,]+(?:\.\d{2})?|\d+\s*(?:dollars|rupees|euros|pounds)'
        
        matches = re.findall(amount_pattern, text, re.IGNORECASE)
        if matches:
            return matches[0]
        
        return None
    
    def _find_clause_reference(self, text: str) -> Optional[str]:
        """Find clause or section references in text."""
        # Pattern for clause references
        clause_patterns = [
            r'clause\s+\d+[.\d]*',
            r'section\s+\d+[.\d]*',
            r'article\s+\d+[.\d]*',
            r'paragraph\s+\d+[.\d]*'
        ]
        
        for pattern in clause_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def _fallback_analysis(self, parsed_query: Dict, relevant_chunks: List[str], original_query: str) -> Dict[str, Any]:
        """Basic fallback analysis when advanced models are not available."""
        
        # Simple keyword-based analysis
        combined_text = " ".join(relevant_chunks).lower()
        query_lower = original_query.lower()
        
        # Basic decision logic
        positive_keywords = ["covered", "eligible", "approved", "included", "valid"]
        negative_keywords = ["excluded", "not covered", "denied", "invalid", "restricted"]
        
        pos_score = sum(keyword in combined_text for keyword in positive_keywords)
        neg_score = sum(keyword in combined_text for keyword in negative_keywords)
        
        if pos_score > neg_score:
            decision = "Approved"
            confidence = "Medium"
            justification = "Policy language suggests coverage is available for this request."
        elif neg_score > pos_score:
            decision = "Rejected"
            confidence = "Medium"
            justification = "Policy language indicates this request may not be covered."
        else:
            decision = "Under Review"
            confidence = "Low"
            justification = "Insufficient information to make a definitive coverage determination."
        
        return {
            "decision": decision,
            "justification": justification,
            "confidence": confidence,
            "amount": None,
            "clause_reference": None,
            "analysis_method": "Basic Rule-based"
        }
    
    def is_available(self) -> bool:
        """Check if local AI capabilities are available."""
        return True  # Always available with fallback methods
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Get information about available capabilities."""
        return {
            "transformers_models": TRANSFORMERS_AVAILABLE,
            "spacy_nlp": SPACY_AVAILABLE and self.nlp is not None,
            "sentiment_analysis": self.sentiment_analyzer is not None,
            "summarization": self.summarizer is not None,
            "rule_based_analysis": True
        }