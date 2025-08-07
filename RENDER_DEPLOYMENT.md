# Render Deployment Guide for DocQuery

This document provides step-by-step instructions to deploy the DocQuery AI Document Analysis System to Render.

## Prerequisites

- A [Render](https://render.com) account
- Access to this GitHub repository

## Quick Fix for Deployment Issues

### Most Common Solutions

1. **Use Python 3.11**: The `runtime.txt` file now specifies Python 3.11.6, which is fully compatible with Render.

2. **Optimized Build Process**: The deployment now uses a robust build script (`build.sh`) that:
   - Updates pip to the latest version
   - Uses `--no-cache-dir` to avoid memory issues
   - Has fallback requirements if main installation fails
   - Verifies installation before completing

3. **Alternative Requirements**: If build fails with main `requirements.txt`, it automatically falls back to `requirements-render.txt` with minimal, stable versions.

## Deployment Options

### Option 1: Automatic Deployment with render.yaml (Recommended)

1. **Connect Repository**: In your Render dashboard, connect your GitHub repository containing DocQuery.

2. **Automatic Detection**: Render will automatically detect the `render.yaml` file and configure the deployment settings.

3. **Environment Variables**: The following environment variables are automatically configured:
   - `PYTHONUNBUFFERED=1`
   - `STREAMLIT_SERVER_HEADLESS=true`
   - `STREAMLIT_BROWSER_GATHER_USAGE_STATS=false`

### Option 2: Manual Web Service Setup

1. **Create Web Service**: In Render dashboard, click "New" → "Web Service"

2. **Connect Repository**: Connect your GitHub repository

3. **Configure Settings**:
   - **Name**: `docquery-app` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true --server.enableCORS false --server.enableXsrfProtection false`
   - **Instance Type**: Free tier is sufficient for basic usage

4. **Environment Variables**: Add the following environment variables:
   - `PYTHONUNBUFFERED=1`
   - `STREAMLIT_SERVER_HEADLESS=true`
   - `STREAMLIT_BROWSER_GATHER_USAGE_STATS=false`

### Option 3: Using the Startup Script

You can also use the provided startup script:
- **Start Command**: `./start.sh`

## Troubleshooting Build Failures

### Common Issues and Solutions

#### 1. Build Timeout
- **Problem**: Large ML dependencies (PyTorch, transformers) cause timeout
- **Solution**: The build script now uses optimized installation and fallback requirements

#### 2. Memory Issues During Build
- **Problem**: Not enough memory to install all dependencies
- **Solution**: 
  - Uses `--no-cache-dir` flag to reduce memory usage
  - Fallback to minimal requirements file
  - Consider upgrading to Starter plan for more memory

#### 3. Python Version Compatibility
- **Problem**: Python 3.12 not fully supported
- **Solution**: Now uses Python 3.11.6 (specified in `runtime.txt`)

#### 4. Dependency Conflicts
- **Problem**: Version conflicts between packages
- **Solution**: Optimized `requirements.txt` with compatible version ranges

#### 5. Streamlit Configuration Issues
- **Problem**: CORS or server configuration issues
- **Solution**: Updated `.streamlit/config.toml` and startup commands

### Build Log Analysis

If deployment fails, check the build logs for these indicators:

- ❌ `pip install failed`: Use fallback requirements
- ❌ `timeout`: Consider upgrading plan or using minimal requirements  
- ❌ `memory error`: Upgrade to paid plan
- ❌ `python version`: Check `runtime.txt`

### Emergency Deployment (Minimal Features)

If all else fails, use these minimal requirements by replacing `requirements.txt` content:

```
streamlit==1.28.0
PyPDF2==3.0.1
python-docx==0.8.11
numpy==1.21.6
scikit-learn==1.2.2
pandas==1.5.3
```

## Features Available After Deployment

The deployed application includes:

- ✅ **Full Streamlit Web Interface**: Complete web-based document analysis interface
- ✅ **Document Processing**: PDF, DOCX, and email document support
- ✅ **AI Search**: Intelligent search capabilities (features depend on available dependencies)
- ✅ **Multiple AI Backends**: Support for OpenAI API and local AI processing
- ✅ **Database Integration**: SQLAlchemy with PostgreSQL support for document storage
- ✅ **Real-time Analysis**: Interactive query processing and response generation

## Post-Deployment Configuration

### Optional: Database Setup

For persistent document storage, you can add a PostgreSQL database:

1. In Render dashboard, create a new PostgreSQL database
2. Add the database URL as an environment variable: `DATABASE_URL`
3. The application will automatically use the database for document storage

### Optional: OpenAI Integration

To enable OpenAI-powered analysis:

1. Add your OpenAI API key as an environment variable: `OPENAI_API_KEY`
2. The application will automatically detect and use OpenAI for enhanced AI processing

## Application URLs

After successful deployment:
- Your app will be available at: `https://[your-app-name].onrender.com`
- Health check endpoint: `https://[your-app-name].onrender.com/_stcore/health`

## Performance Considerations

- **Free Tier**: Suitable for development and light usage
- **Starter Plan**: Recommended for production use with consistent traffic
- **Pro Plans**: For high-traffic applications requiring guaranteed uptime

## Files Modified for Render Compatibility

The following files have been optimized for Render deployment:

- ✅ `runtime.txt`: Specifies Python 3.11.6
- ✅ `requirements.txt`: Optimized with compatible version ranges
- ✅ `requirements-render.txt`: Fallback minimal requirements
- ✅ `build.sh`: Robust build script with error handling
- ✅ `render.yaml`: Optimized service configuration
- ✅ `Procfile`: Updated with deployment-friendly flags
- ✅ `start.sh`: Enhanced startup script
- ✅ `.streamlit/config.toml`: Deployment-optimized configuration

## Support

For deployment issues specific to Render, consult:
- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com/)

For application-specific issues, refer to the main README.md in this repository.