"""State utility functions for workflow state management."""

from typing import Dict, Any, List
from ..workflow.state import InterviewWorkflowState


def create_initial_state(
    session_id: str,
    name: str,
    description: str,
    agent_type: str,
    roadmap: str
) -> InterviewWorkflowState:
    """Create initial workflow state.
    
    Args:
        session_id: Session ID
        name: Sheet name
        description: Sheet description
        agent_type: Agent type
        roadmap: Roadmap type
        
    Returns:
        Initial workflow state
    """
    return {
        "session_id": session_id,
        "name": name,
        "description": description,
        "agent_type": agent_type,
        "roadmap": roadmap,
        "status": "pending",
        "current_step": "Initializing...",
        "error": None,
        "meta": None,
        "questions": [],
        "question_texts": [],
        "progress": {
            "current_step": "Initializing...",
            "completed": 0,
            "total": 0
        },
        "output_file": None,
        "sheet_data": None
    }


def state_from_session(session_data: Dict[str, Any]) -> InterviewWorkflowState:
    """Create workflow state from session data.
    
    Args:
        session_data: Session data dictionary
        
    Returns:
        Workflow state
    """
    return {
        "session_id": session_data.get("session_id", ""),
        "name": session_data.get("name", ""),
        "description": session_data.get("description", ""),
        "agent_type": session_data.get("agent_type", "generic"),
        "roadmap": session_data.get("roadmap", "Tech"),
        "status": session_data.get("status", "pending"),
        "current_step": session_data.get("progress", {}).get("current_step", "Initializing..."),
        "error": None,
        "meta": session_data.get("meta"),
        "questions": session_data.get("questions", []),
        "question_texts": [],
        "progress": session_data.get("progress", {
            "current_step": "Initializing...",
            "completed": 0,
            "total": 0
        }),
        "output_file": session_data.get("output_file"),
        "sheet_data": None
    }


def determine_resume_status(state: InterviewWorkflowState) -> str:
    """Determine the status to resume from based on state.
    
    Args:
        state: Current workflow state
        
    Returns:
        Status string
    """
    # Check what's already done
    has_meta = bool(state.get("meta"))
    has_questions = bool(state.get("questions") and len(state["questions"]) > 0)
    all_answers_done = (
        has_questions and
        all(q.get("answer") for q in state["questions"])
    )
    
    if has_meta and has_questions and all_answers_done:
        return "finalizing"
    elif has_meta and has_questions:
        return "answers_generating"
    elif has_meta:
        return "questions_generating"
    else:
        return "metadata_generating"


def get_questions_needing_answers(questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Get questions that still need answers.
    
    Args:
        questions: List of question dictionaries
        
    Returns:
        List of questions without answers
    """
    return [q for q in questions if not q.get("answer")]


def count_completed_answers(questions: List[Dict[str, Any]]) -> int:
    """Count questions that have answers.
    
    Args:
        questions: List of question dictionaries
        
    Returns:
        Number of completed answers
    """
    return len([q for q in questions if q.get("answer")])


def normalize_question_metadata(question: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize question metadata to ensure proper format.
    
    Args:
        question: Question dictionary
        
    Returns:
        Normalized question dictionary
    """
    from .schema_utils import (
        validate_frequency,
        validate_priority,
        validate_company_types,
        INTERVIEW_QUESTION_FREQUENCY,
        PRIORITY_LEVELS,
        COMPANY_TYPES
    )
    
    # Ensure frequency is valid
    frequency = question.get("frequency", "Asked Sometimes")
    if not validate_frequency(frequency):
        frequency = "Asked Sometimes"
    
    # Ensure priority is valid
    priority = question.get("priority", "Medium")
    if not validate_priority(priority):
        priority = "Medium"
    
    # Ensure companyTypes is valid
    company_types = question.get("companyTypes", [])
    if not isinstance(company_types, list):
        company_types = []
    company_types = [ct for ct in company_types if ct in COMPANY_TYPES]
    if not company_types:
        company_types = ["Startup", "MNC"]
    
    # Ensure title is within limit
    title = question.get("title", question.get("question", "")[:100])
    if len(title) > 100:
        title = title[:100]
    
    return {
        "title": title,
        "question": question.get("question", ""),
        "answer": question.get("answer", ""),
        "frequency": frequency,
        "priority": priority,
        "companyTypes": company_types
    }
