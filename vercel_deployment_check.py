#!/usr/bin/env python3
"""
Vercel Deployment Verification Script
Checks all requirements for successful Vercel deployment of DocQuery.
"""

import os
import json
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists."""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - MISSING")
        return False

def check_package_json():
    """Check package.json structure."""
    print("\n📦 Checking package.json...")
    if not check_file_exists("package.json", "Package.json file"):
        return False
    
    try:
        with open("package.json", "r") as f:
            package = json.load(f)
        
        if "scripts" in package and "build" in package["scripts"]:
            print(f"✅ Build script found: {package['scripts']['build']}")
            return True
        else:
            print("❌ Build script missing in package.json")
            return False
    except Exception as e:
        print(f"❌ Error reading package.json: {e}")
        return False

def check_vercel_config():
    """Check vercel.json configuration."""
    print("\n⚙️  Checking vercel.json...")
    if not check_file_exists("vercel.json", "Vercel config file"):
        return False
    
    try:
        with open("vercel.json", "r") as f:
            config = json.load(f)
        
        # Check for required fields
        checks = [
            ("version", "Version specified"),
            ("functions", "Functions configuration"),
            ("buildCommand", "Build command specified"),
            ("outputDirectory", "Output directory specified")
        ]
        
        all_good = True
        for field, description in checks:
            if field in config:
                print(f"✅ {description}")
            else:
                print(f"⚠️  {description} - Optional but recommended")
        
        # Check for conflicting configuration
        if "builds" in config and "functions" in config:
            print("❌ Conflicting 'builds' and 'functions' configuration")
            all_good = False
        else:
            print("✅ No conflicting configuration detected")
        
        return all_good
    except Exception as e:
        print(f"❌ Error reading vercel.json: {e}")
        return False

def check_public_directory():
    """Check public directory structure."""
    print("\n📁 Checking public directory...")
    public_dir = Path("public")
    
    if not public_dir.exists():
        print("❌ Public directory missing")
        return False
    
    required_files = [
        "index.html",
        "robots.txt",
        "sitemap.xml",
        "manifest.json"
    ]
    
    all_good = True
    for file in required_files:
        filepath = public_dir / file
        if filepath.exists():
            print(f"✅ Required file: {file}")
        else:
            print(f"❌ Missing required file: {file}")
            all_good = False
    
    # Check file sizes
    index_path = public_dir / "index.html"
    if index_path.exists():
        size = index_path.stat().st_size
        if size > 1000:  # At least 1KB for a real homepage
            print(f"✅ Index.html has content ({size} bytes)")
        else:
            print(f"⚠️  Index.html seems small ({size} bytes)")
    
    return all_good

def check_api_file():
    """Check API file structure."""
    print("\n🔌 Checking API file...")
    if not check_file_exists("api.py", "API file"):
        return False
    
    try:
        with open("api.py", "r") as f:
            content = f.read()
        
        # Check for FastAPI app
        if "app = FastAPI(" in content:
            print("✅ FastAPI app found")
        else:
            print("❌ FastAPI app not found")
            return False
        
        # Check for proper export
        if "app = app" in content or "def handler" in content:
            print("✅ Vercel export structure found")
        else:
            print("⚠️  Vercel export structure may need verification")
        
        return True
    except Exception as e:
        print(f"❌ Error reading api.py: {e}")
        return False

def check_requirements():
    """Check requirements file."""
    print("\n📋 Checking requirements...")
    if not check_file_exists("requirements.txt", "Requirements file"):
        return False
    
    try:
        with open("requirements.txt", "r") as f:
            requirements = f.read()
        
        essential_packages = ["fastapi", "uvicorn", "PyPDF2"]
        all_good = True
        
        for package in essential_packages:
            if package.lower() in requirements.lower():
                print(f"✅ Essential package: {package}")
            else:
                print(f"❌ Missing essential package: {package}")
                all_good = False
        
        return all_good
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False

def check_vercelignore():
    """Check .vercelignore file."""
    print("\n🚫 Checking .vercelignore...")
    if check_file_exists(".vercelignore", "Vercel ignore file"):
        print("✅ .vercelignore helps reduce deployment size")
        return True
    else:
        print("⚠️  .vercelignore missing - may increase deployment size")
        return True  # Not critical

def main():
    """Run all checks."""
    print("🔍 DocQuery Vercel Deployment Verification")
    print("=" * 50)
    
    checks = [
        check_package_json,
        check_vercel_config,
        check_public_directory,
        check_api_file,
        check_requirements,
        check_vercelignore
    ]
    
    results = []
    for check in checks:
        results.append(check())
    
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 ALL CHECKS PASSED ({passed}/{total})")
        print("✅ Your project is ready for Vercel deployment!")
        print("\n🚀 Deploy with: vercel --prod")
        return 0
    else:
        print(f"⚠️  {passed}/{total} checks passed")
        print("❌ Please fix the issues above before deploying")
        return 1

if __name__ == "__main__":
    sys.exit(main())