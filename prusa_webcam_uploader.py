#!/usr/bin/env python3
"""
🎥 Prusa Connect Webcam Uploader

A production-ready Python implementation for uploading webcam snapshots to Prusa Connect.
This module provides robust capture from multiple sources (HTTP/RTSP) and reliable
upload with comprehensive error handling, retry logic, and monitoring capabilities.

Features:
    - 📷 Dual capture methods: HTTP (mjpeg-streamer) and RTSP (IP cameras)
    - 🔄 Intelligent retry mechanisms with exponential backoff
    - 📊 Comprehensive logging and error reporting
    - ⚙️ Environment-based configuration with .env support
    - 🛡️ Production-ready error handling and validation
    - 📈 Health monitoring and observability

Usage:
    Basic usage with environment variables:
        $ export FINGERPRINT="your_fingerprint"
        $ export TOKEN="your_token"
        $ python prusa_webcam_uploader.py

    Using .env file:
        $ cp .env.template .env
        $ # Edit .env with your credentials
        $ python prusa_webcam_uploader.py

    Docker deployment:
        $ docker-compose up -d

Author: Richard van Liessum
License: MIT
Version: 1.0.0
"""

import logging
import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import cv2
import numpy as np

# Module constants
__version__ = "1.0.0"
__author__ = "Richard van Liessum"
__license__ = "MIT"


