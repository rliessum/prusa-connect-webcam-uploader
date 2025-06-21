#!/usr/bin/env python3
"""
Test configuration and utilities for handling OpenCV dependencies gracefully
"""

import sys
from unittest.mock import Mock

# Mock OpenCV if it's not available (useful for testing environments)
def mock_opencv():
    """Mock OpenCV module for testing environments where it's not available."""
    cv2_mock = Mock()
    
    # Mock common OpenCV constants
    cv2_mock.CAP_PROP_BUFFERSIZE = 38
    cv2_mock.IMWRITE_JPEG_QUALITY = 1
    
    # Mock VideoCapture class
    video_capture_mock = Mock()
    video_capture_mock.isOpened.return_value = True
    video_capture_mock.read.return_value = (True, Mock())
    video_capture_mock.set.return_value = True
    video_capture_mock.release.return_value = None
    
    cv2_mock.VideoCapture = Mock(return_value=video_capture_mock)
    cv2_mock.imencode = Mock(return_value=(True, Mock()))
    cv2_mock.error = Exception
    
    return cv2_mock

# Try to import cv2, fall back to mock if not available
try:
    import cv2
except ImportError:
    print("OpenCV not available, using mock for testing", file=sys.stderr)
    cv2 = mock_opencv()
    sys.modules['cv2'] = cv2

# Make cv2 available for import in tests
__all__ = ['cv2']
