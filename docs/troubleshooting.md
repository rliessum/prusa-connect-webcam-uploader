# 🔍 Troubleshooting Guide

This guide covers common issues and their solutions. If you don't find your issue here, please check our [GitHub Issues](https://github.com/rliessum/prusa-connect-webcam-uploader/issues).

## 🚨 Common Issues

### 1. Authentication Errors

#### ❌ Problem: `401 Unauthorized` or `403 Forbidden`
```
ERROR: Upload failed: 401 Client Error: Unauthorized
```

#### ✅ Solutions:
1. **Verify credentials**:
   ```bash
   # Check your .env file or environment variables
   echo $FINGERPRINT
   echo $TOKEN
   ```

2. **Get fresh credentials**:
   - Log into [Prusa Connect](https://connect.prusa3d.com)
   - Go to your printer → Camera settings
   - Copy the latest `FINGERPRINT` and `TOKEN`

3. **Check token format**:
   - Tokens should be alphanumeric strings
   - No spaces or special characters
   - Case-sensitive

---

### 2. Network Connection Issues

#### ❌ Problem: `Connection refused` or `Network unreachable`
```
ERROR: Failed to capture image: Connection refused
```

#### ✅ Solutions:

**For HTTP/mjpeg-streamer:**
1. **Test connectivity**:
   ```bash
   # Test direct access
   curl -I http://localhost:8080/?action=snapshot
   
   # For Docker
   curl -I http://host.docker.internal:8080/?action=snapshot
   ```

2. **Check mjpeg-streamer status**:
   ```bash
   # Check if mjpeg-streamer is running
   ps aux | grep mjpeg
   netstat -tlnp | grep :8080
   ```

3. **Fix Docker networking**:
   ```yaml
   # In docker-compose.yml, ensure:
   extra_hosts:
     - "host.docker.internal:host-gateway"
   ```

**For RTSP:**
1. **Test RTSP URL**:
   ```bash
   # Test with VLC or ffmpeg
   ffmpeg -i "rtsp://username:password@ip:554/stream" -f null -
   ```

2. **Check camera settings**:
   - Ensure RTSP is enabled on camera
   - Verify username/password
   - Check port number (usually 554)

---

### 3. Docker Issues

#### ❌ Problem: Container won't start
```
ERROR: Container exits immediately
```

#### ✅ Solutions:
1. **Check logs**:
   ```bash
   docker-compose logs prusa-webcam-uploader
   ```

2. **Verify environment variables**:
   ```bash
   # Check docker-compose.yml has all required vars
   docker-compose config
   ```

3. **Test without Docker first**:
   ```bash
   # Run directly to isolate Docker issues
   python prusa_webcam_uploader.py
   ```

#### ❌ Problem: `host.docker.internal` not resolving
```
ERROR: Could not resolve host: host.docker.internal
```

#### ✅ Solutions:
1. **Add host mapping**:
   ```yaml
   # In docker-compose.yml
   extra_hosts:
     - "host.docker.internal:host-gateway"
   ```

2. **Use host IP directly**:
   ```bash
   # Find your host IP
   ip route show default | awk '/default/ {print $3}'
   
   # Use in SNAPSHOT_URL
   SNAPSHOT_URL=http://192.168.1.100:8080/?action=snapshot
   ```

---

### 4. Image Capture Issues

#### ❌ Problem: `Failed to capture image` or `Empty response`
```
WARNING: Failed to capture image, retrying...
```

#### ✅ Solutions:

**For HTTP capture:**
1. **Test URL manually**:
   ```bash
   wget http://localhost:8080/?action=snapshot -O test.jpg
   ls -la test.jpg  # Should be > 0 bytes
   ```

2. **Check mjpeg-streamer configuration**:
   ```bash
   # Common mjpeg-streamer command
   mjpg_streamer -i "input_uvc.so -d /dev/video0" -o "output_http.so -p 8080"
   ```

**For RTSP capture:**
1. **Test with OpenCV**:
   ```python
   import cv2
   cap = cv2.VideoCapture('rtsp://user:pass@ip:554/stream')
   ret, frame = cap.read()
   print(f"Capture successful: {ret}")
   ```

2. **Adjust timeout**:
   ```bash
   # Increase RTSP timeout
   export RTSP_TIMEOUT=30
   ```

---

### 5. Configuration Issues

#### ❌ Problem: `Configuration validation failed`
```
ERROR: Required environment variable not set: FINGERPRINT
```

#### ✅ Solutions:
1. **Check .env file**:
   ```bash
   # Ensure .env exists and has correct format
   cat .env
   
   # Should look like:
   # FINGERPRINT=abc123...
   # TOKEN=xyz789...
   ```

2. **Verify environment variables**:
   ```bash
   # Check all required vars are set
   env | grep -E "(FINGERPRINT|TOKEN|CAPTURE_METHOD)"
   ```

3. **Check file permissions**:
   ```bash
   # .env should be readable
   ls -la .env
   chmod 644 .env
   ```

---

## 🛠️ Diagnostic Commands

### System Information
```bash
# Check Python version
python --version

# Check Docker version
docker --version
docker-compose --version

# Check network connectivity
ping google.com
```

### Application Diagnostics
```bash
# Run with debug logging
export PYTHONLOGLEVEL=DEBUG
python prusa_webcam_uploader.py

# Check configuration
python -c "
from prusa_webcam_uploader import PrusaWebcamUploader
uploader = PrusaWebcamUploader()
print('Config loaded successfully')
"
```

### Network Diagnostics
```bash
# Test HTTP endpoint
curl -v http://localhost:8080/?action=snapshot

# Test RTSP (requires ffmpeg)
ffmpeg -rtsp_transport tcp -i "rtsp://ip:554/stream" -t 1 -f null -

# Check port availability
netstat -tlnp | grep 8080
```

---

## 🚨 Getting More Help

### 1. Enable Debug Logging
```bash
export PYTHONLOGLEVEL=DEBUG
python prusa_webcam_uploader.py
```

### 2. Collect System Information
```bash
# Create a diagnostic report
echo "=== System Info ===" > debug.txt
uname -a >> debug.txt
python --version >> debug.txt
docker --version >> debug.txt

echo -e "\n=== Configuration ===" >> debug.txt
env | grep -E "(FINGERPRINT|TOKEN|CAPTURE|RTSP|HTTP)" | sed 's/TOKEN=.*/TOKEN=***/' >> debug.txt

echo -e "\n=== Network Tests ===" >> debug.txt
curl -I http://localhost:8080 >> debug.txt 2>&1
```

### 3. Create an Issue
If you can't resolve your issue:

1. Use our [issue templates](https://github.com/rliessum/prusa-connect-webcam-uploader/issues/new/choose)
2. Include relevant logs (sanitized)
3. Provide system information
4. Describe what you've tried

---

## 📚 Additional Resources

- [Prusa Connect Help](https://help.prusa3d.com/category/prusa-connect_327)
- [mjpeg-streamer Documentation](https://github.com/jacksonliam/mjpg-streamer)
- [Docker Networking Guide](https://docs.docker.com/network/)
- [OpenCV RTSP Documentation](https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html)
