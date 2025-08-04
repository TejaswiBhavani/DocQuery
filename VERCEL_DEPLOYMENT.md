# Vercel Deployment Guide

This document explains how to deploy the DocQuery Streamlit application to Vercel.

## Files Created for Vercel Deployment

### 1. requirements.txt
Contains all Python dependencies needed for the application:
```
streamlit>=1.47.0
openai>=1.97.1
PyPDF2>=3.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
psycopg2-binary>=2.9.0
sqlalchemy>=2.0.0
```

### 2. vercel.json
Configures Vercel to use the Python runtime and route all requests to app.py:
```json
{
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

### 3. app.py Modifications
The application now automatically detects the `$PORT` environment variable provided by Vercel:

```python
if __name__ == "__main__":
    # For Vercel deployment, check if PORT environment variable is set
    port = os.environ.get("PORT")
    if port:
        # When deployed on Vercel, we need to run Streamlit with the provided PORT
        import subprocess
        import sys
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", __file__,
            "--server.port", str(port),
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ])
    else:
        # Local development - run normally
        main()
```

## Deployment Steps

1. **Push to GitHub**: Ensure your repository with these files is pushed to GitHub.

2. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Sign up/login with your GitHub account
   - Click "New Project"
   - Import your repository

3. **Deploy**:
   - Vercel will automatically detect the configuration
   - The build will use `@vercel/python` runtime
   - All routes will be handled by `app.py`
   - The app will automatically use the correct port

4. **Access Your App**:
   - Once deployed, Vercel will provide a URL
   - Your Streamlit app will be accessible at that URL

## Key Features

✅ **Automatic Port Detection**: Uses Vercel's `$PORT` environment variable  
✅ **Python Runtime**: Configured for `@vercel/python` builder  
✅ **Route Handling**: All requests routed to `app.py`  
✅ **Streamlit Compatibility**: Properly configured for Streamlit deployment  
✅ **Backwards Compatibility**: Still works for local development  

## Local Testing

To test locally with the same configuration:
```bash
# Install dependencies
pip install -r requirements.txt

# Run normally (will use local mode)
python app.py

# Or run with streamlit directly
streamlit run app.py
```

## Environment Variables (Optional)

You can set these in Vercel's dashboard under "Environment Variables":

- `DATABASE_URL`: PostgreSQL connection string (optional)
- `OPENAI_API_KEY`: For OpenAI integration (optional)
- Any other environment variables your app needs

## Troubleshooting

- **Build fails**: Check that all dependencies in requirements.txt are available
- **App doesn't start**: Verify the PORT environment variable handling
- **Routing issues**: Ensure vercel.json routes are correctly configured
- **Import errors**: Make sure all required files are in the repository