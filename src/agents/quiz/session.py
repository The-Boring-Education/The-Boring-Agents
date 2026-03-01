"""Session manager for quiz generation.

Extends BaseSessionManager with quiz-specific helpers:
category metadata, question management, and output file tracking.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.core.session import BaseSessionManager, ProgressInfo, SessionStatus

logger = logging.getLogger(__name__)

DEFAULT_QUESTION_COUNT = 20


class QuizSessionManager(BaseSessionManager):
    """Manages quiz generation sessions extending BaseSessionManager."""

    def __init__(self, sessions_dir: Optional[str] = None):
        super().__init__(workflow_type="quiz", sessions_dir=sessions_dir)

    # -- session creation (override for quiz-specific fields) -----------------

    def _create_session_data(
        self,
        session_id: str,
        topic: str,
        description: str,
        agent_type: str,
        question_count: int = DEFAULT_QUESTION_COUNT,
        target_audience: str = "developers",
        difficulty: str = "medium",
        **kwargs,
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        return {
            "session_id": session_id,
            "workflow_type": "quiz",
            "topic": topic,
            "description": description,
            "agent_type": agent_type,
            "question_count": question_count,
            "target_audience": target_audience,
            "difficulty": difficulty,
            "status": SessionStatus.PENDING.value,
            "questions": [],
            "category_metadata": None,
            "progress": ProgressInfo(
                current_step="Initializing...",
                completed=0,
                total=question_count,
            ).to_dict(),
            "created_at": now,
            "updated_at": now,
            "output_file": None,
            "quiz_data": None,
            **kwargs,
        }

    # -- category metadata ----------------------------------------------------

    def set_category_metadata(self, session_id: str, metadata: Dict[str, Any]) -> None:
        session_data = self._require_session(session_id)
        session_data["category_metadata"] = metadata
        self.save_session(session_id, session_data)

    # -- question management --------------------------------------------------

    def add_question(self, session_id: str, question: Dict[str, Any]) -> None:
        session_data = self._require_session(session_id)
        session_data.setdefault("questions", []).append(question)
        self.save_session(session_id, session_data)

    # -- output file ----------------------------------------------------------

    def set_output_file(
        self,
        session_id: str,
        output_file: str,
        quiz_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        session_data = self._require_session(session_id)
        session_data["output_file"] = output_file
        if quiz_data:
            session_data["quiz_data"] = quiz_data
        self.save_session(session_id, session_data)

    # -- private helpers ------------------------------------------------------

    def _require_session(self, session_id: str) -> Dict[str, Any]:
        data = self.get_session(session_id)
        if not data:
            raise ValueError(f"Session {session_id} not found")
        return data
