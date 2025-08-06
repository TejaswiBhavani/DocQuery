#!/usr/bin/env python3
"""
Test script to validate Vercel deployment configuration
"""
import sys
import subprocess
import os
from pathlib import Path

def test_build_process():
    """Test the build process works correctly"""
    print("🔨 Testing build process...")
    
    # Run the build command
    result = subprocess.run([
        sys.executable, "build.py", "--output", "public"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ Build process failed!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False
    
    # Check that public directory was created with expected files
    public_dir = Path("public")
    if not public_dir.exists():
        print("❌ Public directory not created!")
        return False
    
    expected_files = ["index.html", "robots.txt", "sitemap.xml", "manifest.json", "style.css"]
    for file in expected_files:
        if not (public_dir / file).exists():
            print(f"❌ Expected file {file} not found in public directory!")
            return False
    
    print("✅ Build process successful!")
    return True

def test_api_import():
    """Test that the API can be imported successfully"""
    print("🔌 Testing API import...")
    
    try:
        # Test importing the API module
        from api import app
        print("✅ API imports successfully!")
        return True
    except Exception as e:
        print(f"❌ API import failed: {e}")
        return False

def test_vercel_config():
    """Test Vercel configuration files"""
    print("⚙️ Testing Vercel configuration...")
    
    # Check vercel.json exists and is valid JSON
    vercel_config = Path("vercel.json")
    if not vercel_config.exists():
        print("❌ vercel.json not found!")
        return False
    
    try:
        import json
        with open(vercel_config) as f:
            config = json.load(f)
        
        # Check essential keys
        if "builds" not in config:
            print("❌ No builds configuration found in vercel.json!")
            return False
        
        if "routes" not in config:
            print("❌ No routes configuration found in vercel.json!")
            return False
        
        print("✅ Vercel configuration is valid!")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in vercel.json: {e}")
        return False

def test_package_json():
    """Test package.json configuration"""
    print("📦 Testing package.json...")
    
    package_json = Path("package.json")
    if not package_json.exists():
        print("❌ package.json not found!")
        return False
    
    try:
        import json
        with open(package_json) as f:
            package = json.load(f)
        
        # Check for build script
        if "scripts" not in package or "vercel-build" not in package["scripts"]:
            print("❌ No vercel-build script found in package.json!")
            return False
        
        # Check that Node.js engines are not specified (this is a Python project)
        if "engines" in package and "node" in package["engines"]:
            print("❌ Node.js engines specified in package.json for Python project!")
            return False
        
        print("✅ package.json configuration is correct!")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in package.json: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running Vercel deployment validation tests...\n")
    
    tests = [
        test_package_json,
        test_vercel_config,
        test_build_process,
        test_api_import,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Add spacing between tests
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Vercel deployment should work correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())