"""
Enhanced error handling and user experience improvements for DocQuery.
Provides better error messages and graceful fallbacks.
"""

import streamlit as st
import logging
import traceback
from typing import Optional, Any, Dict
from dependency_checker import DependencyChecker

class DocQueryErrorHandler:
    """Centralized error handling for better user experience."""
    
    def __init__(self):
        self.setup_logging()
        self.dependency_checker = DependencyChecker()
    
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/tmp/docquery.log'),
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
    
    def handle_database_error(self, error: Exception) -> None:
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