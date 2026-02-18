"""Session manager for interview sheet generation.

Extends BaseSessionManager with interview-specific question CRUD,
sheet_data mirroring, and question_count auto-healing.
"""

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.core.session import BaseSessionManager, SessionStatus, ProgressInfo

logger = logging.getLogger(__name__)

DEFAULT_QUESTION_COUNT = 20


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_question_index(questions: List[Dict[str, Any]], question_id: str) -> int:
    """Return the index of the question matching *question_id*, or -1."""
    for i, q in enumerate(questions):
        q_id = q.get("id") or q.get("_id")
        if str(q_id) == str(question_id):
            return i
        if question_id.startswith("question_"):
            try:
                if i == int(question_id.split("_")[1]):
                    return i
            except (ValueError, IndexError):
                pass
    return -1


def _sync_output_file(session_data: Dict[str, Any]) -> None:
    """Write sheet_data back to the output JSON file (if both exist)."""
    sheet_data = session_data.get("sheet_data")
    output_file = session_data.get("output_file")
    if not sheet_data or not output_file or not os.path.exists(output_file):
        return
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(sheet_data, f, indent=2, ensure_ascii=False)
    except Exception as exc:
        logger.error("Failed to sync output file %s: %s", output_file, exc)


def _ensure_question_count(session_data: Dict[str, Any]) -> int:
    """Single source of truth for calculating question_count."""
    count = session_data.get("question_count")
    if count and count > 0:
        return count
    progress = session_data.get("progress", {})
    count = progress.get("total") or len(session_data.get("questions", [])) or DEFAULT_QUESTION_COUNT
    session_data["question_count"] = count
    return count


# ---------------------------------------------------------------------------
# InterviewSessionManager
# ---------------------------------------------------------------------------

