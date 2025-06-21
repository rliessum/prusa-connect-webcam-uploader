# CONTRIBUTING.md

# Contributing to Prusa Connect Webcam Uploader

Thank you for your interest in contributing to this project! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Docker (optional, for containerized testing)

### Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rliessum/prusa-connect-webcam-uploader.git
   cd prusa-connect-webcam-uploader
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r test_requirements.txt
   ```

4. **Set up your environment:**
   ```bash
   cp .env.template .env
   # Edit .env with your test credentials
   ```

## Testing

### Running Tests

```bash
# Quick test run
./run_tests.sh

# Manual testing
pytest test_prusa_webcam_uploader.py -v

# With coverage
pytest --cov=prusa_webcam_uploader --cov-report=html

# Performance tests
pytest test_performance.py -v

# Skip slow tests
pytest -m "not slow"
```

### Test Structure

- **Unit Tests** (`test_prusa_webcam_uploader.py`): Test individual components
- **Performance Tests** (`test_performance.py`): Test performance and resource usage
- **Integration Tests**: End-to-end functionality testing

### Writing Tests

- Use pytest fixtures for setup
- Mock external dependencies (OpenCV, requests, subprocess)
- Test both success and failure scenarios
- Include edge cases and error conditions

## Code Quality

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use meaningful variable and function names

### Tools

- **flake8**: Code style checking
- **mypy**: Static type checking
- **pytest**: Testing framework

### Pre-commit Checks

Before submitting, ensure:
```bash
# Linting
flake8 prusa_webcam_uploader.py --max-line-length=100

# Type checking
mypy prusa_webcam_uploader.py --ignore-missing-imports

# Tests pass
pytest
```

## Architecture

### Core Components

1. **PrusaWebcamUploader**: Main class handling the upload logic
2. **Configuration**: Environment-based configuration with .env support
3. **Capture Methods**: HTTP (mjpeg-streamer) and RTSP support
4. **Upload**: Robust upload to Prusa Connect with retry logic
5. **Logging**: Structured logging for monitoring and debugging

### Design Principles

- **Robustness**: Handle failures gracefully with retries
- **Configurability**: Environment-based configuration
- **Observability**: Comprehensive logging and error reporting
- **Testability**: Mockable dependencies and clear interfaces
- **Security**: No hardcoded credentials, minimal privileges

## Submitting Changes

### Pull Request Process

1. **Fork** the repository
2. **Create a feature branch** from main:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** with appropriate tests
4. **Run the test suite** to ensure everything passes
5. **Commit** with clear, descriptive messages
6. **Push** to your fork and create a pull request

### Commit Messages

Use clear, descriptive commit messages:
```
feat: Add support for RTSP authentication
fix: Handle network timeouts gracefully
docs: Update configuration examples
test: Add integration tests for upload retry logic
```

### Pull Request Guidelines

- **Description**: Clearly describe what your change does and why
- **Testing**: Include tests for new functionality
- **Documentation**: Update README.md if needed
- **Breaking Changes**: Clearly document any breaking changes

## Release Process

### Versioning

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Creating Releases

1. Update version in relevant files
2. Update CHANGELOG.md
3. Create a git tag: `git tag v1.0.0`
4. Push tags: `git push --tags`
5. Create GitHub release with release notes

## Getting Help

### Communication

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Security**: For security issues, please email privately

### Issue Templates

When creating issues, please include:
- **Bug Reports**: Steps to reproduce, expected vs actual behavior, environment details
- **Feature Requests**: Use case, proposed solution, alternatives considered

### Debugging

#### Common Issues

1. **OpenCV Installation**: Use `opencv-python-headless` for server environments
2. **Authentication**: Verify FINGERPRINT and TOKEN are correct
3. **Network Issues**: Check connectivity and firewall settings
4. **Docker**: Ensure proper network configuration for container access

#### Debug Mode

Enable debug logging:
```bash
export PYTHONLOGLEVEL=DEBUG
python prusa_webcam_uploader.py
```

## Project Structure

```
├── prusa_webcam_uploader.py    # Main application
├── requirements.txt            # Production dependencies
├── test_requirements.txt       # Development dependencies
├── pytest.ini                 # Test configuration
├── Dockerfile                 # Container definition
├── docker-compose.yml         # Container orchestration
├── .env.template              # Configuration template
├── README.md                  # User documentation
├── CONTRIBUTING.md            # This file
├── run_tests.sh              # Test automation script
├── test_runner.py            # Development test runner
├── test_*.py                 # Test files
└── .github/workflows/        # CI/CD configuration
```

## Dependencies

### Production Dependencies

- **requests**: HTTP client for API calls
- **urllib3**: HTTP utilities
- **opencv-python-headless**: Computer vision library (headless for servers)

### Development Dependencies

- **pytest**: Testing framework
- **pytest-mock**: Mocking utilities
- **pytest-cov**: Coverage reporting
- **responses**: HTTP response mocking
- **flake8**: Code linting
- **mypy**: Type checking

## License

This project is open source. Please ensure any contributions are compatible with the project license.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow GitHub's Community Guidelines

## Acknowledgments

Thank you to all contributors who help improve this project!
