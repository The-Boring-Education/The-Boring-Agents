"""Backward-compatible re-exports -- all state logic now lives in workflow/state.py."""

from src.agents.interview.workflow.state import (
    create_initial_state,
    state_from_session,
    determine_resume_status,
    get_questions_needing_answers,
    count_completed_answers,
    normalize_question_metadata,
    validate_state_transition,
    VALID_TRANSITIONS,
)

__all__ = [
    "create_initial_state",
    "state_from_session",
    "determine_resume_status",
    "get_questions_needing_answers",
    "count_completed_answers",
    "normalize_question_metadata",
    "validate_state_transition",
    "VALID_TRANSITIONS",
]
