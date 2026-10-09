"""API Request/Response model for dedicated shiksha generation"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class ShikshaTopicGenerationRequest(BaseModel):
    """Request payload for one-topic shiksha generation"""

    model_config = ConfigDict(populate_by_name=True)

    topic: str = Field(..., description="e.g. Backend with java, GTM Engineering")
    chapter_count: int = Field(default=5, ge=1, le=20, alias="chapterCount")
    difficulty: str = Field(default="MEDIUM")


class ShikshaSessionResponse(BaseModel):
    """Standard session response payload."""

    sessionId: str
    message: str


class ShikshaPushRequest(BaseModel):
    """Request payload for publishing generated Shiksha content to TBE-Web."""

    model_config = ConfigDict(populate_by_name=True)

    environment: Optional[str] = Field(
        default=None,
        description="Target env: local, dev, prod. Defaults to configured environment.",
    )
    dry_run: bool = Field(default=True, alias="dryRun")


class ShikshaPushResponse(BaseModel):
    """Response payload for Shiksha publish operations."""

    ok: bool
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)
