#!/usr/bin/env python3
"""
Build script for DocQuery Vercel deployment.
Generates static files in the public directory.
"""

import os
import shutil
from pathlib import Path

def create_public_directory():
    """Create public directory with static files for Vercel deployment."""
    
    # Create public directory
    public_dir = Path("public")
    public_dir.mkdir(exist_ok=True)
    
    # Create index.html that provides information about the app
    index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DocQuery - AI Document Analysis</title>
    <meta name="description" content="AI-Powered Document Analysis System">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            padding: 40px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            text-align: center;
        }
        .logo {
            font-size: 4rem;
            margin-bottom: 20px;
        }
        h1 {
            margin: 0 0 20px 0;
            font-size: 3rem;
            font-weight: 300;
        }
        .subtitle {
            font-size: 1.5rem;
            opacity: 0.9;
            margin-bottom: 30px;
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 40px 0;
        }
        .feature {
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .feature h3 {
            margin-top: 0;
            font-size: 1.5rem;
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
        .api-section {
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            margin-top: 40px;
            text-align: left;
        }
        .api-section h3 {
            text-align: center;
            margin-bottom: 20px;
        }
        code {
            background: rgba(0, 0, 0, 0.3);
            padding: 5px 10px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
        }
        .endpoint {
            margin: 15px 0;
            padding: 15px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">📋</div>
        <h1>DocQuery</h1>
        <p class="subtitle">AI-Powered Document Analysis System</p>
        
        <div class="features">
            <div class="feature">
                <h3>🤖 AI-Powered Analysis</h3>
                <p>Advanced natural language processing to understand and analyze documents with intelligent query responses.</p>
            </div>
            <div class="feature">
                <h3>📄 Multiple Formats</h3>
                <p>Support for PDF, DOCX, and text files with automatic content extraction and processing.</p>
            </div>
            <div class="feature">
                <h3>🔍 Smart Search</h3>
                <p>Vector-based semantic search to find relevant information quickly and accurately.</p>
            </div>
        </div>
        
        <div class="api-section">
            <h3>🔧 API Endpoints</h3>
            
            <div class="endpoint">
                <strong>Health Check:</strong><br>
                <code>GET /api/health</code><br>
                <small>Check the API service status</small>
            </div>
            
            <div class="endpoint">
                <strong>Document Analysis:</strong><br>
                <code>POST /api/analyze</code><br>
                <small>Analyze documents and answer queries</small>
            </div>
            
            <div class="endpoint">
                <strong>Batch Processing:</strong><br>
                <code>POST /api/batch</code><br>
                <small>Process multiple documents at once</small>
            </div>
        </div>
        
        <div style="margin-top: 40px;">
            <a href="/api/health" class="button">🔧 API Status</a>
            <a href="https://github.com/TejaswiBhavani/DocQuery" class="button">📚 GitHub</a>
            <a href="/api/docs" class="button">📖 API Docs</a>
        </div>
        
        <div style="margin-top: 40px; opacity: 0.8;">
            <p><strong>For Full Streamlit Interface:</strong></p>
            <p>Deploy on <strong>Heroku</strong>, <strong>Railway</strong>, or <strong>Streamlit Cloud</strong> for the complete interactive experience.</p>
        </div>
    </div>
</body>
</html>"""
    
    # Write index.html
    with open(public_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(index_html)
    
    # Create a simple 404 page
    error_404 = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - DocQuery</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            text-align: center;
            padding: 100px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            padding: 40px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
            display: inline-block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>404 - Page Not Found</h1>
        <p>The page you're looking for doesn't exist.</p>
        <a href="/" style="color: white;">← Go Home</a>
    </div>
</body>
</html>"""
    
    with open(public_dir / "404.html", "w", encoding="utf-8") as f:
        f.write(error_404)
    
    # Copy style.css if it exists
    if Path("style.css").exists():
        shutil.copy2("style.css", public_dir / "style.css")
    
    print("✅ Public directory created successfully!")
    print(f"📁 Files created in {public_dir.absolute()}:")
    for file in public_dir.iterdir():
        print(f"   - {file.name}")

if __name__ == "__main__":
    create_public_directory()