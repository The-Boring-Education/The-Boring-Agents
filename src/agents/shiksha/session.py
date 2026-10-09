"""Session manager for dedicated shiksha agent"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from src.core.session import BaseSessionManager, ProgressInfo, SessionStatus


class ShikshaSessionManager(BaseSessionManager):
    """Manages Shiksha generation sessions."""

    def __init__(self, sessions_dir: Optional[str] = None):
        super().__init__(workflow_type="shiksha", sessions_dir=sessions_dir)

    def _create_session_data(
        self,
        session_id: str,
        topic: str,
        chapter_count: int = 5,
        difficulty: str = "MEDIUM",
        **kwargs,
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        return {
            "session_id": session_id,
            "workflow_type": "shiksha",
            "topic": topic,
            "chapter_count": chapter_count,
            "difficulty": difficulty,
            "status": SessionStatus.PENDING.value,
            "outline": None,
            "chapters": [],
            "progress": ProgressInfo(
                current_step="Initializing...",
                completed=0,
                total=max(chapter_count, 1),
            ).to_dict(),
            "created_at": now,
            "updated_at": now,
            "output_file": None,
            "bundle": None,
            **kwargs,
        }

    def set_outline(self, session_id: str, outline):
        data = self._require_session(session_id)
        data["outline"] = outline
        self.save_session(session_id, data)

    def set_chapters(self, session_id: str, chapters):
        data = self._require_session(session_id)
        data["chapters"] = chapters
        self.save_session(session_id, data)

    def set_output_file(
        self,
        session_id: str,
        output_file: str,
        bundle: Optional[Dict[str, Any]] = None,
    ):
        data = self._require_session(session_id)
        data["output_file"] = output_file
        if bundle is not None:
            data["bundle"] = bundle
        self.save_session(session_id, data)

    def _require_session(self, session_id: str) -> Dict[str, Any]:
        data = self.get_session(session_id)
        if not data:
            raise ValueError(f"Session {session_id} not found")
        return data
