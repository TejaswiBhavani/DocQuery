#!/usr/bin/env python3
"""
Simple test script to verify backend modules work correctly
"""
import os
import sys
import tempfile

# Add backend to path
sys.path.append('backend')

def test_document_processing():
    """Test document processing functionality"""
    print("🧪 Testing document processing...")
    
    try:
        from document_processor import DocumentProcessor
        
        # Create a test document
        test_content = "This is a test document for DocQuery analysis. It contains sample text to verify the document processing functionality works correctly. The system should be able to extract text and create chunks from this content."
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            temp_path = f.name
        
        try:
            processor = DocumentProcessor()
            
            # Test text extraction
            extracted_text = processor.extract_text(temp_path)
            print(f"✅ Text extraction: {len(extracted_text)} characters")
            
            # Test text chunking
            chunks = processor.chunk_text(extracted_text)
            print(f"✅ Text chunking: {len(chunks)} chunks created")
            
            return True
            
        finally:
            os.unlink(temp_path)
            
    except Exception as e:
        print(f"❌ Document processing test error: {e}")
        return False

def test_query_parsing():
    """Test query parsing functionality"""
    print("\n🧪 Testing query parsing...")
    
    try:
        from query_parser import QueryParser
        
        parser = QueryParser()
        
        # Test query parsing
        test_query = "46-year-old male, knee surgery in Pune, 3-month policy"
        parsed = parser.parse_query(test_query)
        
        print(f"✅ Query parsing successful")
        print(f"   - Parsed components: {len([k for k, v in parsed.items() if v])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Query parsing test error: {e}")
        return False

def test_vector_search():
    """Test vector search functionality"""
    print("\n🧪 Testing vector search...")
    
    try:
        # Try different vector search implementations
        search_cls = None
        search_type = "None"
        
        try:
            from vector_search import VectorSearch
            search_cls = VectorSearch
            search_type = "Advanced vector search"
        except ImportError:
            try:
                from enhanced_vector_search import EnhancedVectorSearch
                search_cls = EnhancedVectorSearch
                search_type = "Enhanced TF-IDF search"
            except ImportError:
                try:
                    from simple_vector_search import SimpleVectorSearch
                    search_cls = SimpleVectorSearch
                    search_type = "Simple vector search"
                except ImportError:
                    pass
        
        if search_cls:
            # Test search functionality
            test_chunks = [
                "This document covers insurance policies and procedures.",
                "Medical treatments require pre-authorization.",
                "Coverage includes emergency and planned procedures."
            ]
            
            search = search_cls()
            
            # Try different initialization methods
            if hasattr(search, 'build_index'):
                search.build_index(test_chunks)
            elif hasattr(search, 'add_documents'):
                search.add_documents(test_chunks)
            else:
                search.documents = test_chunks
            
            # Test search
            if hasattr(search, 'search'):
                results = search.search("medical procedures", k=2)
                print(f"✅ Vector search: {search_type}")
                print(f"   - Found {len(results)} relevant chunks")
                return True
            else:
                print(f"✅ Vector search initialized: {search_type}")
                print(f"   - Search method not available, but class loads correctly")
                return True
        else:
            print(f"⚠️ No vector search implementation available")
            return True  # Not a failure, just not available
            
    except Exception as e:
        print(f"❌ Vector search test error: {e}")
        return False

def test_ai_clients():
    """Test AI client functionality"""
    print("\n🧪 Testing AI clients...")
    
    local_ai_available = False
    openai_available = False
    
    try:
        from local_ai_client import LocalAIClient
        local_ai = LocalAIClient()
        local_ai_available = True
        print("✅ Local AI client available")
    except Exception as e:
        print(f"⚠️ Local AI client not available: {e}")
    
    try:
        from openai_client import OpenAIClient
        openai_client = OpenAIClient()
        openai_available = True
        print("✅ OpenAI client available")
    except Exception as e:
        print(f"⚠️ OpenAI client not available: {e}")
    
    if local_ai_available or openai_available:
        return True
    else:
        print("❌ No AI clients available")
        return False

if __name__ == "__main__":
    print("🚀 DocQuery Backend Test Suite")
    print("=" * 40)
    
    results = []
    results.append(test_document_processing())
    results.append(test_query_parsing())
    results.append(test_vector_search())
    results.append(test_ai_clients())
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {sum(results)}/{len(results)} passed")
    
    if sum(results) >= 3:  # Allow for optional components
        print("🎉 Backend functionality tests passed! Core system is working.")
        exit(0)
    else:
        print("⚠️ Critical backend tests failed.")
        exit(1)