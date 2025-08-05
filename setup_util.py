#!/usr/bin/env python3
"""
Setup utility for DocQuery - helps users install optional dependencies
and configure the system for optimal performance.
"""

import sys
import subprocess
import argparse
from dependency_checker import DependencyChecker

def install_basic_setup():
    """Install core dependencies only."""
    print("🔧 Installing core dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
        print("✅ Core dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install core dependencies: {e}")
        return False

def install_enhanced_setup():
    """Install core + all optional dependencies for full functionality."""
    print("🚀 Installing enhanced setup with all optional features...")
    
    enhanced_packages = [
        "transformers",
        "torch", 
        "sentence-transformers",
        "faiss-cpu",
        "python-docx",
        "spacy"
    ]
    
    # Install packages
    try:
        # Install core first
        if not install_basic_setup():
            return False
            
        # Install optional packages
        for package in enhanced_packages:
            print(f"📦 Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        
        # Download spacy model
        print("📥 Downloading spaCy English model...")
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        
        print("✅ Enhanced setup completed successfully!")
        print("🎉 All features are now available!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        print("💡 You can continue with basic functionality")
        return False

def check_system():
    """Check current system status and capabilities."""
    print("🔍 Checking DocQuery system status...\n")
    
    checker = DependencyChecker()
    print(checker.generate_report())
    
    capabilities = checker.get_capabilities_summary()
    
    print("\n💡 Recommendations:")
    if not capabilities['basic_functionality']:
        print("❗ Run: python setup_util.py --basic (to install core dependencies)")
    elif not capabilities['advanced_ai'] or not capabilities['semantic_search']:
        print("🚀 Run: python setup_util.py --enhanced (for full AI capabilities)")
    else:
        print("✅ Your system is fully configured!")

def create_requirements_files():
    """Create different requirements files for different use cases."""
    
    # Basic requirements (already in pyproject.toml)
    basic_reqs = """# Basic DocQuery requirements
# Install with: pip install -r requirements-basic.txt

streamlit>=1.47.0
PyPDF2>=3.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
psycopg2-binary>=2.9.0
sqlalchemy>=2.0.0
openai>=1.97.1
"""

    # Enhanced requirements
    enhanced_reqs = """# Enhanced DocQuery requirements with all optional features
# Install with: pip install -r requirements-enhanced.txt

# Core requirements
streamlit>=1.47.0
PyPDF2>=3.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
psycopg2-binary>=2.9.0
sqlalchemy>=2.0.0
openai>=1.97.1

# Enhanced features
transformers>=4.21.0
torch>=1.12.0
sentence-transformers>=2.2.0
faiss-cpu>=1.7.0
python-docx>=0.8.11
spacy>=3.4.0

# Additional utilities
requests>=2.28.0
beautifulsoup4>=4.11.0
"""

    with open('requirements-basic.txt', 'w') as f:
        f.write(basic_reqs)
    
    with open('requirements-enhanced.txt', 'w') as f:
        f.write(enhanced_reqs)
    
    print("📝 Created requirements files:")
    print("  • requirements-basic.txt (core functionality)")
    print("  • requirements-enhanced.txt (all features)")

def main():
    parser = argparse.ArgumentParser(description='DocQuery Setup Utility')
    parser.add_argument('--basic', action='store_true', 
                       help='Install basic dependencies only')
    parser.add_argument('--enhanced', action='store_true', 
                       help='Install all dependencies for full functionality')
    parser.add_argument('--check', action='store_true', 
                       help='Check current system status')
    parser.add_argument('--create-requirements', action='store_true',
                       help='Create requirements.txt files')
    
    args = parser.parse_args()
    
    if args.basic:
        install_basic_setup()
    elif args.enhanced:
        install_enhanced_setup()
    elif args.check:
        check_system()
    elif args.create_requirements:
        create_requirements_files()
    else:
        # Interactive mode
        print("🤖 DocQuery Setup Utility")
        print("=" * 30)
        print("1. Check system status")
        print("2. Install basic setup (core features)")
        print("3. Install enhanced setup (all features)")
        print("4. Create requirements files")
        print("5. Exit")
        
        while True:
            try:
                choice = input("\nSelect option (1-5): ").strip()
                
                if choice == '1':
                    check_system()
                elif choice == '2':
                    install_basic_setup()
                elif choice == '3':
                    install_enhanced_setup()
                elif choice == '4':
                    create_requirements_files()
                elif choice == '5':
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice. Please select 1-5.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                break

if __name__ == "__main__":
    main()