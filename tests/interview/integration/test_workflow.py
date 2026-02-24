"""Integration tests for interview workflow."""

import pytest
import os
import tempfile
import shutil

from src.agents.interview.workflow import InterviewWorkflowOrchestrator
from src.agents.interview.session import InterviewSessionManager


class TestWorkflowIntegration:
    """Integration tests for the complete workflow."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        # Note: In real tests, you'd mock the LLM calls
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_workflow_orchestrator_initialization(self):
        """Test orchestrator can be initialized."""
        orchestrator = InterviewWorkflowOrchestrator()
        assert orchestrator is not None
        assert hasattr(orchestrator, 'start_generation')
        assert hasattr(orchestrator, 'execute_workflow')
    
    def test_start_generation_creates_session(self):
        """Test starting generation creates a session."""
        orchestrator = InterviewWorkflowOrchestrator()
        
        session_id = orchestrator.start_generation(
            name="Test Sheet",
            description="Test Description",
            agent_type="generic",
            roadmap="Tech"
        )
        
        assert session_id is not None
        assert len(session_id) > 0
        
        # Verify session exists
        status = orchestrator.get_session_status(session_id)
        assert status["name"] == "Test Sheet"
        assert status["status"] == "pending"
    
    @pytest.mark.skip(reason="Requires LLM API key and would make real API calls")
    def test_full_workflow_execution(self):
        """Test full workflow execution (requires LLM)."""
        # This test would require mocking LLM calls or having API keys
        # For now, it's marked as skip
        pass
    
    @pytest.mark.skip(reason="Requires LLM API key and would make real API calls")
    def test_workflow_resume(self):
        """Test workflow resume functionality."""
        # This test would verify that a workflow can resume from a saved state
        pass

