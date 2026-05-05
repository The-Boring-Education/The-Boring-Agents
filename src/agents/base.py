"""Base agent class for all content generation agents.

All agents (interview, quiz, shiksha, etc.) inherit from BaseAgent.
Provides LLM initialization, prompt template management, and content generation.
"""

import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from langchain_core.prompts import PromptTemplate

from src.core.config import config
from src.core.llm import LLMProvider, get_llm

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all content generation agents."""

    CUSTOM_PARAM_KEYS = frozenset({"technology"})

    def __init__(
        self,
        model_name: Optional[str] = None,
        llm_provider: Optional[str] = None,
        **kwargs,
    ):
        self.model_name = model_name or config.default_model
        self.llm_provider = config.resolve_llm_provider(llm_provider)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.model_kwargs = {
            k: v for k, v in kwargs.items() if k not in self.CUSTOM_PARAM_KEYS
        }
        self.custom_params = {
            k: v for k, v in kwargs.items() if k in self.CUSTOM_PARAM_KEYS
        }

        self._llm: Optional[LLMProvider] = None
        self.prompt_templates = self._get_prompt_templates()

        self.logger.info(
            "%s initialized | provider=%s model=%s temperature=%s max_tokens=%s",
            self.__class__.__name__,
            self.llm_provider,
            self.model_name,
            config.temperature,
            config.max_tokens,
        )

    @property
    def llm(self) -> LLMProvider:
        if self._llm is None:
            self._llm = self._initialize_llm(**self.model_kwargs)
        return self._llm

    def _initialize_llm(self, **kwargs) -> LLMProvider:
        if not config.get_llm_api_key(self.llm_provider):
            raise ValueError(
                f"No valid API key found for provider '{self.llm_provider}'."
            )
        return get_llm(
            provider=self.llm_provider,
            model=self.model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            **kwargs,
        )

    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Override in subclasses that use the template-based prompt system."""
        return {}

    @abstractmethod
    def generate_content(self, **kwargs) -> Dict[str, Any]:
        pass

    def _format_prompt(self, template_name: str, **kwargs) -> str:
        if template_name not in self.prompt_templates:
            raise ValueError(
                f"Template '{template_name}' not found in {self.__class__.__name__}"
            )
        return self.prompt_templates[template_name].format(**kwargs)

    def _generate_with_prompt(self, prompt: str) -> str:
        try:
            estimated_tokens = len(prompt.split()) * 1.3
            if estimated_tokens > config.max_context_length:
                self.logger.warning(
                    "Prompt may exceed context length: ~%.0f tokens", estimated_tokens
                )
                max_words = int(config.max_context_length / 1.3)
                words = prompt.split()
                if len(words) > max_words:
                    self.logger.warning(
                        "Truncating prompt from %d to %d words", len(words), max_words
                    )
                    prompt = " ".join(words[:max_words])
            return self.llm.generate(prompt).strip()
        except Exception as e:
            self.logger.error("Error generating content: %s", e)
            raise

    def save_content(self, content: Dict[str, Any], filename: str) -> str:
        filepath = os.path.join(config.output_dir, f"{filename}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        self.logger.info("Content saved to %s", filepath)
        return filepath
