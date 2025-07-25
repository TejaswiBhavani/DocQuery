import streamlit as st
import os
import json
import tempfile
import time
from document_processor import DocumentProcessor
from query_parser import QueryParser
from openai_client import OpenAIClient
from local_ai_client import LocalAIClient
from database_manager import DatabaseManager

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

def main():
    # Load custom CSS
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    # Modern header with enhanced styling
    st.markdown("""
    <div class="app-header">
        <h1 class="app-title">🤖 AI Document Analysis System</h1>
        <p class="app-subtitle">Upload any document (PDF, Word, Email) and ask natural language questions for intelligent AI-powered decisions</p>
        <div style="margin-top: 1.5rem; display: flex; justify-content: center; gap: 2rem; font-size: 0.9rem; opacity: 0.95;">
            <span class="float-animation">📄 Multi-format Support</span>
            <span class="float-animation" style="animation-delay: 0.5s;">🧠 AI-powered Analysis</span>
            <span class="float-animation" style="animation-delay: 1s;">⚡ Real-time Processing</span>
            <span class="float-animation" style="animation-delay: 1.5s;">📊 Audit Trail</span>
        </div>
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
    
    # Initialize database
    try:
        if 'db_manager' not in st.session_state:
            st.session_state.db_manager = DatabaseManager()
        db = st.session_state.db_manager
    except Exception as e:
        st.error(f"❌ Database connection failed: {str(e)}")
        st.info("The app will continue to work without database features.")
        db = None

    # Enhanced Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### ⚙️ Configuration")
        
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
        if db:
            st.markdown("**Database:** 🟢 Connected")
        else:
            st.markdown("**Database:** 🔴 Disconnected")
        
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
        
        # Custom upload area
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Choose your document",
            type=['pdf', 'docx', 'doc', 'txt', 'eml'],
            help="Upload PDFs, Word documents, emails, or text files for AI analysis",
            label_visibility="collapsed"
        )
        
        if not uploaded_file:
            st.markdown("""
            <div style="text-align: center; padding: 2rem;">
                <h4>📄 Drop your document here</h4>
                <p>Supported formats: PDF • Word (.docx) • Email (.eml) • Text (.txt)</p>
                <p><em>Insurance policies • Contracts • Legal documents • Emails • Reports</em></p>
                <div style="margin-top: 1rem; color: #6c757d;">
                    <small>📁 Maximum file size: 200MB</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if uploaded_file is not None:
            try:
                start_time = time.time()
                with st.spinner("Processing document..."):
                    # Save uploaded file temporarily with proper extension
                    file_extension = os.path.splitext(uploaded_file.name)[1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name

                    # Process document
                    processor = DocumentProcessor()
                    text_content = processor.extract_text(tmp_file_path)
                    chunks = processor.chunk_text(text_content)

                    # Initialize vector search
                    vector_search = VectorSearch()
                    vector_search.build_index(chunks)

                    # Store in session state
                    st.session_state.processed_documents = True
                    st.session_state.vector_search = vector_search
                    st.session_state.document_chunks = chunks

                    # Clean up temp file
                    os.unlink(tmp_file_path)
                    
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
                            st.warning(f"Database save failed: {str(db_error)}")
                            st.session_state.current_document_id = None

                # Success message with better styling
                st.markdown(f'''
                <div class="success-card">
                    <h4>✅ Document processed successfully!</h4>
                    <p>Found <strong>{len(chunks)}</strong> text chunks • Using <strong>{SEARCH_TYPE.split(" ")[0]}</strong> search</p>
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
            
            # Enhanced query input with document icon header
            st.markdown('''
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                <h3 style="margin: 0; color: var(--text);">💬 Ask Your Question</h3>
                <div class="document-icon-btn" style="margin-left: auto; font-size: 1.2rem;" title="Document Analysis Feature">
                    📄
                </div>
            </div>
            ''', unsafe_allow_html=True)
            
            # Enhanced text area with custom styling
            user_query = st.text_area(
                "Enter your natural language query:",
                height=120,
                value=selected_example if selected_example else "",
                placeholder="Ask questions like: '46-year-old male, knee surgery in Pune, 3-month-old policy' ✨",
                help="📋 Describe the patient, procedure, location, and policy details in natural language",
                label_visibility="collapsed"
            )

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
                        with st.spinner("Analyzing query..."):
                            # Parse query
                            parser = QueryParser()
                            parsed_query = parser.parse_query(user_query)

                            # Search for relevant chunks
                            relevant_chunks = st.session_state.vector_search.search(user_query, k=3)

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
                                    st.warning(f"Database save failed: {str(db_error)}")

                        # Enhanced results display
                        st.markdown('<div class="results-section">', unsafe_allow_html=True)
                        st.markdown("## 📋 Analysis Results")
                        
                        # Decision card with prominent styling
                        decision = analysis_result.get('decision', 'Unknown')
                        decision_icon = "✅" if decision.lower() == 'approved' else "❌"
                        decision_color = "#28a745" if decision.lower() == 'approved' else "#dc3545"
                        
                        st.markdown(f'''
                        <div style="background-color: {decision_color}; color: white; padding: 1.5rem; border-radius: 10px; text-align: center; margin: 1rem 0;">
                            <h2 style="margin: 0; font-size: 2rem;">{decision_icon} {decision}</h2>
                            {f'<p style="margin: 0.5rem 0 0 0; font-size: 1.2rem;">Amount: {analysis_result["amount"]}</p>' if analysis_result.get('amount') else ''}
                        </div>
                        ''', unsafe_allow_html=True)
                        
                        # Extracted details in a clean layout
                        with st.expander("🔍 Extracted Query Details", expanded=True):
                            if any(parsed_query.values()):
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    if parsed_query.get('age'):
                                        st.markdown(f"**👤 Age:** {parsed_query['age']}")
                                    if parsed_query.get('gender'):
                                        st.markdown(f"**⚧ Gender:** {parsed_query['gender']}")
                                with col_b:
                                    if parsed_query.get('procedure'):
                                        st.markdown(f"**🏥 Procedure:** {parsed_query['procedure']}")
                                    if parsed_query.get('location'):
                                        st.markdown(f"**📍 Location:** {parsed_query['location']}")
                                    if parsed_query.get('policy_duration'):
                                        st.markdown(f"**📅 Policy Duration:** {parsed_query['policy_duration']}")
                            else:
                                st.info("No specific details extracted from query")

                        # Justification and confidence
                        col_just, col_conf = st.columns([3, 1])
                        with col_just:
                            st.markdown("**📝 Justification:**")
                            st.write(analysis_result.get('justification', 'No justification provided'))
                        with col_conf:
                            confidence = analysis_result.get('confidence', 'Medium')
                            conf_color = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}.get(confidence, "🟡")
                            st.metric("Confidence", f"{conf_color} {confidence}")
                        
                        if analysis_result.get('clause_reference'):
                            st.markdown("**📚 Clause Reference:**")
                            st.info(analysis_result['clause_reference'])

                        # Relevant sections with better formatting
                        with st.expander("📄 Supporting Document Sections", expanded=False):
                            for i, chunk in enumerate(relevant_chunks, 1):
                                st.markdown(f"**📖 Section {i}:**")
                                preview = chunk[:400] + "..." if len(chunk) > 400 else chunk
                                st.markdown(f'<div style="background-color: #f8f9fa; padding: 1rem; border-radius: 5px; border-left: 4px solid #007bff;">{preview}</div>', unsafe_allow_html=True)
                                if i < len(relevant_chunks):
                                    st.markdown("---")

                        # Technical details (collapsed by default)
                        with st.expander("🔧 Technical Details", expanded=False):
                            st.json(analysis_result)
                        
                        st.markdown('</div>', unsafe_allow_html=True)

                    except Exception as e:
                        st.error(f"❌ Error analyzing query: {str(e)}")
                else:
                    st.warning("⚠️ Please enter a query to analyze")

    # Enhanced Analytics and History Section
    st.markdown("---")
    st.markdown("## 📊 System Dashboard")
    
    if db:
        try:
            analytics = db.get_analytics()
            
            # Analytics cards with attractive design
            col_a1, col_a2, col_a3, col_a4 = st.columns(4)
            
            with col_a1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("📄 Documents", analytics['total_documents'])
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col_a2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("💬 Queries", analytics['total_queries'])
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col_a3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                approval_rate = analytics['approval_rate']
                st.metric("✅ Approval Rate", f"{approval_rate:.1f}%")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col_a4:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("⚡ Avg Time", f"{analytics['average_processing_time']:.1f}s")
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Decision breakdown
            col_analytics, col_history = st.columns([1, 1], gap="large")
            
            with col_analytics:
                st.markdown("### 📈 Decision Breakdown")
                
                approved = analytics['approved_decisions']
                rejected = analytics['rejected_decisions']
                
                if approved + rejected > 0:
                    col_appr, col_rej = st.columns(2)
                    with col_appr:
                        st.markdown(f'''
                        <div style="background-color: #d4edda; padding: 1rem; border-radius: 8px; text-align: center;">
                            <h3 style="margin: 0; color: #155724;">✅ {approved}</h3>
                            <p style="margin: 0; color: #155724;">Approved</p>
                        </div>
                        ''', unsafe_allow_html=True)
                    with col_rej:
                        st.markdown(f'''
                        <div style="background-color: #f8d7da; padding: 1rem; border-radius: 8px; text-align: center;">
                            <h3 style="margin: 0; color: #721c24;">❌ {rejected}</h3>
                            <p style="margin: 0; color: #721c24;">Rejected</p>
                        </div>
                        ''', unsafe_allow_html=True)
                else:
                    st.info("No decisions recorded yet")
            
            with col_history:
                st.markdown("### 📝 Recent Activity")
                history = db.get_query_history(limit=5)
                if history:
                    for i, record in enumerate(history):
                        decision_icon = "✅" if record['decision'] == 'Approved' else "❌"
                        time_str = record['timestamp'][:16].replace('T', ' ')
                        
                        st.markdown(f'''
                        <div style="background-color: white; padding: 0.8rem; border-radius: 6px; margin-bottom: 0.5rem; border-left: 4px solid {'#28a745' if record['decision'] == 'Approved' else '#dc3545'};">
                            <div style="display: flex; justify-content: between; align-items: center;">
                                <strong>{decision_icon} {record['query'][:40]}...</strong>
                            </div>
                            <small style="color: #6c757d;">📄 {record['document'][:20]}... • 🕒 {time_str}</small>
                        </div>
                        ''', unsafe_allow_html=True)
                else:
                    st.info("No query history available yet")
                    
        except Exception as e:
            st.error(f"Error loading dashboard data: {str(e)}")
    else:
        st.markdown('''
        <div style="background-color: #fff3cd; padding: 2rem; border-radius: 10px; text-align: center;">
            <h3>📊 Dashboard Unavailable</h3>
            <p>Database connection required for analytics and history features</p>
        </div>
        ''', unsafe_allow_html=True)



if __name__ == "__main__":
    main()
