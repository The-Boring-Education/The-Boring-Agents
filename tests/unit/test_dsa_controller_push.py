"""Unit tests for DSA controller push-to-db behavior."""

from unittest.mock import Mock, patch

from src.api.controllers.dsa_controller import DSAController


class TestDSAControllerPush:
    """Tests for push_session_to_db behavior."""

    def test_push_session_questions_and_skip_study_guide(self):
        """Questions should be pushed and study guide should be skipped with warning."""
        controller = DSAController()

        fake_session_data = {
            "session_id": "session-1",
            "dsa_data": {
                "topic": "Arrays",
                "questions": [
                    {
                        "title": "Two Sum",
                        "answer": "Use hashmap",
                        "difficulty": "EASY",
                        "domain": ["DSA"],
                        "companyTypes": ["FAANG"],
                        "topics": ["ARRAY"],
                    }
                ],
                "studyGuide": {"topicId": "arrays", "title": "Arrays Guide"},
            },
        }

        controller.orchestrator.session_manager.get_session = Mock(return_value=fake_session_data)

        mock_pusher = Mock()
        mock_pusher.push.return_value = {"status_code": 201}

        with patch("src.api.controllers.dsa_controller.PushToDB", return_value=mock_pusher):
            result = controller.push_session_to_db(
                "session-1",
                environment="dev",
                push_questions=True,
                push_study_guide=True,
            )

        assert result["ok"] is True
        assert result["data"]["questionsPushed"] == 1
        assert result["data"]["studyGuidePushed"] is False
        assert "Skipped" in (result["data"]["studyGuideError"] or "")

    def test_push_session_requires_at_least_one_target(self):
        """Calling push with both flags false should return graceful no-op."""
        controller = DSAController()
        result = controller.push_session_to_db(
            "session-1",
            push_questions=False,
            push_study_guide=False,
        )
        assert result["ok"] is False
        assert "Nothing to push" in result["message"]
