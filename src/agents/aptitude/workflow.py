"""Aptitude answer generation workflow.

Takes a topic (by slug or name), optionally a list of question strings
or a desired count, generates structured answers via LLM, and saves
output in a format that can be directly POSTed to TBE-Web's bulk upload API.

Output format matches TBE-Web's AptitudeUploadPayload:
    { "topic": "<slug>", "questions": [{ "question", "answer", "difficulty", "order" }] }
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.agents.aptitude.constants import (
    MIN_QUESTIONS_PER_TOPIC,
    resolve_topic,
)
from src.agents.aptitude.generators import get_aptitude_generator
from src.agents.aptitude.question_generator import AptitudeQuestionGenerator
from src.agents.aptitude.study_guide_generator import AptitudeStudyGuideGenerator
from src.core.config import config

logger = logging.getLogger(__name__)


class AptitudeWorkflow:
    """Orchestrates the aptitude generation pipeline.

    Usage:
        workflow = AptitudeWorkflow()

        # Option 1: just a topic slug → generates MIN_QUESTIONS_PER_TOPIC questions
        result = workflow.process_topic("problem-on-trains")

        # Option 2: topic + desired count
        result = workflow.process_topic("problem-on-trains", num_questions=15)

        # Option 3: topic + specific question strings
        result = workflow.process_topic("problem-on-trains", questions=["A train...", "Two trains..."])
    """

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or os.path.join(config.output_dir, "aptitude")
        os.makedirs(self.output_dir, exist_ok=True)

    def process_topic(
        self,
        topic: str,
        questions: Optional[List[str]] = None,
        num_questions: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Generate answers for a topic. Output matches TBE-Web bulk upload schema.

        Args:
            topic: Topic slug or name (resolved via TOPIC_REGISTRY)
            questions: Optional list of question strings to answer
            num_questions: Optional desired count (enforced >= MIN_QUESTIONS_PER_TOPIC)

        Returns:
            Dict with 'topic' (slug), 'questions' (list), and 'metadata'.
        """
        topic_info = resolve_topic(topic)
        topic_slug = topic_info["slug"]
        topic_name = topic_info["name"]
        format_type = topic_info["answerFormatType"]

        generator = get_aptitude_generator(format_type)

        if not questions:
            count = max(
                num_questions or MIN_QUESTIONS_PER_TOPIC, MIN_QUESTIONS_PER_TOPIC
            )
            logger.info(
                "No questions provided — generating %d for '%s'...", count, topic_name
            )
            question_gen = AptitudeQuestionGenerator()
            questions = question_gen.generate_questions(topic_name, count=count)

        logger.info(
            "Processing topic: %s [%s] (%s format, %d questions)",
            topic_name,
            topic_slug,
            format_type,
            len(questions),
        )

        results: List[Dict[str, Any]] = []
        for idx, q_item in enumerate(questions, 1):
            if isinstance(q_item, dict):
                question_text = q_item.get("question", "")
                options = q_item.get("options", [])
            else:
                question_text = str(q_item)
                options = []

            logger.info(
                "Generating answer %d/%d: %s...",
                idx,
                len(questions),
                question_text[:60],
            )

            try:
                answer = generator.generate_answer(
                    question=question_text,
                    topic=topic_name,
                    sub_category=topic_info["subCategory"],
                )

                difficulty = self._assign_difficulty(idx, len(questions))

                results.append(
                    {
                        "question": question_text,
                        "options": options,
                        "answer": answer,
                        "difficulty": difficulty,
                        "order": idx,
                    }
                )
            except Exception as e:
                logger.error("Failed to generate answer for Q%d: %s", idx, e)
                results.append(
                    {
                        "question": question_text,
                        "options": options,
                        "answer": "",
                        "difficulty": "MEDIUM",
                        "order": idx,
                    }
                )

        upload_payload = {
            "topic": topic_slug,
            "questions": results,
        }

        metadata = {
            "topicName": topic_name,
            "formatType": format_type,
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "totalQuestions": len(questions),
            "successfulAnswers": sum(1 for r in results if r["answer"]),
            "failedAnswers": sum(1 for r in results if not r["answer"]),
        }

        output_data = {**upload_payload, "metadata": metadata}

        output_file = os.path.join(self.output_dir, f"{topic_slug}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        logger.info("Saved output to %s", output_file)
        output_data["outputFile"] = output_file
        return output_data

    def generate_study_guide(
        self,
        topic: str,
    ) -> Dict[str, Any]:
        """Generate a study guide for a topic.

        Args:
            topic: Topic slug or name (resolved via TOPIC_REGISTRY)

        Returns:
            Dict with 'topic' (slug), 'content' (markdown), and 'metadata'.
        """
        topic_info = resolve_topic(topic)
        topic_slug = topic_info["slug"]
        topic_name = topic_info["name"]
        sub_category = topic_info["subCategory"]

        logger.info("Generating study guide for: %s [%s]", topic_name, topic_slug)

        generator = AptitudeStudyGuideGenerator()
        content = generator.generate_guide(
            topic=topic_name,
            sub_category=sub_category,
        )

        output_data = {
            "topic": topic_slug,
            "content": content,
            "metadata": {
                "topicName": topic_name,
                "subCategory": sub_category,
                "generatedAt": datetime.now(timezone.utc).isoformat(),
            },
        }

        output_file = os.path.join(self.output_dir, f"{topic_slug}_study_guide.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        logger.info("Study guide saved to %s", output_file)
        output_data["outputFile"] = output_file
        return output_data

    def process_batch(
        self,
        topics: List[str],
        num_questions: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Process multiple topics. Each entry is a slug or name.

        Args:
            topics: List of topic slugs or names
            num_questions: Optional question count per topic (enforced >= MIN_QUESTIONS_PER_TOPIC)

        Returns:
            Summary dict with per-topic results.
        """
        results = []
        for topic_identifier in topics:
            try:
                result = self.process_topic(
                    topic=topic_identifier,
                    num_questions=num_questions,
                )
                results.append(
                    {
                        "topic": result["topic"],
                        "status": "success",
                        "outputFile": result.get("outputFile"),
                        "totalQuestions": result["metadata"]["totalQuestions"],
                        "successfulAnswers": result["metadata"]["successfulAnswers"],
                    }
                )
            except Exception as e:
                logger.error("Failed to process topic '%s': %s", topic_identifier, e)
                results.append(
                    {
                        "topic": topic_identifier,
                        "status": "failed",
                        "error": str(e),
                    }
                )

        summary_file = os.path.join(self.output_dir, "_batch_summary.json")
        summary = {
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "totalTopics": len(topics),
            "successful": sum(1 for r in results if r["status"] == "success"),
            "failed": sum(1 for r in results if r["status"] == "failed"),
            "results": results,
        }
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        logger.info(
            "Batch complete: %d/%d successful, saved summary to %s",
            summary["successful"],
            summary["totalTopics"],
            summary_file,
        )
        return summary

    @staticmethod
    def _assign_difficulty(idx: int, total: int) -> str:
        """Spread difficulty across EASY/MEDIUM/HARD based on position."""
        ratio = idx / total
        if ratio <= 0.3:
            return "EASY"
        elif ratio <= 0.7:
            return "MEDIUM"
        return "HARD"
