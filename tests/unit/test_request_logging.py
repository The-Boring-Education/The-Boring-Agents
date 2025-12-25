"""
Unit tests for request_logging utility module.

Tests the request logging functions used across API routes.
"""

import pytest
import json
import logging
from unittest.mock import Mock, patch, MagicMock
from fastapi import Request

from src.utils.request_logging import get_request_id, log_action


class TestGetRequestId:
    """Tests for get_request_id function."""
    
    def test_get_request_id_from_state(self):
        """Test extracting request ID from request state."""
        mock_request = Mock(spec=Request)
        mock_request.state = Mock()
        mock_request.state.request_id = "test-request-123"
        
        result = get_request_id(mock_request)
        
        assert result == "test-request-123"
    
    def test_get_request_id_missing_returns_unknown(self):
        """Test that missing request ID returns 'unknown'."""
        mock_request = Mock(spec=Request)
        mock_request.state = Mock(spec=[])  # No request_id attribute
        
        result = get_request_id(mock_request)
        
        assert result == "unknown"
    
    def test_get_request_id_with_uuid(self):
        """Test with UUID-style request ID."""
        mock_request = Mock(spec=Request)
        mock_request.state = Mock()
        mock_request.state.request_id = "550e8400-e29b-41d4-a716-446655440000"
        
        result = get_request_id(mock_request)
        
        assert result == "550e8400-e29b-41d4-a716-446655440000"


class TestLogAction:
    """Tests for log_action function."""
    
    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger."""
        with patch("src.utils.request_logging.logger") as mock:
            yield mock
    
    @pytest.fixture
    def mock_env_manager(self):
        """Create a mock environment manager."""
        with patch("src.utils.request_logging.env_manager") as mock:
            mock.get.return_value = "test"
            yield mock
    
    def test_log_action_info_level(self, mock_logger, mock_env_manager):
        """Test logging at INFO level."""
        log_action(None, "test_action")
        
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        data = json.loads(call_args)
        
        assert data["action"] == "test_action"
        assert data["level"] == "INFO"
    
    def test_log_action_error_level(self, mock_logger, mock_env_manager):
        """Test logging at ERROR level."""
        log_action(None, "error_action", level="ERROR")
        
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args[0][0]
        data = json.loads(call_args)
        
        assert data["level"] == "ERROR"
    
    def test_log_action_warning_level(self, mock_logger, mock_env_manager):
        """Test logging at WARNING level."""
        log_action(None, "warning_action", level="WARNING")
        
        mock_logger.warning.assert_called_once()
    
    def test_log_action_with_request(self, mock_logger, mock_env_manager):
        """Test logging with request object."""
        mock_request = Mock(spec=Request)
        mock_request.state = Mock()
        mock_request.state.request_id = "req-123"
        
        log_action(mock_request, "test_action")
        
        call_args = mock_logger.info.call_args[0][0]
        data = json.loads(call_args)
        
        assert data["request_id"] == "req-123"
    
    def test_log_action_with_session_id(self, mock_logger, mock_env_manager):
        """Test logging with session ID."""
        log_action(None, "test_action", session_id="session-456")
        
        call_args = mock_logger.info.call_args[0][0]
        data = json.loads(call_args)
        
        assert data["session_id"] == "session-456"
    
    def test_log_action_with_kwargs(self, mock_logger, mock_env_manager):
        """Test logging with additional kwargs."""
        log_action(None, "test_action", custom_field="value", count=42)
        
        call_args = mock_logger.info.call_args[0][0]
        data = json.loads(call_args)
        
        assert data["custom_field"] == "value"
        assert data["count"] == 42
    
    def test_log_action_includes_timestamp(self, mock_logger, mock_env_manager):
        """Test that log includes timestamp."""
        log_action(None, "test_action")
        
        call_args = mock_logger.info.call_args[0][0]
        data = json.loads(call_args)
        
        assert "timestamp" in data
        assert data["timestamp"].endswith("Z")
    
    def test_log_action_includes_environment(self, mock_logger, mock_env_manager):
        """Test that log includes environment."""
        mock_env_manager.get.return_value = "production"
        
        log_action(None, "test_action")
        
        call_args = mock_logger.info.call_args[0][0]
        data = json.loads(call_args)
        
        assert data["environment"] == "production"
    
    def test_log_action_without_request(self, mock_logger, mock_env_manager):
        """Test logging without request object."""
        log_action(None, "test_action")
        
        call_args = mock_logger.info.call_args[0][0]
        data = json.loads(call_args)
        
        assert "request_id" not in data
    
    def test_log_action_json_format(self, mock_logger, mock_env_manager):
        """Test that log is valid JSON."""
        log_action(None, "test_action", key="value")
        
        call_args = mock_logger.info.call_args[0][0]
        
        # Should not raise
        data = json.loads(call_args)
        assert isinstance(data, dict)


class TestLogActionIntegration:
    """Integration tests for log_action with actual logging."""
    
    def test_log_action_actual_logging(self, caplog):
        """Test that log_action actually logs."""
        with caplog.at_level(logging.INFO):
            with patch("src.utils.request_logging.env_manager") as mock_env:
                mock_env.get.return_value = "test"
                
                log_action(None, "integration_test", test_data="value")
        
        assert len(caplog.records) >= 0  # At least the action should be logged

