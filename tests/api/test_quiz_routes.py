"""
Tests for quiz API routes.

Tests the /api/v1/quiz/* endpoints for quiz generation and management.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient


class TestQuizCreation:
    """Tests for quiz creation endpoints."""
    
    @patch("src.api.routes.quiz.controller")
    def test_create_quiz_returns_session_id(self, mock_controller, client: TestClient, sample_quiz_request):
        """Test that creating a quiz returns a session ID."""
        mock_controller.create_quiz.return_value = Mock(
            sessionId="test-session-123",
            message="Started generating quiz: React.js Fundamentals"
        )
        
        response = client.post("/api/v1/quiz/quizzes", json=sample_quiz_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "sessionId" in data
        assert data["sessionId"] == "test-session-123"
        assert "message" in data
    
    @patch("src.api.routes.quiz.controller")
    def test_create_quiz_with_minimal_data(self, mock_controller, client: TestClient):
        """Test creating a quiz with only required fields."""
        mock_controller.create_quiz.return_value = Mock(
            sessionId="test-session-456",
            message="Started generating quiz: Python Basics"
        )
        
        response = client.post("/api/v1/quiz/quizzes", json={"topic": "Python Basics"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["sessionId"] == "test-session-456"
    
    def test_create_quiz_missing_topic_fails(self, client: TestClient):
        """Test that creating a quiz without topic fails."""
        response = client.post("/api/v1/quiz/quizzes", json={})
        
        assert response.status_code == 422  # Validation error
    
    @patch("src.api.routes.quiz.controller")
    def test_create_quiz_with_custom_settings(self, mock_controller, client: TestClient):
        """Test creating a quiz with custom settings."""
        mock_controller.create_quiz.return_value = Mock(
            sessionId="test-session-789",
            message="Started generating quiz"
        )
        
        request_data = {
            "topic": "Advanced React",
            "agentType": "tech",
            "questionCount": 30,
            "difficulty": "hard",
            "targetAudience": "senior developers"
        }
        
        response = client.post("/api/v1/quiz/quizzes", json=request_data)
        
        assert response.status_code == 200


class TestQuizTopicGeneration:
    """Tests for topic generation endpoint."""
    
    @patch("src.api.routes.quiz.controller")
    def test_generate_topic_returns_session(self, mock_controller, client: TestClient):
        """Test that generating a topic returns a session."""
        mock_controller.generate_topic.return_value = Mock(
            sessionId="topic-session-123",
            message="Started generating quiz for topic: Closures"
        )
        
        response = client.post("/api/v1/quiz/topics", json={
            "topic": "Closures",
            "questionCount": 5,
            "difficulty": "medium"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "sessionId" in data


class TestQuizSessionManagement:
    """Tests for quiz session management endpoints."""
    
    @patch("src.api.routes.quiz.controller")
    def test_list_sessions_returns_array(self, mock_controller, client: TestClient):
        """Test that listing sessions returns an array."""
        mock_controller.list_sessions.return_value = [
            {
                "sessionId": "session-1",
                "topic": "React",
                "status": "completed",
                "progress": {"current": 5, "total": 5}
            }
        ]
        
        response = client.get("/api/v1/quiz/sessions")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @patch("src.api.routes.quiz.controller")
    def test_list_sessions_with_status_filter(self, mock_controller, client: TestClient):
        """Test listing sessions with status filter."""
        mock_controller.list_sessions.return_value = []
        
        response = client.get("/api/v1/quiz/sessions?status=completed")
        
        assert response.status_code == 200
        mock_controller.list_sessions.assert_called_once_with("completed")
    
    @patch("src.api.routes.quiz.controller")
    def test_get_session_progress(self, mock_controller, client: TestClient, sample_session_data):
        """Test getting session progress."""
        mock_controller.get_session_progress.return_value = sample_session_data
        
        response = client.get("/api/v1/quiz/sessions/test-session-123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-session-123"
    
    @patch("src.api.routes.quiz.controller")
    def test_get_session_output(self, mock_controller, client: TestClient, sample_quiz_data):
        """Test getting session output."""
        mock_controller.get_session_output.return_value = {
            "status": "success",
            "session_id": "test-session-123",
            "quiz_data": sample_quiz_data
        }
        
        response = client.get("/api/v1/quiz/sessions/test-session-123/output")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "quiz_data" in data
    
    @patch("src.api.routes.quiz.controller")
    def test_cancel_session(self, mock_controller, client: TestClient):
        """Test cancelling a session."""
        mock_controller.cancel_session.return_value = {"message": "Session cancelled"}
        
        response = client.post("/api/v1/quiz/sessions/test-session-123/cancel")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Session cancelled"
    
    @patch("src.api.routes.quiz.controller")
    def test_resume_session(self, mock_controller, client: TestClient):
        """Test resuming a session."""
        mock_controller.retry_session.return_value = Mock(
            sessionId="test-session-123",
            message="Resuming quiz session"
        )
        
        response = client.post("/api/v1/quiz/sessions/test-session-123/resume")
        
        assert response.status_code == 200
    
    @patch("src.api.routes.quiz.controller")
    def test_retry_session(self, mock_controller, client: TestClient):
        """Test retrying a session."""
        mock_controller.retry_session.return_value = Mock(
            sessionId="test-session-123",
            message="Retrying quiz session"
        )
        
        response = client.post("/api/v1/quiz/sessions/test-session-123/retry")
        
        assert response.status_code == 200
    
    @patch("src.api.routes.quiz.controller")
    def test_delete_session(self, mock_controller, client: TestClient):
        """Test deleting a session."""
        mock_controller.delete_session.return_value = {"message": "Session deleted"}
        
        response = client.delete("/api/v1/quiz/sessions/test-session-123")
        
        assert response.status_code == 200


class TestQuizValidation:
    """Tests for quiz validation endpoint."""
    
    @patch("src.api.routes.quiz.controller")
    def test_validate_valid_quiz(self, mock_controller, client: TestClient, sample_quiz_data):
        """Test validating a valid quiz."""
        mock_controller.validate_quiz.return_value = Mock(
            ok=True,
            message="Validation successful"
        )
        
        response = client.post("/api/v1/quiz/validate", json={"quiz": sample_quiz_data})
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
    
    @patch("src.api.routes.quiz.controller")
    def test_validate_invalid_quiz(self, mock_controller, client: TestClient):
        """Test validating an invalid quiz."""
        mock_controller.validate_quiz.return_value = Mock(
            ok=False,
            message="Validation failed: Missing required field: categoryName"
        )
        
        response = client.post("/api/v1/quiz/validate", json={"quiz": {}})
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is False


class TestQuizUpload:
    """Tests for quiz upload endpoint."""
    
    @patch("src.api.routes.quiz.controller")
    def test_upload_quiz_success(self, mock_controller, client: TestClient, sample_quiz_data):
        """Test uploading a quiz successfully."""
        mock_controller.upload_quiz.return_value = Mock(
            ok=True,
            message="Quiz uploaded successfully"
        )
        
        response = client.post("/api/v1/quiz/upload", json={
            "quiz": sample_quiz_data,
            "apiUrl": "http://localhost:3000"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
    
    @patch("src.api.routes.quiz.controller")
    def test_upload_quiz_failure(self, mock_controller, client: TestClient, sample_quiz_data):
        """Test upload failure handling."""
        mock_controller.upload_quiz.return_value = Mock(
            ok=False,
            message="Upload failed: HTTP 500"
        )
        
        response = client.post("/api/v1/quiz/upload", json={
            "quiz": sample_quiz_data
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is False

