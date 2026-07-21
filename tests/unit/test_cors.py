"""Tests for CORS origin configuration."""

import os
from unittest.mock import patch

from src.core.config import Config


class TestCorsConfiguration:
    """CORS origins come from config, not wildcard."""

    def test_config_parses_cors_origins(self, temp_dir):
        with patch.dict(
            os.environ,
            {
                "ENVIRONMENT": "test",
                "ADMIN_SECRET": "test-admin-secret",
                "OPENAI_API_KEY": "test",
                "CORS_ORIGINS": "https://admin.example.com,http://localhost:3000",
                "OUTPUT_DIR": os.path.join(temp_dir, "out"),
                "TEMP_DIR": os.path.join(temp_dir, "tmp"),
            },
            clear=False,
        ):
            cfg = Config()
            origins = cfg.get_cors_origins()
            assert "https://admin.example.com" in origins
            assert "*" not in origins
