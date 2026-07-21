"""
Configuration management for The Boring Agents.

This module provides a Pydantic-based configuration class that uses
the EnvironmentManager for loading and validating environment variables.
"""

import logging
import os
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.env import get_env_manager
from src.core.env import validate_api_keys as env_validate_api_keys

logger = logging.getLogger(__name__)

# Insecure historical default — must not be used outside local/test.
INSECURE_DEFAULT_ADMIN_SECRET = "TBEAdmin"

_DEFAULT_CORS_ORIGINS = (
    "http://localhost:3000,http://localhost:3001,"
    "http://127.0.0.1:3000,http://127.0.0.1:3001"
)


class Config(BaseSettings):
    """Configuration settings for The Boring Agents application."""

    # Pydantic v2 settings
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ignore unknown env keys like AGENTS_API_HOST, AGENTS_API_PORT
    )

    # API Keys
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    gemini_api_key: Optional[str] = Field(default=None, env="GEMINI_API_KEY")

    # Application Settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    output_dir: str = Field(default="./output", env="OUTPUT_DIR")
    temp_dir: str = Field(default="./temp", env="TEMP_DIR")

    # Content Generation Settings
    default_llm_provider: str = Field(
        default="openai", env="DEFAULT_LLM_PROVIDER"
    )
    default_model: str = Field(default="gpt-4o-mini", env="DEFAULT_MODEL")
    max_tokens: int = Field(default=4000, env="MAX_TOKENS")
    temperature: float = Field(default=0.8, env="TEMPERATURE")
    max_context_length: int = Field(default=16000, env="MAX_CONTEXT_LENGTH")

    # API Configuration
    environment: str = Field(default="dev", env="ENVIRONMENT")  # local, dev, or prod
    local_api_base_url: str = Field(
        default="http://localhost:3000", env="LOCAL_API_BASE_URL"
    )
    dev_api_base_url: str = Field(
        default="https://tbe-dev-git-development-tbe.vercel.app", env="DEV_API_BASE_URL"
    )
    prod_api_base_url: str = Field(
        default="https://www.theboringeducation.com", env="PROD_API_BASE_URL"
    )
    admin_secret: str = Field(
        default=INSECURE_DEFAULT_ADMIN_SECRET, env="ADMIN_SECRET"
    )
    # Optional dedicated inbound API key; falls back to admin_secret when empty
    agents_api_key: Optional[str] = Field(default=None, env="AGENTS_API_KEY")
    cors_origins: str = Field(default=_DEFAULT_CORS_ORIGINS, env="CORS_ORIGINS")

    @property
    def api_base_url(self) -> str:
        """Get the appropriate API base URL based on environment."""
        return self.get_api_base_url()

    def get_api_base_url(self, environment: Optional[str] = None) -> str:
        """Get the API base URL for a given environment (defaults to configured env)."""
        env = environment or self.environment
        url_map = {
            "local": self.local_api_base_url,
            "dev": self.dev_api_base_url,
            "prod": self.prod_api_base_url,
        }
        return url_map.get(env, self.dev_api_base_url)

    @property
    def api_v1_url(self) -> str:
        """Get the API v1 URL with /api/v1 suffix."""
        return f"{self.api_base_url}/api/v1"

    def get_cors_origins(self) -> List[str]:
        """Parse CORS_ORIGINS into a list of allowed origins."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def get_api_auth_secret(self) -> str:
        """Secret expected on inbound API requests (AGENTS_API_KEY or ADMIN_SECRET)."""
        if self.agents_api_key and self.agents_api_key.strip():
            return self.agents_api_key.strip()
        return self.admin_secret

    def validate_security_settings(self) -> None:
        """Refuse insecure ADMIN_SECRET outside local/test environments."""
        env = (self.environment or "").strip().lower()
        secret = (self.admin_secret or "").strip()
        insecure = not secret or secret == INSECURE_DEFAULT_ADMIN_SECRET

        if env in ("local", "test"):
            if insecure:
                logger.warning(
                    "ADMIN_SECRET is empty or the insecure default — allowed only "
                    "for local/test. Set a strong ADMIN_SECRET before deploying."
                )
            return

        if insecure:
            raise ValueError(
                "ADMIN_SECRET must be set to a strong non-default value when "
                f"ENVIRONMENT is '{env}'. Refusing to start."
            )

    def __init__(self, **kwargs):
        """
        Initialize configuration.

        Environment variables are loaded via EnvironmentManager before
        Pydantic processes them.
        """
        # Ensure environment is loaded first
        env_manager = get_env_manager()

        # Log environment summary on first initialization
        if not hasattr(Config, "_initialized"):
            env_manager.log_summary()
            Config._initialized = True

        # Initialize Pydantic settings
        super().__init__(**kwargs)

        # Create directories if they don't exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

    def validate_api_keys(self) -> bool:
        """
        Validate that at least one API key is configured.

        Uses the EnvironmentManager for validation with proper logging.
        """
        return env_validate_api_keys()

    def get_llm_api_key(self, provider: str) -> Optional[str]:
        """Return configured API key for the requested LLM provider."""
        provider_name = provider.strip().lower()
        provider_key_map = {
            "openai": self.openai_api_key,
            "gemini": self.gemini_api_key,
        }
        return provider_key_map.get(provider_name)

    def resolve_llm_provider(self, provider: Optional[str] = None) -> str:
        """Resolve provider with fallback to configured default provider."""
        return (provider or self.default_llm_provider).strip().lower()


# Global configuration instance
# This is initialized lazily to ensure environment is loaded first
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get the global configuration instance.

    This function ensures the config is initialized after environment
    variables are loaded, providing proper initialization order.

    Returns:
        Config instance
    """
    global _config
    if _config is None:
        _config = Config()
    return _config


# For backward compatibility, provide direct access
# But prefer using get_config() for better control
config = get_config()
