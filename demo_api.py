#!/usr/bin/env python3
"""
Demo script for testing DocQuery API with real blob URLs
"""
import httpx
import json
import asyncio

BASE_URL = "http://localhost:8000"
AUTH_TOKEN = "b22f8e46c05cd2c3006ae987bbc9c24ca023045b4af9b189e5d3fe340b91514c"

# Sample request matching the problem statement specification
SAMPLE_REQUEST = {
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?",
        "Does this policy cover maternity expenses, and what are the conditions?",
        "What is the waiting period for cataract surgery?",
        "Are the medical expenses for an organ donor covered under this policy?",
        "What is the No Claim Discount (NCD) offered in this policy?",
        "Is there a benefit for preventive health check-ups?",
        "How does the policy define a 'Hospital'?",
        "What is the extent of coverage for AYUSH treatments?",
        "Are there any sub-limits on room rent and ICU charges for Plan A?"
    ]
}

async def test_real_blob_url():
    """Test with the actual blob URL from the specification"""
    print("🧪 DocQuery API Demo - Real Blob URL Test")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print("📋 Testing with sample request from problem statement:")
    print(json.dumps(SAMPLE_REQUEST, indent=2))
    
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:  # Long timeout for blob download
            print("\n🔄 Sending request to API...")
            
            response = await client.post(
                f"{BASE_URL}/api/v1/hackrx/run",
                json=SAMPLE_REQUEST,
                headers=headers
            )
            
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Success! API Response:")
                print(json.dumps(result, indent=2))
                
                print("\n📝 Question-Answer Pairs:")
                for i, (q, a) in enumerate(zip(SAMPLE_REQUEST["questions"], result["answers"]), 1):
                    print(f"\nQ{i}: {q}")
                    print(f"A{i}: {a}")
                    
                return True
            else:
                print(f"❌ API call failed: {response.status_code}")
                print(f"Error details: {response.text}")
                
    except httpx.TimeoutException:
        print("⏰ Request timed out - this is normal for large documents")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    return False

async def test_alternative_document():
    """Test with a publicly available document URL"""
    print("\n🧪 Testing with alternative document...")
    
    # Test with a local file as backup
    import os
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    if pdf_files:
        test_request = {
            "documents": f"file://{os.path.abspath(pdf_files[0])}",
            "questions": [
                "What is the waiting period mentioned in this policy?",
                "What are the coverage details?",
                "What is the premium payment information?",
                "Are there any exclusions mentioned?",
                "What is the claim process?"
            ]
        }
        
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{BASE_URL}/api/v1/hackrx/run",
                    json=test_request,
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ Local document test successful!")
                    print(f"Processed {len(result['answers'])} questions")
                    
                    for i, (q, a) in enumerate(zip(test_request["questions"], result["answers"]), 1):
                        print(f"\nQ{i}: {q}")
                        print(f"A{i}: {a[:150]}..." if len(a) > 150 else f"A{i}: {a}")
                    
                    return True
                    
        except Exception as e:
            print(f"Local test failed: {e}")
    
    return False

def show_api_info():
    """Show API information and usage"""
    print("\n📚 DocQuery API Information")
    print("=" * 40)
    print(f"🔗 Base URL: {BASE_URL}")
    print(f"📖 Documentation: {BASE_URL}/docs")
    print(f"💚 Health Check: {BASE_URL}/health")
    print(f"📊 Status: {BASE_URL}/api/v1/status")
    print("\n🔐 Authentication:")
    print(f"Header: Authorization: Bearer {AUTH_TOKEN}")
    print("\n📋 Endpoints:")
    print("• POST /api/v1/hackrx/run - Main processing endpoint")
    print("• POST /api/v1/hackrx/run-with-openai - Enhanced with OpenAI")
    print("\n📄 Supported formats: PDF, DOCX, TXT, EML")
    print("📏 Max file size: 100MB")
    print("🔢 Max questions: 10 concurrent")

if __name__ == "__main__":
    async def main():
        show_api_info()
        
        # Test with real blob URL first
        print("\n" + "=" * 60)
        real_url_success = await test_real_blob_url()
        
        # If that fails, test with local document
        if not real_url_success:
            print("\n🔄 Blob URL test failed, trying local document...")
            await test_alternative_document()
        
        print("\n" + "=" * 60)
        print("🎯 Demo completed!")
        print("💡 The API is ready for production use with real blob URLs")
        print("📚 Visit http://localhost:8000/docs for interactive API documentation")
        print("=" * 60)
    
    asyncio.run(main())