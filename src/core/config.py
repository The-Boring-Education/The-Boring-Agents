"""Core configuration management for The Boring Agents."""

import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Configuration settings for The Boring Agents application."""
    
    # API Keys
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    huggingface_api_key: Optional[str] = Field(default=None, env="HUGGINGFACE_API_KEY")
    
    # Application Settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    output_dir: str = Field(default="./output", env="OUTPUT_DIR")
    temp_dir: str = Field(default="./temp", env="TEMP_DIR")
    
    # Content Generation Settings
    default_model: str = Field(default="gpt-3.5-turbo", env="DEFAULT_MODEL")
    max_tokens: int = Field(default=2000, env="MAX_TOKENS")
    temperature: float = Field(default=0.7, env="TEMPERATURE")
    max_context_length: int = Field(default=16000, env="MAX_CONTEXT_LENGTH")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
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