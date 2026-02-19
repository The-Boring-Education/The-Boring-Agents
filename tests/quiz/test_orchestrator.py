"""
E2E and integration tests for Quiz workflow orchestrator.

Tests the complete quiz generation workflow from start to finish.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from src.agents.quiz.workflow.orchestrator import QuizWorkflowOrchestrator
from src.core.session import SessionStatus


class TestQuizWorkflowOrchestratorInit:
    """Tests for QuizWorkflowOrchestrator initialization."""
    
    def test_initialization(self, temp_sessions_dir):
        """Test that orchestrator can be initialized."""
        with patch('src.agents.quiz.workflow.orchestrator.create_workflow_graph') as mock_graph:
            mock_graph.return_value = MagicMock()
            
            with patch('src.agents.quiz.session.session_manager.QuizSessionManager') as mock_manager:
                mock_manager.return_value = MagicMock()
                
                orchestrator = QuizWorkflowOrchestrator()
                assert orchestrator is not None
    
    def test_has_session_manager(self, temp_sessions_dir):
        """Test that orchestrator has a session manager."""
        with patch('src.agents.quiz.workflow.orchestrator.create_workflow_graph') as mock_graph:
            mock_graph.return_value = MagicMock()
            
            orchestrator = QuizWorkflowOrchestrator()
            assert orchestrator.session_manager is not None
    
    def test_has_workflow_graph(self, temp_sessions_dir):
        """Test that orchestrator has a workflow graph."""
        with patch('src.agents.quiz.workflow.orchestrator.create_workflow_graph') as mock_graph:
            mock_graph.return_value = MagicMock()
            
            orchestrator = QuizWorkflowOrchestrator()
            assert orchestrator.graph is not None


class TestQuizWorkflowOrchestratorStartGeneration:
    """Tests for start_generation method."""
    
    @pytest.fixture
    def mock_orchestrator(self, temp_sessions_dir):
        """Create a mock orchestrator."""
        with patch('src.agents.quiz.workflow.orchestrator.create_workflow_graph') as mock_graph:
            mock_graph.return_value = MagicMock()
            
            orchestrator = QuizWorkflowOrchestrator()
            orchestrator.session_manager.sessions_dir = temp_sessions_dir
            return orchestrator
    
    def test_start_generation_returns_session_id(self, mock_orchestrator):
        """Test that start_generation returns a session ID."""
        session_id = mock_orchestrator.start_generation(
            topic="React.js",
            description="React quiz",
            agent_type="tech",
            question_count=10
        )
        
        assert session_id is not None
        assert isinstance(session_id, str)
    
    def test_start_generation_creates_session(self, mock_orchestrator):
        """Test that start_generation creates a session."""
        session_id = mock_orchestrator.start_generation(
            topic="JavaScript",
            description="JS quiz",
            agent_type="tech"
        )
        
        session = mock_orchestrator.session_manager.get_session(session_id)
        assert session is not None
    
    def test_start_generation_with_all_params(self, mock_orchestrator):
        """Test start_generation with all parameters."""
        session_id = mock_orchestrator.start_generation(
            topic="Python",
            description="Python quiz",
            agent_type="tech",
            question_count=25,
            target_audience="beginners",
            difficulty="easy"
        )
        
        session = mock_orchestrator.session_manager.get_session(session_id)
        assert session["topic"] == "Python"
        assert session["question_count"] == 25
        assert session["target_audience"] == "beginners"
        assert session["difficulty"] == "easy"


class TestQuizWorkflowOrchestratorExecuteWorkflow:
    """Tests for execute_workflow method."""
    
    @pytest.fixture
    def mock_orchestrator(self, temp_sessions_dir):
        """Create a mock orchestrator with mocked graph."""
        with patch('src.agents.quiz.workflow.orchestrator.create_workflow_graph') as mock_graph:
            mock_invoke = MagicMock()
            mock_invoke.invoke.return_value = {
                "status": "completed",
                "session_id": "test-123",
                "output_file": "/path/to/output.json",
                "quiz_data": {"categoryName": "Test"}
            }
            mock_graph.return_value = mock_invoke
            
            orchestrator = QuizWorkflowOrchestrator()
            orchestrator.session_manager.sessions_dir = temp_sessions_dir
            return orchestrator
    
    def test_execute_workflow_success(self, mock_orchestrator):
        """Test successful workflow execution."""
        # Create a session first
        session_id = mock_orchestrator.start_generation(
            topic="Test",
            description="Test quiz",
            agent_type="tech"
        )
        
        # Execute workflow
        result = mock_orchestrator.execute_workflow(session_id)
        
        assert result["status"] == "completed"
        assert result["session_id"] == session_id
    
    def test_execute_workflow_nonexistent_session(self, mock_orchestrator):
        """Test executing workflow for nonexistent session raises error."""
        with pytest.raises(ValueError) as exc_info:
            mock_orchestrator.execute_workflow("nonexistent-session")
        
        assert "not found" in str(exc_info.value).lower()
    
    def test_execute_workflow_already_completed(self, mock_orchestrator):
        """Test executing workflow for completed session returns early."""
        session_id = mock_orchestrator.start_generation(
            topic="Test",
            description="Test",
            agent_type="tech"
        )
        
        # Mark as completed
        mock_orchestrator.session_manager.update_status(session_id, SessionStatus.COMPLETED)
        session = mock_orchestrator.session_manager.get_session(session_id)
        session["output_file"] = "/path/to/output.json"
        mock_orchestrator.session_manager.save_session(session_id, session)
        
        # Re-mock to return completed state
        mock_orchestrator.graph.invoke.return_value = {
            "status": "completed",
            "output_file": "/path/to/output.json"
        }
        
        result = mock_orchestrator.execute_workflow(session_id)
        
        assert result["status"] == "completed"


class TestQuizWorkflowOrchestratorGetSessionStatus:
    """Tests for get_session_status method."""
    
    @pytest.fixture
    def mock_orchestrator(self, temp_sessions_dir):
        """Create a mock orchestrator."""
        with patch('src.agents.quiz.workflow.orchestrator.create_workflow_graph') as mock_graph:
            mock_graph.return_value = MagicMock()
            
            orchestrator = QuizWorkflowOrchestrator()
            orchestrator.session_manager.sessions_dir = temp_sessions_dir
            return orchestrator
    
    def test_get_session_status_existing(self, mock_orchestrator):
        """Test getting status for existing session."""
        session_id = mock_orchestrator.start_generation(
            topic="React",
            description="Test",
            agent_type="tech"
        )
        
        status = mock_orchestrator.get_session_status(session_id)
        
        assert status["session_id"] == session_id
        assert status["topic"] == "React"
        assert status["status"] == "pending"
    
    def test_get_session_status_nonexistent(self, mock_orchestrator):
        """Test getting status for nonexistent session raises error."""
        with pytest.raises(ValueError):
            mock_orchestrator.get_session_status("nonexistent")
    
    def test_get_session_status_includes_progress(self, mock_orchestrator):
        """Test that status includes progress information."""
        session_id = mock_orchestrator.start_generation(
            topic="Test",
            description="Test",
            agent_type="tech",
            question_count=10
        )
        
        mock_orchestrator.session_manager.update_progress(
            session_id,
            completed=5,
            total=10
        )
        
        status = mock_orchestrator.get_session_status(session_id)
        
        assert "progress" in status
        assert status["progress"]["completed"] == 5
    
    def test_get_session_status_includes_question_count(self, mock_orchestrator):
        """Test that status includes question_count."""
        session_id = mock_orchestrator.start_generation(
            topic="Test",
            description="Test",
            agent_type="tech",
            question_count=25
        )
        
        status = mock_orchestrator.get_session_status(session_id)
        
        assert status["question_count"] == 25


class TestQuizWorkflowOrchestratorUpdateSession:
    """Tests for _update_session_from_state method."""
    
    @pytest.fixture
    def mock_orchestrator(self, temp_sessions_dir):
        """Create a mock orchestrator."""
        with patch('src.agents.quiz.workflow.orchestrator.create_workflow_graph') as mock_graph:
            mock_graph.return_value = MagicMock()
            
            orchestrator = QuizWorkflowOrchestrator()
            orchestrator.session_manager.sessions_dir = temp_sessions_dir
            return orchestrator
    
    def test_update_session_category_metadata(self, mock_orchestrator):
        """Test updating session with category metadata."""
        session_id = mock_orchestrator.start_generation(
            topic="Test",
            description="Test",
            agent_type="tech"
        )
        
        state_update = {
            "category_metadata": {
                "categoryName": "Test Quiz",
                "categoryDescription": "A test",
                "categoryIcon": "🎯"
            }
        }
        
        mock_orchestrator._update_session_from_state(session_id, state_update)
        
        session = mock_orchestrator.session_manager.get_session(session_id)
        assert session["category_metadata"]["categoryName"] == "Test Quiz"
    
    def test_update_session_questions(self, mock_orchestrator):
        """Test updating session with questions."""
        session_id = mock_orchestrator.start_generation(
            topic="Test",
            description="Test",
            agent_type="tech"
        )
        
        state_update = {
            "questions": [
                {"question": "Q1", "options": ["A", "B"]},
                {"question": "Q2", "options": ["C", "D"]}
            ]
        }
        
        mock_orchestrator._update_session_from_state(session_id, state_update)
        
        session = mock_orchestrator.session_manager.get_session(session_id)
        assert len(session["questions"]) == 2
    
    def test_update_session_status(self, mock_orchestrator):
        """Test updating session status."""
        session_id = mock_orchestrator.start_generation(
            topic="Test",
            description="Test",
            agent_type="tech"
        )
        
        state_update = {"status": "completed"}
        
        mock_orchestrator._update_session_from_state(session_id, state_update)
        
        session = mock_orchestrator.session_manager.get_session(session_id)
        assert session["status"] == "completed"
    
    def test_update_session_output_file(self, mock_orchestrator):
        """Test updating session with output file."""
        session_id = mock_orchestrator.start_generation(
            topic="Test",
            description="Test",
            agent_type="tech"
        )
        
        state_update = {"output_file": "/path/to/quiz.json"}
        
        mock_orchestrator._update_session_from_state(session_id, state_update)
        
        session = mock_orchestrator.session_manager.get_session(session_id)
        assert session["output_file"] == "/path/to/quiz.json"


class TestQuizWorkflowE2E:
    """End-to-end tests for complete quiz workflow."""
    
    @pytest.fixture
    def mock_orchestrator(self, temp_sessions_dir, sample_quiz_data):
        """Create a mock orchestrator with full mocked workflow."""
        with patch('src.agents.quiz.workflow.orchestrator.create_workflow_graph') as mock_graph:
            # Mock the graph to return completed state
            mock_invoke = MagicMock()
            mock_invoke.invoke.return_value = {
                "status": "completed",
                "category_metadata": {
                    "categoryName": "React.js Quiz",
                    "categoryDescription": "Test your React knowledge",
                    "categoryIcon": "⚛️"
                },
                "questions": sample_quiz_data["questions"],
                "progress": {"completed": 2, "total": 2},
                "output_file": "/tmp/quiz_output.json",
                "quiz_data": sample_quiz_data
            }
            mock_graph.return_value = mock_invoke
            
            orchestrator = QuizWorkflowOrchestrator()
            orchestrator.session_manager.sessions_dir = temp_sessions_dir
            return orchestrator
    
    def test_complete_workflow_flow(self, mock_orchestrator):
        """Test complete workflow from start to finish."""
        # Start generation
        session_id = mock_orchestrator.start_generation(
            topic="React.js",
            description="React quiz for developers",
            agent_type="tech",
            question_count=2,
            difficulty="medium"
        )
        
        # Verify session created
        status = mock_orchestrator.get_session_status(session_id)
        assert status["status"] == "pending"
        
        # Execute workflow
        result = mock_orchestrator.execute_workflow(session_id)
        
        # Verify completion
        assert result["status"] == "completed"
        assert result["session_id"] == session_id
    
    def test_workflow_handles_error(self, temp_sessions_dir):
        """Test that workflow handles errors properly."""
        with patch('src.agents.quiz.workflow.orchestrator.create_workflow_graph') as mock_graph:
            mock_invoke = MagicMock()
            mock_invoke.invoke.side_effect = Exception("API error")
            mock_graph.return_value = mock_invoke
            
            orchestrator = QuizWorkflowOrchestrator()
            orchestrator.session_manager.sessions_dir = temp_sessions_dir
            
            session_id = orchestrator.start_generation(
                topic="Test",
                description="Test",
                agent_type="tech"
            )
            
            with pytest.raises(Exception):
                orchestrator.execute_workflow(session_id)
            
            # Session should be marked as failed
            session = orchestrator.session_manager.get_session(session_id)
            assert session["status"] == "failed"


class TestQuizWorkflowResume:
    """Tests for workflow resume functionality."""
    
    @pytest.fixture
    def mock_orchestrator(self, temp_sessions_dir):
        """Create a mock orchestrator."""
        with patch('src.agents.quiz.workflow.orchestrator.create_workflow_graph') as mock_graph:
            mock_invoke = MagicMock()
            mock_invoke.invoke.return_value = {
                "status": "completed",
                "output_file": "/tmp/output.json"
            }
            mock_graph.return_value = mock_invoke
            
            orchestrator = QuizWorkflowOrchestrator()
            orchestrator.session_manager.sessions_dir = temp_sessions_dir
            return orchestrator
    
    def test_resume_in_progress_session(self, mock_orchestrator):
        """Test resuming an in-progress session."""
        session_id = mock_orchestrator.start_generation(
            topic="Test",
            description="Test",
            agent_type="tech",
            question_count=10
        )
        
        # Simulate partial progress
        mock_orchestrator.session_manager.update_status(session_id, SessionStatus.IN_PROGRESS)
        mock_orchestrator.session_manager.update_progress(session_id, completed=5, total=10)
        
        # Resume workflow
        result = mock_orchestrator.execute_workflow(session_id)
        
        assert result["status"] == "completed"

