"""Type definitions for LLM provider abstractions."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class LLMConfig:
    """Configuration used to instantiate an LLM provider."""

    provider: str
    model: str
    temperature: float
    max_tokens: int
    api_key: Optional[str] = None
    model_kwargs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """Normalized response from an LLM provider."""

    content: str
    provider: str
    model: str
    raw: Optional[Any] = None
