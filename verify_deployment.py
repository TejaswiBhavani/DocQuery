#!/usr/bin/env python3
"""
Deployment verification script for DocQuery Vercel deployment.
Checks that all requirements from the problem statement are satisfied.
"""

import os
import sys
import json
from pathlib import Path

def check_package_json():
    """Check if package.json exists with proper build script."""
    print("🔍 Checking package.json...")
    
    if not os.path.exists("package.json"):
        print("❌ package.json is missing")
        return False
    
    try:
        with open("package.json", "r") as f:
            pkg = json.load(f)
        
        if "scripts" not in pkg:
            print("❌ No scripts section in package.json")
            return False
        
        if "build" not in pkg["scripts"]:
            print("❌ No build script in package.json")
            return False
        
        build_script = pkg["scripts"]["build"]
        if "public" not in build_script:
            print("❌ Build script doesn't output to public directory")
            return False
        
        print("✅ package.json has proper build script")
        return True
        
    except Exception as e:
        print(f"❌ Error reading package.json: {e}")
        return False

def check_public_directory():
    """Check if public directory exists with required files."""
    print("🔍 Checking public directory...")
    
    if not os.path.exists("public"):
        print("❌ public directory is missing")
        return False
    
    required_files = ["index.html", "404.html", "robots.txt", "sitemap.xml"]
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(f"public/{file}"):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files in public directory: {missing_files}")
        return False
    
    # Check if index.html has content
    try:
        with open("public/index.html", "r") as f:
            content = f.read()
        
        if len(content) < 1000:  # Should be a substantial HTML file
            print("❌ index.html appears to be too short")
            return False
        
        if "DocQuery" not in content:
            print("❌ index.html doesn't contain DocQuery branding")
            return False
        
        print("✅ public directory exists with all required files")
        return True
        
    except Exception as e:
        print(f"❌ Error reading index.html: {e}")
        return False

def check_vercel_json():
    """Check if vercel.json is properly configured."""
    print("🔍 Checking vercel.json...")
    
    if not os.path.exists("vercel.json"):
        print("❌ vercel.json is missing")
        return False
    
    try:
        with open("vercel.json", "r") as f:
            config = json.load(f)
        
        # Check for proper builds configuration
        if "builds" not in config:
            print("❌ No builds configuration in vercel.json")
            return False
        
        # Check for static build
        has_static_build = False
        has_python_build = False
        
        for build in config["builds"]:
            if build.get("use") == "@vercel/static":
                has_static_build = True
            if build.get("use") == "@vercel/python":
                has_python_build = True
        
        if not has_static_build:
            print("❌ No @vercel/static build found in vercel.json")
            return False
        
        if not has_python_build:
            print("❌ No @vercel/python build found in vercel.json")
            return False
        
        # Check for proper routes
        if "routes" not in config:
            print("❌ No routes configuration in vercel.json")
            return False
        
        # Check if buildCommand is specified
        if "buildCommand" not in config:
            print("❌ No buildCommand specified in vercel.json")
            return False
        
        build_command = config["buildCommand"]
        if "public" not in build_command:
            print("❌ Build command doesn't reference public directory")
            return False
        
        print("✅ vercel.json is properly configured")
        return True
        
    except Exception as e:
        print(f"❌ Error reading vercel.json: {e}")
        return False

def check_build_script():
    """Check if build script exists and works."""
    print("🔍 Checking build script...")
    
    if not os.path.exists("build.py"):
        print("❌ build.py script is missing")
        return False
    
    # Try to import the build script
    try:
        import build
        print("✅ build.py script imports successfully")
        return True
    except Exception as e:
        print(f"❌ Error importing build.py: {e}")
        return False

def check_api_functionality():
    """Check if API can be imported and is functional."""
    print("🔍 Checking API functionality...")
    
    if not os.path.exists("api.py"):
        print("❌ api.py is missing")
        return False
    
    try:
        from api import app
        print("✅ API imports successfully")
        return True
    except Exception as e:
        print(f"❌ Error importing API: {e}")
        return False

def check_dependencies():
    """Check if all required dependencies are available."""
    print("🔍 Checking dependencies...")
    
    # Map package names to their import names
    package_imports = {
        "fastapi": "fastapi",
        "uvicorn": "uvicorn", 
        "PyPDF2": "PyPDF2",
        "numpy": "numpy",
        "scikit-learn": "sklearn",
        "httpx": "httpx",
        "openai": "openai"
    }
    
    missing_packages = []
    
    for package_name, import_name in package_imports.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"❌ Missing packages: {missing_packages}")
        return False
    
    print("✅ All required dependencies are available")
    return True

def main():
    """Run all verification checks."""
    print("🚀 DocQuery Deployment Verification")
    print("="*50)
    
    checks = [
        ("Package.json Configuration", check_package_json),
        ("Public Directory", check_public_directory), 
        ("Vercel Configuration", check_vercel_json),
        ("Build Script", check_build_script),
        ("API Functionality", check_api_functionality),
        ("Dependencies", check_dependencies)
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        print(f"\n{name}:")
        if check_func():
            passed += 1
        else:
            print(f"Failed check: {name}")
    
    print(f"\n{'='*50}")
    print(f"📊 Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All deployment requirements satisfied!")
        print("✅ Ready for successful Vercel deployment")
        return 0
    else:
        print("❌ Some deployment requirements not met")
        print(f"Please fix the {total - passed} failed check(s) above")
        return 1

if __name__ == "__main__":
    sys.exit(main())