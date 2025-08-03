import re
from typing import Dict, Optional, List

class QueryParser:
    """Parses natural language queries to extract structured information."""
    
    def __init__(self):
        # Common patterns for different data types
        self.age_patterns = [
            r'(\d{1,3})\s*(?:year|yr|y)?\s*(?:old|age)',
            r'(\d{1,3})(?:M|F)',  # Common format like "46M"
            r'age\s*:?\s*(\d{1,3})',
            r'(\d{1,3})\s*(?:male|female|man|woman)'
        ]
        
        self.gender_patterns = [
            r'(?:^|\s)(male|female|man|woman|M|F)(?:\s|$|,)',
            r'(\d+)([MF])(?:\s|$|,)',  # Extract from patterns like "46M"
        ]
        
        self.procedure_patterns = [
            r'(?:surgery|procedure|operation|treatment)?\s*(knee|hip|heart|brain|liver|kidney|lung|spine|shoulder|ankle|wrist|back|neck|eye|dental|cardiac|orthopedic|neurological|oncology|cosmetic)\s*(?:surgery|procedure|operation|treatment)',
            r'(knee|hip|heart|brain|liver|kidney|lung|spine|shoulder|ankle|wrist|back|neck|eye|dental|cardiac|orthopedic|neurological|oncology|cosmetic)(?:\s+(?:surgery|procedure|operation|treatment|repair|replacement|implant))',
            r'(?:surgery|procedure|operation|treatment)\s+(?:for|on|of)\s+([a-zA-Z\s]+)',
        ]
        
        self.location_patterns = [
            r'(?:in|at|from|near)\s+([A-Z][a-zA-Z\s]+?)(?:\s*,|$|\s+(?:hospital|clinic|center|medical))',
            r'([A-Z][a-zA-Z\s]+?)\s+(?:hospital|clinic|center|medical)',
            r'(?:^|\s)([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*?)(?:\s*,|\s+\d|\s+policy|$)',
        ]
        
        self.policy_duration_patterns = [
            r'(\d+)\s*(?:month|mon|m)?\s*(?:old|existing|active)?\s*(?:insurance\s*)?policy',
            r'policy\s*(?:of|for)?\s*(\d+)\s*(?:month|mon|m|year|yr|y)',
            r'(\d+)\s*(?:month|mon|m|year|yr|y)\s*(?:old|existing|active)?\s*policy',
            r'(\d+)[\-\s]*(?:month|mon|m|year|yr|y)[\-\s]*(?:old|existing|active)',
        ]
        
        # Enhanced patterns for insurance/legal/HR/compliance domains
        self.medical_condition_patterns = [
            r'(?:with|having|diagnosed with|suffering from)\s+([a-zA-Z\s]+?)(?:\s+for|\s+since|\s*,|$)',
            r'(?:pre[\-\s]*existing|chronic|acute)\s+([a-zA-Z\s]+?)(?:\s+condition|\s*,|$)',
            r'(?:condition|disease|illness|disorder):\s*([a-zA-Z\s]+?)(?:\s*,|$)',
        ]
        
        self.urgency_patterns = [
            r'(?:emergency|urgent|immediate|critical|acute)',
            r'(?:elective|planned|scheduled|routine)',
        ]
        
        self.claim_amount_patterns = [
            r'(?:amount|cost|expense|bill|claim)\s*(?:of|for)?\s*[\$₹€£]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'[\$₹€£]\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:dollars|rupees|euros|pounds|rs|inr)',
        ]
    
    def parse_query(self, query: str) -> Dict[str, Optional[str]]:
        """
        Parse a natural language query to extract structured information.
        
        Args:
            query: Natural language query string
            
        Returns:
            Dictionary containing extracted information
        """
        query_lower = query.lower().strip()
        
        result = {
            'age': self._extract_age(query_lower),
            'gender': self._extract_gender(query, query_lower),
            'procedure': self._extract_procedure(query_lower),
            'location': self._extract_location(query),
            'policy_duration': self._extract_policy_duration(query_lower),
            'medical_condition': self._extract_medical_condition(query_lower),
            'urgency': self._extract_urgency(query_lower),
            'claim_amount': self._extract_claim_amount(query_lower),
            'query_type': self._classify_query_type(query_lower)
        }
        
        return {k: v for k, v in result.items() if v is not None}
    
    def _extract_age(self, query: str) -> Optional[str]:
        """Extract age from query."""
        for pattern in self.age_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                age = int(match.group(1))
                if 0 <= age <= 120:  # Reasonable age range
                    return str(age)
        return None
    
    def _extract_gender(self, original_query: str, query_lower: str) -> Optional[str]:
        """Extract gender from query."""
        for pattern in self.gender_patterns:
            match = re.search(pattern, query_lower, re.IGNORECASE)
            if match:
                gender_text = match.group(1).lower()
                if gender_text in ['m', 'male', 'man']:
                    return 'Male'
                elif gender_text in ['f', 'female', 'woman']:
                    return 'Female'
                elif len(match.groups()) > 1:  # Pattern like "46M"
                    gender_char = match.group(2).upper()
                    if gender_char == 'M':
                        return 'Male'
                    elif gender_char == 'F':
                        return 'Female'
        return None
    
    def _extract_procedure(self, query: str) -> Optional[str]:
        """Extract medical procedure from query."""
        for pattern in self.procedure_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                procedure = match.group(1).strip()
                # Clean up the procedure name
                procedure = re.sub(r'\s+', ' ', procedure)
                return procedure.title()
        
        # Look for common procedure keywords
        procedure_keywords = [
            'surgery', 'operation', 'procedure', 'treatment', 'repair', 
            'replacement', 'implant', 'biopsy', 'transplant', 'removal'
        ]
        
        for keyword in procedure_keywords:
            if keyword in query:
                # Try to extract surrounding context
                pattern = rf'(\w+\s+)*{keyword}(\s+\w+)*'
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    return match.group(0).strip().title()
        
        return None
    
    def _extract_location(self, query: str) -> Optional[str]:
        """Extract location from query."""
        for pattern in self.location_patterns:
            match = re.search(pattern, query)
            if match:
                location = match.group(1).strip()
                # Filter out common false positives
                if location.lower() not in ['old', 'year', 'month', 'policy', 'insurance', 'male', 'female']:
                    return location.title()
        return None
    
    def _extract_policy_duration(self, query: str) -> Optional[str]:
        """Extract policy duration from query."""
        for pattern in self.policy_duration_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                duration = match.group(1)
                # Determine if it's months or years based on context
                if 'year' in match.group(0) or 'yr' in match.group(0):
                    return f"{duration} years"
                else:
                    return f"{duration} months"
        return None
    
    def get_query_summary(self, parsed_query: Dict[str, Optional[str]]) -> str:
        """
        Generate a human-readable summary of the parsed query.
        
        Args:
            parsed_query: Dictionary of parsed query components
            
        Returns:
            Human-readable summary string
        """
        parts = []
        
        if parsed_query.get('age') and parsed_query.get('gender'):
            gender = parsed_query['gender']
            parts.append(f"{parsed_query['age']}-year-old {gender.lower() if gender else 'person'}")
        elif parsed_query.get('age'):
            parts.append(f"{parsed_query['age']} years old")
        elif parsed_query.get('gender'):
            gender = parsed_query['gender']
            parts.append(gender.lower() if gender else 'person')
        
        if parsed_query.get('procedure'):
            procedure = parsed_query['procedure']
            parts.append(f"requiring {procedure.lower() if procedure else 'medical procedure'}")
        
        if parsed_query.get('location'):
            parts.append(f"in {parsed_query['location']}")
        
        if parsed_query.get('policy_duration'):
            parts.append(f"with {parsed_query['policy_duration']} insurance policy")
        
        return ', '.join(parts) if parts else "Query with limited extractable information"
    
    def _extract_medical_condition(self, query: str) -> Optional[str]:
        """Extract pre-existing or mentioned medical conditions."""
        for pattern in self.medical_condition_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                condition = match.group(1).strip()
                # Clean up the condition name
                condition = re.sub(r'\s+', ' ', condition)
                return condition.title()
        return None
    
    def _extract_urgency(self, query: str) -> Optional[str]:
        """Extract urgency level from query."""
        for pattern in self.urgency_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(0).lower()
        return None
    
    def _extract_claim_amount(self, query: str) -> Optional[str]:
        """Extract claim amount from query."""
        for pattern in self.claim_amount_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                amount = match.group(1)
                return amount
        return None
    
    def _classify_query_type(self, query: str) -> str:
        """Classify the type of query for domain-specific handling."""
        query_types = {
            'coverage_inquiry': ['covered', 'coverage', 'eligible', 'include', 'benefit'],
            'claim_submission': ['claim', 'reimbursement', 'submit', 'file', 'process'],
            'policy_details': ['policy', 'terms', 'conditions', 'premium', 'deductible'],
            'pre_authorization': ['pre-auth', 'approval', 'authorization', 'permit'],
            'complaint': ['complaint', 'issue', 'problem', 'dispute', 'unsatisfied'],
            'renewal': ['renew', 'renewal', 'extend', 'continue', 'expires'],
            'legal_compliance': ['legal', 'regulation', 'compliance', 'requirement', 'law'],
            'hr_inquiry': ['employee', 'staff', 'hr', 'human resources', 'benefits']
        }
        
        for query_type, keywords in query_types.items():
            if any(keyword in query for keyword in keywords):
                return query_type
        
        return 'general_inquiry'
