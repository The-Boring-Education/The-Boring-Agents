"""OpenAI provider implementation for LLM abstraction layer."""

from langchain_openai import ChatOpenAI

from src.core.llm.base import LLMProvider


class OpenAIProvider(LLMProvider):
    """OpenAI-backed LLM provider using LangChain ChatOpenAI."""

    def __init__(self, config):
        super().__init__(config)
        if not self.config.api_key:
            raise ValueError("OPENAI_API_KEY is required for openai provider")
        self._client = ChatOpenAI(
            model_name=self.config.model,
            openai_api_key=self.config.api_key,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            **self.config.model_kwargs,
        )

    def generate(self, prompt: str) -> str:
        response = self._client.invoke(prompt)
        return response.content.strip()
