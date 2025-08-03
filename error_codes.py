"""
DocQuery Error Code System

This module defines structured error codes for the DocQuery application,
similar to Vercel's error documentation system. Each error has a specific
code, category, description, and suggested solutions.
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ErrorInfo:
    """Information about a specific error code."""
    code: str
    category: str
    status_code: int
    title: str
    description: str
    causes: List[str]
    solutions: List[str]
    documentation_url: Optional[str] = None


class ErrorCategory(Enum):
    """Error categories for DocQuery system."""
    DOCUMENT = "Document"
    AI = "AI"
    DATABASE = "Database" 
    SEARCH = "Search"
    CONFIG = "Configuration"
    NETWORK = "Network"
    INTERNAL = "Internal"


class DocQueryErrorCodes:
    """Central repository of DocQuery error codes and information."""
    
    # Document Processing Errors
    DOCUMENT_NOT_FOUND = ErrorInfo(
        code="DOCUMENT_NOT_FOUND",
        category="Document",
        status_code=404,
        title="Document Not Found",
        description="The specified document file could not be found or accessed.",
        causes=[
            "File path is incorrect",
            "File has been moved or deleted",
            "Insufficient permissions to access file",
            "Network drive unavailable"
        ],
        solutions=[
            "Verify the file path is correct",
            "Check if the file exists in the specified location",
            "Ensure proper file permissions",
            "Try uploading the file again"
        ]
    )
    
    DOCUMENT_FORMAT_UNSUPPORTED = ErrorInfo(
        code="DOCUMENT_FORMAT_UNSUPPORTED",
        category="Document",
        status_code=415,
        title="Unsupported Document Format",
        description="The document format is not supported by the processing system.",
        causes=[
            "File format not in supported list (PDF, DOCX, TXT, EML)",
            "Corrupted file header",
            "File extension doesn't match content type",
            "Encrypted or password-protected document"
        ],
        solutions=[
            "Convert document to PDF, DOCX, TXT, or EML format",
            "Ensure file is not corrupted",
            "Remove password protection from document",
            "Check file extension matches content type"
        ]
    )
    
    DOCUMENT_EXTRACTION_FAILED = ErrorInfo(
        code="DOCUMENT_EXTRACTION_FAILED",
        category="Document",
        status_code=422,
        title="Text Extraction Failed",
        description="Failed to extract readable text content from the document.",
        causes=[
            "Document is corrupted or damaged",
            "Document contains only images without OCR text",
            "PDF is password-protected",
            "Unsupported PDF version or encoding"
        ],
        solutions=[
            "Ensure document is not corrupted",
            "Try converting to a different format",
            "Remove password protection",
            "Use a different version of the document"
        ]
    )
    
    DOCUMENT_TOO_LARGE = ErrorInfo(
        code="DOCUMENT_TOO_LARGE",
        category="Document",
        status_code=413,
        title="Document Size Exceeds Limit",
        description="The uploaded document exceeds the maximum size limit.",
        causes=[
            "File size larger than 200MB limit",
            "Document contains high-resolution images",
            "Document has extensive formatting data"
        ],
        solutions=[
            "Compress the document",
            "Split large document into smaller parts",
            "Remove unnecessary images or formatting",
            "Convert to a more efficient format"
        ]
    )
    
    # AI Processing Errors
    AI_MODEL_NOT_AVAILABLE = ErrorInfo(
        code="AI_MODEL_NOT_AVAILABLE",
        category="AI",
        status_code=503,
        title="AI Model Unavailable",
        description="The required AI model is not available or failed to load.",
        causes=[
            "Model files not downloaded",
            "Insufficient memory to load model",
            "Model dependency missing",
            "Network connectivity issues"
        ],
        solutions=[
            "Install required model dependencies",
            "Free up system memory",
            "Check internet connection for model download",
            "Switch to Local AI mode"
        ]
    )
    
    AI_PROCESSING_TIMEOUT = ErrorInfo(
        code="AI_PROCESSING_TIMEOUT",
        category="AI",
        status_code=504,
        title="AI Processing Timeout",
        description="AI analysis took longer than the allowed time limit.",
        causes=[
            "Document too complex for processing",
            "System overloaded with requests",
            "AI model running slowly",
            "Network latency with external AI service"
        ],
        solutions=[
            "Try with a smaller document",
            "Simplify the query",
            "Wait and try again later",
            "Switch to Local AI for faster processing"
        ]
    )
    
    AI_API_KEY_INVALID = ErrorInfo(
        code="AI_API_KEY_INVALID",
        category="AI",
        status_code=401,
        title="Invalid API Key",
        description="The provided AI service API key is invalid or expired.",
        causes=[
            "API key is incorrect",
            "API key has expired",
            "API key lacks required permissions",
            "API key quota exceeded"
        ],
        solutions=[
            "Verify API key is correctly entered",
            "Generate a new API key",
            "Check API key permissions and quota",
            "Switch to Local AI mode as alternative"
        ]
    )
    
    AI_ANALYSIS_FAILED = ErrorInfo(
        code="AI_ANALYSIS_FAILED",
        category="AI",
        status_code=500,
        title="AI Analysis Failed",
        description="The AI system failed to analyze the query and document.",
        causes=[
            "Query too complex or ambiguous",
            "Document content incompatible with analysis",
            "AI model encountered an error",
            "Insufficient context for analysis"
        ],
        solutions=[
            "Rephrase the query more clearly",
            "Provide more specific details in query",
            "Try with a different document",
            "Switch between Local AI and OpenAI"
        ]
    )
    
    # Search Engine Errors
    SEARCH_INDEX_NOT_BUILT = ErrorInfo(
        code="SEARCH_INDEX_NOT_BUILT",
        category="Search",
        status_code=500,
        title="Search Index Not Built",
        description="The search index has not been built for the document.",
        causes=[
            "Document processing incomplete",
            "Index building failed",
            "Document chunks empty",
            "System memory insufficient"
        ],
        solutions=[
            "Re-upload and process the document",
            "Ensure document contains text content",
            "Free up system memory",
            "Try with a smaller document"
        ]
    )
    
    SEARCH_QUERY_EMPTY = ErrorInfo(
        code="SEARCH_QUERY_EMPTY",
        category="Search",
        status_code=400,
        title="Empty Search Query",
        description="The search query is empty or contains no searchable content.",
        causes=[
            "Query field left blank",
            "Query contains only special characters",
            "Query too short to be meaningful"
        ],
        solutions=[
            "Enter a descriptive query",
            "Include specific details about your request",
            "Use natural language descriptions",
            "Try one of the example queries"
        ]
    )
    
    SEARCH_NO_RESULTS = ErrorInfo(
        code="SEARCH_NO_RESULTS",
        category="Search",
        status_code=404,
        title="No Search Results Found",
        description="No relevant content found in the document for the given query.",
        causes=[
            "Query terms not present in document",
            "Query too specific",
            "Document doesn't contain relevant information",
            "Search algorithm couldn't find matches"
        ],
        solutions=[
            "Try broader or alternative search terms",
            "Rephrase the query",
            "Check if the document contains relevant content",
            "Use different keywords or synonyms"
        ]
    )
    
    # Database Errors
    DATABASE_CONNECTION_FAILED = ErrorInfo(
        code="DATABASE_CONNECTION_FAILED",
        category="Database",
        status_code=503,
        title="Database Connection Failed",
        description="Unable to establish connection to the database system.",
        causes=[
            "Database server unavailable",
            "Incorrect connection credentials",
            "Network connectivity issues",
            "Database service not running"
        ],
        solutions=[
            "Check database server status",
            "Verify connection credentials",
            "Test network connectivity",
            "Application will continue without database features"
        ]
    )
    
    DATABASE_SAVE_FAILED = ErrorInfo(
        code="DATABASE_SAVE_FAILED",
        category="Database",
        status_code=500,
        title="Database Save Operation Failed",
        description="Failed to save data to the database.",
        causes=[
            "Database disk space full",
            "Data validation errors",
            "Database locks or conflicts",
            "Connection lost during operation"
        ],
        solutions=[
            "Check database disk space",
            "Verify data format and constraints",
            "Retry the operation",
            "Results are still available in current session"
        ]
    )
    
    # Configuration Errors
    CONFIG_INVALID = ErrorInfo(
        code="CONFIG_INVALID",
        category="Configuration",
        status_code=400,
        title="Invalid Configuration",
        description="The system configuration contains invalid or missing values.",
        causes=[
            "Missing required environment variables",
            "Invalid configuration file format",
            "Conflicting configuration settings",
            "Outdated configuration schema"
        ],
        solutions=[
            "Check all required environment variables are set",
            "Validate configuration file format",
            "Review configuration documentation",
            "Reset to default configuration if needed"
        ]
    )
    
    # Internal System Errors
    INTERNAL_SYSTEM_ERROR = ErrorInfo(
        code="INTERNAL_SYSTEM_ERROR",
        category="Internal",
        status_code=500,
        title="Internal System Error",
        description="An unexpected internal error occurred in the system.",
        causes=[
            "Unexpected software bug",
            "System resource exhaustion",
            "Hardware failure",
            "Dependency service failure"
        ],
        solutions=[
            "Try refreshing the page and retrying",
            "Report the error with steps to reproduce",
            "Check system resources and restart if needed",
            "Contact support if the error persists"
        ]
    )
    
    MEMORY_INSUFFICIENT = ErrorInfo(
        code="MEMORY_INSUFFICIENT",
        category="Internal",
        status_code=507,
        title="Insufficient Memory",
        description="The system has insufficient memory to complete the operation.",
        causes=[
            "Document too large for available memory",
            "Multiple documents processed simultaneously",
            "System memory leak",
            "Other applications consuming memory"
        ],
        solutions=[
            "Try with a smaller document",
            "Close other applications to free memory",
            "Process one document at a time",
            "Restart the application if memory issues persist"
        ]
    )
    
    @classmethod
    def get_all_errors(cls) -> Dict[str, ErrorInfo]:
        """Get all error codes as a dictionary."""
        errors = {}
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, ErrorInfo):
                errors[attr.code] = attr
        return errors
    
    @classmethod
    def get_errors_by_category(cls, category: str) -> Dict[str, ErrorInfo]:
        """Get all errors for a specific category."""
        all_errors = cls.get_all_errors()
        return {code: error for code, error in all_errors.items() 
                if error.category.lower() == category.lower()}
    
    @classmethod
    def get_error_info(cls, error_code: str) -> Optional[ErrorInfo]:
        """Get error information for a specific error code."""
        all_errors = cls.get_all_errors()
        return all_errors.get(error_code)


class DocQueryException(Exception):
    """Base exception class for DocQuery application."""
    
    def __init__(self, error_code: str, message: str = None, details: Dict = None):
        self.error_code = error_code
        self.error_info = DocQueryErrorCodes.get_error_info(error_code)
        self.details = details or {}
        
        if message:
            self.message = message
        elif self.error_info:
            self.message = self.error_info.description
        else:
            self.message = f"Unknown error: {error_code}"
        
        super().__init__(self.message)
    
    def to_dict(self) -> Dict:
        """Convert exception to dictionary format."""
        result = {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }
        
        if self.error_info:
            result.update({
                "category": self.error_info.category,
                "status_code": self.error_info.status_code,
                "title": self.error_info.title,
                "causes": self.error_info.causes,
                "solutions": self.error_info.solutions
            })
        
        return result


# Specific exception classes for different categories
class DocumentException(DocQueryException):
    """Exception for document processing errors."""
    pass


class AIException(DocQueryException):
    """Exception for AI processing errors."""
    pass


class SearchException(DocQueryException):
    """Exception for search-related errors."""
    pass


class DatabaseException(DocQueryException):
    """Exception for database-related errors."""
    pass


class ConfigurationException(DocQueryException):
    """Exception for configuration errors."""
    pass