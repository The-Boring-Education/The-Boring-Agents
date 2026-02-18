"""Comprehensive integration tests for interview workflow."""

import pytest
import os
import tempfile
import shutil
import json
from unittest.mock import Mock, patch, MagicMock

from src.agents.interview.workflow import InterviewWorkflowOrchestrator
from src.agents.interview.session import InterviewSessionManager
from src.agents.interview.workflow import InterviewWorkflowState


class TestWorkflowIntegration:
    """Comprehensive integration tests for the complete workflow."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.sessions_dir = os.path.join(self.temp_dir, "sessions")
        os.makedirs(self.sessions_dir, exist_ok=True)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('src.agents.interview.workflow.InterviewSessionManager')
    def test_orchestrator_initialization(self, mock_session_manager):
        """Test orchestrator can be initialized."""
        orchestrator = InterviewWorkflowOrchestrator()
        assert orchestrator is not None
        assert hasattr(orchestrator, 'start_generation')
        assert hasattr(orchestrator, 'execute_workflow')
        assert hasattr(orchestrator, 'get_session_status')
        assert hasattr(orchestrator, 'resume_session')
    
    def test_start_generation_creates_session(self):
        """Test starting generation creates a session."""
        with patch('src.agents.interview.workflow.InterviewSessionManager') as mock_session_class:
            mock_session = Mock()
            mock_session.create_session.return_value = "test-session-123"
            mock_session.get_session.return_value = {
                "session_id": "test-session-123",
                "name": "Test Sheet",
                "status": "pending"
            }
            mock_session_class.return_value = mock_session
            
            orchestrator = InterviewWorkflowOrchestrator()
            orchestrator.session_manager = mock_session
            
            session_id = orchestrator.start_generation(
                name="Test Sheet",
                description="Test Description",
                agent_type="generic",
                roadmap="Tech"
            )
            
            assert session_id == "test-session-123"
            mock_session.create_session.assert_called_once()
    
    def test_start_generation_validates_agent_type(self):
        """Test that invalid agent types are rejected."""
        orchestrator = InterviewWorkflowOrchestrator()
        
        with pytest.raises(ValueError, match="Invalid agent type"):
            orchestrator.start_generation(
                name="Test",
                description="Test",
                agent_type="invalid_type",
                roadmap="Tech"
            )
    
    @patch('src.agents.interview.workflow.create_workflow_graph')
    def test_execute_workflow_with_mocked_llm(self, mock_create_graph):
        """Test workflow execution with mocked LLM."""
        # Create a mock graph that returns a completed state
        mock_graph = Mock()
        mock_graph.invoke.return_value = {
            "session_id": "test-123",
            "name": "Test Sheet",
            "status": "completed",
            "meta": "Generated metadata",
            "questions": [
                {"title": "Q1", "question": "Question 1", "answer": "Answer 1"}
            ],
            "output_file": "/path/to/output.json",
            "sheet_data": {"name": "Test Sheet"}
        }
        mock_create_graph.return_value = mock_graph
        
        # Mock session manager
        with patch('src.agents.interview.workflow.InterviewSessionManager') as mock_session_class:
            mock_session = Mock()
            mock_session.get_session.return_value = {
                "session_id": "test-123",
                "name": "Test Sheet",
                "description": "Test Description",
                "agent_type": "generic",
                "roadmap": "Tech",
                "status": "pending",
                "meta": None,
                "questions": [],
                "progress": {"completed": 0, "total": 0},
                "output_file": None
            }
            mock_session_class.return_value = mock_session
            
            orchestrator = InterviewWorkflowOrchestrator()
            orchestrator.graph = mock_graph
            orchestrator.session_manager = mock_session
            
            result = orchestrator.execute_workflow("test-123")
            
            assert result["status"] == "completed"
            assert "session_id" in result
            mock_graph.invoke.assert_called_once()
    
    def test_get_session_status(self):
        """Test getting session status."""
        with patch('src.agents.interview.workflow.InterviewSessionManager') as mock_session_class:
            mock_session = Mock()
            mock_session.get_session.return_value = {
                "session_id": "test-123",
                "name": "Test Sheet",
                "status": "in_progress",
                "progress": {"completed": 5, "total": 10},
                "output_file": None,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
            mock_session_class.return_value = mock_session
            
            orchestrator = InterviewWorkflowOrchestrator()
            orchestrator.session_manager = mock_session
            
            status = orchestrator.get_session_status("test-123")
            
            assert status["session_id"] == "test-123"
            assert status["name"] == "Test Sheet"
            assert status["status"] == "in_progress"
            assert "progress" in status
    
    def test_get_session_status_not_found(self):
        """Test getting status for non-existent session."""
        with patch('src.agents.interview.workflow.InterviewSessionManager') as mock_session_class:
            mock_session = Mock()
            mock_session.get_session.return_value = None
            mock_session_class.return_value = mock_session
            
            orchestrator = InterviewWorkflowOrchestrator()
            orchestrator.session_manager = mock_session
            
            with pytest.raises(ValueError, match="Session.*not found"):
                orchestrator.get_session_status("non-existent")
    
    def test_resume_session(self):
        """Test resuming a session."""
        with patch('src.agents.interview.workflow.create_workflow_graph') as mock_create_graph:
            mock_graph = Mock()
            mock_graph.invoke.return_value = {
                "session_id": "test-123",
                "status": "completed"
            }
            mock_create_graph.return_value = mock_graph
            
            with patch('src.agents.interview.workflow.InterviewSessionManager') as mock_session_class:
                mock_session = Mock()
                mock_session.get_session.return_value = {
                    "session_id": "test-123",
                    "name": "Test Sheet",
                    "description": "Test Description",
                    "agent_type": "generic",
                    "roadmap": "Tech",
                    "status": "answers_generating",
                    "meta": "Metadata",
                    "questions": [
                        {"title": "Q1", "question": "Question 1", "answer": ""}
                    ],
                    "progress": {"completed": 0, "total": 1},
                    "output_file": None
                }
                mock_session_class.return_value = mock_session
                
                orchestrator = InterviewWorkflowOrchestrator()
                orchestrator.graph = mock_graph
                orchestrator.session_manager = mock_session
                
                result = orchestrator.resume_session("test-123")
                
                assert result["status"] == "completed"
                mock_graph.invoke.assert_called_once()


class TestWorkflowResume:
    """Tests for workflow resume functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_resume_from_metadata_stage(self):
        """Test resuming from metadata generation stage."""
        with patch('src.agents.interview.workflow.create_workflow_graph') as mock_create_graph:
            mock_graph = Mock()
            mock_graph.invoke.return_value = {
                "session_id": "test-123",
                "status": "completed",
                "meta": "Generated metadata"
            }
            mock_create_graph.return_value = mock_graph
            
            with patch('src.agents.interview.workflow.InterviewSessionManager') as mock_session_class:
                mock_session = Mock()
                mock_session.get_session.return_value = {
                    "session_id": "test-123",
                    "name": "Test Sheet",
                    "description": "Test Description",
                    "agent_type": "generic",
                    "roadmap": "Tech",
                    "status": "metadata_generating",
                    "meta": None,
                    "questions": [],
                    "progress": {"completed": 0, "total": 0},
                    "output_file": None
                }
                mock_session_class.return_value = mock_session
                
                orchestrator = InterviewWorkflowOrchestrator()
                orchestrator.graph = mock_graph
                orchestrator.session_manager = mock_session
                
                result = orchestrator.execute_workflow("test-123")
                
                assert result["status"] == "completed"
                # Should have called invoke to continue from metadata stage
                mock_graph.invoke.assert_called_once()
    
    def test_resume_from_questions_stage(self):
        """Test resuming from questions generation stage."""
        with patch('src.agents.interview.workflow.create_workflow_graph') as mock_create_graph:
            mock_graph = Mock()
            mock_graph.invoke.return_value = {
                "session_id": "test-123",
                "status": "completed",
                "meta": "Metadata",
                "questions": [{"title": "Q1", "question": "Q1", "answer": ""}]
            }
            mock_create_graph.return_value = mock_graph
            
            with patch('src.agents.interview.workflow.InterviewSessionManager') as mock_session_class:
                mock_session = Mock()
                mock_session.get_session.return_value = {
                    "session_id": "test-123",
                    "name": "Test Sheet",
                    "description": "Test Description",
                    "agent_type": "generic",
                    "roadmap": "Tech",
                    "status": "questions_generating",
                    "meta": "Metadata",
                    "questions": [],
                    "progress": {"completed": 0, "total": 0},
                    "output_file": None
                }
                mock_session_class.return_value = mock_session
                
                orchestrator = InterviewWorkflowOrchestrator()
                orchestrator.graph = mock_graph
                orchestrator.session_manager = mock_session
                
                result = orchestrator.execute_workflow("test-123")
                
                assert result["status"] == "completed"
                mock_graph.invoke.assert_called_once()
    
    def test_resume_from_answers_stage(self):
        """Test resuming from answers generation stage."""
        with patch('src.agents.interview.workflow.create_workflow_graph') as mock_create_graph:
            mock_graph = Mock()
            mock_graph.invoke.return_value = {
                "session_id": "test-123",
                "status": "completed",
                "meta": "Metadata",
                "questions": [
                    {"title": "Q1", "question": "Q1", "answer": "Answer 1"}
                ]
            }
            mock_create_graph.return_value = mock_graph
            
            with patch('src.agents.interview.workflow.InterviewSessionManager') as mock_session_class:
                mock_session = Mock()
                mock_session.get_session.return_value = {
                    "session_id": "test-123",
                    "name": "Test Sheet",
                    "description": "Test Description",
                    "agent_type": "generic",
                    "roadmap": "Tech",
                    "status": "answers_generating",
                    "meta": "Metadata",
                    "questions": [
                        {"title": "Q1", "question": "Q1", "answer": ""}
                    ],
                    "progress": {"completed": 0, "total": 1},
                    "output_file": None
                }
                mock_session_class.return_value = mock_session
                
                orchestrator = InterviewWorkflowOrchestrator()
                orchestrator.graph = mock_graph
                orchestrator.session_manager = mock_session
                
                result = orchestrator.execute_workflow("test-123")
                
                assert result["status"] == "completed"
                mock_graph.invoke.assert_called_once()
    
    def test_resume_already_completed(self):
        """Test resuming an already completed session."""
        with patch('src.agents.interview.workflow.InterviewSessionManager') as mock_session_class:
            mock_session = Mock()
            mock_session.get_session.return_value = {
                "session_id": "test-123",
                "name": "Test Sheet",
                "description": "Test Description",
                "agent_type": "generic",
                "roadmap": "Tech",
                "status": "completed",
                "meta": "Metadata",
                "questions": [],
                "progress": {"completed": 10, "total": 10},
                "output_file": "/path/to/output.json"
            }
            mock_session_class.return_value = mock_session
            
            orchestrator = InterviewWorkflowOrchestrator()
            orchestrator.session_manager = mock_session
            
            result = orchestrator.execute_workflow("test-123")
            
            assert result["status"] == "completed"
            assert result["output_file"] == "/path/to/output.json"


