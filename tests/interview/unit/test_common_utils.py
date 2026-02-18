"""Unit tests for common utilities."""

import pytest
from unittest.mock import Mock

from src.core.orchestrator import (
    handle_node_errors,
    check_skip_condition,
    update_state_safely,
    validate_state_fields,
    get_progress_update,
    log_node_execution,
    create_error_state
)
from src.agents.interview.workflow import (
    create_initial_state,
    state_from_session,
    determine_resume_status,
    validate_state_transition,
    count_completed_answers,
    get_questions_needing_answers,
    normalize_question_metadata
)


class TestWorkflowUtils:
    """Tests for workflow utilities."""
    
    def test_handle_node_errors_decorator(self):
        """Test error handling decorator."""
        @handle_node_errors("test_node", "failed")
        def test_node(state):
            raise Exception("Test error")
        
        state = {"session_id": "test-123"}
        result = test_node(state)
        
        assert result["status"] == "failed"
        assert "error" in result
        assert "Test error" in result["error"]
    
    def test_handle_node_errors_success(self):
        """Test error handling decorator with successful execution."""
        @handle_node_errors("test_node", "failed")
        def test_node(state):
            return {"status": "success"}
        
        state = {"session_id": "test-123"}
        result = test_node(state)
        
        assert result["status"] == "success"
    
    def test_check_skip_condition_with_value(self):
        """Test skip condition check with specific value via check_func."""
        state = {"meta": "existing_meta"}
        result = check_skip_condition(state, "meta", check_func=lambda v: v == "existing_meta")
        assert result is True
        
        result = check_skip_condition(state, "meta", check_func=lambda v: v == "different_meta")
        assert result is False
    
    def test_check_skip_condition_with_func(self):
        """Test skip condition check with custom function."""
        state = {"questions": [1, 2, 3]}
        result = check_skip_condition(state, "questions", check_func=lambda q: q and len(q) > 0)
        assert result

        state = {"questions": []}
        result = check_skip_condition(state, "questions", check_func=lambda q: q and len(q) > 0)
        assert not result
    
    def test_check_skip_condition_default(self):
        """Test skip condition check with default behavior."""
        state = {"meta": "value"}
        result = check_skip_condition(state, "meta")
        assert result is True
        
        state = {"meta": None}
        result = check_skip_condition(state, "meta")
        assert result is False
    
    def test_update_state_safely(self):
        """Test safe state update."""
        state = {"session_id": "test-123", "status": "pending"}
        updates = {"status": "in_progress", "meta": "metadata"}
        
        result = update_state_safely(state, updates)
        
        assert result["session_id"] == "test-123"
        assert result["status"] == "in_progress"
        assert result["meta"] == "metadata"
        # Original state should not be modified
        assert state["status"] == "pending"
    
    def test_validate_state_fields(self):
        """Test state field validation."""
        state = {
            "session_id": "test-123",
            "name": "Test Sheet",
            "description": "Test Description"
        }
        
        is_valid, missing = validate_state_fields(state, ["session_id", "name", "description"])
        assert is_valid is True
        assert len(missing) == 0
        
        is_valid, missing = validate_state_fields(state, ["session_id", "name", "missing_field"])
        assert is_valid is False
        assert "missing_field" in missing
    
    def test_get_progress_update(self):
        """Test progress update creation."""
        progress = get_progress_update(5, 10, "Processing...")
        
        assert progress["completed"] == 5
        assert progress["total"] == 10
        assert progress["current_step"] == "Processing..."
    
    def test_create_error_state(self):
        """Test error state creation."""
        error_state = create_error_state("Test error", "failed")
        
        assert error_state["status"] == "failed"
        assert error_state["error"] == "Test error"
        assert "Failed: Test error" in error_state["current_step"]


