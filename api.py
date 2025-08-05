"""
FastAPI Backend for DocQuery - LLM-Powered Intelligent Query-Retrieval System
"""
import os
import time
import logging
import asyncio
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Import our components
from blob_downloader import BlobDownloader
from document_processor import DocumentProcessor
from batch_processor import BatchProcessor
from output_formatter import OutputFormatter

# Import Vercel error handler
try:
    from vercel_error_handler import vercel_error_handler
    VERCEL_SUPPORT = True
except ImportError:
    VERCEL_SUPPORT = False
    vercel_error_handler = None

# Try to import vector search with fallbacks
try:
    from vector_search import VectorSearch
    SEARCH_TYPE = "Advanced semantic search with sentence transformers"
except ImportError:
    try:
        from enhanced_vector_search import EnhancedVectorSearch as VectorSearch
        SEARCH_TYPE = "Enhanced semantic search with TF-IDF"
    except ImportError:
        from simple_vector_search import SimpleVectorSearch as VectorSearch
        SEARCH_TYPE = "Simple text-based search"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Authentication
BEARER_TOKEN = "b22f8e46c05cd2c3006ae987bbc9c24ca023045b4af9b189e5d3fe340b91514c"
security = HTTPBearer()

# Global components
app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup application state."""
    logger.info("Starting DocQuery API...")
    
    # Initialize global components
    app_state["blob_downloader"] = BlobDownloader()
    app_state["document_processor"] = DocumentProcessor()
    app_state["output_formatter"] = OutputFormatter()
    
    logger.info(f"Initialized with search type: {SEARCH_TYPE}")
    yield
    
    # Cleanup
    logger.info("Shutting down DocQuery API...")
    app_state.clear()

# FastAPI app
app = FastAPI(
    title="DocQuery - LLM-Powered Intelligent Query-Retrieval System",
    description="An advanced document analysis system for insurance, legal, HR, and compliance domains",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class QueryRequest(BaseModel):
    """Request model for hackrx/run endpoint."""
    documents: str = Field(..., description="Document URL to process")
    questions: List[str] = Field(..., description="List of questions to analyze")

class QueryResponse(BaseModel):
    """Response model for hackrx/run endpoint."""
    answers: List[str] = Field(..., description="List of answers corresponding to the questions")

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    search_type: str
    version: str

# Dependency functions
async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify bearer token."""
    if credentials.credentials != BEARER_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

# API Endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "DocQuery API - LLM-Powered Intelligent Query-Retrieval System",
        "status": "active",
        "docs_url": "/docs",
        "api_version": "v1"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        search_type=SEARCH_TYPE,
        version="1.0.0"
    )

