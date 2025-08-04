#!/usr/bin/env python3
"""
Test suite to validate Vercel deployment configuration for DocQuery.
"""

import os
import json
import unittest
import tempfile

class VercelDeploymentTests(unittest.TestCase):
    """Test cases for Vercel deployment configuration."""
    
    def setUp(self):
        """Set up test environment."""
        self.repo_root = os.path.dirname(os.path.abspath(__file__))
    
    def test_requirements_txt_exists(self):
        """Test that requirements.txt exists in repo root."""
        requirements_path = os.path.join(self.repo_root, 'requirements.txt')
        self.assertTrue(os.path.exists(requirements_path), 
                       "requirements.txt should exist in repo root")
        
        # Verify it contains essential packages
        with open(requirements_path, 'r') as f:
            content = f.read()
            self.assertIn('streamlit>=1.47.0', content)
            self.assertIn('PyPDF2>=3.0.0', content)
    
    def test_vercel_json_exists(self):
        """Test that vercel.json exists and has correct configuration."""
        vercel_path = os.path.join(self.repo_root, 'vercel.json')
        self.assertTrue(os.path.exists(vercel_path), 
                       "vercel.json should exist in repo root")
        
        # Verify JSON structure
        with open(vercel_path, 'r') as f:
            config = json.load(f)
            
        self.assertIn('builds', config)
        self.assertIn('routes', config)
        
        # Check builds configuration
        builds = config['builds']
        self.assertEqual(len(builds), 1)
        self.assertEqual(builds[0]['src'], 'app.py')
        self.assertEqual(builds[0]['use'], '@vercel/python')
        
        # Check routes configuration
        routes = config['routes']
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0]['src'], '/(.*)')
        self.assertEqual(routes[0]['dest'], 'app.py')
    
    def test_app_py_port_configuration(self):
        """Test that app.py reads PORT environment variable."""
        # Test with custom PORT by directly calling setup_environment
        original_port = os.environ.get('PORT')
        original_streamlit_port = os.environ.get('STREAMLIT_SERVER_PORT')
        
        try:
            # Set custom PORT
            os.environ['PORT'] = '9000'
            
            # Clear the STREAMLIT_SERVER_PORT to force re-evaluation
            if 'STREAMLIT_SERVER_PORT' in os.environ:
                del os.environ['STREAMLIT_SERVER_PORT']
            
            # Import and call setup_environment directly
            from app import setup_environment
            port = setup_environment()
            
            # Check that the function returned the correct port
            self.assertEqual(port, 9000)
            # Check that STREAMLIT_SERVER_PORT was set correctly
            self.assertEqual(os.environ.get('STREAMLIT_SERVER_PORT'), '9000')
            
        finally:
            # Clean up environment
            if original_port is not None:
                os.environ['PORT'] = original_port
            elif 'PORT' in os.environ:
                del os.environ['PORT']
                
            if original_streamlit_port is not None:
                os.environ['STREAMLIT_SERVER_PORT'] = original_streamlit_port
            elif 'STREAMLIT_SERVER_PORT' in os.environ:
                del os.environ['STREAMLIT_SERVER_PORT']
    
    def test_app_py_default_port(self):
        """Test that app.py uses default port 8501 when PORT is not set."""
        # Ensure PORT is not set
        if 'PORT' in os.environ:
            del os.environ['PORT']
        if 'STREAMLIT_SERVER_PORT' in os.environ:
            del os.environ['STREAMLIT_SERVER_PORT']
        
        # Import app module fresh (this is tricky with imports)
        # Instead, test the setup_environment function directly
        from app import setup_environment
        port = setup_environment()
        
        self.assertEqual(port, 8501)
        self.assertEqual(os.environ.get('STREAMLIT_SERVER_PORT'), '8501')
    
    def test_vercel_handler_exists(self):
        """Test that app.py has a Vercel handler function."""
        import app
        self.assertTrue(hasattr(app, 'handler'), 
                       "app.py should have a 'handler' function for Vercel")
        
        # Test handler function
        mock_event = {}
        mock_context = {}
        response = app.handler(mock_event, mock_context)
        
        self.assertIsInstance(response, dict)
        self.assertIn('statusCode', response)
        self.assertEqual(response['statusCode'], 200)
    
    def test_start_script_exists(self):
        """Test that start.sh script exists and is executable."""
        start_script = os.path.join(self.repo_root, 'start.sh')
        self.assertTrue(os.path.exists(start_script), 
                       "start.sh should exist for Vercel deployment")
        
        # Check if it's executable
        self.assertTrue(os.access(start_script, os.X_OK), 
                       "start.sh should be executable")
        
        # Check script content
        with open(start_script, 'r') as f:
            content = f.read()
            self.assertIn('streamlit run app.py', content)
            self.assertIn('PORT=${PORT:-8501}', content)

def run_tests():
    """Run all Vercel deployment tests."""
    print("🧪 Running Vercel Deployment Tests")
    print("=" * 50)
    
    # Run tests
    unittest.main(verbosity=2, exit=False)

if __name__ == '__main__':
    run_tests()