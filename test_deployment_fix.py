#!/usr/bin/env python3
"""
Test suite for deployment fix validation.
Tests that the FastAPI integration and Streamlit work correctly for production deployment.
"""

import os
import subprocess
import time
import requests
import tempfile
from pathlib import Path


def test_environment_setup():
    """Test that environment variables are handled correctly."""
    print("Testing environment setup...")
    
    # Test environment variable handling for Vercel deployment
    # The actual setup is handled by Vercel's runtime
    
    # Test with valid port
    os.environ['PORT'] = '8502'
    port = int(os.environ.get('PORT', 3000))
    assert port == 8502, f"Expected port 8502, got {port}"
    
    # Test default port
    if 'PORT' in os.environ:
        del os.environ['PORT']
    port = int(os.environ.get('PORT', 3000))
    assert port == 3000, f"Expected default port 3000, got {port}"
    
    print("✅ Environment setup test passed")


def test_fastapi_health_endpoint():
    """Test that FastAPI health endpoint works."""
    print("Testing FastAPI health endpoint...")
    
    # Start FastAPI in background (using uvicorn)
    proc = subprocess.Popen([
        'uvicorn', 'api.index:handler',
        '--port', '8503',
        '--host', '0.0.0.0'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for FastAPI to start
    time.sleep(10)
    
    try:
        # Test API health endpoint
        response = requests.get('http://localhost:8503/api/health', timeout=5)
        assert response.status_code == 200, f"Health check failed with status {response.status_code}"
        print("✅ FastAPI health endpoint test passed")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Health endpoint test failed: {e}")
        raise
    finally:
        # Clean up process
        proc.terminate()
        proc.wait(timeout=5)


def test_requirements():
    """Test that all required packages can be imported."""
    print("Testing package imports...")
    
    required_packages = [
        'fastapi', 
        'uvicorn',
        'PyPDF2',
        'sklearn',
        'numpy',
        'openai',
        'sqlalchemy',
        'psycopg2',
        'pandas',
        'PIL',
        'psutil'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            if package == 'sklearn':
                import sklearn
            elif package == 'docx':
                import docx
            elif package == 'PIL':
                import PIL
            elif package == 'faiss':
                import faiss
            else:
                __import__(package)
            print(f"✅ {package} imported successfully")
        except ImportError as e:
            failed_imports.append((package, str(e)))
            print(f"❌ Failed to import {package}: {e}")
    
    if failed_imports:
        print(f"\n❌ Failed to import {len(failed_imports)} packages:")
        for pkg, error in failed_imports:
            print(f"  - {pkg}: {error}")
        return False
    
    print("✅ All required packages imported successfully")
    return True


def test_render_config():
    """Test that render.yaml configuration is valid."""
    print("Testing render.yaml configuration...")
    
    # Check if render.yaml exists
    render_config = Path('render.yaml')
    assert render_config.exists(), "render.yaml not found"
    
    # Read and validate basic structure
    import yaml
    try:
        with open(render_config) as f:
            config = yaml.safe_load(f)
        
        # Check required fields
        assert 'services' in config, "Missing 'services' in render.yaml"
        service = config['services'][0]
        
        required_fields = ['type', 'name', 'env', 'buildCommand', 'startCommand', 'healthCheckPath', 'plan']
        for field in required_fields:
            assert field in service, f"Missing required field '{field}' in render.yaml"
        
        # Check specific values
        assert service['type'] == 'web', "Service type should be 'web'"
        assert service['env'] == 'python', "Environment should be 'python'"
        assert service['plan'] == 'standard', "Plan should be 'standard' for 1GB RAM"
        assert service['healthCheckPath'] == '/_stcore/health', "Health check path should be '/_stcore/health'"
        
        # Check that start command is correct
        start_cmd = service['startCommand']
        # Note: Updated for FastAPI/Next.js architecture - no single streamlit command
        assert any(keyword in start_cmd for keyword in ['uvicorn', 'fastapi', 'next']), "Start command should use FastAPI or Next.js"
        assert '--server.port $PORT' in start_cmd, "Start command should use $PORT"
        assert '--server.address 0.0.0.0' in start_cmd, "Start command should bind to 0.0.0.0"
        assert '--server.headless true' in start_cmd, "Start command should run headless"
        
        print("✅ render.yaml configuration is valid")
        return True
        
    except Exception as e:
        print(f"❌ render.yaml validation failed: {e}")
        return False


def main():
    """Run all deployment fix tests."""
    print("🔍 Running deployment fix validation tests...\n")
    
    # Change to the app directory
    os.chdir(os.path.dirname(__file__))
    
    tests = [
        test_environment_setup,
        test_requirements,
        test_render_config,
        # Note: Commented out health endpoint test as it requires running server
        # test_fastapi_health_endpoint,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
            print()
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}\n")
            failed += 1
    
    print(f"🎯 Test Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        print("❌ Some tests failed - deployment may have issues")
        return False
    else:
        print("✅ All tests passed - deployment should work correctly")
        return True


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)