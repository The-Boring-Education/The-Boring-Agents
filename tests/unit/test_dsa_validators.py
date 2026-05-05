"""Unit tests for DSA output normalization helpers."""

from src.agents.dsa.validators import normalize_questions, normalize_study_guide


class TestDSAValidators:
    """Tests for DSA validators."""

    def test_normalize_questions_enforces_real_world_default(self):
        """When include_real_world is true, at least one question is real-world."""
        questions = [{"title": "Q1", "answer": "A1"}, {"title": "Q2", "answer": "A2"}]
        normalized = normalize_questions(
            questions,
            topic="Sliding Window",
            question_count=2,
            include_real_world=True,
            difficulty="MEDIUM",
        )

        assert len(normalized) == 2
        assert any(q["isRealWorldProblem"] for q in normalized)
        assert normalized[0]["topics"][0] == "SLIDING_WINDOW"

    def test_normalize_study_guide_has_default_sections(self):
        """Study guide fallback includes intro/concept/pattern/cheatsheet sections."""
        guide = normalize_study_guide({}, topic="Graphs", question_titles=["Topological Sort"])
        section_types = [section["type"] for section in guide["sections"]]

        assert guide["topicId"] == "graphs"
        assert section_types == ["intro", "concept", "pattern", "cheatsheet"]
