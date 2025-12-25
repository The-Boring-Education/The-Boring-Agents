"""
Unit tests for session_logger utility module.

Tests the session logging functions for agent workflows.
"""

import pytest
import os
import json
import tempfile
import shutil
from unittest.mock import patch

from src.utils.session_logger import (
    _logs_root_dir,
    get_log_file_path,
    append_log,
    read_logs,
)


class TestLogsRootDir:
    """Tests for _logs_root_dir function."""
    
    def test_returns_expected_path(self):
        """Test that logs root dir returns expected path."""
        result = _logs_root_dir()
        assert result == os.path.join("logs", "sessions")


class TestGetLogFilePath:
    """Tests for get_log_file_path function."""
    
    def test_returns_path_with_session_id(self):
        """Test that path includes session ID."""
        path = get_log_file_path("test-session-123")
        
        assert "test-session-123" in path
        assert path.endswith(".log")
    
    def test_creates_directory(self, temp_dir):
        """Test that directory is created if it doesn't exist."""
        with patch("src.utils.session_logger._logs_root_dir") as mock_root:
            mock_root.return_value = os.path.join(temp_dir, "logs", "sessions")
            
            path = get_log_file_path("test-session")
            
            assert os.path.exists(os.path.dirname(path))
    
    def test_handles_special_characters(self):
        """Test handling of session IDs with special characters."""
        path = get_log_file_path("session-with-dashes-and-numbers-123")
        
        assert "session-with-dashes-and-numbers-123" in path


class TestAppendLog:
    """Tests for append_log function."""
    
    @pytest.fixture
    def temp_logs_dir(self, temp_dir):
        """Create temporary logs directory."""
        logs_dir = os.path.join(temp_dir, "logs", "sessions")
        os.makedirs(logs_dir, exist_ok=True)
        return logs_dir
    
    def test_append_log_creates_file(self, temp_logs_dir):
        """Test that append_log creates a log file."""
        with patch("src.utils.session_logger._logs_root_dir") as mock_root:
            mock_root.return_value = temp_logs_dir
            
            append_log("test-session", "test_event", {"key": "value"})
            
            filepath = os.path.join(temp_logs_dir, "test-session.log")
            assert os.path.exists(filepath)
    
    def test_append_log_writes_json(self, temp_logs_dir):
        """Test that append_log writes valid JSON."""
        with patch("src.utils.session_logger._logs_root_dir") as mock_root:
            mock_root.return_value = temp_logs_dir
            
            append_log("test-session", "test_event", {"data": 123})
            
            filepath = os.path.join(temp_logs_dir, "test-session.log")
            with open(filepath, 'r') as f:
                line = f.readline()
                data = json.loads(line)
            
            assert data["event"] == "test_event"
            assert data["meta"]["data"] == 123
            assert "timestamp" in data
    
    def test_append_log_appends_to_existing(self, temp_logs_dir):
        """Test that append_log appends to existing file."""
        with patch("src.utils.session_logger._logs_root_dir") as mock_root:
            mock_root.return_value = temp_logs_dir
            
            append_log("test-session", "event1", {})
            append_log("test-session", "event2", {})
            append_log("test-session", "event3", {})
            
            filepath = os.path.join(temp_logs_dir, "test-session.log")
            with open(filepath, 'r') as f:
                lines = f.readlines()
            
            assert len(lines) == 3
    
    def test_append_log_handles_none_meta(self, temp_logs_dir):
        """Test that append_log handles None meta."""
        with patch("src.utils.session_logger._logs_root_dir") as mock_root:
            mock_root.return_value = temp_logs_dir
            
            append_log("test-session", "test_event")
            
            filepath = os.path.join(temp_logs_dir, "test-session.log")
            with open(filepath, 'r') as f:
                line = f.readline()
                data = json.loads(line)
            
            assert data["meta"] == {}
    
    def test_append_log_timestamp_format(self, temp_logs_dir):
        """Test that timestamp is in ISO format with UTC."""
        with patch("src.utils.session_logger._logs_root_dir") as mock_root:
            mock_root.return_value = temp_logs_dir
            
            append_log("test-session", "test_event")
            
            filepath = os.path.join(temp_logs_dir, "test-session.log")
            with open(filepath, 'r') as f:
                line = f.readline()
                data = json.loads(line)
            
            # Should contain UTC timezone indicator
            assert "+" in data["timestamp"] or "Z" in data["timestamp"] or data["timestamp"].endswith("+00:00")


