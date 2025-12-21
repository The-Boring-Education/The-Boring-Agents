"""
API models for request/response schemas.
"""

from .quiz_models import (
    GenerateQuizRequest,
    GenerateQuizAPIResponse,
    ValidateQuizRequest,
    UploadQuizRequest,
    SimpleStatus,
    QuizTopicsResponse,
)

from .interview_prep_models import (
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

