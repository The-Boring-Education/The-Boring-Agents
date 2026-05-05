"""Dedicated DSA generators for questions and study guides."""

import json
import logging
from typing import Any, Dict, List

from langchain_core.prompts import PromptTemplate

from src.agents.base import BaseAgent
from src.agents.dsa.prompts import DSA_QUESTIONS_PROMPT, DSA_STUDY_GUIDE_PROMPT
from src.agents.dsa.validators import normalize_questions, normalize_study_guide

logger = logging.getLogger(__name__)


def _parse_json_array(response: str) -> List[Dict[str, Any]]:
    """Parse first JSON array found in response text."""
    try:
        start = response.find("[")
        end = response.rfind("]") + 1
        if start != -1 and end > start:
            payload = json.loads(response[start:end])
        else:
            payload = json.loads(response)
        return payload if isinstance(payload, list) else []
    except Exception:
        return []


def _parse_json_object(response: str) -> Dict[str, Any]:
    """Parse first JSON object found in response text."""
    try:
        start = response.find("{")
        end = response.rfind("}") + 1
        if start != -1 and end > start:
            payload = json.loads(response[start:end])
        else:
            payload = json.loads(response)
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


class DSAContentGenerator(BaseAgent):
    """Generates DSA questions and study guides from topic-only input."""

    def _get_prompt_templates(self):
        return {
            "questions": PromptTemplate(
                input_variables=["topic", "question_count", "difficulty", "include_real_world"],
                template=DSA_QUESTIONS_PROMPT,
            ),
            "study_guide": PromptTemplate(
                input_variables=["topic", "question_titles"],
                template=DSA_STUDY_GUIDE_PROMPT,
            ),
        }

    def generate_content(self, **kwargs):
        """Required by BaseAgent; delegates to questions generation."""
        return {
            "questions": self.generate_questions(
                topic=kwargs.get("topic", ""),
                question_count=int(kwargs.get("question_count", 20)),
                include_real_world=bool(kwargs.get("include_real_world", True)),
                difficulty=str(kwargs.get("difficulty", "MEDIUM")),
            )
        }

    def generate_questions(
        self,
        *,
        topic: str,
        question_count: int = 20,
        include_real_world: bool = True,
        difficulty: str = "MEDIUM",
    ) -> List[Dict[str, Any]]:
        """Generate DSA questions and normalize them to stable schema."""
        prompt = self._format_prompt(
            "questions",
            topic=topic,
            question_count=question_count,
            difficulty=difficulty.upper(),
            include_real_world=str(include_real_world).lower(),
        )
        response = self._generate_with_prompt(prompt)
        raw_questions = _parse_json_array(response)

        if not raw_questions:
            logger.warning("DSA question generation parse failed for topic '%s'", topic)

        return normalize_questions(
            raw_questions,
            topic=topic,
            question_count=question_count,
            include_real_world=include_real_world,
            difficulty=difficulty.upper(),
        )

    def generate_study_guide(
        self,
        *,
        topic: str,
        questions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Generate topic study guide informed by generated questions."""
        question_titles = [q.get("title", "") for q in questions][:20]
        titles_for_prompt = "\n".join([f"- {title}" for title in question_titles])
        prompt = self._format_prompt(
            "study_guide",
            topic=topic,
            question_titles=titles_for_prompt or "- Basic fundamentals",
        )

        response = self._generate_with_prompt(prompt)
        raw_guide = _parse_json_object(response)

        if not raw_guide:
            logger.warning("Study guide generation parse failed for topic '%s'", topic)

        return normalize_study_guide(
            raw_guide,
            topic=topic,
            question_titles=question_titles,
        )
