#!/bin/bash
# Render build script with error handling

set -e  # Exit on any error

echo "Starting DocQuery build process..."

# Update pip
pip install --upgrade pip

# Try main requirements first, fallback to minimal requirements
echo "Installing dependencies..."
if pip install --no-cache-dir -r requirements.txt; then
    echo "✅ Main requirements installed successfully"
elif pip install --no-cache-dir -r requirements-render.txt; then
    echo "✅ Fallback requirements installed successfully"
else
    echo "❌ Failed to install requirements"
    exit 1
fi

# Verify core dependencies
echo "Verifying installation..."
python -c "import streamlit, PyPDF2, numpy, sklearn; print('✅ Core dependencies verified')"

echo "✅ Build completed successfully!"