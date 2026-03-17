"""
API models for request/response schemas.
"""

from src.api.models.quiz_models import (
    CreateQuizRequest,
    TopicGenerationRequest as QuizTopicGenerationRequest,
    ValidateQuizRequest,
    UploadQuizRequest,
    SimpleStatus,
    SessionResponse,
    QuizOutputModel,
    QuizQuestionModel,
    QuizOutputResponse,
    QuizGenerationSession,
    QuizDifficulty,
    QuizAgentType,
)

from src.api.models.interview_prep_models import (
    CreateSheetRequest,
    TopicGenerationRequest as InterviewTopicGenerationRequest,
    InterviewGenerationSession,
    TopicTemplate,
    RoadmapSuggestion,
)

from src.api.models.dsa_content_models import (
    DSAContentGenerateRequest,
    DSAContentGenerateResponse,
)

__all__ = [
    # Quiz models
    "CreateQuizRequest",
    "QuizTopicGenerationRequest",
    "ValidateQuizRequest",
    "UploadQuizRequest",
    "SimpleStatus",
    "SessionResponse",  # Shared between quiz and interview prep
    "QuizOutputModel",
    "QuizQuestionModel",
    "QuizOutputResponse",
    "QuizGenerationSession",
    "QuizDifficulty",
    "QuizAgentType",
    # Interview prep models
    "CreateSheetRequest",
    "InterviewTopicGenerationRequest",
    "InterviewGenerationSession",
    "TopicTemplate",
    "RoadmapSuggestion",
    # DSA content models
    "DSAContentGenerateRequest",
    "DSAContentGenerateResponse",
]

