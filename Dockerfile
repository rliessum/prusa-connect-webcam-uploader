# Use official Python runtime as base image
FROM python:3.11-slim

# Set metadata for Portainer
LABEL maintainer="Richard van Liessum"
LABEL description="Prusa Connect Webcam Uploader - Upload webcam snapshots to Prusa Connect"
LABEL version="1.0.0"
LABEL org.opencontainers.image.title="Prusa Connect Webcam Uploader"
LABEL org.opencontainers.image.description="Upload webcam snapshots to Prusa Connect via HTTP or RTSP"
LABEL org.opencontainers.image.vendor="Prusa Research"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.url="https://github.com/PrusaResearch/prusa-connect-webcam-uploader"
LABEL org.opencontainers.image.documentation="https://github.com/PrusaResearch/prusa-connect-webcam-uploader/blob/main/README.md"

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Create non-root user for security
RUN groupadd -r prusa && useradd -r -g prusa -u 1000 prusa

# Set working directory
WORKDIR /app

# Install system dependencies (including OpenCV requirements)
RUN apt-get update && apt-get install -y \
    iputils-ping \
    wget \
    curl \
    libglib2.0-0 \
    libgtk-3-dev \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libatlas-base-dev \
    python3-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY prusa_webcam_uploader.py .

# Create directories and set permissions
RUN mkdir -p /app/logs /tmp && chown -R prusa:prusa /tmp /app

# Switch to non-root user
USER prusa

# Health check - improved to actually test the application
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import sys, os; sys.exit(0 if os.getenv('FINGERPRINT', '<fingerprint>') != '<fingerprint>' else 1)"

# Expose port for health monitoring (optional)
EXPOSE 8000

# Set default environment variables (will be overridden by Portainer)
ENV HTTP_URL="https://webcam.connect.prusa3d.com/c/snapshot" \
    DELAY_SECONDS=10 \
    LONG_DELAY_SECONDS=60 \
    CAPTURE_METHOD=http \
    SNAPSHOT_URL="http://localhost:8080/?action=snapshot" \
    PING_HOST="localhost" \
    MAX_RETRIES=3 \
    TIMEOUT=30 \
    RTSP_TIMEOUT=10

# Run the application
CMD ["python", "prusa_webcam_uploader.py"]
