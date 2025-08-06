"""
Enhanced error handling and user experience improvements for DocQuery.
Provides better error messages and graceful fallbacks.
Includes Vercel-specific error handling for deployment scenarios.
"""

import streamlit as st
import logging
import traceback
import os
from typing import Optional, Any, Dict
from dependency_checker import DependencyChecker

# Import Vercel error handler if FastAPI is available
try:
    from vercel_error_handler import vercel_error_handler, VercelErrorCategory
    VERCEL_SUPPORT = True
except ImportError:
    VERCEL_SUPPORT = False
    vercel_error_handler = None

class DocQueryErrorHandler:
    """Centralized error handling for better user experience."""
    
    def __init__(self):
        self.setup_logging()
        self.dependency_checker = DependencyChecker()
    
    def setup_logging(self):
        """Setup logging configuration."""
        import tempfile
        
        # Create log file in temporary directory
        temp_dir = tempfile.gettempdir()
        log_file = os.path.join(temp_dir, 'docquery.log')
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('DocQuery')
    
    def handle_file_upload_error(self, error: Exception, file_name: str) -> None:
        """Handle file upload and processing errors with user-friendly messages."""
        error_msg = str(error).lower()
        
        if 'docx' in file_name.lower() and 'docx' in error_msg:
            st.error("❌ **Word Document Error**")
            st.info("""
            📄 **Word document support requires additional setup:**
            ```bash
            pip install python-docx
            ```
            **Alternative**: Convert your Word document to PDF and try again.
            """)
        elif 'pdf' in error_msg and 'encrypted' in error_msg:
            st.error("🔒 **Encrypted PDF Detected**")
            st.info("""
            This PDF is password-protected and cannot be processed.
            
            **Solutions**:
            1. Remove password protection from the PDF
            2. Use a non-encrypted version
            3. Convert to plain text first
            """)
        elif 'no text content' in error_msg:
            st.error("📄 **No Text Found**")
            st.info("""
            This document appears to be image-based or has no extractable text.
            
            **Possible causes**:
            - Scanned document (image-only PDF)
            - Empty document
            - Corrupted file
            
            **Solutions**:
            - Use OCR software to convert images to text
            - Try a different version of the document
            """)
        else:
            st.error(f"❌ **Document Processing Error**")
            st.warning(f"Technical details: {str(error)}")
            st.info("""
            **Troubleshooting steps**:
            1. Check if the file is corrupted
            2. Try a different file format (PDF recommended)
            3. Ensure the file size is under 200MB
            """)
        
        self.logger.error(f"File processing error for {file_name}: {error}")
    
    def handle_ai_analysis_error(self, error: Exception, query: str) -> None:
        """Handle AI analysis errors with fallback suggestions."""
        st.error("🤖 **AI Analysis Error**")
        
        error_msg = str(error).lower()
        
        if 'api' in error_msg or 'openai' in error_msg:
            st.warning("**OpenAI API Issue Detected**")
            st.info("""
            **Quick fixes**:
            1. Check your OpenAI API key
            2. Verify you have sufficient API credits
            3. Switch to Local AI (no API key needed)
            """)
        elif 'token' in error_msg or 'rate limit' in error_msg:
            st.warning("**Rate Limit or Token Issue**")
            st.info("""
            **Solutions**:
            1. Wait a few minutes and try again
            2. Use a shorter query
            3. Switch to Local AI mode
            """)
        else:
            st.warning(f"Technical details: {str(error)}")
            st.info("""
            **Alternative approaches**:
            1. Try rephrasing your question
            2. Use simpler language
            3. Break down complex queries into smaller parts
            """)
        
        # Suggest capabilities improvement
        capabilities = self.dependency_checker.get_capabilities_summary()
        if not capabilities['advanced_ai']:
            st.info("""
            💡 **Enhance AI capabilities**: Install transformers for better local AI
            ```bash
            pip install transformers torch
            ```
            """)
        
        self.logger.error(f"AI analysis error for query '{query[:50]}...': {error}")
    
    def handle_vercel_deployment_error(self, error: Exception) -> None:
        """Handle Vercel deployment and runtime errors with specific guidance."""
        if not VERCEL_SUPPORT:
            self.handle_general_deployment_error(error)
            return
            
        error_msg = str(error).lower()
        
        # Check if this looks like a Vercel error
        is_vercel_env = os.getenv('VERCEL_DEPLOYMENT') == 'true' or os.getenv('VERCEL') == '1'
        
        if is_vercel_env:
            st.error("🔧 **Vercel Deployment Error**")
            
            # Common Vercel deployment issues
            if 'timeout' in error_msg:
                st.warning("**Function Timeout Detected**")
                st.info("""
                **Vercel Function Timeout Solutions:**
                1. Optimize document processing for faster execution
                2. Break down large operations into smaller chunks
                3. Consider using streaming responses for large documents
                4. Check for infinite loops in processing logic
                
                **Current limits**: 10s (Hobby), 60s (Pro)
                """)
            elif 'payload too large' in error_msg or 'entity too large' in error_msg:
                st.warning("**Payload Size Limit Exceeded**")
                st.info("""
                **Solutions for large payloads:**
                1. Reduce document size before upload
                2. Use file chunking for large documents
                3. Compress documents before processing
                4. Consider using external storage (S3, etc.)
                
                **Current limit**: 5MB for serverless functions
                """)
            elif 'deployment not found' in error_msg:
                st.warning("**Deployment Not Found**")
                st.info("""
                **Deployment issues:**
                1. Check if deployment was successful
                2. Verify the correct domain/URL
                3. Check Vercel dashboard for deployment status
                4. Try redeploying the application
                """)
            elif 'function invocation failed' in error_msg:
                st.warning("**Function Execution Failed**")
                st.info("""
                **Function execution issues:**
                1. Check function logs in Vercel dashboard
                2. Verify all dependencies are properly installed
                3. Test function locally before deployment
                4. Check memory and CPU usage limits
                """)
            else:
                st.warning(f"**Vercel Error**: {str(error)}")
                st.info("""
                **General Vercel troubleshooting:**
                1. Check Vercel dashboard for detailed logs
                2. Verify environment variables are set correctly
                3. Ensure all dependencies are in requirements.txt
                4. Try redeploying with latest changes
                """)
            
            # Show Vercel-specific debugging info
            with st.expander("🔍 Vercel Debugging Info", expanded=False):
                st.code(f"""
                Environment: {os.getenv('VERCEL_ENV', 'unknown')}
                Region: {os.getenv('VERCEL_REGION', 'unknown')}
                URL: {os.getenv('VERCEL_URL', 'unknown')}
                Function: {os.getenv('AWS_LAMBDA_FUNCTION_NAME', 'N/A')}
                Runtime: {os.getenv('AWS_EXECUTION_ENV', 'unknown')}
                """)
        else:
            self.handle_general_deployment_error(error)
        
        self.logger.error(f"Vercel deployment error: {error}")
    
    def handle_general_deployment_error(self, error: Exception) -> None:
        """Handle general deployment errors when not on Vercel."""
        st.error("🚀 **Deployment Error**")
        st.warning(f"Technical details: {str(error)}")
        st.info("""
        **Alternative deployment platforms:**
        1. **Heroku**: Great for Streamlit apps (`git push heroku main`)
        2. **Railway**: Easy GitHub integration
        3. **Render**: Free tier with GitHub connection
        4. **Streamlit Cloud**: Designed for Streamlit apps
        
        **For Vercel users**: See VERCEL_FIX.md for detailed guidance
        """)
    
    def check_vercel_environment(self) -> Dict[str, Any]:
        """Check if running in Vercel environment and return status."""
        vercel_info = {
            'is_vercel': os.getenv('VERCEL_DEPLOYMENT') == 'true' or os.getenv('VERCEL') == '1',
            'environment': os.getenv('VERCEL_ENV', 'unknown'),
            'region': os.getenv('VERCEL_REGION', 'unknown'),
            'url': os.getenv('VERCEL_URL', 'unknown'),
            'branch': os.getenv('VERCEL_GIT_COMMIT_REF', 'unknown'),
            'commit': os.getenv('VERCEL_GIT_COMMIT_SHA', 'unknown')[:8] if os.getenv('VERCEL_GIT_COMMIT_SHA') else 'unknown'
        }
        
        return vercel_info
        """Handle database connection and operation errors."""
        st.warning("💾 **Database Connection Issue**")
        st.info("""
        The app will continue to work without database features.
        
        **Missing features**:
        - Query history
        - Analytics dashboard
        - Persistent storage
        
        **To fix**: Check PostgreSQL connection settings
        """)
        
        self.logger.warning(f"Database error: {error}")
    
    def handle_search_error(self, error: Exception, query: str) -> None:
        """Handle vector search and indexing errors."""
        st.error("🔍 **Search Error**")
        
        capabilities = self.dependency_checker.get_capabilities_summary()
        
        if not capabilities['semantic_search']:
            st.info("""
            **Using basic text search** (fallback mode)
            
            📈 **Upgrade for better search**:
            ```bash
            pip install sentence-transformers faiss-cpu
            ```
            
            **Benefits**: More accurate, context-aware document matching
            """)
        else:
            st.warning(f"Search error: {str(error)}")
            st.info("Falling back to basic text search...")
        
        self.logger.error(f"Search error for query '{query}': {error}")
    
    def show_system_status(self) -> None:
        """Display system status and capabilities in sidebar."""
        with st.sidebar:
            st.markdown("### 🔧 System Status")
            
            # Show system status including Vercel info
            vercel_info = self.check_vercel_environment()
            if vercel_info['is_vercel']:
                st.markdown("### 🔧 Vercel Deployment Status")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Environment", vercel_info['environment'])
                    st.metric("Region", vercel_info['region'])
                with col2:
                    st.metric("Branch", vercel_info['branch'])
                    st.metric("Commit", vercel_info['commit'])
                
                if vercel_info['url'] != 'unknown':
                    st.info(f"🌐 Deployment URL: {vercel_info['url']}")
            
            capabilities = self.dependency_checker.get_capabilities_summary()
            
            # Core status
            if capabilities['basic_functionality']:
                st.success("✅ Core system operational")
            else:
                st.error("❌ Core dependencies missing")
            
            # Feature status
            feature_count = sum([
                capabilities['word_processing'],
                capabilities['advanced_ai'],
                capabilities['semantic_search'],
                capabilities['fast_search'],
                capabilities['advanced_nlp']
            ])
            
            st.info(f"📊 Enhanced features: {feature_count}/5 active")
            
            # Quick enhancement suggestions
            if feature_count < 3:
                with st.expander("🚀 Quick Upgrades", expanded=False):
                    if not capabilities['word_processing']:
                        st.code("pip install python-docx")
                        st.caption("→ Word document support")
                    
                    if not capabilities['advanced_ai']:
                        st.code("pip install transformers")
                        st.caption("→ Local AI models")
                    
                    if not capabilities['semantic_search']:
                        st.code("pip install sentence-transformers")
                        st.caption("→ Better search")
    
    def safe_execute(self, func, *args, error_handler=None, **kwargs) -> Optional[Any]:
        """Safely execute a function with error handling."""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if error_handler:
                error_handler(e)
            else:
                st.error(f"Unexpected error: {str(e)}")
                self.logger.error(f"Safe execution error in {func.__name__}: {e}")
                if st.checkbox("Show technical details", key=f"debug_{func.__name__}"):
                    st.code(traceback.format_exc())
            return None
    
    def show_enhancement_guide(self) -> None:
        """Show comprehensive enhancement guide."""
        st.markdown("### 🎯 Enhancement Guide")
        
        capabilities = self.dependency_checker.get_capabilities_summary()
        missing_features = []
        
        if not capabilities['word_processing']:
            missing_features.append({
                'name': 'Word Document Support',
                'command': 'pip install python-docx',
                'benefit': 'Process .docx files, extract tables'
            })
        
        if not capabilities['advanced_ai']:
            missing_features.append({
                'name': 'Advanced Local AI',
                'command': 'pip install transformers torch',
                'benefit': 'Better analysis, no API keys needed'
            })
        
        if not capabilities['semantic_search']:
            missing_features.append({
                'name': 'Semantic Search',
                'command': 'pip install sentence-transformers',
                'benefit': 'Context-aware document matching'
            })
        
        if missing_features:
            st.info(f"**{len(missing_features)} enhancements available**")
            
            for i, feature in enumerate(missing_features, 1):
                st.markdown(f"""
                **{i}. {feature['name']}**
                ```bash
                {feature['command']}
                ```
                💡 *{feature['benefit']}*
                """)
        else:
            st.success("🎉 All enhanced features are active!")

# Create global error handler instance
error_handler = DocQueryErrorHandler()