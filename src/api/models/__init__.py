"""
API models for request/response schemas.
"""

from src.api.models.interview_prep_models import (
    CreateSheetRequest,
    InterviewGenerationSession,
    RoadmapSuggestion,
    TopicTemplate,
)
from src.api.models.interview_prep_models import (
    TopicGenerationRequest as InterviewTopicGenerationRequest,
)
from src.api.models.dsa_models import (
    DSAOutputModel,
    DSAPushRequest,
    DSAPushResponse,
    DSAQuestionUpdateRequest,
    DSAQuestionUpdateResponse,
    DSAQuestionModel,
    DSASessionResponse,
    DSAStudyGuideModel,
    DSATopicGenerationRequest,
)
from src.api.models.quiz_models import (
    CreateQuizRequest,
    QuizAgentType,
    QuizDifficulty,
    QuizGenerationSession,
    QuizOutputModel,
    QuizOutputResponse,
    QuizQuestionModel,
    SessionResponse,
    SimpleStatus,
    UploadQuizRequest,
    ValidateQuizRequest,
)
from src.api.models.quiz_models import (
    TopicGenerationRequest as QuizTopicGenerationRequest,
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
    # DSA models
    "DSATopicGenerationRequest",
    "DSASessionResponse",
    "DSAPushRequest",
    "DSAPushResponse",
    "DSAQuestionUpdateRequest",
    "DSAQuestionUpdateResponse",
    "DSAQuestionModel",
    "DSAStudyGuideModel",
    "DSAOutputModel",
]
