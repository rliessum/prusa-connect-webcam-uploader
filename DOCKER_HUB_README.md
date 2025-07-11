# 🐳 Docker Hub Deployment Guide

The Prusa Connect Webcam Uploader is now available on Docker Hub at `rliessum/prusa-webcam-uploader`.

## 📦 Available Images

### Tags
- `latest` - Latest stable version
- `1.0.0` - Version 1.0.0 (current stable)

### Platforms
- `linux/amd64` - Intel/AMD 64-bit processors
- `linux/arm64` - ARM 64-bit processors (Raspberry Pi 4, Apple Silicon, etc.)

## 🚀 Quick Start

### Pull and Run

```bash
# Pull the latest image
docker pull rliessum/prusa-webcam-uploader:latest

# Run with environment variables
docker run -d \
  --name prusa-webcam-uploader \
  --restart unless-stopped \
  -e FINGERPRINT=your_fingerprint_here \
  -e TOKEN=your_token_here \
  -e CAPTURE_METHOD=rtsp \
  -e RTSP_URL=rtsp://admin:password@192.168.1.100:554/stream \
  -e PING_HOST=192.168.1.100 \
  rliessum/prusa-webcam-uploader:latest
```

### Using Docker Compose

```yaml
version: '3.8'

services:
  prusa-webcam-uploader:
    image: rliessum/prusa-webcam-uploader:latest
    container_name: prusa-webcam-uploader
    restart: unless-stopped
    environment:
      - FINGERPRINT=your_fingerprint_here
      - TOKEN=your_token_here
      - CAPTURE_METHOD=rtsp
      - RTSP_URL=rtsp://admin:password@192.168.1.100:554/stream
      - PING_HOST=192.168.1.100
    volumes:
      - prusa-logs:/app/logs

volumes:
  prusa-logs:
```

## 🔧 Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `FINGERPRINT` | Your Prusa Connect fingerprint | `a1b2c3d4e5f6789` |
| `TOKEN` | Your Prusa Connect token | `xyz123abc456def789` |

### Optional Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CAPTURE_METHOD` | `http` | `http` or `rtsp` |
| `RTSP_URL` | - | RTSP stream URL |
| `SNAPSHOT_URL` | `http://localhost:8080/?action=snapshot` | HTTP snapshot URL |
| `PING_HOST` | `localhost` | Host to ping for connectivity check |
| `DELAY_SECONDS` | `10` | Normal delay between uploads |
| `LONG_DELAY_SECONDS` | `60` | Delay after errors |
| `TIMEOUT` | `30` | HTTP request timeout |
| `RTSP_TIMEOUT` | `10` | RTSP connection timeout |
| `MAX_RETRIES` | `3` | Maximum retry attempts |
| `PYTHONLOGLEVEL` | `INFO` | Logging level |

## 📹 Camera Configuration Examples

### RTSP IP Camera
```bash
docker run -d \
  --name prusa-webcam-uploader \
  -e FINGERPRINT=your_fingerprint \
  -e TOKEN=your_token \
  -e CAPTURE_METHOD=rtsp \
  -e RTSP_URL=rtsp://admin:password@192.168.1.150:554/stream \
  -e PING_HOST=192.168.1.150 \
  rliessum/prusa-webcam-uploader:latest
```

### mjpeg-streamer (Raspberry Pi)
```bash
docker run -d \
  --name prusa-webcam-uploader \
  -e FINGERPRINT=your_fingerprint \
  -e TOKEN=your_token \
  -e CAPTURE_METHOD=http \
  -e SNAPSHOT_URL=http://192.168.1.200:8080/?action=snapshot \
  -e PING_HOST=192.168.1.200 \
  rliessum/prusa-webcam-uploader:latest
```

### Local mjpeg-streamer
```bash
docker run -d \
  --name prusa-webcam-uploader \
  --add-host host.docker.internal:host-gateway \
  -e FINGERPRINT=your_fingerprint \
  -e TOKEN=your_token \
  -e CAPTURE_METHOD=http \
  -e SNAPSHOT_URL=http://host.docker.internal:8080/?action=snapshot \
  -e PING_HOST=host.docker.internal \
  rliessum/prusa-webcam-uploader:latest
```

