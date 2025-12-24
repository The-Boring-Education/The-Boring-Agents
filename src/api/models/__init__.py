"""
API models for request/response schemas.
"""

from src.api.models.quiz_models import (
    GenerateQuizRequest,
    GenerateQuizAPIResponse,
    ValidateQuizRequest,
    UploadQuizRequest,
    SimpleStatus,
    QuizTopicsResponse,
)

from src.api.models.interview_prep_models import (
    TopicGenerationRequest,
    BulkTopicRequest,
    BulkGenerationRequest,
    InterviewGenerationSession,
    SessionResponse,
)

__all__ = [
    # Quiz models
    "GenerateQuizRequest",
    "GenerateQuizAPIResponse",
    "ValidateQuizRequest",
    "UploadQuizRequest",
    "SimpleStatus",
    "QuizTopicsResponse",
    # Interview prep models
    "TopicGenerationRequest",
    "BulkTopicRequest",
    "BulkGenerationRequest",
    "InterviewGenerationSession",
    "SessionResponse",
]

