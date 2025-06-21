#!/bin/bash
set -e

echo "🧪 Running Prusa Connect Webcam Uploader Test Suite"
echo "=================================================="

# Check if virtual environment exists
if [[ ! -d "venv" ]]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -q -r requirements.txt
pip install -q -r test_requirements.txt

# Run linting (if available)
if command -v flake8 &> /dev/null; then
    echo "🔍 Running linting checks..."
    flake8 prusa_webcam_uploader.py --max-line-length=100 --ignore=E501,W503 || true
fi

# Run type checking (if available)
if command -v mypy &> /dev/null; then
    echo "🏷️  Running type checks..."
    mypy prusa_webcam_uploader.py --ignore-missing-imports || true
fi

# Run tests
echo "🚀 Running test suite..."
pytest

echo ""
echo "✅ Test suite completed!"
echo "📊 Coverage report generated in htmlcov/index.html"

# Deactivate virtual environment
deactivate
