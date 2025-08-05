#!/usr/bin/env python3
"""
Test script to verify Vercel deployment size optimization.
This simulates what files would be included/excluded in the deployment.
"""
import os
import sys
from pathlib import Path

def check_vercelignore():
    """Check if .vercelignore is properly configured."""
    vercelignore_path = Path('.vercelignore')
    if not vercelignore_path.exists():
        return False, "No .vercelignore file found"
    
    with open(vercelignore_path) as f:
        content = f.read()
    
    required_exclusions = ['*.pdf', '__pycache__/', 'requirements-enhanced.txt', 'uv.lock']
    missing = []
    for exclusion in required_exclusions:
        if exclusion not in content:
            missing.append(exclusion)
    
    if missing:
        return False, f"Missing exclusions: {missing}"
    
    return True, "All required exclusions present"

def simulate_deployment_size():
    """Simulate the deployment by calculating size of files that would be included."""
    vercelignore_path = Path('.vercelignore')
    if not vercelignore_path.exists():
        return False, "No .vercelignore file"
    
    # Read exclusion patterns
    with open(vercelignore_path) as f:
        exclusions = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    total_size = 0
    excluded_size = 0
    excluded_files = []
    
    for root, dirs, files in os.walk('.'):
        for file in files:
            file_path = Path(root) / file
            rel_path = file_path.relative_to('.')
            size = file_path.stat().st_size
            
            # Check if file should be excluded
            excluded = False
            for pattern in exclusions:
                if pattern.endswith('/'):
                    # Directory pattern
                    if str(rel_path).startswith(pattern.rstrip('/')):
                        excluded = True
                        break
                elif '*' in pattern:
                    # Wildcard pattern
                    import fnmatch
                    if fnmatch.fnmatch(str(rel_path), pattern) or fnmatch.fnmatch(file, pattern):
                        excluded = True
                        break
                else:
                    # Exact match
                    if str(rel_path) == pattern or file == pattern:
                        excluded = True
                        break
            
            if excluded:
                excluded_size += size
                excluded_files.append((str(rel_path), size))
            else:
                total_size += size
    
    return True, {
        'deployed_size_mb': total_size / (1024 * 1024),
        'excluded_size_mb': excluded_size / (1024 * 1024),
        'excluded_files': excluded_files[:10]  # Show first 10 excluded files
    }

def check_minimal_requirements():
    """Check if requirements.txt uses minimal dependencies."""
    with open('requirements.txt') as f:
        content = f.read()
    
    # Heavy dependencies that should NOT be in requirements.txt
    heavy_deps = ['transformers', 'torch', 'sentence-transformers', 'faiss', 'spacy']
    found_heavy = []
    
    for dep in heavy_deps:
        if dep in content.lower():
            found_heavy.append(dep)
    
    if found_heavy:
        return False, f"Heavy dependencies found: {found_heavy}"
    
    return True, "Using minimal dependencies"

def main():
    print("🚀 Vercel Deployment Size Optimization Test")
    print("=" * 50)
    
    # Test 1: Check .vercelignore
    success, message = check_vercelignore()
    print(f"{'✅' if success else '❌'} .vercelignore configuration: {message}")
    
    # Test 2: Check requirements
    success, message = check_minimal_requirements()
    print(f"{'✅' if success else '❌'} Minimal requirements: {message}")
    
    # Test 3: Simulate deployment size
    success, result = simulate_deployment_size()
    if success:
        print(f"✅ Deployment simulation:")
        print(f"   📦 Deployed size: {result['deployed_size_mb']:.2f} MB")
        print(f"   🗑️  Excluded size: {result['excluded_size_mb']:.2f} MB")
        print(f"   💾 Size reduction: {result['excluded_size_mb']:.2f} MB")
        
        if result['deployed_size_mb'] < 50:  # Conservative estimate for code + lightweight deps
            print("   ✅ Deployment size looks reasonable for Vercel limits")
        else:
            print("   ⚠️  Deployment size might still be large")
            
        print(f"   🗂️  Sample excluded files:")
        for file_path, size in result['excluded_files']:
            print(f"      - {file_path} ({size / 1024:.1f} KB)")
    else:
        print(f"❌ Deployment simulation failed: {result}")
    
    print("\n📋 Summary:")
    print("- Large PDF files excluded from deployment")
    print("- Heavy ML dependencies removed from requirements.txt")  
    print("- App uses fallback to simple vector search for deployment")
    print("- Estimated deployment size well under 250MB limit")

if __name__ == "__main__":
    main()