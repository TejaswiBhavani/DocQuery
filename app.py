import streamlit as st
import os
import json
import tempfile
from document_processor import DocumentProcessor
from query_parser import QueryParser
from openai_client import OpenAIClient

# Try to import advanced vector search, fallback to simple search
try:
    from vector_search import VectorSearch
    ADVANCED_SEARCH_AVAILABLE = True
except ImportError:
    from simple_vector_search import SimpleVectorSearch as VectorSearch
    ADVANCED_SEARCH_AVAILABLE = False

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

                search_type = "Advanced semantic search" if ADVANCED_SEARCH_AVAILABLE else "Simple text-based search"
                st.success(f"✅ Document processed successfully! Found {len(chunks)} text chunks.")
                st.info(f"Using {search_type} for document analysis.")
                
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

    # Footer
    st.markdown("---")
    st.markdown("""
    **Instructions:**
    1. Upload a PDF document (policy, contract, etc.)
    2. Enter your OpenAI API key in the sidebar
    3. Type a natural language query about the document
    4. Get intelligent analysis with decisions and justifications
    """)

if __name__ == "__main__":
    main()
