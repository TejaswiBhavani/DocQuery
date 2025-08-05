#!/usr/bin/env python3
"""
Simple test to verify DocQuery functionality after Vercel optimizations.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        import app
        print("✓ Main app module imported successfully")
    except Exception as e:
        print(f"✗ Failed to import app: {e}")
        return False
    
    try:
        from database_manager import DatabaseManager
        print("✓ Database manager imported successfully")
    except Exception as e:
        print(f"✗ Failed to import database manager: {e}")
        return False
        
    try:
        from simple_vector_search import SimpleVectorSearch
        print("✓ Simple vector search imported successfully")
    except Exception as e:
        print(f"✗ Failed to import simple vector search: {e}")
        return False
    
    return True

def test_database_manager():
    """Test lightweight database manager."""
    print("\nTesting lightweight database manager...")
    
    try:
        from database_manager import DatabaseManager
        db = DatabaseManager()
        
        # Test saving a document
        doc_id = db.save_document(
            filename="test.pdf",
            file_size=1024,
            chunk_count=5,
            processing_time=2.5,
            search_type="Simple text-based search"
        )
        print(f"✓ Document saved with ID: {doc_id}")
        
        # Test getting stats
        stats = db.get_document_stats()
        print(f"✓ Database stats: {stats}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"✗ Database manager test failed: {e}")
        return False

def test_vector_search():
    """Test simple vector search."""
    print("\nTesting simple vector search...")
    
    try:
        from simple_vector_search import SimpleVectorSearch
        search = SimpleVectorSearch()
        
        # Test with sample text chunks
        chunks = [
            "This is a health insurance policy document.",
            "Coverage includes medical expenses and hospitalization.",
            "Deductible amount is $1000 per year.",
            "Claims must be filed within 30 days."
        ]
        
        search.build_index(chunks)
        print("✓ Search index built successfully")
        
        # Test search
        results = search.search("insurance coverage", k=2)
        print(f"✓ Search completed, found {len(results)} results")
        
        return True
        
    except Exception as e:
        print(f"✗ Vector search test failed: {e}")
        return False

def test_static_files():
    """Test that static files exist in public folders."""
    print("\nTesting static file structure...")
    
    # Check PDF files
    pdf_dir = "public/documents"
    if os.path.exists(pdf_dir):
        pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
        print(f"✓ Found {len(pdf_files)} PDF files in {pdf_dir}")
    else:
        print(f"✗ PDF directory {pdf_dir} not found")
        return False
    
    # Check markdown files
    docs_dir = "public/docs"
    if os.path.exists(docs_dir):
        md_files = [f for f in os.listdir(docs_dir) if f.endswith('.md')]
        print(f"✓ Found {len(md_files)} markdown files in {docs_dir}")
    else:
        print(f"✗ Docs directory {docs_dir} not found")
        return False
    
    return True

def main():
    """Run all tests."""
    print("DocQuery Vercel Optimization Test Suite")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_database_manager,
        test_vector_search,
        test_static_files
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! App is ready for Vercel deployment.")
        return 0
    else:
        print("✗ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())