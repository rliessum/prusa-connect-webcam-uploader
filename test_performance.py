#!/usr/bin/env python3
"""
Performance and stress tests for Prusa Connect Webcam Uploader

These tests focus on performance characteristics, memory usage,
and behavior under load conditions.
"""

import time
import threading
from pathlib import Path
from unittest.mock import Mock, patch
import pytest
import psutil
import os

import sys
sys.path.insert(0, str(Path(__file__).parent))

from prusa_webcam_uploader import PrusaWebcamUploader


class TestPerformance:
    """Performance-related test cases."""
    
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
    
    @pytest.mark.slow
    def test_memory_usage_during_operation(self, uploader, tmp_path):
        """Test memory usage during normal operation."""
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Simulate multiple capture/upload cycles
        temp_image = tmp_path / "test_output.jpg"
        uploader.temp_image_path = temp_image
        
        with patch.object(uploader.session, 'get') as mock_get, \
             patch.object(uploader.session, 'put') as mock_put:
            
            # Mock successful responses
            mock_response = Mock()
            mock_response.iter_content.return_value = [b'x' * 1024 * 100]  # 100KB
            mock_get.return_value = mock_response
            
            mock_put_response = Mock()
            mock_put_response.status_code = 200
            mock_put.return_value = mock_put_response
            
            # Run multiple cycles
            for _ in range(10):
                uploader._capture_from_http()
                uploader.upload_snapshot()
                uploader.cleanup()
        
        # Check memory usage hasn't grown significantly
        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory
        
        # Allow some memory growth but not excessive (less than 50MB)
        assert memory_growth < 50 * 1024 * 1024, f"Memory grew by {memory_growth} bytes"
    
    def test_config_loading_performance(self, monkeypatch):
        """Test configuration loading performance."""
        # Set a large number of environment variables
        for i in range(100):
            monkeypatch.setenv(f"DUMMY_VAR_{i}", f"value_{i}")
        
        monkeypatch.setenv("FINGERPRINT", "test_fingerprint")
        monkeypatch.setenv("TOKEN", "test_token")
        
        start_time = time.time()
        
        with patch.object(PrusaWebcamUploader, '_setup_logging') as mock_logging, \
             patch.object(PrusaWebcamUploader, '_setup_session') as mock_session:
            mock_logging.return_value = Mock()
            mock_session.return_value = Mock()
            
            uploader = PrusaWebcamUploader()
        
        end_time = time.time()
        
        # Configuration loading should be fast (less than 1 second)
        assert end_time - start_time < 1.0
    
    @pytest.mark.slow
    def test_concurrent_instances(self, monkeypatch, tmp_path):
        """Test behavior with multiple concurrent instances."""
        monkeypatch.setenv("FINGERPRINT", "test_fingerprint")
        monkeypatch.setenv("TOKEN", "test_token")
        
        results = []
        errors = []
        
        def create_and_test_uploader(instance_id):
            try:
                with patch.object(PrusaWebcamUploader, '_setup_logging') as mock_logging, \
                     patch.object(PrusaWebcamUploader, '_setup_session') as mock_session:
                    mock_logger = Mock()
                    mock_logging.return_value = mock_logger
                    mock_session.return_value = Mock()
                    
                    uploader = PrusaWebcamUploader()
                    uploader.logger = mock_logger
                    uploader.temp_image_path = tmp_path / f"test_output_{instance_id}.jpg"
                    
                    # Simulate quick operation
                    uploader.temp_image_path.write_bytes(b"test_data")
                    uploader.cleanup()
                    
                    results.append(f"Instance {instance_id} completed")
            except Exception as e:
                errors.append(f"Instance {instance_id} failed: {e}")
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_and_test_uploader, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=10)
        
        # Check results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5, f"Expected 5 results, got {len(results)}"


