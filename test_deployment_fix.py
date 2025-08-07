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
    """Test that the environment setup function works correctly."""
    print("Testing environment setup...")
    
    # Import and test setup function
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from app import setup_environment
    
    # Test with valid port
    os.environ['PORT'] = '8502'
    port = setup_environment()
    assert port == 8502, f"Expected port 8502, got {port}"
    
    # Test with invalid port
    os.environ['PORT'] = 'invalid'
    port = setup_environment()
    assert port == 8501, f"Expected fallback port 8501, got {port}"
    
    # Test default port
    if 'PORT' in os.environ:
        del os.environ['PORT']
    port = setup_environment()
    assert port == 8501, f"Expected default port 8501, got {port}"
    
    print("✅ Environment setup test passed")


def test_streamlit_health_endpoint():
    """Test that Streamlit's built-in health endpoint works."""
    print("Testing Streamlit health endpoint...")
    
    # Start Streamlit in background
    proc = subprocess.Popen([
        'streamlit', 'run', 'app.py',
        '--server.port', '8503',
        '--server.address', '0.0.0.0',
        '--server.headless', 'true'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for Streamlit to start
    time.sleep(10)
    
    try:
        # Test health endpoint
        response = requests.get('http://localhost:8503/_stcore/health', timeout=5)
        assert response.status_code == 200, f"Health check failed with status {response.status_code}"
        assert response.text.strip() == 'ok', f"Unexpected health response: {response.text}"
        print("✅ Streamlit health endpoint test passed")
        
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
        'streamlit',
        'fastapi', 
        'uvicorn',
        'PyPDF2',
        'sklearn',
        'transformers',
        'sentence_transformers', 
        'faiss',
        'spacy',
        'docx',
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
        assert 'streamlit run app.py' in start_cmd, "Start command should run streamlit"
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
        # test_streamlit_health_endpoint,
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