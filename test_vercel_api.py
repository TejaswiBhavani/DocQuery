#!/usr/bin/env python3
"""
Comprehensive test suite for the enhanced Vercel API endpoints
Tests the API functionality to ensure feature parity with Streamlit version
"""

import json
import sys
import os
sys.path.append('.')

from api.index import handler
from unittest.mock import Mock
import io


class TestVercelAPI:
    """Test class for Vercel API endpoints"""
    
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
    
    def create_mock_handler(self):
        """Create a mock handler for testing"""
        mock_handler = handler()
        mock_handler.wfile = Mock()
        mock_handler.response_data = None
        
        def capture_write(data):
            mock_handler.response_data = json.loads(data.decode())
        
        mock_handler.wfile.write = capture_write
        mock_handler.send_response = lambda x: None
        mock_handler.send_header = lambda x, y: None
        mock_handler.end_headers = lambda: None
        
        return mock_handler
    
    def test_status_endpoint(self):
        """Test the /api/status endpoint"""
        print("🔍 Testing API Status Endpoint...")
        self.total_tests += 1
        
        try:
            mock_handler = self.create_mock_handler()
            mock_handler.path = '/api/status'
            mock_handler.headers = {}
            
            mock_handler.do_GET()
            
            response = mock_handler.response_data
            
            # Validate response structure
            required_fields = ['status', 'search_type', 'capabilities', 'message']
            for field in required_fields:
                assert field in response, f"Missing field: {field}"
            
            assert response['status'] == 'online', "Status should be 'online'"
            assert 'capabilities' in response, "Should include capabilities"
            assert 'basic_functionality' in response['capabilities'], "Should include basic functionality check"
            
            print("✅ Status endpoint test PASSED")
            self.passed_tests += 1
            self.test_results.append({"test": "Status Endpoint", "result": "PASS"})
            
        except Exception as e:
            print(f"❌ Status endpoint test FAILED: {str(e)}")
            self.test_results.append({"test": "Status Endpoint", "result": f"FAIL: {str(e)}"})
    
    def test_document_analysis(self):
        """Test the /api/analyze endpoint"""
        print("📄 Testing Document Analysis Endpoint...")
        self.total_tests += 1
        
        try:
            mock_handler = self.create_mock_handler()
            mock_handler.path = '/api/analyze'
            mock_handler.headers = {'Content-Length': '1000'}
            
            # Sample document content
            test_document = """
            Health Insurance Policy
            
            This policy covers medical treatments including:
            - Emergency surgeries
            - Diagnostic tests
            - Hospitalization costs
            
            Policy Terms:
            - Waiting period: 30 days
            - Maximum coverage: $100,000
            - Age limit: 18-75 years
            """
            
            test_data = {
                'document_text': test_document,
                'document_name': 'test_policy.txt'
            }
            
            # Mock the request data
            json_data = json.dumps(test_data).encode()
            mock_handler.rfile = io.BytesIO(json_data)
            
            # Override content length
            mock_handler.headers['Content-Length'] = str(len(json_data))
            
            mock_handler.do_POST()
            
            response = mock_handler.response_data
            
            # Validate enhanced response structure
            assert response['success'] == True, "Analysis should succeed"
            assert 'document_analysis' in response, "Should include document analysis"
            assert 'processing_details' in response, "Should include processing details"
            assert 'document_stats' in response, "Should include document statistics"
            assert 'capabilities' in response, "Should include capabilities"
            
            # Validate document analysis fields
            doc_analysis = response['document_analysis']
            required_doc_fields = ['document_name', 'processed_content', 'full_content_length', 'chunk_count']
            for field in required_doc_fields:
                assert field in doc_analysis, f"Missing document analysis field: {field}"
            
            # Validate processing details
            processing = response['processing_details']
            assert 'processing_time' in processing, "Should include processing time"
            assert 'search_type' in processing, "Should include search type"
            assert 'chunks_created' in processing, "Should include chunks created"
            
            print("✅ Document analysis test PASSED")
            self.passed_tests += 1
            self.test_results.append({"test": "Document Analysis", "result": "PASS"})
            
        except Exception as e:
            print(f"❌ Document analysis test FAILED: {str(e)}")
            self.test_results.append({"test": "Document Analysis", "result": f"FAIL: {str(e)}"})
    
    def test_query_processing(self):
        """Test the /api/query endpoint with comprehensive analysis"""
        print("🔍 Testing Query Processing Endpoint...")
        self.total_tests += 1
        
        try:
            mock_handler = self.create_mock_handler()
            mock_handler.path = '/api/query'
            mock_handler.headers = {'Content-Length': '1000'}
            
            # Sample document and query
            test_document = """
            Health Insurance Policy
            Coverage: Emergency surgeries, diagnostic tests, hospitalization
            Waiting period: 30 days for non-emergency procedures
            Age coverage: 18-75 years
            Maximum benefit: $100,000 per year
            """
            
            test_query = "46-year-old male needs knee surgery, 3-month policy"
            
            test_data = {
                'query': test_query,
                'document_text': test_document
            }
            
            # Mock the request data
            json_data = json.dumps(test_data).encode()
            mock_handler.rfile = io.BytesIO(json_data)
            mock_handler.headers['Content-Length'] = str(len(json_data))
            
            mock_handler.do_POST()
            
            response = mock_handler.response_data
            
            # Validate enhanced response structure
            assert response['success'] == True, "Query processing should succeed"
            assert 'analysis_id' in response, "Should include analysis ID"
            assert 'timestamp' in response, "Should include timestamp"
            assert 'query' in response, "Should include query details"
            assert 'analysis' in response, "Should include analysis results"
            assert 'system' in response, "Should include system information"
            
            # Validate query structure
            query = response['query']
            required_query_fields = ['original', 'parsed_components', 'domain']
            for field in required_query_fields:
                assert field in query, f"Missing query field: {field}"
            
            # Validate analysis structure
            analysis = response['analysis']
            required_analysis_fields = ['decision', 'justification', 'recommendations', 'next_steps']
            for field in required_analysis_fields:
                assert field in analysis, f"Missing analysis field: {field}"
            
            # Validate decision structure
            decision = analysis['decision']
            required_decision_fields = ['status', 'confidence', 'risk_level']
            for field in required_decision_fields:
                assert field in decision, f"Missing decision field: {field}"
            
            # Validate system information
            system = response['system']
            assert 'processing_time' in system, "Should include processing time"
            assert 'model_version' in system, "Should include model version"
            
            print("✅ Query processing test PASSED")
            self.passed_tests += 1
            self.test_results.append({"test": "Query Processing", "result": "PASS"})
            
        except Exception as e:
            print(f"❌ Query processing test FAILED: {str(e)}")
            self.test_results.append({"test": "Query Processing", "result": f"FAIL: {str(e)}"})
    
    def test_query_only_processing(self):
        """Test query processing without document"""
        print("🔍 Testing Query-Only Processing...")
        self.total_tests += 1
        
        try:
            mock_handler = self.create_mock_handler()
            mock_handler.path = '/api/query'
            mock_handler.headers = {'Content-Length': '1000'}
            
            test_data = {
                'query': '46-year-old male needs knee surgery',
                'document_text': ''  # No document
            }
            
            # Mock the request data
            json_data = json.dumps(test_data).encode()
            mock_handler.rfile = io.BytesIO(json_data)
            mock_handler.headers['Content-Length'] = str(len(json_data))
            
            mock_handler.do_POST()
            
            response = mock_handler.response_data
            
            # Should succeed but with limited analysis
            assert response['success'] == True, "Query-only processing should succeed"
            assert response['status'] == 'parsed', "Status should be 'parsed'"
            assert 'message' in response, "Should include explanatory message"
            assert 'query' in response, "Should include query details"
            
            print("✅ Query-only processing test PASSED")
            self.passed_tests += 1
            self.test_results.append({"test": "Query-Only Processing", "result": "PASS"})
            
        except Exception as e:
            print(f"❌ Query-only processing test FAILED: {str(e)}")
            self.test_results.append({"test": "Query-Only Processing", "result": f"FAIL: {str(e)}"})
    
    def test_error_handling(self):
        """Test API error handling"""
        print("⚠️ Testing Error Handling...")
        self.total_tests += 1
        
        try:
            mock_handler = self.create_mock_handler()
            mock_handler.path = '/api/query'
            mock_handler.headers = {'Content-Length': '50'}
            
            # Test with empty query
            test_data = {'query': '', 'document_text': 'some text'}
            json_data = json.dumps(test_data).encode()
            mock_handler.rfile = io.BytesIO(json_data)
            mock_handler.headers['Content-Length'] = str(len(json_data))
            
            mock_handler.do_POST()
            response = mock_handler.response_data
            
            # Should return error for empty query
            assert 'error' in response, "Should return error for empty query"
            assert response['status'] == 400, "Should return status 400 for bad request"
            
            print("✅ Error handling test PASSED")
            self.passed_tests += 1
            self.test_results.append({"test": "Error Handling", "result": "PASS"})
            
        except Exception as e:
            print(f"❌ Error handling test FAILED: {str(e)}")
            self.test_results.append({"test": "Error Handling", "result": f"FAIL: {str(e)}"})
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        print("🧪 Enhanced Vercel API Test Suite")
        print("=" * 60)
        
        # Run all tests
        self.test_status_endpoint()
        self.test_document_analysis()
        self.test_query_processing()
        self.test_query_only_processing()
        self.test_error_handling()
        
        # Generate report
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result['result'] == "PASS" else "❌"
            print(f"  {status_icon} {result['test']}: {result['result']}")
        
        # Test outcome
        if self.passed_tests == self.total_tests:
            print("\n🎉 ALL TESTS PASSED! The enhanced API is working correctly.")
            return True
        else:
            print(f"\n⚠️  {self.total_tests - self.passed_tests} test(s) failed. Please review the issues above.")
            return False


if __name__ == "__main__":
    tester = TestVercelAPI()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)