#!/usr/bin/env python3
"""
Test suite for Prusa Connect Webcam Uploader

This module contains comprehensive test cases for all functionality
including HTTP/RTSP capture, upload, configuration, and error handling.
"""

import os
import sys
import tempfile
import time
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock
import pytest
import responses
import numpy as np
import requests

# Try to import OpenCV, use mock if not available
try:
    import cv2
except ImportError:
    from test_cv2_mock import cv2

# Add the parent directory to the path to import the main module
sys.path.insert(0, str(Path(__file__).parent))

from prusa_webcam_uploader import (
    PrusaWebcamUploader,
    load_dotenv,
    main
)


class TestLoadDotenv:
    """Test cases for the load_dotenv function."""
    
    def test_load_dotenv_nonexistent_file(self, tmp_path):
        """Test loading from a non-existent .env file."""
        env_file = tmp_path / "nonexistent.env"
        # Should not raise an exception
        load_dotenv(env_file)
    
    def test_load_dotenv_valid_file(self, tmp_path, monkeypatch):
        """Test loading a valid .env file."""
        env_file = tmp_path / ".env"
        env_content = """
# This is a comment
TEST_VAR1=value1
TEST_VAR2="quoted value"
TEST_VAR3='single quoted'
EMPTY_VAR=

# Another comment
TEST_VAR4=value with spaces
"""
        env_file.write_text(env_content)
        
        # Clear existing env vars that might interfere
        for key in ["TEST_VAR1", "TEST_VAR2", "TEST_VAR3", "TEST_VAR4"]:
            monkeypatch.delenv(key, raising=False)
        
        load_dotenv(env_file)
        
        assert os.getenv("TEST_VAR1") == "value1"
        assert os.getenv("TEST_VAR2") == "quoted value"
        assert os.getenv("TEST_VAR3") == "single quoted"
        assert os.getenv("TEST_VAR4") == "value with spaces"
    
    def test_load_dotenv_existing_env_vars_take_precedence(self, tmp_path, monkeypatch):
        """Test that existing environment variables take precedence."""
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_PRECEDENCE=from_file")
        
        monkeypatch.setenv("TEST_PRECEDENCE", "from_env")
        
        load_dotenv(env_file)
        
        assert os.getenv("TEST_PRECEDENCE") == "from_env"
    
    def test_load_dotenv_malformed_file(self, tmp_path, capsys):
        """Test loading a malformed .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text("malformed content without equals")
        
        # Should not raise an exception, just skip malformed lines
        load_dotenv(env_file)
    
    def test_load_dotenv_permission_error(self, tmp_path, capsys):
        """Test handling of permission errors."""
        env_file = tmp_path / ".env"
        
        with patch("builtins.open", side_effect=PermissionError("Access denied")):
            load_dotenv(env_file)
            
        captured = capsys.readouterr()
        assert "Warning: Failed to load .env file" in captured.err


class TestPrusaWebcamUploaderInit:
    """Test cases for PrusaWebcamUploader initialization."""
    
    def test_init_with_valid_config(self, monkeypatch):
        """Test initialization with valid configuration."""
        monkeypatch.setenv("FINGERPRINT", "test_fingerprint")
        monkeypatch.setenv("TOKEN", "test_token")
        
        with patch.object(PrusaWebcamUploader, '_setup_logging') as mock_logging, \
             patch.object(PrusaWebcamUploader, '_setup_session') as mock_session:
            mock_logging.return_value = Mock()
            mock_session.return_value = Mock()
            
            uploader = PrusaWebcamUploader()
            
            assert uploader.config['fingerprint'] == "test_fingerprint"
            assert uploader.config['token'] == "test_token"
            assert uploader.config['capture_method'] == "http"  # default
    
    def test_init_missing_required_config(self, monkeypatch):
        """Test initialization with missing required configuration."""
        # Clear required env vars
        monkeypatch.delenv("FINGERPRINT", raising=False)
        monkeypatch.delenv("TOKEN", raising=False)
        
        with pytest.raises(ValueError, match="FINGERPRINT and TOKEN environment variables must be set"):
            PrusaWebcamUploader()
    
    def test_init_invalid_capture_method(self, monkeypatch):
        """Test initialization with invalid capture method."""
        monkeypatch.setenv("FINGERPRINT", "test_fingerprint")
        monkeypatch.setenv("TOKEN", "test_token")
        monkeypatch.setenv("CAPTURE_METHOD", "invalid")
        
        with pytest.raises(ValueError, match="CAPTURE_METHOD must be either 'http' or 'rtsp'"):
            PrusaWebcamUploader()
    
    def test_init_rtsp_without_url(self, monkeypatch):
        """Test initialization with RTSP method but no URL."""
        monkeypatch.setenv("FINGERPRINT", "test_fingerprint")
        monkeypatch.setenv("TOKEN", "test_token")
        monkeypatch.setenv("CAPTURE_METHOD", "rtsp")
        monkeypatch.delenv("RTSP_URL", raising=False)
        
        with pytest.raises(ValueError, match="RTSP_URL must be set when CAPTURE_METHOD is 'rtsp'"):
            PrusaWebcamUploader()


class TestPrusaWebcamUploaderConfig:
    """Test cases for configuration loading and validation."""
    
    @pytest.fixture
    def uploader(self, monkeypatch):
        """Create a valid uploader instance for testing."""
        monkeypatch.setenv("FINGERPRINT", "test_fingerprint")
        monkeypatch.setenv("TOKEN", "test_token")
        
        with patch.object(PrusaWebcamUploader, '_setup_logging') as mock_logging, \
             patch.object(PrusaWebcamUploader, '_setup_session') as mock_session:
            mock_logging.return_value = Mock()
            mock_session.return_value = Mock()
            
            return PrusaWebcamUploader()
    
    def test_default_config_values(self, uploader):
        """Test that default configuration values are set correctly."""
        config = uploader.config
        
        assert config['http_url'] == 'https://webcam.connect.prusa3d.com/c/snapshot'
        assert config['delay_seconds'] == 10
        assert config['long_delay_seconds'] == 60
        assert config['ping_host'] == 'prusa'
        assert config['max_retries'] == 3
        assert config['timeout'] == 30
        assert config['rtsp_timeout'] == 10
        assert config['capture_method'] == 'http'
    
    def test_custom_config_values(self, monkeypatch):
        """Test that custom configuration values override defaults."""
        monkeypatch.setenv("FINGERPRINT", "test_fingerprint")
        monkeypatch.setenv("TOKEN", "test_token")
        monkeypatch.setenv("DELAY_SECONDS", "15")
        monkeypatch.setenv("LONG_DELAY_SECONDS", "90")
        monkeypatch.setenv("PING_HOST", "custom_host")
        monkeypatch.setenv("MAX_RETRIES", "5")
        monkeypatch.setenv("TIMEOUT", "45")
        monkeypatch.setenv("RTSP_TIMEOUT", "20")
        monkeypatch.setenv("CAPTURE_METHOD", "rtsp")
        monkeypatch.setenv("RTSP_URL", "rtsp://test.com/stream")
        
        with patch.object(PrusaWebcamUploader, '_setup_logging') as mock_logging, \
             patch.object(PrusaWebcamUploader, '_setup_session') as mock_session:
            mock_logging.return_value = Mock()
            mock_session.return_value = Mock()
            
            uploader = PrusaWebcamUploader()
            
            assert uploader.config['delay_seconds'] == 15
            assert uploader.config['long_delay_seconds'] == 90
            assert uploader.config['ping_host'] == "custom_host"
            assert uploader.config['max_retries'] == 5
            assert uploader.config['timeout'] == 45
            assert uploader.config['rtsp_timeout'] == 20
            assert uploader.config['capture_method'] == "rtsp"
            assert uploader.config['rtsp_url'] == "rtsp://test.com/stream"


class TestPrusaWebcamUploaderConnectivity:
    """Test cases for connectivity checking."""
    
    @pytest.fixture
    def uploader(self, monkeypatch):
        """Create a valid uploader instance for testing."""
        monkeypatch.setenv("FINGERPRINT", "test_fingerprint")
        monkeypatch.setenv("TOKEN", "test_token")
        
        with patch.object(PrusaWebcamUploader, '_setup_logging') as mock_logging, \
             patch.object(PrusaWebcamUploader, '_setup_session') as mock_session:
            mock_logger = Mock()
            mock_logging.return_value = mock_logger
            mock_session.return_value = Mock()
            
            uploader = PrusaWebcamUploader()
            uploader.logger = mock_logger
            return uploader
    
    @patch('subprocess.run')
    def test_check_connectivity_success(self, mock_run, uploader):
        """Test successful connectivity check."""
        mock_run.return_value.returncode = 0
        
        result = uploader.check_connectivity()
        
        assert result is True
        mock_run.assert_called_once_with(
            ['ping', '-c', '1', 'prusa'],
            capture_output=True,
            text=True,
            timeout=10
        )
    
    @patch('subprocess.run')
    def test_check_connectivity_failure(self, mock_run, uploader):
        """Test failed connectivity check."""
        mock_run.return_value.returncode = 1
        
        result = uploader.check_connectivity()
        
        assert result is False
    
    @patch('subprocess.run')
    def test_check_connectivity_timeout(self, mock_run, uploader):
        """Test connectivity check timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired(['ping'], 10)
        
        result = uploader.check_connectivity()
        
        assert result is False
        uploader.logger.warning.assert_called()


