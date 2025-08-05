#!/usr/bin/env python3
"""
Test script to verify that the Vercel deployment size issue is resolved.
This test validates that all essential files are present and the total size is under limits.
"""

import os
import sys
from pathlib import Path

def test_deployment_size():
    """Test that deployment files are under the 250MB Vercel limit."""
    
    print("=== Vercel Deployment Size Test ===\n")
    
    # Define files that would be deployed (not in .vercelignore)
    excluded_patterns = [
        '*.pdf', '*.md', 'test_*.py', '*_test.py', 'sample_*.txt',
        'style.css', 'start.sh', 'setup.py', 'requirements-*.txt',
        'pyproject.toml', 'uv.lock', '__pycache__', '.git'
    ]
    
    total_size = 0
    deployment_files = []
    
    # Calculate size of files that would be deployed
    for root, dirs, files in os.walk('.'):
        # Skip .git directory
        if '.git' in root:
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            
            # Check if file should be excluded
            should_exclude = False
            for pattern in excluded_patterns:
                if pattern.startswith('*') and file.endswith(pattern[1:]):
                    should_exclude = True
                    break
                elif pattern.endswith('*') and file.startswith(pattern[:-1]):
                    should_exclude = True
                    break
                elif pattern in file_path:
                    should_exclude = True
                    break
            
            if not should_exclude:
                try:
                    size = os.path.getsize(file_path)
                    total_size += size
                    deployment_files.append((file_path, size))
                except OSError:
                    continue
    
    # Sort files by size (largest first)
    deployment_files.sort(key=lambda x: x[1], reverse=True)
    
    print("Files that would be deployed:")
    for file_path, size in deployment_files:
        print(f"  {file_path:<50} {size:>8} bytes ({size/1024:.1f} KB)")
    
    print(f"\nTotal deployment size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
    print(f"Vercel limit: 262,144,000 bytes (250 MB)")
    print(f"Percentage of limit used: {(total_size/262144000)*100:.3f}%")
    
    # Test passes if under 250MB
    if total_size < 262144000:  # 250MB in bytes
        print(f"\n✅ PASS: Deployment size ({total_size/1024:.1f} KB) is well under the 250MB limit!")
        return True
    else:
        print(f"\n❌ FAIL: Deployment size ({total_size/1024:.1f} KB) exceeds the 250MB limit!")
        return False

def test_core_imports():
    """Test that core application components can be imported."""
    
    print("\n=== Core Import Test ===\n")
    
    # Test essential modules (no external dependencies)
    essential_modules = [
        'app',
        'document_processor',
        'query_parser', 
        'openai_client',
        'local_ai_client',
        'database_manager',
        'enhanced_vector_search',
        'simple_vector_search',
        'output_formatter',
        'error_handler',
        'dependency_checker'
    ]
    
    # Test optional modules (may have external dependencies)
    optional_modules = [
        'vector_search',  # Requires faiss which may not be available
    ]
    
    success_count = 0
    
    print("Testing essential modules:")
    for module_name in essential_modules:
        try:
            __import__(module_name)
            print(f"✅ {module_name:<25} imported successfully")
            success_count += 1
        except ImportError as e:
            print(f"❌ {module_name:<25} import failed: {e}")
    
    print(f"\nTesting optional modules (fallbacks available):")
    for module_name in optional_modules:
        try:
            __import__(module_name)
            print(f"✅ {module_name:<25} imported successfully")
        except ImportError as e:
            print(f"⚠️  {module_name:<25} import failed (expected): {e}")
    
    print(f"\nEssential import test results: {success_count}/{len(essential_modules)} modules imported successfully")
    
    if success_count == len(essential_modules):
        print("✅ PASS: All essential modules import successfully!")
        return True
    else:
        print("❌ FAIL: Some essential modules failed to import!")
        return False

def test_vercel_config():
    """Test that Vercel configuration is valid."""
    
    print("\n=== Vercel Configuration Test ===\n")
    
    required_files = [
        'vercel.json',
        'requirements.txt',
        '.vercelignore',
        'app.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            print(f"✅ {file:<20} exists")
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    # Check vercel.json is valid JSON
    try:
        import json
        with open('vercel.json', 'r') as f:
            config = json.load(f)
        print("✅ vercel.json is valid JSON")
        
        # Check for required build configuration
        if 'builds' in config:
            print("✅ vercel.json contains builds configuration")
        else:
            print("❌ vercel.json missing builds configuration")
            return False
            
    except json.JSONDecodeError as e:
        print(f"❌ vercel.json is invalid JSON: {e}")
        return False
    
    print("✅ PASS: Vercel configuration is valid!")
    return True

def main():
    """Run all deployment tests."""
    
    print("Testing DocQuery deployment readiness...\n")
    
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    tests = [
        ("Deployment Size", test_deployment_size),
        ("Core Imports", test_core_imports), 
        ("Vercel Config", test_vercel_config)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
    
    print(f"\n{'='*50}")
    print(f"DEPLOYMENT TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Repository is ready for Vercel deployment.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please fix issues before deploying.")
        sys.exit(1)

if __name__ == "__main__":
    main()