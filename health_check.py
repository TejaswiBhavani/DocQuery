#!/usr/bin/env python3
"""
Vercel Deployment Health Check
A simple script to verify that the deployed application is working correctly.
"""

import requests
import json
import sys
import time
from urllib.parse import urljoin

class DeploymentHealthChecker:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 30

    def check_main_endpoint(self):
        """Check if the main application endpoint is responding."""
        try:
            response = self.session.get(self.base_url)
            if response.status_code == 200:
                print(f"✅ Main endpoint responding (Status: {response.status_code})")
                return True
            else:
                print(f"❌ Main endpoint error (Status: {response.status_code})")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Main endpoint unreachable: {e}")
            return False

    def check_handler_endpoint(self):
        """Check if the Vercel handler endpoint is working."""
        try:
            # Try the handler function directly (for serverless functions)
            handler_url = urljoin(self.base_url, '/api/handler')
            response = self.session.get(handler_url)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'message' in data:
                        print(f"✅ Handler endpoint working: {data.get('message', 'OK')}")
                        return True
                except json.JSONDecodeError:
                    pass
            
            print(f"⚠️  Handler endpoint not accessible (Status: {response.status_code})")
            return False
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Handler endpoint not found (expected for Streamlit apps): {e}")
            return False

    def check_static_assets(self):
        """Check if static assets are loading correctly."""
        static_paths = [
            '/_static/css/main.css',
            '/_static/js/main.js', 
            '/style.css'
        ]
        
        working_assets = 0
        total_assets = len(static_paths)
        
        for path in static_paths:
            try:
                url = urljoin(self.base_url, path)
                response = self.session.head(url)
                if response.status_code == 200:
                    working_assets += 1
                    print(f"✅ Static asset found: {path}")
                else:
                    print(f"⚠️  Static asset missing: {path} (Status: {response.status_code})")
            except requests.exceptions.RequestException:
                print(f"⚠️  Static asset unreachable: {path}")
        
        if working_assets > 0:
            print(f"✅ Some static assets are loading ({working_assets}/{total_assets})")
            return True
        else:
            print(f"⚠️  No static assets found - this may be normal for serverless functions")
            return False

    def check_response_headers(self):
        """Check response headers for common issues."""
        try:
            response = self.session.head(self.base_url)
            headers = response.headers
            
            # Check important headers
            if 'content-type' in headers:
                print(f"✅ Content-Type header present: {headers['content-type']}")
            else:
                print(f"⚠️  Content-Type header missing")
            
            if 'x-vercel-id' in headers:
                print(f"✅ Vercel deployment ID found: {headers['x-vercel-id']}")
            else:
                print(f"⚠️  Not deployed on Vercel or missing headers")
            
            # Check for caching headers
            cache_headers = ['cache-control', 'etag', 'last-modified']
            found_cache = any(header in headers for header in cache_headers)
            if found_cache:
                print(f"✅ Caching headers present")
            else:
                print(f"⚠️  No caching headers found")
                
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Could not check headers: {e}")
            return False

    def check_performance(self):
        """Check basic performance metrics."""
        try:
            start_time = time.time()
            response = self.session.get(self.base_url)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to ms
            
            if response_time < 1000:
                print(f"✅ Good response time: {response_time:.2f}ms")
            elif response_time < 3000:
                print(f"⚠️  Slow response time: {response_time:.2f}ms")
            else:
                print(f"❌ Very slow response time: {response_time:.2f}ms")
            
            # Check response size
            content_length = len(response.content)
            if content_length > 0:
                print(f"✅ Response has content ({content_length} bytes)")
                return True
            else:
                print(f"⚠️  Empty response")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Performance check failed: {e}")
            return False

    def run_health_check(self):
        """Run all health checks."""
        print(f"🏥 Starting Health Check for: {self.base_url}")
        print("=" * 60)
        
        checks = [
            ("Main Endpoint", self.check_main_endpoint),
            ("Handler Function", self.check_handler_endpoint),
            ("Static Assets", self.check_static_assets),
            ("Response Headers", self.check_response_headers),
            ("Performance", self.check_performance)
        ]
        
        passed_checks = 0
        total_checks = len(checks)
        
        for check_name, check_function in checks:
            print(f"\n🔍 {check_name}:")
            try:
                if check_function():
                    passed_checks += 1
            except Exception as e:
                print(f"❌ {check_name} failed with error: {e}")
        
        print("\n" + "=" * 60)
        print(f"🏁 Health Check Summary")
        print("=" * 60)
        print(f"✅ Passed: {passed_checks}/{total_checks} checks")
        
        if passed_checks == total_checks:
            print(f"🎉 All health checks passed! Deployment is healthy.")
            return True
        elif passed_checks >= total_checks * 0.8:
            print(f"⚠️  Most checks passed. Minor issues detected.")
            return True
        else:
            print(f"❌ Multiple issues detected. Check deployment logs.")
            return False

def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python health_check.py <deployment_url>")
        print("Example: python health_check.py https://your-app.vercel.app")
        sys.exit(1)
    
    deployment_url = sys.argv[1]
    
    # Validate URL format
    if not deployment_url.startswith(('http://', 'https://')):
        deployment_url = 'https://' + deployment_url
    
    checker = DeploymentHealthChecker(deployment_url)
    success = checker.run_health_check()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()