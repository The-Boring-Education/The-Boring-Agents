"""Core configuration management for The Boring Agents."""

import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    huggingface_api_key: Optional[str] = Field(default=None, env="HUGGINGFACE_API_KEY")
    
    # Application Settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    output_dir: str = Field(default="./output", env="OUTPUT_DIR")
    temp_dir: str = Field(default="./temp", env="TEMP_DIR")
    
    # Content Generation Settings
    default_model: str = Field(default="gpt-4o-mini", env="DEFAULT_MODEL")
    max_tokens: int = Field(default=4000, env="MAX_TOKENS")
    temperature: float = Field(default=0.8, env="TEMPERATURE")
    max_context_length: int = Field(default=16000, env="MAX_CONTEXT_LENGTH")
    
    # API Configuration
    environment: str = Field(default="dev", env="ENVIRONMENT")  # local, dev, or prod
    local_api_base_url: str = Field(default="http://localhost:3000", env="LOCAL_API_BASE_URL")
    dev_api_base_url: str = Field(default="https://tbe-dev-git-development-tbe.vercel.app", env="DEV_API_BASE_URL")
    prod_api_base_url: str = Field(default="https://www.theboringeducation.com", env="PROD_API_BASE_URL")
    
    @property
    def api_base_url(self) -> str:
        """Get the appropriate API base URL based on environment."""
        if self.environment == "local":
            return self.local_api_base_url
        elif self.environment == "prod":
            return self.prod_api_base_url
        return self.dev_api_base_url
    
    @property
    def api_v1_url(self) -> str:
        """Get the API v1 URL with /api/v1 suffix."""
        return f"{self.api_base_url}/api/v1"
    
    def __init__(self, **kwargs):
        # Load environment variables from .env file
        load_dotenv()
        super().__init__(**kwargs)
        
        # Create directories if they don't exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def validate_api_keys(self) -> bool:
        """Validate that at least one API key is configured."""
        return any([
            self.openai_api_key,
            self.anthropic_api_key,
            self.huggingface_api_key
        ])


# Global configuration instance
config = Config()