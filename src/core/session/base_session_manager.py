"""Base session manager for all agent workflows.

This provides a common interface for session management that can be extended
by specific workflows (Interview, Quiz, Shiksha, etc.).
"""

import json
import logging
import os
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from src.core.config import config
from src.core.session.session_types import SessionStatus, ProgressInfo, BaseSessionData

logger = logging.getLogger(__name__)


class BaseSessionManager(ABC):
    """Base class for session management across all agent workflows."""

    def __init__(self, workflow_type: str, sessions_dir: Optional[str] = None):
        self.workflow_type = workflow_type
        self.sessions_dir = sessions_dir or os.path.join(
            config.temp_dir,
            f"{workflow_type}_sessions",
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
        """Create initial session data structure (workflow-specific)."""
        pass

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        session_file = self._get_session_file(session_id)
        if not os.path.exists(session_file):
            return None
        try:
            with open(session_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error("Error loading session %s: %s", session_id, e)
            return None

    def save_session(self, session_id: str, session_data: Dict[str, Any]) -> None:
        session_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        session_file = self._get_session_file(session_id)
        try:
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error("Error saving session %s: %s", session_id, e)
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

        completed_val = progress.get("completed")
        total_val = progress.get("total")
        if completed_val is not None and total_val and total_val > 0:
            progress["percent"] = round((completed_val / total_val) * 100, 2)

        for key, value in kwargs.items():
            progress[key] = value

        self.save_session(session_id, session_data)

    def list_sessions(self, status: Optional[SessionStatus] = None) -> List[Dict[str, Any]]:
        if not os.path.exists(self.sessions_dir):
            return []

        sessions = []
        for filename in os.listdir(self.sessions_dir):
            if not filename.endswith(".json"):
                continue
            session_id = filename.replace(".json", "")
            session_data = self.get_session(session_id)
            if session_data and (status is None or session_data.get("status") == status.value):
                sessions.append(session_data)

        sessions.sort(
            key=lambda x: x.get("updated_at", x.get("created_at", "")),
            reverse=True,
        )
        return sessions

    def delete_session(self, session_id: str) -> None:
        session_file = self._get_session_file(session_id)
        if os.path.exists(session_file):
            try:
                os.remove(session_file)
            except Exception as e:
                logger.error("Error deleting session %s: %s", session_id, e)
                raise

    def get_progress(self, session_id: str) -> Optional[Dict[str, Any]]:
        session_data = self.get_session(session_id)
        if not session_data:
            return None
        return {
            "session_id": session_id,
            "status": session_data.get("status"),
            "progress": session_data.get("progress", {}),
            "error": session_data.get("error"),
            "updated_at": session_data.get("updated_at"),
        }

