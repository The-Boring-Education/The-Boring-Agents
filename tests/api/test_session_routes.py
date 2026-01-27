"""
Tests for session management API routes.

Tests the /api/v1/sessions/* endpoints for cross-workflow session management.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient


class TestActiveSessionsEndpoint:
    """Tests for listing active sessions across workflows."""
    
    @patch("src.api.routes.session.controller")
    def test_list_active_sessions_returns_both_types(self, mock_controller, client: TestClient):
        """Test that listing active sessions returns both quiz and interview sessions."""
        mock_controller.list_active_sessions.return_value = {
            "ok": True,
            "quiz": [
                {"session_id": "quiz-1", "status": "in_progress"}
            ],
            "interview": [
                {"session_id": "interview-1", "status": "in_progress"}
            ]
        }
        
        response = client.get("/api/v1/sessions/active")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "interview" in data
    
    @patch("src.api.routes.session.controller")
    def test_list_active_sessions_empty(self, mock_controller, client: TestClient):
        """Test listing active sessions when none exist."""
        mock_controller.list_active_sessions.return_value = {
            "ok": True,
            "quiz": [],
            "interview": []
        }
        
        response = client.get("/api/v1/sessions/active")
        
        assert response.status_code == 200
        data = response.json()
        assert data["interview"] == []


class TestSessionLogsEndpoint:
    """Tests for session logs endpoint."""
    
    @patch("src.api.routes.session.controller")
    def test_get_session_logs(self, mock_controller, client: TestClient):
        """Test getting session logs."""
        mock_controller.get_session_logs.return_value = {
            "ok": True,
            "session_id": "test-session-123",
            "logs": [
                {"timestamp": "2024-01-01T00:00:00Z", "action": "start"},
                {"timestamp": "2024-01-01T00:01:00Z", "action": "complete"}
            ]
        }
        
        response = client.get("/api/v1/sessions/logs/test-session-123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "logs" in data
        assert len(data["logs"]) == 2
    
    @patch("src.api.routes.session.controller")
    def test_get_session_logs_with_limit(self, mock_controller, client: TestClient):
        """Test getting session logs with limit parameter."""
        mock_controller.get_session_logs.return_value = {
            "ok": True,
            "session_id": "test-session-123",
            "logs": []
        }
        
        response = client.get("/api/v1/sessions/logs/test-session-123?limit=50")
        
        assert response.status_code == 200
        mock_controller.get_session_logs.assert_called_once_with("test-session-123", 50)
    
    def test_get_session_logs_invalid_limit(self, client: TestClient):
        """Test getting session logs with invalid limit."""
        # Limit must be between 1 and 2000
        response = client.get("/api/v1/sessions/logs/test-session-123?limit=0")
        
        assert response.status_code == 422
    
    def test_get_session_logs_limit_too_high(self, client: TestClient):
        """Test getting session logs with limit too high."""
        response = client.get("/api/v1/sessions/logs/test-session-123?limit=5000")
        
        assert response.status_code == 422


class TestSessionDetailEndpoint:
    """Tests for session detail endpoint."""
    
    @patch("src.api.routes.session.controller")
    def test_get_session_detail(self, mock_controller, client: TestClient, sample_session_data):
        """Test getting session detail."""
        mock_controller.get_session_detail.return_value = {
            "ok": True,
            "data": sample_session_data
        }
        
        response = client.get("/api/v1/sessions/detail/test-session-123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "data" in data
    
    @patch("src.api.routes.session.controller")
    def test_get_session_detail_not_found(self, mock_controller, client: TestClient):
        """Test getting session detail for non-existent session."""
        from fastapi import HTTPException
        mock_controller.get_session_detail.side_effect = HTTPException(
            status_code=404,
            detail="Session not found"
        )
        
        response = client.get("/api/v1/sessions/detail/non-existent")
        
        assert response.status_code == 404


class TestResumeSessionEndpoint:
    """Tests for resume session endpoint."""
    
    @patch("src.api.routes.session.controller")
    def test_resume_session_success(self, mock_controller, client: TestClient):
        """Test resuming a session successfully."""
        mock_controller.resume_session.return_value = {
            "ok": True,
            "result": {"status": "resumed"}
        }
        
        response = client.post("/api/v1/sessions/resume/test-session-123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
    
    @patch("src.api.routes.session.controller")
    def test_resume_session_not_found(self, mock_controller, client: TestClient):
        """Test resuming a non-existent session."""
        from fastapi import HTTPException
        mock_controller.resume_session.side_effect = HTTPException(
            status_code=404,
            detail="Unable to resume session"
        )
        
        response = client.post("/api/v1/sessions/resume/non-existent")
        
        assert response.status_code == 404


class TestDeleteSessionEndpoint:
    """Tests for delete session endpoint."""
    
    @patch("src.api.routes.session.controller")
    def test_delete_session_success(self, mock_controller, client: TestClient):
        """Test deleting a session successfully."""
        mock_controller.delete_session.return_value = {
            "ok": True,
            "removed": {
                "progress_files": ["file1.json"],
                "logs_deleted": True
            }
        }
        
        response = client.delete("/api/v1/sessions/test-session-123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "removed" in data
    
    @patch("src.api.routes.session.controller")
    def test_delete_session_partial_cleanup(self, mock_controller, client: TestClient):
        """Test deleting a session with partial cleanup."""
        mock_controller.delete_session.return_value = {
            "ok": True,
            "removed": {
                "progress_files": [],
                "logs_deleted": False
            }
        }
        
        response = client.delete("/api/v1/sessions/test-session-123")
        
        assert response.status_code == 200

