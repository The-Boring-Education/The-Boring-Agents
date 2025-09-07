from typing import Optional
from pydantic import BaseModel, Field
from typing import List, Optional


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


# Shiksha API Models
class CreateCourseRequest(BaseModel):
    course_name: str = Field(..., description="Name of the course")
    description: str = Field(..., description="Course description")
    difficulty_level: str = Field("Beginner", description="Difficulty level (Beginner, Intermediate, Advanced)")
    roadmap: str = Field("Backend", description="Roadmap category (Backend, Frontend, Full Stack, etc.)")
    api_base_url: Optional[str] = Field(None, description="Custom API URL for research (optional)")
    enhanced: bool = Field(True, description="Use enhanced world-class course creation")


class Course(BaseModel):
    id: str
    name: str
    description: str
    difficulty_level: str
    roadmap: str
    chapters: List[dict]
    created_at: str
    status: str


class CreateCourseResponse(BaseModel):
    status: str
    message: str
    course_id: Optional[str] = None
    course: Optional[Course] = None


class ListCoursesResponse(BaseModel):
    status: str
    courses: List[Course]
    total: int

