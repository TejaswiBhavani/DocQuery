#!/usr/bin/env python3
"""
Deployment verification script for DocQuery Vercel deployment
"""
import os
import json

def check_api_structure():
    """Check that API endpoints exist and have required structure"""
    print("🔍 Checking API structure...")
    
    required_files = ['api/upload.py', 'api/search.py', 'api/analyze.py']
    missing_files = []
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            # Check that handler class exists
            with open(file_path, 'r') as f:
                content = f.read()
                if 'class handler' not in content:
                    print(f"❌ {file_path} missing handler class")
                    return False
                else:
                    print(f"✅ {file_path} - handler class found")
    
    if missing_files:
        print(f"❌ Missing API files: {missing_files}")
        return False
    
    return True

def check_backend_modules():
    """Check that backend modules are properly structured"""
    print("\n🔍 Checking backend modules...")
    
    required_modules = [
        'backend/document_processor.py',
        'backend/query_parser.py',
        'backend/local_ai_client.py',
        'backend/openai_client.py'
    ]
    
    for module_path in required_modules:
        if not os.path.exists(module_path):
            print(f"❌ Missing: {module_path}")
            return False
        else:
            print(f"✅ Found: {module_path}")
    
    return True

def check_frontend_structure():
    """Check that Next.js frontend is properly structured"""
    print("\n🔍 Checking frontend structure...")
    
    required_frontend_files = [
        'frontend/package.json',
        'frontend/pages/index.js',
        'frontend/pages/_app.js',
        'frontend/components/DocumentUpload.js',
        'frontend/components/QueryInterface.js',
        'frontend/styles/globals.css'
    ]
    
    for file_path in required_frontend_files:
        if not os.path.exists(file_path):
            print(f"❌ Missing: {file_path}")
            return False
        else:
            print(f"✅ Found: {file_path}")
    
    return True

def check_vercel_config():
    """Check Vercel configuration"""
    print("\n🔍 Checking Vercel configuration...")
    
    if not os.path.exists('vercel.json'):
        print("❌ Missing vercel.json")
        return False
    
    try:
        with open('vercel.json', 'r') as f:
            config = json.load(f)
        
        # Check required sections
        required_sections = ['builds', 'routes', 'functions']
        for section in required_sections:
            if section not in config:
                print(f"❌ Missing section in vercel.json: {section}")
                return False
        
        # Check for Python and Next.js builds
        builds = config.get('builds', [])
        has_next_build = any('next' in str(build.get('use', '')) for build in builds)
        has_python_build = any('python' in str(build.get('use', '')) for build in builds)
        
        if not has_next_build:
            print("❌ Missing Next.js build configuration")
            return False
        
        if not has_python_build:
            print("❌ Missing Python build configuration")
            return False
        
        print("✅ vercel.json properly configured")
        return True
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON in vercel.json")
        return False

def check_dependencies():
    """Check that dependencies are properly configured"""
    print("\n🔍 Checking dependencies...")
    
    # Check Python requirements
    if not os.path.exists('requirements.txt'):
        print("❌ Missing requirements.txt")
        return False
    
    with open('requirements.txt', 'r') as f:
        requirements = f.read()
    
    # Should NOT contain streamlit
    if 'streamlit' in requirements.lower():
        print("❌ requirements.txt still contains streamlit")
        return False
    
    # Should contain FastAPI
    if 'fastapi' not in requirements.lower():
        print("❌ requirements.txt missing fastapi")
        return False
    
    print("✅ requirements.txt properly configured")
    
    # Check frontend package.json
    if not os.path.exists('frontend/package.json'):
        print("❌ Missing frontend/package.json")
        return False
    
    try:
        with open('frontend/package.json', 'r') as f:
            package = json.load(f)
        
        # Check for Next.js
        if 'next' not in package.get('dependencies', {}):
            print("❌ Next.js not in frontend dependencies")
            return False
        
        print("✅ frontend/package.json properly configured")
        return True
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON in frontend/package.json")
        return False

def main():
    print("🚀 DocQuery Vercel Deployment Verification")
    print("=" * 50)
    
    checks = [
        check_api_structure,
        check_backend_modules,
        check_frontend_structure,
        check_vercel_config,
        check_dependencies
    ]
    
    results = []
    for check in checks:
        results.append(check())
    
    print("\n" + "=" * 50)
    print(f"📊 Verification Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("\n🎉 SUCCESS! DocQuery is ready for Vercel deployment!")
        print("\nNext steps:")
        print("1. Push to GitHub: git push origin main")
        print("2. Connect repository to Vercel")
        print("3. Configure environment variables in Vercel Dashboard")
        print("4. Deploy with: vercel --prod")
        return True
    else:
        print("\n⚠️ Some verification checks failed.")
        print("Please fix the issues above before deploying.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)