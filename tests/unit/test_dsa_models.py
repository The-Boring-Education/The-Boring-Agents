"""Unit tests for DSA API models."""

from src.api.models.dsa_models import DSATopicGenerationRequest


class TestDSAModels:
    """Tests for DSA request model defaults."""

    def test_topic_request_defaults_real_world_true(self):
        """Topic request should include real-world generation by default."""
        payload = DSATopicGenerationRequest(topic="Binary Search")
        assert payload.include_real_world is True
        assert payload.question_count == 20

    def test_topic_request_aliases(self):
        """Model should accept camelCase fields from admin clients."""
        payload = DSATopicGenerationRequest.model_validate(
            {
                "topic": "Arrays",
                "questionCount": 3,
                "includeRealWorld": False,
            }
        )
        assert payload.question_count == 3
        assert payload.include_real_world is False
