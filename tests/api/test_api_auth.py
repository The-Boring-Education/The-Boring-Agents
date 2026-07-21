"""API authentication middleware tests."""

import os

from fastapi.testclient import TestClient


class TestAPIAuth:
    """Inbound API authentication middleware."""

    def test_health_is_public(self, unauthenticated_client: TestClient):
        response = unauthenticated_client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["ok"] is True

    def test_protected_route_rejects_missing_credential(
        self, unauthenticated_client: TestClient
    ):
        response = unauthenticated_client.get("/api/v1/aptitude/topics")
        assert response.status_code == 401
        assert response.json()["detail"] == "Unauthorized"

    def test_protected_route_rejects_wrong_credential(
        self, unauthenticated_client: TestClient
    ):
        response = unauthenticated_client.get(
            "/api/v1/aptitude/topics",
            headers={"x-admin-secret": "wrong-secret"},
        )
        assert response.status_code == 401

    def test_protected_route_accepts_x_admin_secret(self, client: TestClient):
        response = client.get("/api/v1/aptitude/topics")
        assert response.status_code == 200

    def test_protected_route_accepts_bearer_token(
        self, unauthenticated_client: TestClient
    ):
        response = unauthenticated_client.get(
            "/api/v1/aptitude/topics",
            headers={"Authorization": f"Bearer {os.environ['ADMIN_SECRET']}"},
        )
        assert response.status_code == 200

    def test_protected_route_accepts_x_api_key(
        self, unauthenticated_client: TestClient
    ):
        response = unauthenticated_client.get(
            "/api/v1/aptitude/topics",
            headers={"x-api-key": os.environ["ADMIN_SECRET"]},
        )
        assert response.status_code == 200
