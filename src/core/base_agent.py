"""Base agent class for all content generation agents."""

import json
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from src.core.config import config

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all content generation agents."""

    CUSTOM_PARAM_KEYS = frozenset({"technology"})

    def __init__(self, model_name: Optional[str] = None, **kwargs):
        self.model_name = model_name or config.default_model
        self.logger = logging.getLogger(self.__class__.__name__)

        self.model_kwargs = {k: v for k, v in kwargs.items() if k not in self.CUSTOM_PARAM_KEYS}
        self.custom_params = {k: v for k, v in kwargs.items() if k in self.CUSTOM_PARAM_KEYS}

        self._llm: Optional[BaseChatModel] = None
        self.prompt_templates = self._get_prompt_templates()

        self.logger.info(
            "%s initialized | model=%s temperature=%s max_tokens=%s",
            self.__class__.__name__, self.model_name, config.temperature, config.max_tokens,
        )

    @property
    def llm(self) -> BaseChatModel:
        """Get the language model instance, initializing if needed."""
        if self._llm is None:
            self._llm = self._initialize_llm(**self.model_kwargs)
        return self._llm

    def _initialize_llm(self, **kwargs) -> BaseChatModel:
        if not config.openai_api_key:
            raise ValueError("No valid API key found. Please set OPENAI_API_KEY in your environment.")

        return ChatOpenAI(
            model_name=self.model_name,
            openai_api_key=config.openai_api_key,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            **kwargs,
        )

    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates specific to this agent.

        Override in subclasses that use the template-based prompt system.
        Defaults to empty dict for agents that use their own prompting strategy.
        """
        return {}

    @abstractmethod
    def generate_content(self, **kwargs) -> Dict[str, Any]:
        """Generate content based on the agent's specific purpose."""
        pass

    def _format_prompt(self, template_name: str, **kwargs) -> str:
        if template_name not in self.prompt_templates:
            raise ValueError(f"Template '{template_name}' not found in {self.__class__.__name__}")
        return self.prompt_templates[template_name].format(**kwargs)

    def _generate_with_prompt(self, prompt: str) -> str:
        try:
            estimated_tokens = len(prompt.split()) * 1.3
            if estimated_tokens > config.max_context_length:
                self.logger.warning("Prompt may exceed context length: ~%.0f tokens", estimated_tokens)
                max_words = int(config.max_context_length / 1.3)
                words = prompt.split()
                if len(words) > max_words:
                    self.logger.warning("Truncating prompt from %d to %d words", len(words), max_words)
                    prompt = " ".join(words[:max_words])

            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            self.logger.error("Error generating content: %s", e)
            raise

    def save_content(self, content: Dict[str, Any], filename: str) -> str:
        filepath = os.path.join(config.output_dir, f"{filename}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        self.logger.info("Content saved to %s", filepath)
        return filepath