class TestPrusaWebcamUploaderHTTPCapture:
    """Test cases for HTTP snapshot capture."""
    
    @pytest.fixture
    def uploader(self, monkeypatch):
        """Create a valid uploader instance for testing."""
        monkeypatch.setenv("FINGERPRINT", "test_fingerprint")
        monkeypatch.setenv("TOKEN", "test_token")
        
        with patch.object(PrusaWebcamUploader, '_setup_logging') as mock_logging, \
             patch.object(PrusaWebcamUploader, '_setup_session') as mock_session:
            mock_logger = Mock()
            mock_logging.return_value = mock_logger
            mock_session.return_value = Mock()
            
            uploader = PrusaWebcamUploader()
            uploader.logger = mock_logger
            return uploader
    
    def test_capture_from_http_success(self, uploader, tmp_path):
        """Test successful HTTP snapshot capture."""
        # Use a temporary directory for the test
        temp_image = tmp_path / "test_output.jpg"
        uploader.temp_image_path = temp_image
        
        # Mock response with image data
        mock_response = Mock()
        mock_response.iter_content.return_value = [b'fake_image_data']
        uploader.session.get.return_value = mock_response
        
        result = uploader._capture_from_http()
        
        assert result is True
        assert temp_image.exists()
        assert temp_image.read_bytes() == b'fake_image_data'
    
    def test_capture_from_http_request_error(self, uploader):
        """Test HTTP capture with request error."""
        uploader.session.get.side_effect = requests.RequestException("Connection failed")
        
        result = uploader._capture_from_http()
        
        assert result is False
        uploader.logger.error.assert_called()
    
    def test_capture_from_http_empty_response(self, uploader, tmp_path):
        """Test HTTP capture with empty response."""
        temp_image = tmp_path / "test_output.jpg"
        uploader.temp_image_path = temp_image
        
        # Mock response with empty data
        mock_response = Mock()
        mock_response.iter_content.return_value = []
        uploader.session.get.return_value = mock_response
        
        result = uploader._capture_from_http()
        
        assert result is False
        uploader.logger.error.assert_called()
    
    @patch('builtins.open', side_effect=IOError("Write failed"))
    def test_capture_from_http_write_error(self, mock_open, uploader):
        """Test HTTP capture with file write error."""
        mock_response = Mock()
        mock_response.iter_content.return_value = [b'fake_image_data']
        uploader.session.get.return_value = mock_response
        
        result = uploader._capture_from_http()
        
        assert result is False
        uploader.logger.error.assert_called()


