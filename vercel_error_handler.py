"""
Vercel Error Handler for DocQuery Application
Provides comprehensive error handling for Vercel-specific deployment and runtime errors.
"""

import logging
from typing import Dict, Any, Optional, Tuple, List
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from enum import Enum


class VercelErrorCategory(Enum):
    """Categories of Vercel errors."""
    APPLICATION = "Application"
    PLATFORM = "Platform"
    FUNCTION = "Function"
    DEPLOYMENT = "Deployment"
    DNS = "DNS"
    CACHE = "Cache"
    IMAGE = "Image"
    REQUEST = "Request"
    ROUTING = "Routing"
    RUNTIME = "Runtime"
    INTERNAL = "Internal"


class VercelErrorCode:
    """Vercel error codes with their HTTP status codes and categories."""
    
    # Application errors
    APPLICATION_ERRORS = {
        "BODY_NOT_A_STRING_FROM_FUNCTION": {"status": 502, "category": VercelErrorCategory.FUNCTION},
        "DEPLOYMENT_BLOCKED": {"status": 403, "category": VercelErrorCategory.DEPLOYMENT},
        "DEPLOYMENT_DELETED": {"status": 410, "category": VercelErrorCategory.DEPLOYMENT},
        "DEPLOYMENT_DISABLED": {"status": 402, "category": VercelErrorCategory.DEPLOYMENT},
        "DEPLOYMENT_NOT_FOUND": {"status": 404, "category": VercelErrorCategory.DEPLOYMENT},
        "DEPLOYMENT_NOT_READY_REDIRECTING": {"status": 303, "category": VercelErrorCategory.DEPLOYMENT},
        "DEPLOYMENT_PAUSED": {"status": 503, "category": VercelErrorCategory.DEPLOYMENT},
        "DNS_HOSTNAME_EMPTY": {"status": 502, "category": VercelErrorCategory.DNS},
        "DNS_HOSTNAME_NOT_FOUND": {"status": 502, "category": VercelErrorCategory.DNS},
        "DNS_HOSTNAME_RESOLVE_FAILED": {"status": 502, "category": VercelErrorCategory.DNS},
        "DNS_HOSTNAME_RESOLVED_PRIVATE": {"status": 404, "category": VercelErrorCategory.DNS},
        "DNS_HOSTNAME_SERVER_ERROR": {"status": 502, "category": VercelErrorCategory.DNS},
        "EDGE_FUNCTION_INVOCATION_FAILED": {"status": 500, "category": VercelErrorCategory.FUNCTION},
        "EDGE_FUNCTION_INVOCATION_TIMEOUT": {"status": 504, "category": VercelErrorCategory.FUNCTION},
        "FALLBACK_BODY_TOO_LARGE": {"status": 502, "category": VercelErrorCategory.CACHE},
        "FUNCTION_INVOCATION_FAILED": {"status": 500, "category": VercelErrorCategory.FUNCTION},
        "FUNCTION_INVOCATION_TIMEOUT": {"status": 504, "category": VercelErrorCategory.FUNCTION},
        "FUNCTION_PAYLOAD_TOO_LARGE": {"status": 413, "category": VercelErrorCategory.FUNCTION},
        "FUNCTION_RESPONSE_PAYLOAD_TOO_LARGE": {"status": 500, "category": VercelErrorCategory.FUNCTION},
        "FUNCTION_THROTTLED": {"status": 503, "category": VercelErrorCategory.FUNCTION},
        "INFINITE_LOOP_DETECTED": {"status": 508, "category": VercelErrorCategory.RUNTIME},
        "INVALID_IMAGE_OPTIMIZE_REQUEST": {"status": 400, "category": VercelErrorCategory.IMAGE},
        "INVALID_REQUEST_METHOD": {"status": 405, "category": VercelErrorCategory.REQUEST},
        "MALFORMED_REQUEST_HEADER": {"status": 400, "category": VercelErrorCategory.REQUEST},
        "MICROFRONTENDS_MIDDLEWARE_ERROR": {"status": 500, "category": VercelErrorCategory.FUNCTION},
        "MIDDLEWARE_INVOCATION_FAILED": {"status": 500, "category": VercelErrorCategory.FUNCTION},
        "MIDDLEWARE_INVOCATION_TIMEOUT": {"status": 504, "category": VercelErrorCategory.FUNCTION},
        "MIDDLEWARE_RUNTIME_DEPRECATED": {"status": 503, "category": VercelErrorCategory.RUNTIME},
        "NO_RESPONSE_FROM_FUNCTION": {"status": 502, "category": VercelErrorCategory.FUNCTION},
        "NOT_FOUND": {"status": 404, "category": VercelErrorCategory.DEPLOYMENT},
        "OPTIMIZED_EXTERNAL_IMAGE_REQUEST_FAILED": {"status": 502, "category": VercelErrorCategory.IMAGE},
        "OPTIMIZED_EXTERNAL_IMAGE_REQUEST_INVALID": {"status": 502, "category": VercelErrorCategory.IMAGE},
        "OPTIMIZED_EXTERNAL_IMAGE_REQUEST_UNAUTHORIZED": {"status": 502, "category": VercelErrorCategory.IMAGE},
        "OPTIMIZED_EXTERNAL_IMAGE_TOO_MANY_REDIRECTS": {"status": 502, "category": VercelErrorCategory.IMAGE},
        "RANGE_END_NOT_VALID": {"status": 416, "category": VercelErrorCategory.REQUEST},
        "RANGE_GROUP_NOT_VALID": {"status": 416, "category": VercelErrorCategory.REQUEST},
        "RANGE_MISSING_UNIT": {"status": 416, "category": VercelErrorCategory.REQUEST},
        "RANGE_START_NOT_VALID": {"status": 416, "category": VercelErrorCategory.REQUEST},
        "RANGE_UNIT_NOT_SUPPORTED": {"status": 416, "category": VercelErrorCategory.REQUEST},
        "REQUEST_HEADER_TOO_LARGE": {"status": 431, "category": VercelErrorCategory.REQUEST},
        "RESOURCE_NOT_FOUND": {"status": 404, "category": VercelErrorCategory.REQUEST},
        "ROUTER_CANNOT_MATCH": {"status": 502, "category": VercelErrorCategory.ROUTING},
        "ROUTER_EXTERNAL_TARGET_CONNECTION_ERROR": {"status": 502, "category": VercelErrorCategory.ROUTING},
        "ROUTER_EXTERNAL_TARGET_ERROR": {"status": 502, "category": VercelErrorCategory.ROUTING},
        "ROUTER_EXTERNAL_TARGET_HANDSHAKE_ERROR": {"status": 502, "category": VercelErrorCategory.ROUTING},
        "ROUTER_TOO_MANY_HAS_SELECTIONS": {"status": 502, "category": VercelErrorCategory.ROUTING},
        "TOO_MANY_FILESYSTEM_CHECKS": {"status": 502, "category": VercelErrorCategory.ROUTING},
        "TOO_MANY_FORKS": {"status": 502, "category": VercelErrorCategory.ROUTING},
        "TOO_MANY_RANGES": {"status": 416, "category": VercelErrorCategory.REQUEST},
        "URL_TOO_LONG": {"status": 414, "category": VercelErrorCategory.REQUEST},
    }
    
    # Platform errors (all return 500 status)
    PLATFORM_ERRORS = {
        "FUNCTION_THROTTLED": {"status": 500, "category": VercelErrorCategory.INTERNAL},
        "INTERNAL_CACHE_ERROR": {"status": 500, "category": VercelErrorCategory.INTERNAL},
        "INTERNAL_CACHE_KEY_TOO_LONG": {"status": 500, "category": VercelErrorCategory.INTERNAL},
        "INTERNAL_CACHE_LOCK_FULL": {"status": 500, "category": VercelErrorCategory.INTERNAL},
        "INTERNAL_CACHE_LOCK_TIMEOUT": {"status": 500, "category": VercelErrorCategory.INTERNAL},
        "INTERNAL_DEPLOYMENT_FETCH_FAILED": {"status": 500, "category": VercelErrorCategory.INTERNAL},
        "INTERNAL_EDGE_FUNCTION_INVOCATION_FAILED": {"status": 500, "category": VercelErrorCategory.INTERNAL},
        "INTERNAL_EDGE_FUNCTION_INVOCATION_TIMEOUT": {"status": 500, "category": VercelErrorCategory.INTERNAL},
        "INTERNAL_FUNCTION_INVOCATION_FAILED": {"status": 500, "category": VercelErrorCategory.INTERNAL},
        "INTERNAL_FUNCTION_INVOCATION_TIMEOUT": {"status": 500, "category": VercelErrorCategory.INTERNAL},
        "INTERNAL_FUNCTION_NOT_FOUND": {"status": 500, "category": VercelErrorCategory.INTERNAL},
        "INTERNAL_FUNCTION_NOT_READY": {"status": 500, "category": VercelErrorCategory.INTERNAL},
        "INTERNAL_FUNCTION_SERVICE_UNAVAILABLE": {"status": 500, "category": VercelErrorCategory.INTERNAL},
        "INTERNAL_MICROFRONTENDS_BUILD_ERROR": {"status": 500, "category": VercelErrorCategory.INTERNAL},
        "INTERNAL_MICROFRONTENDS_INVALID_CONFIGURATION_ERROR": {"status": 500, "category": VercelErrorCategory.INTERNAL},
        "INTERNAL_MICROFRONTENDS_UNEXPECTED_ERROR": {"status": 500, "category": VercelErrorCategory.INTERNAL},
        "INTERNAL_MISSING_RESPONSE_FROM_CACHE": {"status": 500, "category": VercelErrorCategory.INTERNAL},
        "INTERNAL_OPTIMIZED_IMAGE_REQUEST_FAILED": {"status": 500, "category": VercelErrorCategory.INTERNAL},
        "INTERNAL_ROUTER_CANNOT_PARSE_PATH": {"status": 500, "category": VercelErrorCategory.INTERNAL},
        "INTERNAL_STATIC_REQUEST_FAILED": {"status": 500, "category": VercelErrorCategory.INTERNAL},
        "INTERNAL_UNARCHIVE_FAILED": {"status": 500, "category": VercelErrorCategory.INTERNAL},
        "INTERNAL_UNEXPECTED_ERROR": {"status": 500, "category": VercelErrorCategory.INTERNAL},
    }
    
    @classmethod
    def get_all_errors(cls) -> Dict[str, Dict[str, Any]]:
        """Get all Vercel error codes."""
        return {**cls.APPLICATION_ERRORS, **cls.PLATFORM_ERRORS}