@app.post("/api/v1/hackrx/run", response_model=QueryResponse)
async def process_document_queries(
    request: QueryRequest,
    token: str = Depends(verify_token)
) -> QueryResponse:
    """
    Main endpoint for processing document queries.
    
    This endpoint handles the complete workflow:
    1. Download document from URL
    2. Extract and process text
    3. Build search index
    4. Process all questions
    5. Return structured answers
    """
    start_time = time.time()
    temp_file_path = None
    
    try:
        logger.info(f"Processing request with {len(request.questions)} questions")
        
        # Validate input
        if not request.documents or not request.documents.strip():
            if VERCEL_SUPPORT and vercel_error_handler:
                raise vercel_error_handler.create_http_exception("INVALID_REQUEST_METHOD", "Document URL is required")
            else:
                raise HTTPException(status_code=400, detail="Document URL is required")
        
        if not request.questions or len(request.questions) == 0:
            if VERCEL_SUPPORT and vercel_error_handler:
                raise vercel_error_handler.create_http_exception("INVALID_REQUEST_METHOD", "At least one question is required")
            else:
                raise HTTPException(status_code=400, detail="At least one question is required")
        
        # Step 1: Download document
        logger.info(f"Downloading document from: {request.documents}")
        blob_downloader = app_state["blob_downloader"]
        
        try:
            temp_file_path, original_filename = await blob_downloader.download_document(request.documents)
            logger.info(f"Downloaded document: {original_filename}")
        except Exception as e:
            if VERCEL_SUPPORT and vercel_error_handler:
                if "timeout" in str(e).lower():
                    raise vercel_error_handler.create_http_exception("FUNCTION_INVOCATION_TIMEOUT", f"Document download timed out: {str(e)}")
                elif "too large" in str(e).lower():
                    raise vercel_error_handler.create_http_exception("FUNCTION_PAYLOAD_TOO_LARGE", f"Document too large: {str(e)}")
                else:
                    raise vercel_error_handler.create_http_exception("FUNCTION_INVOCATION_FAILED", f"Failed to download document: {str(e)}")
            else:
                raise HTTPException(status_code=400, detail=f"Failed to download document: {str(e)}")
        
        # Step 2: Extract text from document
        logger.info("Extracting text from document...")
        document_processor = app_state["document_processor"]
        
        try:
            text_content = document_processor.extract_text(temp_file_path)
            if not text_content or len(text_content.strip()) < 100:
                if VERCEL_SUPPORT and vercel_error_handler:
                    raise vercel_error_handler.create_http_exception("RESOURCE_NOT_FOUND", "Document appears to be empty or too short")
                else:
                    raise HTTPException(status_code=400, detail="Document appears to be empty or too short")
            
            # Chunk the text
            document_chunks = document_processor.chunk_text(text_content)
            logger.info(f"Created {len(document_chunks)} text chunks")
            
        except Exception as e:
            if VERCEL_SUPPORT and vercel_error_handler:
                if "timeout" in str(e).lower():
                    raise vercel_error_handler.create_http_exception("FUNCTION_INVOCATION_TIMEOUT", f"Document processing timed out: {str(e)}")
                else:
                    raise vercel_error_handler.create_http_exception("FUNCTION_INVOCATION_FAILED", f"Failed to process document: {str(e)}")
            else:
                raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")
        
        # Step 3: Build search index with intelligent fallback
        logger.info("Building search index...")
        search_method_used = "unknown"
        
        try:
            # Try advanced search first
            vector_search = VectorSearch()
            vector_search.build_index(document_chunks)
            search_method_used = "Advanced semantic search"
            logger.info("Advanced search index built successfully")
        except Exception as e:
            logger.warning(f"Advanced search failed ({str(e)[:100]}...), trying enhanced search")
            try:
                # Fallback to enhanced TF-IDF search
                from enhanced_vector_search import EnhancedVectorSearch
                vector_search = EnhancedVectorSearch()
                vector_search.build_index(document_chunks)
                search_method_used = "Enhanced TF-IDF search"
                logger.info("Enhanced search index built successfully")
            except Exception as enhanced_error:
                logger.warning(f"Enhanced search failed, trying simple search: {str(enhanced_error)}")
                try:
                    # Final fallback to simple search
                    from simple_vector_search import SimpleVectorSearch
                    vector_search = SimpleVectorSearch()
                    vector_search.build_index(document_chunks)
                    search_method_used = "Simple text search"
                    logger.info("Simple search index built successfully")
                except Exception as simple_error:
                    if VERCEL_SUPPORT and vercel_error_handler:
                        raise vercel_error_handler.create_http_exception(
                            "FUNCTION_INVOCATION_FAILED", 
                            f"All search methods failed. Advanced: {str(e)[:50]}, Enhanced: {str(enhanced_error)[:50]}, Simple: {str(simple_error)[:50]}"
                        )
                    else:
                        raise HTTPException(
                            status_code=500,
                            detail=f"All search methods failed. Advanced: {str(e)[:50]}, Enhanced: {str(enhanced_error)[:50]}, Simple: {str(simple_error)[:50]}"
                        )
        
        # Step 4: Process questions
        logger.info(f"Processing {len(request.questions)} questions...")
        try:
            # Initialize batch processor
            batch_processor = BatchProcessor(
                use_openai=False,  # Use local AI by default for reliability
                max_workers=min(3, len(request.questions))  # Limit concurrency
            )
            
            # Process all questions
            answers = await batch_processor.process_questions(
                request.questions, 
                vector_search, 
                document_chunks
            )
            
            logger.info("All questions processed successfully")
            
        except Exception as e:
            if VERCEL_SUPPORT and vercel_error_handler:
                if "timeout" in str(e).lower():
                    raise vercel_error_handler.create_http_exception("FUNCTION_INVOCATION_TIMEOUT", f"Question processing timed out: {str(e)}")
                else:
                    raise vercel_error_handler.create_http_exception("FUNCTION_INVOCATION_FAILED", f"Failed to process questions: {str(e)}")
            else:
                raise HTTPException(status_code=500, detail=f"Failed to process questions: {str(e)}")
        
        # Step 5: Format and return response
        processing_time = time.time() - start_time
        logger.info(f"Request completed in {processing_time:.2f}s using {search_method_used}")
        
        return QueryResponse(answers=answers)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        
        # Use Vercel error handler if available
        if VERCEL_SUPPORT and vercel_error_handler:
            return vercel_error_handler.handle_application_error(e, "document_processing")
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )
    
    finally:
        # Cleanup temporary file
        if temp_file_path and app_state.get("blob_downloader"):
            app_state["blob_downloader"].cleanup_temp_file(temp_file_path)