class TestPrusaWebcamUploaderRTSPCapture:
    """Test cases for RTSP snapshot capture."""
    
    @pytest.fixture
    def uploader(self, monkeypatch):
        """Create a valid uploader instance for RTSP testing."""
        monkeypatch.setenv("FINGERPRINT", "test_fingerprint")
        monkeypatch.setenv("TOKEN", "test_token")
        monkeypatch.setenv("CAPTURE_METHOD", "rtsp")
        monkeypatch.setenv("RTSP_URL", "rtsp://test.com/stream")
        
        with patch.object(PrusaWebcamUploader, '_setup_logging') as mock_logging, \
             patch.object(PrusaWebcamUploader, '_setup_session') as mock_session:
            mock_logger = Mock()
            mock_logging.return_value = mock_logger
            mock_session.return_value = Mock()
            
            uploader = PrusaWebcamUploader()
            uploader.logger = mock_logger
            return uploader
    
    @patch('cv2.VideoCapture')
    @patch('cv2.imencode')
    def test_capture_from_rtsp_success(self, mock_imencode, mock_video_capture, uploader, tmp_path):
        """Test successful RTSP snapshot capture."""
        temp_image = tmp_path / "test_output.jpg"
        uploader.temp_image_path = temp_image
        
        # Mock VideoCapture
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_video_capture.return_value = mock_cap
        
        # Mock imencode
        mock_imencode.return_value = (True, np.array([1, 2, 3, 4], dtype=np.uint8))
        
        result = uploader._capture_from_rtsp()
        
        assert result is True
        mock_cap.release.assert_called_once()
        assert temp_image.exists()
    
    @patch('cv2.VideoCapture')
    def test_capture_from_rtsp_failed_to_open(self, mock_video_capture, uploader):
        """Test RTSP capture when VideoCapture fails to open."""
        mock_cap = Mock()
        mock_cap.isOpened.return_value = False
        mock_video_capture.return_value = mock_cap
        
        result = uploader._capture_from_rtsp()
        
        assert result is False
        uploader.logger.error.assert_called()
        mock_cap.release.assert_called_once()
    
    @patch('cv2.VideoCapture')
    def test_capture_from_rtsp_failed_to_read(self, mock_video_capture, uploader):
        """Test RTSP capture when frame reading fails."""
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (False, None)
        mock_video_capture.return_value = mock_cap
        
        result = uploader._capture_from_rtsp()
        
        assert result is False
        uploader.logger.error.assert_called()
        mock_cap.release.assert_called_once()
    
    @patch('cv2.VideoCapture')
    @patch('cv2.imencode')
    def test_capture_from_rtsp_encode_failure(self, mock_imencode, mock_video_capture, uploader):
        """Test RTSP capture when image encoding fails."""
        mock_cap = Mock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_video_capture.return_value = mock_cap
        
        # Mock failed encoding
        mock_imencode.return_value = (False, None)
        
        result = uploader._capture_from_rtsp()
        
        assert result is False
        uploader.logger.error.assert_called()
        mock_cap.release.assert_called_once()
    
    @patch('cv2.VideoCapture')
    def test_capture_from_rtsp_opencv_error(self, mock_video_capture, uploader):
        """Test RTSP capture with OpenCV error."""
        mock_video_capture.side_effect = cv2.error("OpenCV error")
        
        result = uploader._capture_from_rtsp()
        
        assert result is False
        uploader.logger.error.assert_called()


