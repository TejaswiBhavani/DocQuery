#!/usr/bin/env python3
"""
Simple validation script for Render deployment configuration.
This script checks configuration without requiring external dependencies.
"""

import os
import sys
import yaml
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists and return status."""
    path = Path(file_path)
    if path.exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (missing)")
        return False

def check_port_config():
    """Test port configuration logic."""
    print("\n🔧 Testing port configuration logic...")
    
    def test_port_parsing(port_env, expected):
        """Test port parsing with different values."""
        if port_env is not None:
            os.environ["PORT"] = port_env
        elif "PORT" in os.environ:
            del os.environ["PORT"]
        
        # Simulate the port parsing logic from app.py
        port_env_val = os.getenv('PORT', '8501')
        try:
            port = int(port_env_val)
            if not (1024 <= port <= 65535):
                port = 8501
        except (ValueError, TypeError):
            port = 8501
        
        success = port == expected
        status = "✅" if success else "❌"
        print(f"  {status} PORT='{port_env}' -> {port} (expected {expected})")
        return success
    
    # Test cases
    test_cases = [
        ("8501", 8501),
        ("10000", 10000), 
        ("3000", 3000),
        ("invalid", 8501),
        ("", 8501),
        (None, 8501),
        ("99999", 8501),  # Out of range
    ]
    
    all_passed = True
    for port_env, expected in test_cases:
        if not test_port_parsing(port_env, expected):
            all_passed = False
    
    return all_passed

def check_yaml_config():
    """Check render.yaml configuration."""
    print("\n🚀 Checking render.yaml configuration...")
    
    try:
        with open("render.yaml", 'r') as f:
            config = yaml.safe_load(f)
        
        services = config.get('services', [])
        if not services:
            print("❌ No services defined in render.yaml")
            return False
        
        service = services[0]  # Check first service
        
        checks = [
            ('name', 'Service name defined'),
            ('plan', 'Instance plan specified'),
            ('buildCommand', 'Build command specified'),
            ('startCommand', 'Start command specified'),
            ('healthCheckPath', 'Health check path defined'),
        ]
        
        all_passed = True
        for key, description in checks:
            if key in service:
                print(f"  ✅ {description}: {service[key]}")
            else:
                print(f"  ❌ {description}: missing")
                all_passed = False
        
        # Check specific values
        if service.get('plan') == 'starter':
            print("  ✅ Using Starter plan (1GB RAM)")
        elif service.get('plan') == 'free':
            print("  ⚠️ Using Free plan (512MB RAM) - consider upgrading for AI models")
        else:
            print(f"  ⚠️ Using {service.get('plan', 'unknown')} plan")
        
        start_cmd = service.get('startCommand', '')
        if 'uvicorn healthz:app' in start_cmd and 'streamlit run app.py' in start_cmd:
            print("  ✅ Start command includes both health endpoint and Streamlit")
        else:
            print("  ❌ Start command missing health endpoint or Streamlit")
            all_passed = False
        
        if service.get('healthCheckPath') == '/healthz':
            print("  ✅ Health check path correctly set to /healthz")
        else:
            print("  ❌ Health check path not set or incorrect")
            all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error reading render.yaml: {e}")
        return False

def check_requirements():
    """Check requirements.txt for necessary dependencies."""
    print("\n📦 Checking requirements.txt...")
    
    try:
        with open("requirements.txt", 'r') as f:
            content = f.read().lower()
        
        required_deps = [
            'streamlit',
            'fastapi', 
            'uvicorn',
            'psutil'
        ]
        
        all_found = True
        for dep in required_deps:
            if dep in content:
                print(f"  ✅ {dep} dependency found")
            else:
                print(f"  ❌ {dep} dependency missing")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False

def check_ignore_files():
    """Check .renderignore configuration."""
    print("\n🚫 Checking .renderignore configuration...")
    
    try:
        with open(".renderignore", 'r') as f:
            content = f.read()
        
        important_exclusions = [
            '*.bin',
            '*.pkl',
            'models/',
            '__pycache__/',
            '.cache/'
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
        print(f"❌ Error reading .renderignore: {e}")
        return False

def main():
    """Run all validation checks."""
    print("🔍 DocQuery Render Deployment Validation")
    print("=" * 50)
    
    # File existence checks
    print("📁 Checking required files...")
    files_ok = all([
        check_file_exists("app.py", "Main application"),
        check_file_exists("healthz.py", "Health check endpoint"),
        check_file_exists("render.yaml", "Render configuration"),
        check_file_exists("requirements.txt", "Python dependencies"),
        check_file_exists(".renderignore", "Deployment exclusions"),
    ])
    
    if not files_ok:
        print("\n❌ Some required files are missing!")
        return False
    
    # Configuration checks
    checks = [
        ("Port Configuration", check_port_config),
        ("YAML Configuration", check_yaml_config), 
        ("Requirements", check_requirements),
        ("Ignore Files", check_ignore_files),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"\n❌ {check_name} check failed: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Validation Summary:")
    
    passed = 0
    failed = 0
    
    for check_name, result in results:
        if result:
            print(f"✅ {check_name}: PASSED") 
            passed += 1
        else:
            print(f"❌ {check_name}: FAILED")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All validation checks passed!")
        print("📋 Your configuration is ready for Render deployment.")
        print("\n🚀 Next steps:")
        print("1. Push changes to your repository")
        print("2. Go to Render Dashboard → Settings")  
        print("3. Upgrade to Starter plan (1GB RAM)")
        print("4. Deploy your service")
        print("5. Monitor logs for successful startup")
        return True
    else:
        print(f"\n⚠️ {failed} validation check(s) failed.")
        print("Please fix the issues before deploying.")
        return False

if __name__ == "__main__":
    # Change to the repository directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    success = main()
    sys.exit(0 if success else 1)