import streamlit as st
import os
import json
import tempfile
import time

# Configure environment for Streamlit deployment
def setup_environment():
    """Setup environment variables for Streamlit deployment."""
    # Read PORT environment variable (default 8501)
    port = int(os.getenv('PORT', '8501'))
    
    # Set Streamlit environment variables if not already set
    os.environ.setdefault('STREAMLIT_SERVER_PORT', str(port))
    os.environ.setdefault('STREAMLIT_SERVER_ADDRESS', '0.0.0.0')
    os.environ.setdefault('STREAMLIT_SERVER_HEADLESS', 'true')
    os.environ.setdefault('STREAMLIT_BROWSER_GATHER_USAGE_STATS', 'false')
    
    return port

# Setup environment before importing other modules
setup_environment()

from document_processor import DocumentProcessor
from query_parser import QueryParser
from openai_client import OpenAIClient
from local_ai_client import LocalAIClient
from database_manager import DatabaseManager
from dependency_checker import DependencyChecker

# Try to import advanced vector search, fallback to simpler alternatives
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

# Set page configuration
st.set_page_config(
    page_title="AI Document Analysis System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css():
    """Load custom CSS with error handling for deployment environments"""
    try:
        # Try to load from current directory first
        css_path = 'style.css'
        if not os.path.exists(css_path):
            # Try relative path from app.py location
            css_path = os.path.join(os.path.dirname(__file__), 'style.css')
        
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
            st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"⚠️ Could not load custom styles: {str(e)}")
        # Fallback CSS for basic styling
        fallback_css = """
        <style>
        .main { padding: 1rem; }
        .stButton > button { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            border: none; 
            border-radius: 8px; 
            padding: 0.5rem 1rem; 
        }
        .success-card { 
            background: #d4edda; 
            padding: 1rem; 
            border-radius: 8px; 
            color: #155724; 
            margin: 1rem 0; 
        }
        .warning-card { 
            background: #fff3cd; 
            padding: 1rem; 
            border-radius: 8px; 
            color: #856404; 
            margin: 1rem 0; 
        }
        .error-card { 
            background: #f8d7da; 
            padding: 1rem; 
            border-radius: 8px; 
            color: #721c24; 
            margin: 1rem 0; 
        }
        </style>
        """
        st.markdown(fallback_css, unsafe_allow_html=True)