class TestPrusaWebcamUploaderUpload:
    """Test cases for snapshot upload functionality."""
    
    @pytest.fixture
    def uploader(self, monkeypatch):
        """Create a valid uploader instance for testing."""
        monkeypatch.setenv("FINGERPRINT", "test_fingerprint")
        monkeypatch.setenv("TOKEN", "test_token")
        
        with patch.object(PrusaWebcamUploader, '_setup_logging') as mock_logging, \
             patch.object(PrusaWebcamUploader, '_setup_session') as mock_session:
            mock_logger = Mock()
            mock_logging.return_value = mock_logger
            mock_session.return_value = Mock()
            
            uploader = PrusaWebcamUploader()
            uploader.logger = mock_logger
            return uploader
    
    def test_upload_snapshot_success(self, uploader, tmp_path):
        """Test successful snapshot upload."""
        # Create a test image file
        temp_image = tmp_path / "test_output.jpg"
        temp_image.write_bytes(b"fake_image_data")
        uploader.temp_image_path = temp_image
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        uploader.session.put.return_value = mock_response
        
        result = uploader.upload_snapshot()
        
        assert result is True
        uploader.logger.info.assert_called()
        
        # Verify the request was made with correct parameters
        uploader.session.put.assert_called_once()
        call_args = uploader.session.put.call_args
        assert call_args[0][0] == uploader.config['http_url']
        assert call_args[1]['headers']['fingerprint'] == 'test_fingerprint'
        assert call_args[1]['headers']['token'] == 'test_token'
    
    def test_upload_snapshot_no_file(self, uploader):
        """Test upload when snapshot file doesn't exist."""
        uploader.temp_image_path = Path("/nonexistent/file.jpg")
        
        result = uploader.upload_snapshot()
        
        assert result is False
        uploader.logger.error.assert_called()
    
    def test_upload_snapshot_request_error(self, uploader, tmp_path):
        """Test upload with request error."""
        temp_image = tmp_path / "test_output.jpg"
        temp_image.write_bytes(b"fake_image_data")
        uploader.temp_image_path = temp_image
        
        uploader.session.put.side_effect = requests.RequestException("Upload failed")
        
        result = uploader.upload_snapshot()
        
        assert result is False
        uploader.logger.error.assert_called()
    
    def test_upload_snapshot_http_error(self, uploader, tmp_path):
        """Test upload with HTTP error response."""
        temp_image = tmp_path / "test_output.jpg"
        temp_image.write_bytes(b"fake_image_data")
        uploader.temp_image_path = temp_image
        
        # Mock HTTP error response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        
        error = requests.HTTPError("401 Client Error")
        error.response = mock_response
        uploader.session.put.side_effect = error
        
        result = uploader.upload_snapshot()
        
        assert result is False
        uploader.logger.error.assert_called()


