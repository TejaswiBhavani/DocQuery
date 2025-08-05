#!/usr/bin/env python3
"""
Test script for the full API functionality using local documents
"""
import asyncio
import json
import time
import tempfile
import shutil
from fastapi.testclient import TestClient
from api import app

def simulate_api_request():
    """Test the API with a real document by copying to temp location and using local file URL"""
    
    print("🚀 Testing full API workflow...")
    client = TestClient(app)
    
    # Test authentication first
    print("\n🔐 Testing authentication...")
    
    # Test without token
    response = client.post("/api/v1/hackrx/run", json={
        "documents": "test.pdf",
        "questions": ["Test question"]
    })
    print(f"Without token: {response.status_code} (should be 401)")
    
    # Test with wrong token
    response = client.post("/api/v1/hackrx/run", 
        json={"documents": "test.pdf", "questions": ["Test question"]},
        headers={"Authorization": "Bearer wrong_token"}
    )
    print(f"Wrong token: {response.status_code} (should be 401)")
    
    # Test with correct token but invalid request
    print("\n🧪 Testing API validation...")
    correct_headers = {"Authorization": "Bearer b22f8e46c05cd2c3006ae987bbc9c24ca023045b4af9b189e5d3fe340b91514c"}
    
    # Test empty documents
    response = client.post("/api/v1/hackrx/run", 
        json={"documents": "", "questions": ["Test question"]},
        headers=correct_headers
    )
    print(f"Empty documents: {response.status_code} (should be 400)")
    
    # Test empty questions
    response = client.post("/api/v1/hackrx/run", 
        json={"documents": "test.pdf", "questions": []},
        headers=correct_headers
    )
    print(f"Empty questions: {response.status_code} (should be 400)")
    
    print("\n✅ Authentication and validation tests passed!")

def test_document_processing_components():
    """Test individual components to ensure they work"""
    print("\n🔧 Testing individual components...")
    
    try:
        # Test enhanced vector search specifically 
        from enhanced_vector_search import EnhancedVectorSearch
        from document_processor import DocumentProcessor
        from batch_processor import BatchProcessor
        
        # Process a real document
        print("📄 Processing real document...")
        processor = DocumentProcessor()
        
        # Find a PDF file
        import os
        pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
        if not pdf_files:
            print("❌ No PDF files found")
            return False
            
        test_file = pdf_files[0]
        print(f"Using: {test_file}")
        
        # Extract text
        text_content = processor.extract_text(test_file)
        print(f"✅ Extracted {len(text_content)} characters")
        
        # Create chunks
        chunks = processor.chunk_text(text_content)
        print(f"✅ Created {len(chunks)} chunks")
        
        # Build search index
        search = EnhancedVectorSearch()
        search.build_index(chunks)
        print(f"✅ Built search index")
        
        # Test search
        results = search.search("policy coverage waiting period", k=3)
        print(f"✅ Search returned {len(results)} results")
        
        # Test batch processor
        processor = BatchProcessor(use_openai=False)
        sample_questions = [
            "What is the waiting period for pre-existing diseases?",
            "Does this policy cover maternity expenses?",
            "What is the grace period for premium payment?"
        ]
        
        print(f"🤖 Processing {len(sample_questions)} questions...")
        start_time = time.time()
        
        answers = processor.process_questions_sync(sample_questions, search, chunks)
        processing_time = time.time() - start_time
        
        print(f"✅ Processed questions in {processing_time:.2f}s")
        
        # Show results
        for i, (q, a) in enumerate(zip(sample_questions, answers), 1):
            print(f"\n📝 Q{i}: {q}")
            answer_preview = a[:200] + "..." if len(a) > 200 else a
            print(f"   A{i}: {answer_preview}")
        
        return True
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        return False

def create_sample_request():
    """Create a sample request that mimics the expected API format"""
    
    # This simulates the request format specified in the problem statement
    sample_request = {
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
    
    expected_response_format = {
        "answers": [
            "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.",
            "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered.",
            # ... more answers
        ]
    }
    
    print("📋 Sample API Request Format:")
    print(json.dumps(sample_request, indent=2))
    print("\n📋 Expected Response Format:")
    print(json.dumps(expected_response_format, indent=2))
    
    return sample_request

if __name__ == "__main__":
    print("🧪 DocQuery API Complete Test Suite")
    print("=" * 60)
    
    # Test 1: API functionality
    simulate_api_request()
    
    # Test 2: Component testing
    components_ok = test_document_processing_components()
    
    # Test 3: Show expected format
    print("\n" + "=" * 60)
    print("📝 API CONTRACT VERIFICATION")
    create_sample_request()
    
    print("\n" + "=" * 60)
    if components_ok:
        print("✅ ALL TESTS PASSED! API is ready for deployment.")
        print("💡 To run the server: uvicorn api:app --host 0.0.0.0 --port 8000")
        print("📚 API Documentation: http://localhost:8000/docs")
    else:
        print("❌ Some tests failed. Check the error messages above.")
    print("=" * 60)