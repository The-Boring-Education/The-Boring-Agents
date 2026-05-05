"""Unit tests for DSA push request/response model behavior."""

from src.api.models.dsa_models import DSAPushRequest


class TestDSAPushModels:
    """Tests for DSA push models."""

    def test_push_request_defaults(self):
        """Defaults should push both questions and study guide."""
        payload = DSAPushRequest()
        assert payload.push_questions is True
        assert payload.push_study_guide is True
        assert payload.environment is None

    def test_push_request_aliases(self):
        """Model should accept camelCase aliases for admin requests."""
        payload = DSAPushRequest.model_validate(
            {
                "environment": "dev",
                "pushQuestions": False,
                "pushStudyGuide": True,
            }
        )
        assert payload.environment == "dev"
        assert payload.push_questions is False
        assert payload.push_study_guide is True
