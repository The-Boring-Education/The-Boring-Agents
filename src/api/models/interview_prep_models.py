"""
Interview preparation API request/response models.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator

from src.agents.interview.types import AnswerAgentType


class CreateSheetRequest(BaseModel):
    """Request model for creating interview sheet with title and description."""
    model_config = ConfigDict(populate_by_name=True)
    
    name: str = Field(..., description="Sheet name/title")
    description: str = Field(..., description="Sheet description")
    agent_type: AnswerAgentType = Field(default=AnswerAgentType.GENERIC, alias="agentType")
    roadmap: str = Field(default="Tech", description="Roadmap type: Frontend, Backend, Fullstack, Tech")
    technology: Optional[str] = Field(default=None, description="Technology name for tech agent type")
    
    @field_validator("agent_type", mode="before")
    @classmethod
    def _normalize_agent_type(cls, value):
        if isinstance(value, str):
            return value.lower()
        return value


class GenerateInterviewSheetRequest(BaseModel):
    """Request model for creating interview sheet from MDX."""
    mdx_file: str = Field(..., description="Path to MDX requirements or questions file")
    agent_type: AnswerAgentType = Field(default=AnswerAgentType.GENERIC)
    technology: Optional[str] = Field(default=None)
    save: bool = Field(default=True)


class TopicGenerationRequest(BaseModel):
    """Request payload for single-topic generation."""
    model_config = ConfigDict(populate_by_name=True)

    topic: str = Field(..., description="Topic name to generate questions for")
    agent_type: AnswerAgentType = Field(default=AnswerAgentType.TECH, alias="agentType")
    technology: Optional[str] = Field(default=None)
    question_count: int = Field(default=20, ge=1, le=100, alias="questionCount")
    roadmap: str = Field(default="Tech")
    difficulty: str = Field(default="Medium")
    generate_answers: bool = Field(default=True, alias="generateAnswers")

    @field_validator("agent_type", mode="before")
    @classmethod
    def _normalize_agent_type(cls, value):
        if isinstance(value, str):
            return value.lower()
        return value


class BulkTopicRequest(BaseModel):
    """Topic definition for bulk generation."""
    model_config = ConfigDict(populate_by_name=True)

    name: str
    agent_type: AnswerAgentType = Field(alias="agentType")
    technology: Optional[str] = None
    question_count: int = Field(default=20, ge=1, le=100, alias="questionCount")
    roadmap: str = Field(default="Tech")
    difficulty: str = Field(default="Medium")

    @field_validator("agent_type", mode="before")
    @classmethod
    def _normalize_agent_type(cls, value):
        if isinstance(value, str):
            return value.lower()
        return value


class BulkGenerationRequest(BaseModel):
    """Request payload for bulk topic generation."""
    model_config = ConfigDict(populate_by_name=True)

    topics: List[BulkTopicRequest]
    generate_answers: bool = Field(default=True, alias="generateAnswers")
    auto_publish: bool = Field(default=False, alias="autoPublish")


class InterviewGenerationSession(BaseModel):
    """Interview generation session model."""
    sessionId: str
    topic: str
    agentType: str
    technology: Optional[str] = None
    roadmap: str
    questionCount: int
    status: str  # pending, in_progress, completed, failed
    progress: Dict[str, Any]
    startedAt: str
    completedAt: Optional[str] = None
    outputFile: Optional[str] = None
    sheetData: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class InterviewSheetResponse(BaseModel):
    """Response model for interview sheet operations."""
    ok: bool
    message: str
    output_file: Optional[str] = None
    sheet: Optional[dict] = None


class SessionResponse(BaseModel):
    """Response model for session operations."""
    sessionId: str
    message: str


class TopicTemplate(BaseModel):
    """Topic template model."""
    name: str
    description: str
    agentTypes: List[str]
    suggestedQuestionCount: int
    difficulty: str
    roadmaps: List[str]
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class RoadmapSuggestion(BaseModel):
    """Roadmap suggestion model."""
    name: str
    description: str
    topics: List[str]
    technologies: List[str]
    difficulty: str
    estimatedTime: Optional[str] = None