class InterviewSessionManager(BaseSessionManager):
    """Manages interview sheet generation sessions."""

    def __init__(self, sessions_dir: Optional[str] = None):
        super().__init__(workflow_type="interview", sessions_dir=sessions_dir)

    def _create_session_data(
        self,
        session_id: str,
        name: str,
        description: str,
        agent_type: str,
        roadmap: str = "Tech",
        question_count: int = DEFAULT_QUESTION_COUNT,
        **kwargs,
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        return {
            "session_id": session_id,
            "workflow_type": "interview",
            "name": name,
            "description": description,
            "agent_type": agent_type,
            "roadmap": roadmap,
            "question_count": question_count,
            "status": SessionStatus.PENDING.value,
            "meta": None,
            "questions": [],
            "question_texts": [],
            "progress": ProgressInfo(current_step="Initializing...", completed=0, total=question_count).to_dict(),
            "created_at": now,
            "updated_at": now,
            "output_file": None,
            "sheet_data": None,
            **kwargs,
        }

    def create_session(
        self,
        name: str,
        description: str,
        agent_type: str,
        roadmap: str = "Tech",
        question_count: int = DEFAULT_QUESTION_COUNT,
        **kwargs,
    ) -> str:
        return super().create_session(
            name=name, description=description, agent_type=agent_type,
            roadmap=roadmap, question_count=question_count, **kwargs,
        )

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        session_data = super().get_session(session_id)
        if session_data:
            old_count = session_data.get("question_count")
            new_count = _ensure_question_count(session_data)
            if old_count != new_count:
                try:
                    self.save_session(session_id, session_data)
                except Exception as exc:
                    logger.warning("Failed to persist auto-fixed question_count for %s: %s", session_id, exc)
        return session_data

    def list_sessions(self, status=None) -> List[Dict[str, Any]]:
        if isinstance(status, str):
            try:
                status = SessionStatus(status)
            except ValueError:
                status = None
        sessions = super().list_sessions(status)
        for s in sessions:
            old = s.get("question_count")
            new = _ensure_question_count(s)
            if old != new:
                try:
                    self.save_session(s["session_id"], s)
                except Exception as exc:
                    logger.warning("Failed to persist auto-fixed question_count for %s: %s", s["session_id"], exc)
        return sessions

    # -- metadata helpers -----------------------------------------------------

    def set_meta(self, session_id: str, meta: str) -> None:
        data = self._require_session(session_id)
        data["meta"] = meta
        self.save_session(session_id, data)

    def set_output_file(self, session_id: str, output_file: str, sheet_data: Optional[Dict[str, Any]] = None) -> None:
        data = self._require_session(session_id)
        data["output_file"] = output_file
        if sheet_data:
            data["sheet_data"] = sheet_data
        self.save_session(session_id, data)

    # -- question CRUD --------------------------------------------------------

    def add_question(self, session_id: str, question: Dict[str, Any]) -> Dict[str, Any]:
        data = self._require_session(session_id)
        if "id" not in question and "_id" not in question:
            now = datetime.now(timezone.utc).isoformat()
            question["id"] = str(uuid.uuid4())
            question["created_at"] = now
            question["updated_at"] = now
        data.setdefault("questions", []).append(question)
        self._mirror_to_sheet_data(data, "append", question=question)
        data["question_count"] = max(data.get("question_count", 0), len(data["questions"]))
        self.save_session(session_id, data)
        return question

    def get_question(self, session_id: str, question_id: str) -> Optional[Dict[str, Any]]:
        data = self.get_session(session_id)
        if not data:
            return None
        questions = data.get("questions", [])
        idx = _find_question_index(questions, question_id)
        return questions[idx] if idx >= 0 else None

    def delete_question(self, session_id: str, question_id: str) -> bool:
        data = self._require_session(session_id)
        questions = data.get("questions", [])
        idx = _find_question_index(questions, question_id)
        deleted = False
        if idx >= 0:
            questions.pop(idx)
            data["questions"] = questions
            deleted = True
        self._mirror_to_sheet_data(data, "delete", question_id=question_id)
        if deleted:
            data["question_count"] = len(data.get("questions", []))
            self.save_session(session_id, data)
        return deleted

    def update_question_in_session(self, session_id: str, question_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        data = self._require_session(session_id)
        questions = data.get("questions", [])
        idx = _find_question_index(questions, question_id)
        updated_question = None
        if idx >= 0:
            questions[idx].update(updates)
            questions[idx]["updated_at"] = datetime.now(timezone.utc).isoformat()
            updated_question = questions[idx]
        self._mirror_to_sheet_data(data, "update", question_id=question_id, updates=updates)
        if updated_question is None:
            raise ValueError(f"Question {question_id} not found in session {session_id}")
        self.save_session(session_id, data)
        return updated_question

    # -- migration helper -----------------------------------------------------

    def fix_all_sessions_question_count(self) -> int:
        if not os.path.exists(self.sessions_dir):
            return 0
        fixed = 0
        for fname in os.listdir(self.sessions_dir):
            if not fname.endswith(".json"):
                continue
            sid = fname.replace(".json", "")
            try:
                data = super().get_session(sid)
                if data:
                    old = data.get("question_count")
                    new = _ensure_question_count(data)
                    if old != new or old is None:
                        self.save_session(sid, data)
                        fixed += 1
            except Exception as exc:
                logger.warning("Failed to fix session %s: %s", sid, exc)
        return fixed

    # -- private helpers ------------------------------------------------------

    def _require_session(self, session_id: str) -> Dict[str, Any]:
        data = self.get_session(session_id)
        if not data:
            raise ValueError(f"Session {session_id} not found")
        return data

    def _mirror_to_sheet_data(
        self,
        session_data: Dict[str, Any],
        operation: str,
        *,
        question: Optional[Dict[str, Any]] = None,
        question_id: Optional[str] = None,
        updates: Optional[Dict[str, Any]] = None,
    ) -> None:
        sheet_data = session_data.get("sheet_data")
        if not sheet_data:
            return
        sheet_questions = sheet_data.setdefault("questions", [])
        if operation == "append" and question is not None:
            sheet_questions.append(question)
        elif operation == "delete" and question_id is not None:
            idx = _find_question_index(sheet_questions, question_id)
            if idx >= 0:
                sheet_questions.pop(idx)
        elif operation == "update" and question_id is not None and updates is not None:
            idx = _find_question_index(sheet_questions, question_id)
            if idx >= 0:
                sheet_questions[idx].update(updates)
                sheet_questions[idx]["updated_at"] = datetime.now(timezone.utc).isoformat()
        _sync_output_file(session_data)
