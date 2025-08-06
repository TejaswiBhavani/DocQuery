#!/usr/bin/env python3
"""
Emergency Vercel Deployment Recovery Script
For when all else fails, this script helps migrate DocQuery to a fresh Vercel project.
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

def backup_current_config():
    """Create a backup of current configuration."""
    print("💾 Creating backup of current configuration...")
    
    backup_dir = Path("vercel_backup")
    backup_dir.mkdir(exist_ok=True)
    
    files_to_backup = [
        "vercel.json",
        "package.json", 
        "requirements-vercel.txt",
        ".vercelignore"
    ]
    
    backed_up = []
    for file in files_to_backup:
        if os.path.exists(file):
            try:
                shutil.copy2(file, backup_dir / file)
                backed_up.append(file)
                print(f"   ✅ Backed up {file}")
            except Exception as e:
                print(f"   ❌ Failed to backup {file}: {e}")
    
    print(f"   📁 Backup created in: {backup_dir.absolute()}")
    return backup_dir, backed_up

def create_minimal_vercel_config():
    """Create a minimal, guaranteed-working vercel.json configuration."""
    print("🔧 Creating minimal Vercel configuration...")
    
    minimal_config = {
        "version": 2,
        "builds": [
            {
                "src": "api.py",
                "use": "@vercel/python",
                "config": {
                    "runtime": "python3.12"
                }
            },
            {
                "src": "public/**",
                "use": "@vercel/static"
            }
        ],
        "routes": [
            {
                "src": "/api/(.*)",
                "dest": "/api.py"
            },
            {
                "src": "/(.*)",
                "dest": "/public/$1"
            }
        ]
    }
    
    try:
        with open("vercel.json", "w") as f:
            json.dump(minimal_config, f, indent=2)
        print("   ✅ Created minimal vercel.json")
        return True
    except Exception as e:
        print(f"   ❌ Failed to create vercel.json: {e}")
        return False

def create_minimal_package_json():
    """Create a minimal package.json with just the essential build script."""
    print("📦 Creating minimal package.json...")
    
    minimal_package = {
        "name": "docquery",
        "version": "1.0.0",
        "scripts": {
            "build": "python build.py --output public"
        },
        "engines": {
            "node": ">=16.0.0"
        }
    }
    
    try:
        with open("package.json", "w") as f:
            json.dump(minimal_package, f, indent=2)
        print("   ✅ Created minimal package.json")
        return True
    except Exception as e:
        print(f"   ❌ Failed to create package.json: {e}")
        return False

def create_minimal_requirements():
    """Create a minimal requirements file with only essential dependencies."""
    print("🐍 Creating minimal requirements-vercel.txt...")
    
    minimal_requirements = """# Minimal Vercel requirements - only essentials