def main():
    # Load custom CSS with fallback
    load_css()
    
    # Initialize dependency checker
    dep_checker = DependencyChecker()
    capabilities = dep_checker.get_capabilities_summary()
    
    # POLICYsure Navigation Bar - Simplified for Streamlit compatibility
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem 2rem; margin: -1rem -1rem 2rem -1rem; border-radius: 0 0 20px 20px; box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="color: white; font-size: 1.5rem; font-weight: 700;">📋 POLICYsure</div>
            <div>
                <span style="color: rgba(255, 255, 255, 0.9); margin-right: 1rem;">AI Document Analysis</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Show system status and capabilities
    if not capabilities['basic_functionality']:
        st.error("❌ **Critical Dependencies Missing**")
        st.write("Some core dependencies are missing. Please install them:")
        st.code("pip install -e .")
        return
    
    # Show enhanced capabilities status
    missing_features = []
    if not capabilities['word_processing']:
        missing_features.append("Word document support")
    if not capabilities['advanced_ai']:
        missing_features.append("Advanced AI models")
    if not capabilities['semantic_search']:
        missing_features.append("Semantic search")
    
    if missing_features:
        with st.expander("🔧 **Enhance Your Experience** - Optional Features Available", expanded=False):
            st.info(f"""
            **Missing Features**: {', '.join(missing_features)}
            
            To unlock advanced capabilities, install optional dependencies:
            ```bash
            pip install transformers sentence-transformers faiss-cpu python-docx
            ```
            
            **Benefits**:
            - 🤖 Advanced local AI models (no API key needed)  
            - 🔍 Semantic search (better document understanding)
            - 📄 Word document support (.docx files)
            - ⚡ Faster search performance
            """)
            
            if st.button("📋 View Detailed Dependency Report"):
                st.text(dep_checker.generate_report())

    # App Description
    st.markdown("""
    <div style="text-align: center; padding: 1rem; margin-bottom: 2rem;">
        <h2 style="color: #1a202c; margin-bottom: 0.5rem;">AI-Powered Document Analysis System</h2>
        <p style="color: #4a5568; font-size: 1.1rem;">Upload insurance policies, contracts, or any documents and ask natural language questions. Our AI system analyzes your documents and provides intelligent decisions with detailed justifications.</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'processed_documents' not in st.session_state:
        st.session_state.processed_documents = False
    if 'vector_search' not in st.session_state:
        st.session_state.vector_search = None
    if 'document_chunks' not in st.session_state:
        st.session_state.document_chunks = []
    if 'current_document_id' not in st.session_state:
        st.session_state.current_document_id = None
    
    # Initialize database with better error handling
    try:
        if 'db_manager' not in st.session_state:
            st.session_state.db_manager = DatabaseManager()
        db = st.session_state.db_manager
        
        # Test database connection
        try:
            analytics = db.get_analytics()
            db_status = "🟢 Connected"
        except Exception as e:
            st.warning(f"⚠️ Database features unavailable: {str(e)}")
            db_status = "🟡 Limited functionality"
            
    except Exception as e:
        st.error(f"❌ Database connection failed: {str(e)}")
        st.info("💡 The app will continue to work without database features.")
        db = None
        db_status = "🔴 Disconnected"

    # Enhanced Sidebar with Sample Documents
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### ⚙️ Configuration")
        
        # Sample Documents Section
        st.markdown("### 📄 Available Sample Documents")
        sample_docs = [
            "Health Insurance Policy", 
            "Life Insurance Policy", 
            "Auto Insurance Policy",
            "Sample PDF documents in repository"
        ]
        
        for doc in sample_docs:
            st.markdown(f"• {doc}")
        
        st.markdown("---")
        
        # AI Model Selection
        st.markdown("**AI Analysis Method:**")
        use_local_ai = st.radio(
            "Choose AI method:",
            ["Local AI (No API key needed)", "OpenAI GPT (Requires API key)"],
            help="Local AI uses open-source models, OpenAI provides more advanced analysis"
        )
        
        api_key = None
        if use_local_ai == "OpenAI GPT (Requires API key)":
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                help="Enter your OpenAI API key for advanced AI analysis",
                placeholder="sk-proj-..."
            )
            
            if api_key:
                os.environ["OPENAI_API_KEY"] = api_key
                st.markdown('<div class="success-card">✅ OpenAI API Key configured</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="warning-card">⚠️ Please enter your OpenAI API key</div>', unsafe_allow_html=True)
        else:
            # Initialize local AI
            local_ai = LocalAIClient()
            capabilities = local_ai.get_capabilities()
            
            st.markdown('<div class="success-card">✅ Local AI ready (No API key needed)</div>', unsafe_allow_html=True)
            
            # Show capabilities
            with st.expander("Local AI Capabilities", expanded=False):
                st.write("**Available Features:**")
                if capabilities["transformers_models"]:
                    st.write("• 🤖 Transformer models for sentiment analysis")
                if capabilities["spacy_nlp"]:
                    st.write("• 📝 Advanced NLP processing")
                st.write("• 🔍 Rule-based decision analysis")
                st.write("• 📊 Statistical text analysis")
                st.write("• 🎯 Context-aware processing")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Search functionality with better UX
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 🔍 Search History")
        search_term = st.text_input("Search past queries", placeholder="Type to search...", key="search_input")
        
        if search_term and db:
            try:
                search_results = db.search_queries(search_term, limit=5)
                if search_results:
                    st.markdown("**Recent matches:**")
                    for result in search_results:
                        decision_color = "🟢" if result['decision'] == 'Approved' else "🔴"
                        st.markdown(f"{decision_color} {result['query'][:35]}...")
                else:
                    st.info("No matching queries found")
            except Exception as e:
                st.error(f"Search error: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # System status
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 📊 System Status")
        st.markdown(f"**Search Engine:** {SEARCH_TYPE.split(' ')[0]} search")
        st.markdown(f"**Database:** {db_status}")
        
        # Show AI method status
        if 'use_local_ai' in locals():
            if use_local_ai == "Local AI (No API key needed)":
                st.markdown("**AI Method:** 🤖 Local AI")
            else:
                st.markdown("**AI Method:** 🌐 OpenAI GPT")
        st.markdown('</div>', unsafe_allow_html=True)

    # Main content area with improved layout
    col1, col2 = st.columns([1.2, 1], gap="large")

    with col1:
        st.markdown("### 📁 Document Upload")
        
        # Initialize document processor to check supported formats
        processor = DocumentProcessor()
        supported_formats = processor.get_supported_formats()
        
        # Create file type list based on what's actually supported
        supported_extensions = []
        if supported_formats.get('pdf', False):
            supported_extensions.append('pdf')
        if supported_formats.get('docx', False):
            supported_extensions.extend(['docx', 'doc'])
        if supported_formats.get('txt', False):
            supported_extensions.append('txt')
        if supported_formats.get('eml', False):
            supported_extensions.append('eml')
        
        # Custom upload area with dynamic format info
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Choose your document",
            type=supported_extensions,
            help=processor.get_format_help_text(),
            label_visibility="collapsed"
        )
        
        if not uploaded_file:
            # Show supported formats dynamically
            format_list = []
            if supported_formats.get('pdf', False):
                format_list.append("PDF")
            if supported_formats.get('docx', False):
                format_list.append("Word (.docx)")
            if supported_formats.get('txt', False):
                format_list.append("Text (.txt)")
            if supported_formats.get('eml', False):
                format_list.append("Email (.eml)")
            
            formats_text = " • ".join(format_list)
            
            st.markdown(f"""
            <div style="text-align: center; padding: 2rem;">
                <h4>📄 Drop your document here</h4>
                <p>Supported formats: {formats_text}</p>
                <p><em>Insurance policies • Contracts • Legal documents • Emails • Reports</em></p>
                <div style="margin-top: 1rem; color: #6c757d;">
                    <small>📁 Maximum file size: 200MB</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show info about additional formats if available
            if not supported_formats.get('docx', False):
                st.info("💡 **Want Word document support?** Install `python-docx` for .docx file processing")
        
        st.markdown('</div>', unsafe_allow_html=True)

        if uploaded_file is not None:
            try:
                start_time = time.time()
                
                # Create progress indicators
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                with st.spinner("🔄 Processing document..."):
                    progress_bar.progress(10)
                    status_text.text("📄 Reading document...")
                    
                    # Save uploaded file temporarily with proper extension
                    file_extension = os.path.splitext(uploaded_file.name)[1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name

                    progress_bar.progress(30)
                    status_text.text("📝 Extracting text content...")
                    
                    # Process document
                    processor = DocumentProcessor()
                    text_content = processor.extract_text(tmp_file_path)
                    
                    progress_bar.progress(60)
                    status_text.text("🔍 Creating searchable chunks...")
                    
                    chunks = processor.chunk_text(text_content)

                    progress_bar.progress(80)
                    status_text.text("🧠 Building search index...")
                    
                    # Initialize vector search
                    vector_search = VectorSearch()
                    vector_search.build_index(chunks)

                    progress_bar.progress(95)
                    status_text.text("💾 Saving to session...")
                    
                    # Store in session state
                    st.session_state.processed_documents = True
                    st.session_state.vector_search = vector_search
                    st.session_state.document_chunks = chunks

                    # Clean up temp file
                    os.unlink(tmp_file_path)
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Document processing complete!")
                    
                    # Save to database
                    if db:
                        try:
                            processing_time = time.time() - start_time
                            document_id = db.save_document(
                                filename=uploaded_file.name,
                                file_size=len(uploaded_file.getvalue()),
                                chunk_count=len(chunks),
                                processing_time=processing_time,
                                search_type=SEARCH_TYPE
                            )
                            st.session_state.current_document_id = document_id
                        except Exception as db_error:
                            st.warning(f"⚠️ Database save failed: {str(db_error)}")
                            st.session_state.current_document_id = None

                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                # Success message with better styling
                processing_time = time.time() - start_time
                st.markdown(f'''
                <div class="success-card">
                    <h4>✅ Document processed successfully!</h4>
                    <p>📊 <strong>{len(chunks)}</strong> text chunks • 🔍 <strong>{SEARCH_TYPE.split(" ")[0]}</strong> search • ⏱️ <strong>{processing_time:.2f}s</strong></p>
                </div>
                ''', unsafe_allow_html=True)
                
                # Document statistics in an attractive format
                with st.expander("📊 Document Statistics", expanded=False):
                    col_stat1, col_stat2, col_stat3 = st.columns(3)
                    with col_stat1:
                        st.metric("Characters", f"{len(text_content):,}")
                    with col_stat2:
                        st.metric("Text Chunks", len(chunks))
                    with col_stat3:
                        avg_size = len(text_content) // len(chunks) if chunks else 0
                        st.metric("Avg Chunk Size", f"{avg_size:,}")

            except Exception as e:
                st.error(f"❌ Error processing document: {str(e)}")

    with col2:
        st.markdown("### ❓ Query Analysis")
        
        if not st.session_state.processed_documents:
            st.markdown('''
            <div class="query-section" style="text-align: center;">
                <h4>📋 Ready to analyze</h4>
                <p>Upload a document first to start asking questions</p>
                <p><em>👈 Use the upload area on the left</em></p>
            </div>
            ''', unsafe_allow_html=True)
        elif use_local_ai == "OpenAI GPT (Requires API key)" and not api_key:
            st.markdown('''
            <div class="query-section" style="text-align: center;">
                <h4>🔑 API Key Required</h4>
                <p>Enter your OpenAI API key in the sidebar or switch to Local AI</p>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown('<div class="query-section">', unsafe_allow_html=True)
            
            # Sample queries for better UX
            st.markdown("**💡 Try these example queries:**")
            example_queries = [
                "46M, knee surgery in Pune, 3-month policy",
                "35-year-old female, heart surgery in Mumbai, 1-year insurance",
                "Male patient, dental treatment, Bangalore, 6-month coverage"
            ]
            
            selected_example = st.selectbox("Choose an example:", [""] + example_queries, key="example_select")
            
            # Enhanced query input with multiple options
            st.markdown("### 💬 Ask Your Question")
            
            # Query input method selection
            query_method = st.radio(
                "Choose how to provide your query:",
                ["💬 Text Input", "📄 Upload Query Document"],
                horizontal=True,
                help="Select whether to type your question or upload a document containing your query"
            )
            
            user_query = ""
            
            if query_method == "💬 Text Input":
                # Enhanced text area with custom styling
                user_query = st.text_area(
                    "Enter your natural language query:",
                    height=120,
                    value=selected_example if selected_example else "",
                    placeholder="Ask questions like: '46-year-old male, knee surgery in Pune, 3-month-old policy' ✨",
                    help="📋 Describe the patient, procedure, location, and policy details in natural language",
                    label_visibility="collapsed"
                )
                
                # Quick query templates
                st.markdown("**🚀 Quick Templates:**")
                col_t1, col_t2, col_t3 = st.columns(3)
                
                with col_t1:
                    if st.button("👤 Age + Procedure", help="Template for age and medical procedure"):
                        user_query = "45-year-old patient needs surgery"
                
                with col_t2:
                    if st.button("🏥 Location + Coverage", help="Template for location-based coverage"):
                        user_query = "Treatment in Mumbai, covered under policy"
                
                with col_t3:
                    if st.button("⏱️ Policy Duration", help="Template for policy timing questions"):
                        user_query = "2-year-old insurance policy coverage"
            
            else:  # Document upload option
                st.markdown('''
                <div style="background: rgba(255, 255, 255, 0.9); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(102, 126, 234, 0.2); margin: 1rem 0;">
                    <h4 style="margin: 0 0 1rem 0; color: var(--text);">📤 Upload Query Document</h4>
                    <p style="margin: 0; color: var(--text-muted);">Upload a document containing your questions or requirements for analysis</p>
                </div>
                ''', unsafe_allow_html=True)
                
                query_file = st.file_uploader(
                    "Upload a document with your query:",
                    type=['txt', 'pdf', 'docx', 'eml'],
                    help="Upload a document containing your questions about the main policy document",
                    key="query_upload"
                )
                
                if query_file is not None:
                    try:
                        # Process the query document
                        temp_query_path = f"temp_query_{query_file.name}"
                        with open(temp_query_path, "wb") as f:
                            f.write(query_file.getbuffer())
                        
                        processor = DocumentProcessor()
                        query_content = processor.extract_text(temp_query_path)
                        
                        # Clean up temporary file
                        os.remove(temp_query_path)
                        
                        user_query = query_content.strip()
                        
                        st.success(f"✅ Query document processed: {len(user_query)} characters extracted")
                        
                        # Show extracted query in expandable section
                        with st.expander("👀 Preview Extracted Query", expanded=False):
                            st.text_area(
                                "Extracted query content:",
                                value=user_query[:1000] + ("..." if len(user_query) > 1000 else ""),
                                height=100,
                                disabled=True
                            )
                            
                    except Exception as e:
                        st.error(f"❌ Error processing query document: {str(e)}")
                        user_query = ""

            # Analyze button with better styling
            analyze_button = st.button(
                "🤖 Analyze with AI", 
                type="primary", 
                use_container_width=True,
                help="Click to get AI-powered analysis of your query"
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            if analyze_button:
                if user_query.strip():
                    try:
                        start_time = time.time()
                        
                        # Create progress indicators for analysis
                        analysis_progress = st.progress(0)
                        analysis_status = st.empty()
                        
                        with st.spinner("🤖 AI Analysis in progress..."):
                            analysis_progress.progress(20)
                            analysis_status.text("📝 Parsing your query...")
                            
                            # Parse query
                            parser = QueryParser()
                            parsed_query = parser.parse_query(user_query)

                            analysis_progress.progress(40)
                            analysis_status.text("🔍 Searching relevant content...")
                            
                            # Search for relevant chunks
                            relevant_chunks = st.session_state.vector_search.search(user_query, k=3)

                            analysis_progress.progress(70)
                            analysis_status.text("🧠 Running AI analysis...")
                            
                            # Get AI analysis based on selected method
                            if use_local_ai == "Local AI (No API key needed)":
                                local_ai_client = LocalAIClient()
                                analysis_result = local_ai_client.analyze_query(
                                    parsed_query, 
                                    relevant_chunks, 
                                    user_query
                                )
                            else:
                                openai_client = OpenAIClient()
                                analysis_result = openai_client.analyze_query(
                                    parsed_query, 
                                    relevant_chunks, 
                                    user_query
                                )
                            
                            analysis_progress.progress(90)
                            analysis_status.text("💾 Saving results...")
                            
                            # Save query and analysis to database
                            if db and st.session_state.current_document_id:
                                try:
                                    total_time = time.time() - start_time
                                    query_id = db.save_query(
                                        document_id=st.session_state.current_document_id,
                                        original_query=user_query,
                                        parsed_query=parsed_query,
                                        processing_time=total_time
                                    )
                                    
                                    db.save_analysis(
                                        query_id=query_id,
                                        decision=analysis_result.get('decision', 'Unknown'),
                                        amount=analysis_result.get('amount'),
                                        justification=analysis_result.get('justification', ''),
                                        clause_reference=analysis_result.get('clause_reference', ''),
                                        confidence=analysis_result.get('confidence', 'Medium'),
                                        relevant_chunks=relevant_chunks,
                                        ai_model=analysis_result.get('analysis_method', 'gpt-3.5-turbo'),
                                        processing_time=total_time
                                    )
                                except Exception as db_error:
                                    st.warning(f"⚠️ Database save failed: {str(db_error)}")

                            analysis_progress.progress(100)
                            analysis_status.text("✅ Analysis complete!")
                            
                        # Clear progress indicators
                        analysis_progress.empty()
                        analysis_status.empty()

                        # Enhanced results display
                        st.markdown('<div class="results-section">', unsafe_allow_html=True)
                        st.markdown("## 📋 Analysis Results")
                        
                        # Validate analysis result
                        if not analysis_result or not isinstance(analysis_result, dict):
                            st.error("❌ Analysis failed - Invalid result format")
                            analysis_result = {
                                'decision': 'Error',
                                'justification': 'Analysis could not be completed due to a system error.',
                                'confidence': 'Low',
                                'analysis_method': 'Error Handler'
                            }
                        
                        # Ensure required fields exist
                        decision = analysis_result.get('decision', 'Unknown')
                        justification = analysis_result.get('justification', 'No justification provided')
                        confidence = analysis_result.get('confidence', 'Low')
                        
                        # Decision card with prominent styling
                        decision_icon = "✅" if decision.lower() in ['approved', 'approve'] else "❌" if decision.lower() in ['rejected', 'reject', 'denied'] else "⏳"
                        
                        if decision.lower() in ['approved', 'approve']:
                            decision_color = "#10b981"
                            decision_class = "decision-approved"
                        elif decision.lower() in ['rejected', 'reject', 'denied']:
                            decision_color = "#ef4444"
                            decision_class = "decision-rejected"
                        else:
                            decision_color = "#f59e0b"
                            decision_class = "decision-review"
                        
                        st.markdown(f'''
                        <div class="{decision_class}">
                            <h2 style="margin: 0; font-size: 2.5rem; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">{decision_icon} {decision}</h2>
                            {f'<p style="margin: 0.75rem 0 0 0; font-size: 1.3rem; opacity: 0.95;">💰 Amount: {analysis_result["amount"]}</p>' if analysis_result.get('amount') else ''}
                        </div>
                        ''', unsafe_allow_html=True)
                        
                        # Extracted details in a clean layout
                        with st.expander("🔍 Extracted Query Details", expanded=True):
                            if parsed_query and any(parsed_query.values()):
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    if parsed_query.get('age'):
                                        st.markdown(f"**👤 Age:** {parsed_query['age']}")
                                    if parsed_query.get('gender'):
                                        st.markdown(f"**⚧ Gender:** {parsed_query['gender']}")
                                    if parsed_query.get('query_type'):
                                        st.markdown(f"**📋 Query Type:** {parsed_query['query_type']}")
                                with col_b:
                                    if parsed_query.get('procedure'):
                                        st.markdown(f"**🏥 Procedure:** {parsed_query['procedure']}")
                                    if parsed_query.get('location'):
                                        st.markdown(f"**📍 Location:** {parsed_query['location']}")
                                    if parsed_query.get('policy_duration'):
                                        st.markdown(f"**📅 Policy Duration:** {parsed_query['policy_duration']}")
                            else:
                                st.info("ℹ️ No specific details extracted from query - analysis based on document content")

                        # Justification and confidence with better error handling
                        col_just, col_conf = st.columns([3, 1])
                        with col_just:
                            st.markdown("**📝 Justification:**")
                            if justification and justification.strip():
                                st.write(justification)
                            else:
                                st.warning("⚠️ No justification provided by the analysis engine")
                        with col_conf:
                            conf_color = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}.get(confidence, "🟡")
                            st.metric("Confidence", f"{conf_color} {confidence}")
                        
                        # Additional analysis details
                        if analysis_result.get('clause_reference'):
                            st.markdown("**📚 Clause Reference:**")
                            st.info(analysis_result['clause_reference'])
                        
                        if analysis_result.get('risk_level'):
                            risk_level = analysis_result['risk_level']
                            risk_color = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(risk_level, "🟡")
                            st.markdown(f"**⚠️ Risk Level:** {risk_color} {risk_level}")
                        
                        # Recommendations and next steps
                        if analysis_result.get('recommendations'):
                            st.markdown("**💡 Recommendations:**")
                            for i, rec in enumerate(analysis_result['recommendations'], 1):
                                st.markdown(f"{i}. {rec}")
                        
                        if analysis_result.get('next_steps'):
                            st.markdown("**📋 Next Steps:**")
                            for i, step in enumerate(analysis_result['next_steps'], 1):
                                st.markdown(f"{i}. {step}")

                        # Relevant sections with better formatting
                        with st.expander("📄 Supporting Document Sections", expanded=False):
                            if relevant_chunks and len(relevant_chunks) > 0:
                                for i, chunk in enumerate(relevant_chunks, 1):
                                    st.markdown(f"**📖 Section {i}:**")
                                    preview = chunk[:500] + "..." if len(chunk) > 500 else chunk
                                    st.markdown(f'<div style="background-color: #f8f9fa; padding: 1.25rem; border-radius: 8px; border-left: 4px solid #2563eb; margin: 0.5rem 0;">{preview}</div>', unsafe_allow_html=True)
                                    if i < len(relevant_chunks):
                                        st.markdown("---")
                            else:
                                st.warning("⚠️ No relevant document sections found")

                        # Technical details (collapsed by default) with error handling
                        with st.expander("🔧 Technical Details", expanded=False):
                            try:
                                # Clean up the analysis result for display
                                display_result = {k: v for k, v in analysis_result.items() if v is not None}
                                st.json(display_result)
                            except Exception as json_error:
                                st.error(f"❌ Error displaying technical details: {str(json_error)}")
                                st.write("Raw analysis result:")
                                st.write(str(analysis_result))
                        
                        st.markdown('</div>', unsafe_allow_html=True)

                    except Exception as e:
                        st.error(f"❌ Error analyzing query: {str(e)}")
                else:
                    st.warning("⚠️ Please enter a query to analyze")

    # Enhanced Analytics and History Section with better error handling
    st.markdown("---")
    st.markdown("## 📊 System Dashboard")
    
    if db:
        try:
            analytics = db.get_analytics()
            
            # Analytics cards with attractive design
            col_a1, col_a2, col_a3, col_a4 = st.columns(4)
            
            with col_a1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("📄 Documents", analytics.get('total_documents', 0))
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col_a2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("💬 Queries", analytics.get('total_queries', 0))
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col_a3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                approval_rate = analytics.get('approval_rate', 0)
                st.metric("✅ Approval Rate", f"{approval_rate:.1f}%")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col_a4:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                avg_time = analytics.get('average_processing_time', 0)
                st.metric("⚡ Avg Time", f"{avg_time:.1f}s")
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Decision breakdown with error handling
            col_analytics, col_history = st.columns([1, 1], gap="large")
            
            with col_analytics:
                st.markdown("### 📈 Decision Breakdown")
                
                approved = analytics.get('approved_decisions', 0)
                rejected = analytics.get('rejected_decisions', 0)
                
                if approved + rejected > 0:
                    col_appr, col_rej = st.columns(2)
                    with col_appr:
                        st.markdown(f'''
                        <div style="background: var(--gradient-success); color: white; padding: 1.25rem; border-radius: 12px; text-align: center; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);">
                            <h3 style="margin: 0; font-size: 1.8rem;">✅ {approved}</h3>
                            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Approved</p>
                        </div>
                        ''', unsafe_allow_html=True)
                    with col_rej:
                        st.markdown(f'''
                        <div style="background: var(--gradient-danger); color: white; padding: 1.25rem; border-radius: 12px; text-align: center; box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);">
                            <h3 style="margin: 0; font-size: 1.8rem;">❌ {rejected}</h3>
                            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Rejected</p>
                        </div>
                        ''', unsafe_allow_html=True)
                else:
                    st.info("📊 No decisions recorded yet - start analyzing documents to see statistics")
            
            with col_history:
                st.markdown("### 📝 Recent Activity")
                try:
                    history = db.get_query_history(limit=5)
                    if history and len(history) > 0:
                        for i, record in enumerate(history):
                            decision_icon = "✅" if record.get('decision') == 'Approved' else "❌"
                            decision_color = "#10b981" if record.get('decision') == 'Approved' else "#ef4444"
                            time_str = record.get('timestamp', '')[:16].replace('T', ' ') if record.get('timestamp') else 'Unknown time'
                            query_text = record.get('query', 'Unknown query')[:40] + "..." if len(record.get('query', '')) > 40 else record.get('query', 'Unknown query')
                            doc_name = record.get('document', 'Unknown document')[:20] + "..." if len(record.get('document', '')) > 20 else record.get('document', 'Unknown document')
                            
                            st.markdown(f'''
                            <div style="background: rgba(255, 255, 255, 0.9); padding: 1rem; border-radius: 8px; margin-bottom: 0.75rem; border-left: 4px solid {decision_color}; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                    <div style="flex: 1;">
                                        <strong>{decision_icon} {query_text}</strong>
                                        <br>
                                        <small style="color: #64748b;">📄 {doc_name} • 🕒 {time_str}</small>
                                    </div>
                                </div>
                            </div>
                            ''', unsafe_allow_html=True)
                    else:
                        st.info("📝 No query history available yet - analyze some documents to see recent activity")
                except Exception as history_error:
                    st.warning(f"⚠️ Could not load query history: {str(history_error)}")
                    
        except Exception as analytics_error:
            st.error(f"❌ Error loading dashboard data: {str(analytics_error)}")
            st.info("💡 Try uploading and analyzing a document to initialize the dashboard")
    else:
        st.markdown('''
        <div style="background: var(--gradient-warning); color: white; padding: 2.5rem; border-radius: 16px; text-align: center; box-shadow: 0 8px 24px rgba(245, 158, 11, 0.25);">
            <h3 style="margin: 0 0 1rem 0;">📊 Dashboard Unavailable</h3>
            <p style="margin: 0; opacity: 0.9;">Database connection required for analytics and history features</p>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.8;">The app will still work for document analysis</p>
        </div>
        ''', unsafe_allow_html=True)



# Vercel serverless function handler
def handler(event, context):
    """
    Vercel serverless function handler.
    This function is called by Vercel's serverless runtime.
    """
    # For Vercel deployment, return information about how to run the app
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': json.dumps({
            'message': 'DocQuery Streamlit App',
            'instructions': 'Use: streamlit run app.py --server.port $PORT',
            'port': os.getenv('PORT', '8501')
        })
    }

if __name__ == "__main__":
    import os
    
    # Read PORT environment variable (default 8501 for Streamlit)
    port = int(os.getenv('PORT', '8501'))
    
    # Set Streamlit configuration via environment variables
    os.environ.setdefault('STREAMLIT_SERVER_PORT', str(port))
    os.environ.setdefault('STREAMLIT_SERVER_ADDRESS', '0.0.0.0')
    os.environ.setdefault('STREAMLIT_SERVER_HEADLESS', 'true')
    os.environ.setdefault('STREAMLIT_BROWSER_GATHER_USAGE_STATS', 'false')
    
    # Run the main Streamlit app
    main()
