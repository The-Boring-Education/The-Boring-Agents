"""Tests for aptitude API routes."""

import pytest
from unittest.mock import patch, Mock


class TestListTopicsEndpoint:
    def test_returns_topic_registry(self, client):
        response = client.get("/api/v1/aptitude/topics")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "name" in data[0]
        assert "slug" in data[0]
        assert "category" in data[0]
        assert "subCategory" in data[0]

    def test_contains_expected_topics(self, client):
        response = client.get("/api/v1/aptitude/topics")
        data = response.json()
        slugs = [t["slug"] for t in data]
        assert "problem-on-trains" in slugs
        assert "synonyms" in slugs
        assert "self-introduction" in slugs


class TestGenerateEndpoint:
    @patch("src.api.controllers.aptitude_controller.AptitudeController.generate_for_topic")
    def test_valid_request_with_topic_only(self, mock_generate, client):
        mock_generate.return_value = {
            "topic": "percentage",
            "totalQuestions": 10,
            "successfulAnswers": 10,
            "outputFile": "/tmp/test.json",
            "message": "Generated 10/10 answers for 'Percentage'",
        }

        response = client.post("/api/v1/aptitude/generate", json={
            "topic": "percentage",
        })

        assert response.status_code == 200
        data = response.json()
        assert data["topic"] == "percentage"
        assert data["totalQuestions"] == 10

    @patch("src.api.controllers.aptitude_controller.AptitudeController.generate_for_topic")
    def test_valid_request_with_questions(self, mock_generate, client):
        mock_generate.return_value = {
            "topic": "percentage",
            "totalQuestions": 1,
            "successfulAnswers": 1,
            "outputFile": "/tmp/test.json",
            "message": "Generated 1/1 answers for 'Percentage'",
        }

        response = client.post("/api/v1/aptitude/generate", json={
            "topic": "percentage",
            "questions": ["What is 20% of 500?"],
        })

        assert response.status_code == 200

    @patch("src.api.controllers.aptitude_controller.AptitudeController.generate_for_topic")
    def test_valid_request_with_num_questions(self, mock_generate, client):
        mock_generate.return_value = {
            "topic": "percentage",
            "totalQuestions": 15,
            "successfulAnswers": 15,
            "outputFile": "/tmp/test.json",
            "message": "Generated 15/15 answers for 'Percentage'",
        }

        response = client.post("/api/v1/aptitude/generate", json={
            "topic": "percentage",
            "numQuestions": 15,
        })

        assert response.status_code == 200
        data = response.json()
        assert data["totalQuestions"] == 15

    def test_missing_topic(self, client):
        response = client.post("/api/v1/aptitude/generate", json={
            "questions": ["Some question?"],
        })
        assert response.status_code == 422


class TestGenerateBatchEndpoint:
    @patch("src.api.controllers.aptitude_controller.AptitudeController.generate_batch")
    def test_valid_batch(self, mock_batch, client):
        mock_batch.return_value = {
            "totalTopics": 2,
            "successful": 2,
            "failed": 0,
            "message": "Batch complete: 2/2 topics processed",
        }

        response = client.post("/api/v1/aptitude/generate-batch", json={
            "topics": ["percentage", "clocks"],
        })

        assert response.status_code == 200
        data = response.json()
        assert data["totalTopics"] == 2
        assert data["successful"] == 2

    @patch("src.api.controllers.aptitude_controller.AptitudeController.generate_batch")
    def test_batch_with_num_questions(self, mock_batch, client):
        mock_batch.return_value = {
            "totalTopics": 1,
            "successful": 1,
            "failed": 0,
            "message": "Batch complete: 1/1 topics processed",
        }

        response = client.post("/api/v1/aptitude/generate-batch", json={
            "topics": ["percentage"],
            "numQuestions": 20,
        })

        assert response.status_code == 200

    def test_empty_batch_rejected(self, client):
        response = client.post("/api/v1/aptitude/generate-batch", json={
            "topics": [],
        })
        assert response.status_code == 422


class TestUploadEndpoint:
    @patch("src.api.controllers.aptitude_controller.AptitudeController.upload_to_api")
    def test_upload_success(self, mock_upload, client):
        mock_upload.return_value = {"ok": True, "message": "Upload successful"}

        response = client.post("/api/v1/aptitude/upload", json={
            "outputFile": "/tmp/percentage.json",
        })

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True

    @patch("src.api.controllers.aptitude_controller.AptitudeController.upload_to_api")
    def test_upload_file_not_found(self, mock_upload, client):
        mock_upload.side_effect = FileNotFoundError("File not found")

        response = client.post("/api/v1/aptitude/upload", json={
            "outputFile": "/nonexistent/path.json",
        })

        assert response.status_code == 404