class TestPrusaWebcamUploaderCleanup:
    """Test cases for cleanup functionality."""
    
    @pytest.fixture
    def uploader(self, monkeypatch):
        """Create a valid uploader instance for testing."""
        monkeypatch.setenv("FINGERPRINT", "test_fingerprint")
        monkeypatch.setenv("TOKEN", "test_token")
        
        with patch.object(PrusaWebcamUploader, '_setup_logging') as mock_logging, \
             patch.object(PrusaWebcamUploader, '_setup_session') as mock_session:
            mock_logger = Mock()
            mock_logging.return_value = mock_logger
            mock_session.return_value = Mock()
            
            uploader = PrusaWebcamUploader()
            uploader.logger = mock_logger
            return uploader
    
    def test_cleanup_success(self, uploader, tmp_path):
        """Test successful cleanup of temporary files."""
        temp_image = tmp_path / "test_output.jpg"
        temp_image.write_bytes(b"fake_image_data")
        uploader.temp_image_path = temp_image
        
        assert temp_image.exists()
        
        uploader.cleanup()
        
        assert not temp_image.exists()
        uploader.logger.debug.assert_called()
    
    def test_cleanup_nonexistent_file(self, uploader):
        """Test cleanup when file doesn't exist."""
        uploader.temp_image_path = Path("/nonexistent/file.jpg")
        
        # Should not raise an exception
        uploader.cleanup()
        
        uploader.logger.debug.assert_called()
    
    @patch('pathlib.Path.unlink')
    def test_cleanup_error(self, mock_unlink, uploader):
        """Test cleanup with file deletion error."""
        mock_unlink.side_effect = OSError("Permission denied")
        
        uploader.cleanup()
        
        uploader.logger.warning.assert_called()


class TestPrusaWebcamUploaderMainLoop:
    """Test cases for the main execution loop."""
    
    @pytest.fixture
    def uploader(self, monkeypatch):
        """Create a valid uploader instance for testing."""
        monkeypatch.setenv("FINGERPRINT", "test_fingerprint")
        monkeypatch.setenv("TOKEN", "test_token")
        
        with patch.object(PrusaWebcamUploader, '_setup_logging') as mock_logging, \
             patch.object(PrusaWebcamUploader, '_setup_session') as mock_session:
            mock_logger = Mock()
            mock_logging.return_value = mock_logger
            mock_session.return_value = Mock()
            
            uploader = PrusaWebcamUploader()
            uploader.logger = mock_logger
            return uploader
    
    @patch('time.sleep')
    def test_run_successful_cycle(self, mock_sleep, uploader):
        """Test a successful capture and upload cycle."""
        # Mock all the methods to succeed
        uploader.check_connectivity = Mock(return_value=True)
        uploader.capture_snapshot = Mock(return_value=True)
        uploader.upload_snapshot = Mock(return_value=True)
        uploader.cleanup = Mock()
        
        # Run one iteration and then raise KeyboardInterrupt
        def side_effect(*args):
            raise KeyboardInterrupt()
        
        mock_sleep.side_effect = side_effect
        
        uploader.run()
        
        uploader.check_connectivity.assert_called()
        uploader.capture_snapshot.assert_called()
        uploader.upload_snapshot.assert_called()
        uploader.cleanup.assert_called()
    
    @patch('time.sleep')
    def test_run_connectivity_failure(self, mock_sleep, uploader):
        """Test run with connectivity failure."""
        uploader.check_connectivity = Mock(return_value=False)
        uploader.cleanup = Mock()
        
        # Run one iteration and then raise KeyboardInterrupt
        def side_effect(*args):
            raise KeyboardInterrupt()
        
        mock_sleep.side_effect = side_effect
        
        uploader.run()
        
        uploader.check_connectivity.assert_called()
        uploader.logger.warning.assert_called()
        uploader.cleanup.assert_called()
    
    @patch('time.sleep')
    def test_run_capture_failure(self, mock_sleep, uploader):
        """Test run with capture failure."""
        uploader.check_connectivity = Mock(return_value=True)
        uploader.capture_snapshot = Mock(return_value=False)
        uploader.cleanup = Mock()
        
        # Run one iteration and then raise KeyboardInterrupt
        def side_effect(*args):
            raise KeyboardInterrupt()
        
        mock_sleep.side_effect = side_effect
        
        uploader.run()
        
        uploader.capture_snapshot.assert_called()
        uploader.logger.warning.assert_called()
        uploader.cleanup.assert_called()
    
    @patch('time.sleep')
    def test_run_upload_failure(self, mock_sleep, uploader):
        """Test run with upload failure."""
        uploader.check_connectivity = Mock(return_value=True)
        uploader.capture_snapshot = Mock(return_value=True)
        uploader.upload_snapshot = Mock(return_value=False)
        uploader.cleanup = Mock()
        
        # Run one iteration and then raise KeyboardInterrupt
        def side_effect(*args):
            raise KeyboardInterrupt()
        
        mock_sleep.side_effect = side_effect
        
        uploader.run()
        
        uploader.upload_snapshot.assert_called()
        uploader.logger.warning.assert_called()
        uploader.cleanup.assert_called()


