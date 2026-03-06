"""Aptitude answer generation workflow.

Takes a list of questions with their topics, determines the answer format,
generates structured answers via LLM, validates output, and saves to JSON.
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from slugify import slugify

from src.core.config import config
from src.agents.aptitude.constants import (
    SUB_CATEGORY_FORMAT_MAP,
    get_format_for_sub_category,
    get_topic_info,
    validate_topic_name,
)
from src.agents.aptitude.generators import get_aptitude_generator
from src.agents.aptitude.validators import (
    validate_answer_structure,
    validate_question_payload,
    validate_topic_payload,
)

logger = logging.getLogger(__name__)


class AptitudeWorkflow:
    """Orchestrates the aptitude answer generation pipeline.

    Usage:
        workflow = AptitudeWorkflow()
        result = workflow.process_topic(
            topic_name="Problem on Trains",
            questions=["A train running at 60 km/hr...", "Two trains..."]
        )
    """

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or os.path.join(config.output_dir, "aptitude")
        os.makedirs(self.output_dir, exist_ok=True)

    def process_topic(
        self,
        topic_name: str,
        questions: List[str],
        category: Optional[str] = None,
        sub_category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate answers for all questions under a single topic.

        Args:
            topic_name: Name of the topic (must exist in TOPIC_REGISTRY or category/sub_category must be provided)
            questions: List of question strings
            category: Override category (if topic not in registry)
            sub_category: Override sub-category (if topic not in registry)

        Returns:
            Dict with topic info, questions with answers, and output file path
        """
        validation = validate_topic_payload(topic_name, questions, category, sub_category)
        if not validation["valid"]:
            raise ValueError(f"Invalid payload: {validation['errors']}")

        if validate_topic_name(topic_name):
            topic_info = get_topic_info(topic_name)
        else:
            if not category or not sub_category:
                raise ValueError(
                    f"Topic '{topic_name}' not in registry. "
                    f"Provide category and sub_category explicitly."
                )
            format_type = get_format_for_sub_category(sub_category)
            topic_info = {
                "name": topic_name,
                "category": category.upper(),
                "subCategory": sub_category.upper(),
                "answerFormatType": format_type,
            }

        format_type = topic_info["answerFormatType"]
        generator = get_aptitude_generator(format_type)

        logger.info(
            "Processing topic: %s (%s format, %d questions)",
            topic_name, format_type, len(questions),
        )

        results: List[Dict[str, Any]] = []
        for idx, question_text in enumerate(questions, 1):
            logger.info("Generating answer %d/%d: %s...", idx, len(questions), question_text[:50])

            try:
                answer = generator.generate_answer(
                    question=question_text,
                    topic=topic_name,
                    sub_category=topic_info["subCategory"],
                )

                answer_validation = validate_answer_structure(answer, format_type)

                results.append({
                    "question": question_text,
                    "answer": answer,
                    "difficulty": "MEDIUM",
                    "order": idx,
                    "isActive": True,
                    "validation": answer_validation,
                })
            except Exception as e:
                logger.error("Failed to generate answer for Q%d: %s", idx, e)
                results.append({
                    "question": question_text,
                    "answer": "",
                    "difficulty": "MEDIUM",
                    "order": idx,
                    "isActive": True,
                    "validation": {"valid": False, "errors": [str(e)]},
                })

        topic_slug = slugify(topic_name)
        output_data = {
            "topic": {
                "name": topic_name,
                "slug": topic_slug,
                "category": topic_info["category"],
                "subCategory": topic_info["subCategory"],
                "answerFormatType": format_type,
            },
            "questions": results,
            "metadata": {
                "generatedAt": datetime.now(timezone.utc).isoformat(),
                "totalQuestions": len(questions),
                "successfulAnswers": sum(1 for r in results if r["answer"]),
                "failedAnswers": sum(1 for r in results if not r["answer"]),
            },
        }

        output_file = os.path.join(self.output_dir, f"{topic_slug}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        logger.info("Saved output to %s", output_file)
        output_data["outputFile"] = output_file
        return output_data

    def process_batch(
        self,
        topics: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Process multiple topics in batch.

        Args:
            topics: List of dicts with keys: name, questions, (optional) category, sub_category

        Returns:
            Summary with per-topic results
        """
        results = []
        for topic_data in topics:
            topic_name = topic_data["name"]
            questions = topic_data.get("questions", [])

            if not questions:
                logger.warning("Skipping topic '%s' — no questions provided", topic_name)
                results.append({
                    "topic": topic_name,
                    "status": "skipped",
                    "reason": "no questions",
                })
                continue

            try:
                result = self.process_topic(
                    topic_name=topic_name,
                    questions=questions,
                    category=topic_data.get("category"),
                    sub_category=topic_data.get("sub_category") or topic_data.get("subCategory"),
                )
                results.append({
                    "topic": topic_name,
                    "status": "success",
                    "outputFile": result.get("outputFile"),
                    "totalQuestions": result["metadata"]["totalQuestions"],
                    "successfulAnswers": result["metadata"]["successfulAnswers"],
                })
            except Exception as e:
                logger.error("Failed to process topic '%s': %s", topic_name, e)
                results.append({
                    "topic": topic_name,
                    "status": "failed",
                    "error": str(e),
                })

        summary_file = os.path.join(self.output_dir, "_batch_summary.json")
        summary = {
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "totalTopics": len(topics),
            "successful": sum(1 for r in results if r["status"] == "success"),
            "failed": sum(1 for r in results if r["status"] == "failed"),
            "skipped": sum(1 for r in results if r["status"] == "skipped"),
            "results": results,
        }
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        logger.info(
            "Batch complete: %d/%d successful, saved summary to %s",
            summary["successful"], summary["totalTopics"], summary_file,
        )
        return summary
