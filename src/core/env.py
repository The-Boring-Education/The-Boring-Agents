"""
Environment variable management module for The Boring Agents.

This module provides a centralized, scalable way to handle environment variables
with proper validation, logging, and type safety.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv

# Set up logger for this module
logger = logging.getLogger(__name__)


class EnvironmentManager:
    """
    Centralized environment variable manager with validation and logging.

    This class provides a single source of truth for all environment variables,
    with proper loading, validation, and logging capabilities.
    """

    # Environment file paths (checked in order)
    ENV_FILE_PATHS = [
        Path(".env.local"),  # Local overrides (gitignored)
        Path(".env"),  # Default env file
    ]

    # Required environment variables (must be set)
    REQUIRED_VARS: Dict[str, str] = {
        # At least one API key is required, but we validate separately
    }

    # Optional environment variables with defaults
    OPTIONAL_VARS: Dict[str, Any] = {
        # Application Settings
        "LOG_LEVEL": "INFO",
        "OUTPUT_DIR": "./output",
        "TEMP_DIR": "./temp",
        "ENVIRONMENT": "dev",  # local, dev, or prod
        # Content Generation Settings
        "DEFAULT_LLM_PROVIDER": "openai",
        "DEFAULT_MODEL": "gpt-4o-mini",
        "MAX_TOKENS": 4000,
        "TEMPERATURE": 0.8,
        "MAX_CONTEXT_LENGTH": 16000,
        # API Configuration
        "LOCAL_API_BASE_URL": "http://localhost:3000",
        "DEV_API_BASE_URL": "https://tbe-dev-git-development-tbe.vercel.app",
        "PROD_API_BASE_URL": "https://www.theboringeducation.com",
        # Empty default — must be set explicitly in non-local environments
        "ADMIN_SECRET": "",
        "AGENTS_API_KEY": "",
        "CORS_ORIGINS": (
            "http://localhost:3000,http://localhost:3001,"
            "http://127.0.0.1:3000,http://127.0.0.1:3001"
        ),
        # Server Configuration
        "AGENTS_API_HOST": "0.0.0.0",
        "AGENTS_API_PORT": 8000,
        "RELOAD": "1",
    }

    # API Key variables (at least one required)
    API_KEY_VARS = [
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
    ]

    _instance: Optional["EnvironmentManager"] = None
    _loaded: bool = False

    def __new__(cls):
        """Singleton pattern to ensure single instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the environment manager."""
        if not self._loaded:
            self._load_environment()
            self._loaded = True

    def _load_environment(self) -> None:
        """
        Load environment variables from .env files.

        Checks multiple .env file locations and loads them in order,
        with later files overriding earlier ones.
        """
        loaded_files = []

        for env_path in self.ENV_FILE_PATHS:
            if env_path.exists():
                # override=False so process/env already set (e.g. tests, CI) win
                load_dotenv(env_path, override=False)
                loaded_files.append(str(env_path))
                logger.info(f"Loaded environment file: {env_path}")

        if loaded_files:
            logger.info(
                f"Environment loaded from {len(loaded_files)} file(s): {', '.join(loaded_files)}"
            )
        else:
            logger.warning(
                "No .env files found. Using system environment variables and defaults."
            )

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get an environment variable value.

        Args:
            key: Environment variable name
            default: Default value if not found

        Returns:
            Environment variable value or default
        """
        value = os.getenv(key, default)

        # Log sensitive keys differently
        if "KEY" in key or "SECRET" in key or "PASSWORD" in key:
            if value:
                logger.debug(f"Retrieved {key} (value hidden for security)")
            else:
                logger.warning(f"{key} not set")
        else:
            logger.debug(f"Retrieved {key} = {value}")

        return value

    def get_bool(self, key: str, default: bool = False) -> bool:
        """
        Get an environment variable as boolean.

        Args:
            key: Environment variable name
            default: Default value if not found

        Returns:
            Boolean value
        """
        value = self.get(key, str(default)).lower()
        return value in ("1", "true", "yes", "on")

    def get_int(self, key: str, default: int = 0) -> int:
        """
        Get an environment variable as integer.

        Args:
            key: Environment variable name
            default: Default value if not found

        Returns:
            Integer value
        """
        try:
            return int(self.get(key, str(default)))
        except (ValueError, TypeError):
            logger.warning(f"Could not convert {key} to int, using default: {default}")
            return default

    def get_float(self, key: str, default: float = 0.0) -> float:
        """
        Get an environment variable as float.

        Args:
            key: Environment variable name
            default: Default value if not found

        Returns:
            Float value
        """
        try:
            return float(self.get(key, str(default)))
        except (ValueError, TypeError):
            logger.warning(
                f"Could not convert {key} to float, using default: {default}"
            )
            return default

    def get_optional(self, key: str) -> Optional[str]:
        """
        Get an optional environment variable.

        Args:
            key: Environment variable name

        Returns:
            Environment variable value or None
        """
        return self.get(key, None)

    def validate_api_keys(self) -> bool:
        """
        Validate that at least one API key is configured.

        Returns:
            True if at least one API key is set, False otherwise
        """
        configured_keys = []
        missing_keys = []

        for key in self.API_KEY_VARS:
            value = self.get_optional(key)
            if value:
                configured_keys.append(key)
            else:
                missing_keys.append(key)

        if configured_keys:
            logger.info(f"API keys configured: {', '.join(configured_keys)}")
            return True
        else:
            logger.error(f"No API keys configured. Missing: {', '.join(missing_keys)}")
            return False

    def validate_required(self) -> bool:
        """
        Validate that all required environment variables are set.

        Returns:
            True if all required vars are set, False otherwise
        """
        missing = []

        for key, description in self.REQUIRED_VARS.items():
            if not self.get_optional(key):
                missing.append(f"{key} ({description})")

        if missing:
            logger.error(
                f"Missing required environment variables: {', '.join(missing)}"
            )
            return False

        logger.info("All required environment variables are set")
        return True

    def get_all(self) -> Dict[str, Any]:
        """
        Get all environment variables (for debugging/logging).

        Returns:
            Dictionary of all environment variables (sensitive values masked)
        """
        all_vars = {}

        # Get all optional vars with defaults
        for key in self.OPTIONAL_VARS.keys():
            all_vars[key] = self.get(key, self.OPTIONAL_VARS[key])

        # Get API keys (masked)
        for key in self.API_KEY_VARS:
            value = self.get_optional(key)
            all_vars[key] = "***" if value else None

        # Get required vars
        for key in self.REQUIRED_VARS.keys():
            value = self.get_optional(key)
            all_vars[key] = "***" if value else None

        return all_vars

    def log_summary(self) -> None:
        """Log a summary of environment configuration."""
        logger.info("=== Environment Configuration Summary ===")

        # Log API keys status
        api_keys_status = "✅ Configured" if self.validate_api_keys() else "❌ Missing"
        logger.info(f"API Keys: {api_keys_status}")

        # Log environment
        env = self.get("ENVIRONMENT", "dev")
        logger.info(f"Environment: {env}")

        # Log important settings
        logger.info(f"Log Level: {self.get('LOG_LEVEL', 'INFO')}")
        logger.info(f"Output Directory: {self.get('OUTPUT_DIR', './output')}")
        logger.info(f"Default Model: {self.get('DEFAULT_MODEL', 'gpt-4o-mini')}")

        logger.info("==========================================")


# Global instance
_env_manager: Optional[EnvironmentManager] = None


def get_env_manager() -> EnvironmentManager:
    """
    Get the global environment manager instance.

    Returns:
        EnvironmentManager instance
    """
    global _env_manager
    if _env_manager is None:
        _env_manager = EnvironmentManager()
    return _env_manager


# Convenience functions for common use cases
def get_env(key: str, default: Any = None) -> Any:
    """Get an environment variable."""
    return get_env_manager().get(key, default)


def get_env_bool(key: str, default: bool = False) -> bool:
    """Get an environment variable as boolean."""
    return get_env_manager().get_bool(key, default)


def get_env_int(key: str, default: int = 0) -> int:
    """Get an environment variable as integer."""
    return get_env_manager().get_int(key, default)


def get_env_float(key: str, default: float = 0.0) -> float:
    """Get an environment variable as float."""
    return get_env_manager().get_float(key, default)


def validate_api_keys() -> bool:
    """Validate that at least one API key is configured."""
    return get_env_manager().validate_api_keys()
