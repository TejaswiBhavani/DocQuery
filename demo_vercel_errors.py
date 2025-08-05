#!/usr/bin/env python3
"""
Demo script for Vercel error handling in DocQuery
Shows practical examples of error detection and handling
"""
import sys
import os
import json

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_error_handler():
    """Demonstrate the Vercel error handler capabilities"""
    print("🎬 DocQuery Vercel Error Handling Demo")
    print("=" * 50)
    
    try:
        from vercel_error_handler import VercelErrorHandler
        error_handler = VercelErrorHandler()
        
        print("✅ Vercel error handler loaded successfully")
        print(f"📊 Supporting {len(error_handler.get_all_errors())} error codes\n")
        
        # Demo 1: Common error scenarios
        print("🎯 Demo 1: Common Error Scenarios")
        print("-" * 30)
        
        common_errors = [
            ("FUNCTION_INVOCATION_TIMEOUT", "Function took too long to execute"),
            ("FUNCTION_PAYLOAD_TOO_LARGE", "Request body exceeds 5MB limit"),
            ("DEPLOYMENT_NOT_FOUND", "Deployment URL not accessible"),
            ("NOT_FOUND", "Resource or endpoint not found"),
            ("INVALID_REQUEST_METHOD", "Wrong HTTP method used")
        ]
        
        for error_code, description in common_errors:
            status_code, response = error_handler.create_error_response(error_code, description)
            print(f"🔍 {error_code}")
            print(f"   Status: {status_code}")
            print(f"   Category: {response['error']['category']}")
            print(f"   Message: {response['error']['message']}")
            if response['error'].get('suggestions'):
                print(f"   Suggestions: {len(response['error']['suggestions'])} available")
            print()
        
        # Demo 2: Error category breakdown
        print("📊 Demo 2: Error Category Breakdown")
        print("-" * 30)
        
        categories = {}
        for code, info in error_handler.get_all_errors().items():
            category = info["category"].value
            categories[category] = categories.get(category, 0) + 1
        
        for category, count in sorted(categories.items()):
            print(f"   {category}: {count} errors")
        
        print()
        
        # Demo 3: Practical error simulation
        print("🧪 Demo 3: Practical Error Simulation")
        print("-" * 30)
        
        # Simulate a timeout error
        print("Simulating function timeout...")
        try:
            raise Exception("Connection timeout after 30 seconds")
        except Exception as e:
            from fastapi.responses import JSONResponse
            response = error_handler.handle_application_error(e, "document_processing")
            print(f"   Detected as: {json.loads(response.body)['error']['code']}")
            print(f"   Status: {response.status_code}")
        
        # Simulate a payload error
        print("\nSimulating payload too large...")
        try:
            raise Exception("Request entity too large - 8MB payload")
        except Exception as e:
            response = error_handler.handle_application_error(e, "file_upload")
            print(f"   Detected as: {json.loads(response.body)['error']['code']}")
            print(f"   Status: {response.status_code}")
        
        print("\n🎉 Demo completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Could not import Vercel error handler: {e}")
        print("💡 Make sure FastAPI dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def demo_api_endpoints():
    """Demonstrate API endpoints for error handling"""
    print("\n🌐 Demo: API Endpoints for Error Handling")
    print("=" * 50)
    
    endpoints = [
        ("GET /api/v1/vercel/status", "Check Vercel deployment status and capabilities"),
        ("GET /api/v1/vercel/errors", "List all supported Vercel error codes"),
        ("POST /api/v1/vercel/test-error", "Test specific error code handling"),
        ("GET /health", "General health check with Vercel support info")
    ]
    
    print("Available endpoints:")
    for endpoint, description in endpoints:
        print(f"  📍 {endpoint}")
        print(f"      {description}")
    
    print("\n🔧 Example usage:")
    print("  # Check Vercel status")
    print("  curl http://localhost:8000/api/v1/vercel/status")
    print()
    print("  # List error codes")
    print("  curl http://localhost:8000/api/v1/vercel/errors")
    print()
    print("  # Test timeout error")
    print("  curl -X POST 'http://localhost:8000/api/v1/vercel/test-error?error_code=FUNCTION_INVOCATION_TIMEOUT'")

def demo_environment_detection():
    """Demonstrate Vercel environment detection"""
    print("\n🌍 Demo: Environment Detection")
    print("=" * 50)
    
    try:
        from error_handler import DocQueryErrorHandler
        error_handler = DocQueryErrorHandler()
        
        vercel_info = error_handler.check_vercel_environment()
        
        print("Current environment:")
        for key, value in vercel_info.items():
            print(f"  {key}: {value}")
        
        if vercel_info['is_vercel']:
            print("\n✅ Running in Vercel environment")
            print("🔧 Enhanced error handling active")
        else:
            print("\n📍 Running in local/other environment")
            print("🔧 Standard error handling with Vercel compatibility")
        
        return True
        
    except Exception as e:
        print(f"❌ Environment detection failed: {e}")
        return False

def main():
    """Run the complete demo"""
    demos = [
        demo_error_handler,
        demo_api_endpoints,
        demo_environment_detection
    ]
    
    success_count = 0
    for demo_func in demos:
        try:
            success = demo_func()
            if success:
                success_count += 1
        except Exception as e:
            print(f"❌ Demo section failed: {e}")
    
    print("\n" + "=" * 50)
    print(f"🏁 Demo Summary: {success_count}/{len(demos)} sections completed")
    
    if success_count == len(demos):
        print("🎉 All demo sections completed successfully!")
        print("\n💡 Next steps:")
        print("  1. Deploy to Vercel and test error handling")
        print("  2. Monitor error logs in Vercel dashboard")
        print("  3. Use API endpoints for error diagnostics")
        print("  4. Check VERCEL_ERROR_HANDLING.md for complete documentation")
    else:
        print("⚠️  Some demo sections had issues - check output above")

if __name__ == "__main__":
    main()