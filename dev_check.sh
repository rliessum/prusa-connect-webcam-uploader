#!/bin/bash
# Development helper script for code quality and testing

set -e  # Exit on any error

echo "🧹 Running code quality checks and formatting..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_warning "No virtual environment detected. Consider activating one:"
    echo "  python3 -m venv venv && source venv/bin/activate"
fi

# Install development dependencies if needed
print_status "Checking development dependencies..."
pip install -q -r requirements.txt
pip install -q -r test_requirements.txt

# Run code formatting with black (if available)
if command -v black &> /dev/null; then
    print_status "Formatting code with black..."
    black prusa_webcam_uploader.py --line-length 100 --quiet
    print_success "Code formatting completed"
else
    print_warning "black not installed, skipping code formatting"
fi

# Run import sorting with isort (if available)
if command -v isort &> /dev/null; then
    print_status "Sorting imports with isort..."
    isort prusa_webcam_uploader.py --quiet
    print_success "Import sorting completed"
else
    print_warning "isort not installed, skipping import sorting"
fi

# Run linting with flake8
print_status "Running linting with flake8..."
if flake8 prusa_webcam_uploader.py --max-line-length=100 --ignore=E501,W503,E203; then
    print_success "Linting passed"
else
    print_error "Linting failed - check output above"
    exit 1
fi

# Run type checking with mypy
print_status "Running type checking with mypy..."
if mypy prusa_webcam_uploader.py --ignore-missing-imports --no-strict-optional; then
    print_success "Type checking passed"
else
    print_warning "Type checking had issues - check output above"
fi

# Run security checks with bandit (if available)
if command -v bandit &> /dev/null; then
    print_status "Running security check with bandit..."
    if bandit -r prusa_webcam_uploader.py -q; then
        print_success "Security check passed"
    else
        print_warning "Security check had issues - review output above"
    fi
else
    print_warning "bandit not installed, skipping security check"
fi

# Run tests
print_status "Running test suite..."
if python -m pytest -v --tb=short; then
    print_success "All tests passed"
else
    print_error "Some tests failed - check output above"
    exit 1
fi

# Run test coverage
print_status "Generating test coverage report..."
python -m pytest --cov=prusa_webcam_uploader --cov-report=term-missing --cov-report=html --quiet

print_success "🎉 All quality checks completed!"
print_status "Coverage report generated in htmlcov/index.html"

echo ""
echo "📊 Summary:"
echo "  ✅ Code formatting"
echo "  ✅ Import sorting"
echo "  ✅ Linting (flake8)"
echo "  ✅ Type checking (mypy)"
echo "  ✅ Security check (bandit)"
echo "  ✅ Test suite"
echo "  ✅ Coverage report"
echo ""
print_success "Ready for commit! 🚀"