class TestReadLogs:
    """Tests for read_logs function."""
    
    @pytest.fixture
    def temp_logs_dir(self, temp_dir):
        """Create temporary logs directory with sample logs."""
        logs_dir = os.path.join(temp_dir, "logs", "sessions")
        os.makedirs(logs_dir, exist_ok=True)
        return logs_dir
    
    def test_read_logs_returns_list(self, temp_logs_dir):
        """Test that read_logs returns a list."""
        with patch("src.utils.session_logger._logs_root_dir") as mock_root:
            mock_root.return_value = temp_logs_dir
            
            result = read_logs("non-existent-session")
            
            assert isinstance(result, list)
            assert len(result) == 0
    
    def test_read_logs_returns_empty_for_missing(self, temp_logs_dir):
        """Test that read_logs returns empty list for missing file."""
        with patch("src.utils.session_logger._logs_root_dir") as mock_root:
            mock_root.return_value = temp_logs_dir
            
            result = read_logs("missing-session")
            
            assert result == []
    
    def test_read_logs_parses_json(self, temp_logs_dir):
        """Test that read_logs parses JSON correctly."""
        with patch("src.utils.session_logger._logs_root_dir") as mock_root:
            mock_root.return_value = temp_logs_dir
            
            # Write test logs
            filepath = os.path.join(temp_logs_dir, "test-session.log")
            with open(filepath, 'w') as f:
                f.write('{"event": "start", "timestamp": "2024-01-01T00:00:00Z", "meta": {}}\n')
                f.write('{"event": "end", "timestamp": "2024-01-01T00:01:00Z", "meta": {}}\n')
            
            result = read_logs("test-session")
            
            assert len(result) == 2
            assert result[0]["event"] == "start"
            assert result[1]["event"] == "end"
    
    def test_read_logs_respects_limit(self, temp_logs_dir):
        """Test that read_logs respects the limit parameter."""
        with patch("src.utils.session_logger._logs_root_dir") as mock_root:
            mock_root.return_value = temp_logs_dir
            
            # Write many test logs
            filepath = os.path.join(temp_logs_dir, "test-session.log")
            with open(filepath, 'w') as f:
                for i in range(100):
                    f.write(f'{{"event": "event{i}", "timestamp": "2024-01-01T00:00:00Z", "meta": {{}}}}\n')
            
            result = read_logs("test-session", limit=10)
            
            assert len(result) == 10
            # Should return last 10
            assert result[0]["event"] == "event90"
    
    def test_read_logs_skips_malformed_lines(self, temp_logs_dir):
        """Test that read_logs skips malformed JSON lines."""
        with patch("src.utils.session_logger._logs_root_dir") as mock_root:
            mock_root.return_value = temp_logs_dir
            
            filepath = os.path.join(temp_logs_dir, "test-session.log")
            with open(filepath, 'w') as f:
                f.write('{"event": "good1", "meta": {}}\n')
                f.write('not valid json\n')
                f.write('{"event": "good2", "meta": {}}\n')
            
            result = read_logs("test-session")
            
            assert len(result) == 2
            assert result[0]["event"] == "good1"
            assert result[1]["event"] == "good2"
    
    def test_read_logs_skips_empty_lines(self, temp_logs_dir):
        """Test that read_logs skips empty lines."""
        with patch("src.utils.session_logger._logs_root_dir") as mock_root:
            mock_root.return_value = temp_logs_dir
            
            filepath = os.path.join(temp_logs_dir, "test-session.log")
            with open(filepath, 'w') as f:
                f.write('{"event": "event1", "meta": {}}\n')
                f.write('\n')
                f.write('   \n')
                f.write('{"event": "event2", "meta": {}}\n')
            
            result = read_logs("test-session")
            
            assert len(result) == 2


class TestSessionLoggerIntegration:
    """Integration tests for session logger."""
    
    @pytest.fixture
    def temp_logs_dir(self, temp_dir):
        """Create temporary logs directory."""
        logs_dir = os.path.join(temp_dir, "logs", "sessions")
        os.makedirs(logs_dir, exist_ok=True)
        return logs_dir
    
    def test_append_and_read_roundtrip(self, temp_logs_dir):
        """Test appending and reading logs roundtrip."""
        with patch("src.utils.session_logger._logs_root_dir") as mock_root:
            mock_root.return_value = temp_logs_dir
            
            session_id = "integration-test"
            
            append_log(session_id, "start", {"stage": 1})
            append_log(session_id, "progress", {"stage": 2, "percent": 50})
            append_log(session_id, "complete", {"stage": 3})
            
            logs = read_logs(session_id)
            
            assert len(logs) == 3
            assert logs[0]["event"] == "start"
            assert logs[1]["event"] == "progress"
            assert logs[1]["meta"]["percent"] == 50
            assert logs[2]["event"] == "complete"

