"""
Unit tests for environment management module.

Tests the EnvironmentManager class and related functions.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.core.env import (
    EnvironmentManager,
    get_env_manager,
    get_env,
    get_env_bool,
    get_env_int,
    get_env_float,
    validate_api_keys,
)


class TestEnvironmentManagerGet:
    """Tests for EnvironmentManager.get method."""
    
    @pytest.fixture
    def env_manager(self):
        """Create a fresh environment manager instance."""
        # Reset singleton for testing
        EnvironmentManager._instance = None
        EnvironmentManager._loaded = False
        return EnvironmentManager()
    
    def test_get_existing_env_var(self, env_manager):
        """Test getting an existing environment variable."""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            result = env_manager.get("TEST_VAR")
            assert result == "test_value"
    
    def test_get_missing_env_var_returns_default(self, env_manager):
        """Test getting a missing variable returns default."""
        result = env_manager.get("NONEXISTENT_VAR", "default_value")
        assert result == "default_value"
    
    def test_get_missing_env_var_returns_none(self, env_manager):
        """Test getting a missing variable without default returns None."""
        result = env_manager.get("NONEXISTENT_VAR")
        assert result is None


class TestEnvironmentManagerGetBool:
    """Tests for EnvironmentManager.get_bool method."""
    
    @pytest.fixture
    def env_manager(self):
        """Create a fresh environment manager instance."""
        EnvironmentManager._instance = None
        EnvironmentManager._loaded = False
        return EnvironmentManager()
    
    def test_get_bool_true_values(self, env_manager):
        """Test that various true values are converted correctly."""
        true_values = ["1", "true", "True", "TRUE", "yes", "Yes", "YES", "on", "On", "ON"]
        
        for value in true_values:
            with patch.dict(os.environ, {"BOOL_VAR": value}):
                result = env_manager.get_bool("BOOL_VAR")
                assert result is True, f"Failed for value: {value}"
    
    def test_get_bool_false_values(self, env_manager):
        """Test that various false values are converted correctly."""
        false_values = ["0", "false", "False", "FALSE", "no", "No", "NO", "off", "Off", "OFF", ""]
        
        for value in false_values:
            with patch.dict(os.environ, {"BOOL_VAR": value}):
                result = env_manager.get_bool("BOOL_VAR")
                assert result is False, f"Failed for value: {value}"
    
    def test_get_bool_default_false(self, env_manager):
        """Test that default is False for missing variable."""
        result = env_manager.get_bool("NONEXISTENT_BOOL")
        assert result is False
    
    def test_get_bool_with_default(self, env_manager):
        """Test get_bool with custom default."""
        result = env_manager.get_bool("NONEXISTENT_BOOL", default=True)
        assert result is True


class TestEnvironmentManagerGetInt:
    """Tests for EnvironmentManager.get_int method."""
    
    @pytest.fixture
    def env_manager(self):
        """Create a fresh environment manager instance."""
        EnvironmentManager._instance = None
        EnvironmentManager._loaded = False
        return EnvironmentManager()
    
    def test_get_int_valid(self, env_manager):
        """Test getting a valid integer."""
        with patch.dict(os.environ, {"INT_VAR": "42"}):
            result = env_manager.get_int("INT_VAR")
            assert result == 42
    
    def test_get_int_negative(self, env_manager):
        """Test getting a negative integer."""
        with patch.dict(os.environ, {"INT_VAR": "-100"}):
            result = env_manager.get_int("INT_VAR")
            assert result == -100
    
    def test_get_int_invalid_returns_default(self, env_manager):
        """Test that invalid int returns default."""
        with patch.dict(os.environ, {"INT_VAR": "not_an_int"}):
            result = env_manager.get_int("INT_VAR", default=10)
            assert result == 10
    
    def test_get_int_missing_returns_default(self, env_manager):
        """Test that missing variable returns default."""
        result = env_manager.get_int("NONEXISTENT_INT", default=100)
        assert result == 100


class TestEnvironmentManagerGetFloat:
    """Tests for EnvironmentManager.get_float method."""
    
    @pytest.fixture
    def env_manager(self):
        """Create a fresh environment manager instance."""
        EnvironmentManager._instance = None
        EnvironmentManager._loaded = False
        return EnvironmentManager()
    
    def test_get_float_valid(self, env_manager):
        """Test getting a valid float."""
        with patch.dict(os.environ, {"FLOAT_VAR": "3.14"}):
            result = env_manager.get_float("FLOAT_VAR")
            assert result == 3.14
    
    def test_get_float_integer(self, env_manager):
        """Test getting an integer as float."""
        with patch.dict(os.environ, {"FLOAT_VAR": "42"}):
            result = env_manager.get_float("FLOAT_VAR")
            assert result == 42.0
    
    def test_get_float_invalid_returns_default(self, env_manager):
        """Test that invalid float returns default."""
        with patch.dict(os.environ, {"FLOAT_VAR": "not_a_float"}):
            result = env_manager.get_float("FLOAT_VAR", default=1.5)
            assert result == 1.5


class TestEnvironmentManagerValidation:
    """Tests for validation methods."""
    
    @pytest.fixture
    def env_manager(self):
        """Create a fresh environment manager instance."""
        EnvironmentManager._instance = None
        EnvironmentManager._loaded = False
        return EnvironmentManager()
    
    def test_validate_api_keys_with_openai(self, env_manager):
        """Test validation passes with OpenAI key."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"}):
            result = env_manager.validate_api_keys()
            assert result is True
    
    def test_validate_api_keys_with_anthropic(self, env_manager):
        """Test validation passes with Anthropic key."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}, clear=True):
            result = env_manager.validate_api_keys()
            assert result is True
    
    def test_validate_api_keys_missing_all(self, env_manager):
        """Test validation fails when no API keys are set."""
        # Clear all API keys
        env_copy = os.environ.copy()
        for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "HUGGINGFACE_API_KEY"]:
            env_copy.pop(key, None)
        
        with patch.dict(os.environ, env_copy, clear=True):
            result = env_manager.validate_api_keys()
            assert result is False
    
    def test_validate_required_all_set(self, env_manager):
        """Test required validation passes when all set."""
        result = env_manager.validate_required()
        assert result is True


class TestEnvironmentManagerGetAll:
    """Tests for get_all method."""
    
    @pytest.fixture
    def env_manager(self):
        """Create a fresh environment manager instance."""
        EnvironmentManager._instance = None
        EnvironmentManager._loaded = False
        return EnvironmentManager()
    
    def test_get_all_returns_dict(self, env_manager):
        """Test that get_all returns a dictionary."""
        result = env_manager.get_all()
        assert isinstance(result, dict)
    
    def test_get_all_includes_optional_vars(self, env_manager):
        """Test that get_all includes optional variables."""
        result = env_manager.get_all()
        assert "LOG_LEVEL" in result
        assert "OUTPUT_DIR" in result
    
    def test_get_all_masks_api_keys(self, env_manager):
        """Test that API keys are masked in get_all."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "secret-key"}):
            result = env_manager.get_all()
            assert result["OPENAI_API_KEY"] == "***"