class VercelErrorHandler:
    """Handles Vercel-specific errors and provides appropriate responses."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_codes = VercelErrorCode.get_all_errors()
    
    def get_all_errors(self) -> Dict[str, Dict[str, Any]]:
        """Get all Vercel error codes."""
        return self.error_codes
    
    def get_error_details(self, error_code: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific Vercel error code."""
        return self.error_codes.get(error_code)
    
    def is_vercel_error(self, error_code: str) -> bool:
        """Check if an error code is a known Vercel error."""
        return error_code in self.error_codes
    
    def create_error_response(
        self, 
        error_code: str, 
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Tuple[int, Dict[str, Any]]:
        """Create a standardized error response for Vercel errors."""
        
        error_info = self.get_error_details(error_code)
        if not error_info:
            # Unknown error code, default to 500
            status_code = 500
            category = VercelErrorCategory.INTERNAL
        else:
            status_code = error_info["status"]
            category = error_info["category"]
        
        response_data = {
            "error": {
                "code": error_code,
                "message": message or self._get_default_message(error_code, category),
                "category": category.value,
                "status": status_code,
                "vercel_error": True
            }
        }
        
        if details:
            response_data["error"]["details"] = details
        
        # Add context-specific suggestions
        suggestions = self._get_error_suggestions(error_code, category)
        if suggestions:
            response_data["error"]["suggestions"] = suggestions
        
        self.logger.error(f"Vercel error {error_code}: {response_data['error']['message']}")
        
        return status_code, response_data
    
    def _get_default_message(self, error_code: str, category: VercelErrorCategory) -> str:
        """Get a default error message for a Vercel error code."""
        
        category_messages = {
            VercelErrorCategory.FUNCTION: "Function execution error occurred",
            VercelErrorCategory.DEPLOYMENT: "Deployment-related error occurred",
            VercelErrorCategory.DNS: "DNS resolution error occurred",
            VercelErrorCategory.CACHE: "Cache operation error occurred",
            VercelErrorCategory.IMAGE: "Image processing error occurred",
            VercelErrorCategory.REQUEST: "Request processing error occurred",
            VercelErrorCategory.ROUTING: "Routing error occurred",
            VercelErrorCategory.RUNTIME: "Runtime error occurred",
            VercelErrorCategory.INTERNAL: "Internal platform error occurred",
        }
        
        # Specific messages for common errors
        specific_messages = {
            "FUNCTION_INVOCATION_TIMEOUT": "Function execution timed out",
            "FUNCTION_PAYLOAD_TOO_LARGE": "Request payload exceeds size limit",
            "DEPLOYMENT_NOT_FOUND": "Deployment not found or has been removed",
            "NOT_FOUND": "Resource not found",
            "INVALID_REQUEST_METHOD": "HTTP method not allowed for this endpoint",
            "REQUEST_HEADER_TOO_LARGE": "Request headers exceed size limit",
            "URL_TOO_LONG": "Request URL exceeds maximum length",
            "INFINITE_LOOP_DETECTED": "Infinite loop detected in function execution",
        }
        
        return specific_messages.get(error_code, category_messages.get(category, "An error occurred"))
    
    def _get_error_suggestions(self, error_code: str, category: VercelErrorCategory) -> List[str]:
        """Get suggestions for resolving specific Vercel errors."""
        
        suggestions = {
            "FUNCTION_INVOCATION_TIMEOUT": [
                "Optimize your function to execute faster",
                "Consider breaking down large operations into smaller chunks",
                "Check for potential deadlocks or infinite loops",
                "Increase function timeout if possible"
            ],
            "FUNCTION_PAYLOAD_TOO_LARGE": [
                "Reduce the size of your request payload",
                "Consider using file uploads for large data",
                "Split large requests into multiple smaller ones",
                "Use compression for request bodies"
            ],
            "DEPLOYMENT_NOT_FOUND": [
                "Verify the deployment URL is correct",
                "Check if the deployment has been deleted",
                "Ensure you have access to the deployment",
                "Try redeploying the application"
            ],
            "NOT_FOUND": [
                "Check the endpoint URL for typos",
                "Verify the route exists in your application",
                "Ensure the resource hasn't been moved or deleted",
                "Check your routing configuration"
            ],
            "INVALID_REQUEST_METHOD": [
                "Use the correct HTTP method (GET, POST, PUT, DELETE)",
                "Check your API documentation for allowed methods",
                "Verify your client is sending the right method",
                "Update your request configuration"
            ],
            "REQUEST_HEADER_TOO_LARGE": [
                "Reduce the size of request headers",
                "Remove unnecessary headers",
                "Use shorter header values where possible",
                "Consider moving large data to request body"
            ],
            "INFINITE_LOOP_DETECTED": [
                "Review your code for infinite loops",
                "Add proper exit conditions to loops",
                "Check recursive function calls",
                "Implement timeout mechanisms in your code"
            ],
            "INTERNAL_FUNCTION_INVOCATION_FAILED": [
                "Contact Vercel support for platform issues",
                "Check Vercel status page for ongoing incidents",
                "Try redeploying your function",
                "Monitor function logs for more details"
            ]
        }
        
        # Category-level suggestions
        category_suggestions = {
            VercelErrorCategory.FUNCTION: [
                "Review function execution time and memory usage",
                "Check function logs for detailed error information",
                "Ensure function dependencies are properly configured"
            ],
            VercelErrorCategory.DEPLOYMENT: [
                "Check deployment status in Vercel dashboard",
                "Verify deployment configuration",
                "Try redeploying the application"
            ],
            VercelErrorCategory.DNS: [
                "Check domain configuration in Vercel dashboard",
                "Verify DNS settings with your domain provider",
                "Allow time for DNS propagation"
            ],
            VercelErrorCategory.INTERNAL: [
                "Contact Vercel support for platform issues",
                "Check Vercel status page for ongoing incidents",
                "Try the operation again after a short delay"
            ]
        }
        
        return suggestions.get(error_code, category_suggestions.get(category, []))
    
    def handle_application_error(self, error: Exception, context: str = "") -> JSONResponse:
        """Handle application errors and map them to appropriate Vercel error codes."""
        
        error_message = str(error).lower()
        
        # Map common application errors to Vercel error codes
        if "timeout" in error_message:
            error_code = "FUNCTION_INVOCATION_TIMEOUT"
        elif "payload too large" in error_message or "request entity too large" in error_message:
            error_code = "FUNCTION_PAYLOAD_TOO_LARGE"
        elif "not found" in error_message and "deployment" in error_message:
            error_code = "DEPLOYMENT_NOT_FOUND"
        elif "not found" in error_message:
            error_code = "NOT_FOUND"
        elif "method not allowed" in error_message:
            error_code = "INVALID_REQUEST_METHOD"
        elif "header" in error_message and "too large" in error_message:
            error_code = "REQUEST_HEADER_TOO_LARGE"
        elif "url too long" in error_message or "uri too long" in error_message:
            error_code = "URL_TOO_LONG"
        elif "infinite loop" in error_message or "recursion" in error_message:
            error_code = "INFINITE_LOOP_DETECTED"
        elif "function" in error_message and "failed" in error_message:
            error_code = "FUNCTION_INVOCATION_FAILED"
        else:
            # Default to generic internal error
            error_code = "INTERNAL_UNEXPECTED_ERROR"
        
        status_code, response_data = self.create_error_response(
            error_code,
            message=str(error),
            details={"context": context} if context else None
        )
        
        return JSONResponse(
            status_code=status_code,
            content=response_data
        )
    
    def create_http_exception(self, error_code: str, message: Optional[str] = None) -> HTTPException:
        """Create an HTTPException with proper Vercel error formatting."""
        
        status_code, response_data = self.create_error_response(error_code, message)
        
        return HTTPException(
            status_code=status_code,
            detail=response_data["error"]
        )


# Global instance
vercel_error_handler = VercelErrorHandler()