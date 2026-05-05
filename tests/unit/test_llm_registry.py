"""Unit tests for LLM provider registry and abstraction."""

import sys
import types
from unittest.mock import Mock, patch

import pytest

from src.core.llm.base import LLMProvider
from src.core.llm.registry import get_llm


class TestLLMRegistry:
    """Tests for provider registry behavior."""

    def test_get_openai_provider(self):
        """Creates openai provider with expected contract."""
        with patch("src.core.llm.openai.ChatOpenAI") as chat_openai:
            mock_client = Mock()
            mock_client.invoke.return_value = Mock(content="Hello world")
            chat_openai.return_value = mock_client

            provider = get_llm(provider="openai", model="gpt-4o-mini")
            assert isinstance(provider, LLMProvider)
            assert provider.generate("hi") == "Hello world"

    def test_get_unknown_provider_raises(self):
        """Unknown provider names should fail fast."""
        with pytest.raises(ValueError):
            get_llm(provider="unsupported-provider", model="x")

    def test_get_gemini_provider(self):
        """Creates gemini provider with expected contract."""
        fake_module = types.ModuleType("langchain_google_genai")

        class FakeChatGoogleGenerativeAI:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

            def invoke(self, prompt):
                del prompt
                return Mock(content="Gemini response")

        fake_module.ChatGoogleGenerativeAI = FakeChatGoogleGenerativeAI

        with patch.dict(sys.modules, {"langchain_google_genai": fake_module}):
            with patch(
                "src.core.llm.registry.config.gemini_api_key",
                "test-gemini-key",
            ):
                provider = get_llm(provider="gemini", model="gemini-2.0-flash")
                assert isinstance(provider, LLMProvider)
                assert provider.generate("hi") == "Gemini response"

    def test_generate_json_parses_object(self):
        """generate_json parses JSON object response."""
        with patch("src.core.llm.openai.ChatOpenAI") as chat_openai:
            mock_client = Mock()
            mock_client.invoke.return_value = Mock(content='{"ok": true, "count": 3}')
            chat_openai.return_value = mock_client

            provider = get_llm(provider="openai", model="gpt-4o-mini")
            payload = provider.generate_json("return json")
            assert payload["ok"] is True
            assert payload["count"] == 3

    def test_generate_json_non_object_raises(self):
        """generate_json should reject non-object payloads."""
        with patch("src.core.llm.openai.ChatOpenAI") as chat_openai:
            mock_client = Mock()
            mock_client.invoke.return_value = Mock(content='[1, 2, 3]')
            chat_openai.return_value = mock_client

            provider = get_llm(provider="openai", model="gpt-4o-mini")
            with pytest.raises(ValueError):
                provider.generate_json("return json array")
