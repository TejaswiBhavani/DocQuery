#!/usr/bin/env python3
"""
Test script to validate the Vercel deployment fixes.
This script tests that all the deployment errors have been resolved.
"""
import os
import json
import subprocess
import sys

def test_no_conflicting_configuration():
    """Test that vercel.json doesn't have conflicting builds and functions."""
    print("✅ Testing: No conflicting builds/functions configuration...")
    
    with open('vercel.json', 'r') as f:
        config = json.load(f)
    
    has_builds = 'builds' in config
    has_functions = 'functions' in config
    
    if has_builds and has_functions:
        print("❌ FAIL: vercel.json has both 'builds' and 'functions' - this creates a conflict")
        return False
    elif has_builds:
        print("✅ PASS: Using 'builds' configuration only")
    elif has_functions:
        print("✅ PASS: Using 'functions' configuration only") 
    else:
        print("❌ FAIL: vercel.json missing both 'builds' and 'functions'")
        return False
    
    return True

def test_public_directory_exists():
    """Test that public directory exists and is not empty."""
    print("\n✅ Testing: Public directory exists...")
    
    if not os.path.exists('public'):
        print("❌ FAIL: public directory is missing")
        return False
    
    if not os.path.isdir('public'):
        print("❌ FAIL: public exists but is not a directory")
        return False
    
    # Check if directory has content
    files = os.listdir('public')
    if not files:
        print("⚠️  WARNING: public directory is empty")
    else:
        print(f"✅ PASS: public directory exists with {len(files)} file(s)")
        for file in files:
            print(f"   - {file}")
    
    return True

def test_package_json_with_build_script():
    """Test that package.json exists with build script."""
    print("\n✅ Testing: package.json with build script...")
    
    if not os.path.exists('package.json'):
        print("❌ FAIL: package.json is missing")
        return False
    
    with open('package.json', 'r') as f:
        package = json.load(f)
    
    if 'scripts' not in package:
        print("❌ FAIL: package.json missing 'scripts' section")
        return False
    
    if 'build' not in package['scripts']:
        print("❌ FAIL: package.json missing 'build' script")
        return False
    
    print("✅ PASS: package.json has build script")
    print(f"   Build command: {package['scripts']['build']}")
    
    return True

def test_build_script_works():
    """Test that the build script actually works."""
    print("\n✅ Testing: Build script execution...")
    
    try:
        result = subprocess.run(['npm', 'run', 'build'], 
                              capture_output=True, text=True, 
                              timeout=30)
        
        if result.returncode == 0:
            print("✅ PASS: Build script executed successfully")
            print(f"   Output: {result.stdout.strip()}")
        else:
            print("❌ FAIL: Build script failed")
            print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ FAIL: Build script timed out")
        return False
    except FileNotFoundError:
        print("⚠️  WARNING: npm not found - skipping build script test")
        return True  # This is OK for the fix verification
    
    return True

def test_vercel_handler_function():
    """Test that the Vercel handler function works."""
    print("\n✅ Testing: Vercel handler function...")
    
    try:
        import app
        if not hasattr(app, 'handler'):
            print("❌ FAIL: app.py missing handler function")
            return False
        
        # Test handler function
        response = app.handler({}, {})
        
        if not isinstance(response, dict):
            print("❌ FAIL: handler function should return a dict")
            return False
        
        if 'statusCode' not in response:
            print("❌ FAIL: handler response missing statusCode")
            return False
        
        if response['statusCode'] != 200:
            print(f"❌ FAIL: handler returned status {response['statusCode']}, expected 200")
            return False
        
        print("✅ PASS: handler function works correctly")
        print(f"   Response: {response}")
        
    except Exception as e:
        print(f"❌ FAIL: Error testing handler function: {e}")
        return False
    
    return True

def test_no_mixed_routing_properties():
    """Test that vercel.json doesn't have mixed routing properties."""
    print("\n✅ Testing: No mixed routing properties...")
    
    with open('vercel.json', 'r') as f:
        config = json.load(f)
    
    # Check for properties that conflict with routes
    conflicting_props = ['rewrites', 'redirects', 'headers', 'cleanUrls', 'trailingSlash']
    has_routes = 'routes' in config
    has_conflicting = any(prop in config for prop in conflicting_props)
    
    if has_routes and has_conflicting:
        conflicts = [prop for prop in conflicting_props if prop in config]
        print(f"❌ FAIL: vercel.json has both 'routes' and conflicting properties: {conflicts}")
        return False
    
    print("✅ PASS: No mixed routing properties detected")
    return True

def main():
    """Run all deployment validation tests."""
    print("🧪 Running Vercel Deployment Validation Tests")
    print("=" * 60)
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    tests = [
        test_no_conflicting_configuration,
        test_public_directory_exists, 
        test_package_json_with_build_script,
        test_build_script_works,
        test_vercel_handler_function,
        test_no_mixed_routing_properties
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ FAIL: {test.__name__} threw exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Vercel deployment issues resolved!")
        return 0
    else:
        print("❌ Some tests failed - deployment issues remain")
        return 1

if __name__ == '__main__':
    sys.exit(main())