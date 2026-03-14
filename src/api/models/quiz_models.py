"""
Quiz generation API request/response models.

Matches the Interview Prep API pattern for consistency.
Output models match the Quiz.ts database schema.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

# =============================================================================
# Enums (Quiz-specific types)
# =============================================================================


class QuizDifficulty(str, Enum):
    """Quiz difficulty levels - matches DB schema."""

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
# Database Schema Models (matches Quiz.ts)
# =============================================================================


class QuizQuestionModel(BaseModel):
    """Quiz question model - matches QuizQuestionModel in Quiz.ts."""

    question: str = Field(..., description="The question text")
    options: List[str] = Field(..., description="Array of options (min 2)")
    correctAnswer: int = Field(
        ..., ge=0, le=3, description="Index of correct answer (0-3)"
    )
    explanation: str = Field(..., description="Brief explanation of the answer")
    detailedExplanation: str = Field(
        ..., description="Detailed explanation with context"
    )
    difficulty: QuizDifficulty = Field(..., description="Question difficulty level")

    @field_validator("options")
    @classmethod
    def validate_options(cls, v):
        if len(v) < 2:
            raise ValueError("At least 2 options are required")
        return v

    @field_validator("difficulty", mode="before")
    @classmethod
    def normalize_difficulty(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v


class QuizOutputModel(BaseModel):
    """Quiz output model - matches QuizModel in Quiz.ts."""

    model_config = ConfigDict(populate_by_name=True)

    categoryName: str = Field(..., description="Category/quiz name")
    categoryDescription: str = Field(..., description="Category description")
    categoryIcon: str = Field(..., description="Category icon (emoji or icon name)")
    questions: List[QuizQuestionModel] = Field(
        ..., description="List of quiz questions"
    )
    isActive: bool = Field(default=True, description="Whether quiz is active")


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

    @field_validator("difficulty", mode="before")
    @classmethod
    def _normalize_difficulty(cls, value):
        if isinstance(value, str):
            return value.lower()
        return value


class UploadQuizRequest(BaseModel):
    """Request model for uploading quiz to database."""

    model_config = ConfigDict(populate_by_name=True)

    quiz: QuizOutputModel = Field(..., description="Quiz data matching DB schema")
    environment: Optional[str] = Field(
        default=None, description="Target env: local, dev, prod"
    )


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
    quizData: Optional[QuizOutputModel] = None
    error: Optional[str] = None


class SimpleStatus(BaseModel):
    """Simple status response model."""

    ok: bool
    message: str


class QuizOutputResponse(BaseModel):
    """Response model for quiz output."""

    status: str
    session_id: str
    quiz_data: QuizOutputModel


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
