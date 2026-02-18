"""Unit tests for interview session manager."""

import pytest
import os
import tempfile
import shutil

from src.agents.interview.session import InterviewSessionManager
from src.core.session import SessionStatus


class TestInterviewSessionManager:
    """Tests for InterviewSessionManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.session_manager = InterviewSessionManager(sessions_dir=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_create_session(self):
        """Test session creation."""
        session_id = self.session_manager.create_session(
            name="Test Sheet",
            description="Test Description",
            agent_type="generic",
            roadmap="Tech"
        )
        
        assert session_id is not None
        assert len(session_id) > 0
        
        session = self.session_manager.get_session(session_id)
        assert session is not None
        assert session["name"] == "Test Sheet"
        assert session["description"] == "Test Description"
        assert session["agent_type"] == "generic"
        assert session["roadmap"] == "Tech"
    
    def test_get_session_not_found(self):
        """Test getting non-existent session."""
        session = self.session_manager.get_session("non-existent-id")
        assert session is None
    
    def test_update_session_status(self):
        """Test updating session status."""
        session_id = self.session_manager.create_session(
            name="Test",
            description="Test",
            agent_type="generic"
        )
        
        self.session_manager.update_status(session_id, SessionStatus.IN_PROGRESS, current_step="Processing...")
        
        session = self.session_manager.get_session(session_id)
        assert session["status"] == "in_progress"
        assert session["progress"]["current_step"] == "Processing..."
    
    def test_add_question(self):
        """Test adding question to session."""
        session_id = self.session_manager.create_session(
            name="Test",
            description="Test",
            agent_type="generic"
        )
        
        question = {
            "title": "Test Question",
            "question": "What is Python?",
            "answer": "",
            "frequency": "Asked Sometimes",
            "priority": "Medium",
            "companyTypes": ["Startup"]
        }
        
        self.session_manager.add_question(session_id, question)
        
        session = self.session_manager.get_session(session_id)
        assert len(session["questions"]) == 1
        assert session["questions"][0]["question"] == "What is Python?"

