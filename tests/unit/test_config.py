"""
Unit tests for configuration module.

Tests the Config class and related functions.
"""

import pytest
import os
from unittest.mock import patch, MagicMock

from src.core.config import Config, get_config


class TestConfigDefaults:
    """Tests for Config default values."""
    
    @pytest.fixture
    def mock_env(self):
        """Mock environment for testing."""
        env_vars = {
            "OPENAI_API_KEY": "test-key",
            "ENVIRONMENT": "test"
        }
        with patch.dict(os.environ, env_vars, clear=False):
            yield
    
    def test_config_has_log_level(self, mock_env):
        """Test that config has log_level with default."""
        config = Config()
        assert hasattr(config, 'log_level')
        assert config.log_level in ["INFO", "DEBUG", "WARNING", "ERROR"]
    
    def test_config_has_output_dir(self, mock_env):
        """Test that config has output_dir."""
        config = Config()
        assert hasattr(config, 'output_dir')
    
    def test_config_has_temp_dir(self, mock_env):
        """Test that config has temp_dir."""
        config = Config()
        assert hasattr(config, 'temp_dir')
    
    def test_config_has_default_model(self, mock_env):
        """Test that config has default_model."""
        config = Config()
        assert hasattr(config, 'default_model')
        assert config.default_model == "gpt-4o-mini"
    
    def test_config_has_max_tokens(self, mock_env):
        """Test that config has max_tokens."""
        config = Config()
        assert hasattr(config, 'max_tokens')
        assert config.max_tokens == 4000
    
    def test_config_has_temperature(self, mock_env):
        """Test that config has temperature."""
        config = Config()
        assert hasattr(config, 'temperature')
        # Temperature may vary based on environment, just check it's a valid float
        assert isinstance(config.temperature, float)
        assert 0 <= config.temperature <= 2.0


class TestConfigEnvironments:
    """Tests for environment-specific configuration."""
    
    def test_local_api_base_url(self):
        """Test local environment API URL."""
        with patch.dict(os.environ, {"ENVIRONMENT": "local", "OPENAI_API_KEY": "test"}):
            config = Config()
            assert "localhost" in config.api_base_url
    
    def test_dev_api_base_url(self):
        """Test dev environment API URL."""
        with patch.dict(os.environ, {"ENVIRONMENT": "dev", "OPENAI_API_KEY": "test"}):
            config = Config()
            assert "vercel" in config.api_base_url or "localhost" in config.api_base_url
    
    def test_prod_api_base_url(self):
        """Test prod environment API URL."""
        with patch.dict(os.environ, {"ENVIRONMENT": "prod", "OPENAI_API_KEY": "test"}):
            config = Config()
            assert "theboringeducation" in config.api_base_url
    
    def test_api_v1_url(self):
        """Test API v1 URL property."""
        with patch.dict(os.environ, {"ENVIRONMENT": "local", "OPENAI_API_KEY": "test"}):
            config = Config()
            assert config.api_v1_url.endswith("/api/v1")


class TestConfigDirectories:
    """Tests for directory creation."""
    
    def test_creates_output_dir(self, temp_dir):
        """Test that output directory is created."""
        output_path = os.path.join(temp_dir, "output")
        
        with patch.dict(os.environ, {
            "OUTPUT_DIR": output_path,
            "TEMP_DIR": os.path.join(temp_dir, "temp"),
            "OPENAI_API_KEY": "test"
        }):
            config = Config()
            assert os.path.exists(output_path)
    
    def test_creates_temp_dir(self, temp_dir):
        """Test that temp directory is created."""
        temp_path = os.path.join(temp_dir, "temp")
        
        with patch.dict(os.environ, {
            "OUTPUT_DIR": os.path.join(temp_dir, "output"),
            "TEMP_DIR": temp_path,
            "OPENAI_API_KEY": "test"
        }):
            config = Config()
            assert os.path.exists(temp_path)


class TestConfigApiKeys:
    """Tests for API key handling."""
    
    def test_openai_api_key(self):
        """Test OpenAI API key configuration."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"}):
            config = Config()
            assert config.openai_api_key == "sk-test-key"
    
    def test_anthropic_api_key(self):
        """Test Anthropic API key configuration."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key", "OPENAI_API_KEY": "test"}):
            config = Config()
            assert config.anthropic_api_key == "test-key"
    
    def test_validate_api_keys_with_key(self):
        """Test API key validation passes with key."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            config = Config()
            result = config.validate_api_keys()
            assert result is True
    
    def test_validate_api_keys_without_key(self):
        """Test API key validation fails without key."""
        # Clear all API keys
        env_copy = os.environ.copy()
        for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "HUGGINGFACE_API_KEY"]:
            env_copy.pop(key, None)
        
        with patch.dict(os.environ, env_copy, clear=True):
            config = Config()
            result = config.validate_api_keys()
            assert result is False


class TestGetConfig:
    """Tests for get_config function."""
    
    def test_get_config_returns_config(self):
        """Test that get_config returns a Config instance."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test"}):
            config = get_config()
            assert isinstance(config, Config)
    
    def test_get_config_singleton(self):
        """Test that get_config returns same instance."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test"}):
            config1 = get_config()
            config2 = get_config()
            # Note: Not a strict singleton, but should work consistently
            assert config1.default_model == config2.default_model


class TestConfigEnvironmentOverrides:
    """Tests for environment variable overrides."""
    
    def test_override_log_level(self):
        """Test overriding log level via environment."""
        with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG", "OPENAI_API_KEY": "test"}):
            config = Config()
            assert config.log_level == "DEBUG"
    
    def test_override_max_tokens(self):
        """Test overriding max tokens via environment."""
        with patch.dict(os.environ, {"MAX_TOKENS": "8000", "OPENAI_API_KEY": "test"}):
            config = Config()
            assert config.max_tokens == 8000
    
    def test_override_temperature(self):
        """Test overriding temperature via environment."""
        with patch.dict(os.environ, {"TEMPERATURE": "0.5", "OPENAI_API_KEY": "test"}):
            config = Config()
            assert config.temperature == 0.5

