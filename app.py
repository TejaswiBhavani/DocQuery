import streamlit as st
import os
import json
import tempfile
import time
from document_processor import DocumentProcessor
from query_parser import QueryParser
from openai_client import OpenAIClient
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
    page_icon="📄",
    layout="wide"
)

def main():
    st.title("🤖 AI-Powered Document Analysis System")
    st.markdown("""
    Upload documents (PDFs) and ask natural language questions to get intelligent decisions 
    based on semantic document analysis and AI reasoning.
    """)

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

    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # OpenAI API Key input
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Enter your OpenAI API key to enable AI analysis",
            placeholder="sk-..."
        )
        
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            st.success("✅ API Key configured")
        else:
            st.warning("⚠️ Please enter your OpenAI API key to continue")
        
        st.markdown("---")
        st.subheader("🔍 Search History")
        search_term = st.text_input("Search past queries", placeholder="Enter search term...")
        
        if search_term and db:
            try:
                search_results = db.search_queries(search_term, limit=5)
                if search_results:
                    st.write("**Search Results:**")
                    for result in search_results:
                        st.write(f"• {result['query'][:40]}... → {result['decision']}")
                else:
                    st.info("No matching queries found")
            except Exception as e:
                st.error(f"Search error: {str(e)}")

    # Main content area
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📁 Document Upload")
        uploaded_file = st.file_uploader(
            "Upload a PDF document",
            type=['pdf'],
            help="Upload policy documents, contracts, or other PDFs for analysis"
        )

        if uploaded_file is not None:
            try:
                start_time = time.time()
                with st.spinner("Processing document..."):
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
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

                st.success(f"✅ Document processed successfully! Found {len(chunks)} text chunks.")
                st.info(f"Using {SEARCH_TYPE} for document analysis.")
                
                # Show document statistics
                with st.expander("📊 Document Statistics"):
                    st.write(f"**Total characters:** {len(text_content):,}")
                    st.write(f"**Text chunks:** {len(chunks)}")
                    st.write(f"**Average chunk size:** {len(text_content) // len(chunks) if chunks else 0} characters")

            except Exception as e:
                st.error(f"❌ Error processing document: {str(e)}")

    with col2:
        st.subheader("❓ Query Analysis")
        
        if not st.session_state.processed_documents:
            st.info("👈 Please upload a document first to enable query analysis")
        elif not api_key:
            st.info("👈 Please enter your OpenAI API key in the sidebar")
        else:
            # Query input
            user_query = st.text_area(
                "Enter your query",
                height=100,
                placeholder="e.g., 46-year-old male, knee surgery in Pune, 3-month-old insurance policy",
                help="Enter a natural language query about the uploaded document"
            )

            if st.button("🔍 Analyze Query", type="primary"):
                if user_query.strip():
                    try:
                        start_time = time.time()
                        with st.spinner("Analyzing query..."):
                            # Parse query
                            parser = QueryParser()
                            parsed_query = parser.parse_query(user_query)

                            # Search for relevant chunks
                            relevant_chunks = st.session_state.vector_search.search(user_query, k=3)

                            # Get AI analysis
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
                                        ai_model="gpt-3.5-turbo",
                                        processing_time=total_time
                                    )
                                except Exception as db_error:
                                    st.warning(f"Database save failed: {str(db_error)}")

                        # Display results
                        st.subheader("📋 Analysis Results")
                        
                        # Show parsed query details
                        with st.expander("🔍 Extracted Query Details", expanded=True):
                            col_a, col_b = st.columns(2)
                            with col_a:
                                if parsed_query.get('age'):
                                    st.write(f"**Age:** {parsed_query['age']}")
                                if parsed_query.get('gender'):
                                    st.write(f"**Gender:** {parsed_query['gender']}")
                            with col_b:
                                if parsed_query.get('procedure'):
                                    st.write(f"**Procedure:** {parsed_query['procedure']}")
                                if parsed_query.get('location'):
                                    st.write(f"**Location:** {parsed_query['location']}")
                                if parsed_query.get('policy_duration'):
                                    st.write(f"**Policy Duration:** {parsed_query['policy_duration']}")

                        # Show AI decision
                        decision_color = "green" if analysis_result.get('decision', '').lower() == 'approved' else "red"
                        st.markdown(f"### Decision: :{decision_color}[{analysis_result.get('decision', 'Unknown')}]")
                        
                        if analysis_result.get('amount'):
                            st.write(f"**Amount:** {analysis_result['amount']}")
                        
                        st.write(f"**Justification:** {analysis_result.get('justification', 'No justification provided')}")
                        
                        if analysis_result.get('clause_reference'):
                            st.write(f"**Clause Reference:** {analysis_result['clause_reference']}")

                        # Show relevant document sections
                        with st.expander("📄 Relevant Document Sections"):
                            for i, chunk in enumerate(relevant_chunks, 1):
                                st.write(f"**Section {i}:**")
                                st.write(chunk[:500] + "..." if len(chunk) > 500 else chunk)
                                st.divider()

                        # Show raw JSON response
                        with st.expander("🔧 Raw JSON Response"):
                            st.json(analysis_result)

                    except Exception as e:
                        st.error(f"❌ Error analyzing query: {str(e)}")
                else:
                    st.warning("⚠️ Please enter a query to analyze")

    # Analytics and History Section
    st.markdown("---")
    col_analytics, col_history = st.columns([1, 1])
    
    with col_analytics:
        st.subheader("📊 Analytics")
        if db:
            try:
                analytics = db.get_analytics()
                col_a1, col_a2, col_a3 = st.columns(3)
                
                with col_a1:
                    st.metric("Total Documents", analytics['total_documents'])
                    st.metric("Total Queries", analytics['total_queries'])
                
                with col_a2:
                    st.metric("Approved", analytics['approved_decisions'])
                    st.metric("Rejected", analytics['rejected_decisions'])
                
                with col_a3:
                    st.metric("Approval Rate", f"{analytics['approval_rate']:.1f}%")
                    st.metric("Avg Processing", f"{analytics['average_processing_time']:.2f}s")
                    
            except Exception as e:
                st.error(f"Error loading analytics: {str(e)}")
        else:
            st.info("Database analytics not available")
    
    with col_history:
        st.subheader("📝 Recent Queries")
        if db:
            try:
                history = db.get_query_history(limit=10)
                if history:
                    for record in history:
                        with st.expander(f"Query: {record['query'][:50]}..."):
                            st.write(f"**Decision:** {record['decision']}")
                            if record['amount']:
                                st.write(f"**Amount:** {record['amount']}")
                            st.write(f"**Confidence:** {record['confidence']}")
                            st.write(f"**Document:** {record['document']}")
                            st.write(f"**Time:** {record['timestamp']}")
                else:
                    st.info("No query history available yet.")
            except Exception as e:
                st.error(f"Error loading history: {str(e)}")
        else:
            st.info("Database history not available")

    # Footer
    st.markdown("---")
    st.markdown("""
    **Instructions:**
    1. Upload a PDF document (policy, contract, etc.)
    2. Enter your OpenAI API key in the sidebar
    3. Type a natural language query about the document
    4. Get intelligent analysis with decisions and justifications
    5. View analytics and query history below
    """)

if __name__ == "__main__":
    main()
