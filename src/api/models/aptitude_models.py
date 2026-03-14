"""Aptitude API request/response models."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class AptitudeGenerateRequest(BaseModel):
    """Request to generate questions+answers for a single topic.

    Accepts EITHER:
    - topic only → auto-generates MIN 10 questions
    - topic + num_questions → auto-generates that many (min 10)
    - topic + questions → answers the provided questions (must have >= 1)
    """
    model_config = ConfigDict(populate_by_name=True)

    topic: str = Field(..., alias="topicName", description="Topic slug or name (e.g., 'problem-on-trains' or 'Problem on Trains')")
    questions: Optional[List[str]] = Field(default=None, description="Optional list of question strings to answer")
    num_questions: int = Field(default=10, alias="questionCount", ge=1, description="Number of questions to generate (minimum 10 enforced)")


class AptitudeBatchRequest(BaseModel):
    """Request to generate for multiple topics."""
    model_config = ConfigDict(populate_by_name=True)

    topics: List[str] = Field(..., min_length=1, description="List of topic slugs or names")
    num_questions: int = Field(default=10, alias="numQuestions", ge=1, description="Questions per topic (minimum 10 enforced)")


class AptitudeGenerateResponse(BaseModel):
    """Response after generating answers for a topic."""
    model_config = ConfigDict(populate_by_name=True)

    topic: str = Field(description="Topic slug")
    total_questions: int = Field(alias="totalQuestions")
    successful_answers: int = Field(alias="successfulAnswers")
    output_file: Optional[str] = Field(default=None, alias="outputFile")
    message: str


class AptitudeBatchResponse(BaseModel):
    """Response after batch generation."""
    model_config = ConfigDict(populate_by_name=True)

    total_topics: int = Field(alias="totalTopics")
    successful: int
    failed: int
    message: str


class AptitudeUploadRequest(BaseModel):
    """Request to upload generated output to TBE-Web bulk upload API."""
    model_config = ConfigDict(populate_by_name=True)

    output_file: str = Field(..., alias="outputFile", description="Path to generated JSON file")
    api_url: Optional[str] = Field(default=None, alias="apiUrl")
    admin_secret: Optional[str] = Field(default=None, alias="adminSecret")


class SimpleStatus(BaseModel):
    ok: bool
    message: str


class StudyGuideGenerateRequest(BaseModel):
    """Request to generate a study guide for a topic."""
    model_config = ConfigDict(populate_by_name=True)

    topic: str = Field(..., alias="topicName", description="Topic slug or name")


class StudyGuideGenerateResponse(BaseModel):
    """Response after generating a study guide."""
    model_config = ConfigDict(populate_by_name=True)

    topic: str = Field(description="Topic slug")
    content: str = Field(description="Markdown study guide content")
    output_file: Optional[str] = Field(default=None, alias="outputFile")
    message: str
