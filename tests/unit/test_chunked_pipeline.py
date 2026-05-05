"""Unit tests for ChunkedPipeline behavior."""

from typing import Dict, List

from src.core.pipeline import ChunkedPipeline, Job
from src.core.session import BaseSessionManager


class DummySessionManager(BaseSessionManager):
    """Minimal concrete session manager for tests."""

    def _create_session_data(self, session_id: str, **kwargs):
        return {
            "session_id": session_id,
            "workflow_type": self.workflow_type,
            "status": "pending",
            "progress": {"current_step": "init", "completed": 0, "total": 0},
            "metadata": kwargs.get("metadata", {}),
        }


class DummyChunkedPipeline(ChunkedPipeline):
    """Concrete chunked pipeline used in tests."""

    def __init__(self):
        super().__init__(pipeline_name="dummy")


class TestChunkedPipeline:
    """Tests for chunk execution and resumability support."""

    def test_run_processes_all_chunks(self, temp_sessions_dir):
        """Pipeline should process target count in multiple chunks."""
        manager = DummySessionManager("chunk", sessions_dir=temp_sessions_dir)
        session_id = manager.create_session()
        pipeline = DummyChunkedPipeline()

        job = Job(agent_type="dsa", topic="array", target_count=7, chunk_size=3)

        def chunk_generator(_job: Job, start_index: int, count: int) -> List[Dict]:
            return [
                {"id": start_index + idx + 1, "topic": _job.topic}
                for idx in range(count)
            ]

        result = pipeline.run(
            job,
            session_manager=manager,
            session_id=session_id,
            chunk_generator=chunk_generator,
        )

        assert result["items_generated"] == 7
        assert result["remaining_items"] == 0
        assert result["is_complete"] is True
        assert len(result["chunks"]) == 3

        session = manager.get_session(session_id)
        assert session is not None
        assert session["metadata"]["items_generated"] == 7
        assert session["progress"]["percent"] == 100.0

    def test_run_resumes_from_existing_progress(self, temp_sessions_dir):
        """Pipeline should continue from existing generated item count."""
        manager = DummySessionManager("chunk", sessions_dir=temp_sessions_dir)
        session_id = manager.create_session(
            metadata={"target_count": 6, "chunk_size": 2, "items_generated": 4}
        )
        pipeline = DummyChunkedPipeline()
        job = Job(agent_type="dsa", topic="array", target_count=6, chunk_size=2)

        def chunk_generator(_job: Job, start_index: int, count: int) -> List[Dict]:
            return [{"id": start_index + idx + 1} for idx in range(count)]

        result = pipeline.run(
            job,
            session_manager=manager,
            session_id=session_id,
            chunk_generator=chunk_generator,
        )

        assert result["items_generated"] == 6
        assert len(result["chunks"]) == 1

    def test_job_validation_happens_before_processing(self, temp_sessions_dir):
        """Invalid jobs should raise and not call chunk generator."""
        manager = DummySessionManager("chunk", sessions_dir=temp_sessions_dir)
        session_id = manager.create_session()
        pipeline = DummyChunkedPipeline()

        job = Job(agent_type="", topic="array", target_count=1, chunk_size=1)

        called = {"value": False}

        def chunk_generator(_job: Job, start_index: int, count: int) -> List[Dict]:
            del _job, start_index, count
            called["value"] = True
            return []

        try:
            pipeline.run(
                job,
                session_manager=manager,
                session_id=session_id,
                chunk_generator=chunk_generator,
            )
            assert False, "Expected ValueError for invalid job"
        except ValueError:
            pass

        assert called["value"] is False
