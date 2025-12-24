"""
Quiz generation API request/response models.

Matches the Interview Prep API pattern for consistency.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator


# =============================================================================
# Enums (Quiz-specific types)
# =============================================================================

class QuizDifficulty(str, Enum):
    """Quiz difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuizAgentType(str, Enum):
    """Available quiz generator agent types."""
    GENERIC = "generic"
    TECH = "tech"
    DSA = "dsa"
    CONCEPTUAL = "conceptual"


# =============================================================================
# Request Models
# =============================================================================

class CreateQuizRequest(BaseModel):
    """Request model for creating a quiz with topic and settings."""
    model_config = ConfigDict(populate_by_name=True)
    
    topic: str = Field(..., description="Quiz topic (e.g., React.js, Python, DSA)")
    description: Optional[str] = Field(default=None, description="Quiz description")
    agent_type: QuizAgentType = Field(default=QuizAgentType.TECH, alias="agentType")
    question_count: int = Field(default=20, ge=1, le=100, alias="questionCount")
    target_audience: str = Field(default="developers", alias="targetAudience")
    difficulty: QuizDifficulty = Field(default=QuizDifficulty.MEDIUM)
    
    @field_validator("agent_type", mode="before")
    @classmethod
    def _normalize_agent_type(cls, value):
        if isinstance(value, str):
            return value.lower()
        return value
    
    @field_validator("difficulty", mode="before")
    @classmethod
    def _normalize_difficulty(cls, value):
        if isinstance(value, str):
            return value.lower()
        return value


class TopicGenerationRequest(BaseModel):
    """Request payload for single-topic quiz generation."""
    model_config = ConfigDict(populate_by_name=True)

    topic: str = Field(..., description="Topic name to generate questions for")
    agent_type: QuizAgentType = Field(default=QuizAgentType.TECH, alias="agentType")
    question_count: int = Field(default=20, ge=1, le=100, alias="questionCount")
    target_audience: str = Field(default="developers", alias="targetAudience")
    difficulty: QuizDifficulty = Field(default=QuizDifficulty.MEDIUM)

    @field_validator("agent_type", mode="before")
    @classmethod
    def _normalize_agent_type(cls, value):
        if isinstance(value, str):
            return value.lower()
        return value


class BulkTopicRequest(BaseModel):
    """Topic definition for bulk quiz generation."""
    model_config = ConfigDict(populate_by_name=True)

    topic: str
    agent_type: QuizAgentType = Field(default=QuizAgentType.TECH, alias="agentType")
    question_count: int = Field(default=20, ge=1, le=100, alias="questionCount")
    target_audience: str = Field(default="developers", alias="targetAudience")
    difficulty: QuizDifficulty = Field(default=QuizDifficulty.MEDIUM)

    @field_validator("agent_type", mode="before")
    @classmethod
    def _normalize_agent_type(cls, value):
        if isinstance(value, str):
            return value.lower()
        return value


class BulkGenerationRequest(BaseModel):
    """Request payload for bulk quiz generation."""
    model_config = ConfigDict(populate_by_name=True)

    topics: List[BulkTopicRequest]
    auto_upload: bool = Field(default=False, alias="autoUpload")


class UploadQuizRequest(BaseModel):
    """Request model for uploading quiz to database."""
    quiz: Dict[str, Any]
    api_url: Optional[str] = Field(default=None, alias="apiUrl")
    admin_secret: Optional[str] = Field(default="TBEAdmin", alias="adminSecret")


class ValidateQuizRequest(BaseModel):
    """Request model for quiz validation."""
    quiz: Dict[str, Any]


# =============================================================================
# Response Models
# =============================================================================

class SessionResponse(BaseModel):
    """Response model for session operations."""
    sessionId: str
    message: str


class QuizGenerationSession(BaseModel):
    """Quiz generation session model."""
    sessionId: str
    topic: str
    agentType: str
    targetAudience: str
    questionCount: int
    status: str  # pending, in_progress, completed, failed
    progress: Dict[str, Any]
    startedAt: str
    completedAt: Optional[str] = None
    outputFile: Optional[str] = None
    quizData: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class SimpleStatus(BaseModel):
    """Simple status response model."""
    ok: bool
    message: str


class QuizTopicsResponse(BaseModel):
    """Response model for available quiz topics."""
    topics: List[str]


# =============================================================================
# Template & Suggestion Models
# =============================================================================

class QuizTopicTemplate(BaseModel):
    """Quiz topic template model."""
    name: str
    description: str
    agentTypes: List[str]
    suggestedQuestionCount: int
    difficulty: str
    targetAudiences: List[str]
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class QuizCategorySuggestion(BaseModel):
    """Quiz category suggestion model."""
    name: str
    description: str
    topics: List[str]
    difficulty: str
    estimatedTime: Optional[str] = None
