# AI Document Analysis System

## Overview

This is a Streamlit-based Python web application that processes PDF documents (primarily insurance policies) and provides intelligent decision-making through AI analysis. The system combines document processing, semantic search, and OpenAI's GPT-3.5-turbo model to analyze user queries against uploaded documents and provide structured decisions.

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
- **Purpose**: Extracts and processes text from PDF files
- **Key Features**: 
  - PDF text extraction using PyPDF2
  - Text cleaning and chunking
  - Error handling for encrypted or corrupted PDFs
- **Design Decision**: Uses PyPDF2 for broad compatibility and simplicity

### 2. Query Parser (`query_parser.py`)
- **Purpose**: Extracts structured information from natural language queries
- **Key Features**:
  - Regex-based parsing for age, gender, procedure, location, policy duration
  - Multiple pattern matching for robust extraction
  - No external NLP dependencies
- **Design Decision**: Uses regex patterns instead of ML models to avoid external dependencies and ensure reliability

### 3. Vector Search (`vector_search.py`)
- **Purpose**: Provides semantic search capabilities using embeddings
- **Key Features**:
  - FAISS indexing for efficient similarity search
  - Sentence transformer embeddings (all-MiniLM-L6-v2)
  - Top-k document chunk retrieval
- **Design Decision**: Uses FAISS for fast similarity search and sentence-transformers for quality embeddings

### 4. OpenAI Client (`openai_client.py`)
- **Purpose**: Handles AI-powered analysis and decision making
- **Key Features**:
  - Integration with OpenAI GPT-3.5-turbo
  - Structured JSON response format
  - Context-aware prompting with document chunks
- **Design Decision**: Uses GPT-3.5-turbo for cost-effectiveness while maintaining quality

### 5. Main Application (`app.py`)
- **Purpose**: Streamlit frontend and application orchestration
- **Key Features**:
  - File upload interface
  - Query input and processing
  - Results display
  - Configuration management

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
- `sentence-transformers`: Text embedding generation
- `faiss-cpu`: Vector similarity search
- `openai`: AI analysis integration
- `numpy`: Numerical operations

### External Services
- **OpenAI API**: Required for intelligent decision making
  - Model: GPT-3.5-turbo
  - Authentication: User-provided API key
  - Response format: Structured JSON

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