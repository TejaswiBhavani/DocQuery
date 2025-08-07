#!/usr/bin/env python3
"""
Simple test script to verify the API functionality works correctly.
This can be used to test the Vercel deployment locally or remotely.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:3000"  # Change for deployed version
TEST_DOCUMENT = """
Health Insurance Policy

Coverage: This policy covers medical expenses including:
- Surgery procedures including knee and heart surgery
- Emergency treatments
- Hospitalization costs
- Outpatient care

Waiting Period: 
- General medical: 30 days
- Surgery: 90 days
- Pre-existing conditions: 2 years

Eligibility:
- Age: 18-65 years
- Medical examination required for applicants over 45
"""

TEST_QUERY = "Does this policy cover knee surgery for a 46-year-old male?"

def test_api_status():
    """Test the status endpoint"""
    print("🔍 Testing API Status...")
    try:
        response = requests.get(f"{BASE_URL}/api/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status', 'unknown')}")
            print(f"   Search Type: {data.get('search_type', 'unknown')}")
            print(f"   Basic Functionality: {data.get('capabilities', {}).get('basic_functionality', False)}")
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return False

def test_api_analyze():
    """Test the document analysis endpoint"""
    print("\n📄 Testing Document Analysis...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/analyze",
            json={
                "document_text": TEST_DOCUMENT,
                "document_name": "test_policy.txt"
            },
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Document analyzed successfully")
                print(f"   Document: {data.get('document_name')}")
                print(f"   Content Length: {data.get('content_length')} characters")
                print(f"   Status: {data.get('status')}")
                return True
            else:
                print(f"❌ Analysis failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Analysis request failed: {response.status_code}")
            if response.headers.get('content-type', '').startswith('application/json'):
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return False

def test_api_query():
    """Test the query processing endpoint"""
    print("\n🔍 Testing Query Processing...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={
                "query": TEST_QUERY,
                "document_text": TEST_DOCUMENT
            },
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Query processed successfully")
                print(f"   Query: {data.get('query')}")
                print(f"   Status: {data.get('status')}")
                
                # Show parsed query details
                parsed = data.get('parsed_query', {})
                if parsed:
                    print(f"   Parsed Components:")
                    for key, value in parsed.items():
                        if value:
                            print(f"     - {key}: {value}")
                
                # Show analysis if available
                analysis = data.get('analysis')
                if analysis:
                    print(f"   Analysis Available: Yes")
                else:
                    print(f"   Analysis: {data.get('message', 'No analysis returned')}")
                
                return True
            else:
                print(f"❌ Query processing failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Query request failed: {response.status_code}")
            if response.headers.get('content-type', '').startswith('application/json'):
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Query processing error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 DocQuery API Test Suite")
    print("=" * 40)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Status
    if test_api_status():
        tests_passed += 1
    
    # Test 2: Document Analysis
    if test_api_analyze():
        tests_passed += 1
    
    # Test 3: Query Processing
    if test_api_query():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! API is working correctly.")
        return 0
    else:
        print(f"⚠️  {total_tests - tests_passed} test(s) failed. Check the API deployment.")
        return 1

if __name__ == "__main__":
    import sys
    
    # Allow custom base URL
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1].rstrip('/')
        print(f"🔧 Using custom base URL: {BASE_URL}")
    
    exit_code = main()
    sys.exit(exit_code)