#!/usr/bin/env python3
"""
Vercel entry point for DocQuery Streamlit application.
This file provides the WSGI/ASGI interface that Vercel needs.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Set environment variables for Streamlit
os.environ.setdefault('STREAMLIT_SERVER_HEADLESS', 'true')
os.environ.setdefault('STREAMLIT_SERVER_PORT', '8080')
os.environ.setdefault('STREAMLIT_SERVER_ADDRESS', '0.0.0.0')
os.environ.setdefault('STREAMLIT_BROWSER_GATHER_USAGE_STATS', 'false')
os.environ.setdefault('STREAMLIT_SERVER_ENABLE_CORS', 'true')
os.environ.setdefault('STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION', 'false')

def app(environ, start_response):
    """
    WSGI application entry point for Vercel.
    """
    # For Vercel, we need to return a response that indicates how to access the Streamlit app
    response_body = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>DocQuery - AI Document Analysis</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta http-equiv="refresh" content="3;url=/streamlit">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-direction: column;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                padding: 40px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            }
            .logo {
                font-size: 3rem;
                margin-bottom: 20px;
            }
            h1 {
                margin: 0 0 20px 0;
                font-size: 2.5rem;
                font-weight: 300;
            }
            p {
                font-size: 1.2rem;
                opacity: 0.9;
                margin-bottom: 30px;
            }
            .button {
                display: inline-block;
                padding: 15px 30px;
                background: rgba(255, 255, 255, 0.2);
                color: white;
                text-decoration: none;
                border-radius: 50px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                font-size: 1.1rem;
                transition: all 0.3s ease;
                margin: 10px;
            }
            .button:hover {
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-2px);
            }
            .spinner {
                border: 3px solid rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                border-top: 3px solid white;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 20px auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .instructions {
                background: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 10px;
                margin-top: 30px;
                text-align: left;
            }
            .instructions h3 {
                margin-top: 0;
                color: #fff;
            }
            .instructions p {
                font-size: 1rem;
                margin-bottom: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">📋</div>
            <h1>DocQuery</h1>
            <p>AI-Powered Document Analysis System</p>
            
            <div class="spinner"></div>
            <p>Loading application...</p>
            
            <div class="instructions">
                <h3>🚀 Deployment Instructions</h3>
                <p><strong>For Vercel deployment:</strong></p>
                <p>Streamlit applications require persistent server processes, which work differently on Vercel.</p>
                <p><strong>Recommended deployment platforms:</strong></p>
                <ul style="text-align: left; max-width: 400px; margin: 0 auto;">
                    <li><strong>Heroku:</strong> Perfect for Streamlit apps (uses Procfile)</li>
                    <li><strong>Railway:</strong> Easy deployment with git integration</li>
                    <li><strong>Render:</strong> Free tier available</li>
                    <li><strong>Streamlit Cloud:</strong> Designed specifically for Streamlit</li>
                </ul>
                
                <p style="margin-top: 20px;"><strong>For Vercel (Advanced):</strong></p>
                <p>Run the application using the FastAPI endpoint instead:</p>
                <code style="background: rgba(0,0,0,0.3); padding: 5px 10px; border-radius: 5px; display: block; margin: 10px 0;">
                    uvicorn api:app --host 0.0.0.0 --port $PORT
                </code>
            </div>
            
            <a href="/api/health" class="button">🔧 API Status</a>
            <a href="https://github.com/TejaswiBhavani/DocQuery" class="button">📚 GitHub</a>
        </div>
        
        <script>
            // Try to redirect to streamlit after a delay
            setTimeout(function() {
                window.location.href = '/streamlit';
            }, 3000);
        </script>
    </body>
    </html>
    '''
    
    status = '200 OK'
    headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(response_body.encode('utf-8'))))
    ]
    start_response(status, headers)
    return [response_body.encode('utf-8')]

# For Vercel compatibility
application = app

def handler(event, context):
    """
    Vercel serverless function handler.
    This provides information about the app and deployment instructions.
    """
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        },
        'body': {
            'message': 'DocQuery - AI Document Analysis System',
            'status': 'Running',
            'deployment': 'Vercel',
            'note': 'Streamlit apps work best on platforms like Heroku, Railway, or Streamlit Cloud',
            'api_available': True,
            'endpoints': {
                'health': '/api/health',
                'analyze': '/api/analyze',
                'web_interface': 'Best deployed on Heroku/Railway/Render'
            },
            'instructions': {
                'heroku': 'git push heroku main (uses Procfile)',
                'railway': 'Connect GitHub repo to Railway',
                'render': 'Connect GitHub repo to Render',
                'streamlit_cloud': 'Deploy directly from GitHub'
            }
        }
    }

if __name__ == '__main__':
    # For local development, run Streamlit
    import subprocess
    subprocess.run(['streamlit', 'run', 'app.py', '--server.port', '8501'])