"""Aptitude API request/response models."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator


class AptitudeTopicRequest(BaseModel):
    """Request to generate answers for a single topic."""
    model_config = ConfigDict(populate_by_name=True)

    topic_name: str = Field(..., alias="topicName", description="Topic name (e.g., 'Problem on Trains')")
    questions: List[str] = Field(default_factory=list, description="List of question strings. If empty, questions will be auto-generated.")
    category: Optional[str] = Field(default=None, description="Override category")
    sub_category: Optional[str] = Field(default=None, alias="subCategory", description="Override sub-category")


class AptitudeBatchRequest(BaseModel):
    """Request to generate answers for multiple topics."""
    model_config = ConfigDict(populate_by_name=True)

    topics: List[AptitudeTopicRequest] = Field(..., min_length=1)


class AptitudeTopicResponse(BaseModel):
    """Response after generating answers for a topic."""
    topic: str
    format_type: str = Field(alias="formatType")
    total_questions: int = Field(alias="totalQuestions")
    successful_answers: int = Field(alias="successfulAnswers")
    output_file: Optional[str] = Field(default=None, alias="outputFile")
    message: str


class AptitudeBatchResponse(BaseModel):
    """Response after batch generation."""
    total_topics: int = Field(alias="totalTopics")
    successful: int
    failed: int
    skipped: int
    message: str


class AptitudeUploadRequest(BaseModel):
    """Request to upload generated aptitude data to TBE-Web API."""
    model_config = ConfigDict(populate_by_name=True)

    output_file: str = Field(..., alias="outputFile", description="Path to generated JSON file")
    api_url: Optional[str] = Field(default=None, alias="apiUrl")
    admin_secret: Optional[str] = Field(default="TBEAdmin", alias="adminSecret")


class SimpleStatus(BaseModel):
    ok: bool
    message: str
