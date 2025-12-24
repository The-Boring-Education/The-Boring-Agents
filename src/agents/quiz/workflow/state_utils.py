"""State utility functions for workflow state management."""

from typing import Any, Dict
from src.agents.quiz.workflow.state import QuizWorkflowState

def create_initial_state(
    session_id: str,
    topic: str,
    description: str,
    agent_type: str,
    question_count: int = 20,
    target_audience: str = "developers",
    difficulty: str = "medium",
) -> QuizWorkflowState:
    """Create initial workflow state."""
    return {
        "session_id": session_id,
        "topic": topic,
        "description": description,
        "agent_type": agent_type,
        "question_count": question_count,
        "target_audience": target_audience,
        "difficulty": difficulty,
        "status": "pending",
        "current_step": "Initializing...",
        "error": None,
        "category_metadata": None,
        "questions": [],
        "progress": {
            "current_step": "Initializing...",
            "completed": 0,
            "total": 0
        },
        "output_file": None,
        "quiz_data": None
    }

def state_from_session(session_data: Dict[str, Any]) -> QuizWorkflowState:
    """Create workflow state from session data."""
    return {
        "session_id": session_data.get("session_id", ""),
        "topic": session_data.get("topic", ""),
        "description": session_data.get("description", ""),
        "agent_type": session_data.get("agent_type", "generic"),
        "question_count": session_data.get("question_count", 20),
        "target_audience": session_data.get("target_audience", "developers"),
        "difficulty": session_data.get("difficulty", "medium"),
        "status": session_data.get("status", "pending"),
        "current_step": session_data.get("progress", {}).get("current_step", "Initializing..."),
        "error": None,
        "category_metadata": session_data.get("category_metadata"),
        "progress": session_data.get("progress", {
            "current_step": "Initializing...",
            "completed": 0,
            "total": 0
        }),
        "output_file": session_data.get("output_file"),
        "quiz_data": session_data.get("quiz_data")
    }

def determine_resume_status(state: QuizWorkflowState) -> str:
    """Determine resume status based on workflow state."""
    has_questions = bool(state.get("questions") and len(state["questions"]) > 0)
    has_metadata = bool(state.get("category_metadata"))
    all_done = has_questions and has_metadata
    
    if all_done:
        return "completed"
    elif has_questions:
        return "metadata_generating"
    else:
        return "questions_generating"