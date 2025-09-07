from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from typing import List, Optional


class BaseResponse(BaseModel):
    """Base response model for all API endpoints."""
    ok: bool = True
    message: Optional[str] = None


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

