"""Answer generators for aptitude interview prep.

Contains:
- AptitudeAnswerGenerator: generates structured answers based on format type
- get_aptitude_generator() factory function
"""

import logging
from typing import Any, Dict

from langchain_core.prompts import PromptTemplate

from src.agents.aptitude.prompts import (
    ANSWER_STRUCTURE_MAP,
    PROMPT_MAP,
)
from src.agents.base import BaseAgent

logger = logging.getLogger(__name__)

APTITUDE_PROMPT_VARS = ["topic", "sub_category", "question"]


class AptitudeAnswerGenerator(BaseAgent):
    """Generates aptitude answers using the appropriate format template."""

    def __init__(self, format_type: str, **kwargs):
        super().__init__(**kwargs)
        self.format_type = format_type.upper()

        if self.format_type not in PROMPT_MAP:
            raise ValueError(
                f"Invalid format_type: {format_type}. "
                f"Must be one of: {list(PROMPT_MAP.keys())}"
            )

    def generate_content(
        self, content_type: str = "answer", **kwargs
    ) -> Dict[str, Any]:
        if content_type == "answer":
            answer = self.generate_answer(
                question=kwargs.get("question", ""),
                topic=kwargs.get("topic", ""),
                sub_category=kwargs.get("sub_category", ""),
            )
            return {
                "status": "success",
                "answer": answer,
                "format_type": self.format_type,
            }
        raise ValueError(f"Unknown content type: {content_type}")

    def generate_answer(
        self,
        question: str,
        topic: str,
        sub_category: str = "",
    ) -> str:
        self.logger.info(
            "Generating %s answer for: %s...",
            self.format_type,
            question[:60],
        )

        prompt_template = PromptTemplate(
            input_variables=APTITUDE_PROMPT_VARS,
            template=PROMPT_MAP[self.format_type],
        )

        prompt = prompt_template.format(
            question=question,
            topic=topic,
            sub_category=sub_category,
        )

        raw_answer = self._generate_with_prompt(prompt)
        improved = self._apply_quality_check(raw_answer, question, topic)
        self.logger.info("Answer generated successfully (%s format)", self.format_type)
        return improved.strip()

    def _apply_quality_check(self, answer: str, question: str, topic: str) -> str:
        """Verify all required sections are present; regenerate missing ones."""
        required = ANSWER_STRUCTURE_MAP[self.format_type]
        missing = [
            name
            for name, keyword in required.items()
            if keyword.lower() not in answer.lower()
        ]

        if not missing:
            return answer

        self.logger.warning("Missing sections: %s — patching...", missing)
        for section in missing:
            patch_prompt = (
                f"Generate a brief '{section}' section for this aptitude question.\n"
                f"Question: {question}\nTopic: {topic}\n"
                f"Write only the section content, starting with the section header."
            )
            answer += f"\n\n{self._generate_with_prompt(patch_prompt)}"

        return answer


def get_aptitude_generator(format_type: str, **kwargs) -> AptitudeAnswerGenerator:
    """Factory: instantiate an AptitudeAnswerGenerator for the given format type."""
    return AptitudeAnswerGenerator(format_type=format_type, **kwargs)
