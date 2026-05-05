"""API request/response models for dedicated DSA generation."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class DSATopicGenerationRequest(BaseModel):
    """Request payload for one-topic DSA generation."""

    model_config = ConfigDict(populate_by_name=True)

    topic: str = Field(..., description="Topic name, e.g., Sliding Window")
    question_count: int = Field(default=20, ge=1, le=100, alias="questionCount")
    include_real_world: bool = Field(default=True, alias="includeRealWorld")
    difficulty: str = Field(default="MEDIUM")


class DSASessionResponse(BaseModel):
    """Standard session response payload."""

    sessionId: str
    message: str


class DSAQuestionModel(BaseModel):
    """Generated DSA question representation."""

    title: str
    answer: str
    difficulty: str
    domain: List[str] = Field(default_factory=list)
    companyTypes: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    isRealWorldProblem: bool = False
    resources: Dict[str, Any] = Field(default_factory=dict)
    sections: Dict[str, Any] = Field(default_factory=dict)


class DSAStudyGuideModel(BaseModel):
    """Generated study guide representation."""

    topicId: str
    title: str
    hasGuide: bool = True
    sections: List[Dict[str, Any]] = Field(default_factory=list)


class DSAOutputModel(BaseModel):
    """Combined DSA output model for session output endpoints."""

    topic: str
    questions: List[DSAQuestionModel] = Field(default_factory=list)
    studyGuide: Optional[DSAStudyGuideModel] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DSAPushRequest(BaseModel):
    """Request payload for publishing generated DSA content to TBE-Web."""

    model_config = ConfigDict(populate_by_name=True)

    environment: Optional[str] = Field(
        default=None,
        description="Target env: local, dev, prod. Defaults to configured environment.",
    )
    push_questions: bool = Field(default=True, alias="pushQuestions")
    push_study_guide: bool = Field(default=True, alias="pushStudyGuide")


class DSAPushResponse(BaseModel):
    """Response payload for DSA publish operations."""

    ok: bool
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)
