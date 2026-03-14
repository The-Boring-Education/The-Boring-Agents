"""Quiz generators: metadata and question generation.

Contains:
- QuizAgentType / QuizDifficulty enums
- QuizMetadataGenerator  -- category name, description, icon
- QuizQuestionGenerator  -- single + batch question generation
- get_generator() factory
"""

import json
import logging
from enum import Enum
from typing import Any, Dict, List, Optional

from langchain_core.prompts import PromptTemplate

from src.agents.base import BaseAgent
from src.agents.quiz.prompts import (
    BATCH_QUESTIONS_PROMPT,
    CATEGORY_METADATA_PROMPT,
    DEFAULT_ICON,
    DEFAULT_ICON_MAP,
    SINGLE_QUESTION_PROMPT,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enums (canonical definitions for the agent layer)
# ---------------------------------------------------------------------------


class QuizAgentType(Enum):
    GENERIC = "generic"
    TECH = "tech"
    DSA = "dsa"
    CONCEPTUAL = "conceptual"


class QuizDifficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# ---------------------------------------------------------------------------
# Private JSON parsing helpers
# ---------------------------------------------------------------------------


def _parse_json_object(response: str) -> Optional[Dict[str, Any]]:
    """Extract the first JSON object from an LLM response string."""
    try:
        start = response.find("{")
        end = response.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(response[start:end])
        return json.loads(response)
    except json.JSONDecodeError as exc:
        logger.error("JSON parse error: %s", exc)
        logger.debug("Response: %s...", response[:500])
        return None


def _parse_json_array(response: str) -> Optional[List[Dict[str, Any]]]:
    """Extract the first JSON array from an LLM response string."""
    try:
        start = response.find("[")
        end = response.rfind("]") + 1
        if start != -1 and end > start:
            return json.loads(response[start:end])
        return json.loads(response)
    except json.JSONDecodeError as exc:
        logger.error("JSON array parse error: %s", exc)
        logger.debug("Response: %s...", response[:500])
        return None


def _get_default_icon(topic: str) -> str:
    topic_lower = topic.lower()
    for key, icon in DEFAULT_ICON_MAP.items():
        if key in topic_lower:
            return icon
    return DEFAULT_ICON


# ---------------------------------------------------------------------------
# QuizMetadataGenerator
# ---------------------------------------------------------------------------


class QuizMetadataGenerator(BaseAgent):
    """Generates quiz category metadata (name, description, icon)."""

    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        return {
            "generate_category_metadata": PromptTemplate(
                input_variables=["topic", "question_count", "target_audience"],
                template=CATEGORY_METADATA_PROMPT,
            ),
        }

    def generate_content(
        self, content_type: str = "generate_category_metadata", **kwargs
    ) -> Dict[str, Any]:
        if content_type == "generate_category_metadata":
            return self.generate_category_metadata(
                topic=kwargs.get("topic", ""),
                question_count=kwargs.get("question_count", 20),
                target_audience=kwargs.get("target_audience", "developers"),
            )
        raise ValueError(f"Unknown content type: {content_type}")

    def generate_category_metadata(
        self,
        topic: str,
        question_count: int = 20,
        target_audience: str = "developers",
    ) -> Dict[str, Any]:
        prompt = self._format_prompt(
            "generate_category_metadata",
            topic=topic,
            question_count=question_count,
            target_audience=target_audience,
        )
        response = self._generate_with_prompt(prompt)
        metadata = _parse_json_object(response)

        if not metadata:
            logger.warning("Failed to parse metadata, using defaults for %s", topic)
            metadata = {
                "categoryName": topic,
                "categoryDescription": (
                    f"Test your knowledge of {topic} with this comprehensive quiz "
                    "covering key concepts, best practices, and real-world scenarios."
                ),
                "categoryIcon": _get_default_icon(topic),
            }

        return self._validate_metadata(metadata, topic)

    @staticmethod
    def _validate_metadata(metadata: Dict[str, Any], topic: str) -> Dict[str, Any]:
        metadata.setdefault("categoryName", topic)
        metadata.setdefault(
            "categoryDescription",
            f"Test your knowledge of {topic} with this comprehensive quiz.",
        )
        metadata.setdefault("categoryIcon", _get_default_icon(topic))

        if len(metadata["categoryName"]) > 100:
            metadata["categoryName"] = metadata["categoryName"][:100]
        if len(metadata["categoryDescription"]) > 500:
            metadata["categoryDescription"] = metadata["categoryDescription"][:500]

        return metadata


# ---------------------------------------------------------------------------
# QuizQuestionGenerator
# ---------------------------------------------------------------------------


class QuizQuestionGenerator(BaseAgent):
    """Generates quiz questions with multiple-choice options."""

    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        return {
            "generate_question": PromptTemplate(
                input_variables=[
                    "topic",
                    "concept",
                    "difficulty",
                    "target_audience",
                    "question_type",
                ],
                template=SINGLE_QUESTION_PROMPT,
            ),
            "generate_batch_questions": PromptTemplate(
                input_variables=[
                    "topic",
                    "question_count",
                    "difficulty",
                    "target_audience",
                    "concepts",
                ],
                template=BATCH_QUESTIONS_PROMPT,
            ),
        }

    def generate_content(
        self, content_type: str = "generate_question", **kwargs
    ) -> Dict[str, Any]:
        if content_type == "generate_question":
            return self.generate_question(
                topic=kwargs.get("topic", ""),
                concept=kwargs.get("concept", ""),
                difficulty=kwargs.get("difficulty", QuizDifficulty.MEDIUM),
                target_audience=kwargs.get("target_audience", "developers"),
                question_type=kwargs.get("question_type", "conceptual"),
            )
        if content_type == "generate_batch":
            return self.generate_batch_questions(
                topic=kwargs.get("topic", ""),
                question_count=kwargs.get("question_count", 20),
                difficulty=kwargs.get("difficulty", QuizDifficulty.MEDIUM),
                target_audience=kwargs.get("target_audience", "developers"),
                concepts=kwargs.get("concepts", []),
            )
        raise ValueError(f"Unknown content type: {content_type}")

    def generate_question(
        self,
        topic: str,
        concept: str,
        difficulty: QuizDifficulty = QuizDifficulty.MEDIUM,
        target_audience: str = "developers",
        question_type: str = "conceptual",
    ) -> Dict[str, Any]:
        diff_value = (
            difficulty.value if isinstance(difficulty, QuizDifficulty) else difficulty
        )
        prompt = self._format_prompt(
            "generate_question",
            topic=topic,
            concept=concept,
            difficulty=diff_value,
            target_audience=target_audience,
            question_type=question_type,
        )
        response = self._generate_with_prompt(prompt)
        question_data = _parse_json_object(response)

        if not question_data:
            raise ValueError("Failed to parse question from LLM response")

        question_data["difficulty"] = diff_value
        return _validate_question(question_data)

    def generate_batch_questions(
        self,
        topic: str,
        question_count: int,
        difficulty: QuizDifficulty = QuizDifficulty.MEDIUM,
        target_audience: str = "developers",
        concepts: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        if concepts is None:
            concepts = [f"{topic} concept {i + 1}" for i in range(question_count)]

        diff_value = (
            difficulty.value if isinstance(difficulty, QuizDifficulty) else difficulty
        )
        concepts_str = "\n".join(f"- {c}" for c in concepts[:20])

        prompt = self._format_prompt(
            "generate_batch_questions",
            topic=topic,
            question_count=question_count,
            difficulty=diff_value,
            target_audience=target_audience,
            concepts=concepts_str,
        )
        response = self._generate_with_prompt(prompt)
        questions = _parse_json_array(response)

        if not questions or len(questions) < question_count:
            logger.warning(
                "Batch generation returned %d questions, generating individually",
                len(questions) if questions else 0,
            )
            questions = []
            question_types = ("conceptual", "code_based", "scenario")
            for i in range(question_count):
                concept = (
                    concepts[i % len(concepts)]
                    if concepts
                    else f"{topic} concept {i + 1}"
                )
                try:
                    q = self.generate_question(
                        topic=topic,
                        concept=concept,
                        difficulty=difficulty,
                        target_audience=target_audience,
                        question_type=question_types[i % 3],
                    )
                    questions.append(q)
                except Exception as exc:
                    logger.error("Error generating question %d: %s", i + 1, exc)

        validated: List[Dict[str, Any]] = []
        for q in questions[:question_count]:
            try:
                q["difficulty"] = diff_value
                validated.append(_validate_question(q))
            except Exception as exc:
                logger.error("Error validating question: %s", exc)
        return validated


# ---------------------------------------------------------------------------
# Question validation (shared)
# ---------------------------------------------------------------------------


def _validate_question(question: Dict[str, Any]) -> Dict[str, Any]:
    required = (
        "question",
        "options",
        "correctAnswer",
        "explanation",
        "detailedExplanation",
    )
    for field in required:
        if field not in question:
            raise ValueError(f"Missing required field: {field}")

    options = question.get("options", [])
    if len(options) != 4:
        raise ValueError(f"Must have exactly 4 options, found {len(options)}")

    correct = question.get("correctAnswer")
    if not isinstance(correct, int) or correct < 0 or correct >= len(options):
        raise ValueError(f"correctAnswer must be 0-3, found {correct}")

    difficulty = question.get("difficulty", "medium")
    if isinstance(difficulty, str):
        difficulty = difficulty.lower()
    question["difficulty"] = (
        difficulty if difficulty in ("easy", "medium", "hard") else "medium"
    )

    return question


# ---------------------------------------------------------------------------
# Generator factory
# ---------------------------------------------------------------------------

_GENERATOR_REGISTRY: Dict[QuizAgentType, type] = {
    QuizAgentType.GENERIC: QuizQuestionGenerator,
    QuizAgentType.TECH: QuizQuestionGenerator,
    QuizAgentType.DSA: QuizQuestionGenerator,
    QuizAgentType.CONCEPTUAL: QuizQuestionGenerator,
}


def get_generator(agent_type, **kwargs) -> QuizQuestionGenerator:
    """Instantiate a generator by QuizAgentType enum or string name."""
    if isinstance(agent_type, str):
        try:
            agent_type = QuizAgentType(agent_type.lower())
        except ValueError:
            raise ValueError(f"Unknown agent type: {agent_type}")
    cls = _GENERATOR_REGISTRY.get(agent_type)
    if cls is None:
        raise ValueError(f"Unknown agent type: {agent_type}")
    return cls(**kwargs)