class TestWorkflowErrorHandling:
    """Tests for workflow error handling and recovery."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_workflow_handles_llm_errors(self):
        """Test that workflow handles LLM API errors gracefully."""
        with patch('src.agents.interview.workflow.create_workflow_graph') as mock_create_graph:
            mock_graph = Mock()
            mock_graph.invoke.side_effect = Exception("LLM API Error")
            mock_create_graph.return_value = mock_graph
            
            with patch('src.agents.interview.workflow.InterviewSessionManager') as mock_session_class:
                mock_session = Mock()
                mock_session.get_session.return_value = {
                    "session_id": "test-123",
                    "name": "Test Sheet",
                    "description": "Test Description",
                    "agent_type": "generic",
                    "roadmap": "Tech",
                    "status": "pending",
                    "meta": None,
                    "questions": [],
                    "progress": {"completed": 0, "total": 0},
                    "output_file": None
                }
                mock_session_class.return_value = mock_session
                
                orchestrator = InterviewWorkflowOrchestrator()
                orchestrator.graph = mock_graph
                orchestrator.session_manager = mock_session
                
                with pytest.raises(Exception):
                    orchestrator.execute_workflow("test-123")
                
                # Should have updated session status to failed
                mock_session.update_status.assert_called_once()
                call_args = mock_session.update_session_status.call_args
                assert call_args[0][0] == "test-123"
                assert call_args[0][1] == "failed"
    
    def test_workflow_handles_missing_session(self):
        """Test that workflow handles missing session gracefully."""
        with patch('src.agents.interview.workflow.InterviewSessionManager') as mock_session_class:
            mock_session = Mock()
            mock_session.get_session.return_value = None
            mock_session_class.return_value = mock_session
            
            orchestrator = InterviewWorkflowOrchestrator()
            orchestrator.session_manager = mock_session
            
            with pytest.raises(ValueError, match="Session.*not found"):
                orchestrator.execute_workflow("non-existent")
    
    def test_workflow_handles_invalid_state(self):
        """Test that workflow handles invalid state gracefully."""
        with patch('src.agents.interview.workflow.create_workflow_graph') as mock_create_graph:
            mock_graph = Mock()
            mock_graph.invoke.side_effect = ValueError("Invalid state")
            mock_create_graph.return_value = mock_graph
            
            with patch('src.agents.interview.workflow.InterviewSessionManager') as mock_session_class:
                mock_session = Mock()
                mock_session.get_session.return_value = {
                    "session_id": "test-123",
                    "name": "Test Sheet",
                    "description": "Test Description",
                    "agent_type": "generic",
                    "roadmap": "Tech",
                    "status": "pending",
                    "meta": None,
                    "questions": [],
                    "progress": {"completed": 0, "total": 0},
                    "output_file": None
                }
                mock_session_class.return_value = mock_session
                
                orchestrator = InterviewWorkflowOrchestrator()
                orchestrator.graph = mock_graph
                orchestrator.session_manager = mock_session
                
                with pytest.raises(ValueError):
                    orchestrator.execute_workflow("test-123")
                
                # Should have updated session status
                mock_session.update_status.assert_called_once()

