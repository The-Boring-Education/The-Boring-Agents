"""
Unit tests for quiz workflow state.

Tests the QuizWorkflowState TypedDict and state utilities.
"""

import pytest
from typing import Dict, Any

from src.agents.quiz.workflow import QuizWorkflowState


class TestQuizWorkflowState:
    """Tests for QuizWorkflowState TypedDict."""
    
    def test_create_minimal_state(self):
        """Test creating a minimal workflow state."""
        state: QuizWorkflowState = {
            "session_id": "test-123",
            "topic": "React",
            "description": "React quiz",
            "agent_type": "tech",
            "question_count": 10,
            "target_audience": "developers",
            "difficulty": "medium",
            "status": "pending",
            "current_step": "Initializing",
            "error": None,
            "category_metadata": None,
            "questions": [],
            "progress": {},
            "output_file": None,
            "quiz_data": None
        }
        
        assert state["session_id"] == "test-123"
        assert state["topic"] == "React"
        assert state["status"] == "pending"
    
    def test_state_with_metadata(self):
        """Test state with category metadata."""
        state: QuizWorkflowState = {
            "session_id": "test-456",
            "topic": "JavaScript",
            "description": "JS quiz",
            "agent_type": "tech",
            "question_count": 20,
            "target_audience": "developers",
            "difficulty": "hard",
            "status": "in_progress",
            "current_step": "Generating questions",
            "error": None,
            "category_metadata": {
                "categoryName": "JavaScript Quiz",
                "categoryDescription": "Test your JS knowledge",
                "categoryIcon": "🟨"
            },
            "questions": [],
            "progress": {"completed": 0, "total": 20},
            "output_file": None,
            "quiz_data": None
        }
        
        assert state["category_metadata"]["categoryName"] == "JavaScript Quiz"
    
    def test_state_with_questions(self):
        """Test state with questions."""
        state: QuizWorkflowState = {
            "session_id": "test-789",
            "topic": "Python",
            "description": "Python quiz",
            "agent_type": "tech",
            "question_count": 5,
            "target_audience": "beginners",
            "difficulty": "easy",
            "status": "completed",
            "current_step": "Finalizing",
            "error": None,
            "category_metadata": None,
            "questions": [
                {
                    "question": "What is Python?",
                    "options": ["A", "B", "C", "D"],
                    "correctAnswer": 0
                },
                {
                    "question": "What is a list?",
                    "options": ["A", "B", "C", "D"],
                    "correctAnswer": 1
                }
            ],
            "progress": {"completed": 5, "total": 5, "percent": 100},
            "output_file": "/path/to/output.json",
            "quiz_data": None
        }
        
        assert len(state["questions"]) == 2
        assert state["status"] == "completed"
    
    def test_state_with_error(self):
        """Test state with error."""
        state: QuizWorkflowState = {
            "session_id": "test-error",
            "topic": "Test",
            "description": "Test",
            "agent_type": "generic",
            "question_count": 10,
            "target_audience": "developers",
            "difficulty": "medium",
            "status": "failed",
            "current_step": "Question generation",
            "error": "API rate limit exceeded",
            "category_metadata": None,
            "questions": [],
            "progress": {"completed": 3, "total": 10},
            "output_file": None,
            "quiz_data": None
        }
        
        assert state["status"] == "failed"
        assert state["error"] == "API rate limit exceeded"
    
    def test_state_agent_types(self):
        """Test different agent types in state."""
        agent_types = ["generic", "tech", "dsa", "conceptual"]
        
        for agent_type in agent_types:
            state: QuizWorkflowState = {
                "session_id": f"test-{agent_type}",
                "topic": "Test",
                "description": "Test",
                "agent_type": agent_type,
                "question_count": 10,
                "target_audience": "developers",
                "difficulty": "medium",
                "status": "pending",
                "current_step": "Initializing",
                "error": None,
                "category_metadata": None,
                "questions": [],
                "progress": {},
                "output_file": None,
                "quiz_data": None
            }
            
            assert state["agent_type"] == agent_type
    
    def test_state_difficulty_levels(self):
        """Test different difficulty levels."""
        difficulties = ["easy", "medium", "hard"]
        
        for difficulty in difficulties:
            state: QuizWorkflowState = {
                "session_id": f"test-{difficulty}",
                "topic": "Test",
                "description": "Test",
                "agent_type": "generic",
                "question_count": 10,
                "target_audience": "developers",
                "difficulty": difficulty,
                "status": "pending",
                "current_step": "Initializing",
                "error": None,
                "category_metadata": None,
                "questions": [],
                "progress": {},
                "output_file": None,
                "quiz_data": None
            }
            
            assert state["difficulty"] == difficulty
    
    def test_state_progress_tracking(self):
        """Test progress tracking in state."""
        state: QuizWorkflowState = {
            "session_id": "test-progress",
            "topic": "Test",
            "description": "Test",
            "agent_type": "tech",
            "question_count": 10,
            "target_audience": "developers",
            "difficulty": "medium",
            "status": "in_progress",
            "current_step": "Generating question 5 of 10",
            "error": None,
            "category_metadata": None,
            "questions": [],
            "progress": {
                "current": 5,
                "total": 10,
                "percent": 50.0,
                "current_step": "Generating question 5 of 10"
            },
            "output_file": None,
            "quiz_data": None
        }
        
        assert state["progress"]["current"] == 5
        assert state["progress"]["total"] == 10
        assert state["progress"]["percent"] == 50.0


class TestStateUtilities:
    """Tests for state utility functions (if any exist in state_utils.py)."""
    
    def test_import_state_utils(self):
        """Test that state_utils can be imported."""
        from src.agents.quiz.workflow import (
            create_initial_state,
            state_from_session,
            determine_resume_status,
        )
        
        assert create_initial_state is not None
        assert state_from_session is not None
        assert determine_resume_status is not None

