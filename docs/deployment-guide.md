# 🚀 Deployment Guide

Complete deployment guide for the Prusa Connect Webcam Uploader with various deployment scenarios.

## 📋 Quick Start

### Basic Deployment
```bash
# Clone the repository
git clone https://github.com/rliessum/prusa-connect-webcam-uploader.git
cd prusa-connect-webcam-uploader

# Configure credentials
cp .env.template .env
# Edit .env with your Prusa Connect credentials

# Deploy with Docker Compose
docker-compose up -d
```

## 🐋 Docker Deployment Options

### 1. Standard Deployment (docker-compose.yml)
For most users, the standard `docker-compose.yml` provides everything needed:

```yaml
version: '3.8'

services:
  prusa-webcam-uploader:
    image: rliessum/prusa-webcam-uploader:latest
    container_name: prusa-webcam-uploader
    restart: unless-stopped
    
    environment:
      - FINGERPRINT=${FINGERPRINT}
      - TOKEN=${TOKEN}
      - CAPTURE_METHOD=${CAPTURE_METHOD:-http}
      - SNAPSHOT_URL=${SNAPSHOT_URL:-http://host.docker.internal:8080/?action=snapshot}
      - PING_HOST=${PING_HOST:-host.docker.internal}
    
    extra_hosts:
      - "host.docker.internal:host-gateway"
    
    volumes:
      - prusa-logs:/app/logs
    
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 60s
      timeout: 10s
      retries: 3

volumes:
  prusa-logs:
```

### 2. Development Deployment
For development with live code editing, use the development override:

```bash
# Use development configuration
docker-compose -f docker-compose.yml -f docs/development-override.yml up -d
```

### 3. Portainer Deployment
For Portainer users, use the specialized configuration:

```bash
# Copy the Portainer configuration
cp docs/portainer-deployment.yml docker-compose.portainer.yml

# Deploy in Portainer using the stack editor
```

## 🎥 Camera Configuration

### HTTP Capture (mjpeg-streamer)
```bash
# Environment variables
CAPTURE_METHOD=http
SNAPSHOT_URL=http://localhost:8080/?action=snapshot
PING_HOST=localhost
```

### RTSP Capture (IP Cameras)
```bash
# Environment variables
CAPTURE_METHOD=rtsp
RTSP_URL=rtsp://admin:password@192.168.1.100:554/stream
RTSP_TIMEOUT=10
PING_HOST=192.168.1.100
```

## 🔧 Advanced Configurations

### Multi-Camera Setup
```yaml
version: '3.8'

services:
  prusa-cam1:
    image: rliessum/prusa-webcam-uploader:latest
    container_name: prusa-cam1
    environment:
      - FINGERPRINT=${FINGERPRINT_1}
      - TOKEN=${TOKEN_1}
      - CAPTURE_METHOD=http
      - SNAPSHOT_URL=http://192.168.1.100:8080/?action=snapshot
      - PING_HOST=192.168.1.100
  
  prusa-cam2:
    image: rliessum/prusa-webcam-uploader:latest
    container_name: prusa-cam2
    environment:
      - FINGERPRINT=${FINGERPRINT_2}
      - TOKEN=${TOKEN_2}
      - CAPTURE_METHOD=rtsp
      - RTSP_URL=rtsp://admin:pass@192.168.1.101:554/stream
      - PING_HOST=192.168.1.101
```

### Production Deployment with Monitoring
```yaml
version: '3.8'

services:
  prusa-webcam-uploader:
    image: rliessum/prusa-webcam-uploader:latest
    container_name: prusa-webcam-uploader
    restart: unless-stopped
    
    environment:
      - FINGERPRINT=${FINGERPRINT}
      - TOKEN=${TOKEN}
      - CAPTURE_METHOD=${CAPTURE_METHOD}
      - RTSP_URL=${RTSP_URL}
      - DELAY_SECONDS=${DELAY_SECONDS:-10}
      - MAX_RETRIES=${MAX_RETRIES:-3}
      - TIMEOUT=${TIMEOUT:-30}
    
    deploy:
      resources:
        limits:
          memory: 128M
          cpus: '0.1'
        reservations:
          memory: 64M
    
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8080', timeout=5)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    
    volumes:
      - ./logs:/app/logs
    
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

## 🖥️ Unraid NAS Deployment

Unraid runs Docker natively, making it a great platform for this uploader.

### Using Docker Compose on Unraid

Install the **Docker Compose** plugin from Community Applications if you haven't already.

```bash
# Clone to Unraid appdata
cd /mnt/user/appdata
git clone https://github.com/rliessum/prusa-connect-webcam-uploader.git
cd prusa-connect-webcam-uploader

# Configure
cp .env.template .env
nano .env  # Fill in FINGERPRINT, TOKEN, and camera settings

