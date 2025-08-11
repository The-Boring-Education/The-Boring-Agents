from typing import Optional
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class GenerateQuizRequest(BaseModel):
    topic: str = Field(..., description="Quiz topic (e.g., React, Python, DevOps)")
    question_count: int = Field(20, ge=1, le=100, description="Number of questions to generate")
    target_audience: str = Field("developers", description="Target audience label")
    save: bool = Field(True, description="Whether to persist output JSON under output/")
    environment: Optional[str] = Field(None, description="Environment where request originated (local, dev, prod)")


class GenerateQuizAPIResponse(BaseModel):
    session_id: str
    output_file: Optional[str] = None
    quiz: dict


class ValidateQuizRequest(BaseModel):
    quiz: dict


class UploadQuizRequest(BaseModel):
    quiz: dict
    api_url: Optional[str] = None
    admin_secret: Optional[str] = Field(default="TBEAdmin")
    environment: Optional[str] = Field(None, description="Environment where request originated (local, dev, prod)")


class SimpleStatus(BaseModel):
    ok: bool
    message: str


class QuizTopicsResponse(BaseModel):
    """Response model for available quiz topics."""
    topics: List[str]


class SessionInfo(BaseModel):
    session_id: str
    topic: Optional[str] = None
    status: Optional[str] = None
    current_step: Optional[str] = None
    questions_generated: Optional[int] = 0
    created_at: Optional[str] = None
    filename: Optional[str] = None


class SessionListResponse(BaseModel):
    status: str
    sessions: List[SessionInfo] = []
    count: int = 0


class SessionProgress(BaseModel):
    session_id: str
    topic: Optional[str] = None
    status: Optional[str] = None
    current_step: Optional[str] = None
    steps_completed: List[str] = []
    question_count: Optional[int] = None
    questions_generated: int = 0
    percent: float = 0.0
    last_updated: Optional[str] = None
    created_at: Optional[str] = None
    raw: Dict[str, Any] = {}


class SessionLogsResponse(BaseModel):
    session_id: str
    logs: List[Dict[str, Any]] = []

