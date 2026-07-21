"""API tests for path traversal hardening on quiz pending endpoints."""

import json
import os
from unittest.mock import patch

from fastapi.testclient import TestClient


class TestQuizPendingPathTraversal:
    """Quiz pending file endpoints reject traversal."""

    def test_get_pending_rejects_traversal(self, client: TestClient, temp_dir):
        with patch("src.api.routes.quiz.config") as mock_config:
            mock_config.output_dir = temp_dir
            os.makedirs(os.path.join(temp_dir, "quizzes"), exist_ok=True)
            response = client.get("/api/v1/quiz/pending/%2E%2E/content")
            assert response.status_code == 400

    def test_delete_pending_rejects_traversal(self, client: TestClient, temp_dir):
        with patch("src.api.routes.quiz.config") as mock_config:
            mock_config.output_dir = temp_dir
            os.makedirs(os.path.join(temp_dir, "quizzes"), exist_ok=True)
            response = client.delete("/api/v1/quiz/pending/%2E%2E")
            assert response.status_code == 400

    def test_get_pending_reads_safe_file(self, client: TestClient, temp_dir):
        quizzes_dir = os.path.join(temp_dir, "quizzes")
        os.makedirs(quizzes_dir, exist_ok=True)
        payload = {"categoryName": "Safe Quiz", "questions": []}
        with open(os.path.join(quizzes_dir, "safe.json"), "w", encoding="utf-8") as f:
            json.dump(payload, f)

        with patch("src.api.routes.quiz.config") as mock_config:
            mock_config.output_dir = temp_dir
            response = client.get("/api/v1/quiz/pending/safe.json/content")
            assert response.status_code == 200
            assert response.json()["categoryName"] == "Safe Quiz"
