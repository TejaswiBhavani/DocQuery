# DocQuery API Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install optional dependencies for full functionality
RUN pip install --no-cache-dir sentence-transformers faiss-cpu python-docx || echo "Optional dependencies failed, continuing with basic functionality"

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 docquery && chown -R docquery:docquery /app
USER docquery

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]