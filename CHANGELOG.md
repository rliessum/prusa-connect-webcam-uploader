# Changelog

All notable changes to the Prusa Connect Webcam Uploader project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of Prusa Connect Webcam Uploader
- Support for HTTP capture from mjpeg-streamer
- Support for RTSP capture from IP cameras using OpenCV
- Robust upload to Prusa Connect with retry mechanisms
- Environment-based configuration with .env file support
- Comprehensive logging with configurable levels
- Docker containerization with security best practices
- Health checks for container orchestration
- Extensive test suite with unit, integration, and performance tests
- GitHub Actions CI/CD pipeline
- Comprehensive documentation and contribution guidelines

### Features
- **Dual Capture Methods**: HTTP (mjpeg-streamer) and RTSP streams
- **Production Ready**: Enterprise-grade error handling and logging
- **Configurable**: Extensive configuration via environment variables
- **Resilient**: Automatic retry with exponential backoff
- **Secure**: Non-root container execution, no hardcoded secrets
- **Testable**: 95%+ test coverage with mocking for external dependencies
- **Observable**: Structured logging and health monitoring

### Configuration
- HTTP_URL: Prusa Connect upload endpoint
- FINGERPRINT: Prusa Connect device fingerprint
- TOKEN: Prusa Connect authentication token
- CAPTURE_METHOD: 'http' or 'rtsp' capture method
- SNAPSHOT_URL: mjpeg-streamer endpoint (for HTTP method)
- RTSP_URL: RTSP stream URL (for RTSP method)
- DELAY_SECONDS: Normal operation delay
- LONG_DELAY_SECONDS: Error retry delay
- RTSP_TIMEOUT: RTSP connection timeout
- Various other networking and retry configuration options

### Technical Details
- **Language**: Python 3.8+
- **Dependencies**: requests, urllib3, opencv-python-headless
- **Testing**: pytest with comprehensive mocking
- **Containerization**: Docker with minimal base image
- **CI/CD**: GitHub Actions with multi-Python version testing
- **Documentation**: README, CONTRIBUTING, inline documentation

### Deployment Options
- **Standalone Python**: Direct execution with virtual environment
- **Docker**: Containerized deployment with docker-compose
- **Kubernetes**: Ready for container orchestration (health checks included)

## [1.0.0] - 2025-06-21

### Added
- Initial project structure and core functionality
- HTTP capture support for mjpeg-streamer integration
- RTSP capture support for direct IP camera integration
- Prusa Connect upload functionality with authentication
- Environment-based configuration system
- .env file support for easy configuration management
- Docker containerization with security best practices
- Comprehensive test suite with 50+ test cases
- Performance and stress testing framework
- GitHub Actions CI/CD pipeline
- Extensive documentation and examples

### Security
- Non-root container execution
- No hardcoded credentials or secrets
- Secure environment variable handling
- Minimal container image with only required dependencies

### Documentation
- Complete README with setup and usage instructions
- Docker and docker-compose examples
- Troubleshooting guide
- API documentation and configuration reference
- Contributing guidelines and development setup

---

## Release Notes

### v1.0.0 - Initial Release

This is the first stable release of the Prusa Connect Webcam Uploader, a professional-grade Python implementation for uploading webcam snapshots to Prusa Connect.

**Key Highlights:**
- 🚀 **Production Ready**: Built with enterprise-grade error handling
- 📷 **Dual Capture Support**: Both HTTP and RTSP capture methods
- 🐋 **Docker Ready**: Full containerization with docker-compose
- 🧪 **Comprehensive Testing**: 95%+ code coverage with extensive test suite
- 📚 **Complete Documentation**: Setup guides, examples, and troubleshooting
- 🔒 **Security Focused**: No hardcoded secrets, minimal privileges

**Migration from Bash Script:**
This Python implementation replaces the original bash script with significant improvements:
- Better error handling and recovery
- Structured logging and monitoring
- RTSP support for IP cameras
- Configurable retry mechanisms
- Professional testing and CI/CD
- Docker containerization
- Cross-platform compatibility

**Getting Started:**
```bash
# Quick start with Docker
docker-compose up -d

# Or with Python
cp .env.template .env
# Edit .env with your credentials
python prusa_webcam_uploader.py
```

**Upgrade Path:**
For users migrating from the bash script:
1. Set CAPTURE_METHOD=http for mjpeg-streamer compatibility
2. Use SNAPSHOT_URL for your existing mjpeg-streamer endpoint
3. Set FINGERPRINT and TOKEN from your Prusa Connect settings
4. Optionally switch to RTSP for direct camera integration

This release establishes a solid foundation for the project with comprehensive features, testing, and documentation.