fastapi>=0.104.0
uvicorn>=0.24.0
PyPDF2>=3.0.0
numpy>=1.24.0
openai>=1.97.1
python-multipart>=0.0.6
"""
    
    try:
        with open("requirements-vercel.txt", "w") as f:
            f.write(minimal_requirements)
        print("   ✅ Created minimal requirements-vercel.txt")
        return True
    except Exception as e:
        print(f"   ❌ Failed to create requirements: {e}")
        return False

def cleanup_deployment_blockers():
    """Remove files that might cause deployment issues."""
    print("🧹 Cleaning up potential deployment blockers...")
    
    files_to_remove = [
        ".vercel",
        "node_modules", 
        "__pycache__",
        ".pytest_cache",
        "dist",
        "build"
    ]
    
    removed = []
    for item in files_to_remove:
        if os.path.exists(item):
            try:
                if os.path.isdir(item):
                    shutil.rmtree(item)
                else:
                    os.remove(item)
                removed.append(item)
                print(f"   ✅ Removed {item}")
            except Exception as e:
                print(f"   ⚠️  Failed to remove {item}: {e}")
    
    if not removed:
        print("   ℹ️  No problematic files found")
    
    return True

def verify_essential_files():
    """Verify all essential files are present and correct."""
    print("🔍 Verifying essential files...")
    
    essential_files = {
        "api.py": "Main API file",
        "build.py": "Build script", 
        "vercel.json": "Vercel configuration",
        "package.json": "Node.js configuration",
        "requirements-vercel.txt": "Python dependencies"
    }
    
    missing = []
    for file, description in essential_files.items():
        if not os.path.exists(file):
            missing.append(f"{file} ({description})")
            print(f"   ❌ Missing: {file}")
        else:
            print(f"   ✅ Found: {file}")
    
    if missing:
        print(f"   ⚠️  Missing files: {missing}")
        return False
    
    # Test build process
    print("   🔨 Testing build process...")
    try:
        result = subprocess.run(["python", "build.py", "--output", "public"], 
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0 and os.path.exists("public"):
            print("   ✅ Build process works")
            return True
        else:
            print(f"   ❌ Build failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Build test failed: {e}")
        return False

def emergency_recovery():
    """Run the complete emergency recovery process."""
    print("🚨 DocQuery Emergency Vercel Deployment Recovery")
    print("=" * 60)
    print("This script will create a minimal, guaranteed-working Vercel configuration.")
    print("Use this when normal deployment troubleshooting fails.")
    print()
    
    steps = [
        ("Backup Current Config", backup_current_config),
        ("Cleanup Blockers", cleanup_deployment_blockers),
        ("Create Minimal Vercel Config", create_minimal_vercel_config),
        ("Create Minimal Package.json", create_minimal_package_json),
        ("Create Minimal Requirements", create_minimal_requirements),
        ("Verify Essential Files", verify_essential_files)
    ]
    
    passed = 0
    total = len(steps) - 1  # backup doesn't count as pass/fail
    
    for name, step_func in steps:
        print(f"{name}:")
        try:
            result = step_func()
            if name == "Backup Current Config":
                # Backup always succeeds, just continue
                pass
            elif result:
                passed += 1
            else:
                print(f"   ⚠️  {name} needs attention")
        except Exception as e:
            print(f"   ❌ {name} failed: {e}")
        print()
    
    print("=" * 60)
    print(f"📊 Results: {passed}/{total} steps completed")
    
    if passed == total:
        print("🎉 Emergency recovery completed successfully!")
        print("✅ Ready for fresh Vercel deployment")
        
        print("\n🚀 Next steps for fresh deployment:")
        print("1. Remove any existing project link:")
        print("   rm -rf .vercel")
        print("2. Create fresh Vercel project:")
        print("   vercel init")
        print("3. Deploy with debug output:")
        print("   vercel --debug")
        print("4. If successful, gradually add back features")
        
        return 0
    else:
        print("❌ Emergency recovery incomplete")
        print("Manual intervention may be required")
        
        print("\n🆘 Manual recovery steps:")
        print("1. Create completely new repository")
        print("2. Copy only essential files: api.py, build.py")
        print("3. Use vercel init to create fresh project")
        print("4. Migrate code incrementally")
        
        return 1

def main():
    """Main function for emergency recovery."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("DocQuery Emergency Vercel Deployment Recovery")
            print()
            print("Use this script when normal deployment fails.")
            print("It creates a minimal configuration guaranteed to work.")
            print()
            print("Usage: python emergency_recovery.py")
            print("       python emergency_recovery.py --help")
            return 0
        elif sys.argv[1] == "--minimal":
            # Just create minimal configs without other steps
            print("Creating minimal configurations only...")
            create_minimal_vercel_config()
            create_minimal_package_json()
            create_minimal_requirements()
            return 0
    
    # Ask for confirmation
    print("⚠️  This will modify your Vercel configuration files.")
    print("A backup will be created, but please commit your changes first.")
    response = input("Continue? (y/N): ").strip().lower()
    
    if response != 'y':
        print("Operation cancelled.")
        return 0
    
    return emergency_recovery()

if __name__ == "__main__":
    sys.exit(main())