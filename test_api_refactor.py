#!/usr/bin/env python3
"""
Simple test script to verify API endpoints work correctly
"""
import json
import tempfile
import os
import sys

# Add backend to path
sys.path.append('backend')

def test_upload_api():
    """Test the upload API logic"""
    print("🧪 Testing upload API...")
    
    # Import the handler from our API
    sys.path.append('api')
    from upload import handler
    
    # Test the handle_upload function directly without HTTP setup
    test_data = {
        'file_content': "This is a test document for DocQuery analysis. It contains sample text to verify the upload and processing functionality works correctly.",
        'file_name': 'test_document.txt',
        'document_name': 'Test Document'
    }
    
    try:
        # Create a handler instance to access the handle_upload method
        h = handler(None, None, None)  # BaseRequestHandler requires these but we won't use them
        result = h.handle_upload(test_data)
        if result.get('success'):
            print("✅ Upload API test passed")
            print(f"   - Document ID: {result.get('document_id', 'N/A')[:8]}...")
            print(f"   - Processing time: {result.get('processing_time', 'N/A')}")
            print(f"   - Character count: {result.get('document_analysis', {}).get('character_count', 'N/A')}")
            return True
        else:
            print(f"❌ Upload API test failed: {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Upload API test error: {e}")
        return False

def test_search_api():
    """Test the search API logic"""
    print("\n🧪 Testing search API...")
    
    try:
        sys.path.append('api')
        from search import handler
        
        h = handler(None, None, None)
        
        # Test data
        test_data = {
            'query': 'test document analysis',
            'document_text': 'This is a test document for DocQuery analysis. It contains sample text to verify the search functionality works correctly. Document analysis is important.',
            'top_k': 2,
            'document_id': 'test-doc-123'
        }
        
        result = h.handle_search(test_data)
        if result.get('success'):
            print("✅ Search API test passed")
            print(f"   - Chunks found: {result.get('search_results', {}).get('chunks_found', 'N/A')}")
            print(f"   - Search method: {result.get('search_metadata', {}).get('search_method', 'N/A')}")
            return True
        else:
            print(f"❌ Search API test failed: {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Search API test error: {e}")
        return False

def test_analyze_api():
    """Test the analyze API logic"""
    print("\n🧪 Testing analyze API...")
    
    try:
        sys.path.append('api')
        from analyze import handler
        
        h = handler(None, None, None)
        
        # Test data
        test_data = {
            'query': 'Test patient, sample procedure',
            'document_text': 'This is a sample insurance policy document. It covers various procedures and conditions for policy holders.',
            'use_local_ai': True,
            'document_id': 'test-doc-123'
        }
        
        result = h.handle_analysis(test_data)
        if result.get('success'):
            print("✅ Analyze API test passed")
            print(f"   - Analysis ID: {result.get('analysis_id', 'N/A')}")
            print(f"   - Decision: {result.get('analysis', {}).get('decision', {}).get('status', 'N/A')}")
            print(f"   - AI Method: {result.get('system', {}).get('analysis_method', 'N/A')}")
            return True
        else:
            print(f"❌ Analyze API test failed: {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Analyze API test error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 DocQuery API Test Suite")
    print("=" * 40)
    
    results = []
    results.append(test_upload_api())
    results.append(test_search_api())  
    results.append(test_analyze_api())
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("🎉 All API tests passed! The refactored system is working correctly.")
        exit(0)
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        exit(1)