"""Core session management for all agent workflows.

Provides BaseSessionManager (ABC) and session types (SessionStatus, ProgressInfo).
Each agent extends BaseSessionManager for workflow-specific session logic.

All classes defined here. Sub-files (base_session_manager.py, session_types.py)
are backward-compatible re-exports.
"""

import json
import logging
import os
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from src.core.config import config

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Session types
# ---------------------------------------------------------------------------


class SessionStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProgressInfo:
    def __init__(
        self,
        current_step: str = "Initializing...",
        completed: int = 0,
        total: int = 0,
        percent: Optional[float] = None,
    ):
        self.current_step = current_step
        self.completed = completed
        self.total = total
        self.percent = percent or (completed / total * 100 if total > 0 else 0.0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_step": self.current_step,
            "completed": self.completed,
            "total": self.total,
            "percent": round(self.percent, 2),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProgressInfo":
        return cls(
            current_step=data.get("current_step", "Initializing..."),
            completed=data.get("completed", 0),
            total=data.get("total", 0),
            percent=data.get("percent"),
        )


class BaseSessionData:
    def __init__(
        self,
        session_id: str,
        workflow_type: str,
        status: SessionStatus = SessionStatus.PENDING,
        progress: Optional[ProgressInfo] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.session_id = session_id
        self.workflow_type = workflow_type
        self.status = status
        self.progress = progress or ProgressInfo()
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
        self.error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "workflow_type": self.workflow_type,
            "status": self.status.value,
            "progress": self.progress.to_dict(),
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseSessionData":
        session = cls(
            session_id=data["session_id"],
            workflow_type=data.get("workflow_type", "unknown"),
            status=SessionStatus(data.get("status", SessionStatus.PENDING.value)),
            progress=ProgressInfo.from_dict(data.get("progress", {})),
            metadata=data.get("metadata", {}),
        )
        session.created_at = data.get("created_at", session.created_at)
        session.updated_at = data.get("updated_at", session.updated_at)
        session.error = data.get("error")
        return session


# ---------------------------------------------------------------------------
# Base session manager
# ---------------------------------------------------------------------------


class BaseSessionManager(ABC):
    """File-backed session manager. Subclasses implement _create_session_data."""

    def __init__(self, workflow_type: str, sessions_dir: Optional[str] = None):
        self.workflow_type = workflow_type
        self.sessions_dir = sessions_dir or os.path.join(
            config.temp_dir, f"{workflow_type}_sessions"
        )
        os.makedirs(self.sessions_dir, exist_ok=True)

    def _get_session_file(self, session_id: str) -> str:
        return os.path.join(self.sessions_dir, f"{session_id}.json")

    def create_session(self, **kwargs) -> str:
        session_id = str(uuid.uuid4())
        session_data = self._create_session_data(session_id, **kwargs)
        self.save_session(session_id, session_data)
        return session_id

    @abstractmethod
    def _create_session_data(self, session_id: str, **kwargs) -> Dict[str, Any]:
        pass

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        path = self._get_session_file(session_id)
        if not os.path.exists(path):
            return None
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error("Error loading session %s: %s", session_id, e)
            return None

    def save_session(self, session_id: str, session_data: Dict[str, Any]) -> None:
        session_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        try:
            with open(self._get_session_file(session_id), "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error("Error saving session %s: %s", session_id, e)
            raise

    def delete_session(self, session_id: str) -> None:
        path = self._get_session_file(session_id)
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                logger.error("Error deleting session %s: %s", session_id, e)
                raise

    def update_status(
        self,
        session_id: str,
        status: SessionStatus,
        current_step: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        session_data = self.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session {session_id} not found")
        session_data["status"] = status.value
        if current_step:
            session_data.setdefault("progress", {})["current_step"] = current_step
        if error:
            session_data["error"] = error
        self.save_session(session_id, session_data)

    def update_progress(
        self,
        session_id: str,
        completed: Optional[int] = None,
        total: Optional[int] = None,
        current_step: Optional[str] = None,
        **kwargs,
    ) -> None:
        session_data = self.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session {session_id} not found")
        progress = session_data.setdefault("progress", {})
        if completed is not None:
            progress["completed"] = completed
        if total is not None:
            progress["total"] = total
        if current_step:
            progress["current_step"] = current_step
        c, t = progress.get("completed"), progress.get("total")
        if c is not None and t and t > 0:
            progress["percent"] = round((c / t) * 100, 2)
        for k, v in kwargs.items():
            progress[k] = v
        self.save_session(session_id, session_data)

    def list_sessions(
        self, status: Optional[SessionStatus] = None
    ) -> List[Dict[str, Any]]:
        if not os.path.exists(self.sessions_dir):
            return []
        sessions = []
        for fname in os.listdir(self.sessions_dir):
            if not fname.endswith(".json"):
                continue
            data = self.get_session(fname.replace(".json", ""))
            if data and (status is None or data.get("status") == status.value):
                sessions.append(data)
        sessions.sort(
            key=lambda x: x.get("updated_at", x.get("created_at", "")), reverse=True
        )
        return sessions

    def get_progress(self, session_id: str) -> Optional[Dict[str, Any]]:
        data = self.get_session(session_id)
        if not data:
            return None
        return {
            "session_id": session_id,
            "status": data.get("status"),
            "progress": data.get("progress", {}),
            "error": data.get("error"),
            "updated_at": data.get("updated_at"),
        }
