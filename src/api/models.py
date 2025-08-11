from typing import Optional
from pydantic import BaseModel, Field


class GenerateQuizRequest(BaseModel):
    topic: str = Field(..., description="Quiz topic (e.g., React, Python, DevOps)")
    question_count: int = Field(20, ge=1, le=100, description="Number of questions to generate")
    target_audience: str = Field("developers", description="Target audience label")
    save: bool = Field(True, description="Whether to persist output JSON under output/")


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


class SimpleStatus(BaseModel):
    ok: bool
    message: str

