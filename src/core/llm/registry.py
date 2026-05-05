"""Factory/registry for provider-specific LLM clients."""

from typing import Any

from src.core.config import config
from src.core.llm.base import LLMProvider
from src.core.llm.gemini import GeminiProvider
from src.core.llm.openai import OpenAIProvider
from src.core.llm.types import LLMConfig


PROVIDER_REGISTRY = {
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
}


def get_llm(provider: str, model: str, **kwargs: Any) -> LLMProvider:
    """Instantiate an LLM provider implementation from the registry."""
    provider_name = config.resolve_llm_provider(provider)
    provider_cls = PROVIDER_REGISTRY.get(provider_name)
    if provider_cls is None:
        supported = ", ".join(sorted(PROVIDER_REGISTRY.keys()))
        raise ValueError(
            f"Unsupported LLM provider '{provider_name}'. Supported providers: {supported}"
        )

    llm_config = LLMConfig(
        provider=provider_name,
        model=model,
        temperature=float(kwargs.pop("temperature", config.temperature)),
        max_tokens=int(kwargs.pop("max_tokens", config.max_tokens)),
        api_key=config.get_llm_api_key(provider_name),
        model_kwargs=kwargs,
    )
    return provider_cls(llm_config)
