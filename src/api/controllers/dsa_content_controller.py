"""DSA content generation controller."""

import logging
import time
from typing import Any, Dict, List, Optional

import requests

from src.agents.interview.dsa_content_generator import DSAContentGenerator
from src.api.models.dsa_content_models import (
    DSAContentBulkEnrichRequest,
    DSAContentBulkEnrichResponse,
    DSAContentEnrichRequest,
    DSAContentGenerateRequest,
    DSAContentGenerateResponse,
)
from src.core.config import config

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
            # If resources is null in DB, .get("resources", {}) still returns None
            resources = question_data.get("resources") or {}
            
            gen_payload = DSAContentGenerateRequest(
                question=question_data.get("title", ""),
                topic=question_data.get("topics", ["Array"])[0],
                difficulty=question_data.get("difficulty", "Medium"),
                constraints=[],
                examples=[],
                leetcodeUrl=resources.get("leetcodeURL") or "",
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

    def bulk_enrich_content(
        self, payload: DSAContentBulkEnrichRequest
    ) -> DSAContentBulkEnrichResponse:
        """Fetch all questions, find those without sections, and enrich them.

        Args:
            payload: Bulk enrichment options.

        Returns:
            Summary of enrichment results.
        """
        api_url = (payload.api_url or config.api_base_url).rstrip("/")
        # We use the export API to get all questions efficiently
        export_url = f"{api_url}/api/v1/content/export?type=dsa-questions"
        headers = {
            "x-admin-secret": payload.admin_secret or "TBEAdmin",
            "Content-Type": "application/json",
        }

        try:
            # 1. Fetch all questions
            logger.info("Bulk enrichment: Fetching all questions from %s...", api_url)
            response = requests.get(export_url, headers=headers, timeout=60)
            response.raise_for_status()

            raw_data = response.json().get("data", {}).get("dsaQuestions", {})
            all_questions = raw_data.get("questions", [])
            logger.info("Fetched %d total questions", len(all_questions))

            # 2. Filter for questions to enrich
            to_enrich = []
            for q in all_questions:
                # Enrich if sections is missing/null OR if force is True
                if payload.force or not q.get("sections"):
                    to_enrich.append(q)

            total_found = len(to_enrich)
            logger.info("Found %d questions that need enrichment", total_found)

            # 3. Limit the batch
            to_enrich = to_enrich[:payload.limit]
            logger.info("Processing batch of %d questions", len(to_enrich))

            enriched_count = 0
            failed_count = 0
            details = []

            # 4. Process each question
            enrich_payload = DSAContentEnrichRequest(
                admin_secret=payload.admin_secret,
                api_url=payload.api_url,
            )

            for i, q in enumerate(to_enrich):
                question_id = q.get("_id")
                question_title = q.get("title", "Unknown")

                logger.info("[%d/%d] Processing: %s (ID: %s)", i+1, len(to_enrich), question_title, question_id)

                result = self.enrich_content(question_id, enrich_payload)

                if result.status == "success":
                    enriched_count += 1
                else:
                    failed_count += 1

                details.append({
                    "id": question_id,
                    "title": question_title,
                    "status": result.status,
                    "error": result.error
                })

                # Rate limiting delay
                if i < len(to_enrich) - 1:
                    logger.info("Sleeping for %.1f seconds...", payload.delay)
                    time.sleep(payload.delay)

            return DSAContentBulkEnrichResponse(
                status="success" if failed_count == 0 else "completed_with_errors",
                total_found=total_found,
                enriched_count=enriched_count,
                failed_count=failed_count,
                details=details
            )

        except Exception as e:
            logger.error("Bulk enrichment failed: %s", e, exc_info=True)
            return DSAContentBulkEnrichResponse(
                status="error",
                total_found=0,
                enriched_count=0,
                failed_count=0,
                error=str(e)
            )
