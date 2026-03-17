"""DSA content generation controller."""

import logging
from typing import Any, Dict

from src.agents.interview.dsa_content_generator import DSAContentGenerator
from src.api.models.dsa_content_models import (
    DSAContentGenerateRequest,
    DSAContentGenerateResponse,
)

logger = logging.getLogger(__name__)


class DSAContentController:
    """Controller for DSA question content generation."""

    def __init__(self):
        self._generator = None

    @property
    def generator(self) -> DSAContentGenerator:
        """Lazy-init the generator (avoids LLM init until first request)."""
        if self._generator is None:
            self._generator = DSAContentGenerator()
        return self._generator

    def generate_content(
        self, payload: DSAContentGenerateRequest
    ) -> DSAContentGenerateResponse:
        """Generate structured DSA content sections for a question.

        Args:
            payload: Request with question metadata.

        Returns:
            Response with the 8 structured content sections.
        """
        logger.info(
            "DSA content generation requested: question=%s, topic=%s, difficulty=%s",
            payload.question[:60],
            payload.topic,
            payload.difficulty,
        )

        try:
            # Convert examples from Pydantic models to dicts
            examples = [
                {
                    "inputText": ex.inputText,
                    "outputText": ex.outputText,
                    "explanation": ex.explanation or "",
                }
                for ex in payload.examples
            ]

            result = self.generator.generate_content(
                question=payload.question,
                topic=payload.topic,
                difficulty=payload.difficulty,
                constraints=payload.constraints,
                examples=examples,
                leetcode_url=payload.leetcode_url,
            )

            logger.info(
                "DSA content generated successfully for: %s",
                payload.question[:60],
            )

            return DSAContentGenerateResponse(
                status="success",
                sections=result.get("sections"),
                question=result.get("question"),
                topic=result.get("topic"),
                difficulty=result.get("difficulty"),
            )

        except ValueError as e:
            logger.error("Validation error in DSA content generation: %s", e)
            return DSAContentGenerateResponse(
                status="error",
                error=f"Content generation failed: {str(e)}",
            )
        except Exception as e:
            logger.error(
                "Unexpected error in DSA content generation: %s", e, exc_info=True
            )
            return DSAContentGenerateResponse(
                status="error",
                error=f"Internal error: {str(e)}",
            )
