# Prusa Connect Webcam Uploader

A robust, production-ready Python implementation for uploading webcam snapshots to Prusa Connect. This application continuously captures snapshots from either an mjpeg-streamer instance or directly from RTSP streams and uploads them to Prusa Connect with comprehensive error handling, logging, and monitoring.

## Features

- 🚀 **Production Ready**: Built with enterprise-grade error handling and logging
- 🔄 **Automatic Retry**: Intelligent retry mechanisms with exponential backoff
- 📊 **Comprehensive Logging**: Structured logging with configurable levels
- 🐋 **Docker Support**: Containerized deployment with security best practices
- ⚙️ **Configurable**: Extensive configuration options via environment variables
- 🛡️ **Secure**: Runs as non-root user in container
- 📈 **Health Checks**: Built-in health monitoring for container orchestration
- 🌐 **Network Resilient**: Handles network failures gracefully
- 📷 **Dual Capture Methods**: Support for both HTTP (mjpeg-streamer) and RTSP streams
- 🎥 **RTSP Support**: Direct capture from IP cameras with RTSP streams using OpenCV

## Quick Start

### Using Docker (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd prusa-connect-webcam-uploader
   ```

2. **Configure your credentials and capture method:**
   Edit `docker-compose.yml` and replace the placeholder values:
   ```yaml
   environment:
     - FINGERPRINT=your_actual_fingerprint_here
     - TOKEN=your_actual_token_here
     - CAPTURE_METHOD=http  # or 'rtsp' for RTSP streams
     # For RTSP, also set:
     # - RTSP_URL=rtsp://your-camera-ip:554/stream
   ```

3. **Start the service:**
   ```bash
   docker-compose up -d
   ```

4. **View logs:**
   ```bash
   docker-compose logs -f prusa-webcam-uploader
   ```

### Using Python Directly

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create a .env file (recommended):**
   ```bash
   cp .env.template .env
   # Edit .env with your actual values
   ```
   
   **Or set environment variables manually:**
   ```bash
   export FINGERPRINT="your_fingerprint_here"
   export TOKEN="your_token_here"
   export CAPTURE_METHOD="http"  # or "rtsp"
   # For RTSP also set:
   # export RTSP_URL="rtsp://your-camera-ip:554/stream"
   ```

3. **Run the application:**
   ```bash
   python prusa_webcam_uploader.py
   ```

## Configuration

The application can be configured in two ways:

### Option 1: .env File (Recommended)

Create a `.env` file in the same directory as the script:

```bash
cp .env.template .env
```

Then edit the `.env` file with your actual values. The application will automatically load these settings on startup.

### Option 2: Environment Variables

You can also set configuration via environment variables, which take precedence over .env file settings.

### Configuration Options

The application is configured via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `HTTP_URL` | `https://webcam.connect.prusa3d.com/c/snapshot` | Prusa Connect upload endpoint |
| `FINGERPRINT` | **Required** | Your Prusa Connect fingerprint |
| `TOKEN` | **Required** | Your Prusa Connect token |
| `CAPTURE_METHOD` | `http` | Capture method: `http` for mjpeg-streamer or `rtsp` for RTSP streams |
| `SNAPSHOT_URL` | `http://localhost:8080/?action=snapshot` | mjpeg-streamer snapshot URL (used when `CAPTURE_METHOD=http`) |
| `RTSP_URL` | *None* | RTSP stream URL (required when `CAPTURE_METHOD=rtsp`) |
| `RTSP_TIMEOUT` | `10` | RTSP connection timeout (seconds) |
| `PING_HOST` | `prusa` | Hostname to ping for connectivity check |
| `DELAY_SECONDS` | `10` | Normal delay between uploads (seconds) |
| `LONG_DELAY_SECONDS` | `60` | Delay after errors (seconds) |
| `MAX_RETRIES` | `3` | Maximum HTTP request retries |
| `TIMEOUT` | `30` | HTTP request timeout (seconds) |

## Docker Deployment

### Building the Image

```bash
docker build -t prusa-webcam-uploader .
```

### Running with Docker

```bash
docker run -d \
  --name prusa-webcam-uploader \
  --restart unless-stopped \
  -e FINGERPRINT="your_fingerprint" \
  -e TOKEN="your_token" \
  -e CAPTURE_METHOD="http" \
  -e SNAPSHOT_URL="http://host.docker.internal:8080/?action=snapshot" \
  -e PING_HOST="host.docker.internal" \
  --add-host=host.docker.internal:host-gateway \
  prusa-webcam-uploader
```

**For RTSP streams:**
```bash
docker run -d \
  --name prusa-webcam-uploader \
  --restart unless-stopped \
  -e FINGERPRINT="your_fingerprint" \
  -e TOKEN="your_token" \
  -e CAPTURE_METHOD="rtsp" \
  -e RTSP_URL="rtsp://192.168.1.100:554/stream" \
  -e PING_HOST="192.168.1.100" \
  prusa-webcam-uploader
```

### Using Docker Compose

1. Copy the provided `docker-compose.yml`
2. Edit environment variables
3. Run: `docker-compose up -d`

## Getting Your Prusa Connect Credentials

