"""
Enhanced output formatter for LLM-powered document analysis system.
Provides structured JSON responses with domain-specific formatting.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

class OutputFormatter:
    """Formats analysis results into structured, comprehensive JSON responses."""
    
    def __init__(self):
        self.schema_version = "1.0"
    
    def format_analysis_result(self, 
                             result: Dict[str, Any], 
                             parsed_query: Dict[str, Any],
                             original_query: str,
                             document_metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Format analysis result into comprehensive structured JSON.
        
        Args:
            result: Raw analysis result from AI client
            parsed_query: Parsed query components
            original_query: Original user query
            document_metadata: Metadata about analyzed documents
            
        Returns:
            Structured JSON response
        """
        
        # Generate unique analysis ID
        analysis_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Base response structure
        formatted_response = {
            "analysis_id": analysis_id,
            "timestamp": timestamp,
            "schema_version": self.schema_version,
            "query": {
                "original": original_query,
                "parsed_components": parsed_query,
                "type": result.get("query_type", "general_inquiry"),
                "domain": self._determine_domain(parsed_query, result)
            },
            "analysis": {
                "decision": {
                    "status": result.get("decision", "Unknown"),
                    "confidence": result.get("confidence", "Medium"),
                    "risk_level": result.get("risk_level", "Medium")
                },
                "justification": {
                    "summary": result.get("justification", ""),
                    "detailed_factors": self._extract_detailed_factors(result),
                    "clause_references": self._format_clause_references(result)
                },
                "financial": {
                    "estimated_amount": result.get("amount"),
                    "currency": self._detect_currency(result.get("amount")),
                    "amount_status": self._determine_amount_status(result)
                },
                "recommendations": result.get("recommendations", []),
                "next_steps": result.get("next_steps", [])
            },
            "system": {
                "analysis_method": result.get("analysis_method", "Unknown"),
                "processing_time": None,  # Will be populated by caller
                "model_version": "local_ai_v1.0",
                "document_chunks_analyzed": None  # Will be populated by caller
            }
        }
        
        # Add domain-specific enhancements
        domain = formatted_response["query"]["domain"]
        if domain == "insurance":
            formatted_response["analysis"]["insurance_specific"] = self._format_insurance_specific(result, parsed_query)
        elif domain == "legal":
            formatted_response["analysis"]["legal_specific"] = self._format_legal_specific(result, parsed_query)
        elif domain == "hr":
            formatted_response["analysis"]["hr_specific"] = self._format_hr_specific(result, parsed_query)
        
        # Add document metadata if available
        if document_metadata:
            formatted_response["document_context"] = document_metadata
        
        # Add compliance and audit trail
        formatted_response["compliance"] = {
            "data_privacy": "No personal data stored beyond session",
            "processing_location": "Local system",
            "retention_policy": "Analysis results not permanently stored"
        }
        
        return formatted_response
    
    def _determine_domain(self, parsed_query: Dict, result: Dict) -> str:
        """Determine the primary domain of the query."""
        query_type = result.get("query_type", "general_inquiry")
        
        domain_mapping = {
            "coverage_inquiry": "insurance",
            "claim_submission": "insurance",
            "policy_details": "insurance",
            "pre_authorization": "insurance",
            "legal_compliance": "legal",
            "hr_inquiry": "hr",
            "complaint": "customer_service",
            "renewal": "insurance"
        }
        
        return domain_mapping.get(query_type, "general")
    
    def _extract_detailed_factors(self, result: Dict) -> List[Dict]:
        """Extract and format detailed analysis factors."""
        factors = []
        
        # Extract factors from result if available
        if "factors" in result:
            result_factors = result["factors"]
            
            factor_descriptions = {
                "age_compliance": "Age eligibility and compliance",
                "procedure_coverage": "Medical procedure coverage status",
                "geographic_coverage": "Geographic location coverage",
                "policy_validity": "Policy validity and waiting periods",
                "pre_conditions": "Pre-existing conditions impact",
                "claim_amount_validity": "Claim amount within policy limits"
            }
            
            for factor_key, score in result_factors.items():
                if isinstance(score, (int, float)):
                    factors.append({
                        "factor": factor_descriptions.get(factor_key, factor_key),
                        "score": score,
                        "impact": "positive" if score > 0 else "negative" if score < 0 else "neutral",
                        "weight": abs(score)
                    })
        
        return factors
    
    def _format_clause_references(self, result: Dict) -> List[Dict]:
        """Format clause and document references."""
        references = []
        
        clause_ref = result.get("clause_reference")
        if clause_ref:
            references.append({
                "type": "policy_clause",
                "reference": clause_ref,
                "relevance": "high"
            })
        
        return references
    
    def _detect_currency(self, amount_str: Optional[str]) -> str:
        """Detect currency from amount string."""
        if not amount_str:
            return "unknown"
        
        currency_symbols = {
            "$": "USD",
            "₹": "INR", 
            "€": "EUR",
            "£": "GBP"
        }
        
        for symbol, currency in currency_symbols.items():
            if symbol in amount_str:
                return currency
        
        # Check for currency words
        if any(word in amount_str.lower() for word in ["rupees", "rs", "inr"]):
            return "INR"
        elif any(word in amount_str.lower() for word in ["dollars", "usd"]):
            return "USD"
        
        return "unknown"
    
    def _determine_amount_status(self, result: Dict) -> str:
        """Determine the status of the claim amount."""
        factors = result.get("factors", {})
        amount_validity = factors.get("claim_amount_validity", 0)
        
        if amount_validity > 0:
            return "within_limits"
        elif amount_validity < 0:
            return "exceeds_limits"
        else:
            return "needs_verification"
    
    def _format_insurance_specific(self, result: Dict, parsed_query: Dict) -> Dict:
        """Format insurance-specific analysis details."""
        return {
            "coverage_type": self._determine_coverage_type(parsed_query),
            "policy_validation": {
                "age_eligible": self._check_factor_positive(result, "age_compliance"),
                "procedure_covered": self._check_factor_positive(result, "procedure_coverage"),
                "location_valid": self._check_factor_positive(result, "geographic_coverage"),
                "waiting_period_satisfied": self._check_factor_positive(result, "policy_validity")
            },
            "claim_processing": {
                "priority": self._determine_claim_priority(parsed_query),
                "required_documents": self._suggest_required_documents(parsed_query),
                "estimated_processing_time": self._estimate_processing_time(result)
            }
        }
    
    def _format_legal_specific(self, result: Dict, parsed_query: Dict) -> Dict:
        """Format legal-specific analysis details."""
        return {
            "compliance_status": result.get("decision", "Unknown"),
            "legal_framework": "Insurance and Contract Law",
            "risk_assessment": {
                "regulatory_compliance": result.get("risk_level", "Medium"),
                "litigation_risk": "Low" if result.get("decision") == "Compliant" else "Medium"
            },
            "required_actions": result.get("next_steps", [])
        }
    
    def _format_hr_specific(self, result: Dict, parsed_query: Dict) -> Dict:
        """Format HR-specific analysis details."""
        return {
            "eligibility_status": result.get("decision", "Unknown"),
            "employee_benefits": {
                "health_insurance": "evaluated" if parsed_query.get("procedure") else "not_applicable",
                "leave_policy": "not_evaluated",
                "reimbursement": "evaluated" if parsed_query.get("claim_amount") else "not_applicable"
            },
            "policy_compliance": {
                "handbook_reference": result.get("clause_reference"),
                "approval_required": result.get("decision") != "Eligible"
            }
        }
    
    def _determine_coverage_type(self, parsed_query: Dict) -> str:
        """Determine the type of insurance coverage."""
        procedure = parsed_query.get("procedure", "").lower()
        
        if any(term in procedure for term in ["surgery", "operation"]):
            return "surgical"
        elif any(term in procedure for term in ["emergency", "urgent"]):
            return "emergency"
        elif any(term in procedure for term in ["diagnostic", "test", "scan"]):
            return "diagnostic"
        else:
            return "general_medical"
    
    def _check_factor_positive(self, result: Dict, factor_name: str) -> bool:
        """Check if a specific factor has a positive score."""
        factors = result.get("factors", {})
        return factors.get(factor_name, 0) > 0
    
    def _determine_claim_priority(self, parsed_query: Dict) -> str:
        """Determine claim processing priority."""
        urgency = parsed_query.get("urgency", "").lower()
        
        if urgency in ["emergency", "urgent", "critical"]:
            return "high"
        elif urgency in ["routine", "elective"]:
            return "low"
        else:
            return "normal"
    
    def _suggest_required_documents(self, parsed_query: Dict) -> List[str]:
        """Suggest required documents based on query type."""
        documents = [
            "Medical prescription/referral",
            "Treatment estimate/bill",
            "Identity proof",
            "Policy document"
        ]
        
        procedure = parsed_query.get("procedure", "").lower()
        if "surgery" in procedure:
            documents.extend([
                "Pre-operative evaluation reports",
                "Surgeon's recommendation letter",
                "Hospital admission details"
            ])
        
        if parsed_query.get("medical_condition"):
            documents.append("Medical history and previous treatment records")
        
        return documents
    
    def _estimate_processing_time(self, result: Dict) -> str:
        """Estimate claim processing time based on decision and complexity."""
        decision = result.get("decision", "Unknown")
        
        if decision == "Approved":
            return "3-5 business days"
        elif decision == "Rejected":
            return "1-2 business days"
        else:
            return "7-10 business days"
    
    def export_json(self, formatted_result: Dict, indent: int = 2) -> str:
        """Export formatted result as JSON string."""
        return json.dumps(formatted_result, indent=indent, ensure_ascii=False)
    
    def export_summary(self, formatted_result: Dict) -> Dict:
        """Export a concise summary of the analysis."""
        return {
            "analysis_id": formatted_result["analysis_id"],
            "decision": formatted_result["analysis"]["decision"]["status"],
            "confidence": formatted_result["analysis"]["decision"]["confidence"],
            "domain": formatted_result["query"]["domain"],
            "recommendations_count": len(formatted_result["analysis"]["recommendations"]),
            "next_steps_count": len(formatted_result["analysis"]["next_steps"])
        }