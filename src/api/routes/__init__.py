"""
API routes for The Boring Agents.

Routes define endpoints and delegate to controllers for business logic.
"""

from src.api.routes.aptitude import router as aptitude_router
from src.api.routes.interview_prep import router as interview_prep_router
from src.api.routes.quiz import router as quiz_router
from src.api.routes.session import router as session_router

__all__ = [
    "quiz_router",
    "interview_prep_router",
    "session_router",
    "aptitude_router",
]
