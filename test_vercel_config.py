#!/usr/bin/env python3
"""
Test script to validate vercel.json configuration
"""

import json
import sys

def validate_vercel_config():
    """Validate the vercel.json configuration"""
    
    try:
        with open('vercel.json', 'r') as f:
            config = json.load(f)
        
        print("✅ vercel.json is valid JSON")
        
        # Check for functions configuration
        if 'functions' in config:
            functions = config['functions']
            print(f"✅ Functions configuration found: {len(functions)} patterns")
            
            for pattern, settings in functions.items():
                if 'runtime' in settings:
                    runtime = settings['runtime']
                    print(f"✅ Pattern '{pattern}' uses runtime: {runtime}")
                    
                    # Check if runtime follows Vercel format (@vercel/...)
                    if runtime.startswith('@vercel/'):
                        print(f"✅ Runtime '{runtime}' uses correct Vercel format")
                    else:
                        print(f"❌ Runtime '{runtime}' uses incorrect format (should start with @vercel/)")
                        return False
        
        # Check builds configuration
        if 'builds' in config:
            builds = config['builds']
            print(f"✅ Builds configuration found: {len(builds)} builds")
            
            for build in builds:
                if 'use' in build:
                    use = build['use']
                    print(f"✅ Build uses: {use}")
        
        print("✅ All runtime configurations are correct!")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in vercel.json: {e}")
        return False
    except FileNotFoundError:
        print("❌ vercel.json file not found")
        return False
    except Exception as e:
        print(f"❌ Error validating vercel.json: {e}")
        return False

if __name__ == "__main__":
    success = validate_vercel_config()
    sys.exit(0 if success else 1)