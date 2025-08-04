#!/usr/bin/env python3
"""
Vercel Deployment Validation Script
Validates deployment configuration and identifies potential issues before deployment.
"""

import os
import json
import sys
import subprocess
import importlib.util
from pathlib import Path

class VercelValidator:
    def __init__(self):
        self.repo_root = Path(__file__).parent
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_checks = 0

    def log_error(self, message):
        """Log an error message."""
        self.errors.append(f"❌ ERROR: {message}")
        print(f"❌ ERROR: {message}")

    def log_warning(self, message):
        """Log a warning message."""
        self.warnings.append(f"⚠️  WARNING: {message}")
        print(f"⚠️  WARNING: {message}")

    def log_success(self, message):
        """Log a success message."""
        self.success_count += 1
        print(f"✅ SUCCESS: {message}")

    def check_file_exists(self, file_path, required=True):
        """Check if a file exists."""
        self.total_checks += 1
        full_path = self.repo_root / file_path
        
        if full_path.exists():
            self.log_success(f"{file_path} exists")
            return True
        else:
            if required:
                self.log_error(f"Required file {file_path} is missing")
            else:
                self.log_warning(f"Optional file {file_path} is missing")
            return False

    def validate_vercel_json(self):
        """Validate vercel.json configuration."""
        print("\n🔍 Validating vercel.json...")
        
        if not self.check_file_exists("vercel.json"):
            return False

        try:
            with open(self.repo_root / "vercel.json", 'r') as f:
                config = json.load(f)

            # Check required sections
            required_sections = ['builds', 'routes']
            for section in required_sections:
                if section in config:
                    self.log_success(f"vercel.json has {section} section")
                else:
                    self.log_error(f"vercel.json missing {section} section")

            # Validate builds
            if 'builds' in config:
                builds = config['builds']
                if len(builds) > 0:
                    build = builds[0]
                    if build.get('src') == 'app.py' and build.get('use') == '@vercel/python':
                        self.log_success("Build configuration is correct for Python/Streamlit")
                    else:
                        self.log_warning("Build configuration may not be optimal for Python/Streamlit")
                else:
                    self.log_error("No builds configured in vercel.json")

            # Validate routes
            if 'routes' in config:
                routes = config['routes']
                if len(routes) > 0:
                    route = routes[0]
                    if route.get('dest') == 'app.py':
                        self.log_success("Route configuration is correct")
                    else:
                        self.log_warning("Route destination may not be correct")
                else:
                    self.log_error("No routes configured in vercel.json")

            # Check functions configuration
            if 'functions' in config:
                self.log_success("Function timeout configuration present")
            else:
                self.log_warning("No function timeout configuration - may cause timeout issues")

            return True

        except json.JSONDecodeError as e:
            self.log_error(f"vercel.json has invalid JSON: {e}")
            return False
        except Exception as e:
            self.log_error(f"Error reading vercel.json: {e}")
            return False

    def validate_requirements(self):
        """Validate Python requirements."""
        print("\n🔍 Validating requirements.txt...")
        
        if not self.check_file_exists("requirements.txt"):
            return False

        try:
            with open(self.repo_root / "requirements.txt", 'r') as f:
                requirements = f.read()

            # Check for essential packages
            essential_packages = ['streamlit', 'PyPDF2', 'numpy']
            for package in essential_packages:
                if package.lower() in requirements.lower():
                    self.log_success(f"Essential package {package} found in requirements.txt")
                else:
                    self.log_warning(f"Essential package {package} not found in requirements.txt")

            # Check for version pinning
            lines = [line.strip() for line in requirements.split('\n') if line.strip() and not line.startswith('#')]
            pinned_count = sum(1 for line in lines if '>=' in line or '==' in line or '~=' in line)
            
            if pinned_count == len(lines):
                self.log_success("All packages have version constraints")
            elif pinned_count > len(lines) * 0.8:
                self.log_warning("Most packages have version constraints - consider pinning all")
            else:
                self.log_warning("Many packages lack version constraints - this may cause deployment issues")

            return True

        except Exception as e:
            self.log_error(f"Error reading requirements.txt: {e}")
            return False

    def validate_app_py(self):
        """Validate app.py configuration."""
        print("\n🔍 Validating app.py...")
        
        if not self.check_file_exists("app.py"):
            return False

        try:
            with open(self.repo_root / "app.py", 'r') as f:
                app_content = f.read()

            # Check for Vercel handler function
            if 'def handler(' in app_content:
                self.log_success("Vercel handler function found")
            else:
                self.log_error("Vercel handler function missing")

            # Check for environment setup
            if 'setup_environment(' in app_content:
                self.log_success("Environment setup function found")
            else:
                self.log_warning("Environment setup function not found")

            # Check for PORT environment variable handling
            if 'PORT' in app_content and 'os.getenv' in app_content:
                self.log_success("PORT environment variable handling found")
            else:
                self.log_warning("PORT environment variable handling not found")

            # Check for Streamlit configuration
            if 'STREAMLIT_SERVER_HEADLESS' in app_content:
                self.log_success("Streamlit headless configuration found")
            else:
                self.log_warning("Streamlit headless configuration not found")

            return True

        except Exception as e:
            self.log_error(f"Error reading app.py: {e}")
            return False

    def validate_environment_variables(self):
        """Check for common environment variable issues."""
        print("\n🔍 Validating environment variables...")
        
        # Check for .env files that might contain secrets
        env_files = ['.env', '.env.local', '.env.production']
        for env_file in env_files:
            if (self.repo_root / env_file).exists():
                self.log_warning(f"{env_file} found - ensure it's in .gitignore and secrets are in Vercel dashboard")

        # Check if .gitignore exists and contains .env
        if self.check_file_exists(".gitignore", required=False):
            try:
                with open(self.repo_root / ".gitignore", 'r') as f:
                    gitignore_content = f.read()
                
                if '.env' in gitignore_content:
                    self.log_success(".env files are properly ignored in .gitignore")
                else:
                    self.log_warning(".env files should be added to .gitignore")
            except Exception:
                pass

        self.log_success("Environment variable validation completed")

    def validate_optimization_files(self):
        """Check for deployment optimization files."""
        print("\n🔍 Validating optimization files...")
        
        # Check for .vercelignore
        if self.check_file_exists(".vercelignore", required=False):
            try:
                with open(self.repo_root / ".vercelignore", 'r') as f:
                    vercelignore_content = f.read()
                
                optimization_patterns = ['__pycache__/', '*.pdf', '.git/', 'test_']
                found_patterns = sum(1 for pattern in optimization_patterns if pattern in vercelignore_content)
                
                if found_patterns >= 3:
                    self.log_success(".vercelignore contains good optimization patterns")
                else:
                    self.log_warning(".vercelignore could be more comprehensive")
                    
            except Exception:
                pass
        else:
            self.log_warning(".vercelignore not found - deployment may include unnecessary files")

    def check_dependencies_installable(self):
        """Check if dependencies can be installed."""
        print("\n🔍 Testing dependency installation...")
        
        try:
            # Try importing key modules
            test_imports = [
                ('streamlit', 'Streamlit'),
                ('PyPDF2', 'PyPDF2'),
                ('numpy', 'NumPy'),
                ('sklearn', 'scikit-learn')
            ]
            
            for module_name, display_name in test_imports:
                try:
                    importlib.import_module(module_name)
                    self.log_success(f"{display_name} is importable")
                except ImportError:
                    self.log_warning(f"{display_name} is not installed - run 'pip install -r requirements.txt'")
                    
        except Exception as e:
            self.log_error(f"Error testing dependencies: {e}")

    def generate_report(self):
        """Generate a final validation report."""
        print("\n" + "="*60)
        print("🏁 VERCEL DEPLOYMENT VALIDATION REPORT")
        print("="*60)
        
        print(f"\n📊 Summary:")
        print(f"   ✅ Successful checks: {self.success_count}/{self.total_checks}")
        print(f"   ⚠️  Warnings: {len(self.warnings)}")
        print(f"   ❌ Errors: {len(self.errors)}")
        
        if self.errors:
            print(f"\n❌ Critical Issues (Must Fix):")
            for error in self.errors:
                print(f"   {error}")
        
        if self.warnings:
            print(f"\n⚠️  Recommendations:")
            for warning in self.warnings:
                print(f"   {warning}")
        
        if not self.errors:
            print(f"\n🎉 Deployment validation PASSED! Ready to deploy to Vercel.")
            print(f"   Run 'vercel --prod' to deploy to production.")
        else:
            print(f"\n🚨 Deployment validation FAILED!")
            print(f"   Fix the critical issues above before deploying.")
            
        # Next steps
        print(f"\n📋 Next Steps:")
        if self.errors:
            print(f"   1. Fix all critical errors listed above")
            print(f"   2. Re-run this validator: python vercel_validator.py")
            print(f"   3. Test locally: streamlit run app.py")
            print(f"   4. Deploy to Vercel when all issues are resolved")
        else:
            print(f"   1. Test locally: streamlit run app.py")
            print(f"   2. Deploy to Vercel: vercel --prod")
            print(f"   3. Monitor deployment logs for any runtime issues")
            
        return len(self.errors) == 0

    def run_validation(self):
        """Run all validation checks."""
        print("🚀 Starting Vercel Deployment Validation")
        print("="*60)
        
        validation_steps = [
            self.validate_vercel_json,
            self.validate_requirements,
            self.validate_app_py,
            self.validate_environment_variables,
            self.validate_optimization_files,
            self.check_dependencies_installable
        ]
        
        for step in validation_steps:
            try:
                step()
            except Exception as e:
                self.log_error(f"Validation step failed: {e}")
        
        return self.generate_report()

def main():
    """Main entry point."""
    validator = VercelValidator()
    success = validator.run_validation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()