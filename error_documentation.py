"""
Error Documentation Page for DocQuery System

This module creates a documentation page similar to Vercel's error documentation,
displaying all error codes, their descriptions, and solutions in a user-friendly format.
"""

import streamlit as st
from error_codes import DocQueryErrorCodes, ErrorCategory
from typing import Dict, List


def render_error_documentation():
    """Render the complete error documentation page."""
    
    st.set_page_config(
        page_title="DocQuery Error Codes",
        page_icon="⚠️",
        layout="wide"
    )
    
    # Custom CSS for error documentation
    st.markdown("""
    <style>
    .error-header {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .error-category {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 10px;
        margin: 1.5rem 0;
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    .error-card {
        background: white;
        border: 1px solid #e1e8ed;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .error-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        border-color: #667eea;
    }
    
    .error-code {
        background: #667eea;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    
    .status-code {
        background: #ff6b6b;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    
    .error-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 0.5rem 0;
    }
    
    .error-description {
        color: #5a6c7d;
        margin: 1rem 0;
        line-height: 1.6;
    }
    
    .causes-solutions {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
        margin-top: 1rem;
    }
    
    .causes-section, .solutions-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
    }
    
    .section-title {
        font-weight: bold;
        color: #495057;
        margin-bottom: 0.5rem;
        font-size: 1rem;
    }
    
    .list-item {
        color: #6c757d;
        margin: 0.3rem 0;
        padding-left: 1rem;
        position: relative;
    }
    
    .list-item::before {
        content: "•";
        color: #667eea;
        font-weight: bold;
        position: absolute;
        left: 0;
    }
    
    .category-summary {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }
    
    .toc-section {
        background: white;
        border: 1px solid #e1e8ed;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .toc-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    
    .toc-item {
        padding: 0.5rem 0;
        border-bottom: 1px solid #f1f3f4;
    }
    
    .toc-item:last-child {
        border-bottom: none;
    }
    
    .toc-link {
        color: #667eea;
        text-decoration: none;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .toc-link:hover {
        color: #764ba2;
    }
    
    .error-count {
        background: #e9ecef;
        color: #495057;
        padding: 0.2rem 0.5rem;
        border-radius: 10px;
        font-size: 0.8rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="error-header">
        <h1>⚠️ DocQuery Error Codes</h1>
        <p>When developing your document analysis applications with DocQuery, you may encounter a variety of errors. They can reflect issues that happen with document processing, AI analysis, or internal problems at the level of your application's deployment.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Table of Contents
    render_table_of_contents()
    
    # Error Categories
    all_errors = DocQueryErrorCodes.get_all_errors()
    categories = set(error.category for error in all_errors.values())
    
    for category in sorted(categories):
        render_error_category(category, all_errors)


def render_table_of_contents():
    """Render the table of contents for error categories."""
    all_errors = DocQueryErrorCodes.get_all_errors()
    categories = {}
    
    # Group errors by category
    for error in all_errors.values():
        if error.category not in categories:
            categories[error.category] = []
        categories[error.category].append(error)
    
    st.markdown("""
    <div class="toc-section">
        <div class="toc-title">📋 Error Categories</div>
    """, unsafe_allow_html=True)
    
    for category, errors in sorted(categories.items()):
        error_count = len(errors)
        st.markdown(f"""
        <div class="toc-item">
            <a href="#{category.lower()}-errors" class="toc-link">
                <span>{category} Errors</span>
                <span class="error-count">{error_count} error{'s' if error_count != 1 else ''}</span>
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


def render_error_category(category: str, all_errors: Dict):
    """Render all errors for a specific category."""
    category_errors = {code: error for code, error in all_errors.items() 
                      if error.category == category}
    
    if not category_errors:
        return
    
    # Category header
    st.markdown(f"""
    <div class="error-category" id="{category.lower()}-errors">
        {get_category_icon(category)} {category} Errors
    </div>
    """, unsafe_allow_html=True)
    
    # Category description
    category_description = get_category_description(category)
    if category_description:
        st.markdown(f"""
        <div class="category-summary">
            {category_description}
        </div>
        """, unsafe_allow_html=True)
    
    # Render each error in the category
    for error_code, error_info in sorted(category_errors.items()):
        render_error_card(error_info)


def render_error_card(error_info):
    """Render an individual error code card."""
    st.markdown(f"""
    <div class="error-card">
        <div>
            <span class="error-code">{error_info.code}</span>
            <span class="status-code">{get_category_prefix(error_info.category)}{error_info.status_code}</span>
        </div>
        <div class="error-title">{error_info.title}</div>
        <div class="error-description">{error_info.description}</div>
        
        <div class="causes-solutions">
            <div class="causes-section">
                <div class="section-title">🔍 Common Causes</div>
                {"".join(f'<div class="list-item">{cause}</div>' for cause in error_info.causes)}
            </div>
            <div class="solutions-section">
                <div class="section-title">💡 Solutions</div>
                {"".join(f'<div class="list-item">{solution}</div>' for solution in error_info.solutions)}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def get_category_icon(category: str) -> str:
    """Get icon for error category."""
    icons = {
        "Document": "📄",
        "AI": "🤖",
        "Database": "🗄️",
        "Search": "🔍",
        "Configuration": "⚙️",
        "Network": "🌐",
        "Internal": "⚡"
    }
    return icons.get(category, "⚠️")


def get_category_prefix(category: str) -> str:
    """Get status code prefix for category."""
    prefixes = {
        "Document": "Doc",
        "AI": "AI",
        "Database": "DB",
        "Search": "Search",
        "Configuration": "Config",
        "Network": "Net",
        "Internal": "Internal"
    }
    return prefixes.get(category, "Error")


def get_category_description(category: str) -> str:
    """Get description for error category."""
    descriptions = {
        "Document": "Errors related to document processing, format detection, and text extraction. These occur when uploading, parsing, or analyzing document files.",
        "AI": "Errors related to AI model loading, processing, and analysis. These include issues with OpenAI API, local models, and analysis timeouts.",
        "Database": "Errors related to database connections, data storage, and retrieval operations. The application can continue to work without database features.",
        "Search": "Errors related to vector search, index building, and query processing. These affect the document search and retrieval functionality.",
        "Configuration": "Errors related to system configuration, environment variables, and application setup.",
        "Network": "Errors related to network connectivity, API calls, and external service communications.",
        "Internal": "Internal system errors including memory issues, unexpected failures, and resource exhaustion."
    }
    return descriptions.get(category, "")


def create_error_sidebar():
    """Create a sidebar for navigation and search."""
    st.sidebar.title("🔍 Error Search")
    
    # Search functionality
    search_term = st.sidebar.text_input("Search error codes:", placeholder="Type error name...")
    
    if search_term:
        all_errors = DocQueryErrorCodes.get_all_errors()
        matching_errors = {}
        
        for code, error in all_errors.items():
            if (search_term.lower() in code.lower() or 
                search_term.lower() in error.title.lower() or
                search_term.lower() in error.description.lower()):
                matching_errors[code] = error
        
        if matching_errors:
            st.sidebar.markdown("### 🎯 Search Results")
            for code, error in matching_errors.items():
                st.sidebar.markdown(f"**{error.code}**")
                st.sidebar.markdown(f"{error.title}")
                st.sidebar.markdown("---")
        else:
            st.sidebar.info("No matching errors found")
    
    # Category filter
    st.sidebar.markdown("### 📂 Categories")
    all_errors = DocQueryErrorCodes.get_all_errors()
    categories = sorted(set(error.category for error in all_errors.values()))
    
    for category in categories:
        category_count = len([e for e in all_errors.values() if e.category == category])
        icon = get_category_icon(category)
        st.sidebar.markdown(f"{icon} {category} ({category_count})")


def main():
    """Main function to run the error documentation page."""
    create_error_sidebar()
    render_error_documentation()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #6c757d;">
        <p>📚 For more help with DocQuery, refer to the main application documentation.</p>
        <p><em>Last updated: 2025</em></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()