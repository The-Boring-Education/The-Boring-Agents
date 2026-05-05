"""Base contracts for provider-agnostic LLM clients."""

import json
from abc import ABC, abstractmethod
from types import SimpleNamespace
from typing import Any, Dict, Optional

from src.core.llm.types import LLMConfig, LLMResponse


class LLMProvider(ABC):
    """Provider abstraction used by agents to generate text and JSON."""

    def __init__(self, config: LLMConfig):
        self.config = config

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate plain text output for a prompt."""

    def generate_json(self, prompt: str) -> Dict[str, Any]:
        """Generate output and parse it as JSON object."""
        raw_content = self.generate(prompt)
        parsed = json.loads(raw_content)
        if not isinstance(parsed, dict):
            raise ValueError("Expected JSON object response from LLM")
        return parsed

    def invoke(self, prompt: str) -> Any:
        """Compatibility helper for code paths expecting LangChain style invoke()."""
        return SimpleNamespace(content=self.generate(prompt))

    def build_response(self, content: str, raw: Optional[Any] = None) -> LLMResponse:
        """Create a normalized response payload."""
        return LLMResponse(
            content=content,
            provider=self.config.provider,
            model=self.config.model,
            raw=raw,
        )
