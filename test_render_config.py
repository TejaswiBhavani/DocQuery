#!/usr/bin/env python3
"""
Test script to validate Render deployment configuration.
This script checks that all the configuration is correct and tests key components.
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

def test_port_configuration():
    """Test that port configuration works correctly."""
    print("🔧 Testing port configuration...")
    
    # Test various PORT environment variable values
    test_cases = [
        ("8501", 8501),
        ("10000", 10000),
        ("3000", 3000),
        ("invalid", 8501),  # Should fallback to 8501
        ("", 8501),  # Should fallback to 8501
        ("99999", 8501),  # Out of range, should fallback
    ]
    
    for port_env, expected in test_cases:
        # Set environment variable
        if port_env:
            os.environ["PORT"] = port_env
        elif "PORT" in os.environ:
            del os.environ["PORT"]
        
        # Import and test the setup function
        sys.path.insert(0, "/home/runner/work/DocQuery/DocQuery")
        try:
            from app import setup_environment
            result = setup_environment()
            
            if result == expected:
                print(f"  ✅ PORT='{port_env}' -> {result} (expected {expected})")
            else:
                print(f"  ❌ PORT='{port_env}' -> {result} (expected {expected})")
                return False
                
        except Exception as e:
            print(f"  ❌ PORT='{port_env}' -> Error: {e}")
            return False
        finally:
            # Clean up import
            if 'app' in sys.modules:
                del sys.modules['app']
            if "/home/runner/work/DocQuery/DocQuery" in sys.path:
                sys.path.remove("/home/runner/work/DocQuery/DocQuery")
    
    return True

def test_health_endpoint():
    """Test that the health endpoint is correctly configured."""
    print("🏥 Testing health endpoint...")
    
    try:
        # Check if healthz.py exists and is importable
        health_file = Path("/home/runner/work/DocQuery/DocQuery/healthz.py")
        if not health_file.exists():
            print("  ❌ healthz.py file not found")
            return False
        
        print("  ✅ healthz.py file exists")
        
        # Try to import the health module
        sys.path.insert(0, "/home/runner/work/DocQuery/DocQuery")
        try:
            import healthz
            print("  ✅ healthz module imports successfully")
            
            # Check if FastAPI app exists
            if hasattr(healthz, 'app'):
                print("  ✅ FastAPI app is defined")
            else:
                print("  ❌ FastAPI app not found in healthz.py")
                return False
                
        except ImportError as e:
            print(f"  ❌ Failed to import healthz: {e}")
            return False
        finally:
            if 'healthz' in sys.modules:
                del sys.modules['healthz']
            if "/home/runner/work/DocQuery/DocQuery" in sys.path:
                sys.path.remove("/home/runner/work/DocQuery/DocQuery")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Health endpoint test failed: {e}")
        return False

def test_render_configuration():
    """Test that render.yaml is correctly configured."""
    print("🚀 Testing Render configuration...")
    
    try:
        render_file = Path("/home/runner/work/DocQuery/DocQuery/render.yaml")
        if not render_file.exists():
            print("  ❌ render.yaml file not found")
            return False
        
        with open(render_file, 'r') as f:
            content = f.read()
        
        # Check for required configurations
        checks = [
            ("healthCheckPath: /healthz", "Health check path"),
            ("uvicorn healthz:app", "Health endpoint startup"),
            ("streamlit run app.py", "Streamlit startup"),
            ("plan: starter", "Starter plan (1GB RAM)"),
            ("--port $PORT", "Port configuration"),
            ("--host 0.0.0.0", "Host binding")
        ]
        
        all_passed = True
        for check_string, description in checks:
            if check_string in content:
                print(f"  ✅ {description} configured")
            else:
                print(f"  ❌ {description} missing or misconfigured")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"  ❌ Render configuration test failed: {e}")
        return False

def test_requirements():
    """Test that requirements.txt includes necessary dependencies."""
    print("📦 Testing requirements configuration...")
    
    try:
        requirements_file = Path("/home/runner/work/DocQuery/DocQuery/requirements.txt")
        if not requirements_file.exists():
            print("  ❌ requirements.txt file not found")
            return False
        
        with open(requirements_file, 'r') as f:
            content = f.read()
        
        # Check for required packages
        required_packages = [
            "streamlit",
            "fastapi",
            "uvicorn",
            "psutil"
        ]
        
        all_found = True
        for package in required_packages:
            if package in content.lower():
                print(f"  ✅ {package} dependency found")
            else:
                print(f"  ❌ {package} dependency missing")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"  ❌ Requirements test failed: {e}")
        return False

def test_renderignore():
    """Test that .renderignore is properly configured."""
    print("🚫 Testing .renderignore configuration...")
    
    try:
        renderignore_file = Path("/home/runner/work/DocQuery/DocQuery/.renderignore")
        if not renderignore_file.exists():
            print("  ❌ .renderignore file not found")
            return False
        
        with open(renderignore_file, 'r') as f:
            content = f.read()
        
        # Check for important exclusions
        important_exclusions = [
            "*.bin",
            "*.pkl", 
            "*.model",
            "__pycache__/",
            ".cache/",
            "models/"
        ]
        
        all_found = True
        for exclusion in important_exclusions:
            if exclusion in content:
                print(f"  ✅ {exclusion} exclusion found")
            else:
                print(f"  ❌ {exclusion} exclusion missing")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"  ❌ .renderignore test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🔍 DocQuery Render Deployment Configuration Tests")
    print("=" * 50)
    
    tests = [
        ("Port Configuration", test_port_configuration),
        ("Health Endpoint", test_health_endpoint),
        ("Render Configuration", test_render_configuration),
        ("Requirements", test_requirements),
        (".renderignore", test_renderignore),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        if result:
            print(f"✅ {test_name}: PASSED")
            passed += 1
        else:
            print(f"❌ {test_name}: FAILED")
            failed += 1
    
    print(f"\nTotal: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Configuration is ready for Render deployment.")
        return True
    else:
        print("⚠️ Some tests failed. Please review the configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)