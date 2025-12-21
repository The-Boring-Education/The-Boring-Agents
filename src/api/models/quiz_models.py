"""
Quiz API request/response models.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class GenerateQuizRequest(BaseModel):
    """Request model for quiz generation."""
    topic: str = Field(..., description="Quiz topic (e.g., React, Python, DevOps)")
    question_count: int = Field(20, ge=1, le=100, description="Number of questions to generate")
    target_audience: str = Field("developers", description="Target audience label")
    save: bool = Field(True, description="Whether to persist output JSON under output/")
    environment: Optional[str] = Field(None, description="Environment where request originated (local, dev, prod)")


class GenerateQuizAPIResponse(BaseModel):
    """Response model for quiz generation."""
    session_id: str
    output_file: Optional[str] = None
    quiz: dict


class ValidateQuizRequest(BaseModel):
    """Request model for quiz validation."""
    quiz: dict


class UploadQuizRequest(BaseModel):
    """Request model for quiz upload."""
    quiz: dict
    api_url: Optional[str] = None
    admin_secret: Optional[str] = Field(default="TBEAdmin")
    environment: Optional[str] = Field(None, description="Environment where request originated (local, dev, prod)")


class SimpleStatus(BaseModel):
    """Simple status response model."""
    ok: bool
    message: str


class QuizTopicsResponse(BaseModel):
    """Response model for available quiz topics."""
    topics: List[str]

