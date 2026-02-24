"""
Unit tests for quiz session manager.

Tests the QuizSessionManager class for quiz workflow session management.
"""

import pytest
import os
import json
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.agents.quiz.session.session_manager import QuizSessionManager
from src.core.session import SessionStatus


class TestQuizSessionManagerCreation:
    """Tests for quiz session creation."""
    
    @pytest.fixture
    def session_manager(self, temp_sessions_dir):
        """Create a quiz session manager with temp directory."""
        return QuizSessionManager(sessions_dir=temp_sessions_dir)
    
    def test_create_session_returns_id(self, session_manager):
        """Test that create_session returns a session ID."""
        session_id = session_manager.create_session(
            topic="React.js",
            description="React quiz",
            agent_type="tech"
        )
        
        assert session_id is not None
        assert isinstance(session_id, str)
        assert len(session_id) > 0
    
    def test_create_session_saves_file(self, session_manager, temp_sessions_dir):
        """Test that create_session saves a file."""
        session_id = session_manager.create_session(
            topic="JavaScript",
            description="JS quiz",
            agent_type="tech"
        )
        
        filepath = os.path.join(temp_sessions_dir, f"{session_id}.json")
        assert os.path.exists(filepath)
    
    def test_create_session_stores_correct_data(self, session_manager):
        """Test that create_session stores correct data."""
        session_id = session_manager.create_session(
            topic="Python",
            description="Python quiz",
            agent_type="tech",
            question_count=25,
            difficulty="hard"
        )
        
        session_data = session_manager.get_session(session_id)
        
        assert session_data["topic"] == "Python"
        assert session_data["description"] == "Python quiz"
        assert session_data["agent_type"] == "tech"
        assert session_data["question_count"] == 25
        assert session_data["difficulty"] == "hard"
        assert session_data["workflow_type"] == "quiz"
    
    def test_create_session_default_values(self, session_manager):
        """Test that create_session uses default values."""
        session_id = session_manager.create_session(
            topic="Default Test",
            description="Test",
            agent_type="generic"
        )
        
        session_data = session_manager.get_session(session_id)
        
        assert session_data["question_count"] == 20
        assert session_data["target_audience"] == "developers"
        assert session_data["difficulty"] == "medium"
    
    def test_create_session_initial_status(self, session_manager):
        """Test that new session has pending status."""
        session_id = session_manager.create_session(
            topic="Test",
            description="Test",
            agent_type="tech"
        )
        
        session_data = session_manager.get_session(session_id)
        
        assert session_data["status"] == "pending"
    
    def test_create_session_empty_questions(self, session_manager):
        """Test that new session has empty questions list."""
        session_id = session_manager.create_session(
            topic="Test",
            description="Test",
            agent_type="tech"
        )
        
        session_data = session_manager.get_session(session_id)
        
        assert session_data["questions"] == []
    
    def test_create_session_timestamps(self, session_manager):
        """Test that session has timestamps."""
        session_id = session_manager.create_session(
            topic="Test",
            description="Test",
            agent_type="tech"
        )
        
        session_data = session_manager.get_session(session_id)
        
        assert "created_at" in session_data
        assert "updated_at" in session_data


class TestQuizSessionManagerRetrieval:
    """Tests for session retrieval."""
    
    @pytest.fixture
    def session_manager(self, temp_sessions_dir):
        """Create a quiz session manager with temp directory."""
        return QuizSessionManager(sessions_dir=temp_sessions_dir)
    
    def test_get_session_existing(self, session_manager):
        """Test getting an existing session."""
        session_id = session_manager.create_session(
            topic="Test",
            description="Test",
            agent_type="tech"
        )
        
        session_data = session_manager.get_session(session_id)
        
        assert session_data is not None
        assert session_data["session_id"] == session_id
    
    def test_get_session_nonexistent(self, session_manager):
        """Test getting a nonexistent session returns None."""
        result = session_manager.get_session("nonexistent-session-id")
        
        assert result is None


