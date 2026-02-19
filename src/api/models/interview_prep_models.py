"""
Interview preparation API request/response models.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator

from src.agents.interview.generators import AnswerAgentType


class CreateSheetRequest(BaseModel):
    """Request model for creating interview sheet with title and description."""
    model_config = ConfigDict(populate_by_name=True)
    
    name: str = Field(..., description="Sheet name/title")
    description: str = Field(..., description="Sheet description")
    agent_type: AnswerAgentType = Field(default=AnswerAgentType.GENERIC, alias="agentType")
    roadmap: str = Field(default="Tech", description="Roadmap type: Frontend, Backend, Fullstack, Tech")
    technology: Optional[str] = Field(default=None, description="Technology name for tech agent type")
    question_count: int = Field(default=20, ge=1, le=100, alias="questionCount")
    
    @field_validator("agent_type", mode="before")
    @classmethod
    def _normalize_agent_type(cls, value):
        if isinstance(value, str):
            return value.lower()
        return value


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


class InterviewQuestionResources(BaseModel):
    """Resources for interview questions."""
    youtubeURL: Optional[str] = None
    leetcodeURL: Optional[str] = None
    blogURL: Optional[str] = None


class InterviewSheetQuestionModel(BaseModel):
    """Interview question model - matches InterviewSheetQuestionModel in Sheet.ts."""
    title: str = Field(..., description="Question title")
    question: str = Field(..., description="Question text")
    answer: str = Field(..., description="Question answer")
    frequency: str = Field(..., description="Frequency: Most Asked, Asked Frequently, Asked Sometimes")
    companyTypes: List[str] = Field(..., description="List of company types")
    priority: str = Field(default="Medium", description="Priority: High, Medium, Low")
    resources: InterviewQuestionResources = Field(default_factory=InterviewQuestionResources)


class InterviewSheetModel(BaseModel):
    """Interview sheet model - matches InterviewSheetModel in Sheet.ts."""
    model_config = ConfigDict(populate_by_name=True)

    name: str
    slug: str
    description: str
    meta: str
    coverImageURL: str
    liveOn: str
    roadmap: str
    questions: List[InterviewSheetQuestionModel]
    dsaQuestions: List[str] = Field(default_factory=list)  # List of ObjectIds
    
    # Defaults
    isPremium: bool = False
    price: int = 0
    discountPercentage: int = 0
    appliedCoupon: Optional[str] = None
    features: List[str] = Field(default_factory=list)


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
    sheetData: Optional[InterviewSheetModel] = None
    error: Optional[str] = None



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
