"""Session manager for dedicated DSA generation workflows."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from src.core.session import BaseSessionManager, ProgressInfo, SessionStatus


class DSASessionManager(BaseSessionManager):
    """Manages DSA topic generation sessions."""

    def __init__(self, sessions_dir: Optional[str] = None):
        super().__init__(workflow_type="dsa", sessions_dir=sessions_dir)

    def _create_session_data(
        self,
        session_id: str,
        topic: str,
        question_count: int = 20,
        include_real_world: bool = True,
        difficulty: str = "MEDIUM",
        **kwargs,
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        return {
            "session_id": session_id,
            "workflow_type": "dsa",
            "topic": topic,
            "question_count": question_count,
            "include_real_world": include_real_world,
            "difficulty": difficulty,
            "status": SessionStatus.PENDING.value,
            "questions": [],
            "study_guide": None,
            "progress": ProgressInfo(
                current_step="Initializing...",
                completed=0,
                total=max(question_count, 1),
            ).to_dict(),
            "created_at": now,
            "updated_at": now,
            "output_file": None,
            "dsa_data": None,
            **kwargs,
        }

    def set_questions(self, session_id: str, questions):
        data = self._require_session(session_id)
        data["questions"] = questions
        self.save_session(session_id, data)

    def set_study_guide(self, session_id: str, study_guide):
        data = self._require_session(session_id)
        data["study_guide"] = study_guide
        self.save_session(session_id, data)

    def set_output_file(
        self,
        session_id: str,
        output_file: str,
        dsa_data: Optional[Dict[str, Any]] = None,
    ):
        data = self._require_session(session_id)
        data["output_file"] = output_file
        if dsa_data is not None:
            data["dsa_data"] = dsa_data
        self.save_session(session_id, data)

    def _require_session(self, session_id: str) -> Dict[str, Any]:
        data = self.get_session(session_id)
        if not data:
            raise ValueError(f"Session {session_id} not found")
        return data
