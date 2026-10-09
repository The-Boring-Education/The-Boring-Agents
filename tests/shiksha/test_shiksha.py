"""
Shiksha agent tests: class-based, every LLM call mocked, no real API calls.
"""

import json
from unittest.mock import patch

from src.agents.shiksha import workflow as shiksha_workflow
from src.agents.shiksha.generators import ChapterGenerator, OutlineGenerator
from src.agents.shiksha.session import ShikshaSessionManager
from src.agents.shiksha.workflow import (
    ShikshaWorkflowOrchestrator,
    determine_resume_status,
    state_from_session,
)
from src.core.session import BaseSessionManager

OUTLINE_JSON = json.dumps(
    {
        "name": "Backend with Java",
        "slug": "backend-with-java",
        "description": "Learn backend engineering with Java.",
        "coverImageURL": "",
        "roadmap": "BACKEND",
        "difficultyLevel": "MEDIUM",
        "isPremium": False,
        "features": ["Hands-on examples"],
        "credits": [],
        "chapters": [
            {"key": "intro", "title": "Intro"},
            {"key": "intro", "title": "Intro Dup"},
            {"key": "rest-apis", "title": "REST APIs"},
        ],
    }
)

CHAPTER_JSON = json.dumps(
    {
        "key": "SHOULD-BE-OVERRIDDEN",
        "title": "SHOULD-BE-OVERRIDDEN",
        "content": "# Intro\n\nBody.\n\n## Example\n\n```python\nprint(1)\n```\n",
        "isOptional": False,
        "credits": [],
        "status": "published",
    }
)


def _isolated_manager(tmp_path):
    manager = ShikshaSessionManager(sessions_dir=str(tmp_path / "sessions"))
    shiksha_workflow._session_manager = manager
    return manager


class TestShikshaSessionManager:
    def test_extends_base(self, tmp_path):
        assert isinstance(
            ShikshaSessionManager(sessions_dir=str(tmp_path)), BaseSessionManager
        )

    def test_create_and_helpers(self, tmp_path):
        manager = ShikshaSessionManager(sessions_dir=str(tmp_path))
        sid = manager.create_session(topic="Java", chapter_count=3)
        data = manager.get_session(sid)
        assert data["workflow_type"] == "shiksha"
        assert data["outline"] is None and data["chapters"] == []

        manager.set_outline(sid, {"name": "C"})
        manager.set_chapters(sid, [{"key": "a", "title": "A"}])
        manager.set_output_file(sid, "/tmp/x.json", {"schemaVersion": "v"})
        data = manager.get_session(sid)
        assert data["outline"] == {"name": "C"}
        assert data["bundle"]["schemaVersion"] == "v"


class TestOutlineGenerator:
    def test_normalizes_keys_unique_no_status(self):
        gen = OutlineGenerator.__new__(OutlineGenerator)
        with patch.object(
            OutlineGenerator, "_generate_with_prompt", return_value=OUTLINE_JSON
        ):
            gen.prompt_templates = gen._get_prompt_templates()
            out = gen.generate_outline(topic="Backend with Java", chapter_count=3)
        keys = [c["key"] for c in out["chapters"]]
        assert len(out["chapters"]) == 3
        assert len(set(keys)) == 3  # dup "intro" suffixed
        assert out["slug"] == "backend-with-java"
        assert "status" not in out and "price" not in out
        assert out["credits"] == [] and out["isPremium"] is False

    def test_parse_failure_falls_back(self):
        gen = OutlineGenerator.__new__(OutlineGenerator)
        with patch.object(
            OutlineGenerator, "_generate_with_prompt", return_value="not json"
        ):
            gen.prompt_templates = gen._get_prompt_templates()
            out = gen.generate_outline(topic="GTM Engineering", chapter_count=2)
        assert len(out["chapters"]) == 2
        assert out["slug"] == "gtm-engineering-course"


