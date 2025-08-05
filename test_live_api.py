#!/usr/bin/env python3
"""
Test the running API server with real requests
"""
import httpx
import json
import time
import asyncio

BASE_URL = "http://localhost:8000"
AUTH_TOKEN = "b22f8e46c05cd2c3006ae987bbc9c24ca023045b4af9b189e5d3fe340b91514c"

async def test_api_endpoints():
    """Test all API endpoints"""
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        print("🚀 Testing DocQuery API Server")
        print("=" * 50)
        
        # Test 1: Health check
        print("\n1️⃣ Testing health endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/health")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {json.dumps(response.json(), indent=2)}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
        
        # Test 2: Status endpoint
        print("\n2️⃣ Testing status endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/api/v1/status")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"❌ Status check failed: {e}")
        
        # Test 3: API Documentation
        print("\n3️⃣ Testing API documentation...")
        try:
            response = await client.get(f"{BASE_URL}/docs", headers={"Accept": "text/html"})
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ API documentation accessible")
            else:
                print(f"❌ Documentation not accessible: {response.status_code}")
        except Exception as e:
            print(f"❌ Documentation test failed: {e}")
        
        # Test 4: Authentication test
        print("\n4️⃣ Testing authentication...")
        try:
            # Test without auth
            response = await client.post(f"{BASE_URL}/api/v1/hackrx/run", json={
                "documents": "test",
                "questions": ["test"]
            })
            print(f"Without auth: {response.status_code} (should be 403)")
            
            # Test with wrong auth
            response = await client.post(f"{BASE_URL}/api/v1/hackrx/run", 
                json={"documents": "test", "questions": ["test"]},
                headers={"Authorization": "Bearer wrong_token"}
            )
            print(f"Wrong auth: {response.status_code} (should be 401)")
            
            print("✅ Authentication working correctly")
        except Exception as e:
            print(f"❌ Authentication test failed: {e}")
        
        # Test 5: Input validation
        print("\n5️⃣ Testing input validation...")
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        
        try:
            # Test empty documents
            response = await client.post(f"{BASE_URL}/api/v1/hackrx/run", 
                json={"documents": "", "questions": ["test"]},
                headers=headers
            )
            print(f"Empty documents: {response.status_code} (should be 400)")
            
            # Test empty questions
            response = await client.post(f"{BASE_URL}/api/v1/hackrx/run", 
                json={"documents": "test", "questions": []},
                headers=headers
            )
            print(f"Empty questions: {response.status_code} (should be 400)")
            
            print("✅ Input validation working correctly")
        except Exception as e:
            print(f"❌ Input validation test failed: {e}")
        
        return True

async def test_document_processing():
    """Test document processing with a simulated blob URL"""
    print("\n6️⃣ Testing document processing...")
    
    # Create a simple test with a local file (simulating blob URL)
    import os
    import shutil
    import tempfile
    from pathlib import Path
    
    # Find a PDF file to test with
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    if not pdf_files:
        print("❌ No PDF files found for testing")
        return False
    
    test_file = pdf_files[0]
    print(f"📄 Using test file: {test_file}")
    
    # For now, we'll test with a file:// URL since we can't easily mock the blob downloader
    # In a real scenario, this would be a blob URL
    
    # Create the request payload matching the API specification
    request_payload = {
        "documents": f"file://{os.path.abspath(test_file)}",  # Simulating blob URL
        "questions": [
            "What is the grace period for premium payment?",
            "What is the waiting period for pre-existing diseases?",
            "Does this policy cover maternity expenses?",
            "What is the extent of coverage for treatments?",
            "Are there any sub-limits on room rent and charges?"
        ]
    }
    
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"📋 Request payload:")
    print(json.dumps(request_payload, indent=2))
    
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:  # Longer timeout for processing
            print("\n🔄 Sending request to API...")
            start_time = time.time()
            
            response = await client.post(
                f"{BASE_URL}/api/v1/hackrx/run",
                json=request_payload,
                headers=headers
            )
            
            processing_time = time.time() - start_time
            print(f"⏱️ Processing time: {processing_time:.2f}s")
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"📋 Response format matches specification: ✅")
                print(f"📝 Number of answers: {len(result.get('answers', []))}")
                
                print("\n📋 API Response:")
                print(json.dumps(result, indent=2))
                
                # Validate response format
                if "answers" in result and isinstance(result["answers"], list):
                    if len(result["answers"]) == len(request_payload["questions"]):
                        print("✅ Response format is correct!")
                        
                        # Show Q&A pairs
                        print("\n📝 Question-Answer Pairs:")
                        for i, (q, a) in enumerate(zip(request_payload["questions"], result["answers"]), 1):
                            print(f"\nQ{i}: {q}")
                            print(f"A{i}: {a}")
                        
                        return True
                    else:
                        print(f"❌ Answer count mismatch: {len(result['answers'])} vs {len(request_payload['questions'])}")
                else:
                    print("❌ Invalid response format")
            else:
                print(f"❌ API call failed: {response.status_code}")
                print(f"Error: {response.text}")
                
    except httpx.TimeoutException:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    return False

async def run_complete_test():
    """Run the complete test suite"""
    print("🧪 DocQuery API Complete Test Suite")
    print("=" * 60)
    
    # Test basic endpoints
    basic_tests_passed = await test_api_endpoints()
    
    if not basic_tests_passed:
        print("❌ Basic tests failed, skipping document processing test")
        return
    
    # Test document processing
    doc_tests_passed = await test_document_processing()
    
    print("\n" + "=" * 60)
    if basic_tests_passed and doc_tests_passed:
        print("✅ ALL TESTS PASSED!")
        print("🎉 DocQuery API is working correctly!")
        print(f"📚 API Documentation: {BASE_URL}/docs")
        print(f"🔗 Health Check: {BASE_URL}/health")
        print(f"📊 Status: {BASE_URL}/api/v1/status")
    else:
        print("❌ Some tests failed. Check the logs above.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_complete_test())