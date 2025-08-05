#!/usr/bin/env python3
"""
Test script for DocQuery API
"""
import asyncio
import json
import time
from api import app
from fastapi.testclient import TestClient

def test_api_basic():
    """Test basic API functionality"""
    client = TestClient(app)
    
    # Test health endpoint
    print("🔍 Testing health endpoint...")
    response = client.get("/health")
    print(f"Health response: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Health check: {response.json()}")
    else:
        print(f"❌ Health check failed: {response.text}")
    
    # Test status endpoint
    print("\n🔍 Testing status endpoint...")
    response = client.get("/api/v1/status")
    print(f"Status response: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Status check: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"❌ Status check failed: {response.text}")

def test_document_processing():
    """Test document processing components"""
    print("\n🔍 Testing document processing components...")
    
    # Test document processor
    try:
        from document_processor import DocumentProcessor
        processor = DocumentProcessor()
        print(f"✅ Document processor initialized")
        print(f"   Supported formats: {processor.get_supported_formats()}")
    except Exception as e:
        print(f"❌ Document processor failed: {e}")
    
    # Test vector search
    try:
        from vector_search import VectorSearch
        search = VectorSearch()
        print(f"✅ Vector search initialized")
        
        # Test with sample chunks
        sample_chunks = [
            "This is a test document about insurance policies.",
            "The policy covers medical expenses for insured persons.",
            "Emergency procedures require prior authorization."
        ]
        search.build_index(sample_chunks)
        results = search.search("insurance policy", k=2)
        print(f"   Search test successful: {len(results)} results")
        
    except Exception as e:
        print(f"❌ Vector search failed: {e}")
    
    # Test batch processor
    try:
        from batch_processor import BatchProcessor
        processor = BatchProcessor()
        print(f"✅ Batch processor initialized")
    except Exception as e:
        print(f"❌ Batch processor failed: {e}")
    
    # Test blob downloader
    try:
        from blob_downloader import SyncBlobDownloader
        downloader = SyncBlobDownloader()
        print(f"✅ Blob downloader initialized")
    except Exception as e:
        print(f"❌ Blob downloader failed: {e}")

def test_local_documents():
    """Test with local PDF documents"""
    print("\n🔍 Testing with local PDF documents...")
    
    try:
        import os
        from document_processor import DocumentProcessor
        from vector_search import VectorSearch
        from batch_processor import BatchProcessor
        
        # Find available PDF files
        pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
        if not pdf_files:
            print("❌ No PDF files found for testing")
            return
        
        print(f"📄 Found PDF files: {pdf_files[:3]}")  # Show first 3
        
        # Test with first PDF
        test_file = pdf_files[0]
        print(f"🧪 Testing with: {test_file}")
        
        # Process document
        processor = DocumentProcessor()
        text_content = processor.extract_text(test_file)
        print(f"✅ Extracted text: {len(text_content)} characters")
        
        # Create chunks
        chunks = processor.chunk_text(text_content)
        print(f"✅ Created chunks: {len(chunks)} pieces")
        
        # Build search index
        search = VectorSearch()
        search.build_index(chunks)
        print(f"✅ Built search index")
        
        # Test sample questions
        sample_questions = [
            "What is covered under this policy?",
            "What are the waiting periods?",
            "What is the premium payment grace period?"
        ]
        
        # Process questions
        batch_processor = BatchProcessor()
        start_time = time.time()
        answers = batch_processor.process_questions_sync(sample_questions, search, chunks)
        processing_time = time.time() - start_time
        
        print(f"✅ Processed {len(sample_questions)} questions in {processing_time:.2f}s")
        
        # Show results
        for i, (q, a) in enumerate(zip(sample_questions, answers), 1):
            print(f"\n📝 Q{i}: {q}")
            print(f"   A{i}: {a[:100]}..." if len(a) > 100 else f"   A{i}: {a}")
        
    except Exception as e:
        print(f"❌ Local document test failed: {e}")

if __name__ == "__main__":
    print("🚀 DocQuery API Test Suite")
    print("=" * 50)
    
    test_api_basic()
    test_document_processing() 
    test_local_documents()
    
    print("\n" + "=" * 50)
    print("✅ Test suite completed!")