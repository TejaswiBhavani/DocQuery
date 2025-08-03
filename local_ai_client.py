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
            
            # Determine domain-specific analysis approach
            query_type = parsed_query.get('query_type', 'general_inquiry')
            
            if query_type in ['coverage_inquiry', 'claim_submission']:
                decision_info = self._analyze_insurance_coverage(combined_text, parsed_query, original_query)
            elif query_type == 'legal_compliance':
                decision_info = self._analyze_legal_compliance(combined_text, parsed_query, original_query)
            elif query_type == 'hr_inquiry':
                decision_info = self._analyze_hr_benefits(combined_text, parsed_query, original_query)
            else:
                decision_info = self._analyze_decision_context(combined_text, parsed_query, original_query)
            
            # Generate comprehensive structured response
            result = {
                "decision": decision_info["decision"],
                "justification": decision_info["justification"],
                "confidence": decision_info["confidence"],
                "amount": decision_info.get("amount"),
                "clause_reference": decision_info.get("clause_reference"),
                "analysis_method": "Enhanced Local AI + Domain Rules",
                "query_type": query_type,
                "risk_level": decision_info.get("risk_level", "Medium"),
                "recommendations": decision_info.get("recommendations", []),
                "next_steps": decision_info.get("next_steps", [])
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
    
    def _check_age_compliance(self, age: Optional[str], text: str) -> float:
        """Check age compliance for insurance coverage."""
        if not age:
            return 0
        
        try:
            age_num = int(re.search(r'\d+', age).group())
            text_lower = text.lower()
            
            # Look for age-related restrictions
            if "age" in text_lower:
                # Extract age limits from text
                age_limit_pattern = r'(?:minimum|maximum|min|max)\s*age[:\s]*(\d+)'
                matches = re.findall(age_limit_pattern, text_lower)
                
                for limit_str in matches:
                    limit = int(limit_str)
                    if "minimum" in text_lower or "min" in text_lower:
                        if age_num >= limit:
                            return 2  # Meets minimum age
                        else:
                            return -2  # Below minimum age
                    elif "maximum" in text_lower or "max" in text_lower:
                        if age_num <= limit:
                            return 2  # Within maximum age
                        else:
                            return -2  # Exceeds maximum age
            
            # Default age scoring (standard insurance age ranges)
            if 18 <= age_num <= 65:
                return 1  # Standard coverage age
            elif 65 < age_num <= 75:
                return 0  # Senior coverage may have restrictions
            else:
                return -1  # Outside typical coverage age
                
        except (ValueError, AttributeError):
            return 0
    
    def _check_procedure_coverage(self, procedure: Optional[str], text: str) -> float:
        """Check if medical procedure is covered."""
        if not procedure:
            return 0
        
        procedure_lower = procedure.lower()
        text_lower = text.lower()
        
        # Check if procedure is explicitly mentioned
        if procedure_lower in text_lower:
            # Look for coverage context around procedure
            proc_index = text_lower.find(procedure_lower)
            context = text_lower[max(0, proc_index-100):proc_index+100]
            
            coverage_terms = ["covered", "included", "eligible", "benefit"]
            exclusion_terms = ["excluded", "not covered", "denied", "restriction"]
            
            coverage_count = sum(term in context for term in coverage_terms)
            exclusion_count = sum(term in context for term in exclusion_terms)
            
            if coverage_count > exclusion_count:
                return 2
            elif exclusion_count > coverage_count:
                return -2
            else:
                return 0
        
        # Check for general procedure categories
        procedure_categories = {
            "surgery": ["surgical", "operation", "procedure"],
            "emergency": ["emergency", "urgent", "critical"],
            "diagnostic": ["diagnostic", "test", "scan", "examination"]
        }
        
        for category, keywords in procedure_categories.items():
            if any(keyword in procedure_lower for keyword in keywords):
                if category in text_lower:
                    return 1
        
        return 0
    
    def _check_geographic_coverage(self, location: Optional[str], text: str) -> float:
        """Check geographic coverage for the specified location."""
        if not location:
            return 0
        
        location_lower = location.lower()
        text_lower = text.lower()
        
        # Check if location is mentioned
        if location_lower in text_lower:
            # Look for network/coverage terms
            network_terms = ["network", "covered area", "service area", "available"]
            restriction_terms = ["restricted", "not available", "excluded area"]
            
            network_count = sum(term in text_lower for term in network_terms)
            restriction_count = sum(term in text_lower for term in restriction_terms)
            
            if network_count > restriction_count:
                return 2
            elif restriction_count > network_count:
                return -2
        
        # Default geographic coverage assumption
        return 0
    
    def _check_policy_validity(self, duration: Optional[str], text: str) -> float:
        """Check policy validity and waiting periods."""
        if not duration:
            return 0
        
        try:
            duration_match = re.search(r'(\d+)\s*(month|year)', duration.lower())
            if duration_match:
                num = int(duration_match.group(1))
                unit = duration_match.group(2)
                months = num if unit == "month" else num * 12
                
                text_lower = text.lower()
                
                # Look for waiting periods
                waiting_pattern = r'waiting\s*period[:\s]*(\d+)\s*(month|day)'
                waiting_match = re.search(waiting_pattern, text_lower)
                
                if waiting_match:
                    wait_num = int(waiting_match.group(1))
                    wait_unit = waiting_match.group(2)
                    wait_months = wait_num if wait_unit == "month" else wait_num / 30
                    
                    if months > wait_months:
                        return 2  # Past waiting period
                    else:
                        return -2  # Still in waiting period
                
                # Policy age scoring
                if months >= 12:
                    return 1  # Mature policy
                elif months >= 6:
                    return 0  # Moderate policy age
                else:
                    return -1  # New policy
                    
        except (ValueError, AttributeError):
            pass
        
        return 0
    
    def _check_pre_existing_conditions(self, condition: Optional[str], text: str) -> float:
        """Check pre-existing condition coverage."""
        if not condition:
            return 0
        
        condition_lower = condition.lower()
        text_lower = text.lower()
        
        # Look for pre-existing condition clauses
        if "pre-existing" in text_lower or "pre existing" in text_lower:
            if condition_lower in text_lower:
                # Check if condition is covered or excluded
                context_window = 200
                condition_index = text_lower.find(condition_lower)
                if condition_index != -1:
                    context = text_lower[max(0, condition_index-context_window):condition_index+context_window]
                    
                    if any(term in context for term in ["covered", "included", "eligible"]):
                        return 1
                    elif any(term in context for term in ["excluded", "not covered", "denied"]):
                        return -2
            
            # General pre-existing condition penalty
            return -1
        
        return 0
    
    def _check_claim_amount(self, amount: Optional[str], text: str) -> float:
        """Check if claim amount is within policy limits."""
        if not amount:
            return 0
        
        try:
            # Extract numeric amount
            amount_num = float(re.sub(r'[^\d.]', '', amount))
            text_lower = text.lower()
            
            # Look for coverage limits
            limit_patterns = [
                r'(?:maximum|max|limit|cap)[:\s]*[\$₹€£]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'[\$₹€£]\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:maximum|max|limit|cap)'
            ]
            
            for pattern in limit_patterns:
                matches = re.findall(pattern, text_lower)
                for limit_str in matches:
                    limit_amount = float(re.sub(r'[^\d.]', '', limit_str))
                    if amount_num <= limit_amount:
                        return 1  # Within limits
                    else:
                        return -2  # Exceeds limits
            
            # Default scoring based on amount ranges (example for Indian market)
            if amount_num <= 50000:
                return 1  # Small claim
            elif amount_num <= 200000:
                return 0  # Medium claim
            else:
                return -1  # Large claim (may need more scrutiny)
                
        except (ValueError, AttributeError):
            pass
        
        return 0
    
    def _generate_insurance_justification(self, decision: str, factors: Dict, parsed_query: Dict) -> str:
        """Generate detailed insurance-specific justification."""
        
        justification_parts = []
        
        # Decision-specific opening
        if decision == "Approved":
            justification_parts.append("Coverage analysis indicates this claim meets policy requirements.")
        elif decision == "Rejected":
            justification_parts.append("Coverage analysis indicates this claim does not meet policy requirements.")
        else:
            justification_parts.append("This claim requires additional review to determine coverage eligibility.")
        
        # Add factor-specific details
        if factors.get("age_compliance", 0) > 0:
            justification_parts.append("Patient age meets policy eligibility criteria.")
        elif factors.get("age_compliance", 0) < 0:
            justification_parts.append("Patient age may not meet policy eligibility criteria.")
        
        if factors.get("procedure_coverage", 0) > 0:
            justification_parts.append("The requested procedure is covered under the policy.")
        elif factors.get("procedure_coverage", 0) < 0:
            justification_parts.append("The requested procedure may be excluded or have restrictions.")
        
        if factors.get("geographic_coverage", 0) > 0:
            justification_parts.append("Treatment location is within the covered service area.")
        
        if factors.get("policy_validity", 0) > 0:
            justification_parts.append("Policy is in good standing and past any waiting periods.")
        elif factors.get("policy_validity", 0) < 0:
            justification_parts.append("Policy may still be within a waiting period or have validity issues.")
        
        if factors.get("pre_conditions", 0) < 0:
            justification_parts.append("Pre-existing condition clauses may apply.")
        
        if factors.get("claim_amount_validity", 0) > 0:
            justification_parts.append("Claim amount is within policy limits.")
        elif factors.get("claim_amount_validity", 0) < 0:
            justification_parts.append("Claim amount may exceed policy limits.")
        
        return " ".join(justification_parts)
    
    def _generate_insurance_recommendations(self, decision: str, factors: Dict, parsed_query: Dict) -> List[str]:
        """Generate insurance-specific recommendations."""
        
        recommendations = []
        
        if decision == "Approved":
            recommendations.extend([
                "Proceed with claim submission through proper channels",
                "Ensure all required documentation is complete",
                "Verify network provider status for maximum benefits"
            ])
        elif decision == "Rejected":
            recommendations.extend([
                "Review policy terms and conditions for coverage details",
                "Consider alternative treatment options that may be covered",
                "Contact insurance customer service for clarification"
            ])
        else:
            recommendations.extend([
                "Gather additional medical documentation",
                "Obtain pre-authorization if required",
                "Contact insurance provider for coverage confirmation"
            ])
        
        # Factor-specific recommendations
        if factors.get("pre_conditions", 0) < 0:
            recommendations.append("Review pre-existing condition waiting periods and coverage")
        
        if factors.get("claim_amount_validity", 0) < 0:
            recommendations.append("Consider breaking down treatment into phases to stay within limits")
        
        if factors.get("geographic_coverage", 0) <= 0:
            recommendations.append("Verify if treatment can be obtained at a network facility")
        
        return recommendations
    
    def _generate_insurance_next_steps(self, decision: str, parsed_query: Dict) -> List[str]:
        """Generate insurance-specific next steps."""
        
        next_steps = []
        
        if decision == "Approved":
            next_steps.extend([
                "Submit formal claim with all required documents",
                "Keep copies of all medical records and bills",
                "Follow up on claim status within 15-30 days"
            ])
        elif decision == "Rejected":
            next_steps.extend([
                "Request detailed explanation from insurance provider",
                "Consider filing an appeal if decision seems incorrect",
                "Explore alternative funding options for treatment"
            ])
        else:
            next_steps.extend([
                "Contact insurance customer service for guidance",
                "Submit any additional documentation requested",
                "Schedule follow-up review in 5-7 business days"
            ])
        
        # Query-type specific steps
        query_type = parsed_query.get('query_type', 'general_inquiry')
        
        if query_type == 'pre_authorization':
            next_steps.append("Submit pre-authorization request with medical necessity documentation")
        elif query_type == 'claim_submission':
            next_steps.append("Use online portal or mobile app for faster claim processing")
        
        return next_steps
    
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
    
    def _analyze_insurance_coverage(self, text: str, parsed_query: Dict, original_query: str) -> Dict[str, Any]:
        """Domain-specific analysis for insurance coverage queries."""
        
        # Insurance-specific keywords and patterns
        coverage_indicators = {
            "positive": ["covered", "eligible", "included", "benefits", "entitled", "compensated"],
            "negative": ["excluded", "not covered", "denied", "restricted", "limitation", "cap"],
            "conditional": ["subject to", "depends on", "may be covered", "under certain conditions"]
        }
        
        text_lower = text.lower()
        
        # Score based on insurance-specific criteria
        coverage_score = 0
        
        # Check coverage keywords
        for keyword in coverage_indicators["positive"]:
            coverage_score += text_lower.count(keyword) * 2
        
        for keyword in coverage_indicators["negative"]:
            coverage_score -= text_lower.count(keyword) * 3
        
        for keyword in coverage_indicators["conditional"]:
            coverage_score -= text_lower.count(keyword) * 1
        
        # Analyze specific insurance factors
        factors = {
            "age_compliance": self._check_age_compliance(parsed_query.get("age"), text),
            "procedure_coverage": self._check_procedure_coverage(parsed_query.get("procedure"), text),
            "geographic_coverage": self._check_geographic_coverage(parsed_query.get("location"), text),
            "policy_validity": self._check_policy_validity(parsed_query.get("policy_duration"), text),
            "pre_conditions": self._check_pre_existing_conditions(parsed_query.get("medical_condition"), text),
            "claim_amount_validity": self._check_claim_amount(parsed_query.get("claim_amount"), text)
        }
        
        # Calculate final coverage score
        total_score = coverage_score + sum(factors.values())
        
        # Determine decision with insurance-specific logic
        if total_score >= 3:
            decision = "Approved"
            confidence = "High" if total_score >= 5 else "Medium"
            risk_level = "Low"
        elif total_score <= -3:
            decision = "Rejected"
            confidence = "High" if total_score <= -5 else "Medium"
            risk_level = "High"
        else:
            decision = "Requires Review"
            confidence = "Medium"
            risk_level = "Medium"
        
        # Generate insurance-specific justification
        justification = self._generate_insurance_justification(decision, factors, parsed_query)
        
        # Generate recommendations
        recommendations = self._generate_insurance_recommendations(decision, factors, parsed_query)
        
        # Generate next steps
        next_steps = self._generate_insurance_next_steps(decision, parsed_query)
        
        return {
            "decision": decision,
            "justification": justification,
            "confidence": confidence,
            "risk_level": risk_level,
            "amount": self._extract_amount(text),
            "clause_reference": self._find_clause_reference(text),
            "recommendations": recommendations,
            "next_steps": next_steps,
            "factors": factors
        }
    
    def _analyze_legal_compliance(self, text: str, parsed_query: Dict, original_query: str) -> Dict[str, Any]:
        """Domain-specific analysis for legal and compliance queries."""
        
        legal_indicators = {
            "compliant": ["complies", "meets requirements", "in accordance", "conforms", "satisfies"],
            "non_compliant": ["violates", "non-compliance", "breach", "fails to meet", "inadequate"],
            "unclear": ["review required", "unclear", "ambiguous", "interpretation needed"]
        }
        
        text_lower = text.lower()
        compliance_score = 0
        
        for keyword in legal_indicators["compliant"]:
            compliance_score += text_lower.count(keyword) * 2
        
        for keyword in legal_indicators["non_compliant"]:
            compliance_score -= text_lower.count(keyword) * 3
        
        for keyword in legal_indicators["unclear"]:
            compliance_score -= text_lower.count(keyword) * 1
        
        # Legal compliance decision logic
        if compliance_score >= 2:
            decision = "Compliant"
            confidence = "High"
            risk_level = "Low"
        elif compliance_score <= -2:
            decision = "Non-Compliant"
            confidence = "High"  
            risk_level = "High"
        else:
            decision = "Legal Review Required"
            confidence = "Medium"
            risk_level = "Medium"
        
        justification = f"Legal compliance analysis indicates {decision.lower()} status based on available documentation."
        
        recommendations = [
            "Consult with legal counsel for definitive interpretation",
            "Review relevant regulations and guidelines",
            "Document compliance measures taken"
        ]
        
        next_steps = [
            "Schedule legal review meeting",
            "Gather additional documentation if needed",
            "Implement recommended compliance measures"
        ]
        
        return {
            "decision": decision,
            "justification": justification,
            "confidence": confidence,
            "risk_level": risk_level,
            "amount": None,
            "clause_reference": self._find_clause_reference(text),
            "recommendations": recommendations,
            "next_steps": next_steps
        }
    
    def _analyze_hr_benefits(self, text: str, parsed_query: Dict, original_query: str) -> Dict[str, Any]:
        """Domain-specific analysis for HR and employee benefits queries."""
        
        hr_indicators = {
            "eligible": ["eligible", "entitled", "qualified", "included", "covered"],
            "ineligible": ["ineligible", "excluded", "not covered", "restricted", "unavailable"],
            "conditional": ["subject to approval", "depends on", "may qualify", "under review"]
        }
        
        text_lower = text.lower()
        eligibility_score = 0
        
        for keyword in hr_indicators["eligible"]:
            eligibility_score += text_lower.count(keyword) * 2
        
        for keyword in hr_indicators["ineligible"]:
            eligibility_score -= text_lower.count(keyword) * 3
        
        for keyword in hr_indicators["conditional"]:
            eligibility_score -= text_lower.count(keyword) * 1
        
        # HR benefits decision logic
        if eligibility_score >= 2:
            decision = "Eligible"
            confidence = "High"
            risk_level = "Low"
        elif eligibility_score <= -2:
            decision = "Not Eligible"
            confidence = "High"
            risk_level = "Low"
        else:
            decision = "HR Review Required"
            confidence = "Medium"
            risk_level = "Medium"
        
        justification = f"HR benefits analysis indicates {decision.lower()} status based on employee handbook and policies."
        
        recommendations = [
            "Review employee handbook for complete details",
            "Contact HR department for clarification",
            "Verify employment status and tenure requirements"
        ]
        
        next_steps = [
            "Submit formal benefits application if eligible",
            "Schedule meeting with HR representative",
            "Gather required documentation"
        ]
        
        return {
            "decision": decision,
            "justification": justification,
            "confidence": confidence,
            "risk_level": risk_level,
            "amount": self._extract_amount(text),
            "clause_reference": self._find_clause_reference(text),
            "recommendations": recommendations,
            "next_steps": next_steps
        }