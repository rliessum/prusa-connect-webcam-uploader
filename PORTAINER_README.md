# 🐋 Portainer Deployment Guide

This guide will help you deploy the Prusa Connect Webcam Uploader using Portainer.

## 📋 Prerequisites

- Portainer installed and running
- Docker host with Portainer agent (if using Portainer Business)
- Your Prusa Connect credentials (fingerprint and token)
- Camera/webcam accessible via HTTP or RTSP

## 🚀 Quick Deployment

### Method 1: Using Portainer Stacks (Recommended)

1. **Log into Portainer**
2. **Navigate to Stacks** → **Add stack**
3. **Name your stack**: `prusa-webcam-uploader`
4. **Copy and paste** the content from `docker-compose.portainer.yml`
5. **Configure environment variables** (see below)
6. **Click "Deploy the stack"**

### Method 2: Using Portainer App Templates

If you have custom app templates enabled:

1. **Navigate to App Templates**
2. **Search for "Prusa"** or create a custom template
3. **Configure the template** with your parameters
4. **Deploy**

## ⚙️ Configuration

### Required Environment Variables

Set these in Portainer's **Environment variables** section:

```bash
# 🔑 REQUIRED: Your Prusa Connect credentials
FINGERPRINT=your_actual_fingerprint_here
TOKEN=your_actual_token_here

# 📷 Choose capture method
CAPTURE_METHOD=rtsp  # or 'http' for mjpeg-streamer

# 📹 For RTSP cameras (IP cameras)
RTSP_URL=rtsp://admin:password@192.168.1.100:554/stream
PING_HOST=192.168.1.100

# 🌐 For HTTP cameras (mjpeg-streamer)
SNAPSHOT_URL=http://192.168.1.200:8080/?action=snapshot
PING_HOST=192.168.1.200
```

### 🔑 Getting Your Prusa Connect Credentials

1. Go to [Prusa Connect](https://connect.prusa3d.com)
2. Log in to your account
3. Navigate to your printer
4. Go to **Camera** settings
5. Copy your **FINGERPRINT** and **TOKEN**

### 📹 Camera Configuration Examples

#### RTSP IP Camera
```bash
CAPTURE_METHOD=rtsp
RTSP_URL=rtsp://admin:mypassword@192.168.1.150:554/stream
PING_HOST=192.168.1.150
```

#### mjpeg-streamer on Raspberry Pi
```bash
CAPTURE_METHOD=http
SNAPSHOT_URL=http://192.168.1.200:8080/?action=snapshot
PING_HOST=192.168.1.200
```

#### Local mjpeg-streamer (same machine)
```bash
CAPTURE_METHOD=http
SNAPSHOT_URL=http://host.docker.internal:8080/?action=snapshot
PING_HOST=host.docker.internal
```

## 📊 Monitoring

### Health Checks

The container includes built-in health checks:
- **Healthy**: Green dot in Portainer
- **Unhealthy**: Red dot - check logs for issues

### Viewing Logs

1. **Go to Containers** in Portainer
2. **Click on** `prusa-webcam-uploader`
3. **View Logs** tab
4. **Look for**:
   - ✅ `Snapshot uploaded successfully (Status: 200)`
   - ❌ Error messages for troubleshooting

### Volume Management

Logs are stored in a persistent volume:
- **Volume name**: `prusa-webcam-logs`
- **Mount point**: `/app/logs`
- **Access**: Portainer → Volumes → Browse

## 🔧 Troubleshooting

### Common Issues

#### 1. "Printer not reachable"
```bash
# Fix: Set correct IP address
PING_HOST=192.168.1.100  # Your actual printer/camera IP
```

#### 2. "Failed to capture RTSP snapshot"
```bash
# Check RTSP URL format:
RTSP_URL=rtsp://username:password@camera_ip:554/stream

# Common RTSP paths:
# Hikvision: rtsp://admin:pass@ip:554/Streaming/Channels/101
# Dahua: rtsp://admin:pass@ip:554/cam/realmonitor?channel=1&subtype=0
# Generic: rtsp://admin:pass@ip:554/stream
```

#### 3. "FINGERPRINT and TOKEN environment variables must be set"
```bash
# Ensure you've set both variables in Portainer:
FINGERPRINT=your_actual_fingerprint
TOKEN=your_actual_token
```

#### 4. Container keeps restarting
- Check environment variables are set correctly
- Verify camera URL is accessible
- Check logs for specific error messages

### Debug Mode

Enable debug logging:
```bash
PYTHONLOGLEVEL=DEBUG
```

## 🏗️ Advanced Configuration

### Resource Management

Default resource limits:
```yaml
resources:
  limits:
    memory: 256M
    cpus: '0.2'
  reservations:
    memory: 128M
    cpus: '0.1'
```

### Custom Networks

For advanced networking, you can:
1. Create a custom network in Portainer
2. Modify the stack to use your network
3. Configure firewall rules as needed

### Multiple Cameras

To run multiple instances:
1. Create separate stacks for each camera
2. Use different container names
3. Configure different environment variables

## 🔒 Security

### Best Practices

- ✅ Use strong passwords for camera access
- ✅ Keep Prusa Connect tokens secure
- ✅ Run containers as non-root user (default)
- ✅ Use read-only file systems where possible
- ✅ Regular token rotation
- ❌ Don't expose unnecessary ports
- ❌ Don't use default camera passwords

### Network Security

- Place cameras on isolated VLAN if possible
- Use firewall rules to restrict access
- Enable HTTPS/TLS for camera streams when available

## 🔄 Updates

### Updating the Container

1. **Pull latest image**:
   ```bash
   docker pull prusa-webcam-uploader:latest
   ```

2. **In Portainer**:
   - Go to **Stacks**
   - Click **Edit stack**
   - Click **Update the stack**

3. **Or rebuild**:
   - **Stacks** → **prusa-webcam-uploader**
   - **Editor** tab
   - Click **Update the stack**

## 📞 Support

If you need help:

1. **Check logs** in Portainer first
2. **Verify configuration** against this guide
3. **Test camera access** independently
4. **Check network connectivity**

### Log Analysis

Look for these patterns:
- `✅ Snapshot uploaded successfully` = Working correctly
- `❌ Failed to capture snapshot` = Camera issue
- `❌ Failed to upload snapshot` = Network/Prusa Connect issue
- `⚠️ Printer not reachable` = Network connectivity issue

## 🎯 Example Complete Configuration

Here's a complete working example for Portainer environment variables:

```bash
# Prusa Connect credentials
FINGERPRINT=a1b2c3d4e5f6789
TOKEN=xyz123abc456def789

# RTSP camera configuration
CAPTURE_METHOD=rtsp
RTSP_URL=rtsp://admin:camera123@192.168.1.150:554/stream
RTSP_TIMEOUT=10

# Network settings
PING_HOST=192.168.1.150

# Timing settings
DELAY_SECONDS=10
LONG_DELAY_SECONDS=60
TIMEOUT=30

# Debug (optional)
PYTHONLOGLEVEL=INFO
```

Copy this template and replace with your actual values! 