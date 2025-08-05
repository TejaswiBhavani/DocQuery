"""
Blob Downloader - Handles downloading documents from URLs
"""
import os
import tempfile
import httpx
import aiofiles
from typing import Optional, Tuple
from urllib.parse import urlparse, unquote
import logging

logger = logging.getLogger(__name__)

class BlobDownloader:
    """Handles downloading documents from blob URLs or other sources."""
    
    def __init__(self, timeout: int = 30, max_size: int = 100 * 1024 * 1024):  # 100MB max
        """
        Initialize the blob downloader.
        
        Args:
            timeout: Request timeout in seconds
            max_size: Maximum file size in bytes
        """
        self.timeout = timeout
        self.max_size = max_size
        
    async def download_document(self, url: str) -> Tuple[str, str]:
        """
        Download document from URL and save to temporary file.
        Supports HTTP/HTTPS URLs and local file:// URLs for testing.
        
        Args:
            url: Document URL to download
            
        Returns:
            Tuple of (temp_file_path, original_filename)
            
        Raises:
            Exception: If download fails or file is too large
        """
        try:
            # Handle local file URLs for testing
            if url.startswith('file://'):
                return await self._handle_local_file(url)
            
            # Parse URL to get filename
            parsed_url = urlparse(url)
            original_filename = self._extract_filename(url)
            
            # Determine file extension
            file_extension = self._get_file_extension(original_filename, url)
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Stream download to check size
                async with client.stream('GET', url) as response:
                    response.raise_for_status()
                    
                    # Check content length if available
                    content_length = response.headers.get('content-length')
                    if content_length and int(content_length) > self.max_size:
                        raise Exception(f"File too large: {content_length} bytes (max: {self.max_size})")
                    
                    # Create temporary file
                    temp_file = tempfile.NamedTemporaryFile(
                        delete=False, 
                        suffix=file_extension,
                        prefix="downloaded_doc_"
                    )
                    temp_file_path = temp_file.name
                    temp_file.close()
                    
                    # Download file in chunks
                    downloaded_size = 0
                    async with aiofiles.open(temp_file_path, 'wb') as f:
                        async for chunk in response.aiter_bytes(chunk_size=8192):
                            downloaded_size += len(chunk)
                            
                            # Check size limit
                            if downloaded_size > self.max_size:
                                os.unlink(temp_file_path)  # Clean up
                                raise Exception(f"File too large: {downloaded_size} bytes (max: {self.max_size})")
                            
                            await f.write(chunk)
                    
                    logger.info(f"Downloaded document: {original_filename} ({downloaded_size} bytes)")
                    return temp_file_path, original_filename
                    
        except httpx.RequestError as e:
            raise Exception(f"Network error downloading document: {str(e)}")
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP error downloading document: {e.response.status_code} {e.response.reason_phrase}")
        except Exception as e:
            if "temp_file_path" in locals() and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)  # Clean up on error
            raise Exception(f"Error downloading document: {str(e)}")
    
    async def _handle_local_file(self, file_url: str) -> Tuple[str, str]:
        """Handle local file:// URLs for testing."""
        try:
            # Extract file path from URL
            file_path = file_url.replace('file://', '')
            
            if not os.path.exists(file_path):
                raise Exception(f"Local file not found: {file_path}")
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > self.max_size:
                raise Exception(f"File too large: {file_size} bytes (max: {self.max_size})")
            
            # Get original filename
            original_filename = os.path.basename(file_path)
            
            # Get file extension
            file_extension = os.path.splitext(file_path)[1] or '.pdf'
            
            # Create temporary copy
            temp_file = tempfile.NamedTemporaryFile(
                delete=False, 
                suffix=file_extension,
                prefix="local_doc_"
            )
            temp_file_path = temp_file.name
            temp_file.close()
            
            # Copy file content
            async with aiofiles.open(file_path, 'rb') as src, aiofiles.open(temp_file_path, 'wb') as dst:
                async for chunk in self._async_read_chunks(src):
                    await dst.write(chunk)
            
            logger.info(f"Loaded local document: {original_filename} ({file_size} bytes)")
            return temp_file_path, original_filename
            
        except Exception as e:
            if "temp_file_path" in locals() and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            raise Exception(f"Error loading local file: {str(e)}")
    
    async def _async_read_chunks(self, file_obj, chunk_size: int = 8192):
        """Async generator to read file in chunks."""
        while True:
            chunk = await file_obj.read(chunk_size)
            if not chunk:
                break
            yield chunk
    
    def _extract_filename(self, url: str) -> str:
        """Extract filename from URL."""
        try:
            parsed_url = urlparse(url)
            # Get filename from path
            path = unquote(parsed_url.path)
            filename = os.path.basename(path)
            
            if not filename or filename == '/':
                # Try to get from query parameters
                if 'filename' in parsed_url.query:
                    from urllib.parse import parse_qs
                    params = parse_qs(parsed_url.query)
                    if 'filename' in params:
                        filename = params['filename'][0]
                else:
                    filename = "downloaded_document"
            
            return filename
        except Exception:
            return "downloaded_document"
    
    def _get_file_extension(self, filename: str, url: str) -> str:
        """Determine file extension from filename or URL."""
        # Try to get extension from filename
        if '.' in filename:
            ext = os.path.splitext(filename)[1].lower()
            if ext in ['.pdf', '.docx', '.doc', '.txt', '.eml']:
                return ext
        
        # Try to guess from URL
        if '.pdf' in url.lower():
            return '.pdf'
        elif '.docx' in url.lower():
            return '.docx'
        elif '.doc' in url.lower():
            return '.doc'
        elif '.txt' in url.lower():
            return '.txt'
        elif '.eml' in url.lower():
            return '.eml'
        
        # Default to .pdf for blob URLs (common case)
        return '.pdf'
    
    def cleanup_temp_file(self, temp_file_path: str) -> None:
        """Clean up temporary file."""
        try:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                logger.debug(f"Cleaned up temporary file: {temp_file_path}")
        except Exception as e:
            logger.warning(f"Failed to clean up temporary file {temp_file_path}: {str(e)}")


