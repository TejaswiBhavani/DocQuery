# AI Document Analysis System

## Overview

This is a Streamlit-based Python web application that processes PDF documents (primarily insurance policies) and provides intelligent decision-making through AI analysis. The system combines document processing, semantic search, and OpenAI's GPT-4o model to analyze user queries against uploaded documents and provide structured decisions.

**Latest Update (July 24, 2025)**: Added local AI support eliminating the need for external API keys. Enhanced the system with multi-format document support (PDF, Word, Email), professional UI/UX design with gradient styling and intuitive user experience. Users can now choose between local AI processing (no API key needed) or OpenAI for advanced analysis.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a modular architecture with clear separation of concerns:

- **Frontend**: Streamlit web interface for user interactions
- **Document Processing**: PDF text extraction and chunking using PyPDF2
- **Semantic Search**: FAISS-based vector search with sentence transformers
- **Query Processing**: Natural language query parsing using regex patterns
- **AI Integration**: OpenAI GPT-3.5-turbo for intelligent decision making

The system is designed to run entirely in Replit without external dependencies beyond the OpenAI API.

## Key Components

### 1. Document Processor (`document_processor.py`)
- **Purpose**: Extracts and processes text from multiple document formats
- **Key Features**: 
  - Multi-format support: PDF, Word (.docx), Email (.eml), Text (.txt)
  - Automatic file type detection based on extensions
  - Text cleaning and chunking for all formats
  - Email metadata extraction (subject, sender, recipient, date)
  - Error handling for encrypted, corrupted, or unsupported files
- **Design Decision**: Extensible architecture with format-specific processors and graceful fallbacks

### 2. Query Parser (`query_parser.py`)
- **Purpose**: Extracts structured information from natural language queries
- **Key Features**:
  - Regex-based parsing for age, gender, procedure, location, policy duration
  - Multiple pattern matching for robust extraction
  - No external NLP dependencies
- **Design Decision**: Uses regex patterns instead of ML models to avoid external dependencies and ensure reliability

### 3. Vector Search (Multi-tier approach)
- **Advanced Search (`vector_search.py`)**: 
  - FAISS indexing with sentence transformer embeddings (all-MiniLM-L6-v2)
  - Highest quality semantic understanding
- **Enhanced Search (`enhanced_vector_search.py`)**:
  - TF-IDF vectorization with cosine similarity
  - Medical domain term expansion and normalization
  - Semantic query expansion for better matching
- **Simple Search (`simple_vector_search.py`)**:
  - Text-based keyword matching with Jaccard similarity
  - Fallback option when ML dependencies unavailable
- **Design Decision**: Multi-tier fallback ensures system works in all environments while providing best available search quality

### 4. AI Analysis Clients
#### OpenAI Client (`openai_client.py`)
- **Purpose**: Handles AI-powered analysis using OpenAI models
- **Key Features**:
  - Integration with OpenAI GPT-3.5-turbo
  - Structured JSON response format
  - Context-aware prompting with document chunks
- **Design Decision**: Uses GPT-3.5-turbo for cost-effectiveness while maintaining quality

#### Local AI Client (`local_ai_client.py`)
- **Purpose**: Provides AI analysis without external API dependencies
- **Key Features**:
  - Rule-based decision analysis with NLP enhancement
  - Optional transformer models for sentiment analysis
  - Automatic fallback to basic analysis if models unavailable
  - Age, procedure, location, and policy duration analysis
  - Context-aware justification generation
- **Design Decision**: Combines rule-based logic with optional ML models for robust offline analysis

### 5. Database Manager (`database_manager.py`)
- **Purpose**: Manages persistent storage and audit trail
- **Key Features**:
  - Document upload tracking
  - Query history storage
  - Analysis results archiving
  - Analytics and search functionality
- **Design Decision**: Uses PostgreSQL for reliable audit trail and complex querying

### 6. Main Application (`app.py`)
- **Purpose**: Streamlit frontend and application orchestration
- **Key Features**:
  - File upload interface
  - Query input and processing
  - Results display with database integration
  - Analytics dashboard
  - Query history search

## Data Flow

1. **Document Upload**: User uploads PDF through Streamlit interface
2. **Text Extraction**: PDF content is extracted and cleaned
3. **Chunking**: Text is split into manageable chunks
4. **Embedding Generation**: Chunks are converted to vector embeddings
5. **Index Building**: FAISS index is created for similarity search
6. **Query Processing**: User query is parsed to extract structured information
7. **Semantic Search**: Query embeddings are used to find relevant document chunks
8. **AI Analysis**: OpenAI analyzes query and relevant chunks to make decisions
9. **Results Display**: Structured results are presented to the user

## External Dependencies

### Required Libraries
- `streamlit`: Web interface framework
- `PyPDF2`: PDF text extraction
- `sentence-transformers`: Text embedding generation (optional)
- `faiss-cpu`: Vector similarity search (optional)
- `scikit-learn`: TF-IDF semantic search
- `openai`: AI analysis integration
- `numpy`: Numerical operations
- `psycopg2-binary`: PostgreSQL database connectivity
- `sqlalchemy`: Database ORM

### External Services
- **OpenAI API**: Required for intelligent decision making
  - Model: GPT-3.5-turbo
  - Authentication: User-provided API key
  - Response format: Structured JSON
- **PostgreSQL Database**: Stores analysis history and audit trail
  - Tables: documents, queries, analysis_results
  - Features: Analytics, search, audit tracking

## Deployment Strategy

### Replit Configuration
- **Platform**: Designed to run entirely in Replit
- **Port**: Configured for Streamlit's default port 8501
- **Dependencies**: All libraries available in Replit ecosystem
- **File I/O**: Minimal local file operations, primarily using in-memory processing

### Security Considerations
- API keys are handled securely through Streamlit's password input
- No persistent storage of sensitive information
- Temporary file handling for uploaded PDFs

### Error Handling
- Comprehensive error handling for PDF processing failures
- API key validation and error reporting
- Network failure resilience
- User-friendly error messages throughout the application

### Scalability Considerations
- In-memory processing suitable for individual document analysis
- FAISS indexing provides efficient search for large documents
- Modular design allows for easy component replacement or enhancement