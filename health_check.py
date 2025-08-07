#!/usr/bin/env python3
"""
Health check script for DocQuery deployment
Returns exit code 0 if everything is working, 1 if there are issues
"""
import sys

def health_check():
    """Perform basic health checks"""
    
    print("🔍 Performing health check...")
    
    try:
        # Test core imports
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__}")
        
        import PyPDF2
        print("✅ PyPDF2")
        
        import numpy
        print(f"✅ NumPy {numpy.__version__}")
        
        import sklearn
        print("✅ Scikit-learn")
        
        # Test optional imports
        try:
            import sentence_transformers
            print("✅ Sentence Transformers")
        except ImportError:
            print("⚠️ Sentence Transformers not available (fallback mode)")
            
        try:
            import faiss
            print("✅ FAISS")
        except ImportError:
            print("⚠️ FAISS not available (fallback mode)")
            
        # Test app imports
        try:
            from app import setup_environment
            setup_environment()
            print("✅ App configuration")
        except Exception as e:
            print(f"❌ App configuration error: {e}")
            return False
            
        print("🎉 Health check passed!")
        return True
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

if __name__ == "__main__":
    if health_check():
        sys.exit(0)
    else:
        sys.exit(1)