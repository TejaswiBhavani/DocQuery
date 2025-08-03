# DocQuery Error Code System

A comprehensive error handling and documentation system for the DocQuery application, inspired by Vercel's error documentation format.

## Overview

The error system provides structured, categorized error codes with detailed descriptions, causes, and solutions. Each error includes:

- **Unique Error Code**: Clear, descriptive identifiers (e.g., `DOCUMENT_NOT_FOUND`)
- **Category Classification**: Organized by component (Document, AI, Search, etc.)
- **HTTP-style Status Codes**: Standard status codes for API compatibility
- **Detailed Descriptions**: Clear explanations of what went wrong
- **Cause Analysis**: Common reasons why the error occurs
- **Solution Guidance**: Step-by-step solutions to resolve the error

## Error Categories

### 📄 Document Errors
- `DOCUMENT_NOT_FOUND` (404) - File not found or inaccessible
- `DOCUMENT_FORMAT_UNSUPPORTED` (415) - Unsupported file format
- `DOCUMENT_EXTRACTION_FAILED` (422) - Text extraction failure
- `DOCUMENT_TOO_LARGE` (413) - File size exceeds limits

### 🤖 AI Errors
- `AI_MODEL_NOT_AVAILABLE` (503) - AI model loading failure
- `AI_PROCESSING_TIMEOUT` (504) - Analysis timeout
- `AI_API_KEY_INVALID` (401) - Invalid API credentials
- `AI_ANALYSIS_FAILED` (500) - General analysis failure

### 🔍 Search Errors
- `SEARCH_INDEX_NOT_BUILT` (500) - Search index not initialized
- `SEARCH_QUERY_EMPTY` (400) - Empty or invalid query
- `SEARCH_NO_RESULTS` (404) - No matching content found

### 🗄️ Database Errors
- `DATABASE_CONNECTION_FAILED` (503) - Database connection issues
- `DATABASE_SAVE_FAILED` (500) - Data save operation failure

### ⚙️ Configuration Errors
- `CONFIG_INVALID` (400) - Invalid system configuration

### ⚡ Internal Errors
- `INTERNAL_SYSTEM_ERROR` (500) - Unexpected system failure
- `MEMORY_INSUFFICIENT` (507) - Insufficient system memory

## Usage

### Basic Error Handling

```python
from error_codes import DocumentException

try:
    # Document processing code
    pass
except DocumentException as e:
    print(f"Error: {e.error_code}")
    print(f"Message: {e.message}")
    for solution in e.error_info.solutions:
        print(f"Solution: {solution}")
```

### Creating Custom Errors

```python
from error_codes import DocumentException

# Raise a specific error with details
raise DocumentException(
    "DOCUMENT_NOT_FOUND",
    details={"file_path": "/path/to/file.pdf"}
)
```

### Error Dictionary Format

```python
try:
    # Some operation
    pass
except DocQueryException as e:
    error_dict = e.to_dict()
    # Returns structured error information
    {
        "error_code": "DOCUMENT_NOT_FOUND",
        "message": "The specified document file could not be found...",
        "category": "Document",
        "status_code": 404,
        "title": "Document Not Found",
        "causes": ["File path is incorrect", ...],
        "solutions": ["Verify the file path is correct", ...],
        "details": {"file_path": "/path/to/file.pdf"}
    }
```

## Error Documentation

### View Full Documentation

```bash
# Run the error documentation page
streamlit run error_documentation.py
```

This opens a comprehensive documentation page similar to Vercel's error documentation, showing:

- Complete list of all error codes
- Categorized error listings
- Detailed error descriptions
- Common causes and solutions
- Search functionality

### Integration in Main App

The main DocQuery application (`app.py`) automatically uses structured error handling:

- Displays errors with proper formatting
- Shows solution suggestions
- Links to full error documentation
- Maintains user-friendly error messages

## File Structure

```
├── error_codes.py              # Error definitions and classes
├── error_documentation.py     # Streamlit documentation page
├── test_error_system.py       # Test script for error system
├── app.py                     # Main app with integrated error handling
├── document_processor.py     # Updated with structured errors
├── vector_search.py          # Updated with structured errors
└── enhanced_vector_search.py # Updated with structured errors
```

## Testing

Run the test script to verify the error system:

```bash
python test_error_system.py
```

This tests:
- Error code loading and categorization
- Exception creation and handling
- Error dictionary conversion
- Integration with existing modules

## Benefits

1. **Consistency**: Standardized error handling across the application
2. **User Experience**: Clear, actionable error messages with solutions
3. **Developer Experience**: Structured error information for debugging
4. **Documentation**: Comprehensive error reference similar to enterprise systems
5. **Maintainability**: Centralized error definitions and management
6. **API Compatibility**: HTTP status codes for potential API integration

## Adding New Errors

To add new error codes:

1. Define the error in `error_codes.py`:
```python
NEW_ERROR_CODE = ErrorInfo(
    code="NEW_ERROR_CODE",
    category="Category",
    status_code=400,
    title="Error Title",
    description="Error description",
    causes=["Cause 1", "Cause 2"],
    solutions=["Solution 1", "Solution 2"]
)
```

2. Update the appropriate exception class if needed
3. The error documentation page will automatically include the new error
4. Test the new error code

## Comparison with Vercel Error System

| Feature | Vercel | DocQuery |
|---------|---------|----------|
| Structured Codes | ✅ | ✅ |
| Categorization | ✅ | ✅ |
| Status Codes | ✅ | ✅ |
| Documentation Page | ✅ | ✅ |
| Solution Guidance | ✅ | ✅ |
| Search Functionality | ✅ | ✅ |
| Integration | ✅ | ✅ |

The DocQuery error system follows the same principles as Vercel's error documentation while being tailored for document analysis workflows.