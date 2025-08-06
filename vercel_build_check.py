#!/usr/bin/env python3
"""
Vercel Build Check Script
Validates that the project is ready for Vercel deployment
"""

import os
import sys
import json
from pathlib import Path

def check_public_directory():
    """Check if public directory exists and has required files"""
    public_dir = Path("public")
    if not public_dir.exists():
        print("❌ Public directory does not exist")
        return False
    
    required_files = ["index.html", "favicon.ico", "robots.txt", "sitemap.xml", "manifest.json"]
    missing_files = []
    
    for file in required_files:
        if not (public_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files in public directory: {missing_files}")
        return False
    
    print("✅ Public directory is properly configured")
    return True

def check_vercel_config():
    """Check vercel.json configuration"""
    vercel_config = Path("vercel.json")
    if not vercel_config.exists():
        print("❌ vercel.json does not exist")
        return False
    
    try:
        with open(vercel_config) as f:
            config = json.load(f)
        
        # Check for modern configuration
        if "builds" in config and "functions" in config:
            print("❌ vercel.json has conflicting builds and functions configuration")
            return False
        
        if "routes" in config and any(key in config for key in ["rewrites", "redirects", "headers"]):
            print("❌ vercel.json has conflicting routes and modern properties")
            return False
        
        print("✅ vercel.json configuration is valid")
        return True
        
    except json.JSONDecodeError:
        print("❌ vercel.json is not valid JSON")
        return False

def check_package_json():
    """Check package.json configuration"""
    package_json = Path("package.json")
    if not package_json.exists():
        print("❌ package.json does not exist")
        return False
    
    try:
        with open(package_json) as f:
            config = json.load(f)
        
        if "scripts" not in config or "build" not in config["scripts"]:
            print("❌ package.json missing build script")
            return False
        
        build_script = config["scripts"]["build"]
        if "--output public" not in build_script and "public" not in build_script:
            print("❌ Build script does not output to public directory")
            return False
        
        print("✅ package.json is properly configured")
        return True
        
    except json.JSONDecodeError:
        print("❌ package.json is not valid JSON")
        return False

def check_api_file():
    """Check if API file is properly configured for Vercel"""
    api_file = Path("api.py")
    if not api_file.exists():
        print("❌ api.py does not exist")
        return False
    
    try:
        with open(api_file) as f:
            content = f.read()
        
        if "handler = app" not in content and "app = " not in content:
            print("❌ api.py missing proper Vercel handler export")
            return False
        
        print("✅ api.py is properly configured")
        return True
        
    except Exception:
        print("❌ Error reading api.py")
        return False

def check_requirements():
    """Check requirements.txt exists"""
    requirements = Path("requirements.txt")
    if not requirements.exists():
        print("❌ requirements.txt does not exist")
        return False
    
    print("✅ requirements.txt exists")
    return True

def main():
    """Run all checks"""
    print("🔍 Running Vercel deployment readiness check...")
    print()
    
    checks = [
        check_public_directory,
        check_vercel_config,
        check_package_json,
        check_api_file,
        check_requirements
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
        print()
    
    if all_passed:
        print("🎉 All checks passed! Project is ready for Vercel deployment.")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())