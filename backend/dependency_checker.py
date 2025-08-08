"""
Dependency checker and installer for DocQuery system.
Provides clear feedback about available and missing features.
"""

import subprocess
import sys
import importlib
from typing import Dict, List, Tuple, Optional
import json

class DependencyChecker:
    """Checks and manages optional dependencies for enhanced functionality."""
    
    def __init__(self):
        self.core_dependencies = {
            'fastapi': 'Web API framework',
            'PyPDF2': 'PDF document processing',
            'numpy': 'Numerical operations',
            'sklearn': 'Machine learning and text analysis',  # scikit-learn imports as sklearn
            'openai': 'OpenAI API integration',
            'sqlalchemy': 'Database operations',
            'psycopg2': 'PostgreSQL database support'
        }
        
        self.optional_dependencies = {
            'transformers': {
                'description': 'Advanced local AI models (sentiment analysis, summarization)',
                'install_command': 'pip install transformers torch',
                'features': ['Local AI sentiment analysis', 'Text summarization', 'Advanced NLP'],
                'fallback': 'Rule-based text analysis'
            },
            'sentence_transformers': {  # Fixed import name
                'description': 'Semantic text embeddings for better search',
                'install_command': 'pip install sentence-transformers',
                'features': ['Semantic search', 'Better document similarity', 'Context-aware matching'],
                'fallback': 'TF-IDF text search'
            },
            'faiss': {  # Fixed import name
                'description': 'Fast approximate nearest neighbor search',
                'install_command': 'pip install faiss-cpu',
                'features': ['Faster vector search', 'Scalable document indexing', 'Improved performance'],
                'fallback': 'Scikit-learn similarity search'
            },
            'docx': {
                'description': 'Microsoft Word document processing',
                'install_command': 'pip install python-docx',
                'features': ['Word document (.docx) support', 'Table extraction', 'Advanced formatting'],
                'fallback': 'PDF and text files only'
            },
            'spacy': {
                'description': 'Advanced natural language processing',
                'install_command': 'pip install spacy && python -m spacy download en_core_web_sm',
                'features': ['Named entity recognition', 'Advanced text analysis', 'Language models'],
                'fallback': 'Basic regex-based parsing'
            }
        }
    
    def check_all_dependencies(self) -> Dict[str, Dict]:
        """Check status of all dependencies and return detailed report."""
        results = {
            'core': {},
            'optional': {},
            'summary': {
                'core_missing': 0,
                'optional_missing': 0,
                'available_features': [],
                'missing_features': []
            }
        }
        
        # Check core dependencies
        for dep, description in self.core_dependencies.items():
            status, version = self._check_dependency(dep)
            results['core'][dep] = {
                'available': status,
                'version': version,
                'description': description,
                'required': True
            }
            if not status:
                results['summary']['core_missing'] += 1
        
        # Check optional dependencies
        for dep, info in self.optional_dependencies.items():
            status, version = self._check_dependency(dep)
            results['optional'][dep] = {
                'available': status,
                'version': version,
                'description': info['description'],
                'install_command': info['install_command'],
                'features': info['features'],
                'fallback': info['fallback'],
                'required': False
            }
            
            if status:
                results['summary']['available_features'].extend(info['features'])
            else:
                results['summary']['optional_missing'] += 1
                results['summary']['missing_features'].extend(info['features'])
        
        return results
    
    def _check_dependency(self, package_name: str) -> Tuple[bool, Optional[str]]:
        """Check if a package is available and return its version."""
        try:
            module = importlib.import_module(package_name)
            version = getattr(module, '__version__', 'Unknown')
            return True, version
        except ImportError:
            return False, None
    
    def generate_report(self, detailed: bool = True) -> str:
        """Generate a human-readable dependency report."""
        results = self.check_all_dependencies()
        
        report = []
        report.append("🔍 DocQuery Dependency Status Report")
        report.append("=" * 50)
        
        # Core dependencies summary
        core_missing = results['summary']['core_missing']
        if core_missing == 0:
            report.append("✅ All core dependencies are installed")
        else:
            report.append(f"❌ {core_missing} core dependencies missing - system may not work properly")
        
        # Optional dependencies summary
        optional_missing = results['summary']['optional_missing']
        total_optional = len(self.optional_dependencies)
        available_optional = total_optional - optional_missing
        
        report.append(f"📊 Optional features: {available_optional}/{total_optional} available")
        
        if detailed:
            # Core dependencies detail
            report.append("\n📦 Core Dependencies:")
            for dep, info in results['core'].items():
                status = "✅" if info['available'] else "❌"
                version_str = f" (v{info['version']})" if info['version'] else ""
                report.append(f"  {status} {dep}{version_str} - {info['description']}")
            
            # Optional dependencies detail
            report.append("\n🔧 Optional Dependencies:")
            for dep, info in results['optional'].items():
                status = "✅" if info['available'] else "⚠️"
                version_str = f" (v{info['version']})" if info['version'] else ""
                report.append(f"  {status} {dep}{version_str}")
                report.append(f"     📝 {info['description']}")
                
                if info['available']:
                    report.append(f"     🎯 Features: {', '.join(info['features'])}")
                else:
                    report.append(f"     📥 Install: {info['install_command']}")
                    report.append(f"     🔄 Fallback: {info['fallback']}")
                report.append("")
        
        # Installation recommendations
        missing_deps = [dep for dep, info in results['optional'].items() if not info['available']]
        if missing_deps:
            report.append("💡 Quick Installation Commands:")
            for dep in missing_deps[:3]:  # Show top 3 recommendations
                command = results['optional'][dep]['install_command']
                features = ', '.join(results['optional'][dep]['features'][:2])
                report.append(f"  • {command}")
                report.append(f"    → Enables: {features}")
            
            if len(missing_deps) > 3:
                report.append(f"  ... and {len(missing_deps) - 3} more")
        
        return "\n".join(report)
    
    def get_installation_script(self) -> str:
        """Generate a script to install all optional dependencies."""
        script_lines = [
            "#!/bin/bash",
            "# DocQuery Optional Dependencies Installation Script",
            "echo 'Installing optional dependencies for enhanced DocQuery functionality...'",
            ""
        ]
        
        for dep, info in self.optional_dependencies.items():
            script_lines.append(f"echo 'Installing {dep}...'")
            script_lines.append(f"{info['install_command']}")
            script_lines.append("")
        
        script_lines.append("echo 'Installation complete! Restart the application to use new features.'")
        return "\n".join(script_lines)
    
    def install_dependency(self, dependency_name: str) -> Tuple[bool, str]:
        """Install a specific optional dependency."""
        if dependency_name not in self.optional_dependencies:
            return False, f"Unknown dependency: {dependency_name}"
        
        info = self.optional_dependencies[dependency_name]
        command = info['install_command']
        
        try:
            # Split command and run
            cmd_parts = command.split(' && ')
            for cmd in cmd_parts:
                result = subprocess.run(
                    cmd.split(), 
                    capture_output=True, 
                    text=True, 
                    check=True
                )
            
            # Verify installation
            success, version = self._check_dependency(dependency_name)
            if success:
                return True, f"Successfully installed {dependency_name} v{version}"
            else:
                return False, f"Installation completed but {dependency_name} is not importable"
                
        except subprocess.CalledProcessError as e:
            return False, f"Installation failed: {e.stderr}"
        except Exception as e:
            return False, f"Installation error: {str(e)}"
    
    def get_capabilities_summary(self) -> Dict[str, bool]:
        """Get a summary of current system capabilities."""
        results = self.check_all_dependencies()
        
        capabilities = {
            'pdf_processing': results['core']['PyPDF2']['available'],
            'word_processing': results['optional'].get('docx', {}).get('available', False),
            'advanced_ai': results['optional'].get('transformers', {}).get('available', False),
            'semantic_search': results['optional'].get('sentence-transformers', {}).get('available', False),
            'fast_search': results['optional'].get('faiss-cpu', {}).get('available', False),
            'advanced_nlp': results['optional'].get('spacy', {}).get('available', False),
            'basic_functionality': all(info['available'] for info in results['core'].values())
        }
        
        return capabilities

def main():
    """CLI interface for dependency checking."""
    checker = DependencyChecker()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--install-all':
        print("Installing all optional dependencies...")
        script = checker.get_installation_script()
        with open('/tmp/install_optional_deps.sh', 'w') as f:
            f.write(script)
        print("Installation script saved to /tmp/install_optional_deps.sh")
        print("Run: bash /tmp/install_optional_deps.sh")
    else:
        print(checker.generate_report())

if __name__ == "__main__":
    main()