"""Job models for unified content-generation pipeline."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class JobStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Job:
    """Represents one generation workload request."""

    agent_type: str
    topic: str
    target_count: int
    chunk_size: int = 5
    difficulty: Optional[str] = None
    model: Optional[str] = None
    llm_provider: Optional[str] = None
    constraints: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate job configuration before execution."""
        if not self.agent_type.strip():
            raise ValueError("agent_type is required")
        if not self.topic.strip():
            raise ValueError("topic is required")
        if self.target_count < 1:
            raise ValueError("target_count must be greater than zero")
        if self.chunk_size < 1:
            raise ValueError("chunk_size must be greater than zero")
