"""DSA content generation controller."""

import logging
from typing import Any, Dict, Optional

from src.agents.interview.dsa_content_generator import DSAContentGenerator
from src.api.models.dsa_content_models import (
    DSAContentEnrichRequest,
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

    def enrich_content(
        self, question_id: str, payload: DSAContentEnrichRequest
    ) -> DSAContentGenerateResponse:
        """Fetch existing question from TBE-Web, enrich it, and push back.

        Args:
            question_id: TBE-Web DSA question ID.
            payload: Enrichment options (admin secret, etc).

        Returns:
            Response with success/error status.
        """
        import requests
        from src.core.config import config

        api_url = (payload.api_url or config.api_base_url).rstrip("/")
        get_url = f"{api_url}/api/v1/interview-prep/dsa-sheet/{question_id}"
        patch_url = get_url  # Same endpoint for PATCH

        headers = {
            "x-admin-secret": payload.admin_secret or "TBEAdmin",
            "Content-Type": "application/json",
        }

        try:
            # 1. Fetch existing question
            logger.info("Enriching question %s: Fetching metadata...", question_id)
            get_response = requests.get(get_url, headers=headers, timeout=10)
            if get_response.status_code != 200:
                return DSAContentGenerateResponse(
                    status="error",
                    error=f"Failed to fetch question: HTTP {get_response.status_code}",
                )

            question_data = get_response.json().get("data", {})
            if not question_data:
                return DSAContentGenerateResponse(
                    status="error",
                    error="Question data not found in TBE response",
                )

            # 2. Extract info for generation
            # Note: TBE-Web uses 'title' for name, agent uses 'question'
            # TBE-Web uses 'resources.leetcodeURL', agent uses 'leetcodeUrl'
            resources = question_data.get("resources", {})
            gen_payload = DSAContentGenerateRequest(
                question=question_data.get("title", ""),
                topic=question_data.get("topics", ["Array"])[0],
                difficulty=question_data.get("difficulty", "Medium"),
                constraints=[],  # TBE doesn't seem to store raw constraints list
                examples=[],  # TBE doesn't store structured examples
                leetcodeUrl=resources.get("leetcodeURL", ""),
            )

            # 3. Generate content
            logger.info("Enriching question %s: Generating sections...", question_id)
            gen_result = self.generate_content(gen_payload)
            if gen_result.status != "success":
                return gen_result

            # 4. Push back to TBE-Web
            logger.info("Enriching question %s: Pushing sections to DB...", question_id)
            sections = gen_result.sections
            patch_response = requests.patch(
                patch_url, json={"sections": sections}, headers=headers, timeout=30
            )

            if patch_response.status_code not in (200, 201):
                return DSAContentGenerateResponse(
                    status="error",
                    error=f"Failed to push sections: HTTP {patch_response.status_code} - {patch_response.text}",
                )

            logger.info("Enriching question %s: Success!", question_id)
            return gen_result

        except Exception as e:
            logger.error("Enrichment error: %s", e, exc_info=True)
            return DSAContentGenerateResponse(
                status="error", error=f"Enrichment failed: {str(e)}"
            )
