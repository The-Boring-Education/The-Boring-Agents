"""Data models for Shiksha and other agents."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class Assignment(BaseModel):
    id: str
    title: str
    description: str
    type: str = "practical"
    expected_time: Optional[str] = "1-3 hours"
    grading: Optional[Dict[str, Any]] = None


class Chapter(BaseModel):
    _id: str
    name: str
    content: str
    assignments: List[Assignment] = []
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)


class MiniProject(BaseModel):
    id: str
    title: str
    description: str
    difficulty: Optional[str] = "Intermediate"
    expected_time: Optional[str] = "5-10 hours"


class Course(BaseModel):
    _id: str
    name: str
    slug: str
    description: str
    roadmap: str
    difficulty: str
    chapters: List[Chapter]
    mini_projects: List[MiniProject] = []
    meta_content: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    isPremium: bool = True
    price: int = 1