@app.post("/api/v1/hackrx/run-with-openai", response_model=QueryResponse)
async def process_document_queries_openai(
    request: QueryRequest,
    openai_api_key: Optional[str] = None,
    token: str = Depends(verify_token)
) -> QueryResponse:
    """
    Alternative endpoint using OpenAI for enhanced analysis.
    
    Requires OpenAI API key as header: X-OpenAI-Key
    """
    if not openai_api_key:
        from fastapi import Header
        openai_api_key = Header(None, alias="X-OpenAI-Key")
    
    if not openai_api_key:
        raise HTTPException(
            status_code=400,
            detail="OpenAI API key required for this endpoint"
        )
    
    start_time = time.time()
    temp_file_path = None
    
    try:
        # Similar processing but with OpenAI
        logger.info(f"Processing request with OpenAI for {len(request.questions)} questions")
        
        # Download and process document (same as above)
        blob_downloader = app_state["blob_downloader"]
        temp_file_path, original_filename = await blob_downloader.download_document(request.documents)
        
        document_processor = app_state["document_processor"]
        text_content = document_processor.extract_text(temp_file_path)
        document_chunks = document_processor.chunk_text(text_content)
        
        # Build search index
        vector_search = VectorSearch()
        vector_search.build_index(document_chunks)
        
        # Process with OpenAI
        batch_processor = BatchProcessor(
            use_openai=True,
            api_key=openai_api_key,
            max_workers=min(2, len(request.questions))  # Lower concurrency for API limits
        )
        
        answers = await batch_processor.process_questions(
            request.questions, 
            vector_search, 
            document_chunks
        )
        
        processing_time = time.time() - start_time
        logger.info(f"OpenAI request completed in {processing_time:.2f}s")
        
        return QueryResponse(answers=answers)
        
    except Exception as e:
        logger.error(f"OpenAI processing error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"OpenAI processing failed: {str(e)}"
        )
    
    finally:
        if temp_file_path and app_state.get("blob_downloader"):
            app_state["blob_downloader"].cleanup_temp_file(temp_file_path)

