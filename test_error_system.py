#!/usr/bin/env python3
"""
Test script to demonstrate the DocQuery error handling system.
"""

from error_codes import (
    DocQueryErrorCodes, 
    DocQueryException, 
    DocumentException, 
    AIException, 
    SearchException
)

def test_error_system():
    """Test the error handling system."""
    print("🔍 Testing DocQuery Error Handling System\n")
    
    # Test 1: List all error codes
    print("1. All Available Error Codes:")
    all_errors = DocQueryErrorCodes.get_all_errors()
    print(f"   Total error codes: {len(all_errors)}")
    
    categories = set(error.category for error in all_errors.values())
    print(f"   Categories: {', '.join(sorted(categories))}")
    print()
    
    # Test 2: Show errors by category
    print("2. Errors by Category:")
    for category in sorted(categories):
        category_errors = DocQueryErrorCodes.get_errors_by_category(category)
        print(f"   {category}: {len(category_errors)} errors")
        for code in list(category_errors.keys())[:2]:  # Show first 2
            print(f"     - {code}")
    print()
    
    # Test 3: Create and display specific errors
    print("3. Example Error Handling:")
    
    # Document error
    try:
        raise DocumentException(
            "DOCUMENT_NOT_FOUND",
            details={"file_path": "/nonexistent/document.pdf"}
        )
    except DocQueryException as e:
        print(f"   Document Error: {e.error_code}")
        print(f"   Message: {e.message}")
        print(f"   Solutions: {len(e.error_info.solutions)} available")
        print()
    
    # AI error
    try:
        raise AIException(
            "AI_MODEL_NOT_AVAILABLE",
            details={"model_name": "test-model"}
        )
    except DocQueryException as e:
        print(f"   AI Error: {e.error_code}")
        print(f"   Message: {e.message}")
        print(f"   Status Code: {e.error_info.status_code}")
        print()
    
    # Search error
    try:
        raise SearchException("SEARCH_QUERY_EMPTY")
    except DocQueryException as e:
        print(f"   Search Error: {e.error_code}")
        print(f"   Solutions:")
        for solution in e.error_info.solutions[:2]:
            print(f"     • {solution}")
        print()
    
    # Test 4: Error to dict conversion
    print("4. Error Dictionary Format:")
    try:
        raise DocumentException("DOCUMENT_FORMAT_UNSUPPORTED")
    except DocQueryException as e:
        error_dict = e.to_dict()
        print(f"   Error Code: {error_dict['error_code']}")
        print(f"   Category: {error_dict['category']}")
        print(f"   Status Code: {error_dict['status_code']}")
        print(f"   Has Solutions: {len(error_dict['solutions']) > 0}")
        print()
    
    print("✅ Error system test completed successfully!")

def test_document_processor():
    """Test document processor with error handling."""
    print("\n🔍 Testing Document Processor Error Handling\n")
    
    try:
        from document_processor import DocumentProcessor
        processor = DocumentProcessor()
        
        # Test with non-existent file
        try:
            processor.extract_text("/nonexistent/file.pdf")
        except DocumentException as e:
            print(f"✅ Caught expected error: {e.error_code}")
            print(f"   Details: {e.details}")
            print()
        
        print("✅ Document processor error handling working!")
        
    except ImportError as e:
        print(f"⚠️  Could not test document processor: {e}")

def main():
    """Run all tests."""
    print("=" * 60)
    print("DocQuery Error Code System Test")
    print("=" * 60)
    
    test_error_system()
    test_document_processor()
    
    print("\n" + "=" * 60)
    print("🎉 All tests completed!")
    print("Run 'streamlit run error_documentation.py' to see full documentation")
    print("=" * 60)

if __name__ == "__main__":
    main()