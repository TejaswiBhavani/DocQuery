#!/usr/bin/env python3
"""
Pre-deployment validation script for DocQuery
Run this before deploying to Render to validate the setup
"""

import os
import sys
import subprocess
import importlib

def run_command(cmd, timeout=60):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"

def check_file_exists(filepath):
    """Check if a file exists"""
    exists = os.path.exists(filepath)
    print(f"{'✅' if exists else '❌'} {filepath}")
    return exists

def validate_deployment():
    """Validate deployment configuration"""
    
    print("🚀 DocQuery Render Deployment Validation")
    print("="*50)
    
    # Check required files
    print("\n📁 Checking required files...")
    files_ok = True
    required_files = [
        "app.py",
        "requirements.txt", 
        "runtime.txt",
        "render.yaml",
        "Procfile",
        "start.sh",
        "build.sh",
        ".streamlit/config.toml"
    ]
    
    for file in required_files:
        if not check_file_exists(file):
            files_ok = False
    
    # Check Python version
    print(f"\n🐍 Python version: {sys.version}")
    
    # Check runtime.txt content
    try:
        with open("runtime.txt", "r") as f:
            runtime_version = f.read().strip()
            print(f"✅ runtime.txt specifies: {runtime_version}")
    except FileNotFoundError:
        print("❌ runtime.txt not found")
        files_ok = False
    
    # Test build script
    print("\n🔨 Testing build script...")
    build_ok, build_out, build_err = run_command("./build.sh", timeout=180)
    if build_ok:
        print("✅ Build script executed successfully")
    else:
        print("❌ Build script failed")
        print(f"Error: {build_err}")
        return False
    
    # Test health check
    print("\n🔍 Running health check...")
    health_ok, health_out, health_err = run_command("python health_check.py")
    if health_ok:
        print("✅ Health check passed")
    else:
        print("❌ Health check failed")
        print(f"Error: {health_err}")
        return False
    
    # Test app import
    print("\n📱 Testing app import...")
    try:
        import app
        print("✅ App imports successfully")
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False
    
    # Validate configuration files
    print("\n⚙️ Validating configuration...")
    
    # Check render.yaml
    try:
        import yaml
        with open("render.yaml", "r") as f:
            render_config = yaml.safe_load(f)
            if render_config and "services" in render_config:
                print("✅ render.yaml is valid")
            else:
                print("❌ render.yaml format issues")
                return False
    except Exception as e:
        print(f"⚠️ Could not validate render.yaml: {e}")
    
    print("\n" + "="*50)
    if files_ok:
        print("🎉 Validation passed! Your app is ready for Render deployment.")
        print("\nNext steps:")
        print("1. Push your code to GitHub")
        print("2. Connect your GitHub repo to Render")
        print("3. Render will automatically use render.yaml for deployment")
        return True
    else:
        print("❌ Validation failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = validate_deployment()
    sys.exit(0 if success else 1)