class TestStress:
    """Stress testing for edge cases and error conditions."""
    
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
    
    def test_large_image_handling(self, uploader, tmp_path):
        """Test handling of large image files."""
        temp_image = tmp_path / "large_test_output.jpg"
        uploader.temp_image_path = temp_image
        
        # Create a large fake image (10MB)
        large_data = b'x' * (10 * 1024 * 1024)
        
        with patch.object(uploader.session, 'get') as mock_get, \
             patch.object(uploader.session, 'put') as mock_put:
            
            # Mock large response
            mock_response = Mock()
            mock_response.iter_content.return_value = [large_data]
            mock_get.return_value = mock_response
            
            mock_put_response = Mock()
            mock_put_response.status_code = 200
            mock_put.return_value = mock_put_response
            
            # Should handle large files without issues
            result = uploader._capture_from_http()
            assert result is True
            
            result = uploader.upload_snapshot()
            assert result is True
    
    def test_rapid_successive_operations(self, uploader, tmp_path):
        """Test rapid successive capture and upload operations."""
        temp_image = tmp_path / "rapid_test_output.jpg"
        uploader.temp_image_path = temp_image
        
        with patch.object(uploader.session, 'get') as mock_get, \
             patch.object(uploader.session, 'put') as mock_put:
            
            mock_response = Mock()
            mock_response.iter_content.return_value = [b'test_data']
            mock_get.return_value = mock_response
            
            mock_put_response = Mock()
            mock_put_response.status_code = 200
            mock_put.return_value = mock_put_response
            
            # Perform rapid operations
            for i in range(50):
                assert uploader._capture_from_http() is True
                assert uploader.upload_snapshot() is True
                uploader.cleanup()
    
    def test_filesystem_stress(self, uploader, tmp_path):
        """Test behavior under filesystem stress conditions."""
        temp_image = tmp_path / "fs_stress_test.jpg"
        uploader.temp_image_path = temp_image
        
        # Test with various file system conditions
        test_scenarios = [
            b'',  # Empty file
            b'x',  # Single byte
            b'x' * 1024,  # 1KB
            b'x' * (1024 * 1024),  # 1MB
        ]
        
        with patch.object(uploader.session, 'get') as mock_get, \
             patch.object(uploader.session, 'put') as mock_put:
            
            mock_put_response = Mock()
            mock_put_response.status_code = 200
            mock_put.return_value = mock_put_response
            
            for data in test_scenarios:
                mock_response = Mock()
                mock_response.iter_content.return_value = [data] if data else []
                mock_get.return_value = mock_response
                
                # Empty data should fail, others should succeed
                expected_result = len(data) > 0
                assert uploader._capture_from_http() == expected_result
                
                if expected_result:
                    assert uploader.upload_snapshot() is True
                
                uploader.cleanup()


class TestErrorRecovery:
    """Test error recovery and resilience."""
    
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
    
    def test_network_interruption_recovery(self, uploader, tmp_path):
        """Test recovery from network interruptions."""
        temp_image = tmp_path / "network_test.jpg"
        uploader.temp_image_path = temp_image
        
        call_count = 0
        
        def failing_then_success(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise ConnectionError("Network unavailable")
            
            # Success on third try
            mock_response = Mock()
            mock_response.iter_content.return_value = [b'recovered_data']
            return mock_response
        
        with patch.object(uploader.session, 'get', side_effect=failing_then_success):
            # First two attempts should fail
            assert uploader._capture_from_http() is False
            assert uploader._capture_from_http() is False
            
            # Third attempt should succeed
            assert uploader._capture_from_http() is True
    
    def test_partial_file_corruption_handling(self, uploader, tmp_path):
        """Test handling of partial file corruption scenarios."""
        temp_image = tmp_path / "corruption_test.jpg"
        uploader.temp_image_path = temp_image
        
        # Simulate partial write and system crash
        with patch('builtins.open', mock_open()) as mock_file:
            # Simulate write failure midway
            mock_file.return_value.write.side_effect = [4, IOError("Disk full")]
            
            with patch.object(uploader.session, 'get') as mock_get:
                mock_response = Mock()
                mock_response.iter_content.return_value = [b'test', b'data']
                mock_get.return_value = mock_response
                
                result = uploader._capture_from_http()
                assert result is False
    
    @pytest.mark.slow
    def test_resource_cleanup_under_stress(self, uploader, tmp_path):
        """Test that resources are properly cleaned up under stress."""
        temp_image = tmp_path / "cleanup_stress_test.jpg"
        uploader.temp_image_path = temp_image
        
        # Create many temporary files and ensure they're cleaned up
        for i in range(100):
            test_file = tmp_path / f"stress_file_{i}.jpg"
            test_file.write_bytes(b'test_data')
            
            uploader.temp_image_path = test_file
            uploader.cleanup()
            
            # File should be cleaned up
            assert not test_file.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "slow"])