# Build and deploy
docker compose up -d --build

# View logs
docker compose logs -f prusa-webcam-uploader
```

### Using the Unraid Docker UI

1. First build the image on your Unraid server via SSH/terminal:
   ```bash
   cd /mnt/user/appdata
   git clone https://github.com/rliessum/prusa-connect-webcam-uploader.git
   cd prusa-connect-webcam-uploader
   docker build -t rliessum/prusa-webcam-uploader:latest .
   ```

2. In the Unraid web UI, go to **Docker** → **Add Container** and configure:

   | Field | Value |
   |-------|-------|
   | Name | `prusa-webcam-uploader` |
   | Repository | `rliessum/prusa-webcam-uploader:latest` |
   | Network Type | `bridge` |
   | Extra Parameters | `--restart unless-stopped` |

3. Add environment variables:

   | Variable | Value |
   |----------|-------|
   | `FINGERPRINT` | Your Prusa Connect fingerprint |
   | `TOKEN` | Your Prusa Connect token |
   | `CAPTURE_METHOD` | `http` or `rtsp` |
   | `SNAPSHOT_URL` | `http://<CAMERA_IP>:8080/?action=snapshot` |
   | `RTSP_URL` | `rtsp://user:pass@<CAMERA_IP>:554/stream` |
   | `PING_HOST` | Your printer's IP address |
   | `DELAY_SECONDS` | `10` |

4. Optionally add a volume mapping for logs:
   - Container path: `/app/logs`
   - Host path: `/mnt/user/appdata/prusa-webcam-uploader/logs`

5. Click **Apply**.

### Unraid-Specific Notes

- **Use IP addresses**: On Unraid, `host.docker.internal` may not resolve. Use the actual IP address of your webcam/printer instead (e.g., `192.168.1.x`).
- **Bridge networking**: The default bridge network works for most setups since the uploader connects to external IPs (camera, Prusa Connect cloud).
- **Updating**: To update, SSH into Unraid and re-run `git pull && docker compose up -d --build` in the appdata directory, or rebuild the image and restart the container via the UI.

## 🍓 Raspberry Pi Deployment

For Raspberry Pi deployments, use host networking for easier camera access:

```yaml
version: '3.8'

services:
  prusa-webcam-uploader:
    image: rliessum/prusa-webcam-uploader:latest
    container_name: prusa-webcam-uploader
    restart: unless-stopped
    
    environment:
      - FINGERPRINT=${FINGERPRINT}
      - TOKEN=${TOKEN}
      - CAPTURE_METHOD=http
      - SNAPSHOT_URL=http://localhost:8080/?action=snapshot
      - DELAY_SECONDS=15  # Slower on Pi
      - TIMEOUT=45        # Longer timeout on Pi
    
    network_mode: host
    
    deploy:
      resources:
        limits:
          memory: 64M
          cpus: '0.2'
    
    devices:
      - /dev/video0:/dev/video0
    
    volumes:
      - /opt/vc:/opt/vc  # Pi GPU libraries
```

## 🔍 Troubleshooting

### Common Issues

1. **Container exits immediately**
   ```bash
   docker-compose logs prusa-webcam-uploader
   # Check for missing FINGERPRINT or TOKEN
   ```

2. **Can't reach mjpeg-streamer**
   ```bash
   # Test connectivity
   docker exec -it prusa-webcam-uploader curl -I http://host.docker.internal:8080
   ```

3. **RTSP connection fails**
   ```bash
   # Test RTSP URL with ffmpeg
   docker run --rm -it jrottenberg/ffmpeg:latest \
     -i "rtsp://user:pass@ip:554/stream" -t 1 -f null -
   ```

### Debug Mode
```bash
# Enable debug logging
docker-compose run --rm -e PYTHONLOGLEVEL=DEBUG prusa-webcam-uploader
```

## 📊 Monitoring

### Health Checks
```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' prusa-webcam-uploader

# View resource usage
docker stats prusa-webcam-uploader
```

### Logs
```bash
# View logs
docker-compose logs -f prusa-webcam-uploader

# Follow logs with timestamps
docker-compose logs -f -t prusa-webcam-uploader
```

## 🔄 Updates

### Update to Latest Version
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose build --no-cache
docker-compose up -d

# Clean up old images
docker image prune -f
```

### Backup Configuration
```bash
# Backup your configuration
cp docker-compose.yml docker-compose.yml.backup
cp .env .env.backup
```

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Networking Guide](https://docs.docker.com/network/)
- [Container Security Best Practices](https://docs.docker.com/engine/security/)
- [Docker on Raspberry Pi](https://docs.docker.com/engine/install/debian/)
- [Unraid Docker Management](https://docs.unraid.net/unraid-os/manual/docker-management/)
