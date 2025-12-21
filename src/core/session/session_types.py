"""Common types for session management."""

from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime


class SessionStatus(str, Enum):
    """Standard session status values."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProgressInfo:
    """Standard progress information structure."""
    
    def __init__(
        self,
        current_step: str = "Initializing...",
        completed: int = 0,
        total: int = 0,
        percent: Optional[float] = None
    ):
        self.current_step = current_step
        self.completed = completed
        self.total = total
        self.percent = percent or (completed / total * 100 if total > 0 else 0.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "current_step": self.current_step,
            "completed": self.completed,
            "total": self.total,
            "percent": round(self.percent, 2)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProgressInfo":
        """Create from dictionary."""
        return cls(
            current_step=data.get("current_step", "Initializing..."),
            completed=data.get("completed", 0),
            total=data.get("total", 0),
            percent=data.get("percent")
        )


class BaseSessionData:
    """Base structure for session data."""
    
    def __init__(
        self,
        session_id: str,
        workflow_type: str,
        status: SessionStatus = SessionStatus.PENDING,
        progress: Optional[ProgressInfo] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.session_id = session_id
        self.workflow_type = workflow_type  # "interview", "quiz", "shiksha"
        self.status = status
        self.progress = progress or ProgressInfo()
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
        self.error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "workflow_type": self.workflow_type,
            "status": self.status.value,
            "progress": self.progress.to_dict(),
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "error": self.error
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseSessionData":
        """Create from dictionary."""
        session = cls(
            session_id=data["session_id"],
            workflow_type=data.get("workflow_type", "unknown"),
            status=SessionStatus(data.get("status", SessionStatus.PENDING.value)),
            progress=ProgressInfo.from_dict(data.get("progress", {})),
            metadata=data.get("metadata", {})
        )
        session.created_at = data.get("created_at", session.created_at)
        session.updated_at = data.get("updated_at", session.updated_at)
        session.error = data.get("error")
        return session

