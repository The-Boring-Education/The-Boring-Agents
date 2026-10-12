"""
Tests for bulk purge of completed sessions.

No LLM involved (file mtime + status scan only).
"""

import json
import os
import time
from unittest.mock import patch

import pytest

from src.agents.quiz.session import QuizSessionManager
from src.core.session import SessionStatus

DAY = 86400


def _write_session(sessions_dir: str, session_id: str, status: str, age_days: float):
    path = os.path.join(sessions_dir, f"{session_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"session_id": session_id, "status": status}, f)
    old = time.time() - age_days * DAY
    os.utime(path, (old, old))
    return path


class TestPurgeCompleted:
    """Manager-level purge: old completed only."""

    @pytest.fixture
    def manager(self, temp_sessions_dir):
        return QuizSessionManager(sessions_dir=temp_sessions_dir)

    def test_deletes_only_old_completed(self, manager, temp_sessions_dir):
        old_done = _write_session(temp_sessions_dir, "old-done", "completed", 40)
        result = manager.purge_completed(30)
        assert result == {"deleted": 1, "kept": 0}
        assert not os.path.exists(old_done)

    def test_never_touches_failed_or_pending(self, manager, temp_sessions_dir):
        failed = _write_session(temp_sessions_dir, "old-failed", "failed", 90)
        pending = _write_session(temp_sessions_dir, "old-pending", "pending", 90)
        busy = _write_session(temp_sessions_dir, "old-busy", "in_progress", 90)
        result = manager.purge_completed(30)
        assert result == {"deleted": 0, "kept": 3}
        for p in (failed, pending, busy):
            assert os.path.exists(p)

    def test_keeps_recent_completed(self, manager, temp_sessions_dir):
        recent = _write_session(temp_sessions_dir, "recent-done", "completed", 2)
        result = manager.purge_completed(30)
        assert result == {"deleted": 0, "kept": 1}
        assert os.path.exists(recent)

    def test_missing_dir_returns_zeros(self, temp_dir):
        manager = QuizSessionManager(
            sessions_dir=os.path.join(temp_dir, "no_such_dir")
        )
        assert manager.purge_completed(30) == {"deleted": 0, "kept": 0}

    def test_invalid_age_raises(self, manager):
        with pytest.raises(ValueError):
            manager.purge_completed(0)


class TestPurgeController:
    """Controller aggregates across all *_sessions dirs."""

    def test_aggregates_counts(self, temp_dir, monkeypatch):
        from src.api.controllers.session_controller import SessionController
        from src.core.config import config as app_config

        for agent in ("quiz", "dsa"):
            d = os.path.join(temp_dir, f"{agent}_sessions")
            os.makedirs(d, exist_ok=True)
        _write_session(os.path.join(temp_dir, "quiz_sessions"), "q-old", "completed", 40)
        _write_session(os.path.join(temp_dir, "quiz_sessions"), "q-new", "completed", 2)
        _write_session(os.path.join(temp_dir, "dsa_sessions"), "d-old", "completed", 40)
        _write_session(os.path.join(temp_dir, "dsa_sessions"), "d-fail", "failed", 40)

        monkeypatch.setattr(app_config, "temp_dir", temp_dir)
        result = SessionController().purge_completed_sessions(30)
        assert result == {"ok": True, "deleted": 2, "kept": 2}

    def test_invalid_age_rejected(self, monkeypatch):
        from fastapi import HTTPException

        from src.api.controllers.session_controller import SessionController

        with pytest.raises(HTTPException):
            SessionController().purge_completed_sessions(0)


class TestPurgeEndpoint:
    """DELETE /sessions?older_than_days=N (no LLM calls)."""

    @patch("src.api.routes.session.controller")
    def test_purge_reports_counts(self, mock_controller, client):
        mock_controller.purge_completed_sessions.return_value = {
            "ok": True,
            "deleted": 2,
            "kept": 5,
        }
        response = client.delete("/api/v1/sessions?older_than_days=30")
        assert response.status_code == 200
        assert response.json() == {"ok": True, "deleted": 2, "kept": 5}
        mock_controller.purge_completed_sessions.assert_called_once_with(30)

    def test_purge_rejects_non_positive_age(self, client):
        response = client.delete("/api/v1/sessions?older_than_days=0")
        assert response.status_code == 422