## 🔍 Monitoring

### View Logs
```bash
docker logs prusa-webcam-uploader
```

### Follow Logs
```bash
docker logs -f prusa-webcam-uploader
```

### Check Container Status
```bash
docker ps | grep prusa-webcam-uploader
```

### Health Check
```bash
docker inspect prusa-webcam-uploader | grep Health -A 10
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Container exits immediately
```bash
# Check logs for errors
docker logs prusa-webcam-uploader

# Common causes:
# - Missing FINGERPRINT or TOKEN
# - Invalid RTSP_URL format
# - Network connectivity issues
```

#### 2. "Printer not reachable"
```bash
# Set correct PING_HOST
-e PING_HOST=192.168.1.100  # Your actual printer/camera IP
```

#### 3. RTSP connection fails
```bash
# Verify RTSP URL format:
# Generic: rtsp://username:password@ip:554/stream
# Hikvision: rtsp://admin:pass@ip:554/Streaming/Channels/101
# Dahua: rtsp://admin:pass@ip:554/cam/realmonitor?channel=1&subtype=0
```

### Debug Mode
```bash
docker run -d \
  --name prusa-webcam-uploader \
  -e FINGERPRINT=your_fingerprint \
  -e TOKEN=your_token \
  -e PYTHONLOGLEVEL=DEBUG \
  # ... other environment variables
  rliessum/prusa-webcam-uploader:latest
```

## 🔒 Security

### Best Practices
- ✅ Use strong passwords for camera access
- ✅ Keep Prusa Connect tokens secure
- ✅ Run containers as non-root user (default)
- ✅ Use read-only file systems where possible
- ❌ Don't expose unnecessary ports
- ❌ Don't use default camera passwords

### Network Security
- Place cameras on isolated VLAN if possible
- Use firewall rules to restrict access
- Enable HTTPS/TLS for camera streams when available

## 📊 Resource Usage

### Default Limits
- **Memory**: 256MB limit, 128MB reservation
- **CPU**: 0.2 cores limit, 0.1 cores reservation
- **Storage**: ~1.4GB image size

### Custom Limits
```bash
docker run -d \
  --name prusa-webcam-uploader \
  --memory=512m \
  --cpus=0.5 \
  # ... environment variables
  rliessum/prusa-webcam-uploader:latest
```

## 🔄 Updates

### Pull Latest Version
```bash
docker pull rliessum/prusa-webcam-uploader:latest
docker stop prusa-webcam-uploader
docker rm prusa-webcam-uploader
# Re-run with your configuration
```

### Using Docker Compose
```bash
docker-compose pull
docker-compose up -d
```

## 📞 Support

### Getting Help
1. Check container logs: `docker logs prusa-webcam-uploader`
2. Verify configuration against this guide
3. Test camera access independently
4. Check network connectivity

### Log Analysis
Look for these patterns:
- `✅ Snapshot uploaded successfully` = Working correctly
- `❌ Failed to capture snapshot` = Camera issue
- `❌ Failed to upload snapshot` = Network/Prusa Connect issue
- `⚠️ Printer not reachable` = Network connectivity issue

## 🎯 Complete Example

Here's a complete working example:

```bash
docker run -d \
  --name prusa-webcam-uploader \
  --restart unless-stopped \
  --memory=256m \
  --cpus=0.2 \
  -e FINGERPRINT=a1b2c3d4e5f6789 \
  -e TOKEN=xyz123abc456def789 \
  -e CAPTURE_METHOD=rtsp \
  -e RTSP_URL=rtsp://admin:camera123@192.168.1.150:554/stream \
  -e PING_HOST=192.168.1.150 \
  -e DELAY_SECONDS=10 \
  -e PYTHONLOGLEVEL=INFO \
  -v prusa-logs:/app/logs \
  rliessum/prusa-webcam-uploader:latest
```

Replace the credentials and IP addresses with your actual values! 