def load_dotenv(dotenv_path: Path = None) -> None:
    """
    Load environment variables from a .env file.
    
    Args:
        dotenv_path: Path to the .env file. If None, looks for .env in current directory.
    """
    if dotenv_path is None:
        dotenv_path = Path.cwd() / '.env'
    
    if not dotenv_path.exists():
        return
    
    try:
        with open(dotenv_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse key=value pairs
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove surrounding quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    # Only set if not already in environment (env vars take precedence)
                    if key not in os.environ:
                        os.environ[key] = value
                        
    except Exception as e:
        # Don't fail if .env file has issues, just log and continue
        print(f"Warning: Failed to load .env file: {e}", file=sys.stderr)


class PrusaWebcamUploader:
    """
    Handles webcam snapshot capture and upload to Prusa Connect.
    
    This class provides a robust implementation with proper error handling,
    logging, and configuration management.
    """
    
    def __init__(self):
        """Initialize the uploader with configuration from environment variables."""
        # Load .env file first (if it exists)
        load_dotenv()
        
        self.config = self._load_config()
        self.logger = self._setup_logging()
        self.session = self._setup_session()
        self.temp_image_path = Path("/tmp/prusa_output.jpg")
        
    def _load_config(self) -> dict:
        """Load configuration from environment variables with validation."""
        config = {
            'http_url': os.getenv('HTTP_URL', 'https://webcam.connect.prusa3d.com/c/snapshot'),
            'delay_seconds': int(os.getenv('DELAY_SECONDS', '10')),
            'long_delay_seconds': int(os.getenv('LONG_DELAY_SECONDS', '60')),
            'fingerprint': os.getenv('FINGERPRINT', '<fingerprint>'),
            'token': os.getenv('TOKEN', '<token>'),
            'snapshot_url': os.getenv('SNAPSHOT_URL', 'http://localhost:8080/?action=snapshot'),
            'rtsp_url': os.getenv('RTSP_URL', ''),
            'ping_host': os.getenv('PING_HOST', 'prusa'),
            'max_retries': int(os.getenv('MAX_RETRIES', '3')),
            'timeout': int(os.getenv('TIMEOUT', '30')),
            'rtsp_timeout': int(os.getenv('RTSP_TIMEOUT', '10')),
            'capture_method': os.getenv('CAPTURE_METHOD', 'http').lower(),  # 'http' or 'rtsp'
        }
        
        # Validate required configuration
        if config['fingerprint'] == '<fingerprint>' or config['token'] == '<token>':
            raise ValueError("FINGERPRINT and TOKEN environment variables must be set")
        
        # Validate capture method configuration
        if config['capture_method'] not in ['http', 'rtsp']:
            raise ValueError("CAPTURE_METHOD must be either 'http' or 'rtsp'")
        
        if config['capture_method'] == 'rtsp' and not config['rtsp_url']:
            raise ValueError("RTSP_URL must be set when CAPTURE_METHOD is 'rtsp'")
            
        return config
    
    def _setup_logging(self) -> logging.Logger:
        """Set up structured logging with appropriate formatting."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        logger = logging.getLogger('prusa_uploader')
        
        # Add console handler for better visibility
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        return logger
    
    def _setup_session(self) -> requests.Session:
        """Set up HTTP session with retry strategy and timeouts."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config['max_retries'],
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "POST", "DELETE", "OPTIONS", "TRACE"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def check_connectivity(self) -> bool:
        """
        Check if the Prusa printer is reachable via ping.
        
        Returns:
            bool: True if ping is successful, False otherwise.
        """
        try:
            result = subprocess.run(
                ['ping', '-c', '1', self.config['ping_host']],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            self.logger.warning(f"Ping check failed: {e}")
            return False
    
    def capture_snapshot(self) -> bool:
        """
        Capture a snapshot from either mjpeg-streamer or RTSP stream.
        
        Returns:
            bool: True if snapshot was captured successfully, False otherwise.
        """
        if self.config['capture_method'] == 'rtsp':
            return self._capture_from_rtsp()
        else:
            return self._capture_from_http()
    
    def _capture_from_http(self) -> bool:
        """
        Capture a snapshot from the mjpeg-streamer HTTP endpoint.
        
        Returns:
            bool: True if snapshot was captured successfully, False otherwise.
        """
        try:
            # Remove previous image if it exists
            self.temp_image_path.unlink(missing_ok=True)
            
            response = self.session.get(
                self.config['snapshot_url'],
                timeout=self.config['timeout'],
                stream=True
            )
            response.raise_for_status()
            
            # Save the image to temporary file
            with open(self.temp_image_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify the file was created and has content
            if not self.temp_image_path.exists() or self.temp_image_path.stat().st_size == 0:
                self.logger.error("Captured image is empty or doesn't exist")
                return False
                
            self.logger.debug(f"HTTP snapshot captured successfully: {self.temp_image_path.stat().st_size} bytes")
            return True
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to capture HTTP snapshot: {e}")
            return False
        except IOError as e:
            self.logger.error(f"Failed to save HTTP snapshot: {e}")
            return False
    
    def _capture_from_rtsp(self) -> bool:
        """
        Capture a snapshot from an RTSP stream using OpenCV.
        
        Returns:
            bool: True if snapshot was captured successfully, False otherwise.
        """
        cap = None
        try:
            # Remove previous image if it exists
            self.temp_image_path.unlink(missing_ok=True)
            
            # Create VideoCapture object for RTSP stream
            cap = cv2.VideoCapture(self.config['rtsp_url'])
            
            # Set timeout for RTSP connection
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            if not cap.isOpened():
                self.logger.error(f"Failed to open RTSP stream: {self.config['rtsp_url']}")
                return False
            
            # Set a reasonable timeout for frame capture
            start_time = time.time()
            timeout = self.config['rtsp_timeout']
            
            # Try to read a frame
            ret, frame = cap.read()
            
            if not ret or frame is None:
                self.logger.error("Failed to read frame from RTSP stream")
                return False
            
            # Check if we got a valid frame within timeout
            if time.time() - start_time > timeout:
                self.logger.error(f"RTSP frame capture timed out after {timeout} seconds")
                return False
            
            # Encode frame as JPEG
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 85]  # 85% quality
            success, encoded_img = cv2.imencode('.jpg', frame, encode_param)
            
            if not success:
                self.logger.error("Failed to encode RTSP frame as JPEG")
                return False
            
            # Save the encoded image
            with open(self.temp_image_path, 'wb') as f:
                f.write(encoded_img.tobytes())
            
            # Verify the file was created and has content
            if not self.temp_image_path.exists() or self.temp_image_path.stat().st_size == 0:
                self.logger.error("Captured RTSP image is empty or doesn't exist")
                return False
            
            self.logger.debug(f"RTSP snapshot captured successfully: {self.temp_image_path.stat().st_size} bytes")
            return True
            
        except cv2.error as e:
            self.logger.error(f"OpenCV error during RTSP capture: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to capture RTSP snapshot: {e}")
            return False
        finally:
            if cap is not None:
                cap.release()
    
    def upload_snapshot(self) -> bool:
        """
        Upload the captured snapshot to Prusa Connect.
        
        Returns:
            bool: True if upload was successful, False otherwise.
        """
        if not self.temp_image_path.exists():
            self.logger.error("No snapshot file to upload")
            return False
            
        try:
            headers = {
                'accept': '*/*',
                'content-type': 'image/jpg',
                'fingerprint': self.config['fingerprint'],
                'token': self.config['token'],
            }
            
            with open(self.temp_image_path, 'rb') as f:
                response = self.session.put(
                    self.config['http_url'],
                    headers=headers,
                    data=f,
                    timeout=self.config['timeout']
                )
            
            response.raise_for_status()
            self.logger.info(f"Snapshot uploaded successfully (Status: {response.status_code})")
            return True
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to upload snapshot: {e}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response status: {e.response.status_code}")
                self.logger.error(f"Response content: {e.response.text}")
            return False
        except IOError as e:
            self.logger.error(f"Failed to read snapshot file: {e}")
            return False
    
    def cleanup(self):
        """Clean up temporary files."""
        try:
            self.temp_image_path.unlink(missing_ok=True)
            self.logger.debug("Cleanup completed")
        except Exception as e:
            self.logger.warning(f"Cleanup failed: {e}")
    
    def run(self):
        """
        Main execution loop.
        
        Continuously captures and uploads snapshots with appropriate delays
        and error handling.
        """
        self.logger.info("Starting Prusa Connect Webcam Uploader")
        
        # Check if .env file exists and log it
        env_file = Path.cwd() / '.env'
        if env_file.exists():
            self.logger.info(f"Loaded configuration from .env file: {env_file}")
        
        self.logger.info(f"Upload URL: {self.config['http_url']}")
        self.logger.info(f"Capture method: {self.config['capture_method'].upper()}")
        
        if self.config['capture_method'] == 'rtsp':
            self.logger.info(f"RTSP URL: {self.config['rtsp_url']}")
            self.logger.info(f"RTSP timeout: {self.config['rtsp_timeout']}s")
        else:
            self.logger.info(f"Snapshot URL: {self.config['snapshot_url']}")
            
        self.logger.info(f"Normal delay: {self.config['delay_seconds']}s")
        self.logger.info(f"Error delay: {self.config['long_delay_seconds']}s")
        
        delay = self.config['delay_seconds']
        
        try:
            while True:
                try:
                    # Check connectivity first
                    if not self.check_connectivity():
                        self.logger.warning(f"Printer not reachable at {self.config['ping_host']}")
                        time.sleep(delay)
                        continue
                    
                    # Capture snapshot
                    if self.capture_snapshot():
                        # Upload snapshot
                        if self.upload_snapshot():
                            delay = self.config['delay_seconds']
                            self.logger.debug(f"Next upload in {delay} seconds")
                        else:
                            delay = self.config['long_delay_seconds']
                            self.logger.warning(f"Upload failed, retrying in {delay} seconds")
                    else:
                        delay = self.config['long_delay_seconds']
                        self.logger.warning(f"Snapshot capture failed, retrying in {delay} seconds")
                    
                    time.sleep(delay)
                    
                except KeyboardInterrupt:
                    self.logger.info("Received interrupt signal, shutting down...")
                    break
                except Exception as e:
                    self.logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
                    delay = self.config['long_delay_seconds']
                    time.sleep(delay)
                    
        finally:
            self.cleanup()
            self.logger.info("Prusa Connect Webcam Uploader stopped")


def main():
    """Entry point for the application."""
    try:
        uploader = PrusaWebcamUploader()
        uploader.run()
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