class TestMainFunction:
    """Test cases for the main function."""
    
    def test_main_success(self, monkeypatch):
        """Test successful main function execution."""
        monkeypatch.setenv("FINGERPRINT", "test_fingerprint")
        monkeypatch.setenv("TOKEN", "test_token")
        
        with patch.object(PrusaWebcamUploader, '__init__', return_value=None) as mock_init, \
             patch.object(PrusaWebcamUploader, 'run') as mock_run:
            
            main()
            
            mock_init.assert_called_once()
            mock_run.assert_called_once()
    
    def test_main_value_error(self, monkeypatch, capsys):
        """Test main function with configuration error."""
        # Don't set required environment variables
        monkeypatch.delenv("FINGERPRINT", raising=False)
        monkeypatch.delenv("TOKEN", raising=False)
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Configuration error" in captured.err
    
    def test_main_unexpected_error(self, monkeypatch, capsys):
        """Test main function with unexpected error."""
        monkeypatch.setenv("FINGERPRINT", "test_fingerprint")
        monkeypatch.setenv("TOKEN", "test_token")
        
        with patch.object(PrusaWebcamUploader, '__init__') as mock_init:
            mock_init.side_effect = RuntimeError("Unexpected error")
            
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "Fatal error" in captured.err


class TestIntegration:
    """Integration test cases."""
    
    @responses.activate
    def test_end_to_end_http_capture_and_upload(self, monkeypatch, tmp_path):
        """Test end-to-end HTTP capture and upload."""
        # Set up environment
        monkeypatch.setenv("FINGERPRINT", "test_fingerprint")
        monkeypatch.setenv("TOKEN", "test_token")
        monkeypatch.setenv("CAPTURE_METHOD", "http")
        monkeypatch.setenv("SNAPSHOT_URL", "http://localhost:8080/?action=snapshot")
        
        # Mock HTTP responses
        responses.add(
            responses.GET,
            "http://localhost:8080/?action=snapshot",
            body=b"fake_image_data",
            status=200,
            content_type="image/jpeg"
        )
        
        responses.add(
            responses.PUT,
            "https://webcam.connect.prusa3d.com/c/snapshot",
            status=200
        )
        
        # Create uploader and override temp path
        with patch.object(PrusaWebcamUploader, '_setup_logging') as mock_logging:
            mock_logger = Mock()
            mock_logging.return_value = mock_logger
            
            uploader = PrusaWebcamUploader()
            uploader.logger = mock_logger
            uploader.temp_image_path = tmp_path / "test_output.jpg"
            
            # Mock connectivity check
            with patch.object(uploader, 'check_connectivity', return_value=True):
                # Test the capture and upload process
                assert uploader.capture_snapshot() is True
                assert uploader.upload_snapshot() is True
                
                # Verify file was created and cleaned up
                assert uploader.temp_image_path.exists()
                uploader.cleanup()
                assert not uploader.temp_image_path.exists()


if __name__ == "__main__":
    pytest.main([__file__])
