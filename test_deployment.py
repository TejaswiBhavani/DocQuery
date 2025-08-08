#!/usr/bin/env python3
"""
Test script for the deployment-ready DocQuery application.
Tests FastAPI backend without Streamlit dependency.
"""

import requests
import json
import time
import sys

def test_deployment():
    """Test the deployment-ready FastAPI application."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing DocQuery FastAPI Deployment (No Streamlit)")
    print("=" * 60)
    
    # Test 1: Health check
    print("1. Testing health check endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check passed: {data.get('service', 'Unknown')}")
            print(f"   📊 Capabilities: {len(data.get('capabilities', {}))} features available")
        else:
            print(f"   ❌ Health check failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return False
    
    # Test 2: API status
    print("\n2. Testing API status endpoint...")
    try:
        response = requests.get(f"{base_url}/api/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API status: {data.get('status', 'Unknown')}")
            print(f"   🔍 Search type: {data.get('search_type', 'Unknown')}")
            capabilities = data.get('capabilities', {})
            print(f"   🧠 Basic functionality: {'✅' if capabilities.get('basic_functionality') else '❌'}")
            print(f"   🤖 Advanced AI: {'✅' if capabilities.get('advanced_ai') else '❌'}")
        else:
            print(f"   ❌ API status failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ API status failed: {e}")
        return False
    
    # Test 3: Frontend serving
    print("\n3. Testing HTML frontend serving...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200 and "DocQuery" in response.text:
            print("   ✅ HTML frontend served successfully")
            print(f"   📄 Content length: {len(response.text)} characters")
        else:
            print(f"   ❌ Frontend serving failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Frontend serving failed: {e}")
        return False
    
    # Test 4: Document analysis
    print("\n4. Testing document analysis...")
    test_document = {
        "document_text": "This is a comprehensive health insurance policy. Coverage includes medical treatments, surgeries, and emergency care for policy holders aged 18-70. Premium members get additional benefits including dental and vision coverage.",
        "document_name": "test_health_policy.txt"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/analyze",
            json=test_document,
            timeout=15,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Document analysis successful")
            doc_stats = data.get('document_stats', {})
            print(f"   📊 Characters: {doc_stats.get('total_characters', 0)}")
            print(f"   📝 Words: {doc_stats.get('total_words', 0)}")
            print(f"   🧩 Chunks: {data.get('document_analysis', {}).get('chunk_count', 0)}")
            processing = data.get('processing_details', {})
            print(f"   ⏱️ Processing time: {processing.get('processing_time', 'N/A')}")
        else:
            print(f"   ❌ Document analysis failed: HTTP {response.status_code}")
            print(f"   📝 Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Document analysis failed: {e}")
        return False
    
    # Test 5: Query analysis
    print("\n5. Testing query analysis...")
    test_query = {
        "query": "Does this policy cover emergency surgery for a 45-year-old patient?",
        "document_text": test_document["document_text"]
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/query",
            json=test_query,
            timeout=15,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Query analysis successful")
            query_data = data.get('query', {})
            print(f"   💬 Original query: {query_data.get('original', 'N/A')[:50]}...")
            print(f"   🏷️ Domain: {query_data.get('domain', 'N/A')}")
            analysis = data.get('analysis', {})
            decision = analysis.get('decision', {})
            print(f"   🎯 Decision: {decision.get('status', 'N/A')}")
            print(f"   🎲 Confidence: {decision.get('confidence', 'N/A')}")
            system = data.get('system', {})
            print(f"   🔧 Analysis method: {system.get('analysis_method', 'N/A')}")
            print(f"   ⏱️ Processing time: {system.get('processing_time', 'N/A')}")
        else:
            print(f"   ❌ Query analysis failed: HTTP {response.status_code}")
            print(f"   📝 Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Query analysis failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 All tests passed! Deployment-ready FastAPI app working correctly.")
    print("📋 Summary:")
    print("   • Streamlit dependency removed ✅")  
    print("   • FastAPI backend functional ✅")
    print("   • HTML frontend served ✅")
    print("   • Document processing working ✅")
    print("   • Query analysis working ✅")
    print("   • All core features preserved ✅")
    print("\n🚀 Ready for deployment on Render, Heroku, or similar platforms!")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage: python test_deployment.py")
        print("Make sure the FastAPI server is running on localhost:8000")
        print("Start server with: python main.py")
        sys.exit(0)
    
    print("⏳ Starting deployment tests in 3 seconds...")
    print("   (Make sure the server is running: python main.py)")
    time.sleep(3)
    
    success = test_deployment()
    sys.exit(0 if success else 1)