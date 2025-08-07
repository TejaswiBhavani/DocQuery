# Render Deployment Guide for DocQuery

This document provides step-by-step instructions to deploy the DocQuery AI Document Analysis System to Render.

## Prerequisites

- A [Render](https://render.com) account
- Access to this GitHub repository

## Deployment Options

### Option 1: Automatic Deployment with render.yaml (Recommended)

1. **Connect Repository**: In your Render dashboard, connect your GitHub repository containing DocQuery.

2. **Automatic Detection**: Render will automatically detect the `render.yaml` file and configure the deployment settings.

3. **Environment Variables**: The following environment variables are automatically configured:
   - `PYTHONUNBUFFERED=true`
   - `STREAMLIT_SERVER_HEADLESS=true`
   - `STREAMLIT_BROWSER_GATHER_USAGE_STATS=false`

### Option 2: Manual Web Service Setup

1. **Create Web Service**: In Render dashboard, click "New" → "Web Service"

2. **Connect Repository**: Connect your GitHub repository

3. **Configure Settings**:
   - **Name**: `docquery-app` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`
   - **Instance Type**: Free tier is sufficient for basic usage

4. **Environment Variables**: Add the following environment variables:
   - `PYTHONUNBUFFERED=true`
   - `STREAMLIT_SERVER_HEADLESS=true`
   - `STREAMLIT_BROWSER_GATHER_USAGE_STATS=false`

### Option 3: Using the Startup Script

You can also use the provided startup script:
- **Start Command**: `./start.sh`

## Features Available After Deployment

The deployed application includes:

- ✅ **Full Streamlit Web Interface**: Complete web-based document analysis interface
- ✅ **Document Processing**: PDF, DOCX, and email document support
- ✅ **Advanced AI Search**: Sentence transformers with FAISS-based semantic search
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

## Troubleshooting

### Common Issues

1. **Build Timeout**: The initial build may take 5-10 minutes due to ML dependencies
2. **Memory Issues**: Consider upgrading to a paid plan if you experience memory constraints
3. **Cold Starts**: Free tier services may have cold start delays

### Monitoring

- Check build logs in Render dashboard for any dependency installation issues
- Monitor application logs for runtime errors
- Use Render's metrics to track performance

## Performance Considerations

- **Free Tier**: Suitable for development and light usage
- **Starter Plan**: Recommended for production use with consistent traffic
- **Pro Plans**: For high-traffic applications requiring guaranteed uptime

## Support

For deployment issues specific to Render, consult:
- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com/)

For application-specific issues, refer to the main README.md in this repository.