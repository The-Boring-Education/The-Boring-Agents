"""Gemini provider implementation for LLM abstraction layer."""

from src.core.llm.base import LLMProvider


class GeminiProvider(LLMProvider):
    """Gemini-backed provider. Requires langchain-google-genai package."""

    def __init__(self, config):
        super().__init__(config)
        if not self.config.api_key:
            raise ValueError("GEMINI_API_KEY is required for gemini provider")

        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError as exc:
            raise ImportError(
                "Gemini provider requires 'langchain-google-genai'. Install it to use this provider."
            ) from exc

        self._client = ChatGoogleGenerativeAI(
            model=self.config.model,
            google_api_key=self.config.api_key,
            temperature=self.config.temperature,
            max_output_tokens=self.config.max_tokens,
            **self.config.model_kwargs,
        )

    def generate(self, prompt: str) -> str:
        response = self._client.invoke(prompt)
        return response.content.strip()
