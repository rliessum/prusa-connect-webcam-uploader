# 🐋 Docker Deployment Examples

This guide provides various Docker deployment scenarios and configurations for the Prusa Connect Webcam Uploader.

## 🚀 Quick Start Examples

### 1. Basic HTTP Capture (mjpeg-streamer)

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  prusa-webcam-uploader:
    build: .
    container_name: prusa-webcam-uploader
    restart: unless-stopped
    
    environment:
      - FINGERPRINT=your_fingerprint_here
      - TOKEN=your_token_here
      - CAPTURE_METHOD=http
      - SNAPSHOT_URL=http://host.docker.internal:8080/?action=snapshot
      - PING_HOST=host.docker.internal
    
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

**Deploy:**
```bash
docker-compose up -d
docker-compose logs -f
```

### 2. RTSP IP Camera

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  prusa-webcam-uploader:
    build: .
    container_name: prusa-webcam-uploader
    restart: unless-stopped
    
    environment:
      - FINGERPRINT=your_fingerprint_here
      - TOKEN=your_token_here
      - CAPTURE_METHOD=rtsp
      - RTSP_URL=rtsp://admin:password@192.168.1.100:554/stream
      - RTSP_TIMEOUT=15
      - PING_HOST=192.168.1.100
```

## 🏗️ Advanced Configurations

### 3. Production Deployment with Monitoring

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  prusa-webcam-uploader:
    build: .
    container_name: prusa-webcam-uploader
    restart: unless-stopped
    
    environment:
      - FINGERPRINT=${PRUSA_FINGERPRINT}
      - TOKEN=${PRUSA_TOKEN}
      - CAPTURE_METHOD=${CAPTURE_METHOD:-http}
      - SNAPSHOT_URL=${SNAPSHOT_URL:-http://host.docker.internal:8080/?action=snapshot}
      - DELAY_SECONDS=${DELAY_SECONDS:-10}
      - MAX_RETRIES=${MAX_RETRIES:-3}
      - TIMEOUT=${TIMEOUT:-30}
    
    # Resource limits
    deploy:
      resources:
        limits:
          memory: 128M
          cpus: '0.1'
        reservations:
          memory: 64M
    
    # Health check
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8080', timeout=5)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    
    # Logging
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    
    # Volumes for persistent logs
    volumes:
      - ./logs:/app/logs
    
    extra_hosts:
      - "host.docker.internal:host-gateway"

  # Optional: Log monitoring with Fluent Bit
  fluent-bit:
    image: fluent/fluent-bit:latest
    container_name: log-forwarder
    volumes:
      - ./logs:/var/log/app:ro
      - ./fluent-bit.conf:/fluent-bit/etc/fluent-bit.conf:ro
    depends_on:
      - prusa-webcam-uploader
```

**.env file:**
```bash
PRUSA_FINGERPRINT=abc123def456
PRUSA_TOKEN=xyz789uvw012
CAPTURE_METHOD=http
SNAPSHOT_URL=http://host.docker.internal:8080/?action=snapshot
DELAY_SECONDS=10
MAX_RETRIES=3
TIMEOUT=30
```

### 4. Multi-Camera Setup

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  # Camera 1 - HTTP
  prusa-cam1:
    build: .
    container_name: prusa-cam1
    restart: unless-stopped
    environment:
      - FINGERPRINT=${PRUSA_FINGERPRINT_1}
      - TOKEN=${PRUSA_TOKEN_1}
      - CAPTURE_METHOD=http
      - SNAPSHOT_URL=http://host.docker.internal:8080/?action=snapshot
    extra_hosts:
      - "host.docker.internal:host-gateway"
  
  # Camera 2 - RTSP
  prusa-cam2:
    build: .
    container_name: prusa-cam2
    restart: unless-stopped
    environment:
      - FINGERPRINT=${PRUSA_FINGERPRINT_2}
      - TOKEN=${PRUSA_TOKEN_2}
      - CAPTURE_METHOD=rtsp
      - RTSP_URL=rtsp://admin:password@192.168.1.101:554/stream
      - RTSP_TIMEOUT=20
  
  # Camera 3 - Different RTSP Camera
  prusa-cam3:
    build: .
    container_name: prusa-cam3
    restart: unless-stopped
    environment:
      - FINGERPRINT=${PRUSA_FINGERPRINT_3}
      - TOKEN=${PRUSA_TOKEN_3}
      - CAPTURE_METHOD=rtsp
      - RTSP_URL=rtsp://user:pass@192.168.1.102:554/onvif1
      - RTSP_TIMEOUT=15
```

## 🔧 Specialized Configurations

### 5. Development Setup with Volume Mounts

**docker-compose.dev.yml:**
```yaml
version: '3.8'

services:
  prusa-webcam-uploader-dev:
    build: 
      context: .
      dockerfile: Dockerfile.dev  # Development dockerfile
    container_name: prusa-dev
    restart: "no"  # Don't auto-restart in dev
    
    environment:
      - PYTHONLOGLEVEL=DEBUG
      - FINGERPRINT=test_fingerprint
      - TOKEN=test_token
      - CAPTURE_METHOD=http
      - SNAPSHOT_URL=http://host.docker.internal:8080/?action=snapshot
    
    # Mount source code for live editing
    volumes:
      - .:/app
      - /app/.venv  # Exclude virtual environment
    
    # Override entrypoint for development
    entrypoint: ["python", "-u", "prusa_webcam_uploader.py"]
    
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

