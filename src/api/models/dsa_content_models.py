"""DSA content generation API request/response models."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class DSAExampleInput(BaseModel):
    """A single example from the DSA question."""
    inputText: str = Field(..., description="Example input")
    outputText: str = Field(..., description="Example output")
    explanation: Optional[str] = Field(default=None, description="Optional explanation")


class DSAContentGenerateRequest(BaseModel):
    """Request model for generating DSA content sections for a question."""
    model_config = ConfigDict(populate_by_name=True)

    question: str = Field(..., description="DSA question title/name")
    topic: str = Field(..., description="Primary topic (e.g. Array, Linked List)")
    difficulty: str = Field(
        default="Medium",
        description="Difficulty: Easy, Medium, Hard",
    )
    constraints: List[str] = Field(
        default_factory=list,
        description="List of constraint strings from LeetCode",
    )
    examples: List[DSAExampleInput] = Field(
        default_factory=list,
        description="List of examples with input/output",
    )
    leetcode_url: str = Field(
        default="",
        alias="leetcodeUrl",
        description="URL to the LeetCode problem",
    )


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class DSAContentGenerateResponse(BaseModel):
    """Response model for DSA content generation."""
    status: str = Field(..., description="success or error")
    sections: Optional[Dict[str, Any]] = Field(
        default=None,
        description="The 8 structured content sections",
    )
    question: Optional[str] = None
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    error: Optional[str] = Field(
        default=None,
        description="Error message if status is error",
    )