class SyncBlobDownloader:
    """Synchronous version of blob downloader for compatibility."""
    
    def __init__(self, timeout: int = 30, max_size: int = 100 * 1024 * 1024):
        self.timeout = timeout
        self.max_size = max_size
    
    def download_document(self, url: str) -> Tuple[str, str]:
        """
        Synchronously download document from URL.
        
        Args:
            url: Document URL to download
            
        Returns:
            Tuple of (temp_file_path, original_filename)
        """
        try:
            # Parse URL to get filename
            parsed_url = urlparse(url)
            original_filename = self._extract_filename(url)
            
            # Determine file extension
            file_extension = self._get_file_extension(original_filename, url)
            
            with httpx.Client(timeout=self.timeout) as client:
                # Download file
                response = client.get(url)
                response.raise_for_status()
                
                # Check size
                content_length = len(response.content)
                if content_length > self.max_size:
                    raise Exception(f"File too large: {content_length} bytes (max: {self.max_size})")
                
                # Create temporary file
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False, 
                    suffix=file_extension,
                    prefix="downloaded_doc_"
                )
                
                # Write content
                temp_file.write(response.content)
                temp_file_path = temp_file.name
                temp_file.close()
                
                logger.info(f"Downloaded document: {original_filename} ({content_length} bytes)")
                return temp_file_path, original_filename
                
        except httpx.RequestError as e:
            raise Exception(f"Network error downloading document: {str(e)}")
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP error downloading document: {e.response.status_code}")
        except Exception as e:
            raise Exception(f"Error downloading document: {str(e)}")
    
    def _extract_filename(self, url: str) -> str:
        """Extract filename from URL."""
        try:
            parsed_url = urlparse(url)
            path = unquote(parsed_url.path)
            filename = os.path.basename(path)
            
            if not filename or filename == '/':
                filename = "downloaded_document"
            
            return filename
        except Exception:
            return "downloaded_document"
    
    def _get_file_extension(self, filename: str, url: str) -> str:
        """Determine file extension from filename or URL."""
        if '.' in filename:
            ext = os.path.splitext(filename)[1].lower()
            if ext in ['.pdf', '.docx', '.doc', '.txt', '.eml']:
                return ext
        
        if '.pdf' in url.lower():
            return '.pdf'
        elif '.docx' in url.lower():
            return '.docx'
        elif '.doc' in url.lower():
            return '.doc'
        elif '.txt' in url.lower():
            return '.txt'
        elif '.eml' in url.lower():
            return '.eml'
        
        return '.pdf'
    
    def cleanup_temp_file(self, temp_file_path: str) -> None:
        """Clean up temporary file."""
        try:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        except Exception as e:
            logger.warning(f"Failed to clean up temporary file {temp_file_path}: {str(e)}")