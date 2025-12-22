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
    GenerateInterviewSheetRequest,
    TopicGenerationRequest,
    BulkTopicRequest,
    BulkGenerationRequest,
    InterviewGenerationSession,
    InterviewSheetResponse,
    SessionResponse,
    TopicTemplate,
    RoadmapSuggestion,
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
    "GenerateInterviewSheetRequest",
    "TopicGenerationRequest",
    "BulkTopicRequest",
    "BulkGenerationRequest",
    "InterviewGenerationSession",
    "InterviewSheetResponse",
    "SessionResponse",
    "TopicTemplate",
    "RoadmapSuggestion",
]