1. **Log into Prusa Connect**: Visit [connect.prusa3d.com](https://connect.prusa3d.com)
2. **Navigate to your printer**: Select your printer from the dashboard
3. **Go to Camera settings**: Look for webcam/camera configuration
4. **Copy credentials**: Find your `FINGERPRINT` and `TOKEN` values

## Network Configuration

### Capture Methods

The application supports two capture methods:

#### HTTP Method (mjpeg-streamer)
For traditional mjpeg-streamer setups:

**For mjpeg-streamer on the same host:**
- Use `http://localhost:8080/?action=snapshot` (direct Python)
- Use `http://host.docker.internal:8080/?action=snapshot` (Docker)

**For mjpeg-streamer on different host:**
- Use `http://printer-ip:8080/?action=snapshot`
- Ensure the host is reachable from your deployment environment

#### RTSP Method (IP Cameras)
For direct IP camera RTSP streams:

**Common RTSP URL formats:**
- Generic: `rtsp://username:password@ip:port/stream`
- Hikvision: `rtsp://username:password@ip:554/Streaming/Channels/101`
- Dahua: `rtsp://username:password@ip:554/cam/realmonitor?channel=1&subtype=0`
- Axis: `rtsp://username:password@ip:554/axis-media/media.amp`
- ONVIF: `rtsp://username:password@ip:554/onvif1`

**Configuration:**
```bash
export CAPTURE_METHOD="rtsp"
export RTSP_URL="rtsp://admin:password@192.168.1.100:554/stream"
export RTSP_TIMEOUT=10  # Connection timeout in seconds
```

**RTSP Notes:**
- Ensure your camera supports RTSP and it's enabled
- Test RTSP connectivity with VLC or similar before using
- Some cameras require authentication in the URL
- RTSP timeout should be adjusted based on your network latency

## Development and Testing

### Running Tests

The project includes a comprehensive test suite with unit tests, integration tests, and performance tests.

#### Quick Test Run
```bash
# Using the provided test script
./run_tests.sh
```

#### Manual Test Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r test_requirements.txt

# Run all tests
pytest

# Run specific test categories
pytest test_prusa_webcam_uploader.py -v          # Unit tests
pytest test_performance.py -v                    # Performance tests
pytest -m "not slow"                            # Skip slow tests
pytest --cov=prusa_webcam_uploader              # With coverage
```

#### Test Categories

- **Unit Tests**: Test individual components and methods
- **Integration Tests**: Test end-to-end functionality
- **Performance Tests**: Test memory usage and performance characteristics
- **Stress Tests**: Test behavior under load and error conditions

#### Coverage Reports

Test coverage reports are generated in HTML format:
```bash
pytest --cov=prusa_webcam_uploader --cov-report=html
open htmlcov/index.html  # View coverage report
```

### Code Quality

The project uses several tools to maintain code quality:

- **pytest**: Test framework with fixtures and parametrization
- **flake8**: Code style and error checking
- **mypy**: Static type checking
- **coverage**: Test coverage measurement

### Continuous Integration

GitHub Actions automatically run tests on:
- Python 3.8, 3.9, 3.10, 3.11
- Ubuntu latest
- Docker container builds
- Code coverage reporting

## Monitoring and Logging

### Viewing Logs

**Docker Compose:**
```bash
docker-compose logs -f prusa-webcam-uploader
```

**Docker:**
```bash
docker logs -f prusa-webcam-uploader
```

### Log Levels

The application logs at different levels:
- `INFO`: Normal operation events
- `WARNING`: Recoverable errors (network issues, retries)
- `ERROR`: Upload failures, configuration issues
- `DEBUG`: Detailed operation information

### Health Monitoring

The Docker container includes health checks. Monitor with:
```bash
docker inspect --format='{{.State.Health.Status}}' prusa-webcam-uploader
```

## Troubleshooting

### Common Issues

1. **Configuration Issues**
   - Verify your `.env` file exists and contains valid values
   - Check that `FINGERPRINT` and `TOKEN` are correctly set
   - Ensure `CAPTURE_METHOD` is either `http` or `rtsp`
   - For RTSP, verify `RTSP_URL` is properly formatted

2. **Connection Refused**
   - Check if mjpeg-streamer is running: `curl http://localhost:8080/?action=snapshot`
   - Verify network connectivity between containers

3. **Authentication Errors**
   - Verify `FINGERPRINT` and `TOKEN` are correct
   - Check Prusa Connect dashboard for active tokens

4. **Image Capture Failures**
   - Test snapshot URL manually: `wget http://localhost:8080/?action=snapshot -O test.jpg`
   - Check mjpeg-streamer logs for errors

5. **Docker Network Issues**
   - Ensure `host.docker.internal` resolves: `docker exec container ping host.docker.internal`
   - Try using the host's IP address instead

### Debug Mode

Enable debug logging by setting the Python logging level:
```bash
export PYTHONLOGLEVEL=DEBUG
```

### Testing Connectivity

Test your setup manually:
```bash
# Test snapshot capture
curl -o test.jpg http://localhost:8080/?action=snapshot

# Test upload (replace with your credentials)
curl -X PUT "https://webcam.connect.prusa3d.com/c/snapshot" \
  -H "fingerprint: YOUR_FINGERPRINT" \
  -H "token: YOUR_TOKEN" \
  -H "content-type: image/jpg" \
  --data-binary "@test.jpg"
```

## Security Considerations

- Container runs as non-root user (`prusa:1000`)
- No unnecessary system capabilities
- Minimal base image with only required dependencies
- Environment variables for sensitive data (no hardcoded secrets)
- Resource limits to prevent resource exhaustion

## Performance

- **Memory Usage**: ~50-100MB typical
- **CPU Usage**: Minimal (<1% on modern systems)
- **Network**: ~1-10KB per upload (depends on image size)
- **Disk**: Temporary image files cleaned automatically

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license here]

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review container logs
3. Open an issue with detailed information about your setup