# Additional utility endpoints
@app.get("/api/v1/status")
async def api_status():
    """Get API status and capabilities."""
    return {
        "status": "operational",
        "search_type": SEARCH_TYPE,
        "capabilities": {
            "document_formats": ["PDF", "DOCX", "TXT", "EML"],
            "max_file_size": "100MB",
            "concurrent_questions": "Up to 10",
            "ai_models": ["Local AI", "OpenAI GPT (with API key)"]
        },
        "endpoints": {
            "/api/v1/hackrx/run": "Main processing endpoint with local AI",
            "/api/v1/hackrx/run-with-openai": "Enhanced processing with OpenAI",
            "/health": "Health check",
            "/docs": "API documentation"
        }
    }

@app.get("/api/v1/vercel/status")
async def vercel_status():
    """Get Vercel deployment status and error handling capabilities."""
    vercel_env = os.getenv('VERCEL_DEPLOYMENT') == 'true' or os.getenv('VERCEL') == '1'
    
    response_data = {
        "vercel_deployment": vercel_env,
        "vercel_support": VERCEL_SUPPORT,
        "environment": {
            "vercel_env": os.getenv('VERCEL_ENV', 'unknown'),
            "vercel_region": os.getenv('VERCEL_REGION', 'unknown'),
            "vercel_url": os.getenv('VERCEL_URL', 'unknown'),
            "branch": os.getenv('VERCEL_GIT_COMMIT_REF', 'unknown'),
            "commit": os.getenv('VERCEL_GIT_COMMIT_SHA', 'unknown')[:8] if os.getenv('VERCEL_GIT_COMMIT_SHA') else 'unknown'
        },
        "error_handling": {
            "application_errors": len(vercel_error_handler.get_all_errors()) if VERCEL_SUPPORT else 0,
            "platform_errors": "All platform errors handled" if VERCEL_SUPPORT else "Limited",
            "supported_categories": ["Function", "Deployment", "DNS", "Cache", "Image", "Request", "Routing", "Runtime", "Internal"] if VERCEL_SUPPORT else []
        },
        "limits": {
            "function_timeout": "10s (Hobby), 60s (Pro)",
            "payload_size": "5MB",
            "memory": "1GB",
            "execution_duration": "30s max per request"
        }
    }
    
    return response_data

@app.get("/api/v1/vercel/errors")
async def vercel_error_codes():
    """Get all supported Vercel error codes."""
    if not VERCEL_SUPPORT:
        raise HTTPException(status_code=501, detail="Vercel error handling not available")
    
    error_codes = vercel_error_handler.get_all_errors()
    categorized_errors = {}
    
    for code, info in error_codes.items():
        category = info["category"].value
        if category not in categorized_errors:
            categorized_errors[category] = []
        
        categorized_errors[category].append({
            "code": code,
            "status": info["status"],
            "category": category
        })
    
    return {
        "total_errors": len(error_codes),
        "categories": categorized_errors,
        "documentation": "See Vercel documentation for detailed error descriptions"
    }

@app.post("/api/v1/vercel/test-error")
async def test_vercel_error(error_code: str):
    """Test endpoint for Vercel error handling."""
    if not VERCEL_SUPPORT:
        raise HTTPException(status_code=501, detail="Vercel error handling not available")
    
    if not vercel_error_handler.is_vercel_error(error_code):
        raise HTTPException(status_code=400, detail=f"Unknown Vercel error code: {error_code}")
    
    # Create a test error response
    raise vercel_error_handler.create_http_exception(error_code, f"Test error for code: {error_code}")

# Development server function
def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the FastAPI server."""
    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    # Run with development settings
    run_server(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True
    )

# Vercel serverless function handler
def handler(request):
    """Handler for Vercel serverless deployment."""
    import os
    from fastapi import Request
    from fastapi.responses import JSONResponse
    
    # Set up the app for serverless execution if not already done
    if not hasattr(handler, '_app_initialized'):
        os.environ.setdefault('VERCEL_DEPLOYMENT', 'true')
        handler._app_initialized = True
    
    # Return app instance for Vercel
    return app