class TestQuizSessionManagerMetadata:
    """Tests for category metadata operations."""
    
    @pytest.fixture
    def session_manager(self, temp_sessions_dir):
        """Create a quiz session manager with temp directory."""
        return QuizSessionManager(sessions_dir=temp_sessions_dir)
    
    def test_set_category_metadata(self, session_manager):
        """Test setting category metadata."""
        session_id = session_manager.create_session(
            topic="React",
            description="Test",
            agent_type="tech"
        )
        
        metadata = {
            "categoryName": "React.js Quiz",
            "categoryDescription": "Test your React knowledge",
            "categoryIcon": "⚛️"
        }
        
        session_manager.set_category_metadata(session_id, metadata)
        
        session_data = session_manager.get_session(session_id)
        assert session_data["category_metadata"] == metadata
    
    def test_set_category_metadata_nonexistent(self, session_manager):
        """Test setting metadata for nonexistent session raises error."""
        with pytest.raises(ValueError):
            session_manager.set_category_metadata("nonexistent", {"test": "data"})


class TestQuizSessionManagerQuestions:
    """Tests for question operations."""
    
    @pytest.fixture
    def session_manager(self, temp_sessions_dir):
        """Create a quiz session manager with temp directory."""
        return QuizSessionManager(sessions_dir=temp_sessions_dir)
    
    def test_add_question(self, session_manager):
        """Test adding a question to session."""
        session_id = session_manager.create_session(
            topic="Test",
            description="Test",
            agent_type="tech"
        )
        
        question = {
            "question": "What is React?",
            "options": ["A", "B", "C", "D"],
            "correctAnswer": 0,
            "explanation": "Test",
            "difficulty": "easy"
        }
        
        session_manager.add_question(session_id, question)
        
        session_data = session_manager.get_session(session_id)
        assert len(session_data["questions"]) == 1
        assert session_data["questions"][0]["question"] == "What is React?"
    
    def test_add_multiple_questions(self, session_manager):
        """Test adding multiple questions."""
        session_id = session_manager.create_session(
            topic="Test",
            description="Test",
            agent_type="tech"
        )
        
        for i in range(5):
            session_manager.add_question(session_id, {"question": f"Q{i}"})
        
        session_data = session_manager.get_session(session_id)
        assert len(session_data["questions"]) == 5
    
    def test_add_question_nonexistent(self, session_manager):
        """Test adding question to nonexistent session raises error."""
        with pytest.raises(ValueError):
            session_manager.add_question("nonexistent", {"question": "test"})


class TestQuizSessionManagerOutput:
    """Tests for output file operations."""
    
    @pytest.fixture
    def session_manager(self, temp_sessions_dir):
        """Create a quiz session manager with temp directory."""
        return QuizSessionManager(sessions_dir=temp_sessions_dir)
    
    def test_set_output_file(self, session_manager):
        """Test setting output file path."""
        session_id = session_manager.create_session(
            topic="Test",
            description="Test",
            agent_type="tech"
        )
        
        session_manager.set_output_file(session_id, "/path/to/output.json")
        
        session_data = session_manager.get_session(session_id)
        assert session_data["output_file"] == "/path/to/output.json"
    
    def test_set_output_file_with_quiz_data(self, session_manager, sample_quiz_data):
        """Test setting output file with quiz data."""
        session_id = session_manager.create_session(
            topic="Test",
            description="Test",
            agent_type="tech"
        )
        
        session_manager.set_output_file(session_id, "/path/to/output.json", sample_quiz_data)
        
        session_data = session_manager.get_session(session_id)
        assert session_data["output_file"] == "/path/to/output.json"
        assert session_data["quiz_data"] is not None
    
    def test_set_output_file_nonexistent(self, session_manager):
        """Test setting output file for nonexistent session raises error."""
        with pytest.raises(ValueError):
            session_manager.set_output_file("nonexistent", "/path/to/output.json")


class TestQuizSessionManagerProgress:
    """Tests for progress tracking."""
    
    @pytest.fixture
    def session_manager(self, temp_sessions_dir):
        """Create a quiz session manager with temp directory."""
        return QuizSessionManager(sessions_dir=temp_sessions_dir)
    
    def test_update_progress(self, session_manager):
        """Test updating progress."""
        session_id = session_manager.create_session(
            topic="Test",
            description="Test",
            agent_type="tech",
            question_count=10
        )
        
        session_manager.update_progress(
            session_id,
            completed=5,
            total=10,
            current_step="Generating question 5"
        )
        
        session_data = session_manager.get_session(session_id)
        assert session_data["progress"]["completed"] == 5
        assert session_data["progress"]["total"] == 10
        assert session_data["progress"]["percent"] == 50.0