class TestStateUtils:
    """Tests for state utilities."""
    
    def test_create_initial_state(self):
        """Test initial state creation."""
        state = create_initial_state(
            session_id="test-123",
            name="Test Sheet",
            description="Test Description",
            agent_type="generic",
            roadmap="Tech"
        )
        
        assert state["session_id"] == "test-123"
        assert state["name"] == "Test Sheet"
        assert state["description"] == "Test Description"
        assert state["agent_type"] == "generic"
        assert state["roadmap"] == "Tech"
        assert state["status"] == "pending"
        assert state["meta"] is None
        assert state["questions"] == []
    
    def test_state_from_session(self):
        """Test state creation from session data."""
        session_data = {
            "session_id": "test-123",
            "name": "Test Sheet",
            "description": "Test Description",
            "agent_type": "generic",
            "roadmap": "Tech",
            "status": "in_progress",
            "meta": "Metadata",
            "questions": [{"title": "Q1", "question": "Q1", "answer": ""}],
            "progress": {"completed": 5, "total": 10}
        }
        
        state = state_from_session(session_data)
        
        assert state["session_id"] == "test-123"
        assert state["name"] == "Test Sheet"
        assert state["status"] == "in_progress"
        assert state["meta"] == "Metadata"
        assert len(state["questions"]) == 1
    
    def test_determine_resume_status(self):
        """Test resume status determination."""
        # No metadata - should start with metadata
        state = {"meta": None, "questions": []}
        status = determine_resume_status(state)
        assert status == "metadata_generating"
        
        # Has metadata, no questions - should generate questions
        state = {"meta": "Metadata", "questions": []}
        status = determine_resume_status(state)
        assert status == "questions_generating"
        
        # Has metadata and questions, no answers - should generate answers
        state = {"meta": "Metadata", "questions": [{"answer": ""}]}
        status = determine_resume_status(state)
        assert status == "answers_generating"
        
        # Has everything - should finalize
        state = {"meta": "Metadata", "questions": [{"answer": "Answer"}]}
        status = determine_resume_status(state)
        assert status == "finalizing"
    
    def test_validate_state_transition(self):
        """Test state transition validation."""
        # Valid transitions
        assert validate_state_transition("pending", "metadata_generating") is True
        assert validate_state_transition("metadata_generating", "questions_generating") is True
        assert validate_state_transition("questions_generating", "answers_generating") is True
        assert validate_state_transition("answers_generating", "finalizing") is True
        assert validate_state_transition("finalizing", "completed") is True
        
        # Invalid transitions
        assert validate_state_transition("completed", "pending") is False
        assert validate_state_transition("failed", "pending") is False
        
        # Same state (allowed)
        assert validate_state_transition("pending", "pending") is True
    
    def test_count_completed_answers(self):
        """Test counting completed answers."""
        questions = [
            {"answer": "Answer 1"},
            {"answer": ""},
            {"answer": "Answer 3"},
            {"answer": None}
        ]
        
        count = count_completed_answers(questions)
        assert count == 2
    
    def test_get_questions_needing_answers(self):
        """Test getting questions that need answers."""
        questions = [
            {"title": "Q1", "answer": "Answer 1"},
            {"title": "Q2", "answer": ""},
            {"title": "Q3", "answer": None},
            {"title": "Q4"}  # No answer field
        ]
        
        needing_answers = get_questions_needing_answers(questions)
        assert len(needing_answers) == 3
    
    def test_normalize_question_metadata(self):
        """Test question metadata normalization."""
        question = {
            "title": "A" * 150,  # Too long
            "question": "Test question",
            "frequency": "Invalid",
            "priority": "Invalid",
            "companyTypes": ["Invalid"]
        }
        
        normalized = normalize_question_metadata(question)
        
        assert len(normalized["title"]) == 100
        assert normalized["frequency"] in ["Most Asked", "Asked Frequently", "Asked Sometimes"]
        assert normalized["priority"] in ["High", "Medium", "Low"]
        assert all(ct in ["Startup", "MidSize", "MNC", "FAANG"] for ct in normalized["companyTypes"])
        assert "answer" in normalized
    
    def test_normalize_question_metadata_with_valid_values(self):
        """Test normalization with already valid values."""
        question = {
            "title": "Valid Title",
            "question": "Test question",
            "frequency": "Most Asked",
            "priority": "High",
            "companyTypes": ["FAANG", "MNC"]
        }
        
        normalized = normalize_question_metadata(question)
        
        assert normalized["title"] == "Valid Title"
        assert normalized["frequency"] == "Most Asked"
        assert normalized["priority"] == "High"
        assert normalized["companyTypes"] == ["FAANG", "MNC"]

