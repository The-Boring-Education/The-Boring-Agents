"""Interview workflow state definition and state utility functions.

Single source of truth for the InterviewWorkflowState TypedDict and all
functions that create / transform / inspect that state.
"""

from typing import TypedDict, List, Dict, Any, Optional


# ---------------------------------------------------------------------------
# State schema
# ---------------------------------------------------------------------------

class InterviewWorkflowState(TypedDict):
    """State schema for interview sheet generation workflow."""

    # Session information
    session_id: str
    name: str
    description: str
    agent_type: str
    roadmap: str
    question_count: int

    # Status tracking
    status: str
    current_step: str
    error: Optional[str]

    # Generated content
    meta: Optional[str]
    questions: List[Dict[str, Any]]
    question_texts: List[str]

    # Progress tracking
    progress: Dict[str, Any]

    # Output
    output_file: Optional[str]
    sheet_data: Optional[Dict[str, Any]]


# ---------------------------------------------------------------------------
# State factories
# ---------------------------------------------------------------------------

_DEFAULT_PROGRESS: Dict[str, Any] = {"current_step": "Initializing...", "completed": 0, "total": 0}


def create_initial_state(
    session_id: str,
    name: str,
    description: str,
    agent_type: str,
    roadmap: str,
    question_count: int = 20,
) -> InterviewWorkflowState:
    return {
        "session_id": session_id,
        "name": name,
        "description": description,
        "agent_type": agent_type,
        "roadmap": roadmap,
        "question_count": question_count,
        "status": "pending",
        "current_step": "Initializing...",
        "error": None,
        "meta": None,
        "questions": [],
        "question_texts": [],
        "progress": {**_DEFAULT_PROGRESS},
        "output_file": None,
        "sheet_data": None,
    }


def state_from_session(session_data: Dict[str, Any]) -> InterviewWorkflowState:
    return {
        "session_id": session_data.get("session_id", ""),
        "name": session_data.get("name", ""),
        "description": session_data.get("description", ""),
        "agent_type": session_data.get("agent_type", "generic"),
        "roadmap": session_data.get("roadmap", "Tech"),
        "question_count": session_data.get("question_count", 20),
        "status": session_data.get("status", "pending"),
        "current_step": session_data.get("progress", {}).get("current_step", "Initializing..."),
        "error": None,
        "meta": session_data.get("meta"),
        "questions": session_data.get("questions", []),
        "question_texts": [],
        "progress": session_data.get("progress", {**_DEFAULT_PROGRESS}),
        "output_file": session_data.get("output_file"),
        "sheet_data": None,
    }


# ---------------------------------------------------------------------------
# Resume / transition helpers
# ---------------------------------------------------------------------------

def determine_resume_status(state: InterviewWorkflowState) -> str:
    has_meta = bool(state.get("meta"))
    has_questions = bool(state.get("questions"))
    all_answered = has_questions and all(q.get("answer") for q in state["questions"])

    if has_meta and all_answered:
        return "finalizing"
    if has_meta and has_questions:
        return "answers_generating"
    if has_meta:
        return "questions_generating"
    return "metadata_generating"


VALID_TRANSITIONS: Dict[str, List[str]] = {
    "pending": ["pending", "metadata_generating", "failed"],
    "metadata_generating": ["metadata_generating", "questions_generating", "failed"],
    "questions_generating": ["questions_generating", "answers_generating", "failed"],
    "answers_generating": ["answers_generating", "finalizing", "failed"],
    "finalizing": ["finalizing", "completed", "failed"],
    "completed": ["completed"],
    "failed": ["failed"],
}


def validate_state_transition(from_status: str, to_status: str) -> bool:
    return to_status in VALID_TRANSITIONS.get(from_status, [])


# ---------------------------------------------------------------------------
# Question helpers
# ---------------------------------------------------------------------------

def get_questions_needing_answers(questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [q for q in questions if not q.get("answer")]


def count_completed_answers(questions: List[Dict[str, Any]]) -> int:
    return sum(1 for q in questions if q.get("answer"))


def normalize_question_metadata(question: Dict[str, Any]) -> Dict[str, Any]:
    from src.agents.interview.common.schema_utils import (
        validate_frequency,
        validate_priority,
        validate_company_types,
        COMPANY_TYPES,
    )

    frequency = question.get("frequency", "Asked Sometimes")
    if not validate_frequency(frequency):
        frequency = "Asked Sometimes"

    priority = question.get("priority", "Medium")
    if not validate_priority(priority):
        priority = "Medium"

    company_types = question.get("companyTypes", [])
    if not isinstance(company_types, list):
        company_types = []
    company_types = [ct for ct in company_types if ct in COMPANY_TYPES]
    if not company_types:
        company_types = ["Startup", "MNC"]

    title = question.get("title", question.get("question", "")[:100])
    if len(title) > 100:
        title = title[:100]

    return {
        "title": title,
        "question": question.get("question", ""),
        "answer": question.get("answer", ""),
        "frequency": frequency,
        "priority": priority,
        "companyTypes": company_types,
        "resources": question.get("resources", []),
    }
