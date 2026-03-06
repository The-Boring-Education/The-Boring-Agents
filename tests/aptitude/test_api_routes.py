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
        assert "category" in data[0]
        assert "subCategory" in data[0]

    def test_contains_expected_topics(self, client):
        response = client.get("/api/v1/aptitude/topics")
        data = response.json()
        topic_names = [t["name"] for t in data]
        assert "Problem on Trains" in topic_names
        assert "Synonyms" in topic_names
        assert "Self Introduction" in topic_names


class TestGenerateEndpoint:
    @patch("src.api.controllers.aptitude_controller.AptitudeController.generate_for_topic")
    def test_valid_request(self, mock_generate, client):
        mock_generate.return_value = {
            "topic": "Percentage",
            "formatType": "SPEED",
            "totalQuestions": 1,
            "successfulAnswers": 1,
            "outputFile": "/tmp/test.json",
            "message": "Generated 1/1 answers",
        }

        response = client.post("/api/v1/aptitude/generate", json={
            "topicName": "Percentage",
            "questions": ["What is 20% of 500?"],
        })

        assert response.status_code == 200
        data = response.json()
        assert data["topic"] == "Percentage"
        assert data["formatType"] == "SPEED"

    def test_missing_topic_name(self, client):
        response = client.post("/api/v1/aptitude/generate", json={
            "questions": ["Some question?"],
        })
        assert response.status_code == 422

    def test_empty_questions(self, client):
        response = client.post("/api/v1/aptitude/generate", json={
            "topicName": "Percentage",
            "questions": [],
        })
        assert response.status_code == 422

    @patch("src.api.controllers.aptitude_controller.AptitudeController.generate_for_topic")
    def test_with_explicit_category(self, mock_generate, client):
        mock_generate.return_value = {
            "topic": "Custom",
            "formatType": "SPEED",
            "totalQuestions": 1,
            "successfulAnswers": 1,
            "outputFile": None,
            "message": "Generated 1/1 answers",
        }

        response = client.post("/api/v1/aptitude/generate", json={
            "topicName": "Custom Topic",
            "questions": ["A valid custom question?"],
            "category": "QUANTITATIVE",
            "subCategory": "ARITHMETIC_APTITUDE",
        })
        assert response.status_code == 200


class TestGenerateBatchEndpoint:
    @patch("src.api.controllers.aptitude_controller.AptitudeController.generate_batch")
    def test_valid_batch(self, mock_batch, client):
        mock_batch.return_value = {
            "totalTopics": 2,
            "successful": 2,
            "failed": 0,
            "skipped": 0,
            "message": "Batch complete: 2/2 topics processed",
        }

        response = client.post("/api/v1/aptitude/generate-batch", json={
            "topics": [
                {"topicName": "Percentage", "questions": ["Q1 about percentage?"]},
                {"topicName": "Clocks", "questions": ["Q1 about clock angle?"]},
            ],
        })

        assert response.status_code == 200
        data = response.json()
        assert data["totalTopics"] == 2
        assert data["successful"] == 2

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