**Dockerfile.dev:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install development dependencies
COPY requirements.txt test_requirements.txt ./
RUN pip install -r requirements.txt -r test_requirements.txt

# Development tools
RUN pip install black isort flake8 mypy

# Create non-root user
RUN groupadd -r prusa && useradd -r -g prusa -u 1000 prusa
RUN chown -R prusa:prusa /app
USER prusa

CMD ["python", "-u", "prusa_webcam_uploader.py"]
```

### 6. Raspberry Pi Deployment

**docker-compose.rpi.yml:**
```yaml
version: '3.8'

services:
  prusa-webcam-uploader:
    build:
      context: .
      dockerfile: Dockerfile.rpi
    container_name: prusa-webcam-uploader-rpi
    restart: unless-stopped
    
    environment:
      - FINGERPRINT=${PRUSA_FINGERPRINT}
      - TOKEN=${PRUSA_TOKEN}
      - CAPTURE_METHOD=http
      - SNAPSHOT_URL=http://localhost:8080/?action=snapshot
      - DELAY_SECONDS=15  # Slower on Pi
      - TIMEOUT=45        # Longer timeout on Pi
    
    # Use host networking on Pi for easier camera access
    network_mode: host
    
    # Pi-specific resource limits
    deploy:
      resources:
        limits:
          memory: 64M
          cpus: '0.2'
    
    # Access host camera devices
    devices:
      - /dev/video0:/dev/video0
    
    volumes:
      - /opt/vc:/opt/vc  # Pi GPU libraries
```

**Dockerfile.rpi:**
```dockerfile
FROM python:3.11-slim

# Install Pi-specific dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY prusa_webcam_uploader.py .

RUN groupadd -r prusa && useradd -r -g prusa -u 1000 prusa
RUN chown -R prusa:prusa /app
USER prusa

CMD ["python", "-u", "prusa_webcam_uploader.py"]
```

## 🎛️ Environment Configuration

### Complete Environment Variables Reference

```bash
# === Required Configuration ===
FINGERPRINT=your_prusa_fingerprint        # Required: Prusa Connect fingerprint
TOKEN=your_prusa_token                     # Required: Prusa Connect token

# === Capture Configuration ===
CAPTURE_METHOD=http                        # http or rtsp
SNAPSHOT_URL=http://localhost:8080/?action=snapshot  # For HTTP method
RTSP_URL=rtsp://user:pass@ip:554/stream   # For RTSP method
RTSP_TIMEOUT=10                           # RTSP connection timeout

# === Upload Configuration ===
HTTP_URL=https://webcam.connect.prusa3d.com/c/snapshot  # Prusa Connect endpoint
DELAY_SECONDS=10                          # Normal delay between uploads
LONG_DELAY_SECONDS=60                     # Delay after errors
MAX_RETRIES=3                             # HTTP request retries
TIMEOUT=30                                # HTTP request timeout

# === Network Configuration ===
PING_HOST=prusa                           # Host to ping for connectivity
```

## 🚀 Deployment Commands

### Build and Deploy
```bash
# Build the image
docker-compose build

# Deploy in background
docker-compose up -d

# View logs
docker-compose logs -f prusa-webcam-uploader

# Restart service
docker-compose restart prusa-webcam-uploader

# Stop and remove
docker-compose down
```

### Debugging
```bash
# Run interactively for debugging
docker-compose run --rm prusa-webcam-uploader bash

# Check container health
docker inspect --format='{{.State.Health.Status}}' prusa-webcam-uploader

# View resource usage
docker stats prusa-webcam-uploader

# Execute commands in running container
docker exec -it prusa-webcam-uploader python -c "
from prusa_webcam_uploader import PrusaWebcamUploader
uploader = PrusaWebcamUploader()
print('Config loaded successfully')
"
```

### Maintenance
```bash
# Update to latest version
git pull
docker-compose build --no-cache
docker-compose up -d

# View container logs
docker-compose logs --tail=100 -f

# Backup configuration
cp docker-compose.yml docker-compose.yml.backup
cp .env .env.backup

# Clean up old images
docker image prune -f
```

## 🔍 Troubleshooting

### Common Docker Issues

1. **Container exits immediately**
   ```bash
   docker-compose logs prusa-webcam-uploader
   # Check for configuration errors
   ```

2. **Can't reach mjpeg-streamer**
   ```bash
   # Test from container
   docker exec -it prusa-webcam-uploader curl -I http://host.docker.internal:8080
   ```

3. **RTSP connection fails**
   ```bash
   # Test RTSP URL
   docker run --rm -it jrottenberg/ffmpeg:latest \
     -i "rtsp://user:pass@ip:554/stream" -t 1 -f null -
   ```

4. **High memory usage**
   ```bash
   # Monitor resource usage
   docker stats prusa-webcam-uploader
   
   # Adjust memory limits in docker-compose.yml
   deploy:
     resources:
       limits:
         memory: 64M
   ```

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Networking Guide](https://docs.docker.com/network/)
- [Container Security Best Practices](https://docs.docker.com/engine/security/)
- [Docker on Raspberry Pi](https://docs.docker.com/engine/install/debian/)
