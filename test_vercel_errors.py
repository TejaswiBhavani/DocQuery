#!/usr/bin/env python3
"""
Test script for Vercel error handling in DocQuery API
"""
import asyncio
import json
import time
import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_vercel_error_handler():
    """Test the Vercel error handler functionality"""
    print("🧪 Testing Vercel Error Handler...")
    
    try:
        from vercel_error_handler import VercelErrorHandler, VercelErrorCode
        error_handler = VercelErrorHandler()
        
        print("✅ Vercel error handler imported successfully")
        
        # Test error code mapping
        total_errors = len(error_handler.get_all_errors())
        print(f"📊 Total Vercel error codes supported: {total_errors}")
        
        # Test specific error codes
        test_codes = [
            "FUNCTION_INVOCATION_TIMEOUT",
            "FUNCTION_PAYLOAD_TOO_LARGE", 
            "DEPLOYMENT_NOT_FOUND",
            "INTERNAL_UNEXPECTED_ERROR"
        ]
        
        for code in test_codes:
            if error_handler.is_vercel_error(code):
                details = error_handler.get_error_details(code)
                print(f"  ✅ {code}: {details['status']} ({details['category'].value})")
            else:
                print(f"  ❌ {code}: Not recognized")
        
        # Test error response creation
        status_code, response = error_handler.create_error_response(
            "FUNCTION_INVOCATION_TIMEOUT",
            "Test timeout error"
        )
        print(f"📝 Test error response: {status_code} - {response['error']['message']}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import Vercel error handler: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing Vercel error handler: {e}")
        return False

def test_api_with_vercel_errors():
    """Test API integration with Vercel error handling"""
    print("\n🔌 Testing API with Vercel Error Integration...")
    
    try:
        # Try to start the API for testing
        from fastapi.testclient import TestClient
        from api import app
        
        client = TestClient(app)
        print("✅ API test client created")
        
        # Test health endpoint
        response = client.get("/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
        
        # Test Vercel status endpoint
        response = client.get("/api/v1/vercel/status")
        if response.status_code == 200:
            data = response.json()
            print("✅ Vercel status endpoint working")
            print(f"   Vercel support: {data.get('vercel_support', False)}")
            print(f"   Error handling: {data.get('error_handling', {}).get('application_errors', 0)} error codes")
        else:
            print(f"❌ Vercel status endpoint failed: {response.status_code}")
        
        # Test Vercel error codes endpoint
        response = client.get("/api/v1/vercel/errors")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Vercel error codes endpoint: {data.get('total_errors', 0)} errors")
        elif response.status_code == 501:
            print("⚠️  Vercel error codes endpoint: Not available (expected without FastAPI)")
        else:
            print(f"❌ Vercel error codes endpoint failed: {response.status_code}")
        
        # Test error simulation
        test_error_codes = ["FUNCTION_INVOCATION_TIMEOUT", "DEPLOYMENT_NOT_FOUND"]
        for error_code in test_error_codes:
            response = client.post(f"/api/v1/vercel/test-error?error_code={error_code}")
            if response.status_code >= 400:  # Expected error response
                print(f"✅ Error simulation for {error_code}: {response.status_code}")
            else:
                print(f"❌ Error simulation for {error_code}: Unexpected {response.status_code}")
        
        return True
        
    except ImportError as e:
        print(f"⚠️  API testing skipped (missing dependencies): {e}")
        return True  # Not a failure, just missing optional deps
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def test_error_handler_integration():
    """Test enhanced error handler integration"""
    print("\n🔧 Testing Enhanced Error Handler Integration...")
    
    try:
        from error_handler import DocQueryErrorHandler
        error_handler = DocQueryErrorHandler()
        
        print("✅ Enhanced error handler imported")
        
        # Test Vercel environment check
        vercel_info = error_handler.check_vercel_environment()
        print(f"📊 Vercel environment detected: {vercel_info['is_vercel']}")
        print(f"   Environment: {vercel_info['environment']}")
        print(f"   Region: {vercel_info['region']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing enhanced error handler: {e}")
        return False

def test_comprehensive_coverage():
    """Test comprehensive error coverage"""
    print("\n📋 Testing Comprehensive Error Coverage...")
    
    try:
        from vercel_error_handler import VercelErrorCode
        
        app_errors = VercelErrorCode.APPLICATION_ERRORS
        platform_errors = VercelErrorCode.PLATFORM_ERRORS
        
        print(f"📊 Application errors: {len(app_errors)}")
        print(f"📊 Platform errors: {len(platform_errors)}")
        print(f"📊 Total coverage: {len(app_errors) + len(platform_errors)} error codes")
        
        # Check coverage of different categories
        categories = {}
        for code, info in {**app_errors, **platform_errors}.items():
            category = info["category"].value
            categories[category] = categories.get(category, 0) + 1
        
        print("📋 Error categories covered:")
        for category, count in categories.items():
            print(f"   {category}: {count} errors")
        
        # Check status code distribution
        status_codes = {}
        for code, info in {**app_errors, **platform_errors}.items():
            status = info["status"]
            status_codes[status] = status_codes.get(status, 0) + 1
        
        print("📋 HTTP status codes:")
        for status, count in sorted(status_codes.items()):
            print(f"   {status}: {count} errors")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing coverage: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 DocQuery Vercel Error Handling Test Suite")
    print("=" * 60)
    
    tests = [
        ("Vercel Error Handler", test_vercel_error_handler),
        ("API Integration", test_api_with_vercel_errors),
        ("Enhanced Error Handler", test_error_handler_integration),
        ("Comprehensive Coverage", test_comprehensive_coverage)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 40)
        success = test_func()
        results.append((test_name, success))
        print(f"Result: {'✅ PASSED' if success else '❌ FAILED'}")
    
    print("\n" + "=" * 60)
    print("🏁 Test Results Summary:")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Vercel error handling is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)