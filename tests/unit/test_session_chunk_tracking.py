"""Unit tests for chunk-tracking helpers in BaseSessionManager."""

import os

from src.core.session import BaseSessionManager


class DummySessionManager(BaseSessionManager):
    """Minimal test implementation for BaseSessionManager ABC."""

    def _create_session_data(self, session_id: str, **kwargs):
        return {
            "session_id": session_id,
            "workflow_type": self.workflow_type,
            "status": "pending",
            "progress": {"current_step": "init", "completed": 0, "total": 0},
            "metadata": kwargs.get("metadata", {}),
        }


class TestSessionChunkTracking:
    """Tests for chunk-tracking support."""

    def test_initialize_chunk_tracking(self, temp_sessions_dir):
        """Initializes target/chunk metadata and progress counters."""
        manager = DummySessionManager("dummy", sessions_dir=temp_sessions_dir)
        session_id = manager.create_session()

        manager.initialize_chunk_tracking(
            session_id=session_id,
            target_count=12,
            chunk_size=5,
            items_generated=2,
        )

        data = manager.get_session(session_id)
        assert data is not None
        assert data["metadata"]["target_count"] == 12
        assert data["metadata"]["chunk_size"] == 5
        assert data["metadata"]["items_generated"] == 2
        assert data["metadata"]["remaining_items"] == 10
        assert data["progress"]["completed"] == 2
        assert data["progress"]["total"] == 12

    def test_increment_generated_items_caps_at_target(self, temp_sessions_dir):
        """Increment should never exceed target_count."""
        manager = DummySessionManager("dummy", sessions_dir=temp_sessions_dir)
        session_id = manager.create_session()
        manager.initialize_chunk_tracking(session_id, target_count=5, chunk_size=2)

        first = manager.increment_generated_items(session_id, generated_delta=2)
        second = manager.increment_generated_items(session_id, generated_delta=10)

        assert first["items_generated"] == 2
        assert second["items_generated"] == 5
        assert second["remaining_items"] == 0

        data = manager.get_session(session_id)
        assert data is not None
        assert data["progress"]["completed"] == 5
        assert data["progress"]["total"] == 5
        assert data["progress"]["percent"] == 100.0

    def test_invalid_chunk_values_raise(self, temp_sessions_dir):
        """Invalid chunk metadata should raise explicit errors."""
        manager = DummySessionManager("dummy", sessions_dir=temp_sessions_dir)
        session_id = manager.create_session()

        try:
            manager.initialize_chunk_tracking(session_id, target_count=-1, chunk_size=2)
            assert False, "Expected ValueError for negative target_count"
        except ValueError:
            pass

        try:
            manager.initialize_chunk_tracking(session_id, target_count=1, chunk_size=0)
            assert False, "Expected ValueError for zero chunk_size"
        except ValueError:
            pass

        files = os.listdir(temp_sessions_dir)
        assert len(files) >= 1