class TestChapterGenerator:
    def test_preserves_key_title_identity(self):
        gen = ChapterGenerator.__new__(ChapterGenerator)
        with patch.object(
            ChapterGenerator, "_generate_with_prompt", return_value=CHAPTER_JSON
        ):
            gen.prompt_templates = gen._get_prompt_templates()
            out = gen.generate_chapter(
                topic="Java",
                course_name="Backend with Java",
                chapter_key="intro",
                chapter_title="Intro",
            )
        # ponytail: LLM must not rename identity fields
        assert out["key"] == "intro"
        assert out["title"] == "Intro"
        assert out["content"].startswith("# Intro")
        assert "status" not in out


class TestResumeHelpers:
    def test_state_from_session_defaults(self):
        state = state_from_session({"session_id": "s"})
        assert state["chapter_count"] == 5
        assert state["difficulty"] == "MEDIUM"
        assert state["chapters"] == []

    def test_determine_resume_status(self):
        assert (
            determine_resume_status(
                {"outline": None, "chapters": [], "output_file": None}
            )
            == "outline_generating"
        )
        assert (
            determine_resume_status(
                {"outline": {"a": 1}, "chapters": [], "output_file": None}
            )
            == "chapters_generating"
        )
        assert (
            determine_resume_status(
                {"outline": {"a": 1}, "chapters": [{"k": 1}], "output_file": None}
            )
            == "finalizing"
        )
        assert (
            determine_resume_status(
                {"outline": {"a": 1}, "chapters": [{"k": 1}], "output_file": "f"}
            )
            == "completed"
        )


class TestShikshaWorkflowEndToEnd:
    def test_full_run_emits_valid_bundle(self, tmp_path, monkeypatch):
        manager = _isolated_manager(tmp_path / "s")
        monkeypatch.setattr(
            "src.agents.shiksha.workflow.config",
            type("C", (), {"output_dir": str(tmp_path / "o")})(),
        )
        with (
            patch.object(
                OutlineGenerator, "_generate_with_prompt", return_value=OUTLINE_JSON
            ),
            patch.object(
                ChapterGenerator, "_generate_with_prompt", return_value=CHAPTER_JSON
            ),
        ):
            orch = ShikshaWorkflowOrchestrator()
            orch.session_manager = manager
            sid = manager.create_session(topic="Backend with Java", chapter_count=3)
            result = orch.execute_workflow(sid)

        assert result["status"] == "completed"
        bundle = manager.get_session(sid)["bundle"]
        assert bundle["schemaVersion"] == "shiksha-course@1"
        assert len(bundle["chapters"]) == 3
        assert all(c["key"] and c["content"] for c in bundle["chapters"])
        assert "status" not in bundle and "lifecycleStatus" not in bundle

    def test_failing_node_sets_failed_gracefully(self, tmp_path):
        _isolated_manager(tmp_path)
        state = {
            "session_id": "missing",
            "topic": "T",
            "chapter_count": 2,
            "difficulty": "MEDIUM",
            "status": "pending",
            "current_step": "",
            "error": None,
            "outline": None,
            "chapters": [],
            "progress": {},
            "output_file": None,
            "bundle": None,
        }
        with patch.object(
            OutlineGenerator, "_generate_with_prompt", side_effect=RuntimeError("boom")
        ):
            update = shiksha_workflow.generate_outline_node(state)
        assert update["status"] == "failed"
        assert "boom" in update["error"]

    def test_resume_skips_generated_outline(self, tmp_path):
        manager = _isolated_manager(tmp_path)
        sid = manager.create_session(topic="T", chapter_count=2)
        manager.set_outline(sid, {"name": "C", "chapters": []})
        state = state_from_session(manager.get_session(sid))
        assert determine_resume_status(state) == "chapters_generating"
        update = shiksha_workflow.generate_outline_node(
            {**state, "outline": {"name": "C"}}
        )
        assert update["status"] == "chapters_generating"
