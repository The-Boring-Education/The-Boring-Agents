"""Utilities for pushing approved generated content to TBE-Web APIs."""

from typing import Any, Dict, Optional

import requests

from src.core.config import config


class PushToDB:
    """HTTP client for pushing generated content to TBE-Web admin endpoints."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        admin_secret: Optional[str] = None,
        timeout_seconds: int = 30,
    ):
        self.base_url = (base_url or config.api_v1_url).rstrip("/")
        self.admin_secret = admin_secret or config.admin_secret
        self.timeout_seconds = timeout_seconds

    def push(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Push payload to target endpoint and return normalized response."""
        normalized_endpoint = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        url = f"{self.base_url}{normalized_endpoint}"

        response = requests.post(
            url,
            json=payload,
            headers={
                "x-admin-secret": self.admin_secret,
                "Content-Type": "application/json",
            },
            timeout=self.timeout_seconds,
        )

        response_payload: Dict[str, Any]
        try:
            response_payload = response.json()
        except ValueError:
            response_payload = {"raw": response.text}

        if not response.ok:
            raise RuntimeError(
                f"Push failed ({response.status_code}) at {normalized_endpoint}: {response_payload}"
            )

        return {
            "endpoint": normalized_endpoint,
            "status_code": response.status_code,
            "response": response_payload,
        }
