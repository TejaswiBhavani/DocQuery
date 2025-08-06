#!/usr/bin/env python3
"""
Vercel Deployment Troubleshooting Script for DocQuery
Based on the comprehensive troubleshooting guide from the problem statement.
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path

def clear_vercel_cache():
    """Clear Vercel cached configuration as per troubleshooting guide."""
    print("🧹 Clearing Vercel cache...")
    
    cache_dirs = ['.vercel', 'node_modules']
    cleared = []
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                shutil.rmtree(cache_dir)
                cleared.append(cache_dir)
                print(f"   ✅ Removed {cache_dir}")
            except Exception as e:
                print(f"   ❌ Failed to remove {cache_dir}: {e}")
    
    if cleared:
        print(f"   🎉 Cleared cache directories: {cleared}")
    else:
        print("   ℹ️  No cache directories found to clear")
    
    return True

def check_legacy_files():
    """Check for and remove conflicting legacy files."""
    print("🔍 Checking for legacy configuration files...")
    
    legacy_files = ['now.json', '.nowignore']
    legacy_dirs = ['.now']
    
    removed = []
    
    # Check files
    for file in legacy_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                removed.append(file)
                print(f"   ✅ Removed legacy file: {file}")
            except Exception as e:
                print(f"   ❌ Failed to remove {file}: {e}")
    
    # Check directories
    for dir_name in legacy_dirs:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                removed.append(dir_name)
                print(f"   ✅ Removed legacy directory: {dir_name}")
            except Exception as e:
                print(f"   ❌ Failed to remove {dir_name}: {e}")
    
    if not removed:
        print("   ✅ No legacy files found")
    
    return True

def validate_vercel_json():
    """Validate vercel.json for common syntax errors."""
    print("🔧 Validating vercel.json configuration...")
    
    if not os.path.exists('vercel.json'):
        print("   ❌ vercel.json not found")
        return False
    
    try:
        with open('vercel.json', 'r') as f:
            config = json.load(f)
        
        # Check for common issues mentioned in problem statement
        issues = []
        
        # Check routes configuration
        if 'routes' in config:
            for i, route in enumerate(config['routes']):
                src = route.get('src', '')
                dest = route.get('dest', '')
                
                # Check for negative lookahead issues
                if '(?!' in src and not '((?!' in src:
                    issues.append(f"Route {i}: Potential negative lookahead issue in '{src}'")
                
                # Check parameter matching
                if ':' in src and ':' in dest:
                    src_params = set([p.split(')')[0] for p in src.split(':')[1:] if p])
                    dest_params = set([p.split('/')[0].split('?')[0] for p in dest.split(':')[1:] if p])
                    if src_params != dest_params:
                        issues.append(f"Route {i}: Parameter mismatch between source and destination")
        
        # Check for functions configuration issues (Next.js specific warning)
        if 'functions' in config:
            for func_name, func_config in config['functions'].items():
                allowed_keys = ['memory', 'maxDuration']
                for key in func_config.keys():
                    if key not in allowed_keys:
                        issues.append(f"Function {func_name}: Non-standard configuration key '{key}' (only memory/maxDuration recommended)")
        
        if issues:
            print("   ⚠️  Found potential issues:")
            for issue in issues:
                print(f"      - {issue}")
            return False
        else:
            print("   ✅ vercel.json validation passed")
            return True
    
    except json.JSONDecodeError as e:
        print(f"   ❌ JSON syntax error in vercel.json: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error reading vercel.json: {e}")
        return False

def check_build_output():
    """Verify build generates correct output directory."""
    print("🏗️  Checking build output...")
    
    # Check if package.json has build script
    if not os.path.exists('package.json'):
        print("   ❌ package.json not found")
        return False
    
    try:
        with open('package.json', 'r') as f:
            pkg = json.load(f)
        
        if 'scripts' not in pkg or 'build' not in pkg['scripts']:
            print("   ❌ No build script found in package.json")
            return False
        
        build_script = pkg['scripts']['build']
        print(f"   📝 Build script: {build_script}")
        
        # Run build to verify it works
        print("   🔨 Running build process...")
        result = subprocess.run(['npm', 'run', 'build'], 
                              capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            print(f"   ❌ Build failed: {result.stderr}")
            return False
        
        # Check if public directory was created
        if not os.path.exists('public'):
            print("   ❌ Build didn't generate public directory")
            return False
        
        # Check if public directory has content
        public_files = list(Path('public').rglob('*'))
        if len(public_files) < 3:  # Should have at least index.html, robots.txt, etc.
            print("   ❌ Public directory appears empty or incomplete")
            return False
        
        print(f"   ✅ Build successful, generated {len(public_files)} files")
        return True
        
    except subprocess.TimeoutExpired:
        print("   ❌ Build process timed out")
        return False
    except Exception as e:
        print(f"   ❌ Build check failed: {e}")
        return False

def check_environment_variables():
    """Check for conflicting environment variables."""
    print("🌍 Checking environment variables...")
    
    # Check for conflicting NOW_/VERCEL_ variables
    conflicting_vars = []
    env_vars = dict(os.environ)
    
    for var_name in env_vars:
        if var_name.startswith('NOW_') and not var_name.startswith('VERCEL_'):
            conflicting_vars.append(var_name)
    
    if conflicting_vars:
        print("   ⚠️  Found legacy NOW_ environment variables:")
        for var in conflicting_vars:
            print(f"      - {var}")
        print("   💡 Consider removing these in favor of VERCEL_ equivalents")
    else:
        print("   ✅ No conflicting environment variables found")
    
    return True

def run_deployment_fixes():
    """Run all the common fixes from the troubleshooting guide."""
    print("🚀 DocQuery Vercel Deployment Troubleshooting")
    print("=" * 60)
    print()
    
    fixes = [
        ("Clear Vercel Cache", clear_vercel_cache),
        ("Remove Legacy Files", check_legacy_files),
        ("Validate Configuration", validate_vercel_json),
        ("Check Build Output", check_build_output),
        ("Check Environment", check_environment_variables)
    ]
    
    passed = 0
    total = len(fixes)
    
    for name, fix_func in fixes:
        print(f"{name}:")
        try:
            if fix_func():
                passed += 1
            else:
                print(f"   ⚠️  {name} needs attention")
        except Exception as e:
            print(f"   ❌ {name} failed: {e}")
        print()
    
    print("=" * 60)
    print(f"📊 Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All deployment fixes applied successfully!")
        print("✅ Ready for Vercel deployment")
        
        print("\n🚀 Next steps:")
        print("1. Run: vercel --link (if project not linked)")
        print("2. Run: vercel deploy")
        print("3. Check deployment at: https://your-project.vercel.app")
        
        return 0
    else:
        print("❌ Some issues remain - check the output above")
        
        print("\n🔧 Additional troubleshooting steps:")
        print("1. Check Vercel status: https://status.vercel.com")
        print("2. Try: vercel --debug for detailed output")
        print("3. Contact Vercel support if issues persist")
        
        return 1

def main():
    """Main function to run deployment fixes."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("DocQuery Vercel Deployment Troubleshooting Tool")
        print()
        print("This script implements the fixes from the troubleshooting guide:")
        print("- Clears Vercel cache")
        print("- Removes legacy configuration files")
        print("- Validates vercel.json for common issues")
        print("- Verifies build output")
        print("- Checks environment variables")
        print()
        print("Usage: python deployment_fixes.py")
        return 0
    
    return run_deployment_fixes()

if __name__ == "__main__":
    sys.exit(main())