"""Tests for ADMIN_SECRET security validation."""

import os
from unittest.mock import patch

import pytest

from src.core.config import Config, INSECURE_DEFAULT_ADMIN_SECRET


class TestAdminSecretValidation:
    """Config.validate_security_settings behavior."""

    def test_allows_default_secret_in_local(self, temp_dir):
        with patch.dict(
            os.environ,
            {
                "ENVIRONMENT": "local",
                "ADMIN_SECRET": INSECURE_DEFAULT_ADMIN_SECRET,
                "OPENAI_API_KEY": "test",
                "OUTPUT_DIR": os.path.join(temp_dir, "out"),
                "TEMP_DIR": os.path.join(temp_dir, "tmp"),
            },
            clear=False,
        ):
            cfg = Config()
            cfg.validate_security_settings()  # should not raise

    def test_rejects_default_secret_in_prod(self, temp_dir):
        with patch.dict(
            os.environ,
            {
                "ENVIRONMENT": "prod",
                "ADMIN_SECRET": INSECURE_DEFAULT_ADMIN_SECRET,
                "OPENAI_API_KEY": "test",
                "OUTPUT_DIR": os.path.join(temp_dir, "out"),
                "TEMP_DIR": os.path.join(temp_dir, "tmp"),
            },
            clear=False,
        ):
            cfg = Config()
            with pytest.raises(ValueError, match="ADMIN_SECRET"):
                cfg.validate_security_settings()

    def test_rejects_empty_secret_in_dev(self, temp_dir):
        with patch.dict(
            os.environ,
            {
                "ENVIRONMENT": "dev",
                "ADMIN_SECRET": "placeholder",
                "OPENAI_API_KEY": "test",
                "OUTPUT_DIR": os.path.join(temp_dir, "out"),
                "TEMP_DIR": os.path.join(temp_dir, "tmp"),
            },
            clear=False,
        ):
            cfg = Config()
            cfg.admin_secret = ""
            with pytest.raises(ValueError, match="ADMIN_SECRET"):
                cfg.validate_security_settings()
