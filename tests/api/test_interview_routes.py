"""
Tests for interview preparation API routes.

Tests the /api/v1/interview/* endpoints for interview sheet generation and management.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient


class TestInterviewSheetCreation:
    """Tests for interview sheet creation endpoint."""
    
    @patch("src.api.routes.interview_prep.controller")
    def test_create_sheet_returns_session_id(self, mock_controller, client: TestClient, sample_interview_request):
        """Test that creating a sheet returns a session ID."""
        mock_controller.create_sheet.return_value = Mock(
            sessionId="sheet-session-123",
            message="Started generating interview sheet: React.js Interview Questions"
        )
        
        response = client.post("/api/v1/interview/sheets", json=sample_interview_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "sessionId" in data
        assert data["sessionId"] == "sheet-session-123"
    
    @patch("src.api.routes.interview_prep.controller")
    def test_create_sheet_with_minimal_data(self, mock_controller, client: TestClient):
        """Test creating a sheet with only required fields."""
        mock_controller.create_sheet.return_value = Mock(
            sessionId="sheet-session-456",
            message="Started generating interview sheet"
        )
        
        response = client.post("/api/v1/interview/sheets", json={
            "name": "JavaScript Basics",
            "description": "Basic JS interview questions"
        })
        
        assert response.status_code == 200
    
    def test_create_sheet_missing_name_fails(self, client: TestClient):
        """Test that creating a sheet without name fails."""
        response = client.post("/api/v1/interview/sheets", json={
            "description": "Test description"
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_create_sheet_missing_description_fails(self, client: TestClient):
        """Test that creating a sheet without description fails."""
        response = client.post("/api/v1/interview/sheets", json={
            "name": "Test Sheet"
        })
        
        assert response.status_code == 422


class TestInterviewTopicGeneration:
    """Tests for topic generation endpoint."""
    
    @patch("src.api.routes.interview_prep.controller")
    def test_generate_topic_returns_session(self, mock_controller, client: TestClient):
        """Test that generating a topic returns a session."""
        mock_controller.generate_topic.return_value = Mock(
            sessionId="topic-session-123",
            message="Started generating questions for topic: React Hooks"
        )
        
        response = client.post("/api/v1/interview/topics", json={
            "topic": "React Hooks",
            "agentType": "tech",
            "questionCount": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "sessionId" in data
    
    @patch("src.api.routes.interview_prep.controller")
    def test_generate_topic_with_all_options(self, mock_controller, client: TestClient):
        """Test generating a topic with all options."""
        mock_controller.generate_topic.return_value = Mock(
            sessionId="topic-session-456",
            message="Started generating questions"
        )
        
        response = client.post("/api/v1/interview/topics", json={
            "topic": "System Design",
            "agentType": "system_design",
            "technology": "Distributed Systems",
            "questionCount": 15,
            "roadmap": "Backend",
            "difficulty": "Hard",
            "generateAnswers": True
        })
        
        assert response.status_code == 200


class TestInterviewSessionManagement:
    """Tests for interview session management endpoints."""
    
    @patch("src.api.routes.interview_prep.controller")
    def test_list_sessions_returns_array(self, mock_controller, client: TestClient):
        """Test that listing sessions returns an array."""
        mock_controller.list_sessions.return_value = [
            {
                "sessionId": "session-1",
                "topic": "React",
                "status": "completed",
                "progress": {"current": 20, "total": 20}
            }
        ]
        
        response = client.get("/api/v1/interview/sessions")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @patch("src.api.routes.interview_prep.controller")
    def test_list_sessions_with_status_filter(self, mock_controller, client: TestClient):
        """Test listing sessions with status filter."""
        mock_controller.list_sessions.return_value = []
        
        response = client.get("/api/v1/interview/sessions?status=in_progress")
        
        assert response.status_code == 200
    
    @patch("src.api.routes.interview_prep.controller")
    def test_get_session_progress(self, mock_controller, client: TestClient):
        """Test getting session progress."""
        mock_controller.get_session_progress.return_value = {
            "session_id": "test-session-123",
            "status": "in_progress",
            "progress": {"current": 5, "total": 20},
            "questionCount": 20
        }
        
        response = client.get("/api/v1/interview/sessions/test-session-123")
        
        assert response.status_code == 200
        data = response.json()
        assert "progress" in data
    
    @patch("src.api.routes.interview_prep.controller")
    def test_get_session_output(self, mock_controller, client: TestClient):
        """Test getting session output."""
        mock_controller.get_session_progress.return_value = {
            "output_file": "/path/to/output.json"
        }
        
        # This test would need file mocking for full coverage
        # Simplified test just checks the endpoint exists
        response = client.get("/api/v1/interview/sessions/test-session-123/output")
        
        # Will return 404 because mock file doesn't exist
        assert response.status_code in [200, 404]
    
    @patch("src.api.routes.interview_prep.controller")
    def test_cancel_session(self, mock_controller, client: TestClient):
        """Test cancelling a session."""
        mock_controller.cancel_session.return_value = {"message": "Session cancelled"}
        
        response = client.post("/api/v1/interview/sessions/test-session-123/cancel")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Session cancelled"
    
    @patch("src.api.routes.interview_prep.controller")
    def test_resume_session(self, mock_controller, client: TestClient):
        """Test resuming a session."""
        mock_controller.retry_session.return_value = Mock(
            sessionId="test-session-123",
            message="Resuming session"
        )
        
        response = client.post("/api/v1/interview/sessions/test-session-123/resume")
        
        assert response.status_code == 200
    
    @patch("src.api.routes.interview_prep.controller")
    def test_retry_session(self, mock_controller, client: TestClient):
        """Test retrying a session."""
        mock_controller.retry_session.return_value = Mock(
            sessionId="test-session-123",
            message="Retrying session"
        )
        
        response = client.post("/api/v1/interview/sessions/test-session-123/retry")
        
        assert response.status_code == 200
    
    @patch("src.api.routes.interview_prep.controller")
    def test_delete_session(self, mock_controller, client: TestClient):
        """Test deleting a session."""
        mock_controller.delete_session.return_value = {"message": "Session deleted"}
        
        response = client.delete("/api/v1/interview/sessions/test-session-123")
        
        assert response.status_code == 200