class TestQuizSessionManagerStatus:
    """Tests for status updates."""
    
    @pytest.fixture
    def session_manager(self, temp_sessions_dir):
        """Create a quiz session manager with temp directory."""
        return QuizSessionManager(sessions_dir=temp_sessions_dir)
    
    def test_update_status_in_progress(self, session_manager):
        """Test updating status to in_progress."""
        session_id = session_manager.create_session(
            topic="Test",
            description="Test",
            agent_type="tech"
        )
        
        session_manager.update_status(session_id, SessionStatus.IN_PROGRESS)
        
        session_data = session_manager.get_session(session_id)
        assert session_data["status"] == "in_progress"
    
    def test_update_status_completed(self, session_manager):
        """Test updating status to completed."""
        session_id = session_manager.create_session(
            topic="Test",
            description="Test",
            agent_type="tech"
        )
        
        session_manager.update_status(session_id, SessionStatus.COMPLETED)
        
        session_data = session_manager.get_session(session_id)
        assert session_data["status"] == "completed"
    
    def test_update_status_with_error(self, session_manager):
        """Test updating status with error."""
        session_id = session_manager.create_session(
            topic="Test",
            description="Test",
            agent_type="tech"
        )
        
        session_manager.update_status(
            session_id,
            SessionStatus.FAILED,
            error="API rate limit exceeded"
        )
        
        session_data = session_manager.get_session(session_id)
        assert session_data["status"] == "failed"
        assert session_data["error"] == "API rate limit exceeded"


class TestQuizSessionManagerListing:
    """Tests for listing sessions."""
    
    @pytest.fixture
    def session_manager(self, temp_sessions_dir):
        """Create a quiz session manager with temp directory."""
        return QuizSessionManager(sessions_dir=temp_sessions_dir)
    
    def test_list_sessions_empty(self, session_manager):
        """Test listing sessions when none exist."""
        sessions = session_manager.list_sessions()
        assert sessions == []
    
    def test_list_sessions_multiple(self, session_manager):
        """Test listing multiple sessions."""
        for i in range(3):
            session_manager.create_session(
                topic=f"Topic {i}",
                description=f"Description {i}",
                agent_type="tech"
            )
        
        sessions = session_manager.list_sessions()
        assert len(sessions) == 3
    
    def test_list_sessions_filter_by_status(self, session_manager):
        """Test filtering sessions by status."""
        # Create sessions with different statuses
        s1 = session_manager.create_session(
            topic="Test 1",
            description="Test",
            agent_type="tech"
        )
        s2 = session_manager.create_session(
            topic="Test 2",
            description="Test",
            agent_type="tech"
        )
        
        session_manager.update_status(s1, SessionStatus.COMPLETED)
        
        completed = session_manager.list_sessions(status=SessionStatus.COMPLETED)
        pending = session_manager.list_sessions(status=SessionStatus.PENDING)
        
        assert len(completed) == 1
        assert len(pending) == 1


class TestQuizSessionManagerDeletion:
    """Tests for session deletion."""
    
    @pytest.fixture
    def session_manager(self, temp_sessions_dir):
        """Create a quiz session manager with temp directory."""
        return QuizSessionManager(sessions_dir=temp_sessions_dir)
    
    def test_delete_session(self, session_manager, temp_sessions_dir):
        """Test deleting a session."""
        session_id = session_manager.create_session(
            topic="Test",
            description="Test",
            agent_type="tech"
        )
        
        filepath = os.path.join(temp_sessions_dir, f"{session_id}.json")
        assert os.path.exists(filepath)
        
        session_manager.delete_session(session_id)
        
        assert not os.path.exists(filepath)
    
    def test_delete_session_then_get(self, session_manager):
        """Test that deleted session returns None."""
        session_id = session_manager.create_session(
            topic="Test",
            description="Test",
            agent_type="tech"
        )
        
        session_manager.delete_session(session_id)
        
        result = session_manager.get_session(session_id)
        assert result is None

