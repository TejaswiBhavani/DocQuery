"""
Comprehensive test suite for the enhanced LLM-powered DocQuery system.
Tests real-world scenarios across insurance, legal, HR, and compliance domains.
"""

import json
import time
from typing import Dict, List, Any
from document_processor import DocumentProcessor
from enhanced_vector_search import EnhancedVectorSearch
from query_parser import QueryParser
from local_ai_client import LocalAIClient
from output_formatter import OutputFormatter

class DocQueryTestSuite:
    """Comprehensive test suite for document query system."""
    
    def __init__(self):
        self.processor = DocumentProcessor()
        self.search = EnhancedVectorSearch()
        self.parser = QueryParser()
        self.ai_client = LocalAIClient()
        self.formatter = OutputFormatter()
        self.test_results = []
    
    def setup_test_environment(self, document_path: str = "sample_health_insurance_policy.txt"):
        """Set up the test environment with a sample document."""
        print(f"Setting up test environment with document: {document_path}")
        
        # Process document
        text = self.processor.extract_text(document_path)
        chunks = self.processor.chunk_text(text, chunk_size=500, overlap=100)
        
        # Build search index
        self.search.build_index(chunks)
        
        print(f"✅ Document processed: {len(chunks)} chunks created")
        return len(chunks)
    
    def run_test_case(self, test_name: str, query: str, expected_decision: str = None) -> Dict[str, Any]:
        """Run a single test case and return formatted results."""
        print(f"\n🔍 Running test: {test_name}")
        print(f"Query: {query}")
        
        start_time = time.time()
        
        # Parse query
        parsed_query = self.parser.parse_query(query)
        
        # Find relevant chunks
        relevant_chunks = self.search.search(query, k=3)
        
        # Analyze with AI
        analysis_result = self.ai_client.analyze_query(parsed_query, relevant_chunks, query)
        
        # Format output
        processing_time = time.time() - start_time
        analysis_result["processing_time"] = processing_time
        
        formatted_result = self.formatter.format_analysis_result(
            analysis_result, 
            parsed_query, 
            query,
            {
                "document_name": "sample_health_insurance_policy.txt",
                "chunks_analyzed": len(relevant_chunks),
                "search_method": "enhanced_tfidf"
            }
        )
        
        # Add processing time to system info
        formatted_result["system"]["processing_time"] = f"{processing_time:.3f}s"
        formatted_result["system"]["document_chunks_analyzed"] = len(relevant_chunks)
        
        # Validate result if expected decision provided
        decision = formatted_result["analysis"]["decision"]["status"]
        validation_status = "✅ PASS" if expected_decision is None or decision == expected_decision else "❌ FAIL"
        
        print(f"Decision: {decision}")
        print(f"Confidence: {formatted_result['analysis']['decision']['confidence']}")
        print(f"Processing time: {processing_time:.3f}s")
        print(f"Validation: {validation_status}")
        
        # Store test result
        test_result = {
            "test_name": test_name,
            "query": query,
            "expected_decision": expected_decision,
            "actual_decision": decision,
            "validation_status": validation_status,
            "processing_time": processing_time,
            "formatted_result": formatted_result
        }
        
        self.test_results.append(test_result)
        return test_result
    
    def run_insurance_test_suite(self):
        """Run comprehensive insurance domain test cases."""
        print("\n" + "="*60)
        print("🏥 INSURANCE DOMAIN TEST SUITE")
        print("="*60)
        
        insurance_tests = [
            {
                "name": "Basic Coverage Query",
                "query": "46-year-old male needs knee surgery in Mumbai with 3-month policy",
                "expected": "Approved"
            },
            {
                "name": "Emergency Surgery",
                "query": "Emergency heart surgery for 35-year-old female, 2-year policy, Mumbai hospital",
                "expected": "Approved"
            },
            {
                "name": "Diagnostic Test Coverage",
                "query": "MRI scan for 55-year-old male with diabetes, 6-month old policy in Delhi",
                "expected": None  # No specific expectation
            },
            {
                "name": "High-Value Claim",
                "query": "Cancer treatment for 42-year-old female, cost 500000 rupees, 18-month policy",
                "expected": None
            },
            {
                "name": "Pre-existing Condition",
                "query": "Diabetic patient needs surgery, 28-year-old male with 4-month policy in Bangalore",
                "expected": None
            },
            {
                "name": "Elderly Patient Coverage",
                "query": "Hip replacement for 70-year-old female, 5-year policy, Chennai hospital",
                "expected": None
            },
            {
                "name": "Cosmetic Surgery Query",
                "query": "Cosmetic surgery for 30-year-old female, 1-year policy, private clinic Mumbai",
                "expected": None
            }
        ]
        
        for test in insurance_tests:
            self.run_test_case(test["name"], test["query"], test["expected"])
    
    def run_legal_compliance_test_suite(self):
        """Run legal and compliance domain test cases."""
        print("\n" + "="*60)
        print("⚖️ LEGAL & COMPLIANCE TEST SUITE")
        print("="*60)
        
        legal_tests = [
            {
                "name": "Policy Terms Compliance",
                "query": "Does this policy comply with insurance regulations for minimum coverage requirements?",
                "expected": None
            },
            {
                "name": "Age Discrimination Check",
                "query": "Are there any age-based restrictions that might violate anti-discrimination laws?",
                "expected": None
            },
            {
                "name": "Coverage Limitation Legal Review",
                "query": "Legal compliance review of pre-existing condition waiting periods",
                "expected": None
            },
            {
                "name": "Claim Processing Regulation",
                "query": "Does the claim processing timeline meet regulatory requirements?",
                "expected": None
            }
        ]
        
        for test in legal_tests:
            self.run_test_case(test["name"], test["query"], test["expected"])
    
    def run_hr_benefits_test_suite(self):
        """Run HR and employee benefits test cases."""
        print("\n" + "="*60)
        print("👥 HR & EMPLOYEE BENEFITS TEST SUITE")
        print("="*60)
        
        hr_tests = [
            {
                "name": "Employee Health Benefit",
                "query": "Employee health insurance coverage for surgery, 5 years tenure",
                "expected": None
            },
            {
                "name": "Dependent Coverage",
                "query": "Coverage for employee's spouse medical treatment, family policy",
                "expected": None
            },
            {
                "name": "Maternity Benefits",
                "query": "Maternity coverage for female employee, 2-year tenure, normal delivery",
                "expected": None
            },
            {
                "name": "Reimbursement Policy",
                "query": "Medical reimbursement for employee emergency treatment, amount 25000",
                "expected": None
            }
        ]
        
        for test in hr_tests:
            self.run_test_case(test["name"], test["query"], test["expected"])
    
    def run_edge_case_test_suite(self):
        """Run edge cases and stress tests."""
        print("\n" + "="*60)
        print("🔬 EDGE CASES & STRESS TEST SUITE")
        print("="*60)
        
        edge_tests = [
            {
                "name": "Minimal Information Query",
                "query": "Surgery coverage?",
                "expected": None
            },
            {
                "name": "Very Detailed Query",
                "query": "46-year-old male software engineer with diabetes and hypertension needs arthroscopic knee surgery at Apollo Hospital Mumbai under corporate health insurance policy active for 14 months with family floater coverage worth 500000 rupees and seeking pre-authorization for estimated cost of 125000 rupees",
                "expected": None
            },
            {
                "name": "Multiple Procedures",
                "query": "Coverage for knee surgery and heart treatment for 50-year-old patient",
                "expected": None
            },
            {
                "name": "International Treatment",
                "query": "Cancer treatment in USA for Indian policy holder, 3-year policy",
                "expected": None
            },
            {
                "name": "Ambiguous Query",
                "query": "Is this covered or not? Need urgent help with medical situation.",
                "expected": None
            }
        ]
        
        for test in edge_tests:
            self.run_test_case(test["name"], test["query"], test["expected"])
    
    def run_comprehensive_test_suite(self):
        """Run all test suites and generate comprehensive report."""
        print("🚀 Starting Comprehensive DocQuery Test Suite")
        print("="*80)
        
        # Setup test environment
        chunk_count = self.setup_test_environment()
        
        # Run all test suites
        self.run_insurance_test_suite()
        self.run_legal_compliance_test_suite()
        self.run_hr_benefits_test_suite()
        self.run_edge_case_test_suite()
        
        # Generate final report
        self.generate_test_report()
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if "✅ PASS" in result["validation_status"])
        failed_tests = total_tests - passed_tests
        
        # Calculate performance metrics
        avg_processing_time = sum(result["processing_time"] for result in self.test_results) / total_tests
        max_processing_time = max(result["processing_time"] for result in self.test_results)
        min_processing_time = min(result["processing_time"] for result in self.test_results)
        
        # Decision distribution
        decisions = [result["actual_decision"] for result in self.test_results]
        decision_counts = {}
        for decision in decisions:
            decision_counts[decision] = decision_counts.get(decision, 0) + 1
        
        print(f"📈 TEST SUMMARY:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n⏱️ PERFORMANCE METRICS:")
        print(f"   Average Processing Time: {avg_processing_time:.3f}s")
        print(f"   Max Processing Time: {max_processing_time:.3f}s")
        print(f"   Min Processing Time: {min_processing_time:.3f}s")
        
        print(f"\n🎯 DECISION DISTRIBUTION:")
        for decision, count in decision_counts.items():
            percentage = (count/total_tests)*100
            print(f"   {decision}: {count} ({percentage:.1f}%)")
        
        print(f"\n📋 DETAILED TEST RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            print(f"   {i:2d}. {result['test_name']}: {result['actual_decision']} ({result['processing_time']:.3f}s)")
        
        # Export detailed results
        self.export_test_results()
    
    def export_test_results(self):
        """Export detailed test results to JSON file."""
        export_data = {
            "test_suite_metadata": {
                "total_tests": len(self.test_results),
                "timestamp": self.test_results[0]["formatted_result"]["timestamp"] if self.test_results else None,
                "system_info": {
                    "analysis_method": "Enhanced Local AI + Domain Rules",
                    "search_method": "Enhanced TF-IDF",
                    "model_version": "local_ai_v1.0"
                }
            },
            "test_results": []
        }
        
        for result in self.test_results:
            export_data["test_results"].append({
                "test_name": result["test_name"],
                "query": result["query"],
                "decision": result["actual_decision"],
                "processing_time": result["processing_time"],
                "full_analysis": result["formatted_result"]
            })
        
        filename = f"/tmp/docquery_test_results_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Detailed test results exported to: {filename}")
        
        # Also create a summary report
        summary_filename = f"/tmp/docquery_test_summary_{int(time.time())}.json"
        summary_data = {
            "summary": {
                "total_tests": len(self.test_results),
                "avg_processing_time": sum(r["processing_time"] for r in self.test_results) / len(self.test_results),
                "decision_distribution": {}
            },
            "sample_analyses": [result["formatted_result"] for result in self.test_results[:3]]  # First 3 as samples
        }
        
        with open(summary_filename, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Summary report exported to: {summary_filename}")

def main():
    """Main function to run the test suite."""
    test_suite = DocQueryTestSuite()
    test_suite.run_comprehensive_test_suite()

if __name__ == "__main__":
    main()