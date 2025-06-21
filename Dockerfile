# Use official Python runtime as base image
FROM python:3.11-slim

# Set metadata
LABEL maintainer="your-email@example.com"
LABEL description="Prusa Connect Webcam Uploader"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user for security
RUN groupadd -r prusa && useradd -r -g prusa -u 1000 prusa

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    iputils-ping \
    wget \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgthread-2.0-0 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY prusa_webcam_uploader.py .

# Create temp directory and set permissions
RUN mkdir -p /tmp && chown -R prusa:prusa /tmp /app

# Switch to non-root user
USER prusa

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Set default environment variables (can be overridden)
ENV HTTP_URL="https://webcam.connect.prusa3d.com/c/snapshot" \
    DELAY_SECONDS=10 \
    LONG_DELAY_SECONDS=60 \
    SNAPSHOT_URL="http://localhost:8080/?action=snapshot" \
    PING_HOST="prusa" \
    MAX_RETRIES=3 \
    TIMEOUT=30

# Run the application
CMD ["python", "prusa_webcam_uploader.py"]
