#!/usr/bin/env python3
"""
Setup script for DocQuery - LLM-Powered Intelligent Query-Retrieval System
"""

from setuptools import setup, find_packages
import os

# Read the contents of requirements.txt
def read_requirements():
    with open('requirements.txt', 'r') as f:
        return [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]

# Read the README file
def read_readme():
    if os.path.exists('README.md'):
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    return "LLM-Powered Intelligent Query-Retrieval System for document analysis"

setup(
    name="docquery",
    version="1.0.0",
    author="TejaswiBhavani",
    description="LLM-Powered Intelligent Query-Retrieval System",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/TejaswiBhavani/DocQuery",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "enhanced": [
            "transformers>=4.21.0",
            "torch>=1.12.0",
            "spacy>=3.4.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ]
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.toml", "*.css"],
    },
    entry_points={
        "console_scripts": [
            "docquery-web=app:main",
            "docquery-api=api:main",
            "docquery-setup=setup_util:main",
        ],
    },
    zip_safe=False,
)