class TestConvenienceFunctions:
    """Tests for convenience functions."""
    
    def test_get_env(self):
        """Test get_env convenience function."""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            result = get_env("TEST_VAR")
            assert result == "test_value"
    
    def test_get_env_bool(self):
        """Test get_env_bool convenience function."""
        with patch.dict(os.environ, {"TEST_BOOL": "true"}):
            result = get_env_bool("TEST_BOOL")
            assert result is True
    
    def test_get_env_int(self):
        """Test get_env_int convenience function."""
        with patch.dict(os.environ, {"TEST_INT": "42"}):
            result = get_env_int("TEST_INT")
            assert result == 42
    
    def test_get_env_float(self):
        """Test get_env_float convenience function."""
        with patch.dict(os.environ, {"TEST_FLOAT": "3.14"}):
            result = get_env_float("TEST_FLOAT")
            assert result == 3.14
    
    def test_validate_api_keys_function(self):
        """Test validate_api_keys convenience function."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            result = validate_api_keys()
            assert result is True


class TestEnvironmentManagerSingleton:
    """Tests for singleton behavior."""
    
    def test_singleton_returns_same_instance(self):
        """Test that singleton returns same instance."""
        # Reset singleton
        EnvironmentManager._instance = None
        EnvironmentManager._loaded = False
        
        manager1 = EnvironmentManager()
        manager2 = EnvironmentManager()
        
        assert manager1 is manager2
    
    def test_get_env_manager_returns_same_instance(self):
        """Test that get_env_manager returns consistent instance."""
        manager1 = get_env_manager()
        manager2 = get_env_manager()
        
        assert manager1 is manager2

