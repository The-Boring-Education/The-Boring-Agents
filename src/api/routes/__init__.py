"""
API routes for The Boring Agents.

Routes define endpoints and delegate to controllers for business logic.
"""

from .quiz import router as quiz_router
from .interview_prep import router as interview_prep_router
from .session import router as session_router

__all__ = [
    "quiz_router",
    "interview_prep_router",
    "session_router",
]

